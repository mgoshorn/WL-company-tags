import os
import logging

"""
    Utility logger used for the application
"""

def create_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel("DEBUG")
    stream_logger = logging.StreamHandler()
    file_logger = logging.FileHandler('log.txt')

    stream_logger.setLevel(os.environ.get('CONSOLE_LOG_LEVEL', "DEBUG"))
    file_logger.setLevel(os.environ.get('FILE_LOG_LEVEL', "INFO"))

    format = logging.Formatter('%(asctime)s %(levelname)s [%(name)s]: %(message)s')

    stream_logger.setFormatter(format)
    file_logger.setFormatter(format)

    logger.addHandler(stream_logger)
    logger.addHandler(file_logger)
    
    return logger

log = create_logger("logger")
log.info("Initializing logger")
