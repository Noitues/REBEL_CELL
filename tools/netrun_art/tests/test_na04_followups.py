import os
import subprocess

from netrun_art import io
from netrun_art.checks import data_checks as D
from netrun_art.checks import reference as REF
from netrun_art.tests import gen_fixtures as GF
from netrun_art.tests import producer, synth


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def test_pin_reads_the_pinned_commit(tmp_path):
    repo = tmp_path / "art"
    (repo / "docs" / "concepts" / "city_all_corps").mkdir(parents=True)
    f = repo / "docs" / "concepts" / "city_all_corps" / "city_all_corps_night.png"
    _git(repo, "init", "-q")
    f.write_bytes(b"pinned-bytes")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "a")
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    f.write_bytes(b"regenerated-later")
    cfg = {"pairs": [{"images": {"p_city_night": {"role": "procedural", "path": "{C}/city_all_corps/city_all_corps_night.png"},
                                 "other": {"role": "custom", "path": "{C}/city_all_corps/city_all_corps_night.png"}}}]}
    concepts = str(repo / "docs" / "concepts")
    imgs, missing = REF.collect(cfg, concepts, pins={"p_city_night": sha}, repo=str(repo), cache_dir=str(tmp_path / "cache"))
    assert missing == [] and imgs["p_city_night"]["pinned"] == sha
    assert open(imgs["p_city_night"]["path"], "rb").read() == b"pinned-bytes"
    assert open(imgs["other"]["path"], "rb").read() == b"regenerated-later"          # unpinned ids read the disk
    imgs, missing = REF.collect(cfg, concepts, pins={"p_city_night": "deadbeef"}, repo=str(repo), cache_dir=str(tmp_path / "c2"))
    assert "p_city_night" not in imgs and any("pinned deadbeef" in m for m in missing)   # never silently replaced


def test_pin_default_names_the_commit():
    assert REF.PINS == {"p_city_night": "ded90765"}


def test_dress_checks_read_typed_lists():
    out = producer.produce_world(synth.make_world(int(GF.SEEDS[0])))
    d, dr = out["derive_street"], out["dress_street"]
    flat = D.dress_positions(dr)
    assert {n for n, _ in flat} == {"signs", "lamps", "washes", "glows", "beams"}      # lists with a pos only
    assert len(flat) == sum(len(dr[n]) for n in ("signs", "lamps", "washes", "glows", "beams"))
    rec = D.check_foreground(d, {"items": [{"kind": "stall", "pos": [20.0, 20.0, 1.0]}]}, 0.5)
    assert rec["status"] == "fail" and "typed dress lists" in rec["threshold"]
    assert D.check_foreground(d, {"signs": []}, 0.5)["status"] == "fail"          # a missing list is an input-shape failure


def test_beam_input_shape():
    out = producer.produce_world(synth.make_world(int(GF.SEEDS[1])))
    bi = D.beams_input(out["dress_street"], out["derive_street"], out["city"])
    assert bi["route_bids"] == out["derive_street"]["route_keys"]
    for b in bi["beams"]:
        assert set(b) >= {"bid", "pos", "lean", "sweep_deg", "phase", "pal", "top", "spot", "shaft"}
        assert len(b["pos"]) == 3 and len(b["lean"]) == 2
    # spot / shaft come from the look.preset rig, not from the dress file
    assert all("spot" not in b and "shaft" not in b for b in out["dress_street"]["beams"])
    assert not set(b["bid"] for b in bi["beams"]) & set(bi["route_bids"])


def test_suite_derives_beams_from_dress():
    out = producer.produce_world(synth.make_world(int(GF.SEEDS[2])))
    from netrun_art.checks import image_checks as IC
    recs, _ = D.run_data_suite({"derive": out["derive_street"], "city": out["city"], "dress": out["dress_street"]}, IC.load_config())
    ids = {r["id"] for r in recs}
    assert {"12.4.5c", "12.5.1", "12.5.3"} <= ids


def test_expected_parity_files_match(tmp_path):
    for s in GF.SEEDS:
        files = producer.produce(s)
        for kind in ("street", "hq"):
            want = os.path.join(GF.EXPECTED, f"{s}_{kind}_poses.json")
            with open(want, encoding="utf-8", newline="") as f:
                assert f.read() == io.canonical_dumps(files[f"poses_{kind}"])
