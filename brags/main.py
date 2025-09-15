import argparse
from pathlib import Path
import logging

from .config_parser.data_types import RAGConfig
from .config_parser.parser import load_config
from .factories.llm.llmFactory import LLMFactory
from .pipeline.assembler import get_docs, build_qa_system
from .utils.logging_setup import setup_logging

# please run this to install the python part of the package locally so that it interfaces with the go hlaf correctly
# pip install -e .

# clear && python -m adora.main

# # Run with a query
# python -m adora.main --query "What is in the document?"

# # Run with a custom config
# python -m adora.main --config ./adora/rag_config.yaml --query "Summarize this document"

# # Run with new/ specific files:
# clear && python -m adora.main --query "What is in the document?" --docs "/home/omkar/rag_check/adora/testFiles/test2.pdf"



logger = logging.getLogger("Adora")
def get_qa_object(config_path: Path, docs_path: str | None = None):
    config: RAGConfig = load_config(config_path)
    setup_logging(config.logging)

    logger.info("Running Adora...")
    docs = get_docs(docs_path) if docs_path else None

    logger.info("Setting up pipeline...")
    qa = build_qa_system(config=config, documents=docs)

    return qa


def main():
    parser = argparse.ArgumentParser(
        prog="adora",
        description="Adora: RAG-powered document QA system",
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
        required=True,
        help="The query/question to ask.",
    )

    args = parser.parse_args()

    qa = get_qa_object(config_path=args.config, docs_path=args.docs)

    logger.info(f"Asking query: {args.query}")
    res = qa(args.query)
    logger.info(f"Got result: {res}")

    print("\n=== Answer ===")
    print(res['result'])
    print("==============\n")


if __name__ == "__main__":
    main()