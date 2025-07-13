import logging
import sys
from typing import Optional

def get_logger(name: Optional[str] = None):
    """Get configured logger instance with consistent formatting"""
    
    # Create logger
    logger_name = name or __name__
    logger = logging.getLogger(logger_name)
    
    # Set level
    logger.setLevel(logging.INFO)
    
    # Check if logger already has handlers to avoid duplicates
    if not logger.handlers:
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
    
    return logger 