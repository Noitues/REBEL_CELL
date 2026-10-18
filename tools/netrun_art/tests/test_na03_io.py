import hashlib
import os

import pytest

from netrun_art import io as nio


def test_float_format():
    assert nio.fmt_float(1.0) == "1.0"
    assert nio.fmt_float(0.5) == "0.5"
    assert nio.fmt_float(12.34567) == "12.3457"
    assert nio.fmt_float(-0.0) == "0.0"
    assert nio.fmt_float(-0.00001) == "0.0"
    assert nio.fmt_float(1e20).startswith("100000000000000000000.0")
    with pytest.raises(ValueError):
        nio.fmt_float(float("nan"))
    with pytest.raises(ValueError):
        nio.fmt_float(float("inf"))


def test_exact_bytes():
    obj = {"b": [1, 2.5, {"z": None, "a": True}], "a": "été", "e": [], "o": {}}
    want = (
        '{\n "a": "été",\n "b": [\n  1,\n  2.5,\n  {\n   "a": true,\n   "z": null\n  }\n ],\n'
        ' "e": [],\n "o": {}\n}\n'
    )
    assert nio.canonical_dumps(obj) == want


def test_key_order_independent():
    a = {"x": 1, "y": {"b": 1, "a": 2}}
    b = {"y": {"a": 2, "b": 1}, "x": 1}
    assert nio.canonical_dumps(a) == nio.canonical_dumps(b)


def test_roundtrip_idempotent_and_hash(tmp_path):
    obj = {"layout_seed": nio.u64_str(-1), "v": [0.12345, 3, "x"], "version": 1}
    p = os.path.join(str(tmp_path), "t.json")
    nio.dump(obj, p)
    raw = open(p, "rb").read()
    assert raw.endswith(b"}\n") and b"\r" not in raw and not raw.startswith(b"\xef\xbb\xbf")
    again = nio.canonical_dumps(nio.load(p))
    assert again.encode("utf-8") == raw
    assert nio.is_canonical_text(raw.decode("utf-8"))
    assert hashlib.sha256(raw).hexdigest() == hashlib.sha256(again.encode("utf-8")).hexdigest()
    assert nio.load(p)["layout_seed"] == "18446744073709551615"


def test_int_limit_and_non_canonical():
    with pytest.raises(ValueError):
        nio.canonical_dumps({"a": 2 ** 53 + 1})
    nio.canonical_dumps({"a": 2 ** 53})
    assert nio.check_canonical({"a": 2 ** 60, "b": float("nan")})
    assert not nio.is_canonical_text('{"a":1}')
    assert not nio.is_canonical_text("﻿{}\n")
    with pytest.raises(TypeError):
        nio.canonical_dumps({1: 2})


def test_validate_subset():
    schema = {"type": "object", "required": ["version"], "properties": {
        "version": {"type": "integer", "const": 1}, "ids": {"type": "array", "items": {"type": "string"}}}}
    assert nio.validate({"version": 1, "ids": ["a"]}, schema) == []
    assert nio.validate({"version": True}, schema)
    assert nio.validate({"ids": [1]}, schema)
