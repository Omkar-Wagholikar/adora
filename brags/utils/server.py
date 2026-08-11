import logging
import os
import subprocess
import sys
from pathlib import Path

import requests

logger = logging.getLogger("SERVER")


def spawn_server(server_path: str):
    logger.info("Spawning Go server...")
    # stdout/stderr=PIPE would connect the Go server to an anonymous pipe
    # that nothing ever reads (brags init/watch are one-shot commands, not
    # daemons that stay around to drain it) -- once this Python process
    # exits, the pipe's read end closes, and the *next* time the Go process
    # writes anything to stdout/stderr (its own "Server running at ..."
    # banner, or any log line from the file watcher), that write raises
    # SIGPIPE and kills the server outright. This was silently killing the
    # server shortly after every `brags init`/`brags watch` invocation --
    # confirmed by spawning it the same way directly and watching it die the
    # instant a real write happened, versus staying alive indefinitely when
    # given a real file instead of a pipe (files have no "reader" to lose).
    log_path = Path(server_path).parent / "go_server_stdout.log"
    log_file = open(log_path, "a")
    try:
        process = subprocess.Popen(
            [server_path],
            stdout=log_file,
            stderr=log_file,
            # The Go server's file watcher shells out to `python3` (a bare
            # PATH lookup, go/callPython/performFileOp.go) to run its
            # ingestion bridge script -- whatever `python3` happens to
            # resolve first on PATH may not be the interpreter brags is
            # actually installed into (e.g. a venv, --user install, or
            # pipx). Passing this down lets the Go side prefer the exact
            # interpreter that's running right now instead of guessing.
            env={**os.environ, "BRAGS_PYTHON_EXECUTABLE": sys.executable},
        )
        logger.info(f"Go server spawned with PID: {process.pid} (its stdout/stderr: {log_path})")
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
