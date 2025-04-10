from collections import OrderedDict
import json
import structlog
from settings.settings import azure_settings
from settings.invalid_config_exception import InvalidConfigException
import os
import logging
from logging.handlers import RotatingFileHandler


def custom_json_serializer(dic, **kw):
    mod = {}
    if "event" in dic:
        mod["level"] = dic["level"]
        mod["timestamp"] = dic["timestamp"]
        mod["logger"] = dic["logger"]
        try:
            mod["request_id"] = dic["request_id"]
        except:
            mod["request_id"] = None

        mod["message"] = dic["event"]

        try:
            mod["request_type"] = dic["request_type"]
        except:
            pass

    for k in dic:
        if k != "event":
            mod[k] = dic[k]
    return json.dumps(mod, **kw)


class JsonLogger:
    def __init__(self, name: str):
        if azure_settings.logger_setting.logging_mode == "file":
            log_dir = os.path.dirname(azure_settings.logger_setting.logging_file_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            handler = RotatingFileHandler(azure_settings.logger_setting.logging_file_path)
            handler.setFormatter(logging.Formatter("%(message)s"))

            logging.basicConfig(
                handlers=[handler], level=logging.INFO, format="%(message)s"
            )

            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.filter_by_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer(
                        serializer=custom_json_serializer
                    ),
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                ],
                context_class=OrderedDict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        elif azure_settings.logger_setting.logging_mode == "stream":
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))

            logging.basicConfig(
                handlers=[handler], level=logging.INFO, format="%(message)s"
            )

            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.filter_by_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer(
                        serializer=custom_json_serializer
                    ),
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                ],
                context_class=OrderedDict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
        else:
            raise InvalidConfigException(
                r"Invalid settings for log. Please choose between 'file' or 'stream' only"
            )

        self.logger = structlog.get_logger(name).bind()

    def debug(self, message: str, **kwargs):
        kwargs["level"] = 10  # DEBUG level
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        kwargs["level"] = 20  # INFO level
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        kwargs["level"] = 30  # WARNING level
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        kwargs["level"] = 40  # ERROR level
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        kwargs["level"] = 50  # CRITICAL level
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        kwargs["level"] = 50  # CRITICAL level
        self.logger.exception(message, **kwargs)
