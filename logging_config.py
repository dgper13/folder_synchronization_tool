import logging
from typing import Optional

# Initialize logger with no handlers
logger = logging.getLogger()

def setup_logging(log_file: Optional[str] = 'file.log') -> None:
    """
    Configures logging for the application with both console and file handlers.

    Args:
        log_file (str, optional): Path to the log file. Defaults to 'file.log'.

    Returns:
        None
    """

    global logger

    # Remove existing handlers to avoid duplicate logs
    logger.handlers = []

    # Set logger level to capture all messages
    logger.setLevel(logging.DEBUG)

    # Create console handler to display logs in the console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create file handler to log messages to a specified log file
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # Create formatter with timestamp, log level, and message
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set formatter for console and file handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add console and file handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

# Initial setup with default log file 'file.log'
setup_logging()