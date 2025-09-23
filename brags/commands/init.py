import logging
from pathlib import Path
import sys
import time
import requests
import subprocess

from ..config_parser.data_types import RAGConfig
from ..config_parser.parser import load_config
from ..utils.logging_setup import setup_logging

logger = None

def add_parser(subparsers):
    parser = subparsers.add_parser("init", help="Initialize configuration")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent.parent / "rag_config.yaml",
        help="Path to configuration YAML (default: rag_config.yaml in project root).",
    )
    parser.set_defaults(func=run)

def run(args):
    config_path=args.config
    config: RAGConfig = load_config(config_path)
    
    setup_logging(config.logging)
    global logger
    logger = logging.getLogger("INIT") 

    logger.info("Running Brags init...")
    server_prev_working = True
    if not check_server_status():
        server_prev_working = False
        logger.info("Server not detected. Attempting to start...")
        server_path = "/home/omkar/rag_check/brags/brags/bin/server_executable"
        create_active_watcher_if_not_exist = open("/home/omkar/rag_check/brags/brags/bin/ActiveWatcherList", "r+")
        logger.info("spawning server")
        spawn_server(server_path)
        logger.info("going to sleep")
        time.sleep(10)
        logger.info("woke up")


        if not server_prev_working and check_server_status():
            print("Server successfully started and is now running.")
            return
        else:
            print("Server spawned, but failed to become responsive.")
            sys.exit(1)

    print("Server was already running")


def spawn_server(server_path: str):
    logger.info("Spawning Go server...")
    try:
        process = subprocess.Popen([server_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Go server spawned with PID: {process.pid}")
    except FileNotFoundError:
        logger.info(f"Error: Executable not found at '{server_path}'.")
        logger.info("Please ensure the Go executable is built and at the correct path.")
        sys.exit(1)

def check_server_status():
    try:
        logger.info("Making request to ping server...")
        res = requests.get("http://localhost:8011/ping", timeout=2)
        res.raise_for_status()

        body = res.json()
        message = body.get("message")

        if message == "pong":
            logger.info("Server is running and healthy.")
            return True
        else:
            logger.error("Server responded unexpectedly. Message: '%s'", message)
            return False

    except requests.exceptions.RequestException as e:
        # Network / HTTP / connection errors
        logger.warning("Server not reachable: %s", str(e))
        return False
    except ValueError as e:
        # JSON decode errors
        logger.error("Invalid response from server: %s", str(e))
        return False
    except Exception as e:
        # Catch-all (no console print)
        logger.error("Unexpected error while checking server status: %s", str(e))
        return False
