from brags.config_parser.data_types import EmbeddingConfig
from brags.factories.baseclasses.baseembedding import BaseEmbedding
from .implementations.huggingFaceEmbedding import HuggingFaceEmbedding


class EmbeddingFactory:
    @staticmethod
    def create(config: EmbeddingConfig) -> BaseEmbedding:
        if config.provider == "huggingface":
            return HuggingFaceEmbedding(config)
        elif config.provider == "ensemble":
            # Imported lazily: gensim/scikit-learn/rank_bm25 live in pyproject.toml's
            # optional "ensemble" poetry group, not the base install. Importing
            # EnsembleEmbedding (and therefore gensim) at module load time made every
            # `brags` CLI invocation crash with ModuleNotFoundError for anyone who
            # installed the package without that extra group -- brags/__main__.py
            # eagerly imports every command module, so this module gets loaded
            # regardless of which provider a user actually configured.
            from .implementations.ensembleEmbedding import EnsembleEmbedding
            return EnsembleEmbedding(config)
        raise ValueError(f"Unsupported embedding provider: {config.provider}")
