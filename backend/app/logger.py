import logging
import sys
from typing import Any, Dict

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.DEBUG

def setup_logger(name: str = "patient_dashboard") -> logging.Logger:
    """Setup and return a configured logger instance"""
    
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str = "patient_dashboard") -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)

# Create default logger instance
logger = setup_logger() 