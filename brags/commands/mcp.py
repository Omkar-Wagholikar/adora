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

    # Imported lazily to avoid paying the mcp SDK's import cost on every
    # `brags` invocation regardless of subcommand -- it's a base dependency
    # now (not an optional extra), but brags/__main__.py's command
    # auto-discovery still eagerly imports every command module's top-level
    # imports, so this only actually gets pulled in when `brags mcp` runs.
    from ..mcp.server import run as run_server
    run_server(config)
