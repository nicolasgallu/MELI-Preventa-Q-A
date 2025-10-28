import logging
import os

log_file = os.getenv("LOG_FILE", "app.log")
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()

logging.basicConfig(
    level=log_level,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger("app")
