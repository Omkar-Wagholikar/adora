from langchain.chains import RetrievalQA
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.document_loaders import PDFPlumberLoader, TextLoader
from typing import Optional
import os

from ..config_parser.data_types import RAGConfig
from ..factories.llm.llmFactory import LLMFactory
from ..factories.embedding.embeddingFactory import EmbeddingFactory
from ..factories.vectorStore.vector_store_factory import VectorStoreFactory
from ..factories.reranking.rerankerFactory import RerankerFactory
from ..factories.chains.safe_chain import SafeRetrievalQA

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_docs(path: str, config: RAGConfig):
    if config.chunking.splitter == "code":
        # Imported lazily to avoid paying tree-sitter-language-pack's import
        # cost on every `brags` invocation regardless of subcommand -- it's a
        # base dependency now (not an optional extra), but brags/__main__.py's
        # command auto-discovery still eagerly imports every command module's
        # top-level imports, so this only actually gets pulled in when
        # chunking.splitter: code is configured and actually used.
        from .code_loader import load_code_documents
        return load_code_documents(
            path,
            languages=config.chunking.languages,
            chunk_size=config.chunking.chunk_size,
            chunk_overlap=config.chunking.chunk_overlap,
        )

    # PDFPlumberLoader only understands actual PDF bytes -- pointing it at a
    # .txt (or any other plain-text) file blows up with a pdfminer
    # PDFSyntaxError instead of ingesting it, even though "text, etc." is
    # part of the advertised --docs contract (see commands/ingest.py). Only
    # .pdf gets the PDF-specific loader; everything else is read as text.
    _, ext = os.path.splitext(path)
    loader = PDFPlumberLoader(path) if ext.lower() == ".pdf" else TextLoader(path)
    docs = loader.load()
    for d in docs:
        if "source" not in d.metadata:
            d.metadata["source"] = path
    text_splitter = SemanticChunker(HuggingFaceEmbeddings())
    documents = text_splitter.split_documents(docs)
    return documents
def build_qa_system(config: RAGConfig, documents: Optional[list]):
    embedder = EmbeddingFactory.create(config=config.embedding).create()
    
    # Create vectorstore
    vector = VectorStoreFactory.create(config=config.vector_store).create(embedder=embedder, documents=documents, save_if_not_local=config.vector_store.save_if_not_local)
    retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": config.vector_store.top_k})

    # Create LLM
    llm = LLMFactory.create(config.llm).create()

    # Prompts
    QA_CHAIN_PROMPT = PromptTemplate.from_template(
        """
        1. Use the following pieces of context to answer the question at the end.
        2. If you don't know the answer, say "I don't know".
        3. Keep the answer crisp (3-4 sentences).

        Context: {context}

        Question: {question}

        Helpful Answer:"""
    )

    llm_chain = LLMChain(llm=llm, prompt=QA_CHAIN_PROMPT, verbose=config.debug)

    document_prompt = PromptTemplate(
        input_variables=["page_content", "source"],
        template="Context:\ncontent:{page_content}\nsource:{source}",
    )

    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
        document_prompt=document_prompt,
    )

    qa = RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        retriever=retriever,
        return_source_documents=True,
        verbose=config.debug,
    )

    return SafeRetrievalQA(qa)


def retrieve_raw(config: RAGConfig, query: str, top_k: Optional[int] = None) -> list[dict]:
    """Similarity search (with optional reranking) directly against the
    persisted vector store, returning raw chunks -- no LLM involved. Used by
    the MCP search tool, which wants source chunks back, not a re-summarized
    answer.
    """
    embedder = EmbeddingFactory.create(config=config.embedding).create()
    vector = VectorStoreFactory.create(config=config.vector_store).create(embedder=embedder, documents=None)

    if config.reranking.enabled:
        final_k = top_k or config.reranking.top_k or config.vector_store.top_k
        fetch_k = final_k * (config.reranking.fetch_multiplier or 1)
    else:
        final_k = top_k or config.vector_store.top_k
        fetch_k = final_k

    results = vector.similarity_search_with_score(query, k=fetch_k)
    docs = [doc for doc, _ in results]

    if config.reranking.enabled:
        reranker = RerankerFactory.create(config.reranking)
        reranked = reranker.rerank(query, docs, top_k=final_k)
        return [
            {"content": doc.page_content, "metadata": doc.metadata, "score": score}
            for doc, score in reranked
        ]

    scores = {id(doc): float(score) for doc, score in results}
    return [
        {"content": doc.page_content, "metadata": doc.metadata, "score": scores.get(id(doc))}
        for doc in docs[:final_k]
    ]