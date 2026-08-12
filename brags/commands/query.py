from pathlib import Path
import logging

from ..config_parser.parser import load_config
from ..config_parser.data_types import RAGConfig
from ..utils.logging_setup import setup_logging
from ..pipeline.assembler import get_docs, build_qa_system


def add_parser(subparsers):
    parser = subparsers.add_parser("query", help="Ask a question against the ingested documents")
    parser.add_argument(
        "--query",
        type=str,
        # required=True,
        default=None,
        help="The query/question to ask.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent.parent / "rag_config.yaml",
        help="Path to configuration YAML.",
    )
    
    parser.add_argument(
        "--docs",
        type=str,
        default=None,
        help="Path to document(s) to ingest (PDF, text, etc.).",
    )
    parser.set_defaults(func=run)

def run(args):
    qa, logger = get_qa_object(config_path=args.config, docs_path=args.docs)
    logger.info(f"Querying with: {args.query} using config {args.config}")

    if args.query is not None:
        logger.info(f"Asking query: {args.query}")
        res = qa(args.query)
        logger.info(f"Got result: {res}")
        print_result(res)

    else:
        logger.info("Initiating REPL")
        repl(qa, logger)

    logger.info("query complete completed")


def print_result(res: dict):
    # SafeRetrievalQA (safe_chain.py) catches errors at the LLM/combine step
    # -- an invalid API key, a rate limit, etc. -- and falls back to
    # "I don't know" with no other detail. Retrieval itself may well have
    # succeeded even though the LLM call failed, so show the real error and
    # whatever chunks were retrieved instead of a bare, undiagnosable
    # "I don't know".
    if res.get("error"):
        print(f"No answer available -- the LLM step failed: {res['error']}\n")
        docs = res.get("source_documents") or []
        if docs:
            print(f"Retrieved {len(docs)} relevant chunk(s) (no LLM summary, since that step failed):\n")
            for doc in docs:
                source = doc.metadata.get("source", "unknown")
                print(f"--- {source} ---\n{doc.page_content}\n")
        else:
            print("No chunks were retrieved either.\n")
    else:
        print(f"Answer: {res['result']}\n")

def get_qa_object(config_path: Path, docs_path: str | None = None):
    config: RAGConfig = load_config(config_path)
    
    setup_logging(config.logging)
    logger = logging.getLogger("QUERY") 

    logger.info("Running Brags...")
    docs = get_docs(docs_path, config) if docs_path else None

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
                logger.info(f"Got result: {res}")
                print_result(res)
            except Exception as e:
                logger.error(f"Error while processing query: {e}", exc_info=True)
                print(f"Error: {e}")
    except KeyboardInterrupt:
        logger.info("REPL interrupted by user. Exiting.")
