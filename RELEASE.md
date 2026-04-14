# Release Notes

## v1.0.0 (2026-04-14)

Initial release of vim-ai-provider-openrouter plugin.

### Features

- **OpenRouter API Support** - Unified access to 200+ AI models
- **Reasoning Models** - Support for reasoning_effort parameter (DeepSeek R1, OpenAI o1, etc.)
- **Provider Routing** - Control which providers to use (include/exclude/sort)
- **Transforms** - OpenRouter output transforms (deepthink, etc.)
- **Attribution Headers** - HTTP-Referer and X-OpenRouter-Title support
- **Location-based Selection** - Longitude, latitude, altitude headers for provider selection

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| model | anthropic/claude-3.5-sonnet | Model ID |
| endpoint_url | https://openrouter.ai/api/v1/chat/completions | API endpoint |
| request_timeout | 20 | Timeout in seconds |
| site_url | vim-ai | HTTP-Referer header |
| site_name | vim-ai | X-OpenRouter-Title header |
| temperature | 1.0 | Sampling temperature |
| max_tokens | 4096 | Max tokens to generate |
| reasoning | - | Reasoning config JSON |
| transforms | [] | Transform array |
| models | [] | Alternate model list |
| provider | {} | Provider routing object |

### Installation

```vim
Plug 'madox2/vim-ai'
Plug 'madox2/vim-ai-provider-openrouter'
```

### API Key

```sh
export OPENROUTER_API_KEY="your-key"
```

### Usage

```ini
[openrouter]
provider = openrouter
options.model = anthropic/claude-3.5-sonnet
```

### Testing

- 14 unit tests included
- Pre-push hook configured

### Dependencies

- vim-ai (core plugin)
- Python 3.10+

### License

MIT