from adora.config_parser.data_types import RAGConfig


def print_rag_config(config: RAGConfig):
    print("=" * 10, "LLM", "=" * 10)
    print(f"\tprovider: {config.llm.provider}")
    print(f"\tmodel_name: {config.llm.model_name}")
    print(f"\ttemperature: {config.llm.temperature}")
    print(f"\tmax_tokens: {config.llm.max_tokens}")
    print(f"\tapi_keys: {config.llm.api_keys}")
    print(f"\thuggingface_api_token: {config.llm.huggingface_api_token}")
    print(f"\tollama_host: {config.llm.ollama_host}")

    print("\n" + "=" * 10, "EmbeddingConfig", "=" * 10)
    print(f"\tprovider: {config.embedding.provider}")
    print(f"\tmodel_name: {config.embedding.model_name}")
    print(f"\tdimensions: {config.embedding.dimensions}")
    print(f"\tnormalize: {config.embedding.normalize}")

    print("\n" + "=" * 10, "VectorStoreConfig", "=" * 10)
    print(f"\ttype: {config.vector_store.type}")
    print(f"\tpersist_path: {config.vector_store.persist_path}")
    print(f"\tsimilarity_metric: {config.vector_store.similarity_metric}")
    print(f"\ttop_k: {config.vector_store.top_k}")

    print("\n" + "=" * 10, "ChunkingConfig", "=" * 10)
    print(f"\tchunk_size: {config.chunking.chunk_size}")
    print(f"\tchunk_overlap: {config.chunking.chunk_overlap}")
    print(f"\tsplitter: {config.chunking.splitter}")

    print("\n" + "=" * 10, "RerankingConfig", "=" * 10)
    print(f"\tenabled: {config.reranking.enabled}")
    print(f"\tmodel_name: {config.reranking.model_name}")
    print(f"\ttop_k: {config.reranking.top_k}")

    print("\n" + "=" * 10, "HallucinationCheckerConfig", "=" * 10)
    print(f"\tenabled: {config.hallucination_checker.enabled}")
    print(f"\tsame_as_retriever: {config.hallucination_checker.same_as_retriever}")
    print(f"\tmethod: {config.hallucination_checker.method}")
    print(f"\tthreshold: {config.hallucination_checker.threshold}")
    print(f"\tprovider: {config.hallucination_checker.provider}")
    print(f"\tmodel_name: {config.hallucination_checker.model_name}")
    print(f"\ttemperature: {config.hallucination_checker.temperature}")
    print(f"\tmax_tokens: {config.hallucination_checker.max_tokens}")
    print(f"\tapi_keys: {config.hallucination_checker.api_keys}")
    print(f"\thuggingface_api_token: {config.hallucination_checker.huggingface_api_token}")
    print(f"\tollama_host: {config.hallucination_checker.ollama_host}")
    print(f"\tprompt_template: {config.hallucination_checker.prompt_template}")

    print("\n" + "=" * 10, "LoggingConfig", "=" * 10)
    print(f"\tlevel: {config.logging.level}")
    print(f"\tlog_to_file: {config.logging.log_to_file}")
    print(f"\tlog_file_path: {config.logging.log_file_path}")

    print("\n" + "=" * 10, "Misc", "=" * 10)
    print(f"\trag_mode: {config.rag_mode}")
    print(f"\tstreaming: {config.streaming}")
    print(f"\tuse_cache: {config.use_cache}")
    print(f"\tdebug: {config.debug}")
