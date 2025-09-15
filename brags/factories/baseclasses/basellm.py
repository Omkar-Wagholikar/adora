from abc import ABC, abstractmethod
from typing import Any

class BaseLLM(ABC):
    @abstractmethod
    def create(self) -> Any:
        """Return a LangChain LLM instance"""
        pass
