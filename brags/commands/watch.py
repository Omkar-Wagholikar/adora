import logging
import platform
import time
from pathlib import Path

import requests

from ..config_parser.data_types import RAGConfig
from ..config_parser.parser import load_config
from ..utils.logging_setup import setup_logging
from ..utils.server import check_server_status, spawn_server


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "watch", help="Watch a file or directory and keep the vector store updated on change"
    )
    parser.add_argument("path", type=Path, help="File or directory path to watch")
    parser.add_argument(
        "--type",
        choices=["persistent", "cron"],
        default="persistent",
        help="Watcher type: persistent (live fsnotify) or cron (periodic poll). Default: persistent.",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=0,
        help="Polling period in seconds, only used when --type=cron. Default: 0.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent.parent / "rag_config.yaml",
        help="Path to configuration YAML.",
    )
    parser.set_defaults(func=run)


def run(args):
    config: RAGConfig = load_config(args.config)
    setup_logging(config.logging)
    logger = logging.getLogger("WATCH")

    if not check_server_status():
        logger.info("Server not detected. Attempting to start...")
        binary_name = "server_executable.exe" if platform.system() == "Windows" else "server_executable"
        server_path = str(Path(__file__).parent.parent / "bin" / binary_name)
        spawn_server(server_path)
        time.sleep(10)
        if not check_server_status():
            print("Server spawned, but failed to become responsive.")
            raise SystemExit(1)

    resp = requests.get(
        "http://localhost:8011/add_path",
        params={"path": str(args.path.resolve()), "type": args.type, "period": args.period},
        timeout=5,
    )
    resp.raise_for_status()
    print(f"Watching {args.path.resolve()} ({args.type}).")
    print(resp.json())
