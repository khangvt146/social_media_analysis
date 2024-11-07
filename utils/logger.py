import logging
from typing import Optional

DEFAULT_FORMAT = r"[%(asctime)s] [p%(process)s][%(filename)s:%(funcName)s:%(lineno)s] %(levelname)s: %(message)s"


class Logger(logging.Logger):
    """
    Custom Logger class.
    """

    def __init__(
        self,
        name: str,
        path: Optional[str],
        log_format: str = DEFAULT_FORMAT,
        level: int = logging.INFO,
    ) -> None:
        super().__init__(name, level)

        formatter = logging.Formatter(log_format)
        self.setLevel(level)

        # Create StreamHandler logger
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

        if path is not None:
            # Create FileHandler logger
            file_handler = logging.FileHandler(path)
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)


if __name__ == "__main__":
    log_name = "Test Log"
    log_path = "log_test.log"

    log = Logger(log_name, log_path)
    log.debug("debug message")
    log.info("info message")
    log.warning("warn message")
    log.error("error message")
    log.critical("critical message")
