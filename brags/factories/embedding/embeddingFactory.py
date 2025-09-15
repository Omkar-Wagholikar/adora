from brags.config_parser.data_types import EmbeddingConfig
from brags.factories.baseclasses.baseembedding import BaseEmbedding
from .implementations.huggingFaceEmbedding import HuggingFaceEmbedding
from .implementations.ensembleEmbedding import EnsembleEmbedding


class EmbeddingFactory:
    @staticmethod
    def create(config: EmbeddingConfig) -> BaseEmbedding:
        if config.provider == "huggingface":
            return HuggingFaceEmbedding(config)
        elif config.provider == "ensemble":
            return EnsembleEmbedding(config)
        raise ValueError(f"Unsupported embedding provider: {config.provider}")
