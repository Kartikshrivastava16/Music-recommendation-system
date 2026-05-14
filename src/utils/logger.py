"""
Logging utilities
"""

import logging
import sys
from pathlib import Path
from config import LOG_LEVEL, LOG_FILE

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        log_file = Path(LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not set up file handler: {e}")
    
    return logger
