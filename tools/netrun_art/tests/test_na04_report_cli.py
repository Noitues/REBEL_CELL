import ast
import json
import os

import na04_fixtures as F
import pytest
from netrun_art import io
from netrun_art.checks import cli
from netrun_art.checks import report as R

CHECKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "checks")


def test_record_shape_and_exit_codes():
    ok = [R.record("a", "pass", 1, 2, "x"), R.record("b", "warn"), R.record("c", "n/a")]
    assert set(ok[0]) == {"id", "status", "value", "threshold", "note"}
    assert R.exit_code(ok) == 0
    assert R.exit_code(ok + [R.record("d", "fail")]) == 1
    with pytest.raises(ValueError):
        R.record("e", "maybe")


def test_nan_and_numpy_cleaned():
    import numpy as np
    r = R.record("x", "pass", float("nan"), [np.float32(1.5), 2])
    assert r["value"] is None and r["threshold"] == [1.5, 2]
    io.canonical_dumps(R.to_json_obj([r]))  # must be canonical-writable


def test_markdown_and_files(tmp_path):
    recs = [R.record("a|b", "fail", 0.5, [0.1, 0.2], "note | with bar")]
    md = R.to_markdown(recs)
    assert "FAIL" in md and "fail 1" in md and "note / with bar" in md
    R.write_reports(recs, str(tmp_path), "t")
    assert io.load(str(tmp_path / "t.json"))["summary"]["fail"] == 1
    assert (tmp_path / "t.md").exists()


def test_cli_images_exit_codes(tmp_path, capsys):
    cap = {"look": "aaa2"}
    F.make_capture(tmp_path / "caps" / "good", capture=cap)
    assert cli.main(["--images", str(tmp_path / "caps" / "good"), "--out", str(tmp_path / "out")]) == 0
    assert (tmp_path / "out" / "checks.json").exists()
    F.make_capture(tmp_path / "caps" / "dark", rows=lambda y, h: 10, capture=cap)
    assert cli.main(["--images", str(tmp_path / "caps")]) == 1  # a folder of captures; one fails
    out = capsys.readouterr().out
    assert "dark/R-VAL-1" in out and "good/R-VAL-1" in out


def test_cli_images_with_plates(tmp_path):
    cap = {"look": "aaa2"}
    F.make_capture(tmp_path / "godot" / "s1", capture=cap)
    F.make_capture(tmp_path / "plates" / "s1", capture=cap)
    assert cli.main(["--images", str(tmp_path / "godot"), "--plates", str(tmp_path / "plates")]) == 0
    F.make_capture(tmp_path / "godot" / "s1", rows=lambda y, h: 30 if y < h // 2 else 60, capture=cap)
    assert cli.main(["--images", str(tmp_path / "godot"), "--plates", str(tmp_path / "plates")]) == 1


def test_cli_data_and_parity(tmp_path, capsys):
    spec = F.write_producer(tmp_path)
    a = str(tmp_path / "a.json")
    io.dump({"k": [1, 2]}, a)
    assert cli.main(["--data", "--producer", spec, "--seeds", "1,2,3", "--parity", a, a]) == 0
    out = capsys.readouterr().out
    assert "12.3.1:1" in out and "12.3.4a" in out and "12.3.time" in out and "12.6:a.json" in out
    b = str(tmp_path / "b.json")
    io.dump({"k": [1, 3]}, b)
    assert cli.main(["--data", "--parity", a, b]) == 1


def test_no_forbidden_imports():
    banned = {"bpy", "bmesh", "mathutils", "socket", "urllib", "requests", "http", "ftplib", "smtplib", "godot"}
    for fn in sorted(os.listdir(CHECKS_DIR)):
        if not fn.endswith(".py"):
            continue
        tree = ast.parse(open(os.path.join(CHECKS_DIR, fn), encoding="utf-8").read())
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                names = [node.module]
            for n in names:
                assert n.split(".")[0] not in banned, f"{fn} imports {n}"


def test_data_hash_path_has_no_numpy():
    tree = ast.parse(open(os.path.join(CHECKS_DIR, "data_checks.py"), encoding="utf-8").read())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    assert not mods & {"numpy", "PIL"}


def test_composition_config_is_canonical_json():
    p = os.path.join(CHECKS_DIR, "composition.json")
    assert io.is_canonical_text(open(p, encoding="utf-8", newline="").read())
    assert json.loads(open(p, encoding="utf-8").read())["checks"]["value"]["median_pass"] == [0.11, 0.17]
