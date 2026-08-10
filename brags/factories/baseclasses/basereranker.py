from abc import ABC, abstractmethod
from typing import Any

class BaseReranker(ABC):
    @abstractmethod
    def rerank(self, query: str, documents: list[Any], top_k: int) -> list[tuple[Any, float]]:
        """Return up to top_k (document, relevance_score) pairs, most relevant first."""
        pass
