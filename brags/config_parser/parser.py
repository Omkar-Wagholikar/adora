import yaml
from pathlib import Path

from .data_types import RAGConfig

# Load YAML config
def load_config(path: str) -> RAGConfig:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return RAGConfig(**data)
