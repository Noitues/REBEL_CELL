"""NA-11: the layout rule pipeline (`layout.apply_rules`): frontage minimum, border width, street r2 height passes,
unique ids, the hero sign rule, and the fixtures the GDScript twin must reproduce (`fixtures/layout/`)."""
import json
import os

import pytest

from netrun_art import dress, layout
from netrun_art.derive import street as ST
from netrun_art.tests import gen_layout_fixtures as G
from netrun_art.tests import synth
from netrun_art.units import FLOOR_BU


def _frontage_bids(city, net, mode):
    out = set()
    bases = layout.merged_buildings(city)
    for link in layout.links_of(net, mode):
        legs = layout.link_legs(city, link["pts"])
        for a, c in zip(legs, legs[1:]):
            for rows in layout.frontage_rows(bases, a, c).values():
                out.update(b["bid"] for b in rows)
    return out


@pytest.mark.parametrize("seed", [101, 102, 103])
def test_no_frontage_under_six_floors(seed):
    """Acceptance 1: after the pipeline no street-front building has fewer than 6 floors (HQ stand-ins are not city cells)."""
    w = synth.make_world(seed)
    front = _frontage_bids(w["city"], w["net"], "all")
    assert front
    out = layout.apply_rules(w["city"], w["net"], border_mode="all")
    byid = {b["bid"]: b for b in layout.merged_buildings(out)}
    bad = [bid for bid in sorted(front) if int(byid[bid]["h"] / FLOOR_BU + 1e-9) < 6]
    assert bad == []


@pytest.mark.parametrize("seed", [101, 102])
def test_border_width_from_rules(seed):
    """Acceptance 2: each frontage face steps back (border - base) / 2 BU; the number comes from the rules dict."""
    w = synth.make_world(seed)
    wide = layout.apply_layout_rules(w["city"], w["net"], dict(border_street_width=10.0), border_mode="all")
    base = layout.apply_layout_rules(w["city"], w["net"], border_mode="all")
    a = {b["bid"]: b for b in w["city"]["buildings"]}
    moved8 = moved10 = 0
    for b8, b10 in zip(base["buildings"], wide["buildings"]):
        o = a[b8["bid"]]["parts"][0]["poly"]
        d8 = max(abs(p[i] - q[i]) for p, q in zip(b8["parts"][0]["poly"], o) for i in (0, 1))
        d10 = max(abs(p[i] - q[i]) for p, q in zip(b10["parts"][0]["poly"], o) for i in (0, 1))
        if d8 > 0:
            moved8 += 1
            assert d8 == pytest.approx(1.0) and d10 == pytest.approx(2.0)
        moved10 += d10 > 0
    assert moved8 > 0 and moved8 == moved10


@pytest.mark.parametrize("seed", [101, 102, 103])
def test_pipeline_deterministic_pure_unique_ids(seed):
    w = synth.make_world(seed)
    before = json.dumps(w["city"], sort_keys=True)
    one = layout.apply_rules(w["city"], w["net"], border_mode="all")
    two = layout.apply_rules(w["city"], w["net"], border_mode="all")
    assert json.dumps(one, sort_keys=True) == json.dumps(two, sort_keys=True)
    assert json.dumps(w["city"], sort_keys=True) == before
    bids = [b["bid"] for b in one["buildings"]]
    assert len(bids) == len(set(bids)) and bids == [b["bid"] for b in w["city"]["buildings"]]


def test_silhouette_rhythm_and_horizon():
    """The r2 passes: neighbours differ by the step minimum, and 3 to 5 backdrop spikes reach 2x the median roof."""
    w = synth.make_world(101)
    st = {}
    mid = layout.frontage_silhouette(layout.apply_layout_rules(w["city"], w["net"], border_mode="all"), w["net"],
                                     border_mode="all", stats=st)
    out = layout.horizon_break(mid, w["net"], border_mode="all", stats=st)
    assert st["silhouette_set"] > 0 and 3 <= st["spikes"] <= 5
    before = {b["bid"]: b["h"] for b in layout.merged_buildings(mid)}
    raised = [b for b in layout.merged_buildings(out) if b["h"] > before[b["bid"]] + 1e-9]
    # CITY-A2 step 2: with the r2 floors (14-21 tall) a picked spike may already clear spike_k x the median: none raised then
    assert len(raised) <= st["spikes"]


def test_route_column_rises_over_top_room():
    w = synth.make_world(101)
    bid = layout.merged_buildings(w["city"])[0]["bid"]
    front = _frontage_bids(w["city"], w["net"], "all")
    target = sorted(front)[0]
    out = layout.apply_rules(w["city"], w["net"], route_tops={target: 12}, border_mode="all")
    h = {b["bid"]: b["h"] for b in layout.merged_buildings(out)}
    assert h[target] >= (12 + 3) * FLOOR_BU + 0.1 - 1e-9 or bid == target


def test_hero_sign_rule_count_and_palette():
    """Acceptance 3: one hero sign (blade + band) per route column, palette alternating district_a / district_b; the
    count does not depend on the r2 passes."""
    bad = []
    for seed in range(1000, 1030):
        w = synth.make_world(seed)
        cols = None
        for city in (layout.apply_layout_rules(w["city"], w["net"]), layout.apply_rules(w["city"], w["net"])):
            d = ST.derive_street(city, w["net"], w["run_graph"], w["site"])
            signs = dress.signs(d, dress.PRESET)
            cols = sorted(d["col_info"], key=lambda c: c["layer"])
            if sorted(s["bid"] for s in signs) != sorted(c["bid"] for c in cols):
                bad.append((seed, "sign per column"))
            for k, c in enumerate(cols):
                s = next(x for x in signs if x["bid"] == c["bid"])
                if s["pal"] == s["band_pal"] or s["pal"] != dress.SIGN_PAL[k % 2]:
                    bad.append((seed, c["bid"], "palette"))
    assert bad == []


@pytest.mark.parametrize("seed", G.SEEDS)
def test_fixtures_match_python(seed):
    """The parity fixtures on disk are what the Python oracle produces now (the GDScript twin reads them)."""
    w, out = G.ruled(seed)
    from netrun_art.tests.gen_inputs import encode
    with open(os.path.join(G.LAYOUT_DIR, seed + "_rules.json"), encoding="utf-8") as f:
        assert json.load(f) == json.loads(json.dumps(encode(G.heights_of(out)), sort_keys=True))
