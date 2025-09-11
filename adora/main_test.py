from adora.factories.embedding.embeddingFactory import EmbeddingFactory
from adora.factories.vectorStore.vector_store_factory import VectorStoreFactory
from .config_parser.data_types import EmbeddingConfig, VectorStoreConfig
from .test_documents import documents

ensemble_config = EmbeddingConfig(
    provider="huggingface",
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    dimensions=384,
    normalize=True,
    ensemble_weights={
        'vector': 0.4,
        'tfidf': 0.3,
        'lda': 0.2,
        'bm25': 0.1
    },
    cache_dir="./ensemble_cache",
    tfidf_config={
        'max_features': 10000,
        'stop_words': 'english',
        'ngram_range': (1, 2),
        'min_df': 2,
        'max_df': 0.8
    },
    lda_config={
        'num_topics': 15,
        'passes': 10,
        'random_state': 42,
        'alpha': 'auto'
    },
    bm25_enabled=True
)

embedding_config: EmbeddingConfig =EmbeddingConfig(
        provider="huggingface",
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        dimensions=384,
        normalize=True,
        cache_dir="./embedding_cache",
        tfidf_config={"max_features":10000,"stop_words":"english"},
        lda_config={"num_topics":20},
        bm25_enabled=True
    )

vector_store_config=VectorStoreConfig(
        type="faiss",
        persist_path="./vector_db",
        similarity_metric="cosine",
        top_k=5,
        allow_dangerous_deserialization=True,
        save_if_not_local=True
    )

embedder = EmbeddingFactory.create(config=embedding_config).create()
    
vector = VectorStoreFactory.create(config=vector_store_config).create(embedder=embedder, documents=documents, save_if_not_local=vector_store_config.save_if_not_local)
retriever = vector.as_retriever()

query = "how do you minimize asset risk"
results = retriever.get_relevant_documents(query)
print(results)

# Create ensemble embedding using factory
# embedding_factory = EmbeddingFactory()
# ensemble_embedding = embedding_factory.create(ensemble_config)
# embedding_instance = ensemble_embedding.create()

# # Initialize with documents
# embedding_instance.initialize_with_documents(documents)

# # Get ensemble similarities for a query
# results = embedding_instance.get_ensemble_similarities("how do you minimize asset risk", top_k=5)
# print(results)