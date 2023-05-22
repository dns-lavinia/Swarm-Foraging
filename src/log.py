import sys
import logging 

LOG_FORMAT = logging.Formatter('[%(asctime)s] %(levelname)-8s %(name)-10s %(message)s')

# Add logging levels for this module
LOG_CRITICAL = logging.CRITICAL
LOG_ERROR = logging.ERROR
LOG_WARNING = logging.WARNING
LOG_INFO = logging.INFO
LOG_DEBUG = logging.DEBUG
LOG_NONSET = logging.NOTSET

def create_logger(name, level=logging.DEBUG):
    # Create the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Add a console handler for this logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(LOG_FORMAT)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger