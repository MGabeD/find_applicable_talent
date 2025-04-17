import logging
import json
from datetime import datetime
from pathlib import Path
import os


def resolve_project_source():
    current_file = Path(__file__).resolve()
    while current_file.name != "backend":
        current_file = current_file.parent
    return current_file

_run_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
RESET = "\033[0m"
COLORS = {
    'DEBUG': "\033[36m",    # Cyan
    'INFO': "\033[32m",     # Green
    'WARNING': "\033[33m",  # Yellow
    'ERROR': "\033[31m",    # Red
    'CRITICAL': "\033[41m"  # Red background
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        color = COLORS.get(levelname, RESET)
        message = super().format(record)
        return f"{color}{message}{RESET}"


class DataInjectingFormatter(logging.Formatter):
    def format(self, record):
        base = super().format(record)
        if hasattr(record, 'data'):
            try:
                serialized = json.dumps(record.data, indent=4)
            except Exception as e:
                serialized = str(e)
            return f"{base}\n [data] {serialized}"
        return base


def get_logger(name: str, quiet_mode: bool = os.environ.get("QUIET_MODE", "false").lower() == "true", disable_file_logging: bool = os.environ.get("DISABLE_FILE_LOGGING", "false").lower() == "true") -> logging.Logger:
    project_root: Path = resolve_project_source()
    logs_dir: Path = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file_path = logs_dir / f"pipeline_run_{_run_id}.log"

    logger = logging.getLogger(name)
    if not logger.handlers:
        
        logger.setLevel(logging.INFO)

        stream_handler = logging.StreamHandler()
        stream_formatter = ColorFormatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        stream_handler.setFormatter(stream_formatter)

        if not quiet_mode:
            logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_file_path, mode="a")
        file_formatter = DataInjectingFormatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        if not disable_file_logging:
            logger.addHandler(file_handler)
        txt = ""
        if quiet_mode:
            txt += "Logger initialized with quiet mode enabled, no logging to console. "
        else:
            txt += "Logger initialized, logging to console. "
        if disable_file_logging:
            txt += "File logging disabled. "
        else:
            txt += f"File logging enabled, writing to: {log_file_path} "
        logger.info(txt)

    return logger
