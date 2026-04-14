import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))

import vim  # noqa: F401 - needed for provider mock
from openrouter import OpenRouterProvider


class MockUtils:
    def print_debug(self, text, *args):
        pass

    def make_known_error(self, message):
        raise Exception(message)

    def load_api_key(self, env_variable, token_file_path="", token_load_fn=""):
        return "test-api-key"

    def get_proxy_settings(self):
        return None


def test_provider_initialization():
    utils = MockUtils()
    provider = OpenRouterProvider("chat", {}, utils)
    assert provider.command_type == "chat"
    assert provider.options["model"] == "anthropic/claude-3.5-sonnet"
    assert provider.options["site_url"] == "vim-ai"
    assert provider.options["site_name"] == "vim-ai"


def test_provider_with_custom_options():
    utils = MockUtils()
    raw_options = {"model": "deepseek/deepseek-r1", "temperature": "0.5"}
    provider = OpenRouterProvider("chat", raw_options, utils)
    assert provider.options["model"] == "deepseek/deepseek-r1"
    assert provider.options["temperature"] == 0.5


def test_provider_complete_command():
    utils = MockUtils()
    provider = OpenRouterProvider("complete", {}, utils)
    assert provider.command_type == "complete"


def test_provider_edit_command():
    utils = MockUtils()
    provider = OpenRouterProvider("edit", {}, utils)
    assert provider.command_type == "edit"


def test_options_parsing_temperature():
    utils = MockUtils()
    provider = OpenRouterProvider("chat", {"temperature": "0.7"}, utils)
    assert provider.options["temperature"] == 0.7


def test_options_parsing_max_tokens():
    utils = MockUtils()
    provider = OpenRouterProvider("chat", {"max_tokens": "2048"}, utils)
    assert provider.options["max_tokens"] == 2048


def test_options_parsing_invalid_temperature():
    utils = MockUtils()
    try:
        _ = OpenRouterProvider("chat", {"temperature": "invalid"}, utils)
    except Exception as e:
        assert "Invalid value for option 'temperature'" in str(e)


def test_reasoning_option():
    utils = MockUtils()
    provider = OpenRouterProvider(
        "chat",
        {"reasoning": '{"effort": "high", "max_tokens": 5000}'},
        utils,
    )
    assert provider.options["reasoning"] == {"effort": "high", "max_tokens": 5000}


def test_provider_routing_exclude():
    utils = MockUtils()
    provider = OpenRouterProvider(
        "chat",
        {"provider": '{"exclude": ["replicate"]}'},
        utils,
    )
    assert provider.options["provider"] == {"exclude": ["replicate"]}


def test_provider_routing_include():
    utils = MockUtils()
    provider = OpenRouterProvider(
        "chat",
        {"provider": '{"include": ["anthropic", "openai"]}'},
        utils,
    )
    assert provider.options["provider"] == {"include": ["anthropic", "openai"]}


def test_transforms_option():
    utils = MockUtils()
    provider = OpenRouterProvider(
        "chat",
        {"transforms": '["deepthink"]'},
        utils,
    )
    assert provider.options["transforms"] == ["deepthink"]


def test_models_option():
    utils = MockUtils()
    provider = OpenRouterProvider(
        "chat",
        {"models": '["model1", "model2"]'},
        utils,
    )
    assert provider.options["models"] == ["model1", "model2"]


def test_location_headers():
    utils = MockUtils()
    provider = OpenRouterProvider(
        "chat",
        {"longitude": "-122.4194", "latitude": "37.7749", "altitude": "10"},
        utils,
    )
    assert provider.options["longitude"] == "-122.4194"
    assert provider.options["latitude"] == "37.7749"
    assert provider.options["altitude"] == "10"


def test_request_timeout_parsing():
    utils = MockUtils()
    provider = OpenRouterProvider("chat", {"request_timeout": "30"}, utils)
    assert provider.options["request_timeout"] == 30.0
