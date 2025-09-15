from ...config_parser.data_types import VectorStoreConfig
from ..baseclasses.basevectorstore import BaseVectorStore
from .implementations.chroma_vector_store import ChromaVectorStore
from .implementations.faiss_vector_store import FaissVectorStore

class VectorStoreFactory:
    @staticmethod
    def create(config: VectorStoreConfig) -> BaseVectorStore:
        if config.type == "faiss":
            return FaissVectorStore(config)
        elif config.type == "chroma":
            return ChromaVectorStore(config)
        raise ValueError(f"Unsupported vector store type: {config.type}")