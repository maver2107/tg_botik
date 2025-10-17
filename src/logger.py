import json
import sys
from datetime import datetime
from uuid import UUID

from loguru import logger

from src.config import get_settings

settings = get_settings()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def json_serializer(record):
    log_record = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"],
    }

    if record["exception"]:
        log_record["exception"] = {
            "type": record["exception"].type,
            "value": record["exception"].value,
            "traceback": record["exception"].traceback,
        }

    return json.dumps(log_record, cls=CustomJSONEncoder)


def setup_logging() -> None:
    logger.remove()

    logging_base_config = {
        "level": settings.LOG_LEVEL,
        "backtrace": True,
        "diagnose": True,
        "enqueue": True,
    }

    logger.add(sys.stdout, format=settings.LOG_FORMAT, colorize=True, **logging_base_config)

    logger.add(
        settings.LOG_FILE_PATH,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression=settings.LOG_COMPRESSION,
        serialize=True,
        format="{message}",
        **logging_base_config,
        colorize=False,
    )

    logger.debug("Logger successfully initialized.")
