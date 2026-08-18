import shutil
import tempfile

from tests import *

from langchain.docstore.document import Document
from brags.config_parser.data_types import (
    RAGConfig,
    LLMConfig,
    EmbeddingConfig,
    VectorStoreConfig,
    ChunkingConfig,
    RerankingConfig,
    HallucinationCheckerConfig,
    LoggingConfig,
)
from brags.pipeline.assembler import retrieve_raw
from brags.factories.embedding.embeddingFactory import EmbeddingFactory
from brags.factories.vectorStore.vector_store_factory import VectorStoreFactory


def _build_config(persist_path: str) -> RAGConfig:
    return RAGConfig(
        llm=LLMConfig(provider="gemini", model_name="x", temperature=0.1, max_tokens=100),
        embedding=EmbeddingConfig(
            provider="huggingface",
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimensions=384,
            normalize=True,
        ),
        vector_store=VectorStoreConfig(
            type="faiss",
            persist_path=persist_path,
            similarity_metric="cosine",
            top_k=2,
            save_if_not_local=True,
            allow_dangerous_deserialization=True,
        ),
        chunking=ChunkingConfig(chunk_size=500, chunk_overlap=50, splitter="semantic"),
        reranking=RerankingConfig(enabled=False),
        hallucination_checker=HallucinationCheckerConfig(
            enabled=False, same_as_retriever=True, method="none"
        ),
        logging=LoggingConfig(level="warning", log_to_file=False),
        rag_mode="stuff",
        streaming=False,
        use_cache=False,
        debug=False,
    )


class TestRetrieveRaw(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config = _build_config(self.tmpdir)

        embedder = EmbeddingFactory.create(config=self.config.embedding).create()
        docs = [
            Document(page_content="def greet(name): return f'Hello {name}'", metadata={"source": "a.py"}),
            Document(page_content="def add(a, b): return a + b", metadata={"source": "b.py"}),
        ]
        VectorStoreFactory.create(config=self.config.vector_store).create(
            embedder=embedder, documents=docs, save_if_not_local=True
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_retrieve_returns_ranked_dicts_with_expected_shape(self):
        results = retrieve_raw(self.config, "function that greets someone", top_k=2)
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertIn("content", r)
            self.assertIn("metadata", r)
            self.assertIn("score", r)
        self.assertIn("greet", results[0]["content"])

    def test_retrieve_respects_top_k_override(self):
        results = retrieve_raw(self.config, "code", top_k=1)
        self.assertEqual(len(results), 1)

    def test_retrieve_with_reranking_enabled(self):
        self.config.reranking.enabled = True
        results = retrieve_raw(self.config, "function that greets someone", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("greet", results[0]["content"])

    def test_fresh_store_does_not_leak_dummy_placeholder(self):
        # FaissVectorStore.create used to always seed a brand-new store with
        # a {"source": "dummy"} placeholder Document before adding the real
        # ones, and nothing ever removed it -- every subsequent search
        # returned it alongside genuine results. Once real documents are
        # supplied, the store should be built from them directly.
        results = retrieve_raw(self.config, "greet add function", top_k=5)
        contents = [r["content"] for r in results]
        self.assertNotIn("dummy", contents)
        self.assertEqual(len(results), 2)
