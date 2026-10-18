import json
import os
import subprocess
import sys

import pytest

from netrun_art import io
from netrun_art.checks import data_checks as DC
from netrun_art.tests import gen_fixtures as GF
from netrun_art.tests import producer, synth

with open(os.path.join(GF.FIX, "hashes.json"), encoding="utf-8") as _f:
    HASHES = json.load(_f)
TOOLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_fixture_seed_count():
    assert len(GF.SEEDS) >= 10 and HASHES["seeds"] == GF.SEEDS


@pytest.mark.parametrize("seed", GF.SEEDS)
def test_twice_in_process_and_against_file(seed):
    a = producer.produce(seed)
    b = producer.produce(seed)
    assert io.canonical_dumps(a) == io.canonical_dumps(b)
    h = dict(DC.file_hashes(a), data=DC.data_hash(a))
    assert h == HASHES["hashes"][seed]


@pytest.mark.parametrize("seed", GF.SEEDS[:3])
def test_fresh_process_other_hashseed(seed):
    r = subprocess.run([sys.executable, "-m", "netrun_art.tests.producer", seed],
                       env=dict(os.environ, PYTHONHASHSEED="12345", PYTHONPATH=TOOLS), cwd=TOOLS, capture_output=True,
                       text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == HASHES["hashes"][seed]["data"]


def test_seed_sensitivity_10_of_10():
    """12.3.4: layout_seed + 1 changes the hash for every fixture."""
    changed = sum(1 for s in GF.SEEDS[:10] if DC.data_hash(producer.produce(str(int(s) + 1000))) != HASHES["hashes"][s]["data"])
    assert changed == 10
    # the dressing alone depends on the layout seed: same city, other header seed -> other dress hash
    w = synth.make_world(int(GF.SEEDS[0]))
    out = producer.produce_world(w)
    d2 = dict(out["derive_street"], layout_seed=str(int(w["seed"]) + 1))
    from netrun_art import dress
    assert io.canonical_dumps(dress.dress_street(d2, out["city"])) != io.canonical_dumps(out["dress_street"])


def test_gameplay_stream_values_change_nothing():
    """The art outputs read no gameplay value: elite flags and edge order of the run graph do not move any hash."""
    w = synth.make_world(int(GF.SEEDS[1]))
    base = DC.data_hash(producer.produce_world(w))
    w2 = synth.make_world(int(GF.SEEDS[1]))
    for n in w2["run_graph"]["nodes"]:
        n["elite"] = not n["elite"]
    w2["run_graph"]["edges"].reverse()
    assert DC.data_hash(producer.produce_world(w2)) == base


def test_per_key_independence_of_dress_beams():
    """12.3.4b: removing one building changes no other building's beam placement."""
    from netrun_art import dress
    w = synth.make_world(int(GF.SEEDS[2]))
    out = producer.produce_world(w)
    d, city = out["derive_street"], out["city"]
    before = {b["bid"]: b for b in out["dress_street"]["beams"]}
    assert before
    victim = sorted(before)[-1]
    city2 = dict(city, buildings=[b for b in city["buildings"] if b["bid"] != victim])
    after = {b["bid"]: b for b in dress.dress_street(d, city2)["beams"]}
    rec = DC.check_key_independence(before, after, {victim} | (set(after) - set(before)))
    assert rec["status"] == "pass"
