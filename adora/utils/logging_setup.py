import logging
from pathlib import Path
from ..config_parser.data_types import LoggingConfig

def setup_logging(config: LoggingConfig):
    # Clear existing handlers to avoid duplicate logs
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    log_level = getattr(logging, config.level.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]
    if config.log_to_file and config.log_file_path:
        log_path = Path(config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_path))

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
    )

    logging.getLogger(__name__).info("Logging initialized with level %s", config.level)
