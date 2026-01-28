"""
Logging configuration for the data validation solution.
"""

import logging
import sys
from datetime import datetime


def setup_logger(name: str = "data_validator", level: int = logging.INFO):
    """
    Set up and return a logger with console and file handlers.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Console handler with color support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger


# Default logger instance
logger = setup_logger()
