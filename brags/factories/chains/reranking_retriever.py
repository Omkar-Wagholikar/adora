from typing import Any

from pydantic import ConfigDict
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.retrievers import BaseRetriever


class RerankingRetriever(BaseRetriever):
    """Wraps a base vector-store retriever with an over-fetch + rerank pass.

    Fetches `fetch_k` candidates from the wrapped retriever (more than the
    final `top_k` wanted), then asks the reranker to reorder and truncate
    them. Reranking can only reorder what it's given, so fetch_k needs to be
    larger than top_k for reranking to actually change the result set.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    base_retriever: Any
    reranker: Any
    top_k: int
    fetch_k: int

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> list:
        candidates = self.base_retriever.invoke(
            query, config={"callbacks": run_manager.get_child()}
        )
        if len(candidates) > self.fetch_k:
            candidates = candidates[: self.fetch_k]
        reranked = self.reranker.rerank(query, candidates, top_k=self.top_k)
        return [doc for doc, _score in reranked]
