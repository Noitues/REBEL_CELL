"""G1 graph oracle (docs/handoff/raid_integration/G1_SIM.md, designer 2026-10-25): the four Solace merge concepts
(docs/design/raid_concepts/SOLACE_MERGE_IDEAS.md) and the corp path rules, played as whole campaigns.

Python 3 stdlib only, deterministic and seeded. The raid is the L14 lab raid (sweep_l8.py): the deck and hand, wounds,
the typed BLOCK / HIT scan, HOME hit at most once per raid, sealed A and B, the hunter, the responses, the five tiers and
the greedy-over-outcomes planner. The board is a geometry from g1_geo.py instead of the 4 x 3 lattice.

Campaign (shared by every concept)
- 12 netruns, or until a loss. A netrun claims one Site next to the territory (claim policies greedy / keys / random).
- A raid follows the netrun that queued it. Base trigger: 2 netruns since the last raid. Concept triggers (B: a ward
  first at 50 %; C: the tide's first crossing of each column) queue one at once; a netrun queues at most one raid.
- Raid: DECAY (raids after the first) -> DRAW -> PLAN -> beam 1, extras -> REVEAL A -> RESPONSE -> sealed A -> REVEAL B
  -> sealed B -> [late slot: C field dose, D cure] -> hunter reveal -> hunter -> close -> BETWEEN (repair, build/clean,
  concept dose verbs).
- Loss: HOME 0 (BREACHED) or the concept's timer (CITY LOST). Win proxy: 3 live Exploits at the end with HOME > 0.

G2 (docs/handoff/raid_integration/G2_SIM.md): H "Infected Tide" = C-target's board + D's deck infection (INFECTED
cards tied to Sites, spread, DOSE cards, PURGE win) + the corp's sealed B picked after the response by a readable rule.
Variants H, H-noB, H-nospread (tuned numbers, H_TUNED) and H-brief (the brief's literal numbers, H_BRIEF).

Run: python tools/raid_concepts/sweep_g1.py [--campaigns N] [--jobs J] [--variants A-open,C-all,...] [--check]
Output: D:/rc_tmp/raid_design_lab/g1/sweep_g1.json (summary per variant x claim policy x raid player)."""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import statistics as stats
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g1_geo as G      # noqa: E402

# ------------------------------------------------------------------------------------------------ numbers
# Lab (sweep_l8 L14) values, kept.
START_BANK, START_HEAT, HOME_HP = 10, 44, 3
EXTRA_AT, STRONG_AT = 50, 75
GHOST_START, GHOST_HEAT, SPOOF_HEAT, EVADE_HEAT = 2, 5, 2, 10
SENTRY_PRICE, CLEAN_PRICE, MAX_PLACED, HAND_BASE = 3, 4, 2, 4
EXPLOIT_BONUS, HOME_LOSS_COST, HEAT_CARRY, HEAT_BAND, WOUND_COST, BREACH, KIT_VALUE = 6, 15, 0.5, 6, 5, 100, 2.5
START_DECK = (("s0", "D", "GUARD"), ("s1", "D", "GUARD"), ("s2", "N", "GUARD"), ("s3", "N", "GUARD"),
              ("s4", "E", "GUARD"), ("s5", "D", "SHIFT"), ("s6", "E", "SHIFT"), ("s7", "N", "JAM"))
TYPES = ("D", "N", "E")
PLACEABLE = ("GUARD", "SHIFT", "JAM")
CARD_RESPONSES = ("REDEPLOY", "DEPLOY", "JAM", "JAM_B")
EPS = 1e-9

# Campaign model (G1_SIM; assumed where the brief is silent: listed in G1_RESULTS.md).
NETRUNS = int(os.environ.get("G1_NETRUNS", 12))     # sensitivity runs set G1_NETRUNS=24
RAID_EVERY = 2              # base trigger: a raid once 2 netruns have passed since the last raid
INCOME_DIV = 6              # bank per netrun = sum(value // 6) over OK Sites (lab: sum(v // 3) per raid, 2 runs/raid)
HEAT_EXPLOIT = 5            # Solace SOLACE_BAL_r2: Exploit +5 Heat; any other claim +tier; a patrol +1
DOSE_EVERY = 3              # every 3rd netrun banks one netrun dose (B, D: a DOSE card; C: a held dose)
HEAT_BANDS = (25, 50, 75, 90)   # Heat band edges for the S2 table (GDD 4.3 majors 25/50/75 + PURGE 90)
PATCH_PRICE = 8             # PATCH HOME (an existing HQ verb, INTEGRATION_PLAN): +1 HOME pip, at most HOME_HP
TOP_KEYS = 3                # planner: full response search on the 3 best placements by HOLD EV

# A: Contagion Sweep (SOLACE_MERGE_IDEAS A), basis points.
A_HIT, A_HOME, A_TAKEN, A_EVADED, A_OBJECTIVE, A_LOST = 800, 1500, 500, 1000, 1500, 10000
A_COST = 0.003              # planner: value per basis point (100 % = 30 points before the -100 loss)
# B: Three Wards (%).
B_TICK, B_HIT, B_HOME, B_OBJECTIVE, B_EVADED, B_RAID_AT, B_FALL, B_WARDS_LOST = 2, 8, 15, 15, 5, 50, 100, 2
B_START_DOSES = 2
B_COST = 0.25               # planner: value per ward %
# C: Bloom Tide (milli-columns).
C_START, C_PACE = 4000, {1: 100, 2: 130, 3: 160}
C_HEAT_PCT = (100, 110, 125, 140, 160)      # bloom_pace_heat_pct_by_band (S2)
C_VIRUS_PCT, C_BREACH_PUSH, C_OBJECTIVE, C_EVADED, C_FIELD = 75, 500, 300, 200, 150
C_HQ_DOSE, C_DOSE_PRICE, C_DOSE_STEP = 300, 12, 4
C_COST = 0.01               # planner: value per milli of tide (a column = 10 points)
DOSE_VALUE = 3.0            # planner: a held dose / DOSE card mid-campaign
# D: Carrier Deck.
D_DRAW, D_INFECTED_DRAW_COST, D_SPREAD_COST = 5, 2, 2.0

# H: Infected Tide (G2_SIM.md): C-target's board and paths + D's deck infection. Concept codes: "H" (full),
# "Hb" (H-noB: sealed B fixed at generation), "Hs" (H-nospread). Numbers below are G2 assumptions/tuning.
H_CODES = {"H": "H", "H-noB": "Hb", "H-nospread": "Hs", "H-brief": "Hl"}
# H numbers. G2 tuned values (G2_RESULTS.md section 2); every one can be overridden from the environment (g2_tune.py).
# H-brief ("Hl") keeps the brief's literal numbers, so the tuning can be compared against the brief as written.
#   BRULE: the corp's post-response B rule. "typed" = owned Sites before the first sentry of the route's type (brief
#     literal: the corp sees through types and dodges every block); "any" = before the first sentry of any type (the
#     corp sees sentries, not their types); "greed" = all owned Sites on the route (sentries ignored).
#   KNOWN_ROUTE: chance a known beam is a route to HOME (else a street). SPREAD_MIN: Sites lost since the last raid
#   for the spread. DOSE_EVERY: a DOSE card every Nth netrun. CLEAN: price to clean an INFECTED card between raids.
#   PATCH: PATCH HOME price (+1 pip). HOME: HOME pips. ESCALATE: "" or "N:K" (from raid N, K extra known beams).
#   MAX_PLACED: sentries at PLAN (probe only). DOWN_RISK: planner value per DOWN Site (INFECTED at DECAY unless repaired).
H_TUNED = {"BRULE": "any", "KNOWN_ROUTE": 0.1, "SPREAD_MIN": 2, "DOSE_EVERY": 2, "CLEAN": 2, "PATCH": 8,
           "HOME": HOME_HP, "ESCALATE": "", "MAX_PLACED": MAX_PLACED, "DOWN_RISK": 2.0}
