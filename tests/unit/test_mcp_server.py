import asyncio

from tests import *

pytest.importorskip("mcp")

from brags.config_parser.data_types import (  # noqa: E402
    RAGConfig,
    LLMConfig,
    EmbeddingConfig,
    VectorStoreConfig,
    ChunkingConfig,
    RerankingConfig,
    HallucinationCheckerConfig,
    LoggingConfig,
)
from brags.mcp.server import build_server  # noqa: E402


def _minimal_config() -> RAGConfig:
    return RAGConfig(
        llm=LLMConfig(provider="gemini", model_name="x", temperature=0.1, max_tokens=100),
        embedding=EmbeddingConfig(
            provider="huggingface",
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            dimensions=384,
            normalize=True,
        ),
        # Building the server doesn't touch the vector store -- it's only
        # loaded lazily inside the `search` tool -- so this path never needs
        # to exist for these tests.
        vector_store=VectorStoreConfig(
            type="faiss", persist_path="/nonexistent", similarity_metric="cosine", top_k=3
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


class TestMCPServer(unittest.TestCase):
    def test_search_tool_is_registered(self):
        server = build_server(_minimal_config())
        tools = asyncio.run(server.list_tools())
        self.assertIn("search", [t.name for t in tools])

    def test_search_tool_schema_has_query_and_top_k(self):
        server = build_server(_minimal_config())
        tools = asyncio.run(server.list_tools())
        search_tool = next(t for t in tools if t.name == "search")

        props = search_tool.inputSchema["properties"]
        self.assertIn("query", props)
        self.assertEqual(props["query"]["type"], "string")
        self.assertIn("top_k", props)
        self.assertEqual(search_tool.inputSchema["required"], ["query"])

    def test_only_search_is_exposed(self):
        # Deliberately no ingest/write tool -- an MCP client can invoke tools
        # without a human approving each call, so this stays read-only.
        server = build_server(_minimal_config())
        tools = asyncio.run(server.list_tools())
        self.assertEqual([t.name for t in tools], ["search"])
