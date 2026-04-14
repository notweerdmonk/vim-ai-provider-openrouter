import os

dirname = os.path.dirname(__file__)

_openrouter_config = {
    "model": "anthropic/claude-3.5-sonnet",
    "endpoint_url": "https://openrouter.ai/api/v1/chat/completions",
    "request_timeout": 20,
    "site_url": "vim-ai",
    "site_name": "vim-ai",
    "temperature": 1.0,
    "max_tokens": 4096,
}


def eval(cmd):
    match cmd:
        case "g:vim_ai_openrouter_config":
            return _openrouter_config
        case "exists('g:vim_ai_openrouter_config')":
            return "1"
        case _:
            return None


def command(cmd):
    pass
