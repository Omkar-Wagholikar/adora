from ..baseclasses.basevectorstore import BaseVectorStore
from .implementations.faiss_vector_store import FaissVectorStore
from ...config_parser.data_types import VectorStoreConfig

class VectorStoreFactory:
    @staticmethod
    def create(config: VectorStoreConfig) -> BaseVectorStore:
        if config.type == "faiss":
            return FaissVectorStore(config)
        raise ValueError(f"Unsupported vector store type: {config.type}")