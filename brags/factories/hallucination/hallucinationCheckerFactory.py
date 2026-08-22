from ...config_parser.data_types import HallucinationCheckerConfig
from ..baseclasses.basehallucinationchecker import BaseHallucinationChecker
from .implementations.embeddingSimilarityChecker import EmbeddingSimilarityChecker


class HallucinationCheckerFactory:
    @staticmethod
    def create(config: HallucinationCheckerConfig, embedder) -> BaseHallucinationChecker:
        if config.method == "embedding_similarity":
            # same_as_retriever governs where the embedder comes from -- the
            # caller is responsible for passing the retrieval embedder when
            # True. When False, a checker-specific provider/model_name is
            # requested but not yet implemented (only reusing the retrieval
            # embedder is supported today).
            if not config.same_as_retriever:
                raise NotImplementedError(
                    "hallucination_checker.same_as_retriever=false is not yet "
                    "supported -- only reusing the retrieval embedding provider "
                    "(same_as_retriever: true) is implemented for method "
                    "'embedding_similarity'."
                )
            return EmbeddingSimilarityChecker(config, embedder)
        raise NotImplementedError(
            f"hallucination_checker.method '{config.method}' is not yet implemented -- "
            "only 'embedding_similarity' is supported today."
        )
