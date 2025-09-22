import argparse
from . import commands

def build_parser():
    parser = argparse.ArgumentParser(
        prog="brags",
        description="brags: RAG-powered document QA system",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # dynamically add subcommands
    commands.init.add_parser(subparsers)
    commands.ingest.add_parser(subparsers)
    commands.query.add_parser(subparsers)

    return parser
