"""Concept F, round 3: the PLAN LEDGER of round 2, re-run under the RULES_PROPOSAL package (fixed routes, home not a
corridor, weaker-node tie-break, ICE blocks the strike, 3-of-5 draft). Same presentation; the data and captions come
from the package runs used by concept G, so F and G differ only in presentation."""

from __future__ import annotations

import concept_f2_ledger as F
import concept_g3_merged as G

NAME = "F PLAN LEDGER r3"
_CAP = {}


def _header(d, concept, n, moment):
    from rc_draw import header as h
    h(d, NAME, n, _CAP.get(n, moment))


F.header = _header
F.NAME = NAME
F.RR = {"BARE": G.G["BARE"], "DECOY_ONLY": G.G["RAIL"], "SHIELD": G.G["CLEAN"], "LURE": G.G["DECOY_DRAFT"]}
F.PLANS = dict(F.PLANS)
F.PLANS["SHIELD"] = G.P["CLEAN"]
F.CARDS = ("TURRET", "ICE", "RAILGUN", "CREW")
F.WHATIF = ("RAILGUN", "RELAY")
F.RES_STEP = 2


def _cap():
    b, w, c, alt = F.RR["BARE"], F.RR["DECOY_ONLY"], F.RR["SHIELD"], F.RR["LURE"]
    lb, lw = F.losses(b), F.losses(w)
    _CAP[1] = "Warning: the intercepted strike order as icon rows; fixed routes (they will not change); countdown and Heat cause"
    _CAP[2] = (f"Planning: the ledger = the raid as it stands (home -{b.home_before - b.home_after}, {len(lb['taken'])} TAKEN); dragging a "
               f"railgun onto RELAY on the map previews lost {len(lb['down']) + len(lb['taken'])} > {len(lw['down']) + len(lw['taken'])}")
    _CAP[3] = (f"Forecast: plan 1 (turret + railgun on RELAY, ICE on PROXY) rewrites the ledger: held cells hatched, skulls where threats die; "
               f"totals all hold: CLEAN, patch {G.price(c)}; plan 2 below")
    _CAP[4] = f"Resolution: the big map replays the signed ledger (cursor at step 2 of {len(c.steps)}); no input"
    _CAP[5] = "Aftermath: the receipt on the map; CLEAN stamp with its payout; scuffed nodes listed with their patch price"


_cap()


FRAMES = [F.f1, F.f2, F.f3, F.f4, F.f5]
