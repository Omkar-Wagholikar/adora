import argparse
import importlib
import pkgutil
from pathlib import Path

def load_commands(subparsers):
    import brags.commands 

    for _, module_name, _ in pkgutil.iter_modules(brags.commands.__path__):
        module = importlib.import_module(f"brags.commands.{module_name}")
        if hasattr(module, "add_parser"):
            module.add_parser(subparsers)

def main():
    parser = argparse.ArgumentParser(
        prog="brags",
        description="brags: RAG-powered document QA system",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    load_commands(subparsers)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
