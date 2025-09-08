from pathlib import Path

from .config_parser.data_types import RAGConfig
from .config_parser.parser import load_config
from .config_parser.utils import print_config


if __name__ == "__main__":
    print("Running Adora...")
    CONFIG_PATH = Path(__file__).parent / "rag_config.yaml"
    config: RAGConfig = load_config(CONFIG_PATH)
    print_config(config=config)