import os
import logging

from langchain_community.vectorstores import FAISS

from ....config_parser.data_types import VectorStoreConfig
from ...baseclasses.basevectorstore import BaseVectorStore


class FaissVectorStore(BaseVectorStore):
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.logger = logging.getLogger("Adora")

    def create(self, embedder, documents=None, save_if_not_local=False):
        if documents:
            store = FAISS.from_documents(documents, embedder)
            self.logger.info("VectorStore: Documents provided to the vector store, using them instead of local")
            if save_if_not_local and self.config.persist_path:
                self.logger.info("Saving data to disk")
                os.makedirs(self.config.persist_path, exist_ok=True)
                store.save_local(self.config.persist_path)
                self.logger.info("Saving data complete") 

            return store
        else:
            self.logger.info("VectorStore: Documents not provided, reading from disk")
            self.logger.info(f"Current configs: {self.config.persist_path}, embedder_type: {type(embedder)}, allow_dangerous_deserialization: {self.config.allow_dangerous_deserialization}")
            return FAISS.load_local(self.config.persist_path, embedder, allow_dangerous_deserialization=self.config.allow_dangerous_deserialization)