from tests import *

from brags.factories.chains.reranking_retriever import RerankingRetriever


class _FakeDoc:
    def __init__(self, page_content):
        self.page_content = page_content

    def __eq__(self, other):
        return isinstance(other, _FakeDoc) and self.page_content == other.page_content

    def __repr__(self):
        return f"_FakeDoc({self.page_content!r})"


class _FakeBaseRetriever:
    def __init__(self, docs):
        self.docs = docs

    def invoke(self, query, config=None):
        return self.docs


class _FakeReranker:
    """Reverses the candidate order and truncates to top_k, so tests can
    assert the retriever actually applies the reranker's output rather than
    just passing the base retriever's results through.
    """

    def rerank(self, query, documents, top_k):
        reversed_docs = list(reversed(documents))
        return [(doc, 1.0) for doc in reversed_docs[:top_k]]


class TestRerankingRetriever(unittest.TestCase):
    def test_applies_reranker_and_truncates_to_top_k(self):
        docs = [_FakeDoc("a"), _FakeDoc("b"), _FakeDoc("c"), _FakeDoc("d")]
        retriever = RerankingRetriever(
            base_retriever=_FakeBaseRetriever(docs),
            reranker=_FakeReranker(),
            top_k=2,
            fetch_k=4,
        )
        result = retriever.invoke("some query")
        self.assertEqual(result, [_FakeDoc("d"), _FakeDoc("c")])

    def test_truncates_candidates_to_fetch_k_before_reranking(self):
        docs = [_FakeDoc(str(i)) for i in range(10)]
        retriever = RerankingRetriever(
            base_retriever=_FakeBaseRetriever(docs),
            reranker=_FakeReranker(),
            top_k=2,
            fetch_k=3,
        )
        result = retriever.invoke("some query")
        # Only the first 3 candidates should ever reach the reranker, so the
        # reversed-top-2 must come from within docs[0:3], not docs[7:10].
        self.assertEqual(result, [_FakeDoc("2"), _FakeDoc("1")])
