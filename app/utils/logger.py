import logging.config
import os
from flask import request

class RequestFilter(logging.Filter):
    def filter(self, record):
        try:
            # Intenta obtener la ruta del request actual
            record.route = request.path
        except Exception:
            # Si no hay contexto de request (por ejemplo, en tareas en segundo plano), asigna un valor por defecto
            record.route = 'N/A'
        return True

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "request_filter": {
            "()": RequestFilter,
        }
    },
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s] [%(name)s] [PID:%(process)d] "
                      "[Thread:%(thread)d] [%(filename)s:%(lineno)d] [Ruta:%(route)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["request_filter"],
        },
        "rotating_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.getenv("LOG_FILE", "app.log"),
            "maxBytes": 1 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "default",
            "filters": ["request_filter"],
        },
    },
    "loggers": {
        "openai": {
            "level": "WARNING",
            "propagate": False
        },
        "urllib3": {              # Agrega esta sección para urllib3
            "level": "WARNING",
            "propagate": False
        },
        "werkzeug": {             # Agrega esta sección para werkzeug
            "level": "WARNING",
            "propagate": False
        }
    },
    "root": {
        "level": os.getenv("LOG_LEVEL", "DEBUG").upper(),
        "handlers": ["console", "rotating_file"],
    },
}


def setup_logger():
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger("app")

logger = setup_logger()