H_BRIEF = {"BRULE": "typed", "KNOWN_ROUTE": 0.5, "SPREAD_MIN": 1, "DOSE_EVERY": DOSE_EVERY, "CLEAN": CLEAN_PRICE,
           "PATCH": PATCH_PRICE, "HOME": HOME_HP, "ESCALATE": "", "MAX_PLACED": MAX_PLACED, "DOWN_RISK": 2.0}
for _k, _v in list(H_TUNED.items()):
    _e = os.environ.get("H_" + _k)
    if _e is not None:
        H_TUNED[_k] = type(_v)(_e) if not isinstance(_v, str) else _e


def hp(c: str, key: str):
    """An H number for concept code c (H-brief reads the brief's values; the rest read the tuned ones)."""
    return (H_BRIEF if c == "Hl" else H_TUNED)[key]

VARIANTS = ("A-open", "A-all", "A-target", "B-wards", "C-open", "C-all", "C-target",
            "C-open-tongue", "C-all-tongue", "C-target-tongue", "D-lattice", "H", "H-noB", "H-nospread", "H-brief")
POLICIES = ("greedy", "keys", "random")
PLAYERS = ("greedy", "naive")
OUT = r"D:/rc_tmp/raid_design_lab/g1/sweep_g1.json"

_GEO = {}


def geo_for(variant: str):
    g = _GEO.get(variant)
    if g is None:
        if variant in H_CODES:
            g = G.GraphGeo("P-target", "street", hp(H_CODES[variant], "KNOWN_ROUTE"))
        elif variant.startswith("A-") or variant.startswith("C-"):
            rule = {"open": "P-open", "all": "P-all", "target": "P-target"}[variant.split("-")[1]]
            g = G.GraphGeo(rule, "tongue" if variant.endswith("tongue") else "street")
        elif variant == "B-wards":
            g = G.WardGeo()
        else:
            g = G.LatticeGeo()
        _GEO[variant] = g
    return g


# ------------------------------------------------------------------------------------------------ state
class St:
    __slots__ = ("heat", "bank", "hp", "owned", "deck", "ghost", "opened", "inf", "wards", "fallen", "ward50",
                 "front", "crossed", "infected", "doses", "dose_buys", "dose_n", "obj_done", "breach_used", "lost",
                 "wounds_total", "sites_lost", "front_downs", "lost_flag", "last_lost", "inf_n", "purged")

    def __init__(self):
        self.lost_flag = 0          # H: Sites lost since the last spread check
        self.last_lost = ""         # H: the Site the spread card is tied to
        self.inf_n = 0              # H: monotonic INFECTED card id
        self.purged = False         # H: a raid survived with 0 INFECTED while holding the 3 Exploits
        self.heat, self.bank, self.hp = START_HEAT, START_BANK, HOME_HP
        self.owned = {}
        self.deck = START_DECK
        self.ghost = GHOST_START
        self.opened = frozenset()
        self.inf = 0
        self.wards = (0, 0, 0)
        self.fallen = ()
        self.ward50 = False
        self.front = C_START
        self.crossed = ()
        self.infected = frozenset()
        self.doses = 0
        self.dose_buys = 0
        self.dose_n = 0
        self.obj_done = frozenset()
        self.breach_used = False
        self.lost = ""
        self.wounds_total = 0
        self.sites_lost = 0
        self.front_downs = 0

    def copy(self) -> "St":
        o = St.__new__(St)
        for k in St.__slots__:
            setattr(o, k, getattr(self, k))
        o.owned = dict(self.owned)
        return o


def concept_of(variant: str) -> str:
    return H_CODES.get(variant, variant[0])


def is_h(c: str) -> bool:
    return c[0] == "H"


def h_spread(c: str) -> bool:
    return c in ("H", "Hb", "Hl")


def h_dyn_b(c: str) -> bool:
    """H: the corp picks sealed B after the response by the readable rule (H-noB keeps the generation pick)."""
    return c in ("H", "Hs", "Hl")


def add_infected(st: "St", sites, loss: bool = True) -> None:
    """H: one INFECTED card per Site (the card's type field holds the Site it is tied to; ids are monotonic)."""
    if not sites:
        return
    cards = list(st.deck)
    for s in sites:
        cards.append(("w%03d" % st.inf_n, s, "WOUND"))
        st.inf_n += 1
    st.deck = tuple(sorted(cards))
    st.wounds_total += len(sites)
    if loss:
        st.lost_flag += len(sites)
        st.last_lost = min(sites)


def infected_sites(st: "St") -> set:
    return {c[1] for c in st.deck if c[2] == "WOUND" and c[1] != "-"}


def front_size(geo, st: "St") -> int:
    """H: the visible front = Sites tied to INFECTED cards plus their TAKEN neighbours (base links)."""
    tied = infected_sites(st)
    out = set(tied)
    for s in tied:
        for n in geo.base_adj.get(s, ()):
            if st.owned.get(n) == "TAKEN":
                out.add(n)
    return len(out)


def wound_count(deck) -> int:
    return sum(1 for c in deck if c[2] == "WOUND")


def dose_cards(deck) -> list:
    return [c for c in deck if c[2] == "DOSE"]


def add_wounds(st: St, n: int) -> None:
    if n <= 0:
        return
    cards = list(st.deck)
    for _ in range(n):
        cards.append(("w%d" % wound_count(cards), "-", "WOUND"))
    st.deck = tuple(sorted(cards))
    st.wounds_total += n


def add_dose_card(st: St) -> None:
    st.deck = tuple(sorted(st.deck + (("x%d" % st.dose_n, "-", "DOSE"),)))
    st.dose_n += 1


def remove_card(st: St, cid: str) -> None:
    st.deck = tuple(c for c in st.deck if c[0] != cid)


def band(heat: int) -> int:
    return sum(1 for b in HEAT_BANDS if heat >= b)


def hand_size(heat: int) -> int:
    return HAND_BASE + int(heat >= EXTRA_AT) + int(heat >= STRONG_AT)


def exploits_live(geo, st: St) -> int:
    return sum(1 for s in geo.exploits if st.owned.get(s) in ("OK", "DOWN"))


def timer_pct(c: str, st: St) -> float:
    if c == "A":
        return st.inf / 100.0
    if c == "B":
        return float(max(st.wards))
    if c == "C":
        return (C_START - st.front) / 40.0
    healthy = len(st.deck) - wound_count(st.deck)
    return 100.0 * wound_count(st.deck) / max(1, healthy)


def value(geo, c: str, st: St, mid: bool = True) -> float:
    """The planner's value of a state: the lab score (bank + Sites + Exploits - HOME - Heat - wounds; kit mid-campaign)
    plus the concept's timer term; -100 for a lost campaign."""
    if st.lost or st.hp <= 0:
        return float(-BREACH)
    s = float(st.bank)
    for site, v in st.owned.items():
        if v == "OK":
            s += G.TIER_VALUE[geo.tier[site]] + (EXPLOIT_BONUS if site in geo.exploits else 0)
        elif v == "DOWN":
            x = G.TIER_VALUE[geo.tier[site]]
            s += x - x // 2 + (EXPLOIT_BONUS if site in geo.exploits else 0)
    s -= HOME_LOSS_COST * ((hp(c, "HOME") if is_h(c) else HOME_HP) - st.hp)
    s -= HEAT_CARRY * max(0, st.heat - START_HEAT)
    s -= HEAT_BAND * (int(st.heat >= EXTRA_AT) + int(st.heat >= STRONG_AT))
    w = wound_count(st.deck)
    s -= WOUND_COST * w
    if mid:
        s += KIT_VALUE * (st.ghost + sum(1 for x in st.deck if x[0].startswith("b")))
    if c == "A":
        s -= A_COST * st.inf
    elif c == "B":
        s -= B_COST * sum(st.wards[k] for k in range(3) if k not in st.fallen)
        if mid:
            s += DOSE_VALUE * len(dose_cards(st.deck))
    elif c == "C":
        s -= C_COST * (C_START - st.front)
        if mid:
            s += DOSE_VALUE * st.doses
    else:
        s -= D_SPREAD_COST * w
        if mid:
            s += DOSE_VALUE * len(dose_cards(st.deck))
        if is_h(c) and mid:
            # forecast rows: each Site left DOWN becomes an INFECTED card at DECAY unless repaired, and a loss
            # spreads +1 INFECTED at the next raid unless a DOSE card is spent
            downs = sum(1 for v in st.owned.values() if v == "DOWN")
            s -= hp(c, "DOWN_RISK") * downs
            if h_spread(c) and st.lost_flag + downs >= hp(c, "SPREAD_MIN"):
                s -= DOSE_VALUE if dose_cards(st.deck) else WOUND_COST + D_SPREAD_COST
    return s


