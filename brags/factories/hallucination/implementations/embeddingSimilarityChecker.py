import logging
from typing import Any

from ....config_parser.data_types import HallucinationCheckerConfig
from ...baseclasses.basehallucinationchecker import BaseHallucinationChecker

DEFAULT_THRESHOLD = 0.5


class EmbeddingSimilarityChecker(BaseHallucinationChecker):
    """Flags an answer as a likely hallucination when it's not semantically
    close to any of the retrieved source chunks it's supposed to be grounded
    in. Cheapest method available -- reuses an already-constructed embedder,
    no extra LLM call.
    """

    def __init__(self, config: HallucinationCheckerConfig, embedder):
        self.config = config
        self.embedder = embedder
        self.threshold = config.threshold if config.threshold is not None else DEFAULT_THRESHOLD
        self.logger = logging.getLogger("EmbeddingSimilarityChecker")

    def check(self, answer: str, source_documents: list[Any]) -> dict:
        if not answer or not source_documents:
            return {"is_hallucination": None, "score": None, "method": "embedding_similarity"}

        answer_vec = self.embedder.embed_query(answer)
        context_vecs = self.embedder.embed_documents(
            [doc.page_content for doc in source_documents]
        )

        best_score = max(_cosine_similarity(answer_vec, vec) for vec in context_vecs)
        is_hallucination = best_score < self.threshold

        if is_hallucination:
            self.logger.warning(
                f"Answer's best similarity to retrieved context ({best_score:.3f}) is "
                f"below threshold ({self.threshold}) -- may be ungrounded."
            )

        return {
            "is_hallucination": is_hallucination,
            "score": best_score,
            "method": "embedding_similarity",
        }


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
