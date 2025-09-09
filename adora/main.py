from pathlib import Path
import logging

from .config_parser.data_types import RAGConfig
from .config_parser.parser import load_config
from .factories.llm.llmFactory import LLMFactory
from .pipeline.assembler import get_docs, build_qa_system
from .utils.logging_setup import setup_logging
 
if __name__ == "__main__":
    print("Running Adora...")
    CONFIG_PATH = Path(__file__).parent / "rag_config.yaml"
    config: RAGConfig = load_config(CONFIG_PATH)
    setup_logging(config.logging)
    logger = logging.getLogger("Adora")
    
    logger.info("Getting docs")
    docs = get_docs("/home/omkar/rag_check/adora/testFiles/test1.pdf")
    
    logger.info("setting up pipeline")    
    qa = build_qa_system(config=config, documents=docs)

    logger.info("asking query")
    query = "some data"
    res = qa(query)
    val = str(res)
    logger.info(f"got result: {val}")