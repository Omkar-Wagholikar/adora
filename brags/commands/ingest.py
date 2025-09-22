from pathlib import Path
import logging


from ..config_parser.parser import load_config
from ..factories.embedding.embeddingFactory import EmbeddingFactory
from ..factories.vectorStore.vector_store_factory import VectorStoreFactory
from ..pipeline.assembler import get_docs
from ..config_parser.data_types import RAGConfig
from ..config_parser.parser import load_config
from ..utils.logging_setup import setup_logging

def add_parser(subparsers):
    parser = subparsers.add_parser("ingest", help="Ingest documents into the system")
    parser.add_argument(
        "--docs",
        type=str,
        required=True,
        help="Path to document(s) to ingest (PDF, text, etc.).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent.parent / "rag_config.yaml",
        help="Path to configuration YAML.",
    )
    parser.set_defaults(func=run)

def run(args):
    config_path = args.config
    config: RAGConfig = load_config(config_path)

    setup_logging(config.logging)
    logger = logging.getLogger("Brags") 
    
    logger.info(f"Ingesting documents from {args.docs} using config {args.config}")
    
    docs_path = args.docs
    documents = get_docs(docs_path) if docs_path else None
    embedder = EmbeddingFactory.create(config=config.embedding).create()
    VectorStoreFactory.create(config=config.vector_store).create(embedder=embedder, documents=documents, save_if_not_local=config.vector_store.save_if_not_local)
    
    logger.info("Ingestion completed")
