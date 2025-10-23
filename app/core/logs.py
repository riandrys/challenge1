import logging
import os

from app.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Creating log directory if not exist
if not os.path.isdir(os.path.join(BASE_DIR, "logs/api/")):
    os.makedirs(os.path.join(BASE_DIR, "logs/api/"))


local_log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
            "formatter": "standard",
            "propagate": 0,
        },
        "uvicorn": {"handlers": ["console"], "formatter": "standard", "propagate": 0},
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    },
}

log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
            "formatter": "standard",
            "propagate": 0,
        },
        "uvicorn": {"handlers": ["console"], "formatter": "standard", "propagate": 0},
    },
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "level": settings.LOG_LEVEL,
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(BASE_DIR, "logs/api/challenge-api.log"),
            "utc": 1,
            "when": "midnight",
            "interval": 1,
        },
        "error": {
            "level": logging.ERROR,
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "standard",
            "filename": os.path.join(BASE_DIR, "logs/api/error.log"),
            "utc": 1,
            "when": "midnight",
            "interval": 1,
        },
    },
}


def get_logger(name: str | None = None):
    logger = logging.getLogger(name or settings.PROJECT_NAME)
    return logger
