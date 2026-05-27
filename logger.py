import logging
import os
from pathlib import Path

LOG_DIR = Path.home() / ".config" / "yandex-music-cli"
LOG_FILE = LOG_DIR / "app.log"

def setup_logger():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("ym-cli")
    logger.setLevel(logging.DEBUG)
    
    # Create file handler
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.DEBUG)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(fh)
        
    return logger

logger = setup_logger()
