import logging

from ....config_parser.data_types import RerankingConfig
from ...baseclasses.basereranker import BaseReranker


class CrossEncoderReranker(BaseReranker):
    def __init__(self, config: RerankingConfig):
        self.config = config
        self.logger = logging.getLogger("CrossEncoderReranker")
        # Lazy-loaded: sentence_transformers.CrossEncoder downloads/loads a
        # real model, which shouldn't happen just because reranking.enabled
        # is set -- only once rerank() is actually called.
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import CrossEncoder
            self.logger.info(f"Loading cross-encoder model: {self.config.model_name}")
            self._model = CrossEncoder(self.config.model_name)
        return self._model

    def rerank(self, query, documents, top_k):
        if not documents:
            return []

        model = self._get_model()
        pairs = [(query, doc.page_content) for doc in documents]
        scores = model.predict(pairs)

        ranked = sorted(zip(documents, scores), key=lambda pair: pair[1], reverse=True)
        return [(doc, float(score)) for doc, score in ranked[:top_k]]
