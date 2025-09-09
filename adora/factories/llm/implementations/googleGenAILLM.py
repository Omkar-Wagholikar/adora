from langchain_google_genai import ChatGoogleGenerativeAI

from adora.factories.baseclasses.basellm import BaseLLM


class GoogleGenAILLM(BaseLLM):
    def __init__(self, config):
        self.config = config

    def create(self):
        return ChatGoogleGenerativeAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            google_api_key=self.config.api_keys.get("gemini_api_key"),
        )