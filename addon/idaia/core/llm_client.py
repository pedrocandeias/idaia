# Addon/core/llm_client.py
# -*- coding: utf-8 -*-
"""
Tiny client for a local Ollama persona (e.g., 'freecad-gen').
We call /api/chat with format=json, stream=false, and extract {"code": "..."}.

Usage:
    code = ask_llm("create a cube 10x10x10 mm")
"""

import json
import urllib.request
import urllib.error
from typing import Optional

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "freecad-gen"


class OllamaError(RuntimeError):
    """Raised when the Ollama API call fails or returns an unexpected payload."""


def _post_json(url: str, payload: dict, timeout: float = 20.0) -> dict:
    """POST JSON and return parsed JSON dict, or raise OllamaError."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.URLError as e:
        raise OllamaError(f"Ollama request failed: {e}") from e

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise OllamaError(f"Ollama returned non-JSON response: {raw[:200]}") from e


def ask_llm(
    user_text: str,
    base_url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.0,
    timeout: float = 20.0,
    keep_alive: Optional[str] = None,
) -> str:
    """
    Ask the persona to translate a NL command into FreeCAD Python.

    Returns:
        code (str): the FreeCAD Python snippet.

    Raises:
        OllamaError: if the API fails or the content is not in the expected shape.
    """
    if not user_text or not isinstance(user_text, str):
        raise ValueError("user_text must be a non-empty string")

    payload = {
        "model": model,
        "format": "json",   # Force the assistant to emit JSON
        "stream": False,    # Single response object (easier parsing)
        "messages": [
            {"role": "user", "content": user_text}
        ],
        "options": {"temperature": float(temperature)},
    }
    if keep_alive:
        payload["keep_alive"] = keep_alive  # e.g., "1h"

    url = f"{base_url.rstrip('/')}/api/chat"
    outer = _post_json(url, payload, timeout=timeout)

    # Expect: outer["message"]["content"] is a JSON string like {"code":"..."}
    try:
        content = outer["message"]["content"]
    except (TypeError, KeyError):
        raise OllamaError(f"Unexpected Ollama payload (no message.content): {outer}")

    try:
        inner = json.loads(content)
    except json.JSONDecodeError as e:
        # If the model ever returns stray whitespace, try to trim + recover.
        content_stripped = content.strip()
        try:
            inner = json.loads(content_stripped)
        except Exception:
            raise OllamaError(f"Assistant content is not valid JSON: {content[:200]}") from e

    code = inner.get("code", "")
    if not code or not isinstance(code, str):
        raise OllamaError(f"No 'code' field in assistant JSON: {inner}")

    return code.strip()


def ping(
    base_url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    timeout: float = 5.0,
    keep_alive: Optional[str] = "1h",
) -> bool:
    """
    Lightweight warm-up call to keep the model loaded.
    Returns True on success, False on failure (non-raising).
    """
    try:
        _ = ask_llm(
            user_text="ping",
            base_url=base_url,
            model=model,
            temperature=0.0,
            timeout=timeout,
            keep_alive=keep_alive,
        )
        return True
    except Exception:
        return False
