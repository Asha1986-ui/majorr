import logging
import sys
from app.config.settings import settings


def setup_logger(name: str = "diasense") -> logging.Logger:
    """
    Configures and returns a centralized logger.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        log_level = logging.DEBUG if settings.DEBUG else logging.INFO
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger


logger = setup_logger()
