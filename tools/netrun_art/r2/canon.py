"""Canonical text of the street r2 products (the parity contract between the Python port and the GDScript twin).

Compact JSON: object keys sorted by code point at every depth, ints as ints, floats rounded half up to 1e-6 and written fixed with the
zeros trimmed to one decimal (no exponent, no -0.0), strings escaped as in `netrun_art.io`. A value under the key `seed` is a u64
and is written as a decimal string (JSON numbers stop being exact at 2**53). The first `split` levels put one member per line, so a
fixture diffs by element; deeper levels are one line. One trailing LF. `digest` is the SHA-256 of that text without the split.
"""
import hashlib
import math
from typing import Any, List

M64 = (1 << 64) - 1
FLOAT_SCALE = 1e6
_ESC = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t", "\b": "\\b", "\f": "\\f"}


def fmt_float(x: float) -> str:
    """Fixed 1e-6 text of a float, zeros trimmed to one decimal, `0.0` for -0.0."""
    if not math.isfinite(x):
        raise ValueError("NaN and Inf are not allowed")
    s = f"{math.floor(x * FLOAT_SCALE + 0.5) / FLOAT_SCALE:.6f}".rstrip("0")
    if s.endswith("."):
        s += "0"
    return "0.0" if s in ("-0.0", "-0.") else s


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


def _emit(v: Any, depth: int, split: int, key: str, out: List[str]) -> None:
    if v is None:
        out.append("null")
    elif v is True:
        out.append("true")
    elif v is False:
        out.append("false")
    elif isinstance(v, int):
        out.append('"%d"' % (v & M64) if key == "seed" else str(v))
    elif isinstance(v, float):
        out.append(fmt_float(v))
    elif isinstance(v, str):
        out.append(_str(v))
    elif isinstance(v, (list, tuple)):
        if not v:
            out.append("[]")
            return
        sep = ",\n" if depth < split else ","
        out.append("[\n" if depth < split else "[")
        for i, e in enumerate(v):
            _emit(e, depth + 1, split, key, out)
            if i < len(v) - 1:
                out.append(sep)
        out.append("\n]" if depth < split else "]")
    elif isinstance(v, dict):
        if not v:
            out.append("{}")
            return
        keys = sorted(v)
        sep = ",\n" if depth < split else ","
        out.append("{\n" if depth < split else "{")
        for i, k in enumerate(keys):
            out.append(_str(k) + ":")
            _emit(v[k], depth + 1, split, k, out)
            if i < len(keys) - 1:
                out.append(sep)
        out.append("\n}" if depth < split else "}")
    else:
        raise TypeError(type(v).__name__)


def dumps(obj: Any, split: int = 2) -> str:
    """Canonical text of `obj`."""
    out: List[str] = []
    _emit(obj, 0, split, "", out)
    return "".join(out) + "\n"


def digest(obj: Any) -> str:
    """SHA-256 (hex) of the one-line canonical text of `obj`."""
    return hashlib.sha256(dumps(obj, 0).encode("utf-8")).hexdigest()


# ---- exact float transport for fixture INPUTS: a float is the string "~<float.hex()>" (zero tail trimmed), as in tests/gen_inputs.py
def hexf(x: float) -> str:
    """`"~0x1.8p+3"`: the hex form of a float with the zero tail of the mantissa trimmed."""
    h = float(x).hex()
    if "p" not in h:
        return "~" + h
    m, e = h.split("p")
    if "." in m:
        m = m.rstrip("0").rstrip(".")
    return "~" + m + "p" + e


def encode(v: Any) -> Any:
    """Floats to hex strings, recursively (tuples to lists)."""
    if isinstance(v, bool) or v is None or isinstance(v, (int, str)):
        return v
    if isinstance(v, float):
        return hexf(v)
    if isinstance(v, (list, tuple)):
        return [encode(e) for e in v]
    if isinstance(v, dict):
        return {k: encode(e) for k, e in v.items()}
    raise TypeError(type(v).__name__)


def decode(v: Any) -> Any:
    """Inverse of `encode`."""
    if isinstance(v, str) and v.startswith("~"):
        return float.fromhex(v[1:])
    if isinstance(v, list):
        return [decode(e) for e in v]
    if isinstance(v, dict):
        return {k: decode(e) for k, e in v.items()}
    return v


def dump_input(obj: Any, path: str) -> None:
    """Write a fixture input: hex floats, compact JSON, member order kept, one LF."""
    import json
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(encode(obj), f, separators=(",", ":"))
        f.write("\n")


def load_input(path: str) -> Any:
    """Read a fixture input written by `dump_input`."""
    import json
    with open(path, encoding="utf-8") as f:
        return decode(json.load(f))
