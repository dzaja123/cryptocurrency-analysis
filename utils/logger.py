"""
Centralized logging configuration for the cryptocurrency analysis application.
"""

import os
import logging


def setup_logger():
    """Set up and configure the centralized logger."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Configure logging
    log_file = os.path.join(log_dir, 'crypto_analysis.log')

    # Set up the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s:%(funcName)s:%(lineno)d] '
               '- %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )

    return logging.getLogger(__name__)
