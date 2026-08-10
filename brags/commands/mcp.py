from pathlib import Path
import logging

from ..config_parser.parser import load_config
from ..config_parser.data_types import RAGConfig
from ..utils.logging_setup import setup_logging


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "mcp", help="Run brags as a stdio MCP server exposing a read-only search tool"
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
    logger = logging.getLogger("MCP")
    logger.info("Starting brags MCP server (stdio transport)...")

    # Imported lazily: the `mcp` SDK lives in pyproject.toml's optional "mcp"
    # poetry group, not the base install -- importing it at module load time
    # would make every `brags` CLI invocation crash for anyone who installed
    # brags without that extra group, the same bug fixed earlier for the
    # "ensemble" embedding provider.
    from ..mcp.server import run as run_server
    run_server(config)
