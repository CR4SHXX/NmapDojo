"""
Logging configuration for Nmap Dojo.
"""

import logging
from config.settings import LOG_FILE


def setup_logger():
    """Set up and configure the application logger."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logger()
