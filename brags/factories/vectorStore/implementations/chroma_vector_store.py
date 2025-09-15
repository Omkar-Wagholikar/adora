import os
import logging

from langchain_community.vectorstores import Chroma

from ....config_parser.data_types import VectorStoreConfig
from ...baseclasses.basevectorstore import BaseVectorStore


class ChromaVectorStore(BaseVectorStore):
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.logger = logging.getLogger("Adora")

    def create(self, embedder, documents=None, save_if_not_local=False):
        persist_path = self.config.persist_path
        os.makedirs(persist_path, exist_ok=True)

        if documents:
            self.logger.info("ChromaVectorStore: Adding documents to vector store")

            if os.path.exists(os.path.join(persist_path, "chroma.sqlite3")):
                # Load existing store
                store = Chroma(
                    persist_directory=persist_path,
                    embedding_function=embedder,
                )
                store.add_documents(documents)
                self.logger.info("ChromaVectorStore: Added documents to existing DB")
            else:
                # Create a new store
                store = Chroma.from_documents(
                    documents=documents,
                    embedding=embedder,
                    persist_directory=persist_path,
                )
                self.logger.info("ChromaVectorStore: Created new DB with provided documents")

            if save_if_not_local:
                self.logger.info("Saving Chroma DB to disk")
                store.persist()
                self.logger.info("ChromaVectorStore: Save complete")

            return store

        else:
            self.logger.info("ChromaVectorStore: Documents not provided, loading from disk")
            return Chroma(
                persist_directory=persist_path,
                embedding_function=embedder,
            )

    def remove_by_path(self, embedder, path: str):
        """Remove all documents with metadata['source'] == path from the Chroma store."""
        self.logger.info(f"ChromaVectorStore: Removing documents with source={path}")

        store = Chroma(
            persist_directory=self.config.persist_path,
            embedding_function=embedder,
        )

        # Delete by metadata
        store.delete(where={"source": path})
        store.persist()

        self.logger.info(f"ChromaVectorStore: Removed documents with source={path}")
        return store
