import logging

from mcp.server.fastmcp import FastMCP

from ..config_parser.data_types import RAGConfig
from ..pipeline.assembler import retrieve_raw

logger = logging.getLogger("BragsMCP")


def build_server(config: RAGConfig) -> FastMCP:
    server = FastMCP(
        name="brags",
        instructions=(
            "Search a codebase/document corpus already indexed via `brags ingest`. "
            "Returns raw source chunks with metadata, not a summarized answer -- "
            "read the returned content yourself rather than expecting a direct reply."
        ),
    )

    @server.tool()
    def search(query: str, top_k: int = 5) -> list[dict]:
        """Search the indexed corpus for chunks relevant to `query`.

        Returns up to top_k results, each with:
        - content: the chunk text
        - metadata: source file path, and for code-mode indexes: language,
          symbol_name, symbol_type (function/method/class/...), class_name
          (enclosing class, if any), start_line, end_line
        - score: relevance. When reranking is enabled, higher is more
          relevant (cross-encoder score); otherwise lower is more relevant
          (vector distance).
        """
        logger.info("MCP search: query=%r top_k=%d", query, top_k)
        return retrieve_raw(config, query, top_k=top_k)

    return server


def run(config: RAGConfig):
    server = build_server(config)
    server.run(transport="stdio")
