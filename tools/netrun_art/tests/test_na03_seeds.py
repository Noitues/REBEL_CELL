import json
import os

import pytest

from netrun_art import seeds

VECTORS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures", "na02_vectors.json")
with open(VECTORS, encoding="utf-8") as _f:
    CASES = json.load(_f)


def test_vector_count():
    assert len(CASES) == 14


@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c['stream']}-{c['layout_seed']}")
def test_vector_bit_for_bit(case):
    # Both the u64 decimal string and the signed int form must give the same seed.
    for ls in (case["layout_seed"], case["layout_seed_signed"]):
        s = seeds.art_seed(ls, case["stream"], *case["keys"])
        assert str(s) == case["seed"]
    g = seeds.splitmix64(int(case["seed"]))
    draws = [next(g) for _ in range(3)]
    assert [str(d) for d in draws] == case["splitmix64_first3"]
    assert round(seeds.uniform(draws[0]), 12) == case["uniform_first"]


@pytest.mark.parametrize("bad", [1.5, True, None, b"x", [1]])
def test_bad_key_types(bad):
    with pytest.raises(TypeError):
        seeds.art_seed("1", "building", bad)


def test_uniform_range():
    assert seeds.uniform(0) == 0.0
    assert seeds.uniform(seeds.M64) < 1.0
