"""Runs the deploy unit tests"""
import ConfigParser
import os
import unittest
import mxorc_deploy
import mxorc_logger
from mxorc_deploy import SSHConnector
from socket import gaierror
import paramiko
from paramiko import SSHException

THIS_DIRECTORY = os.path.dirname(__file__)

DEPLOY_CONFIG = ConfigParser.ConfigParser()
DEPLOY_CONFIG.read(os.path.join(THIS_DIRECTORY, "conf/mxorc_deploy.conf"))

LOGGER = mxorc_logger.get_logger(name="mxorc_deploy_test")

USER = DEPLOY_CONFIG.get("Deploy Config", "user")
HOST = "xldmxs10"
KEY = paramiko.RSAKey.from_private_key(open(
    DEPLOY_CONFIG.get("Deploy Config", "private_key_path")))

class TestConfiguration(unittest.TestCase):

    """ Test the configurations in mxorc_deploy.conf
    """

    def validate_config(self):
        """ Validate the configurations
        Globals:
            LOGGER, DEPLOY_CONFIG
        Arguments:
            self
        Returns:
            none
        """
        LOGGER.info("Validating local path.")
        local_dir = DEPLOY_CONFIG.get("Deploy Config", "local_path")
        self.assertTrue(os.path.isdir(local_dir))
        LOGGER.info("Validating the private key file.")
        private_key_path = DEPLOY_CONFIG.get("Deploy Config", "private_key_path")
        self.assertTrue(os.path.isfile(private_key_path))


class TestConnection(unittest.TestCase):

    """ Test a correctly configured connections then test malconfigured
        connections.
    """

    def open_connection(self):
        """ Validate a correctly configured connection.
        Globals:
            LOGGER, DEPLOY_CONFIG
        Arguments:
            self
        Returns:
            none
        """
        user = USER
        host = HOST
        key = KEY

        LOGGER.info("Testing proper connection.")
        try :
            ssh = SSHConnector(user, host, key)
        except AttributeError:
            LOGGER.error("Proper SSH connection failed due to an AttributeError.")
            self.fail()
        except paramiko.ssh_exception.AuthenticationException:
            LOGGER.error("Proper SSH connection failed due to an Auth error.")
            self.fail()
        except SSHException:
            LOGGER.error("Proper SSH connection failed due to a SSHException.")
            self.fail()
        ssh.ssh.close()
        ssh.sftp.close()
        LOGGER.info("Proper connection working.")


    def malconfigured_connection(self):
        """ Validate that all possible malconfigured connections fail.
        Globals:
            LOGGER, DEPLOY_CONFIG
        Arguments:
            self
        Returns:
            none
        """
        user = USER
        host = HOST
        key = KEY

        not_the_user = "fake_mxorc"
        not_the_host = "fake_swahost"
        not_the_key = DEPLOY_CONFIG.get("Deploy Config", "private_key_path")

        LOGGER.info("Testing malconfigured connections.")

        # test malconfigured host
        LOGGER.info("Testing with %s, %s", user, not_the_host)
        self.assertRaises(TypeError, user, not_the_host, key)

        # test with malconfigured user
        LOGGER.info("Testing with %s, %s", not_the_user, host)
        try:
            try:
                ssh = SSHConnector(not_the_user, host, key)
            except paramiko.ssh_exception.AuthenticationException:
                self.assertTrue(True)
        except gaierror:
                self.assertTrue(True)

        # test with malconfigured key
        LOGGER.info("Testing with a malconfigured key.")
        try:
            try:
                ssh = SSHConnector(user, host, not_the_key)
            except AttributeError:
                self.assertTrue(True)
        except gaierror:
                self.assertTrue(True)

        # test with malconfigured host and key
        LOGGER.info("Testing with %s, %s and a malconfigured key.", user,
                     not_the_host)
        try:
            try:
                ssh = SSHConnector(user, not_the_host, not_the_key)
            except AttributeError:
                self.assertTrue(True)
        except gaierror:
                self.assertTrue(True)

        # test with malconfigured user and host
        LOGGER.info("Testing with %s, %s", not_the_user, not_the_host)
        try:
            try:
                ssh = SSHConnector(not_the_user, not_the_host, key)
            except AttributeError:
                self.assertTrue(True)
        except gaierror:
                self.assertTrue(True)

        # test with everything malconfigured
        LOGGER.info("Testing with %s, %s and a malconfigured key.", not_the_user,
                     not_the_host)
        try:
            try:
                ssh = SSHConnector(not_the_user, not_the_host, not_the_key)
            except AttributeError:
                self.assertTrue(True)
        except gaierror:
                self.assertTrue(True)

        LOGGER.info("Malconfigured connections reacting as expected.")

