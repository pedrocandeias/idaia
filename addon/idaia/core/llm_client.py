# Addon/core/llm_client.py
# -*- coding: utf-8 -*-
"""
Tiny client for a local Ollama persona (e.g., 'freecad-gen').
We call /api/chat with format=json, stream=false, and extract {"code": "..."}.
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


# ---------------- Normalização defensiva do código ---------------- #

def _strip_fences(s: str) -> str:
    """Remove blocos ```...``` ou ```python ... ``` se existirem."""
    t = s.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        # remove a 1ª linha (``` ou ```python)
        lines = lines[1:]
        # corta última linha se for ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t

def _trim_trailing_unmatched_braces(t: str) -> str:
    """
    Se não houver '{' e a string terminar em '}', remove chavetas finais.
    Isto corrige casos em que o LLM injecta um '}' perdido no fim.
    """
    u = t.rstrip()
    if "{" not in u:
        while u.endswith("}"):
            u = u[:-1].rstrip()
    return u

def _normalize_code(code: str) -> str:
    """
    Pipeline de limpeza: fences Markdown, whitespace, chavetas soltas.
    Mantém o conteúdo tal como veio, mas remove ruído que parte o exec().
    """
    t = _strip_fences(code)
    # Remover possíveis backticks soltos ou BOM insidioso
    t = t.replace("\uFEFF", "").strip("` \n\r\t")
    t = _trim_trailing_unmatched_braces(t)
    return t.strip()


# ---------------- API principal ---------------- #

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
        code (str): the FreeCAD Python snippet (normalizado).

    Raises:
        OllamaError: if the API fails or the content is not in the expected shape.
    """
    if not user_text or not isinstance(user_text, str):
        raise ValueError("user_text must be a non-empty string")

    # System prompt curta a reforçar o formato.
    system_msg = (
        "You are a FreeCAD code generator. Respond ONLY with JSON of the form "
        '{"code":"<FreeCAD Python>"} with no extra fields, no commentary, no markdown.'
    )

    payload = {
        "model": model,
        "format": "json",   # força JSON parseável
        "stream": False,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_text},
        ],
        "options": {"temperature": float(temperature)},
    }
    if keep_alive:
        payload["keep_alive"] = keep_alive  # e.g., "1h"

    url = f"{base_url.rstrip('/')}/api/chat"
    outer = _post_json(url, payload, timeout=timeout)

    # Esperado: outer["message"]["content"] é um JSON stringificatedo: {"code":"..."}
    try:
        content = outer["message"]["content"]
    except (TypeError, KeyError):
        raise OllamaError(f"Unexpected Ollama payload (no message.content): {outer}")

    # 1) Tentar parsear JSON “interior” normalmente
    inner = None
    try:
        inner = json.loads(content)
    except json.JSONDecodeError:
        # 2) Se o modelo tiver cuspido markdown/ruído, tentar strip e reparse
        content_stripped = content.strip().strip("` \n\r\t")
        try:
            inner = json.loads(content_stripped)
        except Exception as e:
            # 3) Última tentativa: heurística — procurar um bloco ```...``` e extrair
            # (isto acontece raramente com alguns modelos que ignoram format=json)
            if "```" in content:
                fenced = content.split("```", 2)
                if len(fenced) >= 2:
                    candidate = fenced[1]
                    # Pode vir como "python\n<code>"
                    if "\n" in candidate:
                        candidate = "\n".join(candidate.split("\n")[1:])
                    # embrulhar nós próprios em {"code": "..."}
                    inner = {"code": candidate}
                else:
                    raise OllamaError(f"Assistant content is not valid JSON: {content[:200]}") from e
            else:
                raise OllamaError(f"Assistant content is not valid JSON: {content[:200]}") from e

    code = inner.get("code", "")
    if not code or not isinstance(code, str):
        raise OllamaError(f"No 'code' field in assistant JSON: {inner}")

    return _normalize_code(code)


def ping(
    base_url: str = DEFAULT_OLLAMA_URL,
    model: str = DEFAULT_MODEL,
    timeout: float = 5.0,
    keep_alive: Optional[str] = "1h",
) -> bool:
    """Lightweight warm-up call to keep the model loaded. Returns True on success."""
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
