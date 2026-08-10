
# brags 

**brags** (Build-your-own RAG System) is a Python package that makes it easy to spin up a custom Retrieval-Augmented Generation (RAG) pipeline.  
It combines Python for the RAG logic and a background **Go file watcher** that monitors your documents folder, so your vector database is always up to date.  

---

##  Features

-  **Config-driven RAG setup** (`rag_config.yaml`)
-  **Pluggable embeddings** (HuggingFace, OpenAI, etc.)
-  **Flexible LLM providers** (OpenAI, Gemini, Ollama, HuggingFace)
-  **Multiple vector stores** (FAISS, Chroma, Qdrant, Pinecone, Weaviate)
-  **Two file watcher modes**:
  - **Persistent (event-driven)** → watches changes in real time via `fsnotify`
  - **Cron (polling-based)** → scans folder at regular intervals
-  **Chunking and reranking** options
-  **Hallucination checking** with embedding similarity or LLM-based fact checking
-  **Configurable logging & monitoring**

---

##  Installation

Requires **Python 3.10+**. Building the file-watcher binary from source also requires **Go 1.22+**.

### From source (recommended)

```bash
git clone https://github.com/Omkar-Wagholikar/adora.git
cd adora
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

A few features have dependencies that aren't installed by default, to keep the base
install lighter:

```bash
# EnsembleEmbedding: TF-IDF + LDA + BM25 blended with dense embeddings
pip install "brags[ensemble]"

# chunking.splitter: code -- syntax-aware chunking via tree-sitter
pip install "brags[code]"

# `brags mcp` -- stdio MCP server exposing a read-only search tool
pip install "brags[mcp]"

# all of the above
pip install "brags[ensemble,code,mcp]"
```

From a source checkout, the poetry equivalent is `poetry install -E ensemble -E code -E mcp`
(or `--all-extras`).

---

##  Quick Start

1. Copy the example config:

```bash
cp brags/rag_config.example.yaml brags/rag_config.yaml
```

2. Edit `rag_config.yaml` with your model, embeddings, and file watcher preferences:

```yaml
file_watcher:
  type: "persistent"   # Options: persistent, cron
  watch_dir: "./watched"
  pattern: "*.txt"
  cron_schedule: "*/3 * * * * *"  # Only for cron watcher
  debounce_seconds: 1             # Only for persistent watcher
```

3. Run your RAG system:

```bash
python -m brags.main
```

The Go watcher will start in the background, monitor your documents folder, and update your vector DB whenever files change.

---

##  Project Structure

```
brags/                # Python package
go/                   # Go watchers + Python callback
tests/                # Unit tests
vector_db/            # Local FAISS indexes
rag_config.yaml       # Main configuration file
```

---

##  Configuration

All behavior is controlled via `rag_config.yaml`.
Sections include:

* **llm** → provider, model, API keys
* **embedding** → embedding model & dimensions
* **vector\_store** → FAISS, Chroma, etc.
* **chunking** → chunk size, overlap, splitter
* **reranking** → reranker model
* **hallucination\_checker** → method + provider
* **logging** → level and log file path
* **file\_watcher** → watcher type, path, debounce/cron config

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
with source/line metadata rather than an LLM-summarized answer. Needs the `mcp`
extra:

```bash
pip install "brags[mcp]"
```

Register it with Claude Code:

```bash
claude mcp add brags -- python -m brags mcp --config /path/to/rag_config.yaml
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
