import os
import sys
import logging
from pathlib import Path
from brags.config_parser.parser import load_config
from brags.config_parser.data_types import RAGConfig
from brags.factories.vectorStore.vector_store_factory import VectorStoreFactory
from brags.factories.embedding.embeddingFactory import EmbeddingFactory
from brags.pipeline.assembler import get_docs
from brags.utils.logging_setup import setup_logging

# This script is invoked by the Go watcher (go/callPython/performFileOp.go) as a
# standalone subprocess, so it can't rely on the caller's working directory.
# BRAGS_CONFIG_PATH lets a deployment point at a specific config; otherwise fall
# back to the config that lives next to this script in the source/build tree.
#
# __file__ is .../brags/bin/pythonFiles/vector_store_updater.py in both a
# source checkout and an installed package (build.sh copies pythonFiles/
# into brags/bin/ either way), so parent.parent.parent is the `brags`
# package directory itself -- rag_config.yaml lives directly under that, not
# under an extra nested "brags" segment (previously computed
# .../brags/brags/rag_config.yaml, which never existed).
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "rag_config.yaml"


def update_vector_store(event_type: str, file_path: str):
    config_path = os.environ.get("BRAGS_CONFIG_PATH", str(DEFAULT_CONFIG_PATH))
    config: RAGConfig = load_config(config_path)

    setup_logging(config.logging)
    logger = logging.getLogger("update_vector_store")

    vs_config = config.vector_store
    vector_store = VectorStoreFactory.create(vs_config)

    # Create embedder
    embedder = EmbeddingFactory.create(config.embedding).create()

    if event_type in ("CREATE", "WRITE"):
        logger.info(f"Adding/updating file in vector store: {file_path}")
        docs = get_docs(file_path, config)
        store = vector_store.create(embedder, docs, save_if_not_local=True)

    elif event_type in ("REMOVE", "RENAME"):
        logger.info(f"Removing file from vector store: {file_path}")
        vector_store.remove_by_path(embedder, file_path)

    else:
        logger.info(f"Unhandled event: {event_type}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: test.py <EVENT_TYPE> <FILE_PATH>")
        sys.exit(1)

    event_type, file_path = sys.argv[1], sys.argv[2]
    update_vector_store(event_type, file_path)
