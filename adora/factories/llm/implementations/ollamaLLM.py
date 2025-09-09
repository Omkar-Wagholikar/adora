from langchain_community.llms import Ollama

from adora.config_parser.data_types import LLMConfig
from adora.factories.baseclasses.basellm import BaseLLM

class OllamaLLM(BaseLLM):
    def __init__(self, config: LLMConfig):
        self.config = config

    def create(self):
        return Ollama(
            model=self.config.model_name,
            base_url=self.config.ollama_host or "http://localhost:11434",
        )
