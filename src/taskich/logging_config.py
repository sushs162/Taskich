import logging
from pathlib import Path

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging(
    log_file: str | Path = "taskich.log",
    level: int = logging.INFO,
) -> None:
    """Настраивает запись логов в файл, чтобы не засорять консольное меню."""

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[logging.FileHandler(log_file, encoding="utf-8")],
    )
