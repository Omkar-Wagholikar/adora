from langchain.chains import RetrievalQA
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from typing import Optional

from ..config_parser.data_types import RAGConfig
from ..factories.llm.llmFactory import LLMFactory
from ..factories.embedding.embeddingFactory import EmbeddingFactory
from ..factories.vectorStore.vector_store_factory import VectorStoreFactory

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def get_docs(path: str):
    loader = PDFPlumberLoader(path)
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
    # vector = FAISS.from_documents(documents, embedder)
    # retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": config.vector_store.top_k})
    vector = VectorStoreFactory.create(config=config.vector_store).create(embedder=embedder, documents=documents, save_if_not_local=config.vector_store.save_if_not_local)
    retriever = vector.as_retriever()

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

    return RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        retriever=retriever,
        return_source_documents=True,
        verbose=config.debug,
    )