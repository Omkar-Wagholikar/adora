from ....config_parser.data_types import EmbeddingConfig
import numpy as np
import os
import pickle
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim import corpora
from gensim.models import LdaModel

from ....factories.baseclasses.baseembedding import BaseEmbedding


class EnsembleEmbedding(BaseEmbedding):
    """
    Ensemble embedding that combines multiple retrieval methods:
    - Dense embeddings (HuggingFace)
    - TF-IDF (sparse representations)
    - LDA topic modeling
    - BM25 (optional)
    """
    
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.cache_dir = config.cache_dir or "./embedding_cache"
        
        # Default ensemble weights
        self.weights = config.ensemble_weights or {
            'vector': 0.4,
            'tfidf': 0.3,
            'lda': 0.2,
            'bm25': 0.1
        }
        
        # Configuration for individual components
        self.tfidf_config = config.tfidf_config or {
            'max_features': 10000,
            'stop_words': 'english',
            'ngram_range': (1, 2),
            'min_df': 2,
            'max_df': 0.8
        }
        
        self.lda_config = config.lda_config or {
            'num_topics': 20,
            'passes': 10,
            'random_state': 42,
            'alpha': 'auto'
        }
        
        self.bm25_enabled = config.bm25_enabled if config.bm25_enabled is not None else True
        
        # Will be initialized when create() is called
        self._embedding_instance = None
        self._initialized = False

    def create(self):
        """Create the ensemble embedding instance"""
        if self._embedding_instance is None:
            self._embedding_instance = EnsembleEmbeddingInstance(
                config=self.config,
                weights=self.weights,
                cache_dir=self.cache_dir,
                tfidf_config=self.tfidf_config,
                lda_config=self.lda_config,
                bm25_enabled=self.bm25_enabled
            )
        return self._embedding_instance