# ------------------------------------------------------------------------------------------------ concept rules
def check_loss(geo, c: str, st: St) -> None:
    if st.lost:
        return
    if st.hp <= 0:
        st.lost = "BREACHED"
    elif c == "A" and st.inf >= A_LOST:
        st.lost = "CITY_LOST"
    elif c == "B" and len(st.fallen) >= B_WARDS_LOST:
        st.lost = "CITY_LOST"
    elif c == "C" and st.front <= 0:
        st.lost = "CITY_LOST"
    elif c == "D":
        w = wound_count(st.deck)
        if w > 0 and w >= len(st.deck) - w:
            st.lost = "CITY_LOST"
    elif is_h(c):
        w = wound_count(st.deck)
        if w > len(st.deck) - w:         # INFECTED outnumber healthy cards (DOSE cards count as healthy)
            st.lost = "CITY_LOST"


def ward_falls(geo, st: St) -> None:
    """B: a ward at 100 % falls: every owned Site in it goes TAKEN (a wound each); it stops ticking."""
    for w in range(3):
        if w in st.fallen or st.wards[w] < B_FALL:
            continue
        st.fallen = tuple(sorted(st.fallen + (w,)))
        n = 0
        for s, v in list(st.owned.items()):
            if geo.ward_of[s] == w and v != "TAKEN":
                st.owned[s] = "TAKEN"
                n += 1
        st.sites_lost += n
        add_wounds(st, n)


def apply_front(geo, st: St) -> None:
    """C: an owned OK Site the front reaches (column = tier x 1000 >= front) goes DOWN (infected); an infected Site the
    front has been pushed back past, still DOWN, is OK again."""
    inf = set(st.infected)
    for s, v in list(st.owned.items()):
        col = geo.tier[s] * 1000
        if col >= st.front:
            if v == "OK":
                st.owned[s] = "DOWN"
                inf.add(s)
                st.front_downs += 1
        elif s in inf:
            if v == "DOWN":
                st.owned[s] = "OK"
            inf.discard(s)
    inf = {s for s in inf if st.owned.get(s) == "DOWN"}
    st.infected = frozenset(inf)


def lose_annexes(geo, st: St) -> None:
    """D: annexes and objective Sites of a TAKEN anchor are lost (no wound: only the anchor wounds the deck)."""
    if not geo.parent:
        return
    for s in [s for s in st.owned if s in geo.parent and st.owned.get(geo.parent[s]) == "TAKEN"]:
        del st.owned[s]


def decay(geo, c: str, st: St, greedy: bool, log: dict | None = None) -> None:
    """DECAY (every raid after the first): owned DOWN Sites go TAKEN, a wound each (A: +5 % each). D: the spread."""
    downs = sorted(s for s, v in st.owned.items() if v == "DOWN")
    for s in downs:
        st.owned[s] = "TAKEN"
    st.sites_lost += len(downs)
    if is_h(c):
        add_infected(st, downs)
        spread = h_spread(c) and st.lost_flag >= hp(c, "SPREAD_MIN")
        st.lost_flag = 0
        dc = dose_cards(st.deck)
        if greedy and dc and (spread or wound_count(st.deck) > 0):
            remove_card(st, dc[0][0])        # one DOSE per DECAY: block the spread, else remove 1 INFECTED
            if not spread:
                remove_card(st, max(x for x in st.deck if x[2] == "WOUND")[0])
            if log is not None:
                log["decay_dose"] = log.get("decay_dose", 0) + 1
        elif spread:
            add_infected(st, [st.last_lost], loss=False)
            if log is not None:
                log["spread"] = log.get("spread", 0) + 1
        check_loss(geo, c, st)
        return
    add_wounds(st, len(downs))
    if c == "A":
        st.inf += A_TAKEN * len(downs)
    if c == "C":
        st.infected = frozenset(s for s in st.infected if st.owned.get(s) == "DOWN")
    if c == "D":
        lose_annexes(geo, st)
        if wound_count(st.deck) > 0:
            dc = dose_cards(st.deck)
            if greedy and dc:
                remove_card(st, dc[0][0])
                if log is not None:
                    log["decay_dose"] = log.get("decay_dose", 0) + 1
            else:
                add_wounds(st, 1)
    check_loss(geo, c, st)


# ------------------------------------------------------------------------------------------------ netrun
def apply_claim(geo, c: str, st: St, site) -> list:
    """Claim one Site (None = a patrol run). Returns concept raid triggers fired by the claim's netrun (C)."""
    if site is None:
        st.heat += 1
        tier = 1
    else:
        st.owned[site] = "OK"
        tier = geo.tier[site]
        if site in geo.objective_heat and site not in st.obj_done:
            st.obj_done = st.obj_done | {site}
            st.heat = max(0, st.heat + geo.objective_heat[site])
            if c == "A":
                st.inf = max(0, st.inf - A_OBJECTIVE)
            elif c == "B":
                w = geo.ward_of[site]
                st.wards = tuple(max(0, x - B_OBJECTIVE) if k == w else x for k, x in enumerate(st.wards))
            elif c == "C":
                st.front = min(C_START, st.front + C_OBJECTIVE)
            elif c == "D":
                add_dose_card(st)
        elif site in geo.objective_heat:
            st.heat += 1
        else:
            st.heat += tier + (HEAT_EXPLOIT if site in geo.exploits else 0)
        if c in "AC":
            live = {s for s, v in st.owned.items() if v != "TAKEN"}
            new = [l for l in G.SOL_LOCKED if l not in st.opened and l[0] in live and l[1] in live]
            if new:
                st.opened = st.opened | frozenset(new)
            if c == "C" and site == G.BREACH_KEY and not st.breach_used:
                st.breach_used = True
                st.front = min(C_START, st.front + C_BREACH_PUSH)
    return tier


