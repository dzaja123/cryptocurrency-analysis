"""
Logger Setup

This module provides centralized logging configuration for the cryptocurrency analysis application.
"""

import logging
import os
from typing import Optional

class LoggerManager:
    """Centralized logger management class."""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        """Ensure singleton pattern for logger manager."""
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def setup_logger(cls, log_level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
        """Set up and return a configured logger instance."""
        if cls._logger is not None:
            return cls._logger
            
        # Create logger
        logger = logging.getLogger('crypto_analysis')
        logger.setLevel(log_level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler if log file is specified
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        cls._logger = logger
        return logger
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get the configured logger instance."""
        if cls._logger is None:
            return cls.setup_logger()
        return cls._logger
