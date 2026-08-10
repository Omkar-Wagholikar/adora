
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

> **Note:** the version currently published on PyPI predates several fixes made in this
> repository (real dependency declarations, a corrected Python version floor, portable
> file paths) — a new version needs to be tagged and released before `pip install brags`
> reflects them. Until then, prefer the source install above.
>
> The published wheel also bundles a Go binary built for Linux. Installing on macOS or
> Windows gets you the Python RAG pipeline, but the bundled `brags init` binary won't run
> there — build `go/` from source on those platforms instead.

### Optional: ensemble embeddings

`EnsembleEmbedding` (TF-IDF + LDA + BM25 blended with dense embeddings) needs an extra
dependency group not installed by default:

```bash
poetry install --with ensemble
# or, with plain pip:
pip install scikit-learn gensim rank-bm25
```

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

See [`rag_config.example.yaml`](brags/rag_config.example.yaml) for details.

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
