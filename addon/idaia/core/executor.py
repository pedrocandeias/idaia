# Addon/core/executor.py
# -*- coding: utf-8 -*-
"""
Execute model-generated FreeCAD Python with simple guardrails.

Approach
- Block obviously dangerous tokens (import/from, dunders, os/sys/subprocess, eval/exec, I/O, sockets).
- Use a *restricted* globals dict that only exposes FreeCAD modules we expect.
- Replace __builtins__ with a tiny safe subset (True/False/None + a few harmless builtins).
- Keep snippets short (size cap) to avoid accidental dumps.

This is not a perfect sandbox, but it's a big step up from raw exec().
"""

import re
import FreeCAD as App
import Part

# --- Config -----------------------------------------------------------------

# What we allow to be visible inside the executed code:
SAFE_GLOBALS = {
    "App": App,          # FreeCAD App module (document/model ops)
    "FreeCAD": App,      # alias commonly used in scripts
    "Part": Part,        # Part workbench geometry API
}

# Extremely minimal builtins — many scripts don't need any, but these are handy.
SAFE_BUILTINS = {
    "True": True,
    "False": False,
    "None": None,
    # Keep it tiny; add cautiously if you really need more:
    "abs": abs,
    "min": min,
    "max": max,
    "range": range,
}

# Quick-and-blunt red flags to refuse before exec
BANNED_PATTERNS = [
    r"\bimport\b",              # "import X"
    r"\bfrom\s+\w+\s+import\b", # "from X import Y"
    r"__\w+__",                 # any dunder usage
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

# Cap snippet length so we don't exec megabytes by mistake
MAX_CODE_LEN = 5000


# --- Helpers ----------------------------------------------------------------

_banned_regexes = [re.compile(p, re.IGNORECASE | re.MULTILINE) for p in BANNED_PATTERNS]

def _assert_safe(code_str: str) -> None:
    """Raise ValueError if the snippet violates our simple policy."""
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
    Validate then execute model-generated code.

    The code is expected to use FreeCAD APIs only, e.g.:
      doc = App.ActiveDocument or App.newDocument()
      o = doc.addObject("Part::Box","Box")
      o.Length=10; o.Width=10; o.Height=10
      doc.recompute()
    """
    _assert_safe(code_str)

    # Build a minimal global namespace; no local symbols needed.
    g = dict(SAFE_GLOBALS)
    g["__builtins__"] = SAFE_BUILTINS
    l = {}

    # Execute the snippet. Any runtime error will bubble up as usual.
    exec(code_str, g, l)
