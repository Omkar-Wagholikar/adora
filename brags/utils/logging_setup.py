import logging
from pathlib import Path
from ..config_parser.data_types import LoggingConfig

def setup_logging(config: LoggingConfig):
    # Clear existing handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    log_level = getattr(logging, config.level.upper(), logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handlers = [logging.StreamHandler()]
    if config.log_to_file and config.log_file_path:
        log_path = Path(config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
        print(f"Logging to file: {config.log_file_path}")

    # A single basicConfig() call: logging.basicConfig() only takes effect
    # the *first* time it's called on a logger with no handlers (without
    # force=True), so calling it twice — once for the file handler, once for
    # the full handler list — silently dropped the console handler whenever
    # log_to_file was enabled, since the first call already "won".
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    logging.getLogger(__name__).info("Logging initialized with level %s", config.level)
