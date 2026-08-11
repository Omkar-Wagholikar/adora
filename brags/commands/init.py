import logging
import platform
from pathlib import Path
import shutil
import sys
import time

from ..config_parser.data_types import RAGConfig
from ..config_parser.parser import load_config
from ..utils.logging_setup import setup_logging
from ..utils.server import check_server_status, spawn_server

logger = None

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "rag_config.yaml"
EXAMPLE_CONFIG_PATH = Path(__file__).parent.parent / "rag_config.example.yaml"

def add_parser(subparsers):
    parser = subparsers.add_parser("init", help="Initialize configuration")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to configuration YAML (default: rag_config.yaml in project root).",
    )
    parser.set_defaults(func=run)

def run(args):
    config_path = args.config

    # Only bootstrap when the user left --config at its implicit default --
    # an explicit path that happens not to exist (e.g. a typo) should still
    # surface a real error rather than silently creating a file at the wrong
    # location.
    if config_path == DEFAULT_CONFIG_PATH and not config_path.exists():
        shutil.copyfile(EXAMPLE_CONFIG_PATH, config_path)
        print(f"No config found -- created a default one at {config_path}.")
        print("Review it and set your LLM API keys before running ingest/query.")

    config: RAGConfig = load_config(config_path)
    
    setup_logging(config.logging)
    global logger
    logger = logging.getLogger("INIT") 

    logger.info("Running Brags init...")
    if not check_server_status():
        logger.info("Server not detected. Attempting to start...")
        binary_name = "server_executable.exe" if platform.system() == "Windows" else "server_executable"
        server_path = str(Path(__file__).parent.parent / "bin" / binary_name)
        logger.info("spawning server")
        spawn_server(server_path)
        logger.info("going to sleep")
        time.sleep(10)
        logger.info("woke up")

        if check_server_status():
            print("Server successfully started and is now running.")
            return
        else:
            print("Server spawned, but failed to become responsive.")
            sys.exit(1)

    print("Server was already running")
