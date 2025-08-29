# Addon/core/executor.py
# -*- coding: utf-8 -*-
import re
import FreeCAD as App
import Part

SAFE_GLOBALS = {"App": App, "FreeCAD": App, "Part": Part}
SAFE_BUILTINS = {
    "True": True, "False": False, "None": None,
    "abs": abs, "min": min, "max": max, "range": range,
    "len": len, "int": int, "float": float,
}

BANNED_PATTERNS = [
    r"\bimport\b", r"\bfrom\s+\w+\s+import\b", r"__\w+__",
    r"\beval\s*\(", r"\bexec\s*\(", r"\bopen\s*\(",
    r"\bos\.", r"\bsys\.", r"\bsubprocess\b", r"\bsocket\b",
    r"\brequests?\b", r"\burllib\b", r"\bhttpx\b", r"\bctypes\b",
    r"\bpathlib\b", r"\bshutil\b", r"\bthreading\b", r"\basyncio\b",
]
MAX_CODE_LEN = 5000
_banned_regexes = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in BANNED_PATTERNS]

def _normalize(code_str: str) -> str:
    """Remove fences Markdown e chavetas soltas no fim."""
    s = code_str.strip()

    # Tirar ```python / ``` fences
    if s.startswith("```"):
        lines = s.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        s = "\n".join(lines).strip()

    # Se não houver '{' e o texto acabar com '}', corta-as
    if "{" not in s:
        while s.endswith("}"):
            s = s[:-1].rstrip()

    return s

def _assert_safe(code_str: str) -> None:
    if not isinstance(code_str, str) or not code_str.strip():
        raise ValueError("Empty or invalid code snippet.")
    if len(code_str) > MAX_CODE_LEN:
        raise ValueError(f"Code too long ({len(code_str)} chars > {MAX_CODE_LEN}).")
    for rx in _banned_regexes:
        if rx.search(code_str):
            raise ValueError(f"Blocked unsafe code by rule: /{rx.pattern}/")

def safe_run(code_str: str) -> None:
    """
    Validate then execute model-generated code.
      Exemplo:
        doc = App.ActiveDocument or App.newDocument()
        o = doc.addObject("Part::Box","Box")
        o.Length=10; o.Width=10; o.Height=10
        doc.recompute()
    """
    s = _normalize(code_str)
    _assert_safe(s)

    g = dict(SAFE_GLOBALS)
    g["__builtins__"] = SAFE_BUILTINS
    l = {}
    exec(s, g, l)
