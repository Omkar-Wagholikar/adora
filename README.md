
# brags 

**brags** (Build-your-own RAG System) is a Python package that makes it easy to spin up a custom Retrieval-Augmented Generation (RAG) pipeline.  
It combines Python for the RAG logic and a background **Go file watcher** that monitors your documents folder, so your vector database is always up to date.  

---

##  Features

-  **Config-driven RAG setup** (`rag_config.yaml`)
-  **Pluggable embeddings** (HuggingFace dense, or an ensemble of dense + BM25/TF-IDF/LDA)
-  **Flexible LLM providers** (Gemini, Ollama, Claude, OpenAI)
-  **Two vector stores** (FAISS, Chroma)
-  **Syntax-aware code chunking** (tree-sitter, across Python/Go/JS/TS/Java/Rust/C/C++/Ruby) alongside the original semantic prose/PDF chunking
-  **Two file watcher modes**:
  - **Persistent (event-driven)** → watches changes in real time via `fsnotify`
  - **Cron (polling-based)** → scans folder at regular intervals for PDF files
-  **Cross-encoder reranking**
-  **An MCP server** (`brags mcp`) exposing read-only retrieval to Claude Code and other MCP clients
-  **Configurable logging & monitoring**

---

##  Installation

Requires **Python 3.10+**. Building the file-watcher binary from source also requires **Go 1.22+**.

### From source (recommended)

```bash
git clone https://github.com/Omkar-Wagholikar/brags.git
cd brags
pip install -e .
```

Build the Go watcher binary (required for background file monitoring):

```bash
cd go
./build.sh
```

This generates `brags/bin/server_executable` (plus the static UI and `pythonFiles/`, copied alongside it), which `brags init` spawns in the background.

### From PyPI

```bash
pip install brags
```

PyPI publishes a separate wheel per platform (Linux/macOS/Windows, x86_64/arm64), each
bundling a Go binary compiled for that target, so `brags init`'s spawned server works
out of the box regardless of OS.

### Optional extras

`pip install brags` already includes code-aware chunking (tree-sitter) and the MCP server
(`brags mcp`) -- both are base dependencies, not opt-in extras. The only remaining optional
dependency group is `ensemble` embeddings (TF-IDF + LDA + BM25 blended with dense
embeddings), which pulls in a heavier dependency chain (`gensim`, `scikit-learn`) than the
rest of the package:

```bash
pip install "brags[ensemble]"
```

From a source checkout, the poetry equivalent is `poetry install -E ensemble` (or
`--all-extras`).

---

##  Quick Start

1. Bootstrap a config -- first run creates a default `rag_config.yaml` for you (inside
   the installed package directory) and starts the background Go watcher server:

```bash
brags init
```

2. Either ingest once, or register a directory to be watched and auto-re-indexed on every
   change:

```bash
# one-shot ingestion
brags ingest --docs /path/to/your/docs-or-repo

# OR: live-watched, auto re-indexes on file change (starts the server if needed)
brags watch /path/to/your/docs-or-repo
```

3. Query it:

```bash
brags query --query "your question here"
```

Editing `rag_config.yaml` (found via `python3 -c "import brags, os;
print(os.path.dirname(brags.__file__))"` if you're not sure where it landed) lets you set
your LLM provider/API keys, embedding model, and switch `chunking.splitter` between
`semantic` (prose/PDF, the default) and `code` (syntax-aware, for indexing a codebase --
see `rag_config.code.example.yaml` for a ready-made profile). File watching itself is
registered at runtime via `brags watch <path>`, not through the config file.

---

##  Project Structure

```
brags/                # Python package (commands, factories, pipeline, MCP server)
brags/rag_config.example.yaml       # Prose/PDF config profile, copied by `brags init`
brags/rag_config.code.example.yaml  # Code-retrieval config profile
go/                    # Go file watcher + web UI + Python bridge ("goHalf" module)
tests/                 # Python unit tests (pytest)
```

`rag_config.yaml` (your actual config) and any vector store index directory aren't part of
the repo -- they're created at runtime, by default inside the installed package directory
and wherever `vector_store.persist_path` points, respectively.

---

##  Configuration

All behavior is controlled via `rag_config.yaml`.
Sections include:

* **llm** → provider (gemini/ollama/claude/openai), model, API keys
* **embedding** → provider (huggingface/ensemble), model & dimensions
* **vector\_store** → faiss or chroma, persist path, top\_k
* **chunking** → chunk size, overlap, splitter (semantic or code)
* **reranking** → cross-encoder reranking, on by default in the code profile
* **logging** → level and log file path

(`hallucination_checker` is present in the schema but not yet wired up to anything --
setting it doesn't currently change behavior. File watching is a runtime action, not a
config section -- see `brags watch --help`.)

See [`rag_config.example.yaml`](brags/rag_config.example.yaml) for the prose/PDF
profile, or [`rag_config.code.example.yaml`](brags/rag_config.code.example.yaml)
for a profile tuned for indexing and searching a codebase instead (syntax-aware
chunking, hybrid dense+keyword embeddings, reranking on by default -- each
setting's comments explain why it differs from the prose profile).

---

## MCP server

`brags mcp` runs brags as a stdio [MCP](https://modelcontextprotocol.io) server
exposing a single read-only `search` tool -- similarity search (with reranking,
if enabled) directly against the persisted vector store, returning raw chunks
with source/line metadata rather than an LLM-summarized answer.

Register it with Claude Code:

```bash
claude mcp add brags -- brags mcp --config /path/to/rag_config.yaml
```

The index has to already exist (`brags ingest --docs /path/to/repo` first) --
`brags mcp` only searches, it never ingests.

---

## Testing

Run unit tests:

```bash
pytest tests
```

---

##  Contributing

We welcome contributions!
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines, and check [CHANGELOG.md](CHANGELOG.md) for updates.

---

##  License

This project is licensed under the [MIT License](LICENSE).

---
