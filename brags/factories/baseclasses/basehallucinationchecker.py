from abc import ABC, abstractmethod
from typing import Any


class BaseHallucinationChecker(ABC):
    @abstractmethod
    def check(self, answer: str, source_documents: list[Any]) -> dict:
        """Return {"is_hallucination": bool, "score": float, "method": str}."""
        pass
