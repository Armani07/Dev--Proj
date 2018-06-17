"""A python logger to catch all messages from failover scripts"""
from os.path import join, dirname
import logging
import logging.config

THIS_DIRECTORY = dirname(__file__)

logging.config.fileConfig(join(THIS_DIRECTORY, "conf/mxorc_logger.conf"))

def get_logger(name="mxorc_logger"):
    """Get the logging object and name it according to user input

    Globals:
        logging
    Arguments:
        name: A String to use as the Logger's name
    Returns:
        A Logger object, named according to user input
    """
    return logging.getLogger(str(name))
