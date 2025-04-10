import logging
from settings.settings import azure_settings
from settings.invalid_config_exception import InvalidConfigException

class Logger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.hasHandlers():
            if azure_settings.logger_setting.logging_mode == "file":
                import os

                log_dir = os.path.dirname(azure_settings.logger_setting.logging_file_path)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                console_handler = logging.FileHandler(
                    azure_settings.logger_setting.logging_file_path
                )
            elif azure_settings.logger_setting.logging_mode == "stream":
                console_handler = logging.StreamHandler()
            else:
                raise InvalidConfigException(
                    r"Invalid settings for log. Please choose between 'file' or 'stream' only"
                )

            console_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)

            self.logger.addHandler(console_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