def netrun(geo, c: str, st: St, site, seed: int, n: int) -> bool:
    """One netrun: claim, income, concept tick. Returns True when the concept queues a raid (B 50 %, C crossing)."""
    heat0 = st.heat
    tier = apply_claim(geo, c, st, site)
    st.bank += sum(G.TIER_VALUE[geo.tier[s]] // INCOME_DIV for s, v in st.owned.items() if v == "OK")
    queue = False
    if c == "B":
        st.wards = tuple(x if k in st.fallen else x + B_TICK for k, x in enumerate(st.wards))
        if not st.ward50 and max(st.wards) >= B_RAID_AT:
            st.ward50 = True
            queue = True
        ward_falls(geo, st)
    elif c == "C":
        pace = C_PACE[tier] * C_HEAT_PCT[band(heat0)] // 100
        if st.owned.get(G.VIRUS_KEY) in ("OK", "DOWN"):
            pace = pace * C_VIRUS_PCT // 100
        st.front -= pace
        apply_front(geo, st)
        for col in (3000, 2000, 1000):
            if st.front < col and col not in st.crossed:
                st.crossed = st.crossed + (col,)
                queue = True
    elif c == "D" or is_h(c):
        ids = sorted(x[0] for x in st.deck)
        random.Random("run:%d:%d" % (seed, n)).shuffle(ids)
        kinds = {x[0]: x[2] for x in st.deck}
        bad = sum(1 for i in ids[:D_DRAW] if kinds[i] == "WOUND")
        st.bank = max(0, st.bank - D_INFECTED_DRAW_COST * bad)
    if is_h(c):
        if n % hp(c, "DOSE_EVERY") == 0:
            add_dose_card(st)
    elif n % DOSE_EVERY == 0:
        if c in ("B", "D"):
            add_dose_card(st)
        elif c == "C":
            st.doses += 1
    check_loss(geo, c, st)
    return queue


def choose_claim(geo, c: str, st: St, policy: str, rng: random.Random, seed: int, n: int):
    opts = geo.claimable(st.owned, st.fallen)
    if not opts:
        return None
    if policy == "random":
        return rng.choice(opts)
    if policy == "keys":
        targets = {s for s in geo.exploits if st.owned.get(s) not in ("OK", "DOWN")}
        if targets:
            return min(opts, key=lambda s: (geo.exploit_distance(s, targets), -geo.value(s), s))
    best = None
    for s in opts:
        s2 = st.copy()
        netrun(geo, c, s2, s, seed, n)
        v = value(geo, c, s2)
        if best is None or v > best[0] + EPS:
            best = (v, s)
    return best[1]


# ------------------------------------------------------------------------------------------------ the raid sweep
class Sweep:
    __slots__ = ("sent", "ghost", "owned", "hp", "home_hit", "home_ward", "shield", "seen", "hits", "touches",
                 "quar", "taken", "front", "infected", "late", "dose_used", "bpick", "lean", "jam_b")

    def copy(self) -> "Sweep":
        o = Sweep.__new__(Sweep)
        o.sent = dict(self.sent)
        o.ghost = self.ghost
        o.owned = dict(self.owned)
        o.hp = self.hp
        o.home_hit = self.home_hit
        o.home_ward = self.home_ward
        o.shield = self.shield
        o.seen = set(self.seen)
        o.hits = list(self.hits)
        o.touches = self.touches
        o.quar = self.quar
        o.taken = self.taken
        o.front = self.front
        o.infected = self.infected
        o.late = self.late
        o.dose_used = self.dose_used
        o.bpick = self.bpick
        o.lean = self.lean
        o.jam_b = self.jam_b
        return o


def new_sweep(st: St, place) -> Sweep:
    sw = Sweep.__new__(Sweep)
    sw.sent = dict(place[0])
    sw.ghost = place[1]
    sw.owned = dict(st.owned)
    sw.hp = st.hp
    sw.home_hit = False
    sw.home_ward = -1
    sw.shield = False
    sw.seen = set()
    sw.hits = []
    sw.touches = 0
    sw.quar = -1
    sw.taken = 0
    sw.front = st.front
    sw.infected = st.infected
    sw.late = None
    sw.dose_used = None
    sw.bpick = -1
    sw.lean = -1
    sw.jam_b = False
    return sw


def scan(geo, sw: Sweep, ln, ctype: dict) -> None:
    cs = geo.cell_sites
    for cell in ln.cells:
        if cell == sw.ghost:
            continue
        j = sw.sent.get(cell)
        if j is not None and ctype[j] == ln.type:
            sw.touches += 1
            return
        for s in cs[cell]:
            v = sw.owned.get(s)
            if (v == "OK" or v == "DOWN") and s not in sw.seen:
                if v == "OK":
                    sw.owned[s] = "DOWN"
                elif sw.quar >= 0 and geo.ward_of[s] == sw.quar:
                    pass                                # B QUARANTINE: the ward's Sites stop at DOWN
                else:
                    sw.owned[s] = "TAKEN"
                    sw.taken += 1
                    if not geo.cell_live(cell, sw.owned):
                        sw.sent.pop(cell, None)
                sw.hits.append(s)
                sw.seen.add(s)
                sw.touches += 1
                break
    if ln.home and sw.ghost != G.HOME and not sw.home_hit:
        sw.touches += 1
        if sw.shield:
            return
        sw.hp = max(0, sw.hp - 1)
        sw.home_hit = True
        sw.home_ward = ln.ward


class Ctx:
    """One raid: geometry, concept, draw, hand, card types."""
    __slots__ = ("geo", "c", "draw", "hand", "cards", "ctype", "rel", "seed", "raid")


def make_ctx(geo, c: str, st: St, seed: int, raid: int) -> Ctx:
    ctx = Ctx()
    ctx.geo, ctx.c, ctx.seed, ctx.raid = geo, c, seed, raid
    ctx.draw = geo.draw(st, random.Random("raid:%d:%d" % (seed, raid)))
    ids = sorted(x[0] for x in st.deck)
    random.Random("hand:%d:%d" % (seed, raid)).shuffle(ids)
    ctx.hand = ids[:hand_size(st.heat)]
    ctx.cards = {x[0]: (x[1], x[2]) for x in st.deck}
    ctx.ctype = {k: v[0] for k, v in ctx.cards.items()}
    lines = list(ctx.draw.known) + list(ctx.draw.cands)
    if ctx.draw.hunters is not None:
        lines += ctx.draw.hunters
    rel = set()
    for ln in lines:
        rel.update(ln.cells)
    if ctx.draw.hunter_fn is not None:
        for f in (3500, 2500, 1500):
            for ln in ctx.draw.hunter_fn(f):
                rel.update(ln.cells)
    ctx.rel = [cell for cell in geo.cells if cell in rel and geo.cell_live(cell, st.owned)]
    return ctx


def hunters_now(ctx: Ctx, sw: Sweep) -> list:
    if ctx.draw.hunter_fn is not None:
        return ctx.draw.hunter_fn(sw.front)
    return ctx.draw.hunters


def escalation(ctx: Ctx) -> int:
    """H: extra known beams from raid N on (ESCALATE "N:K"; raid index counts from 0)."""
    if not is_h(ctx.c) or not hp(ctx.c, "ESCALATE"):
        return 0
    n, k = (int(x) for x in hp(ctx.c, "ESCALATE").split(":"))
    return k if ctx.raid >= n else 0


def n_known(ctx: Ctx, heat: int) -> int:
    e = escalation(ctx)
    return 1 + int(heat >= EXTRA_AT or e >= 1) + int(heat >= STRONG_AT or e >= 2)


def launch(ctx: Ctx, st: St, place):
    heat = st.heat + (GHOST_HEAT if place[1] is not None else 0)
    sw = new_sweep(st, place)
    for i in range(n_known(ctx, heat)):
        scan(ctx.geo, sw, ctx.draw.known[i], ctx.ctype)
    used = set(place[0].values())
    rhand = [(j,) + ctx.cards[j] for j in ctx.hand if j not in used]
    return heat, sw, rhand


def _has(rhand, verb) -> bool:
    return any(x[2] == verb for x in rhand)


def _deploy_card(rhand, t):
    ids = [x[0] for x in rhand if x[1] == t and x[2] != "WOUND"]
    return min(ids) if ids else None


def response_options(ctx: Ctx, sw: Sweep, rhand) -> list:
    """HOLD; REDEPLOY (SHIFT); DEPLOY t (a card of type t); SACRIFICE (live cells on a line, plus the cheapest live
    cell off every line); JAM (JAM card); B: QUARANTINE w (a DOSE card). Targets are live cells on this raid's lines
    (a sentry anywhere else changes nothing)."""
    geo = ctx.geo
    out = [("HOLD",)]
    live_rel = [cell for cell in ctx.rel if geo.cell_live(cell, sw.owned)]
    targets = [cell for cell in live_rel if cell not in sw.sent]
    if _has(rhand, "SHIFT"):
        for s in [cell for cell in geo.cells if cell in sw.sent]:
            for cell in targets:
                out.append(("REDEPLOY", s, cell))
    for t in TYPES:
        if _deploy_card(rhand, t) is not None:
            for cell in targets:
                out.append(("DEPLOY", t, cell))
    if sw.ghost != G.HOME and not sw.home_hit:
        sac = list(live_rel)
        off = [cell for cell in geo.cells if cell not in ctx.rel and geo.cell_live(cell, sw.owned)]
        if off:
            sac.append(min(off, key=lambda cell: (geo.cell_value(cell, sw.owned), cell)))
        for cell in sac:
            out.append(("SACRIFICE", cell))
    if _has(rhand, "JAM"):
        out.append(("JAM",))
        if h_dyn_b(ctx.c):
            out.append(("JAM_B",))      # H: the JAM card scrambles the corp's B pick instead of the hunter
    if ctx.c == "B" and _has(rhand, "DOSE"):
        for w in range(3):
            if any(geo.ward_of[s] == w and v != "TAKEN" for s, v in sw.owned.items()):
                out.append(("QUARANTINE", w))
    return out


def respond(ctx: Ctx, sw: Sweep, r: tuple, rhand) -> None:
    geo = ctx.geo
    k = r[0]
    if k == "REDEPLOY":
        sw.sent[r[2]] = sw.sent.pop(r[1])
    elif k == "DEPLOY":
        sw.sent[r[2]] = _deploy_card(rhand, r[1])
    elif k == "SACRIFICE":
        for s in geo.cell_sites[r[1]]:
            if sw.owned.get(s) in ("OK", "DOWN"):
                sw.owned[s] = "TAKEN"
                sw.taken += 1
        sw.sent.pop(r[1], None)
        sw.shield = True
    elif k == "QUARANTINE":
        sw.quar = r[1]
        sw.dose_used = min(x[0] for x in rhand if x[2] == "DOSE")
    elif k == "JAM_B":
        sw.jam_b = True


def route_pull(geo, sw: Sweep, ln, ctype: dict, rule: str) -> int:
    """H B rule: live owned Sites on a route before the first sentry of its type (the route's unblocked Sites)."""
    n = 0
    for cell in ln.cells:
        if cell == sw.ghost:
            continue
        j = sw.sent.get(cell)
        if j is not None and (rule == "any" or rule == "typed" and ctype[j] == ln.type):
            break
        for s in geo.cell_sites[cell]:
            if sw.owned.get(s) in ("OK", "DOWN"):
                n += 1
    return n


def b_rule(ctx: Ctx, sw: Sweep, k: int, tie: int) -> int:
    """H: the corp's B (index into the two candidates other than A) = the one with more unblocked owned Sites;
    a tie keeps `tie` (the lean shown at REVEAL A; the lean itself breaks ties by display order)."""
    others = [x for x in range(3) if x != k]
    p = [route_pull(ctx.geo, sw, ctx.draw.cands[b], ctx.ctype, hp(ctx.c, "BRULE")) for b in others]
    if p[0] > p[1]:
        return 0
    if p[1] > p[0]:
        return 1
    return tie


def b_pairs(ctx: Ctx, sw_pre: Sweep, sw_post: Sweep, k: int) -> list:
    """The (bi, b) outcomes the planner averages over: both for fixed-B concepts, the corp's pick for H."""
    others = [x for x in range(3) if x != k]
    if not h_dyn_b(ctx.c):
        return list(enumerate(others))
    lean = b_rule(ctx, sw_pre, k, 0)
    bi = b_rule(ctx, sw_post, k, lean)
    if sw_post.jam_b:
        bi = 1 - bi
    return [(bi, others[bi])]


def late_options(ctx: Ctx, st: St, sw: Sweep, rhand, resp) -> list:
    """The late slot after REVEAL B (R15): C FIELD (a held dose, push 150); D CURE (a DOSE card: -1 INFECTED)."""
    if ctx.c == "C" and st.doses > 0:
        return [None, "FIELD"]
    if ctx.c == "D" and wound_count(st.deck) > 0 and _has(rhand, "DOSE") and resp[0] != "QUARANTINE":
        return [None, "CURE"]
    return [None]


def do_late(ctx: Ctx, sw: Sweep, opt, rhand) -> None:
    if opt is None:
        return
    sw.late = opt
    if opt == "FIELD":
        sw.front = min(C_START, sw.front + C_FIELD)
        inf = set(sw.infected)
        for s in list(inf):
            if ctx.geo.tier[s] * 1000 < sw.front:
                if sw.owned.get(s) == "DOWN":
                    sw.owned[s] = "OK"
                inf.discard(s)
        sw.infected = frozenset(inf)
    elif opt == "CURE":
        sw.dose_used = min(x[0] for x in rhand if x[2] == "DOSE")


def close(ctx: Ctx, st: St, place, heat: int, sw: Sweep, resp: tuple) -> St:
    geo, c = ctx.geo, ctx.c
    ns = st.copy()
    ns.owned = sw.owned
    ns.hp = sw.hp
    evaded = sw.touches == 0 and sw.taken == 0 and not sw.shield
    if evaded:
        heat -= EVADE_HEAT
    if resp[0] in CARD_RESPONSES:
        heat += SPOOF_HEAT
    ns.heat = max(0, heat)
    if place[1] is not None:
        ns.ghost -= 1
    ns.sites_lost += sw.taken
    if is_h(c):
        add_infected(ns, sorted(s for s, v in sw.owned.items() if v == "TAKEN" and st.owned.get(s) != "TAKEN"))
    else:
        add_wounds(ns, sw.taken)
    if sw.dose_used is not None:
        remove_card(ns, sw.dose_used)
    if sw.late == "CURE":
        ws = [x for x in ns.deck if x[2] == "WOUND"]
        if ws:
            remove_card(ns, max(ws)[0])
    if c == "A":
        ns.inf += A_HIT * len(sw.hits) + (A_HOME if sw.home_hit else 0) + A_TAKEN * sw.taken
        if evaded:
            ns.inf = max(0, ns.inf - A_EVADED)
    elif c == "B":
        w = list(ns.wards)
        for s in sw.hits:
            k = geo.ward_of[s]
            if k != sw.quar and k not in ns.fallen:
                w[k] += B_HIT
        if sw.home_hit and sw.home_ward >= 0 and sw.home_ward != sw.quar and sw.home_ward not in ns.fallen:
            w[sw.home_ward] += B_HOME
        if evaded:
            w = [x if k in ns.fallen else max(0, x - B_EVADED) for k, x in enumerate(w)]
        ns.wards = tuple(w)
        ward_falls(geo, ns)
    elif c == "C":
        if sw.late == "FIELD":
            ns.doses -= 1
        ns.front = sw.front
        ns.infected = sw.infected
        if evaded:
            ns.front = min(C_START, ns.front + C_EVADED)
        apply_front(geo, ns)
    elif c == "D":
        lose_annexes(geo, ns)
    check_loss(geo, c, ns)
    if is_h(c) and not ns.lost and wound_count(ns.deck) == 0 and exploits_live(geo, ns) >= 3:
        ns.purged = True
    return ns


def tier(before: St, after: St, sw: Sweep) -> str:
    if after.hp <= 0:
        return "BREACHED"
    if after.hp < before.hp:
        return "DAMAGED"
    new_down = sum(1 for s, v in after.owned.items() if v == "DOWN" and before.owned.get(s) == "OK")
    new_taken = sum(1 for s, v in after.owned.items() if v == "TAKEN" and before.owned.get(s) != "TAKEN")
    if sw.touches == 0 and new_taken == 0:
        return "EVADED"
    return "BATTERED" if new_down >= 2 or new_taken >= 1 else "HOLDS"


def play_one(ctx: Ctx, st: St, place, resp, k: int, bi: int, late, h: int):
    """One full raid on one (A, B, late, hunter) outcome. Returns (state after, tier, sweep)."""
    heat, sw, rhand = launch(ctx, st, place)
    pre = sw.copy()
    respond(ctx, sw, resp, rhand)
    d = ctx.draw
    if h_dyn_b(ctx.c):
        sw.lean = b_rule(ctx, pre, k, 0)
        bi = b_pairs(ctx, pre, sw, k)[0][0]
    sw.bpick = bi
    scan(ctx.geo, sw, d.cands[k], ctx.ctype)
    b = [x for x in range(3) if x != k][bi]
    scan(ctx.geo, sw, d.cands[b], ctx.ctype)
    do_late(ctx, sw, late, rhand)
    if resp[0] != "JAM":
        scan(ctx.geo, sw, hunters_now(ctx, sw)[h], ctx.ctype)
    ns = close(ctx, st, place, heat, sw, resp)
    return ns, tier(st, ns, sw), sw


def eval_place(ctx: Ctx, st: St, place, responses: bool):
    """Per sealed A: (value, response, {bi: late}) maximizing the mean over B (and, per B, the best late slot over the
    two hunter streets). responses=False: HOLD only, no late slot (the HOLD screen)."""
    geo, c = ctx.geo, ctx.c
    heat, sw0, rhand = launch(ctx, st, place)
    opts = response_options(ctx, sw0, rhand) if responses else [("HOLD",)]
    d = ctx.draw
    per = [None, None, None]
    for r in opts:
        sw1 = sw0.copy()
        respond(ctx, sw1, r, rhand)
        lates = late_options(ctx, st, sw1, rhand, r) if responses else [None]
        for k in range(3):
            sw2 = sw1.copy()
            scan(geo, sw2, d.cands[k], ctx.ctype)
            tot = 0.0
            lp = {}
            pairs = b_pairs(ctx, sw0, sw1, k)
            for bi, b in pairs:
                sw3 = sw2.copy()
                scan(geo, sw3, d.cands[b], ctx.ctype)
                best_l = None
                for lo in lates:
                    sw4 = sw3.copy()
                    do_late(ctx, sw4, lo, rhand)
                    hs = hunters_now(ctx, sw4)
                    v = 0.0
                    for h in range(2):
                        sw5 = sw4.copy()
                        if r[0] != "JAM":
                            scan(geo, sw5, hs[h], ctx.ctype)
                        v += value(geo, c, close(ctx, st, place, heat, sw5, r))
                    v /= 2
                    if best_l is None or v > best_l[0] + EPS:
                        best_l = (v, lo)
                tot += best_l[0]
                lp[bi] = best_l[1]
            v = tot / len(pairs)
            if per[k] is None or v > per[k][0] + EPS:
                per[k] = (v, r, lp)
    return per


def placements(ctx: Ctx, st: St, cells: list, ghost_ok: bool) -> list:
    """(sentries {cell: card id}, ghost) with at most MAX_PLACED hand cards on the given cells, distinct by the
    (type, verb) signature per cell (a signature uses its lowest free id). Ghost: None, then HOME (kit)."""
    hids = [i for i in ctx.hand if ctx.cards[i][1] in PLACEABLE]
    sigs = []
    for i in hids:
        if ctx.cards[i] not in sigs:
            sigs.append(ctx.cards[i])

    def pick(sig, used):
        ids = [i for i in hids if i not in used and ctx.cards[i] == sig]
        return min(ids) if ids else None

    maps = [{}]
    for a, ca in enumerate(cells):
        for s1 in sigs:
            j1 = pick(s1, ())
            maps.append({ca: j1})
            for cb in cells[a + 1:]:
                for s2 in sigs:
                    j2 = pick(s2, (j1,))
                    if j2 is not None:
                        maps.append({ca: j1, cb: j2})
    ghosts = [None] + ([G.HOME] if ghost_ok and st.ghost > 0 else [])
    if is_h(ctx.c) and hp(ctx.c, "MAX_PLACED") < MAX_PLACED:
        maps = [m for m in maps if len(m) <= hp(ctx.c, "MAX_PLACED")]
    return [(m, g) for g in ghosts for m in maps]


def type_key(ctx: Ctx, place) -> tuple:
    return (tuple(sorted((c, ctx.ctype[j]) for c, j in place[0].items())), place[1])


def full_key(ctx: Ctx, place) -> tuple:
    used = set(place[0].values())
    rh = [(j,) + ctx.cards[j] for j in ctx.hand if j not in used]
    return (type_key(ctx, place), _has(rh, "SHIFT"), _has(rh, "JAM"), _has(rh, "DOSE"),
            tuple(t for t in TYPES if _deploy_card(rh, t) is not None))


def greedy_plan(ctx: Ctx, st: St):
    """HOLD screen of every placement on this raid's live cells (type-map cached), then the full response and
    late-slot search on the TOP_KEYS best. Returns (place, per-A plan, placement gap, n distinct placements)."""
    places = placements(ctx, st, ctx.rel, True)
    screen = {}
    for p in places:
        key = type_key(ctx, p)
        if key not in screen:
            per = eval_place(ctx, st, p, False)
            screen[key] = sum(x[0] for x in per) / 3
    evs = sorted(screen.values(), reverse=True)
    gap = evs[0] - stats.median(evs) if evs else 0.0
    top = set(k for k, _ in sorted(screen.items(), key=lambda kv: -kv[1])[:TOP_KEYS])
    best = None
    seen = set()
    for p in places:
        if type_key(ctx, p) not in top:
            continue
        fk = full_key(ctx, p)
        if fk in seen:
            continue
        seen.add(fk)
        per = eval_place(ctx, st, p, True)
        ev = sum(x[0] for x in per) / 3
        if best is None or ev > best[0] + EPS:
            best = (ev, p, per)
    return best[1], best[2], gap, len(screen)


def naive_place(ctx: Ctx, st: St):
    geo = ctx.geo
    live = geo.live_cells(st.owned)
    cap = hp(ctx.c, "MAX_PLACED") if is_h(ctx.c) else MAX_PLACED
    ids = [j for j in ctx.hand if ctx.cards[j][1] in PLACEABLE][:min(cap, len(live))]
    cells = sorted(live, key=lambda cell: (-geo.cell_value(cell, st.owned), geo.cells.index(cell)))
    return (dict(zip(cells, ids)), None)


def choose_late(ctx: Ctx, st: St, place, resp, k: int, bi: int):
    """After REVEAL B: the late option with the best mean over the two hunter streets (earliest on ties)."""
    heat, sw0, rhand = launch(ctx, st, place)
    respond(ctx, sw0, resp, rhand)
    lates = late_options(ctx, st, sw0, rhand, resp)
    if len(lates) == 1:
        return None
    best = None
    for lo in lates:
        v = sum(value(ctx.geo, ctx.c, play_one(ctx, st, place, resp, k, bi, lo, h)[0]) for h in range(2)) / 2
        if best is None or v > best[0] + EPS:
            best = (v, lo)
    return best[1]


# ------------------------------------------------------------------------------------------------ between
def clean_price(c: str) -> int:
    return hp(c, "CLEAN") if is_h(c) else CLEAN_PRICE


def between(geo, c: str, st: St, opt) -> St:
    rep, build, dose, patch = opt
    ns = st.copy()
    hp_max, price = (hp(c, "HOME"), hp(c, "PATCH")) if is_h(c) else (HOME_HP, PATCH_PRICE)
    if patch and ns.hp < hp_max and ns.bank >= price:
        ns.bank -= price
        ns.hp += 1
    if rep is not None and ns.owned.get(rep) == "DOWN":
        cost = G.TIER_VALUE[geo.tier[rep]] // 2
        if ns.bank >= cost and not (c == "C" and rep in ns.infected):
            ns.bank -= cost
            ns.owned[rep] = "OK"
    if build in TYPES and ns.bank >= SENTRY_PRICE:
        ns.bank -= SENTRY_PRICE
        ns.deck = tuple(sorted(ns.deck + (("b%d" % sum(1 for x in ns.deck if x[0].startswith("b")), build, "GUARD"),)))
    elif build == "CLEAN" and ns.bank >= clean_price(c):
        ws = [x for x in ns.deck if x[2] == "WOUND"]
        if ws:
            ns.bank -= clean_price(c)
            remove_card(ns, max(ws)[0])
    if dose == "HQ" and ns.doses > 0:
        ns.doses -= 1
        ns.front = min(C_START, ns.front + C_HQ_DOSE)
        apply_front(geo, ns)
    elif dose == "BUY":
        price = C_DOSE_PRICE + C_DOSE_STEP * ns.dose_buys
        if ns.bank >= price:
            ns.bank -= price
            ns.dose_buys += 1
            ns.front = min(C_START, ns.front + C_HQ_DOSE)
            apply_front(geo, ns)
    return ns


def between_options(geo, c: str, st: St) -> list:
    downs = sorted(s for s, v in st.owned.items() if v == "DOWN" and not (c == "C" and s in st.infected))
    builds = [None, "D", "N", "E"] + (["CLEAN"] if wound_count(st.deck) else [])
    doses = [None]
    if c == "C":
        if st.doses > 0:
            doses.append("HQ")
        doses.append("BUY")
    hp_max, price = (hp(c, "HOME"), hp(c, "PATCH")) if is_h(c) else (HOME_HP, PATCH_PRICE)
    patches = [False, True] if st.hp < hp_max else [False]
    out = []
    for r in [None] + downs:
        rc = G.TIER_VALUE[geo.tier[r]] // 2 if r else 0
        for b in builds:
            bc = 0 if b is None else (clean_price(c) if b == "CLEAN" else SENTRY_PRICE)
            for d in doses:
                dc = (C_DOSE_PRICE + C_DOSE_STEP * st.dose_buys) if d == "BUY" else 0
                for pt in patches:
                    if rc + bc + dc + (price if pt else 0) <= st.bank:
                        out.append((r, b, d, pt))
    return out


def greedy_between(geo, c: str, st: St):
    best = None
    for opt in between_options(geo, c, st):
        s2 = between(geo, c, st, opt)
        decay(geo, c, s2, True)      # value the state the next raid will see (repairs dodge DECAY)
        v = value(geo, c, s2)
        if best is None or v > best[0] + EPS:
            best = (v, opt)
    return best[1]


def naive_between(geo, c: str, st: St):
    """Patch HOME when it is down and affordable, then repair the biggest affordable DOWN Site."""
    hp_max, price = (hp(c, "HOME"), hp(c, "PATCH")) if is_h(c) else (HOME_HP, PATCH_PRICE)
    patch = st.hp < hp_max and st.bank >= price
    bank = st.bank - (price if patch else 0)
    rep = None
    for s, v in sorted(st.owned.items()):
        if v == "DOWN" and not (c == "C" and s in st.infected):
            cost = G.TIER_VALUE[geo.tier[s]] // 2
            if bank >= cost and (rep is None or geo.value(s) > geo.value(rep)):
                rep = s
    return (rep, None, None, patch)


# ------------------------------------------------------------------------------------------------ campaign
def raid(geo, c: str, st: St, seed: int, idx: int, greedy: bool, rec: dict) -> St:
    if idx > 0:
        decay(geo, c, st, greedy, rec)
        if st.lost:
            return st
    ctx = make_ctx(geo, c, st, seed, idx)
    d = ctx.draw
    k, b, h = d.real, d.real_b, d.hunt_real
    bi = [x for x in range(3) if x != k].index(b)
    if greedy:
        place, per, gap, n_places = greedy_plan(ctx, st)
        resp = per[k][1]
        late = choose_late(ctx, st, place, resp, k, bi)
    else:
        place, gap, n_places = naive_place(ctx, st), None, None
        resp, late = ("HOLD",), None
    front0 = front_size(geo, st) if is_h(c) else 0
    inf0 = wound_count(st.deck)
    ns, tr, sw = play_one(ctx, st, place, resp, k, bi, late, h)
    b_flip = None
    if h_dyn_b(c):
        b_flip = sw.bpick != sw.lean
        bi = sw.bpick
        b = [x for x in range(3) if x != k][bi]
    # metrics
    hold = [play_one(ctx, st, place, ("HOLD",), kk, bb, None, hh)
            for kk in range(3) for bb in range(2) for hh in range(2)]
    hold_tiers = [x[1] for x in hold]
    if h_dyn_b(c):
        real_hold = play_one(ctx, st, place, ("HOLD",), k, 0, None, h)[1]
    else:
        real_hold = hold_tiers[k * 4 + bi * 2 + h]
    def at_risk(x):     # INFECTED this outcome adds now (TAKEN) or at the next DECAY (new DOWN, if not repaired)
        return (x[0].wounds_total - st.wounds_total
                + sum(1 for q, v in x[0].owned.items() if v == "DOWN" and st.owned.get(q) == "OK"))
    inf_rows = sum(1 for x in hold if at_risk(x) > 0) / len(hold)
    inf_fc = sum(at_risk(x) for x in hold) / len(hold)
    after = []
    for bb in range(2):
        lo = choose_late(ctx, st, place, resp, k, bb) if greedy else None
        for hh in range(2):
            after.append(play_one(ctx, st, place, resp, k, bb, lo, hh)[1])
    late_dec = False
    if late is not None:
        late_dec = play_one(ctx, st, place, resp, k, bi, None, h)[1] != tr
    owned_live = {s for s, v in st.owned.items() if v != "TAKEN"}
    heat_l = st.heat + (GHOST_HEAT if place[1] is not None else 0)
    ran = list(d.known[:n_known(ctx, heat_l)])
    ran += [d.cands[k], d.cands[b]]
    if resp[0] != "JAM":
        hsw = new_sweep(st, place)
        hsw.front = sw.front
        ran.append(hunters_now(ctx, hsw)[h])
    touch = sum(1 for ln in ran if any(s in owned_live for cell in ln.cells for s in geo.cell_sites[cell]))
    lines = [ln.cells for ln in list(d.known) + list(d.cands)]
    if d.hunters is not None:
        lines += [ln.cells for ln in d.hunters]
    else:
        lines += [ln.cells for ln in d.hunter_fn(st.front)]
    rec["raids"].append({
        "tier": tr, "locked": len(set(hold_tiers)) == 1, "live_after": len(set(after)) > 1,
        "decides": tr != real_hold, "late": late, "late_decides": late_dec, "resp": resp[0],
        "gap": gap, "n_places": n_places, "n_paths": d.n_paths, "variety": len(set(lines)),
        "touch": touch, "ran": len(ran), "home": sw.home_hit, "ghost": place[1] is not None,
        "dead": sum(1 for j in ctx.hand if ctx.cards[j][1] == "WOUND"),
        "b_flip": b_flip, "front": front0, "inf_start": inf0, "inf_add": ns.wounds_total - st.wounds_total,
        "inf_rows": inf_rows if is_h(c) else None, "inf_fc": inf_fc if is_h(c) else None})
    if ns.lost:
        return ns
    opt = greedy_between(geo, c, ns) if greedy else naive_between(geo, c, ns)
    rec["between"].append("%s|%s|%s|%s" % (opt[0] is not None, opt[1], opt[2], opt[3]))
    return between(geo, c, ns, opt)


def campaign(variant: str, policy: str, player: str, seed: int) -> dict:
    geo = geo_for(variant)
    c = concept_of(variant)
    st = St()
    if is_h(c):
        st.hp = hp(c, "HOME")
    if c == "B":
        for _ in range(B_START_DOSES):
            add_dose_card(st)
    rng = random.Random("claim:%d" % seed)
    rec = {"raids": [], "between": []}
    since = 0
    n_raids = 0
    netruns = 0
    for n in range(1, NETRUNS + 1):
        site = choose_claim(geo, c, st, policy, rng, seed, n)
        q = netrun(geo, c, st, site, seed, n)
        netruns = n
        if st.lost:
            break
        since += 1
        if q or since >= RAID_EVERY:
            st = raid(geo, c, st, seed, n_raids, player == "greedy", rec)
            n_raids += 1
            since = 0
            if st.lost:
                break
    hold3 = not st.lost and st.hp > 0 and exploits_live(geo, st) >= 3
    win = hold3 and (st.purged or not is_h(c))
    return {"lost": st.lost, "win": win, "hold3": hold3, "purged": st.purged, "spread": rec.get("spread", 0), "netruns": netruns, "raids": n_raids, "wounds": st.wounds_total,
            "sites_lost": st.sites_lost, "timer": timer_pct(c, st), "front_downs": st.front_downs,
            "exploits": exploits_live(geo, st), "hp": st.hp, "heat": st.heat, "rec": rec,
            "decay_dose": rec.get("decay_dose", 0)}


def run_task(task):
    variant, policy, player, seeds = task
    return [(variant, policy, player, s, campaign(variant, policy, player, s)) for s in seeds]


# ------------------------------------------------------------------------------------------------ aggregation
def _entropy(xs) -> float:
    if not xs:
        return 0.0
    n = len(xs)
    cnt = {}
    for x in xs:
        cnt[x] = cnt.get(x, 0) + 1
    return -sum(v / n * math.log2(v / n) for v in cnt.values())


def aggregate(rows: list) -> dict:
    raids = [r for x in rows for r in x["rec"]["raids"]]
    nr = max(1, len(raids))
    bw = [b for x in rows for b in x["rec"]["between"]]
    gaps = [r["gap"] for r in raids if r["gap"] is not None]
    tiers = [r["tier"] for r in raids]
    resp = [r["resp"] for r in raids]
    lates = [r for r in raids if r["late"] is not None]
    n = len(rows)
    return {
        "campaigns": n,
        "loss": round(sum(1 for x in rows if x["lost"]) / n, 3),
        "breached": round(sum(1 for x in rows if x["lost"] == "BREACHED") / n, 3),
        "city_lost": round(sum(1 for x in rows if x["lost"] == "CITY_LOST") / n, 3),
        "win": round(sum(1 for x in rows if x["win"]) / n, 3),
        "netruns": round(stats.mean(x["netruns"] for x in rows), 2),
        "raids": round(stats.mean(x["raids"] for x in rows), 2),
        "raids_per_netrun": round(sum(x["raids"] for x in rows) / max(1, sum(x["netruns"] for x in rows)), 3),
        "locked_at_plan": round(sum(r["locked"] for r in raids) / nr, 3),
        "live_after_response": round(sum(r["live_after"] for r in raids) / nr, 3),
        "response_decides": round(sum(r["decides"] for r in raids) / nr, 3),
        "late_use": round(len(lates) / nr, 3),
        "late_decides": round(sum(r["late_decides"] for r in raids) / nr, 3),
        "placement_gap": round(stats.mean(gaps), 2) if gaps else None,
        "n_places": round(stats.mean(r["n_places"] for r in raids if r["n_places"] is not None), 1)
        if gaps else None,
        "between_entropy": round(_entropy(bw), 2),
        "path_variety": round(sum(r["variety"] for r in raids) / nr, 2),
        "paths_available": round(sum(r["n_paths"] for r in raids) / nr, 1),
        "relevance": round(sum(r["touch"] for r in raids) / max(1, sum(r["ran"] for r in raids)), 3),
        "home_hit_rate": round(sum(r["home"] for r in raids) / nr, 3),
        "wounds": round(stats.mean(x["wounds"] for x in rows), 2),
        "sites_lost": round(stats.mean(x["sites_lost"] for x in rows), 2),
        "timer_end": round(stats.mean(x["timer"] for x in rows), 1),
        "timer_decisive": round(sum(1 for x in rows if x["lost"] == "CITY_LOST") / n, 3),
        "front_downs": round(stats.mean(x["front_downs"] for x in rows), 2),
        "decay_dose": round(stats.mean(x["decay_dose"] for x in rows), 2),
        "dead_per_hand": round(sum(r["dead"] for r in raids) / nr, 2),
        "tier_mix": {t: tiers.count(t) for t in ("BREACHED", "DAMAGED", "EVADED", "BATTERED", "HOLDS")},
        "response_mix": {k: resp.count(k) for k in sorted(set(resp))},
        "ghost_rate": round(sum(r["ghost"] for r in raids) / nr, 3),
        "hold3": round(sum(1 for x in rows if x.get("hold3")) / n, 3),
        "purge": round(sum(1 for x in rows if x.get("purged")) / n, 3),
        "infected_per_campaign": round(stats.mean(x["wounds"] for x in rows), 2),
        "spread": round(stats.mean(x.get("spread", 0) for x in rows), 2),
        "b_flip_rate": _rate([r.get("b_flip") for r in raids]),
        "b_flip_nonhold": _rate([r.get("b_flip") for r in raids if r["resp"] != "HOLD"]),
        "front_size": round(sum(r.get("front", 0) for r in raids) / nr, 2),
        "inf_add_per_raid": round(sum(r.get("inf_add", 0) for r in raids) / nr, 2),
        "forecast_inf_rows": _rate([r.get("inf_rows") for r in raids]),
        "forecast_inf_mean": _rate([r.get("inf_fc") for r in raids]),
    }


def _rate(xs):
    xs = [float(x) for x in xs if x is not None]
    return round(sum(xs) / len(xs), 3) if xs else None


def check(campaigns: int) -> None:
    """Determinism: the same campaign twice gives the same record (one seed per variant and player)."""
    for v in VARIANTS:
        for p in PLAYERS:
            a = json.dumps(campaign(v, "greedy", p, 7), sort_keys=True, default=str)
            b = json.dumps(campaign(v, "greedy", p, 7), sort_keys=True, default=str)
            assert a == b, (v, p)
    print("check ok: seeded replay matches for", len(VARIANTS), "variants x", len(PLAYERS), "players", flush=True)


TABLE_COLS = ("loss", "city_lost", "win", "hold3", "purge", "b_flip_rate", "infected_per_campaign", "spread",
              "front_size", "forecast_inf_rows", "raids_per_netrun", "locked_at_plan", "live_after_response",
              "response_decides", "late_use", "late_decides", "placement_gap", "between_entropy", "path_variety",
              "paths_available", "relevance", "home_hit_rate", "wounds", "sites_lost", "timer_end", "netruns")


def print_table(path: str) -> None:
    with open(path) as f:
        d = json.load(f)
    print("campaigns/policy", d["campaigns_per_policy"], "runtime_s", d["runtime_s"])
    print("variant policy player " + " ".join(TABLE_COLS))
    for v, byp in d["summary"].items():
        for pol in ("all",) + POLICIES:
            for pl in PLAYERS:
                if pol in byp and pl in byp[pol]:
                    r = byp[pol][pl]
                    print(v, pol, pl, " ".join(str(r.get(c)) for c in TABLE_COLS))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaigns", type=int, default=200)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--chunk", type=int, default=10)
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--table", default="", help="print the compact table of a summary JSON and exit")
    a = ap.parse_args()
    if a.table:
        print_table(a.table)
        return
    if a.check:
        check(a.campaigns)
        return
    t0 = time.time()
    variants = a.variants.split(",")
    tasks = []
    for v in variants:
        for pol in POLICIES:
            for pl in PLAYERS:
                for s0 in range(0, a.campaigns, a.chunk):
                    tasks.append((v, pol, pl, list(range(s0, min(a.campaigns, s0 + a.chunk)))))
    # greedy chunks first (the slow ones), so the pool drains evenly
    tasks.sort(key=lambda t: (t[2] != "greedy", t[0], t[1], t[3][0]))
    rows = {}
    done = 0
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.Pool(a.jobs) as pool:
            for res in pool.imap_unordered(run_task, tasks):
                for v, pol, pl, s, r in res:
                    rows.setdefault((v, pol, pl), []).append((s, r))
                done += 1
                if done % 20 == 0:
                    print("progress %d/%d tasks %.0fs" % (done, len(tasks), time.time() - t0), flush=True)
    else:
        for t in tasks:
            for v, pol, pl, s, r in run_task(t):
                rows.setdefault((v, pol, pl), []).append((s, r))
    summary = {}
    for (v, pol, pl), lst in sorted(rows.items()):
        lst.sort(key=lambda x: x[0])
        summary.setdefault(v, {}).setdefault(pol, {})[pl] = aggregate([r for _, r in lst])
    for v in summary:
        for pl in PLAYERS:
            allr = [r for pol in POLICIES for _, r in sorted(rows.get((v, pol, pl), []), key=lambda x: x[0])]
            if allr:
                summary[v].setdefault("all", {})[pl] = aggregate(allr)
    elapsed = time.time() - t0
    out = {"campaigns_per_policy": a.campaigns, "runtime_s": round(elapsed, 1), "jobs": a.jobs, "netruns": NETRUNS,
           "summary": summary}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print("DONE runtime %.0fs -> %s" % (elapsed, a.out), flush=True)


if __name__ == "__main__":
    main()
