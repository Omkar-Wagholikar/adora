from ...baseclasses.basevectorstore import BaseVectorStore
from langchain_community.vectorstores import FAISS

class FaissVectorStore(BaseVectorStore):
    def __init__(self, config):
        self.config = config

    def create(self, embedder, documents=None):
        if documents:
            return FAISS.from_documents(documents, embedder)
        else:
            return FAISS.load_local(self.config.persist_path, embedder)