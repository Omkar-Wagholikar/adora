from abc import ABC, abstractmethod
from typing import Any

class BaseVectorStore(ABC):
    @abstractmethod
    def create(self, embedder: Any, documents: list = None, save_if_not_local=False) -> Any:
        """Return a LangChain VectorStore instance"""
        pass