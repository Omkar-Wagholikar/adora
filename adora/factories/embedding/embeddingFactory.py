from adora.config_parser.data_types import EmbeddingConfig
from adora.factories.baseclasses.baseembedding import BaseEmbedding
from .implementations.huggingFaceEmbedding import HuggingFaceEmbedding


class EmbeddingFactory:
    @staticmethod
    def create(config: EmbeddingConfig) -> BaseEmbedding:
        if config.provider == "huggingface":
            return HuggingFaceEmbedding(config)
        raise ValueError(f"Unsupported embedding provider: {config.provider}")
