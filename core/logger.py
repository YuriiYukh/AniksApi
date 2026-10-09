"""
Project logger configuration.
"""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)

    logger.addHandler(handler)
    logger.propagate = False

    return logger
