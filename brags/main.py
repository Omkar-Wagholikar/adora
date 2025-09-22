import argparse
from pathlib import Path
import logging

from .config_parser.data_types import RAGConfig
from .config_parser.parser import load_config
from .pipeline.assembler import get_docs, build_qa_system
from .utils.logging_setup import setup_logging

# please run this to install the python part of the package locally so that it interfaces with the go hlaf correctly
# pip install -e .

# clear && python -m brags.main

# # Run with a query
# python -m brags.main --query "What is in the document?"

# # Run with a custom config
# python -m brags.main --config ./brags/rag_config.yaml --query "Summarize this document"

# # Run with new/ specific files:
# clear && python -m brags.main --query "What is in the document?" --docs "/home/omkar/rag_check/brags/testFiles/test2.pdf"




def get_qa_object(config_path: Path, docs_path: str | None = None):
    config: RAGConfig = load_config(config_path)
    
    setup_logging(config.logging)
    logger = logging.getLogger("Brags") 

    logger.info("Running Brags...")
    docs = get_docs(docs_path) if docs_path else None

    logger.info("Setting up pipeline...")
    qa = build_qa_system(config=config, documents=docs)

    return qa, logger


def repl(qa, logger):
    """Interactive REPL for asking queries to the QA system."""
    logger.info("Entering interactive REPL. Type 'exit' or 'quit' to leave.")
    try:
        while True:
            query = input("\n>>> ").strip()
            if query.lower() in {"exit", "quit"}:
                logger.info("Exiting REPL.")
                break
            if not query:
                continue

            logger.info(f"Asking query: {query}")
            try:
                res = qa(query)
                logger.info("=== Answer ===")
                logger.info(res["result"])
                logger.info("==============")
                print(f"\nAnswer: {res['result']}\n")
            except Exception as e:
                logger.error(f"Error while processing query: {e}", exc_info=True)
                print(f"Error: {e}")
    except KeyboardInterrupt:
        logger.info("REPL interrupted by user. Exiting.")

def main():
    parser = argparse.ArgumentParser(
        prog="brags",
        description="brags: RAG-powered document QA system",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "rag_config.yaml",
        help="Path to configuration YAML (default: rag_config.yaml in project root).",
    )
    parser.add_argument(
        "--docs",
        type=str,
        default=None,
        help="Path to document(s) to ingest (PDF, text, etc.).",
    )
    parser.add_argument(
        "--query",
        type=str,
        # required=True,
        default=None,
        help="The query/question to ask.",
    )

    args = parser.parse_args()

    qa, logger = get_qa_object(config_path=args.config, docs_path=args.docs)

    if args.query != None:
        logger.info(f"Asking query: {args.query}")
        res = qa(args.query)
        logger.info(f"Got result: {res}")

        logger.info("=== Answer ===")
        logger.info(res['result'])
        logger.info("==============")
    
    else:
        logger.info("Initiating REPL")
        repl(qa, logger)

if __name__ == "__main__":
    main()