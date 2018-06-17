"""Deploys or removes a specified folder of Bash scripts to/from hosts."""
import argparse
import logging
import ConfigParser
from socket import gaierror
from os import listdir
from os.path import isfile, join, dirname
from hashlib import md5
import paramiko
from paramiko import SSHException
import mxorc_logger

THIS_DIRECTORY = dirname(__file__)

DEPLOY_CONFIG = ConfigParser.ConfigParser()
DEPLOY_CONFIG.read(join(THIS_DIRECTORY, "conf/mxorc_deploy.conf"))

LOGGER = mxorc_logger.get_logger(name="mxorc_deploy")
logging.getLogger("paramiko").setLevel(logging.WARNING)

def main():
    """The main function, parses args then defines an SSH connection, then
        then executes deploy or remove, based on arguments
    Globals:
        LOGGER, DEPLOY_CONFIG
    Arguments:
        none
    Returns:
        none
    """
    parser = argparse.ArgumentParser()
    parser_action = parser.add_mutually_exclusive_group(required=True)
    parser_action.add_argument("-d", "--deploy", action="store_true",
                               help="Deploy script folder to hosts.")
    parser_action.add_argument("-r", "--remove", action="store_true",
                               help="Remove script folder from hosts.")
    parser.add_argument("-f", "--folder", required=True,
                        help="Folder of scripts to deploy/remove"
                        " to/from hosts.")
    parser.add_argument("-t", "--target", required=True,
                        help="The host to deploy to.")
    args = parser.parse_args()

    # capture key from file
    service_key = paramiko.RSAKey.from_private_key(open(
        DEPLOY_CONFIG.get("Deploy Config", "private_key_path")))

    # create connections, then act according to parsed arguments
    ssh = SSHConnector(DEPLOY_CONFIG.get("Deploy Config", "user"), args.target,
                       service_key)
    if args.deploy:
        deploy(args.folder, ssh)
    elif args.remove:
        remove(args.folder, ssh)

    # close connections to prevent hanging
    LOGGER.info("Closing connections.")
    ssh.ssh.close()
    ssh.sftp.close()
    LOGGER.info("Successfully closed connections.")

# pylint: disable=too-few-public-methods
class SSHConnector(object):

    """ Creates an SSH and SFTP connection that allows for directly using
        paramiko. Only starts the instance with some error checking. Other
        errors related to execution of commands should be caught where those
        commands are called.
    """

    def __init__(self, user, host, key):
        """SSH initializaton
        Globals:
            LOGGER, DEPLOY_CONFIG
        Arguments:
            self
            host - the host being connected to
            user - the user being connected to
            key - the SSH key used for connectivity
        Returns:
            none
        """
        # Build ssh connections, catch a bad key and a failed connection
        LOGGER.info("Attempting to make SSH connection to %s as %s.", host, user)
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=host, username=user, pkey=key,
                             timeout=int(DEPLOY_CONFIG.get("Deploy Config", "timeout")))
        except AttributeError as error:
            LOGGER.error("Cannot connect to %s with the user %s, no key was "
                         "provided. Use paramiko.RSAKey.from_private_key(open"
                         "(SERVICE_KEY_FILENAME)) to turn a key file into an "
                         "usable key.", host, user)
            LOGGER.error(error)
            raise
        except paramiko.ssh_exception.AuthenticationException as error:
            LOGGER.error("Cannot connect to %s with the user %s, the ssh"
                         " authentication failed.", host, user)
            LOGGER.error(error)
            raise
        LOGGER.info("Successfully made SSH connection to %s as %s.", host, user)

        # build transport, and catch ssh failures and malconfigurations
        LOGGER.info("Attempting to make SFTP connection to  %s as %s.",
                    host, user)
        self.transport = paramiko.Transport((host, 22))
        try:
            self.transport.connect(username=user, pkey=key)
        except SSHException as error:
            LOGGER.error("Cannot connect to %s with the user %s, the transport"
                         " authentication failed.", host, user)
            LOGGER.error(error)
            raise
        except gaierror as error:
            LOGGER.error("Your connection details are malconfigured.")
            LOGGER.error(error)
            raise
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        LOGGER.info("Sucessfully made SFTP connection to %s as %s.", host, user)

        LOGGER.info("Successfully set up connections.")


