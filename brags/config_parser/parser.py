import yaml

from .data_types import RAGConfig

# Load YAML config
def load_config(path: str) -> RAGConfig:
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        # `brags init` auto-creates a default config the first time it's
        # run, but `ingest`/`query`/`mcp`/`watch` don't -- if one of those
        # runs first on a fresh checkout, point at the command that does
        # instead of surfacing a bare "No such file or directory".
        raise FileNotFoundError(
            f"Config file not found: {path}\nRun `brags init` first to create a default config."
        ) from None
    return RAGConfig(**data)
