# vim-ai provider openrouter

[vim-ai](https://github.com/madox2/vim-ai) provider plugin for OpenRouter.

## Installation

`vim-ai-provider-openrouter` extension have to be installed after `vim-ai`

```vim
Plug 'madox2/vim-ai'
Plug 'madox2/vim-ai-provider-openrouter'
```

### API key

Get your API key from https://openrouter.ai/keys

Export API key as an environment variable:

```sh
export OPENROUTER_API_KEY="YOUR_OPENROUTER_API_KEY"
```

or using `token_file_path` configuration:

```ini
options.token_file_path = ~/.config/openrouter.token
```

## Usage

Create an openrouter role:

```ini
[openrouter]
provider = openrouter
options.token_file_path = ~/.config/openrouter.token
```

Or use it as a default:

```ini
[default]
provider = openrouter
options.token_file_path = ~/.config/openrouter.token
```

## Configuration

### Basic Options

```ini
[openrouter]
provider = openrouter
options.model = anthropic/claude-3.5-sonnet
options.endpoint_url = https://openrouter.ai/api/v1/chat/completions
options.request_timeout = 20
options.token_file_path = ~/.config/openrouter.token
options.temperature = 1.0
options.max_tokens = 4096
```

### Attribution Headers

OpenRouter requests attribution headers to identify your app:

```ini
[myapp]
provider = openrouter
options.site_url = https://myapp.com
options.site_name = MyApp
```

### Reasoning Models

Use reasoning models via the `reasoning` option:

```ini
[deepseek-r1]
provider = openrouter
options.model = deepseek/deepseek-r1
options.reasoning = {"effort": "high"}

[o1-reasoning]
provider = openrouter
options.model = openai/o1
options.reasoning = {"effort": "high", "max_tokens": 25000}
```

### Provider Routing

Control which providers are used:

```ini
[no-replicate]
provider = openrouter
options.provider = {"exclude": ["replicate"]}

[prefer-anthropic]
provider = openrouter
options.provider = {"include": ["anthropic", "openai"]}
```

### Transforms

Apply OpenRouter transforms to modify outputs:

```ini
[deepthink]
provider = openrouter
options.transforms = ["deepthink"]
```

## License

[MIT License](https://github.com/madox2/vim-ai-provider-openrouter/blob/main/LICENSE)
