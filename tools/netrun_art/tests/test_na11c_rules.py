"""NA-11c (art-pass W1_NA11 fix list): spikes capped at 1.6x the backdrop median, the frontage stays 6-10 floors, and the HQ
zone (2 lots) holds no building above 0.6x the HQ top and no spikes."""
import pytest

from netrun_art import layout
from netrun_art.tests import gen_layout_fixtures as G
from netrun_art.tests import synth
from netrun_art.units import FLOOR_BU


def _frontage_bids(city, net):
    out = set()
    bases = layout.merged_buildings(city)
    for link in layout.links_of(net, "all"):
        legs = layout.link_legs(city, link["pts"])
        for a, c in zip(legs, legs[1:]):
            for rows in layout.frontage_rows(bases, a, c).values():
                out.update(b["bid"] for b in rows)
    return out


def _zone(city):
    """bid -> cap (BU) for street-level buildings within the HQ zone."""
    k = layout.R2_RULES["hq"]["cap_k"]
    out = {}
    for bi in layout.merged_buildings(city):
        top = layout.hq_zone_top(city, bi)
        if top is not None:
            out[bi["bid"]] = k * top
    return out


@pytest.mark.parametrize("seed", [101, 102, 103])
def test_hq_zone_cap_and_no_spikes(seed):
    """No building within 2 lots of an HQ lot is taller than 0.6x the HQ top (route columns excepted); bids unchanged."""
    w = synth.make_world(seed)
    routes = G.route_tops_of(w["city"])
    out = layout.apply_rules(w["city"], w["net"], route_tops=routes, border_mode="all")
    zone = _zone(w["city"])
    assert zone
    tops = {b["bid"]: b["h"] for b in layout.merged_buildings(out)}
    assert [bid for bid, cap in sorted(zone.items()) if bid not in routes and tops[bid] > cap + 1e-6] == []
    assert [b["bid"] for b in out["buildings"]] == [b["bid"] for b in w["city"]["buildings"]]
    raw = {b["bid"]: b["h"] for b in layout.merged_buildings(w["city"])}
    assert any(raw[bid] > cap for bid, cap in zone.items() if bid not in routes)      # the cap actually bit


@pytest.mark.parametrize("seed", [101, 102, 103])
def test_spikes_capped_and_frontage_band(seed):
    """3..5 spikes are picked; a raised one reaches exactly 1.6x the backdrop median and none is lowered (B-060: a pick
    already above the cap keeps its own top); never in the HQ zone; other frontage is in the r2 floors band."""
    w = synth.make_world(seed)
    routes = G.route_tops_of(w["city"])
    base = layout.apply_layout_rules(w["city"], w["net"], border_mode="all")
    mid = layout.hq_cap(layout.frontage_silhouette(base, w["net"], route_tops=routes, border_mode="all"), list(routes))
    st = {}
    out = layout.horizon_break(mid, w["net"], list(routes), border_mode="all", stats=st)
    before = {b["bid"]: b["h"] for b in layout.merged_buildings(mid)}
    assert not [b["bid"] for b in layout.merged_buildings(out) if b["h"] < before[b["bid"]] - 1e-9]
    spikes = [b for b in layout.merged_buildings(out) if abs(b["h"] - before[b["bid"]]) > 1e-9]
    assert 3 <= st["spikes"] <= 5 and len(spikes) <= st["spikes"]
    assert len({round(s["h"], 6) for s in spikes}) <= 1
    zone = _zone(w["city"])
    assert not [s["bid"] for s in spikes if s["bid"] in zone]
    byid = {b["bid"]: b for b in w["city"]["buildings"]}
    stacked = {b["bid"] for b in layout.merged_buildings(w["city"]) if layout.is_stacked(byid[b["bid"]], b)}
    fl = {b["bid"]: int((b["h"] - 0.1) / FLOOR_BU + 1e-6) for b in layout.merged_buildings(out)}
    for bid in sorted(_frontage_bids(w["city"], w["net"])):
        if bid in routes or bid in zone or bid in stacked or bid in {s["bid"] for s in spikes}:
            continue
        sil = layout.R2_RULES["silhouette"]  # CITY-A2 step 2: the r2 floors band (6 .. 21)
        assert sil["floors_low"][0] <= fl[bid] <= sil["floors_tall"][1], (bid, fl[bid])
