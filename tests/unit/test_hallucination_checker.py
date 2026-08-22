from tests import *

from brags.config_parser.data_types import HallucinationCheckerConfig
from brags.factories.hallucination.hallucinationCheckerFactory import HallucinationCheckerFactory
from brags.factories.hallucination.implementations.embeddingSimilarityChecker import (
    EmbeddingSimilarityChecker,
)
from brags.factories.chains.safe_chain import SafeRetrievalQA


class _FakeEmbedder:
    """Deterministic 2D embeddings so cosine similarity is easy to reason
    about: identical direction -> similarity 1.0, orthogonal -> 0.0.
    """

    VECTORS = {
        "grounded answer": [1.0, 0.0],
        "close context": [1.0, 0.1],
        "unrelated answer": [0.0, 1.0],
        "far context": [1.0, 0.0],
    }

    def embed_query(self, text):
        return self.VECTORS[text]

    def embed_documents(self, texts):
        return [self.VECTORS[t] for t in texts]


class _FakeDoc:
    def __init__(self, page_content):
        self.page_content = page_content


class TestHallucinationCheckerFactory(unittest.TestCase):
    def test_embedding_similarity_with_same_as_retriever_returns_checker(self):
        config = HallucinationCheckerConfig(
            enabled=True, same_as_retriever=True, method="embedding_similarity"
        )
        checker = HallucinationCheckerFactory.create(config, embedder=_FakeEmbedder())
        self.assertIsInstance(checker, EmbeddingSimilarityChecker)

    def test_same_as_retriever_false_raises_not_implemented(self):
        config = HallucinationCheckerConfig(
            enabled=True, same_as_retriever=False, method="embedding_similarity"
        )
        with self.assertRaises(NotImplementedError):
            HallucinationCheckerFactory.create(config, embedder=_FakeEmbedder())

    def test_unsupported_method_raises_not_implemented(self):
        config = HallucinationCheckerConfig(
            enabled=True, same_as_retriever=True, method="fact_checking"
        )
        with self.assertRaises(NotImplementedError):
            HallucinationCheckerFactory.create(config, embedder=_FakeEmbedder())


class TestEmbeddingSimilarityChecker(unittest.TestCase):
    def test_grounded_answer_is_not_flagged(self):
        config = HallucinationCheckerConfig(
            enabled=True, same_as_retriever=True, method="embedding_similarity", threshold=0.5
        )
        checker = EmbeddingSimilarityChecker(config, _FakeEmbedder())
        result = checker.check("grounded answer", [_FakeDoc("close context")])
        self.assertFalse(result["is_hallucination"])
        self.assertGreater(result["score"], 0.5)

    def test_ungrounded_answer_is_flagged(self):
        config = HallucinationCheckerConfig(
            enabled=True, same_as_retriever=True, method="embedding_similarity", threshold=0.5
        )
        checker = EmbeddingSimilarityChecker(config, _FakeEmbedder())
        result = checker.check("unrelated answer", [_FakeDoc("far context")])
        self.assertTrue(result["is_hallucination"])
        self.assertLess(result["score"], 0.5)

    def test_empty_source_documents_returns_none(self):
        config = HallucinationCheckerConfig(
            enabled=True, same_as_retriever=True, method="embedding_similarity"
        )
        checker = EmbeddingSimilarityChecker(config, _FakeEmbedder())
        result = checker.check("grounded answer", [])
        self.assertIsNone(result["is_hallucination"])


class TestSafeRetrievalQAHallucinationWiring(unittest.TestCase):
    def test_successful_call_attaches_hallucination_check(self):
        class _FakeQAChain:
            def __call__(self, query):
                return {"result": "grounded answer", "source_documents": [_FakeDoc("close context")]}

        config = HallucinationCheckerConfig(
            enabled=True, same_as_retriever=True, method="embedding_similarity", threshold=0.5
        )
        checker = EmbeddingSimilarityChecker(config, _FakeEmbedder())
        qa = SafeRetrievalQA(_FakeQAChain(), hallucination_checker=checker)

        result = qa("some query")
        self.assertIn("hallucination_check", result)
        self.assertFalse(result["hallucination_check"]["is_hallucination"])

    def test_no_checker_configured_omits_hallucination_check(self):
        class _FakeQAChain:
            def __call__(self, query):
                return {"result": "answer", "source_documents": []}

        qa = SafeRetrievalQA(_FakeQAChain())
        result = qa("some query")
        self.assertNotIn("hallucination_check", result)
