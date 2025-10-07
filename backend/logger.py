import logging
import sys

def get_logger(name: str) -> logging.Logger:
    """Get a simple logger with timestamp formatting."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        ))
        logger.addHandler(handler)

    return logger
