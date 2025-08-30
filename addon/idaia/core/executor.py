# Addon/core/executor.py
# -*- coding: utf-8 -*-
"""
Execute model-generated FreeCAD Python with simple guardrails.

Abordagem:
- Bloquear tokens perigosos (import/from, dunders, os/sys/subprocess, eval/exec, I/O, sockets).
- Usar um globals minimalista que só expõe o necessário (App/FreeCAD e Part).
- Substituir __builtins__ por um subconjunto seguro (inclui __import__ original p/ FreeCAD).
- Limpeza defensiva do snippet (remover fences Markdown e '}' soltos).
- Verificar sintaxe com ast.parse para erros mais amigáveis.
- Limitar comprimento do snippet.

Isto NÃO é uma sandbox perfeita, mas é muito mais seguro do que um exec() cru.
"""

import re
import ast
import builtins
import FreeCAD as App
import Part

# --- Config -----------------------------------------------------------------

# Objetos visíveis dentro do código executado:
SAFE_GLOBALS = {
    "App": App,     # FreeCAD App module (document/model ops)
    "FreeCAD": App, # alias comum
    "Part": Part,   # API de geometria do Part WB
}

# Builtins mínimos (mantém o __import__ original p/ necessidades internas do FreeCAD)
SAFE_BUILTINS = {
    "True": True,
    "False": False,
    "None": None,
    # utilitários básicos
    "abs": abs,
    "min": min,
    "max": max,
    "range": range,
    "len": len,
    "int": int,
    "float": float,
    # IMPORTANTE: permitir imports internos do FreeCAD (não expõe ao utilizador por regex)
    "__import__": builtins.__import__,
}

# Regras rápidas de bloqueio antes do exec
BANNED_PATTERNS = [
    r"\bimport\b",              # "import X"
    r"\bfrom\s+\w+\s+import\b", # "from X import Y"
    r"__\w+__",                 # qualquer dunder explícito no snippet
    r"\beval\s*\(",             # eval(
    r"\bexec\s*\(",             # exec(
    r"\bopen\s*\(",             # open(
    r"\bos\.",                  # os.*
    r"\bsys\.",                 # sys.*
    r"\bsubprocess\b",          # subprocess
    r"\bsocket\b",              # socket
    r"\brequests?\b",           # request/requests
    r"\burllib\b",              # urllib.*
    r"\bhttpx\b",               # httpx
    r"\bctypes\b",              # ctypes
    r"\bpathlib\b",             # pathlib
    r"\bshutil\b",              # shutil
    r"\bthreading\b",           # threading
    r"\basyncio\b",             # asyncio
]

# Limitar o tamanho do snippet
MAX_CODE_LEN = 5000

# --- Helpers ----------------------------------------------------------------

_banned_regexes = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in BANNED_PATTERNS]

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
    Corrige casos em que o LLM injeta um '}' perdido no fim.
    """
    u = t.rstrip()
    if "{" not in u:
        while u.endswith("}"):
            u = u[:-1].rstrip()
    return u

def _normalize(code_str: str) -> str:
    """
    Limpeza defensiva: fences Markdown, BOM/backticks, chavetas soltas.
    Mantém o conteúdo essencial e evita ruído que parte o exec().
    """
    s = _strip_fences(code_str)
    s = s.replace("\uFEFF", "").strip("` \n\r\t")
    s = _trim_trailing_unmatched_braces(s)
    return s.strip()

def _assert_safe(code_str: str) -> None:
    """Levanta ValueError se o snippet violar a política simples."""
    if not isinstance(code_str, str) or not code_str.strip():
        raise ValueError("Empty or invalid code snippet.")

    if len(code_str) > MAX_CODE_LEN:
        raise ValueError(f"Code too long ({len(code_str)} chars > {MAX_CODE_LEN}).")

    for rx in _banned_regexes:
        if rx.search(code_str):
            raise ValueError(f"Blocked unsafe code by rule: /{rx.pattern}/")

# --- Public API --------------------------------------------------------------

def safe_run(code_str: str) -> None:
    """
    Validar e executar código gerado para FreeCAD.

    O código deve usar apenas as APIs expostas, por exemplo:
      doc = App.ActiveDocument or App.newDocument()
      o = doc.addObject("Part::Box", "Cube")
      o.Length = 10; o.Width = 10; o.Height = 10
      doc.recompute()
    """
    s = _normalize(code_str)
    _assert_safe(s)

    # Check sintático para feedback mais claro antes do exec real
    try:
        ast.parse(s, mode="exec")
    except SyntaxError as e:
        raise SyntaxError(f"Sintaxe inválida na posição {e.lineno}:{e.offset} — {e.msg}")

    # Globals mínimos + builtins seguros
    g = dict(SAFE_GLOBALS)
    g["__builtins__"] = SAFE_BUILTINS
    l = {}

    # Executa o snippet; erros de runtime sobem como habitual
    exec(s, g, l)
