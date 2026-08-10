from tests import *

from langchain.docstore.document import Document
from brags.config_parser.data_types import RerankingConfig
from brags.factories.reranking.rerankerFactory import RerankerFactory


class TestCrossEncoderReranker(unittest.TestCase):
    def test_rerank_orders_by_relevance(self):
        config = RerankingConfig(enabled=True)
        reranker = RerankerFactory.create(config)

        docs = [
            Document(page_content="def add(a, b): return a + b"),
            Document(page_content="def greet(name): return f'Hello {name}'"),
        ]
        results = reranker.rerank("function that greets a user by name", docs, top_k=1)

        self.assertEqual(len(results), 1)
        doc, score = results[0]
        self.assertIn("greet", doc.page_content)
        self.assertIsInstance(score, float)

    def test_rerank_respects_top_k(self):
        config = RerankingConfig(enabled=True)
        reranker = RerankerFactory.create(config)
        docs = [Document(page_content=f"doc {i}") for i in range(5)]
        results = reranker.rerank("query", docs, top_k=2)
        self.assertEqual(len(results), 2)

    def test_rerank_empty_input(self):
        config = RerankingConfig(enabled=True)
        reranker = RerankerFactory.create(config)
        self.assertEqual(reranker.rerank("query", [], top_k=3), [])

    def test_unsupported_provider_raises(self):
        config = RerankingConfig(enabled=True, provider="not-a-real-provider")
        with self.assertRaises(ValueError):
            RerankerFactory.create(config)