class EnsembleEmbeddingInstance:
    """
    The actual embedding instance that handles ensemble operations
    Compatible with LangChain's embedding interface
    """
    
    def __init__(
        self, 
        config: EmbeddingConfig,
        weights: Dict[str, float],
        cache_dir: str,
        tfidf_config: Dict[str, Any],
        lda_config: Dict[str, Any],
        bm25_enabled: bool
    ):
        self.config = config
        self.weights = weights
        self.cache_dir = cache_dir
        self.tfidf_config = tfidf_config
        self.lda_config = lda_config
        self.bm25_enabled = bm25_enabled
        
        # Initialize base vector embedding
        self.vector_embedding = HuggingFaceEmbeddings(
            model_name=config.model_name,
            encode_kwargs={'normalize_embeddings': config.normalize}
        )
        
        # Components will be initialized when documents are provided
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.lda_model = None
        self.doc_topic_matrix = None
        self.dictionary = None
        self.bm25 = None
        self.documents = None
        self.document_texts = None
        
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def initialize_with_documents(self, documents: List[Document]):
        """Initialize the ensemble components with a document corpus"""
        if self.documents is not None:
            # Already initialized
            return
            
        self.documents = documents
        self.document_texts = [doc.page_content for doc in documents]
        
        print(f"Initializing ensemble embedding with {len(documents)} documents...")
        
        # Initialize all components
        self._init_tfidf()
        self._init_lda()
        if self.bm25_enabled:
            self._init_bm25()
        
        print("Ensemble embedding initialized")
    
    def _init_tfidf(self):
        """Initialize TF-IDF component"""
        cache_path = os.path.join(self.cache_dir, "ensemble_tfidf.pkl")
        
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    self.tfidf_vectorizer, self.tfidf_matrix = pickle.load(f)
                print("Loaded cached TF-IDF components")
            else:
                raise FileNotFoundError("Cache not found")
                
        except (FileNotFoundError, EOFError):
            print("Building TF-IDF components...")
            self.tfidf_vectorizer = TfidfVectorizer(**self.tfidf_config)
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.document_texts)
            
            with open(cache_path, 'wb') as f:
                pickle.dump((self.tfidf_vectorizer, self.tfidf_matrix), f)
            print("TF-IDF components cached")
    
    def _init_lda(self):
        """Initialize LDA component"""
        cache_path = os.path.join(self.cache_dir, "ensemble_lda.pkl")
        
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'rb') as f:
                    self.lda_model, self.doc_topic_matrix, self.dictionary = pickle.load(f)
                print("Loaded cached LDA components")
            else:
                raise FileNotFoundError("Cache not found")
                
        except (FileNotFoundError, EOFError):
            print("Building LDA components...")
            
            # Preprocess texts
            processed_texts = []
            for text in self.document_texts:
                words = text.lower().split()
                words = [w for w in words if len(w) > 3 and w.isalpha()]
                processed_texts.append(words)
            
            # Create dictionary and corpus
            self.dictionary = corpora.Dictionary(processed_texts)
            self.dictionary.filter_extremes(no_below=2, no_above=0.8)
            corpus = [self.dictionary.doc2bow(text) for text in processed_texts]
            
            # Dynamic topic count
            num_topics = min(self.lda_config['num_topics'], len(self.documents) // 5)
            
            # Train LDA model
            self.lda_model = LdaModel(
                corpus=corpus,
                id2word=self.dictionary,
                num_topics=num_topics,
                passes=self.lda_config['passes'],
                random_state=self.lda_config['random_state'],
                alpha=self.lda_config['alpha'],
                per_word_topics=True
            )
            
            # Get document-topic distributions
            self.doc_topic_matrix = np.zeros((len(self.documents), num_topics))
            for i, doc_bow in enumerate(corpus):
                topic_dist = self.lda_model.get_document_topics(doc_bow, minimum_probability=0)
                for topic_id, prob in topic_dist:
                    self.doc_topic_matrix[i, topic_id] = prob
            
            with open(cache_path, 'wb') as f:
                pickle.dump((self.lda_model, self.doc_topic_matrix, self.dictionary), f)
            print("LDA components cached")
    
    def _init_bm25(self):
        """Initialize BM25 component"""
        try:
            from rank_bm25 import BM25Okapi
            
            cache_path = os.path.join(self.cache_dir, "ensemble_bm25.pkl")
            
            try:
                if os.path.exists(cache_path):
                    with open(cache_path, 'rb') as f:
                        self.bm25 = pickle.load(f)
                    print(" Loaded cached BM25 index")
                else:
                    raise FileNotFoundError("Cache not found")
                    
            except (FileNotFoundError, EOFError):
                print(" Building BM25 index...")
                tokenized_docs = [doc.lower().split() for doc in self.document_texts]
                self.bm25 = BM25Okapi(tokenized_docs)
                
                with open(cache_path, 'wb') as f:
                    pickle.dump(self.bm25, f)
                print("BM25 index cached")
                
        except ImportError:
            print("BM25 not available. Install rank_bm25 to enable BM25 scoring.")
            self.bm25 = None
            self.weights['bm25'] = 0
            # Renormalize weights
            total = sum(v for k, v in self.weights.items() if k != 'bm25')
            if total > 0:
                for k in ['vector', 'tfidf', 'lda']:
                    if k in self.weights:
                        self.weights[k] /= total
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed documents using ensemble approach
        Returns combined embeddings that incorporate multiple similarity methods
        """
        # For document embedding, we primarily use the vector embedding
        # The ensemble scoring happens at retrieval time
        return self.vector_embedding.embed_documents(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed query using ensemble approach
        Returns combined embedding for query
        """
        # For query embedding, we primarily use the vector embedding
        # The ensemble scoring happens at retrieval time
        return self.vector_embedding.embed_query(text)
    
    def get_ensemble_similarities(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get document similarities using ensemble approach
        Returns list of documents with ensemble scores
        """
        if self.documents is None:
            raise ValueError("Ensemble embedding not initialized with documents. Call initialize_with_documents() first.")
        
        # Get query representations for different methods
        query_representations = self._get_query_representations(query)
        
        # Score documents using all methods
        method_scores = self._score_documents(query, query_representations)
        
        # Combine scores
        final_scores = self._ensemble_scoring(method_scores)
        
        # Get top-k results
        top_indices = np.argsort(final_scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'document_index': idx,
                'document': self.documents[idx],
                'ensemble_score': float(final_scores[idx]),
                'method_scores': {
                    'vector': float(method_scores['vector'][idx]),
                    'tfidf': float(method_scores['tfidf'][idx]),
                    'lda': float(method_scores['lda'][idx]),
                    'bm25': float(method_scores['bm25'][idx]) if self.bm25 else 0.0
                }
            })
        
        return results
    
    def _get_query_representations(self, query: str) -> Dict[str, Any]:
        """Get query representations for different methods"""
        representations = {}
        
        # Vector representation
        representations['vector'] = np.array(self.vector_embedding.embed_query(query))
        
        # TF-IDF representation
        if self.tfidf_vectorizer:
            representations['tfidf'] = self.tfidf_vectorizer.transform([query])
        
        # LDA representation
        if self.lda_model and self.dictionary:
            query_words = [w for w in query.lower().split() if len(w) > 3 and w.isalpha()]
            query_bow = self.dictionary.doc2bow(query_words)
            query_topics = self.lda_model.get_document_topics(query_bow, minimum_probability=0)
            
            query_topic_vec = np.zeros(self.lda_model.num_topics)
            for topic_id, prob in query_topics:
                query_topic_vec[topic_id] = prob
            representations['lda'] = query_topic_vec
        
        # BM25 representation
        if self.bm25:
            representations['bm25'] = query.lower().split()
        
        return representations
    
    def _score_documents(self, query: str, query_representations: Dict[str, Any]) -> Dict[str, np.ndarray]:
        """Score all documents using different methods"""
        scores = {}
        num_docs = len(self.documents)
        
        # Vector similarity scores
        if 'vector' in query_representations:
            doc_embeddings = np.array(self.embed_documents(self.document_texts))
            query_vec = query_representations['vector'].reshape(1, -1)
            from sklearn.metrics.pairwise import cosine_similarity
            vector_similarities = cosine_similarity(query_vec, doc_embeddings).flatten()
            scores['vector'] = vector_similarities
        else:
            scores['vector'] = np.zeros(num_docs)
        
        # TF-IDF similarity scores
        if 'tfidf' in query_representations and self.tfidf_matrix is not None:
            from sklearn.metrics.pairwise import cosine_similarity
            tfidf_similarities = cosine_similarity(
                query_representations['tfidf'], 
                self.tfidf_matrix
            ).flatten()
            scores['tfidf'] = tfidf_similarities
        else:
            scores['tfidf'] = np.zeros(num_docs)
        
        # LDA similarity scores
        if 'lda' in query_representations and self.doc_topic_matrix is not None:
            from sklearn.metrics.pairwise import cosine_similarity
            query_topic_vec = query_representations['lda'].reshape(1, -1)
            lda_similarities = cosine_similarity(query_topic_vec, self.doc_topic_matrix).flatten()
            scores['lda'] = lda_similarities
        else:
            scores['lda'] = np.zeros(num_docs)
        
        # BM25 scores
        if 'bm25' in query_representations and self.bm25:
            bm25_scores = np.array(self.bm25.get_scores(query_representations['bm25']))
            scores['bm25'] = bm25_scores
        else:
            scores['bm25'] = np.zeros(num_docs)
        
        return scores
    
    def _ensemble_scoring(self, scores: Dict[str, np.ndarray]) -> np.ndarray:
        """Combine scores from different methods"""
        # Normalize scores to [0, 1] range
        normalized_scores = {}
        for method, score_array in scores.items():
            if len(score_array) > 0 and score_array.max() > 0:
                normalized_scores[method] = score_array / score_array.max()
            else:
                normalized_scores[method] = score_array
        
        # Weighted combination
        ensemble_scores = np.zeros(len(self.documents))
        for method, weight in self.weights.items():
            if method in normalized_scores:
                ensemble_scores += weight * normalized_scores[method]
        
        return ensemble_scores
