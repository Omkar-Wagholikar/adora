from unittest import mock

from tests import *

from brags.config_parser.data_types import LLMConfig
from brags.factories.llm.llmFactory import LLMFactory
from brags.factories.llm.implementations.claudeLLM import ClaudeLLM
from brags.factories.llm.implementations.openaiLLM import OpenAILLM


class TestLLMFactory(unittest.TestCase):
    def test_claude_provider_returns_claude_llm(self):
        config = LLMConfig(provider="claude", model_name="claude-sonnet-5", temperature=0.7, max_tokens=1024)
        self.assertIsInstance(LLMFactory.create(config), ClaudeLLM)

    def test_openai_provider_returns_openai_llm(self):
        config = LLMConfig(provider="openai", model_name="gpt-5.6", temperature=0.7, max_tokens=1024)
        self.assertIsInstance(LLMFactory.create(config), OpenAILLM)

    def test_unsupported_provider_raises(self):
        config = LLMConfig(provider="not-a-real-provider", model_name="x", temperature=0.1, max_tokens=1)
        with self.assertRaises(ValueError):
            LLMFactory.create(config)


class TestClaudeLLM(unittest.TestCase):
    def test_falls_back_to_env_var_when_config_has_no_key(self):
        config = LLMConfig(provider="claude", model_name="claude-sonnet-5", temperature=0.7, max_tokens=1024)
        with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-from-env"}):
            llm = ClaudeLLM(config).create()
        self.assertEqual(llm.anthropic_api_key.get_secret_value(), "sk-ant-from-env")

    def test_explicit_config_key_takes_precedence_over_env(self):
        config = LLMConfig(
            provider="claude", model_name="claude-sonnet-5", temperature=0.7, max_tokens=1024,
            api_keys={"anthropic_api_key": "sk-ant-from-config"},
        )
        with mock.patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-from-env"}):
            llm = ClaudeLLM(config).create()
        self.assertEqual(llm.anthropic_api_key.get_secret_value(), "sk-ant-from-config")


class TestOpenAILLM(unittest.TestCase):
    def test_falls_back_to_env_var_when_config_has_no_key(self):
        config = LLMConfig(provider="openai", model_name="gpt-5.6", temperature=0.7, max_tokens=1024)
        with mock.patch.dict("os.environ", {"OPENAI_API_KEY": "sk-from-env"}):
            llm = OpenAILLM(config).create()
        self.assertEqual(llm.openai_api_key.get_secret_value(), "sk-from-env")

    def test_explicit_config_key_takes_precedence_over_env(self):
        config = LLMConfig(
            provider="openai", model_name="gpt-5.6", temperature=0.7, max_tokens=1024,
            api_keys={"openai_api_key": "sk-from-config"},
        )
        with mock.patch.dict("os.environ", {"OPENAI_API_KEY": "sk-from-env"}):
            llm = OpenAILLM(config).create()
        self.assertEqual(llm.openai_api_key.get_secret_value(), "sk-from-config")

    def test_missing_key_raises_immediately(self):
        config = LLMConfig(provider="openai", model_name="gpt-5.6", temperature=0.7, max_tokens=1024)
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(Exception):
                OpenAILLM(config).create()
