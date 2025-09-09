from pathlib import Path

from .config_parser.data_types import RAGConfig
from .config_parser.parser import load_config
from .pipeline.assembler import get_docs, build_qa_system

from .factories.llm.llmFactory import LLMFactory
 
if __name__ == "__main__":
    print("Running Adora...")
    CONFIG_PATH = Path(__file__).parent / "rag_config.yaml"
    config: RAGConfig = load_config(CONFIG_PATH)
    # print_config(config=config)
    # /home/omkar/rag_check/adora/testFiles/test1.pdf
    # /home/omkar/rag_check/adora/adora/main.py
    

    docs = get_docs("/home/omkar/rag_check/adora/testFiles/test1.pdf")
    
    qa = build_qa_system(config=config, documents=docs)