class TestCommands(unittest.TestCase):
    def deploy(self):
        """ Tests the deploy functionality.
        Globals:
            LOGGER, DEPLOY_CONFIG
        Arguments:
            self
        Returns:
            none
        """
        # test and open connection
        user = USER
        host = HOST
        key = KEY
        test_folder_one = "bash"
        test_folder_two = "bash/PCS"
        not_a_folder = "fake_bash"

        LOGGER.info("Testing proper connection.")
        try:
            ssh = SSHConnector(user, host, key)
        except AttributeError:
            LOGGER.error("Proper SSH connection failed due to an AttributeError.")
            self.fail()
        except paramiko.ssh_exception.AuthenticationException:
            LOGGER.error("Proper SSH connection failed due to an Auth error.")
            self.fail()
        except SSHException:
            LOGGER.error("Proper SSH connection failed due to a SSHException.")
            self.fail()
        LOGGER.info("Proper connection working.")

        # Test proper deploy methods
        LOGGER.info("Testing proper deployment.")
        try:
            mxorc_deploy.deploy(test_folder_one, ssh)
        except IOError:
            LOGGER.info("Proper deployment failed.")
            self.fail()
        LOGGER.info("Proper deployment succeeded.")
        remote_path = os.path.join(DEPLOY_CONFIG.get("Deploy Config", "remote_path"), test_folder_one)
        for f in ssh.sftp.listdir(os.path.join(DEPLOY_CONFIG.get("Deploy Config", "remote_path"), test_folder_one)):
            if f[-3:] == ".sh":
                file_path = os.path.join(remote_path, f)
                file_stat = ssh.sftp.stat(file_path).st_mode
                # bit mask to remove extra inode permission bits
                mask = 0o777
                assert file_stat & mask == 0o755, "Permission incorrect."
        # test neseted folder deploys
        LOGGER.info("Testing proper nested folder deployment.")
        try:
            mxorc_deploy.deploy(test_folder_two, ssh)
        except IOError:
            LOGGER.info("Proper nested deployment failed.")
            self.fail()
        LOGGER.info("Proper nested folder deployment succeeded.")

        # test malconfigured deploy method
        LOGGER.info("Testing malconfigured folder deployment.")
        self.assertRaises(OSError, mxorc_deploy.deploy, not_a_folder, ssh)
        LOGGER.info("Malconfigured deployment responded as expected.")

        # clsoe connections to avoid hang ups
        ssh.ssh.close()
        ssh.sftp.close()


    def remove(self):
        """ Tests the remove functionality.
        Globals:
            LOGGER, DEPLOY_CONFIG
        Arguments:
            self
        Returns:
            none
        """
        # test and open connection
        user = USER
        host = HOST
        key = KEY
        test_folder_one = "bash"
        test_folder_two = "bash/PCS"
        not_a_folder = "fake_bash"

        LOGGER.info("Testing proper connection.")
        try:
            ssh = SSHConnector(user, host, key)
        except AttributeError:
            LOGGER.error("Proper SSH connection failed due to an AttributeError.")
            self.fail()
        except paramiko.ssh_exception.AuthenticationException:
            LOGGER.error("Proper SSH connection failed due to an Auth error.")
            self.fail()
        except SSHException:
            LOGGER.error("Proper SSH connection failed due to a SSHException.")
            self.fail()
        LOGGER.info("Proper connection working.")

        # Test proper deploy methods
        LOGGER.info("Testing proper removal.")
        try:
            mxorc_deploy.remove(test_folder_one, ssh)
        except IOError:
            LOGGER.info("Proper removal failed.")
            self.fail()
        LOGGER.info("Proper removal succeeded.")

        # test neseted folder deploys
        LOGGER.info("Testing proper nested folder removal.")
        try:
            mxorc_deploy.remove(test_folder_two, ssh)
        except IOError:
            LOGGER.info("Proper nested removal failed.")
            self.fail()
        LOGGER.info("Proper nested folder removal succeeded.")

        # test malconfigured deploy method
        LOGGER.info("Testing malconfigured folder removal.")
        self.assertRaises(OSError, mxorc_deploy.remove, not_a_folder, ssh)
        LOGGER.info("Malconfigured removal responded as expected.")

        # clsoe connections to avoid hang ups
        ssh.ssh.close()
        ssh.sftp.close()
