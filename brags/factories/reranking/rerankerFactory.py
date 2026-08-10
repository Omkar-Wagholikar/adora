from ...config_parser.data_types import RerankingConfig
from ..baseclasses.basereranker import BaseReranker
from .implementations.crossEncoderReranker import CrossEncoderReranker


class RerankerFactory:
    @staticmethod
    def create(config: RerankingConfig) -> BaseReranker:
        if config.provider == "cross_encoder":
            return CrossEncoderReranker(config)
        raise ValueError(f"Unsupported reranking provider: {config.provider}")
