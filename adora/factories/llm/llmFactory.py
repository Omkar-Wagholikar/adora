from config_parser.data_types import LLMConfig
from factories.baseclasses.basellm import BaseLLM
from implementations.googleGenAILLM import GoogleGenAILLM
from implementations.ollamaLLM import OllamaLLM


class LLMFactory:
    @staticmethod
    def create(config: LLMConfig) -> BaseLLM:
        if config.provider == "google":
            return GoogleGenAILLM(config)
        elif config.provider == "ollama":
            return OllamaLLM(config)
        raise ValueError(f"Unsupported LLM provider: {config.provider}")
