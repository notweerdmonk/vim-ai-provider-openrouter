let g:vim_ai_openrouter_config = {
\  "model": "minimax/minimax-m2.5:free",
\  "endpoint_url": "https://openrouter.ai/api/v1/chat/completions",
\  "request_timeout": 20,
\  "site_url": "https://github.com/notweerdmonk/vim-ai-provider-openrouter",
\  "site_name": "vim-ai-provider-openrouter",
\  "temperature": 1.0,
\  "max_tokens": 4096,
\ "reasoning": "",
\ "transforms": [],
\ "models": [],
\ "provider": {},
\ "longitude": "",
\ "latitude": "",
\ "altitude": "",
\}

let s:plugin_root = expand('<sfile>:p:h:h')

cal vim_ai_provider#Register('openrouter', {
\  'script_path': s:plugin_root . '/py/openrouter.py',
\  'class_name': 'OpenRouterProvider',
\})
