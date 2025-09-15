from abc import ABC, abstractmethod
from typing import Any

class BaseEmbedding(ABC):
    @abstractmethod
    def create(self) -> Any:
        """Return a LangChain Embedding instance"""
        pass