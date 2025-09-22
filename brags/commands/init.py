from pathlib import Path

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
    print(f"Initializing config at {args.config}")
    # your init logic here
