"""Small OpenAI-compatible Chat Completions adapter; exactly one HTTP request."""

import json
import os
from pathlib import Path
import shlex
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


class GenerationError(RuntimeError):
    """A safe, credential-free message suitable for persisted results."""


def load_env(path: Path = Path(".env")) -> None:
    """Read literal KEY=value assignments. Existing shell variables take priority."""
    if not path.exists():
        return
    allowed = {"OPENAI_API_KEY", "OPENAI_MODEL", "OPENAI_BASE_URL"}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or key not in allowed:
            raise ValueError(f"Invalid .env assignment on line {number}")
        try:
            parts = shlex.split(value, comments=True)
        except ValueError:
            raise ValueError(f"Invalid .env quoting on line {number}") from None
        if len(parts) > 1:
            raise ValueError(f"Quote values containing spaces on .env line {number}")
        os.environ.setdefault(key, parts[0] if parts else "")


def configuration() -> tuple[str, str, str]:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("OPENAI_MODEL", "").strip()
    base = os.environ.get("OPENAI_BASE_URL", "").strip() or "https://api.openai.com/v1"
    if not key or not model:
        raise GenerationError("Set OPENAI_API_KEY and OPENAI_MODEL in .env (see README.md).")
    try:
        url = urlsplit(base)
        valid = (url.scheme == "https" or
                 (url.scheme == "http" and url.hostname in {"localhost", "127.0.0.1", "::1"}))
        valid = valid and bool(url.hostname) and not (url.username or url.password or url.query or url.fragment)
    except ValueError:
        valid = False
    if not valid:
        raise GenerationError("OPENAI_BASE_URL must be an HTTPS API root (HTTP allowed only for localhost).")
    return key, model, base.rstrip("/")


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not forward a credential to a redirected host.
        return None


def complete(messages: list[dict[str, str]]) -> dict:
    key, model, base = configuration()
    payload = {"model": model, "messages": messages, "max_completion_tokens": 4096}
    request = Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with build_opener(NoRedirect()).open(request, timeout=120) as response:
            data = json.load(response)
    except HTTPError as exc:
        # Provider error bodies can echo credentials; never print or save them.
        raise GenerationError(f"LLM HTTP {exc.code}; check API key, model, endpoint, quota, and token-parameter support.") from None
    except (URLError, TimeoutError, OSError):
        raise GenerationError("LLM connection failed or timed out; check connectivity and API endpoint.") from None
    except (ValueError, UnicodeError):
        raise GenerationError("LLM returned invalid JSON.") from None
    try:
        choice = data["choices"][0]
        content = choice["message"]["content"]
        if choice.get("finish_reason") != "stop":
            raise GenerationError("LLM did not finish normally (possibly truncated or refused).")
        if not isinstance(content, str) or not content.strip():
            raise GenerationError("LLM returned empty or non-text content.")
        return {"content": content, "response_model": data.get("model", model),
                "usage": data.get("usage"), "finish_reason": choice["finish_reason"]}
    except (KeyError, IndexError, TypeError):
        raise GenerationError("LLM response is missing a valid text completion.") from None
