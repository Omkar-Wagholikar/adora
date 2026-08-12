from langchain_openai import ChatOpenAI

from brags.factories.baseclasses.basellm import BaseLLM


class OpenAILLM(BaseLLM):
    def __init__(self, config):
        self.config = config

    def create(self):
        kwargs = {
            "model": self.config.model_name,
            "temperature": self.config.temperature,
        }
        api_key = self.config.api_keys.get("openai_api_key") if self.config.api_keys else None
        if api_key:
            kwargs["openai_api_key"] = api_key
        # Deliberately omitted (not passed as None) when unset -- see
        # claudeLLM.py's comment for why: ChatOpenAI's own OPENAI_API_KEY
        # env fallback only kicks in when the kwarg isn't passed at all.
        return ChatOpenAI(**kwargs)
