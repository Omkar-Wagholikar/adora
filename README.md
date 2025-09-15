
# brags 

**brags** (Build-your-own RAG System) is a Python package that makes it easy to spin up a custom Retrieval-Augmented Generation (RAG) pipeline.  
It combines Python for the RAG logic and a background **Go file watcher** that monitors your documents folder, so your vector database is always up to date.  

---

##  Features

-  **Config-driven RAG setup** (`rag_config.yaml`)
-  **Pluggable embeddings** (HuggingFace, OpenAI, etc.)
-  **Flexible LLM providers** (OpenAI, Gemini, Ollama, HuggingFace)
-  **Multiple vector stores** (FAISS, Chroma, Qdrant, Pinecone, Weaviate)
- ⚙️ **Two file watcher modes**:
  - **Persistent (event-driven)** → watches changes in real time via `fsnotify`
  - **Cron (polling-based)** → scans folder at regular intervals
-  **Chunking and reranking** options
-  **Hallucination checking** with embedding similarity or LLM-based fact checking
-  **Configurable logging & monitoring**

---

##  Installation

Clone the repo and install using Poetry or pip:

```bash
git clone https://github.com/yourusername/brags.git
cd brags
pip install -e .
````

Build the Go watcher binary (required for background file monitoring):

```bash
cd go
./build.sh
```

This will generate the watcher binary that `brags` runs in the background.

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
