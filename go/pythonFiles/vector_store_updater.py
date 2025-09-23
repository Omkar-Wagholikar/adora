import sys
import logging
from pathlib import Path
from brags.config_parser.parser import load_config
from brags.config_parser.data_types import RAGConfig
from brags.factories.vectorStore.vector_store_factory import VectorStoreFactory
from brags.factories.embedding.embeddingFactory import EmbeddingFactory
from brags.pipeline.assembler import get_docs
from brags.utils.logging_setup import setup_logging


def update_vector_store(event_type: str, file_path: str):
    # Load YAML config
    config:RAGConfig = load_config("/home/omkar/rag_check/brags/brags/rag_config.yaml")
    
    setup_logging(config.logging)
    logger = logging.getLogger("update_vector_store")

    vs_config = config.vector_store
    vector_store = VectorStoreFactory.create(vs_config)

    # Create embedder
    embedder = EmbeddingFactory.create(config.embedding).create()

    if event_type in ("CREATE", "WRITE"):
        logger.info(f"Adding/updating file in vector store: {file_path}")
        docs = get_docs(file_path)
        store = vector_store.create(embedder, docs, save_if_not_local=True)

    elif event_type in ("REMOVE", "RENAME"):
        logger.info(f"Removing file from vector store: {file_path}")
        

    else:
        logger.info(f"Unhandled event: {event_type}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: test.py <EVENT_TYPE> <FILE_PATH>")
        sys.exit(1)

    event_type, file_path = sys.argv[1], sys.argv[2]
    update_vector_store(event_type, file_path)
