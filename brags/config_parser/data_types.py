from pydantic import BaseModel
from typing import Any, Optional, Dict

class LLMConfig(BaseModel):
    provider: str
    model_name: str
    temperature: float
    max_tokens: int
    api_keys: Optional[Dict[str, str]] = None
    huggingface_api_token: Optional[str] = None
    ollama_host: Optional[str] = None

class EmbeddingConfig(BaseModel):
    provider: str
    model_name: str
    dimensions: int
    normalize: bool
    ensemble_weights: Optional[Dict[str, float]] = None
    cache_dir: Optional[str] = "./embedding_cache"
    tfidf_config: Optional[Dict[str, Any]] = None
    lda_config: Optional[Dict[str, Any]] = None
    bm25_enabled: Optional[bool] = True

class VectorStoreConfig(BaseModel):
    type: str
    persist_path: str
    similarity_metric: str
    top_k: int
    allow_dangerous_deserialization: Optional[bool] = False
    save_if_not_local: Optional[bool] = False


class ChunkingConfig(BaseModel):
    chunk_size: int
    chunk_overlap: int
    # "semantic": embedding-similarity chunking over prose/PDF documents
    # (the original, still-default behavior).
    # "code": tree-sitter syntax-aware chunking that produces one chunk per
    # function/class/method instead of arbitrary token windows -- chunk_size
    # and chunk_overlap are unused in this mode, since chunk boundaries come
    # from the parse tree rather than a token count.
    splitter: str
    # Which tree-sitter-language-pack language ids to parse (e.g. "python",
    # "go"); only consulted when splitter == "code". None means auto-detect
    # each file's language from its extension.
    languages: Optional[list[str]] = None


class RerankingConfig(BaseModel):
    enabled: bool
    # Matches the provider-field convention used by LLMConfig/EmbeddingConfig/
    # VectorStoreConfig; only "cross_encoder" exists today.
    provider: Optional[str] = "cross_encoder"
    model_name: Optional[str] = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    # Final number of results returned after reranking; defaults to
    # vector_store.top_k when unset.
    top_k: Optional[int] = None
    # Candidates pulled from the vector store before reranking down to
    # top_k = vector_store.top_k * fetch_multiplier. Reranking can only
    # reorder what it's given, so this needs to be larger than top_k for
    # reranking to actually change the result set instead of just
    # re-sorting it.
    fetch_multiplier: Optional[int] = 4


class HallucinationCheckerConfig(BaseModel):
    enabled: bool
    same_as_retriever: bool
    method: str
    threshold: Optional[float] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    api_keys: Optional[Dict[str, str]] = None
    huggingface_api_token: Optional[str] = None
    ollama_host: Optional[str] = None
    prompt_template: Optional[str] = None


class LoggingConfig(BaseModel):
    level: str
    log_to_file: bool
    log_file_path: Optional[str] = None


class RAGConfig(BaseModel):
    llm: LLMConfig
    embedding: EmbeddingConfig
    vector_store: VectorStoreConfig
    chunking: ChunkingConfig
    reranking: RerankingConfig
    hallucination_checker: HallucinationCheckerConfig
    logging: LoggingConfig
    rag_mode: str
    streaming: bool
    use_cache: bool
    debug: bool
