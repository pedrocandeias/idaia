# Addon/core/llm_client.py
# -*- coding: utf-8 -*-
"""
Tiny client for a local Ollama persona (e.g., 'industrial-design-coder').
We call /api/chat with format=json, stream=false, and extract {"code": "..."}.

Robustez extra:
- Normaliza a base_url (remove /api e barras a mais).
- Força system prompt para devolver ONLY {"code":"..."}.
- Remove fences Markdown, BOM/backticks, linhas de import e chavetas soltas no fim.
- Faz parsing resiliente caso o modelo ignore format=json e devolva markdown.
"""

import json
import re
import urllib.request
import urllib.error
from typing import Optional

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "industrial-design-coder"


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
    Pipeline de limpeza: fences Markdown, BOM/backticks, remover imports,
    cortar chavetas soltas no fim e trim final.
    """
    t = _strip_fences(code)
    t = t.replace("\uFEFF", "").strip("` \n\r\t")
    # remove linhas de import / from-import (o executor vai bloquear de qualquer modo)
    t = "\n".join(
        line for line in t.splitlines()
        if not re.match(r"^\s*(import\b|from\b.+\bimport\b)", line)
    )
    t = _trim_trailing_unmatched_braces(t)
    return t.strip()


# ---------------- Utilidades URL ---------------- #

def _normalize_base_url(base_url: str) -> str:
    """
    Normaliza a base_url para apontar ao host/porta do Ollama:
    - remove espaços, barras finais repetidas,
    - remove sufixo '/api' se existir (cliente já acrescenta /api/...).
    """
    if not isinstance(base_url, str) or not base_url.strip():
        raise OllamaError(f"Invalid base URL '{base_url}'")
    norm = base_url.strip().rstrip('/')
    if norm.lower().endswith('/api'):
        norm = norm[:-4]
    if not (norm.startswith('http://') or norm.startswith('https://')):
        raise OllamaError(f"Invalid base URL '{base_url}'. Expecting http://host:port")
    return norm


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

    norm = _normalize_base_url(base_url)
    url = f"{norm}/api/chat"

    # System prompt curta a reforçar o formato e regras.
    system_msg = (
        'You are a FreeCAD code generator. Output ONLY JSON: {"code":"<FreeCAD Python>"} '
        'Rules: (1) NO imports and NO from-import. '
        '(2) Assume variables App (FreeCAD) and Part are available. '
        '(3) Use doc = App.ActiveDocument or App.newDocument(). '
        '(4) Create boxes via doc.addObject("Part::Box", "Cube"). '
        '(5) End with doc.recompute(). '
        '(6) No markdown, no comments, no extra fields.'
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
            if "```" in content:
                fenced = content.split("```", 2)
                if len(fenced) >= 2:
                    candidate = fenced[1]
                    # Pode vir como "python\n<code>"
                    if "\n" in candidate:
                        candidate = "\n".join(candidate.split("\n")[1:])
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
