from pydantic import BaseModel, Field
from typing import Optional, Dict


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
    splitter: str


class RerankingConfig(BaseModel):
    enabled: bool
    model_name: Optional[str] = None
    top_k: Optional[int] = None


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
