"""Canonical JSON for the NA-02 contract files (NA02_FIELDS.md section 1, Ruling O12).

Rules: UTF-8, LF, one trailing LF, no BOM; object keys sorted by code point at every depth; indent 1 space;
floats rounded to 1e-4 and written fixed with trailing zeros trimmed to at least one decimal (no exponent,
no -0.0, no NaN or Inf); ints within +-2**53; u64 values are decimal strings (see `u64_str`).
Standard library only; no numpy so the data-hash path stays free of it.
"""
import json
import math
import os
from typing import Any, List

INT_LIMIT = 1 << 53
FLOAT_DECIMALS = 4
_ESC = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t", "\b": "\\b", "\f": "\\f"}


def u64_str(value: int) -> str:
    """Decimal string for a u64 (signed values are taken as two's complement)."""
    return str(int(value) & ((1 << 64) - 1))


def round_half_up(x: float) -> float:
    """Round to 1e-4 half up, `floor(x * 1e4 + 0.5) / 1e4` (spec 12.8 rule 1; neither Python nor GDScript `round`)."""
    return math.floor(x * 1e4 + 0.5) / 1e4


def fmt_float(x: float) -> str:
    """Fixed 1e-4 text for a float: trailing zeros trimmed, at least one decimal, `0.0` for -0.0."""
    if not math.isfinite(x):
        raise ValueError("NaN and Inf are not allowed")
    s = f"{round_half_up(x):.{FLOAT_DECIMALS}f}".rstrip("0")
    if s.endswith("."):
        s += "0"
    if s in ("-0.0", "-0."):
        s = "0.0"
    return s


def _str(s: str) -> str:
    out = []
    for ch in s:
        if ch in _ESC:
            out.append(_ESC[ch])
        elif ord(ch) < 0x20:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def _emit(v: Any, depth: int, out: List[str]) -> None:
    pad = " " * (depth + 1)
    if v is None:
        out.append("null")
    elif v is True:
        out.append("true")
    elif v is False:
        out.append("false")
    elif isinstance(v, int):
        if abs(v) > INT_LIMIT:
            raise ValueError(f"int {v} outside +-2**53; write u64 as a decimal string")
        out.append(str(v))
    elif isinstance(v, float):
        out.append(fmt_float(v))
    elif isinstance(v, str):
        out.append(_str(v))
    elif isinstance(v, (list, tuple)):
        if not v:
            out.append("[]")
            return
        out.append("[\n")
        for i, e in enumerate(v):
            out.append(pad)
            _emit(e, depth + 1, out)
            out.append(",\n" if i < len(v) - 1 else "\n")
        out.append(" " * depth + "]")
    elif isinstance(v, dict):
        if not v:
            out.append("{}")
            return
        for k in v:
            if not isinstance(k, str):
                raise TypeError("object keys must be strings")
        keys = sorted(v)
        out.append("{\n")
        for i, k in enumerate(keys):
            out.append(pad + _str(k) + ": ")
            _emit(v[k], depth + 1, out)
            out.append(",\n" if i < len(keys) - 1 else "\n")
        out.append(" " * depth + "}")
    else:
        raise TypeError(f"unsupported type {type(v).__name__}")


def canonical_dumps(obj: Any) -> str:
    """Canonical JSON text of `obj` (ends with one LF)."""
    out: List[str] = []
    _emit(obj, 0, out)
    return "".join(out) + "\n"


def dump(obj: Any, path: str) -> None:
    """Write `obj` to `path` as canonical JSON (UTF-8, LF, no BOM)."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(canonical_dumps(obj))


def loads(text: str) -> Any:
    """Parse JSON text. Floats stay Python floats; `check_canonical` flags big ints."""
    return json.loads(text)


def load(path: str) -> Any:
    """Read a JSON file as UTF-8 (a BOM raises, since it breaks the canonical rules)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        return loads(f.read())


def check_canonical(obj: Any, path: str = "$") -> List[str]:
    """Problems that stop `obj` being written canonically (empty list = fine)."""
    errs: List[str] = []
    if isinstance(obj, bool) or obj is None or isinstance(obj, str):
        pass
    elif isinstance(obj, int):
        if abs(obj) > INT_LIMIT:
            errs.append(f"{path}: int outside +-2**53 (use a decimal string)")
    elif isinstance(obj, float):
        if not math.isfinite(obj):
            errs.append(f"{path}: NaN or Inf")
    elif isinstance(obj, (list, tuple)):
        for i, e in enumerate(obj):
            errs += check_canonical(e, f"{path}[{i}]")
    elif isinstance(obj, dict):
        for k in sorted(obj, key=str):
            if not isinstance(k, str):
                errs.append(f"{path}: non-string key {k!r}")
            else:
                errs += check_canonical(obj[k], f"{path}.{k}")
    else:
        errs.append(f"{path}: unsupported type {type(obj).__name__}")
    return errs


def is_canonical_text(text: str) -> bool:
    """True when `text` is byte-for-byte what `canonical_dumps` writes for its own parse."""
    if text.startswith("﻿") or "\r" in text:
        return False
    try:
        return canonical_dumps(loads(text)) == text
    except (ValueError, TypeError):
        return False


_TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def _type_ok(obj: Any, name: str) -> bool:
    if name == "integer":
        return isinstance(obj, int) and not isinstance(obj, bool)
    if name == "number":
        return isinstance(obj, (int, float)) and not isinstance(obj, bool)
    if name == "boolean":
        return isinstance(obj, bool)
    return isinstance(obj, _TYPES[name]) and not isinstance(obj, bool)


def validate(obj: Any, schema: dict, path: str = "$") -> List[str]:
    """Check `obj` against a small JSON-schema subset (type, required, properties, items, enum, const).

    Returns a list of problems (empty = valid).
    """
    errs: List[str] = []
    t = schema.get("type")
    if t is not None:
        names = t if isinstance(t, list) else [t]
        if not any(_type_ok(obj, n) for n in names):
            return [f"{path}: expected {t}, got {type(obj).__name__}"]
    if "const" in schema and obj != schema["const"]:
        errs.append(f"{path}: expected {schema['const']!r}")
    if "enum" in schema and obj not in schema["enum"]:
        errs.append(f"{path}: {obj!r} not in enum")
    if isinstance(obj, dict):
        for r in schema.get("required", []):
            if r not in obj:
                errs.append(f"{path}: missing {r}")
        for k, sub in schema.get("properties", {}).items():
            if k in obj:
                errs += validate(obj[k], sub, f"{path}.{k}")
    if isinstance(obj, list) and "items" in schema:
        for i, e in enumerate(obj):
            errs += validate(e, schema["items"], f"{path}[{i}]")
    return errs


def load_validated(path: str, schema: dict) -> Any:
    """`load`, then `check_canonical` and `validate`; raises ValueError listing the problems."""
    obj = load(path)
    errs = check_canonical(obj) + validate(obj, schema)
    if errs:
        raise ValueError(os.path.basename(path) + ": " + "; ".join(errs))
    return obj
