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
        if documents:
            self.logger.info("ChromaVectorStore: Documents provided to the vector store, using them instead of local")

            store = Chroma.from_documents(
                documents=documents,
                embedding=embedder,
                persist_directory=self.config.persist_path,
            )

            if save_if_not_local and self.config.persist_path:
                os.makedirs(self.config.persist_path, exist_ok=True)
                self.logger.info("Saving data to disk")
                store.persist()
                self.logger.info("Saving data complete")
                # Make sure everything is flushed
                store = Chroma(
                    persist_directory=self.config.persist_path,
                    embedding_function=embedder,
                )

            return store
        else:
            self.logger.info("ChromaVectorStore: Documents not provided, reading from disk")
            self.logger.info(f"Current configs: {self.config.persist_path}, embedder_type: {type(embedder)}, allow_dangerous_deserialization: {self.config.allow_dangerous_deserialization}")
            return Chroma(
                persist_directory=self.config.persist_path,
                embedding_function=embedder,
            )
