import os
import logging

from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

from ....config_parser.data_types import VectorStoreConfig
from ...baseclasses.basevectorstore import BaseVectorStore


class FaissVectorStore(BaseVectorStore):
    def __init__(self, config: VectorStoreConfig):
        self.config = config
        self.logger = logging.getLogger("FaissVectorStore")

    def create(self, embedder, documents=None, save_if_not_local=False):
        if documents:
            for d in documents:
                if "source" not in d.metadata:
                    d.metadata["source"] = "unknown"

        try:
            # Try to load existing store
            store = FAISS.load_local(
                self.config.persist_path,
                embedder,
                allow_dangerous_deserialization=self.config.allow_dangerous_deserialization,
            )
            self.logger.info("FaissVectorStore: Loaded existing vector store from disk")

            if documents:
                store.add_documents(documents)
                self.logger.info("FaissVectorStore: Added new documents to existing store")
        except Exception as e:
            if documents:
                # Build the fresh store straight from the real documents --
                # seeding it with a "dummy" placeholder Document (the
                # previous approach) left that placeholder permanently
                # polluting every future similarity search alongside genuine
                # results, since nothing ever removed it once real
                # documents were added.
                store = FAISS.from_documents(documents, embedder)
                self.logger.info(
                    f"FaissVectorStore: No existing store found, created new one from "
                    f"{len(documents)} document(s). Reason: {e}"
                )
            else:
                dummy_doc = Document(page_content="dummy", metadata={"source": "dummy"})
                store = FAISS.from_documents([dummy_doc], embedder)
                self.logger.info(
                    f"FaissVectorStore: No existing store and no documents to ingest -- "
                    f"creating empty placeholder store. Reason: {e}"
                )

        if documents and save_if_not_local and self.config.persist_path:
            os.makedirs(self.config.persist_path, exist_ok=True)
            store.save_local(self.config.persist_path)
            self.logger.info("FaissVectorStore: Saving updated store to disk complete")

        return store
        
    def remove_by_path(self, embedder, path: str):
        """Remove all documents with metadata['source'] == path from the FAISS store."""
        self.logger.info(f"FaissVectorStore: Removing documents from path={path}")

        store = FAISS.load_local(
            self.config.persist_path,
            embedder,
            allow_dangerous_deserialization=self.config.allow_dangerous_deserialization,
        )

        # Extract all documents
        docs = store.docstore._dict  # internal dict: {id: Document}
        filtered_docs = [doc for doc in docs.values() if doc.metadata.get("source") != path]

        # Rebuild FAISS index
        if filtered_docs:
            new_store = FAISS.from_documents(filtered_docs, store.embedding_function)
        else:
            dummy_doc = Document(page_content="dummy", metadata={"source": "dummy"})
            new_store = FAISS.from_documents([dummy_doc], store.embedding_function)

        # Save back
        if self.config.persist_path:
            os.makedirs(self.config.persist_path, exist_ok=True)
            new_store.save_local(self.config.persist_path)
            self.logger.info("FaissVectorStore: Updated store saved after deletion")

        return new_store