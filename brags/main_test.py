# from brags.factories.embedding.embeddingFactory import EmbeddingFactory
# from brags.factories.vectorStore.vector_store_factory import VectorStoreFactory
# from .config_parser.data_types import EmbeddingConfig, VectorStoreConfig
# from .test_documents import documents

# ensemble_config = EmbeddingConfig(
#     provider="huggingface",
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     dimensions=384,
#     normalize=True,
#     ensemble_weights={
#         'vector': 0.4,
#         'tfidf': 0.3,
#         'lda': 0.2,
#         'bm25': 0.1
#     },
#     cache_dir="./ensemble_cache",
#     tfidf_config={
#         'max_features': 10000,
#         'stop_words': 'english',
#         'ngram_range': (1, 2),
#         'min_df': 2,
#         'max_df': 0.8
#     },
#     lda_config={
#         'num_topics': 15,
#         'passes': 10,
#         'random_state': 42,
#         'alpha': 'auto'
#     },
#     bm25_enabled=True
# )

# embedding_config: EmbeddingConfig =EmbeddingConfig(
#         provider="huggingface",
#         model_name="sentence-transformers/all-MiniLM-L6-v2",
#         dimensions=384,
#         normalize=True,
#         cache_dir="./embedding_cache",
#         tfidf_config={"max_features":10000,"stop_words":"english"},
#         lda_config={"num_topics":20},
#         bm25_enabled=True
#     )

# vector_store_config=VectorStoreConfig(
#         type="faiss",
#         persist_path="./vector_db",
#         similarity_metric="cosine",
#         top_k=5,
#         allow_dangerous_deserialization=True,
#         save_if_not_local=True
#     )

# embedder = EmbeddingFactory.create(config=embedding_config).create()
    
# vector = VectorStoreFactory.create(config=vector_store_config).create(embedder=embedder, documents=documents, save_if_not_local=vector_store_config.save_if_not_local)
# retriever = vector.as_retriever()

# query = "how do you minimize asset risk"
# results = retriever.get_relevant_documents(query)
# print(results)

# # Create ensemble embedding using factory
# # embedding_factory = EmbeddingFactory()
# # ensemble_embedding = embedding_factory.create(ensemble_config)
# # embedding_instance = ensemble_embedding.create()

# # # Initialize with documents
# # embedding_instance.initialize_with_documents(documents)

# # # Get ensemble similarities for a query
# # results = embedding_instance.get_ensemble_similarities("how do you minimize asset risk", top_k=5)
# # print(results)

# import ctypes
# from pathlib import Path
# import sys

# def load_go_library():
#     base_dir = Path(__file__).parent / "bin"
#     lib_path = base_dir / "libbrags.so"
#     if not lib_path.exists():
#         raise FileNotFoundError(f"Go library not found: {lib_path}")
#     return ctypes.CDLL(str(lib_path))

# go_lib = load_go_library()

# # declare signatures
# go_lib.StartCronWatcher.argtypes = []
# go_lib.StartCronWatcher.restype = None

# go_lib.StartPersistentWatcher.argtypes = [ctypes.c_char_p]
# go_lib.StartPersistentWatcher.restype = None

# # call cron watcher
# go_lib.StartCronWatcher()

# # call persistent watcher
# # go_lib.StartPersistentWatcher(b"/home/omkar/rag_check/watched")


import os
from ._golib import go_lib

# Optional: protect with env var so user can control behavior
if not os.environ.get("BRAGS_SKIP_INIT"):
    try:
        go_lib.StartCronWatcher()
    except Exception as e:
        import logging
        logging.warning(f"Failed to start Go watcher: {e}")

