"""Directory-walking loader that feeds source files into code_chunker."""

import logging
import os

from langchain.docstore.document import Document

from .code_chunker import SUPPORTED_LANGUAGES, chunk_source

logger = logging.getLogger("CodeLoader")

# Directories that are never source code, or are generated/vendored --
# walking into them wastes time and would index dependency/build code
# that isn't part of the project being indexed.
_IGNORE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    "env", "vector_db", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    "dist", "build", "target", ".idea", ".vscode", ".egg-info", "site-packages",
}

_EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".go": "go",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp",
    ".rs": "rust",
    ".rb": "ruby",
}
assert set(_EXTENSION_TO_LANGUAGE.values()) <= set(SUPPORTED_LANGUAGES)


def _detect_language(path: str) -> str | None:
    _, ext = os.path.splitext(path)
    return _EXTENSION_TO_LANGUAGE.get(ext.lower())


def _iter_source_files(root_path: str, languages: list[str] | None):
    if os.path.isfile(root_path):
        lang = _detect_language(root_path)
        if lang is not None and (languages is None or lang in languages):
            yield root_path, lang
        return

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in _IGNORE_DIRS and not d.startswith(".")]
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            lang = _detect_language(path)
            if lang is None:
                continue
            if languages is not None and lang not in languages:
                continue
            yield path, lang


def load_code_documents(
    root_path: str,
    languages: list[str] | None = None,
    chunk_size: int = 1500,
    chunk_overlap: int = 100,
) -> list[Document]:
    """Walk `root_path` (a file or directory) and chunk every recognized
    source file into per-symbol Documents via code_chunker.chunk_source.

    `languages` restricts processing to those tree-sitter-language-pack
    language ids; None means every extension in _EXTENSION_TO_LANGUAGE.
    Files that fail to parse are logged and skipped rather than aborting
    the whole ingestion run over one bad file -- but a missing
    tree-sitter-language-pack install fails loudly and immediately instead
    of silently producing zero chunks (which chunk_source's per-file
    ImportError would otherwise look like, one confusing warning per file).
    """
    try:
        import tree_sitter_language_pack  # noqa: F401
    except ImportError as e:
        # tree-sitter-language-pack is a base dependency, so this should
        # never actually fire on a normal `pip install brags` -- surfaces a
        # broken/incomplete install rather than a missing optional extra.
        raise ImportError(
            "tree-sitter-language-pack is missing despite being a base brags "
            "dependency -- this install looks incomplete or corrupted. Try "
            "reinstalling: pip install --force-reinstall brags"
        ) from e

    documents: list[Document] = []
    for path, lang in _iter_source_files(root_path, languages):
        try:
            with open(path, "rb") as f:
                source = f.read()
        except OSError as e:
            logger.warning("CodeLoader: could not read %s: %s", path, e)
            continue

        try:
            docs = chunk_source(source, lang, path, chunk_size, chunk_overlap)
        except Exception as e:
            logger.warning("CodeLoader: failed to parse %s: %s", path, e)
            continue

        documents.extend(docs)

    logger.info("CodeLoader: produced %d chunks from %s", len(documents), root_path)
    return documents
