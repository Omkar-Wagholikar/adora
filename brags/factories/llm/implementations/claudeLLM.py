from langchain_anthropic import ChatAnthropic

from brags.factories.baseclasses.basellm import BaseLLM


class ClaudeLLM(BaseLLM):
    def __init__(self, config):
        self.config = config

    def create(self):
        kwargs = {
            "model": self.config.model_name,
            "temperature": self.config.temperature,
        }
        api_key = self.config.api_keys.get("anthropic_api_key") if self.config.api_keys else None
        if api_key:
            kwargs["anthropic_api_key"] = api_key
        # Deliberately omitted (not passed as None) when unset: ChatAnthropic
        # falls back to the ANTHROPIC_API_KEY environment variable on its
        # own, but only when the kwarg isn't passed at all -- passing an
        # explicit None isn't guaranteed to trigger the same fallback across
        # versions. This is what lets `provider: claude` work with zero
        # config beyond having ANTHROPIC_API_KEY already exported.
        return ChatAnthropic(**kwargs)
