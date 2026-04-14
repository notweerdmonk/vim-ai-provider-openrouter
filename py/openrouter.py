import vim
import json
import urllib.error
import urllib.request
from collections.abc import Sequence, Mapping, Iterator
from typing import TypedDict, Literal, Union, List, Protocol, Any


class AITextContent(TypedDict):
    type: Literal["text"]
    text: str


class AIImageUrlContent(TypedDict):
    type: Literal["image_url"]
    image_url: dict[str, str]


AIMessageContent = Union[AITextContent, AIImageUrlContent]


class AIMessage(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: List[AIMessageContent]


class AIUtils(Protocol):
    def print_debug(self, text: str, *args: Any):
        pass

    def make_known_error(self, message: str):
        pass

    def load_api_key(
        self, env_variable: str, token_file_path: str = "", token_load_fn: str = ""
    ):
        pass

    def get_proxy_settings(self):
        pass


class AIResponseChunk(TypedDict):
    type: Literal["assistant", "thinking"]
    content: str


class AIImageResponseChunk(TypedDict):
    b64_data: str


AICommandType = Literal["chat", "edit", "complete", "image"]


class AIProvider(Protocol):
    def __init__(
        self,
        command_type: AICommandType,
        raw_options: Mapping[str, str],
        utils: AIUtils,
    ) -> None:
        pass

    def request(self, messages: Sequence[AIMessage]) -> Iterator[AIResponseChunk]:
        pass

    def request_image(self, prompt: str) -> list[AIImageResponseChunk]:
        pass


class OpenRouterProvider:
    def __init__(
        self,
        command_type: AICommandType,
        raw_options: Mapping[str, str],
        utils: AIUtils,
    ) -> None:
        self.utils = utils
        self.command_type = command_type
        config_varname = "g:vim_ai_openrouter_config"
        if vim.eval(f"exists('{config_varname}')") == "1":
            raw_default_options = vim.eval(config_varname)
        else:
            raw_default_options = {}
        self.options = self._parse_raw_options({**raw_default_options, **raw_options})

    def _protocol_type_check(self) -> None:
        # ensure type checking works for this class
        options: Mapping[str, str] = {}
        _: AIProvider = OpenRouterProvider("chat", options, options)  # noqa: F841, F821

    def request(self, messages: Sequence[AIMessage]) -> Iterator[AIResponseChunk]:
        options = self.options
        openrouter_options = self._make_openrouter_options(options)
        http_options = {
            "request_timeout": options.get("request_timeout") or 20,
            "auth_type": options.get("auth_type", "bearer"),
            "token_file_path": options.get("token_file_path", ""),
            "token_load_fn": options.get("token_load_fn", ""),
        }

        def _flatten_content(msgs):
            for msg in msgs:
                if msg["role"] in ("system", "assistant"):
                    msg["content"] = "\n".join(map(lambda c: c["text"], msg["content"]))
            return msgs

        request = {"messages": _flatten_content(list(messages)), **openrouter_options}

        self.utils.print_debug(
            "openrouter: [{}] request: {}", self.command_type, request
        )
        url = options["endpoint_url"]
        response = self._openrouter_request(url, request, http_options, options)

        _choice_key = "delta" if openrouter_options.get("stream") else "message"

        def _get_delta(resp):
            choices = resp.get("choices") or [{}]
            return choices[0].get(_choice_key, {})

        def _map_chunk(resp):
            self.utils.print_debug(
                "openrouter: [{}] response: {}", self.command_type, resp
            )
            delta = _get_delta(resp)
            if delta.get("reasoning_content"):
                return {"type": "thinking", "content": delta.get("reasoning_content")}
            if delta.get("reasoning"):
                return {"type": "thinking", "content": delta.get("reasoning")}
            if delta.get("content"):
                return {"type": "assistant", "content": delta.get("content")}
            return None

        def _filter_valid_chunks(chunk):
            return chunk is not None

        return filter(_filter_valid_chunks, map(_map_chunk, response))

    def _load_api_key(self):
        raw_api_key = self.utils.load_api_key(
            "OPENROUTER_API_KEY",
            token_file_path=self.options.get("token_file_path", ""),
            token_load_fn=self.options.get("token_load_fn", ""),
        )
        return raw_api_key.strip()

    def _parse_raw_options(self, raw_options: Mapping[str, Any]):
        options = {**raw_options}

        def _convert_option(name, converter):
            if (
                name in options
                and isinstance(options[name], str)
                and options[name] != ""
            ):
                try:
                    options[name] = converter(options[name])
                except (ValueError, TypeError, json.JSONDecodeError) as e:
                    raise self.utils.make_known_error(
                        f"Invalid value for option '{name}': {options[name]}. Error: {e}"
                    )

        _convert_option("request_timeout", float)

        if self.command_type != "image":
            _convert_option("stream", lambda x: bool(int(x)))
            _convert_option("max_tokens", int)
            _convert_option("temperature", float)
            _convert_option("top_p", float)
            _convert_option("seed", int)
            _convert_option("max_completion_tokens", int)
            _convert_option("frequency_penalty", float)
            _convert_option("presence_penalty", float)
            _convert_option("stop", json.loads)
            _convert_option("logit_bias", json.loads)
            _convert_option("transforms", json.loads)
            _convert_option("models", json.loads)
            _convert_option("provider", json.loads)
            _convert_option("reasoning", json.loads)

        return options

    def _make_openrouter_options(self, options):
        result = {
            "model": options.get("model", "anthropic/claude-3.5-sonnet"),
        }

        option_keys = [
            "stream",
            "temperature",
            "max_tokens",
            "max_completion_tokens",
            "top_p",
            "seed",
            "stop",
            "frequency_penalty",
            "presence_penalty",
            "logit_bias",
            "reasoning",
            "transforms",
            "models",
            "provider",
        ]

        for key in option_keys:
            if key not in options:
                continue
            value = options[key]
            if value == "" or value is None:
                continue
            if (
                key in ("temperature", "max_tokens", "max_completion_tokens")
                and value == -1
            ):
                continue
            if key in ("transforms", "models") and not value:
                continue
            if key == "provider" and not value:
                continue
            result[key] = value

        return result

    def request_image(self, prompt: str) -> list[AIImageResponseChunk]:
        raise self.utils.make_known_error(
            "openrouter provider: image generation not implemented"
        )

    def _openrouter_request(self, url, data, http_opts, options):
        RESP_DATA_PREFIX = "data: "
        RESP_DONE = "[DONE]"

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "VimAI",
            "HTTP-Referer": options.get("site_url", "vim-ai"),
            "X-OpenRouter-Title": options.get("site_name", "vim-ai"),
        }

        longitude = options.get("longitude", "")
        latitude = options.get("latitude", "")
        altitude = options.get("altitude", "")

        if longitude:
            headers["X-OpenRouter-Longitude"] = longitude
        if latitude:
            headers["X-OpenRouter-Latitude"] = latitude
        if altitude:
            headers["X-OpenRouter-Altitude"] = altitude

        api_key = self._load_api_key()
        headers["Authorization"] = f"Bearer {api_key}"

        request_timeout = http_opts.get("request_timeout", 20)
        req = urllib.request.Request(
            url,
            data=json.dumps({**data}).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        proxy_settings = self.utils.get_proxy_settings()
        try:
            if proxy_settings:
                proxy_handler = urllib.request.ProxyHandler(proxy_settings)
                opener = urllib.request.build_opener(proxy_handler)
                response = opener.open(req, timeout=request_timeout)
            else:
                response = urllib.request.urlopen(req, timeout=request_timeout)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="replace")
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get("error", {}).get("message", error_body)
            except json.JSONDecodeError:
                error_msg = error_body
            raise self.utils.make_known_error(f"OpenRouter HTTP {e.code}: {error_msg}")
        except urllib.error.URLError as e:
            raise self.utils.make_known_error(f"OpenRouter network error: {e.reason}")
        except TimeoutError:
            raise self.utils.make_known_error(
                f"OpenRouter request timed out after {request_timeout} seconds"
            )

        with response:
            if not data.get("stream", 0):
                yield json.loads(response.read().decode())
                return
            for line_bytes in response:
                line = line_bytes.decode("utf-8", errors="replace")
                if line.startswith(RESP_DATA_PREFIX):
                    line_data = line[len(RESP_DATA_PREFIX) : -1]
                    if line_data.strip() == RESP_DONE:
                        pass
                    else:
                        openrouter_obj = json.loads(line_data)
                        yield openrouter_obj
