from pathlib import Path
import sys
import time
import requests
import subprocess
import os

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
    if not check_server_status():
        print("Server not detected. Attempting to start...")
        server_path = "/home/omkar/rag_check/brags/brags/bin/server_executable"
        spawn_server(server_path)

        for i in range(20):
            spawn_server(server_path)
            if check_server_status():
                print("Server successfully started and is now running.")
                return
            print(i)
            time.sleep(1)

        if check_server_status():
            print("Server successfully started and is now running.")
        else:
            print("Server spawned, but failed to become responsive.")
            sys.exit(1)


def spawn_server(server_path: str):
    print("Spawning Go server...")
    try:
        process = subprocess.Popen([server_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(f"Go server spawned with PID: {process.pid}")
    except FileNotFoundError:
        print(f"Error: Executable not found at '{server_path}'.")
        print("Please ensure the Go executable is built and at the correct path.")
        sys.exit(1)

def check_server_status():
    try:
        print("Making request to ping server...")
        res = requests.get("http://localhost:8011/ping")
        res.raise_for_status()
        body = res.json()
        message = body.get("message")

        if message == "pong":
            print("Server is running and healthy.")
            return True
        else:
            print(f"Server responded unexpectedly. Message: '{message}'")
            return False
    except Exception as e:
        print("Connection failed:", e)
        return False
