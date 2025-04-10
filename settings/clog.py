import logging
from pathlib import Path
import os
from types import TracebackType
from typing import List, Literal, Mapping


class CustomerLogger:
    def __init__(
        self,
        log_name: str,
        log_mode: Literal["file", "stream"] = "file",
        allow_add_handler=True,
    ) -> None:
        self.log_name = log_name
        self.log_mode = log_mode
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.DEBUG)

        if not allow_add_handler and self.logger.hasHandlers():
            return

        if log_mode == "file":
            self.__add_file_handler(log_name=self.log_name)
            return

        if log_mode == "stream":
            self.__add_stream_handler()
            return

        pass

    def __add_file_handler(self, log_name: str):
        # Create file logger handler
        logfile = os.path.join("./log/", f"{log_name}.log")
        Path(logfile).resolve().parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(filename=logfile)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.__create_formatter())
        self.logger.addHandler(file_handler)
        pass

    def __add_stream_handler(self):
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(self.__create_formatter())
        self.logger.addHandler(stream_handler)
        pass

    def __create_formatter(self):
        return logging.Formatter(
            "[{asctime}][{name}][{levelname}]: {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M",
        )

    def error(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self.logger.error(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def debug(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self.logger.debug(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def info(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self.logger.info(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def warning(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = None,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self.logger.warning(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def exception(
        self,
        msg: object,
        *args: object,
        exc_info: (
            None
            | bool
            | tuple[type[BaseException], BaseException, TracebackType | None]
            | tuple[None, None, None]
            | BaseException
        ) = True,
        stack_info: bool = False,
        stacklevel: int = 1,
        extra: Mapping[str, object] | None = None,
    ) -> None:
        return self.logger.exception(
            msg,
            *args,
            exc_info=exc_info,
            stack_info=stack_info,
            stacklevel=stacklevel,
            extra=extra,
        )

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)
