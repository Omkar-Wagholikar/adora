from brags.config_parser.data_types import LLMConfig
from brags.factories.baseclasses.basellm import BaseLLM
from .implementations.googleGenAILLM import GoogleGenAILLM
from .implementations.ollamaLLM import OllamaLLM
from .implementations.claudeLLM import ClaudeLLM
from .implementations.openaiLLM import OpenAILLM


class LLMFactory:
    @staticmethod
    def create(config: LLMConfig) -> BaseLLM:
        if config.provider == "gemini":
            return GoogleGenAILLM(config)
        elif config.provider == "ollama":
            return OllamaLLM(config)
        elif config.provider == "claude":
            return ClaudeLLM(config)
        elif config.provider == "openai":
            return OpenAILLM(config)
        raise ValueError(f"Unsupported LLM provider: {config.provider}")