def deploy(folder, ssh, retry=0):
    """Deploy a folder to specified host. Sets up an ssh connection with
       the SSHConnector class, then uses that connection to loop through a
       listing of files to deploy. It also deploys a checksum then validates it.
    Globals:
        LOGGER, DEPLOY_CONFIG
    Arguments:
        folder - the folder being deployed
        ssh - the ssh connection
    Returns:
        none
    """
    deploy_attempts = DEPLOY_CONFIG.get("Deploy Config", "deploy_attempts")
    local_path = DEPLOY_CONFIG.get("Deploy Config", "local_path") + folder
    remote_path = DEPLOY_CONFIG.get("Deploy Config", "remote_path") + folder

    # get a listing of all the files of the specified folder on the local path
    try:
        files = [filename for filename in listdir(local_path) if isfile(join(local_path, filename))]
    except OSError:
        LOGGER.error("%s does not exist.", local_path)
        raise

    # create parts of the path not included in the argument
    try:
        ssh.ssh.exec_command("mkdir -p " + remote_path, timeout=int(
            DEPLOY_CONFIG.get("Deploy Config", "timeout")))
    except IOError:
        LOGGER.warning("Cannot create %s, it may already exist.", remote_path)
    LOGGER.info("Created remote folder %s", remote_path)

    for filename in files:
        full_local_path = join(local_path, filename)
        full_remote_path = join(remote_path, filename)
        local_checksum_path = full_local_path + ".md5"

        # don't deploy checksums or anything already deployed and up to date
        if str(filename).endswith(".md5"):
            LOGGER.info("%s is a checksum, and will not be deployed.", filename)
            continue
        elif checksum(local_checksum_path, full_remote_path, ssh):
            LOGGER.warning("Checksums match, the deployment of %s unnecessary",
                           filename)
            continue
        else:
            # deploy the file, and its accompanying checksum
            LOGGER.info("No deployed files detected.")
            LOGGER.info("Generating checksum prior to deployment.")
            md5sum(filename, local_path)
            LOGGER.info("Deploying %s", filename)
            try:
                ssh.sftp.put(full_local_path, full_remote_path)
            except IOError as error:
                LOGGER.error("Could not find %s to deploy.", full_local_path)
                if retry <= deploy_attempts:
                    retry += 1
                    LOGGER.warning("Deploy retry: %s", retry)
                    deploy(folder, ssh, retry)
                else:
                    LOGGER.error(error)
                    raise
            LOGGER.info("Deployed %s", filename)
            if checksum(local_checksum_path, full_remote_path, ssh):
                ssh.sftp.chmod(full_remote_path, 0o755)
                LOGGER.info("Checksums match, the deployment of %s "
                            "was successful.", filename)
            else:
                LOGGER.error("Checksums do not match, the deployment of %s "
                             "was unsuccessful.", filename)

def remove(folder, ssh):
    """ Remove a  folder from a specified host. Sets up an ssh connection with
       the SSHConnector class, then uses that connection to loop through a
       listing of files to remove. Finally, it removes the empty directory.
    Globals:
        LOGGER, DEPLOY_CONFIG
    Arguments:
        folder - the folder to be removed
        ssh - the ssh connection
    Returns:
        none
    """
    local_path = DEPLOY_CONFIG.get("Deploy Config", "local_path") + folder
    remote_path = DEPLOY_CONFIG.get("Deploy Config", "remote_path") + folder

    # get a listing of all the files of the specified folder on the local path
    try:
        files = [filename for filename in listdir(local_path) if isfile(join(local_path, filename))]
    except OSError:
        LOGGER.error("%s does not exist.", local_path)
        raise
    # remove every file in the list of files
    for filename in files:
        full_remote_path = remote_path + "/" + filename
        try:
            LOGGER.info("Removing %s", filename)
            ssh.sftp.remove(full_remote_path)
            LOGGER.info("Successfully removed %s", filename)
        except IOError:
            LOGGER.warning("Can't remove %s, it may not exist.", full_remote_path)

    try:
        ssh.ssh.exec_command("rm -rf " + remote_path, timeout=int(
            DEPLOY_CONFIG.get("Deploy Config", "timeout")))
    except IOError:
        LOGGER.warning("Cannot remove %s, it may not exist.", remote_path)


def md5sum(filename, path):
    """Creates an md5 from a file for a checksum
    Globals:
        none
    Arguments:
        file - the file's name
        path - an absolute path to file's directory
    Returns:
        none
    """
    full_file_path = path  + "/" + filename
    full_md5_path = path + "/" + filename + ".md5"
    md5_file = open(full_md5_path, "w+b")
    md5_hash = md5()

    with open(full_file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(128 * md5_hash.block_size), b""):
            md5_hash.update(chunk)

    md5_file.write(str(md5_hash.hexdigest()))
    md5_file.close()


def checksum(local_checksum, remote_file, ssh):
    """Whether or not the local checksum matches the remote checksum
    Globals:
        LOGGER, DEPLOY_CONFIG
    Arguments:
        local_checksum - the local checksum
        remote_file - the remote file to generate a checksum with
        ssh - the ssh connection
    Returns:
        True - if the checksums match
        False - if the checksums do not match or cannot be determined to be
                matching
    """
    # build remote checksum command, execute it and capture all streams
    generate_remote_checksum = ("md5sum " + remote_file + " | "
                                "awk '{ print $1 }' | tr -d '\n' |"
                                "tee " + remote_file + ".md5")
    try:
        # pylint: disable=unused-variable
        rmt_cs_stdin, rmt_cs_stdout, rmt_cs_stderr = ssh.ssh.exec_command(
            generate_remote_checksum, timeout=int(DEPLOY_CONFIG.get(
                "Deploy Config", "timeout")))
    except SSHException:
        LOGGER.warning("Failed to open remote checksum at %s", remote_file)
        LOGGER.warning("Could not validate deployment.")
        return False

    # the actual check, notice it only returns true or false and does not stop
    # exectuion of the program
    try:
        local_checksum_contents = open(local_checksum, "rb").read()
    except IOError:
        LOGGER.warning("%s could not be read.", local_checksum)
        return False
    remote_checksum_contents = rmt_cs_stdout.read()
    remote_checksum_error = rmt_cs_stderr.read()

    if not remote_checksum_error:
        LOGGER.debug("Local checksum %s", local_checksum_contents)
        LOGGER.debug("Remote checksum %s", remote_checksum_contents)
        return bool(local_checksum_contents == remote_checksum_contents)
    LOGGER.warning("The following error occured reading the checksum : \n"
                   "%s", remote_checksum_error)
    return False


if __name__ == "__main__":
    main()
