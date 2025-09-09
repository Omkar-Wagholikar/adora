from langchain_community.embeddings import HuggingFaceEmbeddings

from adora.factories.baseclasses.baseembedding import BaseEmbedding

class HuggingFaceEmbedding(BaseEmbedding):
    def __init__(self, config):
        self.config = config

    def create(self):
        return HuggingFaceEmbeddings(model_name=self.config.model_name)
