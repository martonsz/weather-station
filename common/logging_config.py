import logging
from logging.handlers import TimedRotatingFileHandler
import os

from dotenv import load_dotenv

load_dotenv()


# Create log directory if it doesn't exist
log_dir = os.getenv("LOG_DIR", "log")
os.makedirs(log_dir, exist_ok=True)

# Configure log level
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, log_level, logging.INFO)
use_log_file_handler = os.getenv("LOG_USE_FILE_HANDLER", "true").lower()


def setup_logger(name: str, log_file: str) -> logging.Logger:
    """Set up a logger with time-based rotation at midnight."""
    logger = logging.getLogger(name)

    # Prevent multiple handlers if the logger is configured multiple times
    if not logger.handlers:
        # Create formatters
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        if use_log_file_handler == "true":
            # Time-based rotation (daily at midnight)
            file_handler = TimedRotatingFileHandler(
                os.path.join(log_dir, log_file),
                when="midnight",
                interval=1,
                backupCount=10,
                encoding="utf-8",
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logger.setLevel(numeric_level)

    return logger


# Create main application logger
logger = setup_logger("l", "app.log")

if __name__ == "__main__":
    logger.info("Test log message")
