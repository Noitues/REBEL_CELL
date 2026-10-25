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
CARD_RESPONSES = ("REDEPLOY", "DEPLOY", "JAM", "JAM_B", "DIVERT")
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
H_CODES = {"H": "H", "H-noB": "Hb", "H-nospread": "Hs", "H-brief": "Hl", "H3": "H3", "H4": "H4", "H5": "H5"}
# H numbers. G2 tuned values (G2_RESULTS.md section 2); every one can be overridden from the environment (g2_tune.py).
# H-brief ("Hl") keeps the brief's literal numbers, so the tuning can be compared against the brief as written.
#   BRULE: the corp's post-response B rule. "typed" = owned Sites before the first sentry of the route's type (brief
#     literal: the corp sees through types and dodges every block); "any" = before the first sentry of any type (the
#     corp sees sentries, not their types); "greed" = all owned Sites on the route (sentries ignored).
#   KNOWN_ROUTE: chance a known beam is a route to HOME (else a street). SPREAD_MIN: Sites lost since the last raid
#   for the spread. DOSE_EVERY: a DOSE card every Nth netrun. CLEAN: price to clean an INFECTED card between raids.
#   PATCH: PATCH HOME price (+1 pip). HOME: HOME pips. ESCALATE: "" or "N:K" (from raid N, K extra known beams).
#   MAX_PLACED: sentries at PLAN (probe only). DOWN_RISK: planner value per DOWN Site (INFECTED at DECAY unless repaired).
# G3 keys (G3 round of docs/handoff/raid_integration/G2_SIM.md; all off for the G2 variants so they reproduce G2):
#   PURGE_MAX: a PURGE is a raid closed with at most this many INFECTED cards while the 3 Exploits are live (G2 0).
#   DOSE_PURGE: 1 = spending 2 DOSE cards at one DECAY (with the 3 Exploits live after the raid) is also a PURGE.
#   DOSES_PER_DECAY: DOSE cards that can be spent at one DECAY (G2 1).
#   EARLY_RAIDS / EARLY_ROUTE: the first N raids draw known route beams at this chance (then KNOWN_ROUTE).
#   SAC_GAP: SACRIFICE allowed only if the last one was at least SAC_GAP raids ago (1 = always; 2 = once per 2 raids).
#   DISCARD: 1 = one INFECTED card drawn in a raid hand may be discarded from the deck for +DISCARD_HEAT Heat.
#   AUTO_DOSE: 1 = DOSE cards are spent at DECAY automatically, for every player (no decision).
#   START_HP: HOME pips at the start (0 = HOME, the maximum).
_H_G3_OFF = {"PURGE_MAX": 0, "DOSE_PURGE": 0, "DOSES_PER_DECAY": 1, "EARLY_RAIDS": 0, "EARLY_ROUTE": 0.0,
             "SAC_GAP": 1, "DISCARD": 0, "DISCARD_HEAT": 2, "AUTO_DOSE": 0, "START_HP": 0}
H_TUNED = {"BRULE": "any", "KNOWN_ROUTE": 0.1, "SPREAD_MIN": 2, "DOSE_EVERY": 2, "CLEAN": 2, "PATCH": 8,
           "HOME": HOME_HP, "ESCALATE": "", "MAX_PLACED": MAX_PLACED, "DOWN_RISK": 2.0, **_H_G3_OFF}
H_BRIEF = {"BRULE": "typed", "KNOWN_ROUTE": 0.5, "SPREAD_MIN": 1, "DOSE_EVERY": DOSE_EVERY, "CLEAN": CLEAN_PRICE,
           "PATCH": PATCH_PRICE, "HOME": HOME_HP, "ESCALATE": "", "MAX_PLACED": MAX_PLACED, "DOWN_RISK": 2.0,
           **_H_G3_OFF}
# H3 (G3): G2's tuned H plus the blind critic's four fixes; values tuned in G3 (G3_RESULTS.md section 2).
H3 = dict(H_TUNED, PURGE_MAX=1, DOSE_PURGE=1, DOSES_PER_DECAY=2, EARLY_RAIDS=3, EARLY_ROUTE=0.6, SAC_GAP=2,
          DISCARD=1, AUTO_DOSE=1)


def _env_over(d: dict, prefix: str) -> None:
    for _k, _v in list(d.items()):
        _e = os.environ.get(prefix + _k)
        if _e is not None:
            d[_k] = type(_v)(_e) if not isinstance(_v, str) else _e


# H4 (G4_PHASE1.md): H3's raid with the real game's numbers (g4_real.REAL, read from content/ at import) and the
# designer's 2026-10-25 rulings: no PURGE (win = a successful Genome Core breach), INFECTED cards move the netrun Bloom
# front (R-D), CITY LOST (R-E), DECAY (R-H). Keys below are the H4-only numbers; [R] = real content, [A] = assumed,
# [T] = tuned in G4. Every one can be overridden as H4_<KEY>.
#   HOME [R] home integrity; PATCH_PT [R] Schematics per HOME point; INSTALL [R] node_base_cost; REPAIR_RATIO [R].
#   START_SCHEM [R]; START_HEAT 0 [R] (CampaignState.heat); CYCLE_SCHEM [A] Schematics from unspent Cycles per netrun;
#   ELITE_RUN [A] elites fought per netrun (x elite_heat); CLEAN [A/T] Schematics to clean one INFECTED card at HQ.
#   P_COMBAT [A] netrun death chance outside the Bloom; INF_STEP_PCT [T] Bloom steps per INFECTED card in % (100 = R-D
#   literal: one entry step per card). BREACH_BASE [A] final-run success with 0 INFECTED (BAL-05: reference boss win
#   52 %); BREACH_K [A] success lost per INFECTED card; BREACH_MIN [A] floor. BREACH_RETRY: failed breaches the campaign
#   survives (each a death, then the campaign goes on); 0 = it ends at the first breach (G4_PHASE1), 99 = the real game.
#   BREACH_INF [T] the skilled player breaches once INFECTED <= this (or BREACH_WAIT netruns after ready, or near the
#   cap); the careless player breaches as soon as it can. CAP: netruns before the campaign stops.
#   RAID_EVERY [T] netruns per cadence raid; HEAT_RAIDS 1 = the first crossing of 25/50/75/100 also queues a raid (GDD
#   4.4). BEAM_HEAT / HAND_HEAT [R thresholds]: Heat at which an extra known beam / an extra hand card is added.
# G4 tuning (G4_RESULTS.md section 3): KNOWN_ROUTE 0.1 -> 0.0, DISCARD 1 -> 0, DOSE_EVERY 2 -> 4, beams at 75 / 100.
H4 = dict(H3, PURGE_MAX=-1, DOSE_PURGE=0, HOME=50, PATCH_PT=1.0, INSTALL=20, REPAIR_RATIO=0.5, START_SCHEM=20,
          START_HEAT=0, CYCLE_SCHEM=4, ELITE_RUN=2, CLEAN=10, P_COMBAT=0.03, INF_STEP_PCT=100, BREACH_BASE=0.52,
          BREACH_K=0.04, BREACH_MIN=0.05, BREACH_RETRY=0, BREACH_INF=1, BREACH_WAIT=4, CAP=30, RAID_EVERY=2,
          HEAT_RAIDS=1, BEAM_HEAT="75,100", HAND_HEAT="25,50,75", DOSE_EVERY=4, KNOWN_ROUTE=0.0, DISCARD=0)


def _h4_real() -> None:
    """Fill H4's [R] keys from the content files (g4_real), before the environment overrides."""
    import g4_real
    r = g4_real.REAL
    H4.update(HOME=r["home_integrity"], PATCH_PT=r["home_repair_cost_per_point"], INSTALL=r["node_base_cost"],
              REPAIR_RATIO=r["node_repair_ratio"], START_SCHEM=r["starting_schematics"])
    H4["_REAL"] = r


_h4_real()
# H5 (designer 2026-10-25, DECISIONS "Phase 1 rule changes"): H4 plus
#   HOME_INF: 1 = a HOME hit adds one INFECTED card tied to HOME (not a lost Site: no spread count);
#   BREACH_RETRY 1 + BREACH_LOSE 1: one retry; the second failure spends the held Exploits (the corp patches them):
#     they are re-taken by a netrun on each Exploit Site, after which the breach has its two attempts again;
#   DIVERT: 1 = the RESPONSE may spend a SHIFT card (+SPOOF_HEAT) to bend one known beam onto another path of its pool
#     that starts or ends at the same Site; the known beams fire after the RESPONSE (they are shown at PLAN);
#   Heat-threshold raids reset the cadence counter (already so in H4: any raid resets it).
# G4 H5 tuning (G4_RESULTS.md section 6): raid cadence 3; raids 1-4 always draw known routes to HOME, none after.
H5 = dict(H4, HOME_INF=1, BREACH_RETRY=1, BREACH_LOSE=1, DIVERT=1, PENDING_TERRITORY=1, RAID_EVERY=3, EARLY_RAIDS=4,
          EARLY_ROUTE=1.0, KNOWN_ROUTE=0.0)
H4.update(HOME_INF=0, BREACH_LOSE=0, DIVERT=0, PENDING_TERRITORY=0)
HFAM = ("H4", "H5")
_env_over(H_TUNED, "H_")
_env_over(H3, "H3_")
_env_over(H4, "H4_")
_env_over(H5, "H5_")
HX = H4         # the H4-family numbers of the campaign being played (set_family sets it)


def hp(c: str, key: str):
    """An H number for concept code c (H-brief: the brief's values; H3: G3 values; H4: G4; the rest: G2 tuned)."""
    return (H_BRIEF if c == "Hl" else H3 if c == "H3" else H4 if c == "H4" else H5 if c == "H5" else H_TUNED)[key]

VARIANTS = ("A-open", "A-all", "A-target", "B-wards", "C-open", "C-all", "C-target",
            "C-open-tongue", "C-all-tongue", "C-target-tongue", "D-lattice", "H", "H-noB", "H-nospread", "H-brief",
            "H3", "H4", "H5")
POLICIES = ("greedy", "keys", "random")
PLAYERS = ("greedy", "naive")
OUT = r"D:/rc_tmp/raid_design_lab/g1/sweep_g1.json"

_GEO = {}


def geo_for(variant: str):
    g = _GEO.get(variant)
    if g is None:
        if variant in H_CODES:
            hc = H_CODES[variant]
            g = G.GraphGeo("P-target", "street", hp(hc, "KNOWN_ROUTE"),
                           (hp(hc, "EARLY_RAIDS"), hp(hc, "EARLY_ROUTE")),
                           1 + len(_ints(hp(hc, "BEAM_HEAT"))) if hc in HFAM else 3)
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
                 "wounds_total", "sites_lost", "front_downs", "lost_flag", "last_lost", "inf_n", "purged",
                 "raid_n", "last_sac", "dose_spent", "held", "pending", "deaths", "won", "breaches", "crossed_h",
                 "ready_at", "asset_n", "purge_q", "cools", "bfails")

    def __init__(self):
        self.held = frozenset()     # H4: Exploits extracted (permanent, campaign.exploits)
        self.pending = ()           # H4: Sites cleared but not yet installed (no Schematics for the node)
        self.deaths = 0             # H4: operatives lost (Bloom, combat, failed breach)
        self.won = False            # H4: the Genome Core breach succeeded
        self.breaches = ()          # H4: (netrun, INFECTED at the breach, success chance, success) per attempt
        self.crossed_h = ()         # H4: Heat thresholds already crossed (a raid fires on the first crossing)
        self.ready_at = -1          # H4: netrun the breach became possible
        self.asset_n = 0            # H4: Armory cards dropped by Server Racks
        self.purge_q = False        # H4: Heat 100 crossed for the first time since the last raid (the PURGE raid)
        self.cools = 0              # H4: Heat purchases made (each costs heat_purchase_increment more)
        self.bfails = 0             # H5: failed breaches since the Exploits were last (re-)taken
        self.lost_flag = 0          # H: Sites lost since the last spread check
        self.last_lost = ""         # H: the Site the spread card is tied to
        self.inf_n = 0              # H: monotonic INFECTED card id
        self.raid_n = 0             # H: index of the raid being played (known-beam early chance)
        self.last_sac = -9          # H3: raid index of the last SACRIFICE
        self.dose_spent = 0         # H3: DOSE cards spent at this raid's DECAY
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
    return c in ("H", "Hb", "Hl", "H3", "H4", "H5")


def h_dyn_b(c: str) -> bool:
    """H: the corp picks sealed B after the response by the readable rule (H-noB keeps the generation pick)."""
    return c in ("H", "Hs", "Hl", "H3", "H4", "H5")


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
    if c in HFAM:
        return value_h4(geo, st, mid)
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


# ------------------------------------------------------------------------------------------------ H4 rules
# Planner weights (the planner's value only, never a rule): Schematics units.
H4_SITE_V, H4_HOME_PT, H4_LETHAL, H4_HEAT_W, H4_BAND_W, H4_INF_W = 20.0, 1.5, 60.0, 0.5, 8.0, 14.0
H4_DOSE_V, H4_GHOST_V, H4_DOWN_RISK, H4_EXPLOIT_V, H4_LOST = 10.0, 5.0, 5.0, 25.0, -300.0


def _ints(s: str) -> tuple:
    return tuple(int(x) for x in str(s).split(",") if x != "")


def h4_band(heat: int) -> int:
    """Heat band index COOL 0, NOTICED 1, FLAGGED 2, HUNTED 3, PURGE 4 (GDD 4.3: 25 / 50 / 75 / 100)."""
    r = HX["_REAL"]
    return sum(1 for t in tuple(r["major_heat"]) + (r["purge_heat"],) if heat >= t)


def h4_home_dmg(heat: int, purge: bool = False) -> int:
    """HOME damage of one hit: the raid of the Heat band (claim / 25 / 50 / 75); the PURGE raid's only for the raid the
    first crossing of 100 queued (a one-time event, GDD 4.3); later raids at 100 hit like the 75 raid."""
    t = HX["_REAL"]["home_hit_damage_by_band"]
    return t[4] if purge else t[min(3, h4_band(heat))]


def h4_n_known(heat: int) -> int:
    return 1 + sum(1 for t in _ints(HX["BEAM_HEAT"]) if heat >= t)


def h4_hand(heat: int) -> int:
    return HAND_BASE + sum(1 for t in _ints(HX["HAND_HEAT"]) if heat >= t)


def h4_repair(geo, site: str) -> int:
    return int(HX["INSTALL"] * HX["REPAIR_RATIO"])


def h4_patch_cost(st: "St") -> tuple:
    """(points, Schematics) of patching HOME with every point the bank buys (CampaignRules.repair_home)."""
    missing = HX["HOME"] - st.hp
    per = HX["PATCH_PT"]
    n = min(missing, int(st.bank // max(0.0001, per)))
    return (n, int(math.ceil(n * per))) if n > 0 else (0, 0)


def h4_keys(st: "St") -> int:
    """Bloom key bits for the Exploits held: 1 Virus, 2 Intel, 4 Breach."""
    return (1 if "t2_virus" in st.held else 0) | (2 if "t2_intel" in st.held else 0) | (4 if "t2_breach" in st.held else 0)


_CURVE = None


def h4_catch(tier: int, heat: int, keys: int, n_inf: int) -> float:
    """R-D: the street Bloom's catch chance (data/g4_bloom_curve.json, g4_bloom.py) with the front INF_STEP_PCT % of
    an entry step closer per INFECTED card (linear between whole steps)."""
    global _CURVE
    if _CURVE is None:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "g4_bloom_curve.json")) as f:
            _CURVE = json.load(f)
    row = _CURVE["catch"]["%d:%d:%d" % (min(3, max(1, tier)), h4_band(heat), keys)]
    x = n_inf * HX["INF_STEP_PCT"] / 100.0
    i = int(x)
    if i >= len(row) - 1:
        return row[-1]
    return row[i] + (row[i + 1] - row[i]) * (x - i)


def h4_death_chance(st: "St", tier: int) -> float:
    p = HX["P_COMBAT"]
    return p + (1 - p) * h4_catch(tier, st.heat, h4_keys(st), wound_count(st.deck))


def h4_breach_chance(st: "St") -> float:
    """R-F: the final Genome Core netrun's success, falling with the INFECTED count at the breach."""
    return max(HX["BREACH_MIN"], HX["BREACH_BASE"] - HX["BREACH_K"] * wound_count(st.deck))


def h4_add_heat(st: "St", d: int) -> bool:
    """Heat clamped 0..heat_max. True when a raid threshold (25 / 50 / 75 / 100) is crossed for the first time."""
    r = HX["_REAL"]
    st.heat = max(0, min(r["heat_max"], st.heat + d))
    new = [t for t in tuple(r["major_heat"]) + (r["purge_heat"],) if st.heat >= t and t not in st.crossed_h]
    if new:
        st.crossed_h = tuple(sorted(st.crossed_h + tuple(new)))
        if r["purge_heat"] in new:
            st.purge_q = True
    return bool(new)


def value_h4(geo, st: "St", mid: bool = True) -> float:
    if st.lost or st.hp <= 0:
        return H4_LOST
    s = float(st.bank)
    downs = 0
    for site, v in st.owned.items():
        if v == "OK":
            s += H4_SITE_V
        elif v == "DOWN":
            s += H4_SITE_V - h4_repair(geo, site)
            downs += 1
    s += H4_SITE_V * len(st.pending) * 0.5
    s += H4_EXPLOIT_V * len(st.held)
    s -= H4_HOME_PT * (HX["HOME"] - st.hp)
    if st.hp <= h4_home_dmg(st.heat, st.purge_q):
        s -= H4_LETHAL
    s -= H4_HEAT_W * st.heat + H4_BAND_W * h4_band(st.heat)
    w = wound_count(st.deck)
    s -= H4_INF_W * w
    if mid:
        s += H4_DOSE_V * len(dose_cards(st.deck)) + H4_GHOST_V * st.ghost
        s -= H4_DOWN_RISK * downs
        if st.lost_flag + downs >= HX["SPREAD_MIN"]:
            s -= H4_DOSE_V if dose_cards(st.deck) else H4_INF_W
    return s


def h4_t3_ready(geo, st: "St") -> bool:
    """The breach needs 3 Exploits and a cleared or claimed T3 Site next to the Genome Core (CampaignRules)."""
    if len(st.held) < HX["_REAL"]["min_exploits_for_breach"]:
        return False
    return any(geo.tier[s] == 3 and s not in geo.objective_heat and (v in ("OK", "DOWN")) for s, v in st.owned.items()) \
        or any(geo.tier[s] == 3 and s not in geo.objective_heat for s in st.pending)


def h4_install_pending(st: "St") -> None:
    """Cleared Sites wait at HQ for Schematics: after PATCH / REPAIR / CLEAN, each is installed (node_base_cost) while
    the bank allows, in id order. Until then a cleared Site is territory (claims, breach) but no raid target."""
    left = []
    for s in st.pending:
        if st.bank >= HX["INSTALL"] and st.owned.get(s) != "OK":
            st.bank -= HX["INSTALL"]
            st.owned[s] = "OK"
        else:
            left.append(s)
    st.pending = tuple(left)


def h4_clear(geo, st: "St", site) -> bool:
    """A completed netrun on `site` (None = patrol): rack Heat and Schematics, Exploit, objective Heat, then the claim
    (install now if affordable, else pending). Returns True when a raid threshold was crossed."""
    tier = 1 if site is None else geo.tier[site]
    r = HX["_REAL"]
    d = r["rack_heat_by_tier"][tier - 1] + HX["ELITE_RUN"] * r["elite_heat"]
    st.bank += r["rack_schematics_by_tier"][tier - 1] + HX["CYCLE_SCHEM"]
    if site is not None:
        if site in geo.exploits and site not in st.held:
            st.held = st.held | {site}
            d += r["exploit_heat"]
        if site in geo.objective_heat and site not in st.obj_done:
            st.obj_done = st.obj_done | {site}
            d += geo.objective_heat[site]
        if st.owned.get(site) not in ("OK", "DOWN"):
            st.pending = tuple(sorted(set(st.pending) | {site}))
    return h4_add_heat(st, d)


def netrun_h4(geo, st: "St", site, seed: int, n: int, roll: bool = True) -> bool:
    """One H4 netrun. roll=False: the claim planner's preview (no death, no drop). Returns True to queue a raid."""
    tier = 1 if site is None else geo.tier[site]
    q = False
    if roll and random.Random("death:%d:%d" % (seed, n)).random() < h4_death_chance(st, tier):
        st.deaths += 1
        q = h4_add_heat(st, HX["_REAL"]["death_heat_base"] + tier)
    else:
        q = h4_clear(geo, st, site)
        if roll:
            ar = random.Random("asset:%d:%d" % (seed, n))
            if ar.random() < HX["_REAL"]["asset_drop_chance"]:
                st.deck = tuple(sorted(st.deck + (("a%02d" % st.asset_n, ar.choice(TYPES), "GUARD"),)))
                st.asset_n += 1
    if roll and n % HX["DOSE_EVERY"] == 0:
        add_dose_card(st)
    check_loss(geo, "H4", st)
    return q and bool(HX["HEAT_RAIDS"])


def h4_territory(st: "St") -> dict:
    """Owned Sites for claim adjacency. H5 (PENDING_TERRITORY): a cleared, not yet installed Site is territory too
    (CampaignRules.touches_territory: claimed or cleared). H4 kept the owned Sites only (an oracle gap found in G4-H5;
    left as it was so H4 reproduces)."""
    if not HX["PENDING_TERRITORY"]:
        return st.owned
    t = dict(st.owned)
    for s in st.pending:
        if t.get(s) not in ("OK", "DOWN"):
            t[s] = "OK"
    return t


def choose_claim_h4(geo, st: "St", policy: str, rng: random.Random, seed: int, n: int):
    opts = [s for s in geo.claimable(h4_territory(st)) if s not in st.pending]
    if HX["BREACH_LOSE"]:       # H5: an Exploit Site still held live can be run again to re-take its Exploit
        opts += [s for s in sorted(geo.exploits) if st.owned.get(s) in ("OK", "DOWN") and s not in st.held]
    if not opts:
        return None
    if policy == "random":
        return rng.choice(opts)
    if len(st.held) >= 3 and not h4_t3_ready(geo, st):
        t3 = {s for s in geo.sites if geo.tier[s] == 3 and s not in geo.objective_heat}
        return min(opts, key=lambda s: (geo.exploit_distance(s, t3), s))
    if policy == "keys":
        targets = {s for s in geo.exploits if s not in st.held}
        if targets:
            return min(opts, key=lambda s: (geo.exploit_distance(s, targets), -geo.value(s), s))
    best = None
    for s in opts:
        s2 = st.copy()
        netrun_h4(geo, s2, s, seed, n, roll=False)
        v = value_h4(geo, s2)
        if best is None or v > best[0] + EPS:
            best = (v, s)
    return best[1]


def h4_wants_breach(geo, st: "St", greedy: bool, n: int) -> bool:
    if not h4_t3_ready(geo, st):
        return False
    if not greedy:
        return True
    return (wound_count(st.deck) <= HX["BREACH_INF"] or n - st.ready_at >= HX["BREACH_WAIT"]
            or HX["CAP"] - n <= 2)


def set_family(c: str) -> None:
    """Select the H4-family numbers (HX) for variant code c ("H4" or "H5")."""
    global HX
    HX = H5 if c == "H5" else H4


def campaign_h4(policy: str, player: str, seed: int, rec: dict, c: str = "H4") -> "St":
    set_family(c)
    geo = geo_for(c)
    st = St()
    st.hp, st.bank, st.heat = HX["HOME"], HX["START_SCHEM"], HX["START_HEAT"]
    greedy = player == "greedy"
    rng = random.Random("claim:%d" % seed)
    since = 0
    n_raids = 0
    rec["netruns"] = 0
    for n in range(1, HX["CAP"] + 1):
        rec["netruns"] = n
        if st.ready_at < 0 and h4_t3_ready(geo, st):
            st.ready_at = n
        gl = rec.get("golden")
        gb = state_json(st) if gl is not None else None
        if h4_wants_breach(geo, st, greedy, n):
            p = h4_breach_chance(st)
            roll = random.Random("breach:%d:%d" % (seed, n)).random()
            ok = roll < p
            if gl is not None:
                gl.append({"phase": "BREACH", "netrun": n, "before": gb, "infected": wound_count(st.deck), "p": p,
                           "roll": roll, "success": ok})
            st.breaches = st.breaches + ((n, wound_count(st.deck), round(p, 4), ok),)
            q = False
            go_on = False
            if ok:
                st.won = True
            else:
                st.deaths += 1      # the breach operative dies: death Heat at tier 4
                q = h4_add_heat(st, HX["_REAL"]["death_heat_base"] + 4)
                st.bfails += 1
                if HX["BREACH_LOSE"]:
                    go_on = True
                    if st.bfails > HX["BREACH_RETRY"]:     # H5: the Exploits are spent; re-take them
                        st.held = frozenset()
                        st.bfails = 0
                        st.ready_at = -1
                else:
                    go_on = len(st.breaches) <= HX["BREACH_RETRY"]
                if go_on and n % HX["DOSE_EVERY"] == 0:
                    add_dose_card(st)
            if gl is not None:
                gl[-1]["after"] = state_json(st)
            if not go_on:
                break
        else:
            site = choose_claim_h4(geo, st, policy, rng, seed, n)
            if gl is not None:
                tier = 1 if site is None else geo.tier[site]
                gl.append({"phase": "NETRUN", "netrun": n, "before": gb, "options": [s for s in geo.claimable(h4_territory(st))
                           if s not in st.pending], "site": site, "death_p": h4_death_chance(st, tier),
                           "death_roll": random.Random("death:%d:%d" % (seed, n)).random()})
            d0 = st.deaths
            q = netrun_h4(geo, st, site, seed, n)
            if gl is not None:
                gl[-1].update(died=st.deaths > d0, raid_queued=q, after=state_json(st))
        if st.lost:
            break
        since += 1
        if q or since >= HX["RAID_EVERY"]:
            st = raid(geo, c, st, seed, n_raids, greedy, rec)
            n_raids += 1
            since = 0
            if st.lost:
                break
    rec["n_raids"] = n_raids
    return st


def line_json(ln) -> dict:
    return {"kind": ln.kind, "cells": list(ln.cells), "type": ln.type, "home": ln.home}


def draw_json(d, n_used: int) -> dict:
    return {"known": [line_json(x) for x in d.known], "known_fired": n_used, "cands": [line_json(x) for x in d.cands],
            "real_a": d.real, "real_b_drawn": d.real_b, "hunter_type": d.hunter_type,
            "hunters": [line_json(x) for x in d.hunters] if d.hunters is not None else None, "hunter_real": d.hunt_real,
            "n_paths": d.n_paths}


def state_json(st: "St") -> dict:
    """The golden's state form (G4): every field the H4 rules read or write, sorted, JSON-plain."""
    d = {"heat": st.heat, "bank": st.bank, "home": st.hp, "owned": [[s, v] for s, v in sorted(st.owned.items())],
            "deck": [list(x) for x in st.deck], "ghost": st.ghost, "held": sorted(st.held), "pending": list(st.pending),
            "obj_done": sorted(st.obj_done), "deaths": st.deaths, "lost": st.lost, "won": st.won,
            "crossed_heat": list(st.crossed_h), "purge_queued": st.purge_q, "lost_since_raid": st.lost_flag,
            "last_lost": st.last_lost, "inf_n": st.inf_n, "dose_n": st.dose_n, "asset_n": st.asset_n,
            "last_sac": st.last_sac, "cools": st.cools, "infected_total": st.wounds_total, "sites_lost": st.sites_lost,
            "dose_spent": st.dose_spent}
    if HX["BREACH_LOSE"]:
        d["breach_fails"] = st.bfails   # H5: failed breaches since the Exploits were (re-)taken
    return d


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
        st.dose_spent = 0
        spender = greedy or hp(c, "AUTO_DOSE")
        for _ in range(hp(c, "DOSES_PER_DECAY")):
            dc = dose_cards(st.deck)
            if not (spender and dc and (spread or wound_count(st.deck) > 0)):
                break
            remove_card(st, dc[0][0])        # a DOSE: block the spread, else remove 1 INFECTED
            st.dose_spent += 1
            if spread:
                spread = False
            else:
                remove_card(st, max(x for x in st.deck if x[2] == "WOUND")[0])
            if log is not None:
                log["decay_dose"] = log.get("decay_dose", 0) + 1
        if spread:
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
                 "quar", "taken", "front", "infected", "late", "dose_used", "bpick", "lean", "jam_b", "home_dmg",
                 "trace", "beam", "n_known", "divert")

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
        o.home_dmg = self.home_dmg
        o.trace = None if self.trace is None else list(self.trace)
        o.beam = self.beam
        o.n_known = self.n_known
        o.divert = self.divert
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
    sw.home_dmg = 1             # HOME integrity one hit removes (H4: by Heat band)
    sw.trace = None             # golden: [beam, site_or_HOME, "block"|"hit"|"home"|"shield"] when a list
    sw.beam = ""
    sw.n_known = 0              # H5: known beams that fire after the RESPONSE
    sw.divert = None            # H5: (known index, cells) of a DIVERT
    return sw


def scan(geo, sw: Sweep, ln, ctype: dict) -> None:
    cs = geo.cell_sites
    for cell in ln.cells:
        if cell == sw.ghost:
            continue
        j = sw.sent.get(cell)
        if j is not None and ctype[j] == ln.type:
            sw.touches += 1
            if sw.trace is not None:
                sw.trace.append([sw.beam, cell, "block"])
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
                if sw.trace is not None:
                    sw.trace.append([sw.beam, s, "hit"])
                break
    if ln.home and sw.ghost != G.HOME and not sw.home_hit:
        sw.touches += 1
        if sw.shield:
            if sw.trace is not None:
                sw.trace.append([sw.beam, G.HOME, "shield"])
            return
        sw.hp = max(0, sw.hp - sw.home_dmg)
        if sw.trace is not None:
            sw.trace.append([sw.beam, G.HOME, "home"])
        sw.home_hit = True
        sw.home_ward = ln.ward


class Ctx:
    """One raid: geometry, concept, draw, hand, card types."""
    __slots__ = ("geo", "c", "draw", "hand", "cards", "ctype", "rel", "seed", "raid", "sac_ok", "trace", "nbrs")


def make_ctx(geo, c: str, st: St, seed: int, raid: int) -> Ctx:
    ctx = Ctx()
    ctx.geo, ctx.c, ctx.seed, ctx.raid = geo, c, seed, raid
    ctx.trace = False
    ctx.nbrs = None
    ctx.sac_ok = not is_h(c) or raid - st.last_sac >= hp(c, "SAC_GAP")
    ctx.draw = geo.draw(st, random.Random("raid:%d:%d" % (seed, raid)))
    ids = sorted(x[0] for x in st.deck)
    random.Random("hand:%d:%d" % (seed, raid)).shuffle(ids)
    ctx.hand = ids[:(h4_hand(st.heat) if c in HFAM else hand_size(st.heat))]
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
    if c == "H5" and HX["DIVERT"]:
        ctx.nbrs = divert_neighbors(geo, ctx.draw, st)
    return ctx


def divert_neighbors(geo, d, st: St) -> list:
    """H5 DIVERT: per known beam, the other paths of its pool (the route pool for a route, this raid's street pool for
    a street) that start or end at the same Site, in pool order."""
    spool = geo.street_pool([ln.cells for ln in d.cands], st.owned)
    out = []
    for ln in d.known:
        pool = geo._all_paths if ln.kind == "ROUTE" else spool
        out.append([p for p in pool if p != ln.cells and (p[0] == ln.cells[0] or p[-1] == ln.cells[-1])])
    return out


def fire_known(ctx: Ctx, sw: Sweep) -> None:
    """H5: the known beams fire after the RESPONSE (a DIVERT replaces one beam's cells)."""
    for i in range(sw.n_known):
        ln = ctx.draw.known[i]
        if sw.divert is not None and sw.divert[0] == i:
            ln = G.Line(ln.kind, tuple(sw.divert[1]), ln.type, ln.home)
        sw.beam = "known%d" % i
        scan(ctx.geo, sw, ln, ctx.ctype)


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
    if ctx.c in HFAM:
        return h4_n_known(heat)
    e = escalation(ctx)
    return 1 + int(heat >= EXTRA_AT or e >= 1) + int(heat >= STRONG_AT or e >= 2)


def launch(ctx: Ctx, st: St, place):
    heat = st.heat + (GHOST_HEAT if place[1] is not None else 0)
    sw = new_sweep(st, place)
    if ctx.c in HFAM:
        sw.home_dmg = h4_home_dmg(st.heat, st.purge_q)
    if getattr(ctx, "trace", False):
        sw.trace = []
    if ctx.c == "H5":
        sw.n_known = n_known(ctx, heat)     # they fire after the RESPONSE (fire_known)
    else:
        for i in range(n_known(ctx, heat)):
            sw.beam = "known%d" % i
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
    if sw.ghost != G.HOME and not sw.home_hit and ctx.sac_ok:
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
    if ctx.nbrs is not None and _has(rhand, "SHIFT"):
        for i in range(sw.n_known):
            for p in ctx.nbrs[i]:
                out.append(("DIVERT", i, p))
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
    elif k == "DIVERT":
        sw.divert = (r[1], tuple(r[2]))


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
    if c in HFAM:
        evaded = False
        # D27 (real): a clean defense (HOME not lower, no Site newly DOWN or TAKEN) gains clean_defense_heat and pays
        # the raid's Schematics (raid_schematics_by_tier by the Heat band's raid: claim/25 -> 8, 50 -> 12, 75 -> 18,
        # 100 -> 25); any damage gains neither
        if sw.hp >= st.hp and not any(v != st.owned.get(s2) for s2, v in sw.owned.items()):
            r = HX["_REAL"]
            heat += r["clean_defense_heat"]
            ns.bank += r["raid_schematics_by_tier"][max(0, h4_band(st.heat) - 1)]
    elif evaded:
        heat -= EVADE_HEAT
    if resp[0] in CARD_RESPONSES:
        heat += SPOOF_HEAT
    ns.heat = max(0, heat) if c not in HFAM else max(0, min(HX["_REAL"]["heat_max"], heat))
    if place[1] is not None:
        ns.ghost -= 1
    ns.sites_lost += sw.taken
    if is_h(c):
        add_infected(ns, sorted(s for s, v in sw.owned.items() if v == "TAKEN" and st.owned.get(s) != "TAKEN"))
        if c == "H5" and sw.home_hit and HX["HOME_INF"]:
            add_infected(ns, ["HOME"], loss=False)      # H5: a HOME hit infects the Cell
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
    if is_h(c) and not ns.lost and exploits_live(geo, ns) >= 3 and (
            wound_count(ns.deck) <= hp(c, "PURGE_MAX") or hp(c, "DOSE_PURGE") and ns.dose_spent >= 2):
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
    if ctx.c == "H5":
        fire_known(ctx, sw)
    sw.beam = "sealed_a"
    scan(ctx.geo, sw, d.cands[k], ctx.ctype)
    b = [x for x in range(3) if x != k][bi]
    sw.beam = "sealed_b"
    scan(ctx.geo, sw, d.cands[b], ctx.ctype)
    do_late(ctx, sw, late, rhand)
    if resp[0] != "JAM":
        sw.beam = "hunter"
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
        swk = sw1
        if c == "H5":
            swk = sw1.copy()
            fire_known(ctx, swk)
        for k in range(3):
            sw2 = swk.copy()
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


def between_h4(geo, st: St, opt) -> St:
    """H4 HQ step: PATCH HOME (every point the bank buys, 1 Schematic each), REPAIR one DOWN Site (half the install),
    CLEAN one INFECTED card (CLEAN Schematics). Healthy cards come from Server Rack drops, so there is no build."""
    rep, build, _dose, patch = opt
    ns = st.copy()
    if patch:
        n, cost = h4_patch_cost(ns)
        if n > 0:
            ns.bank -= cost
            ns.hp += n
    if rep is not None and ns.owned.get(rep) == "DOWN" and ns.bank >= h4_repair(geo, rep):
        ns.bank -= h4_repair(geo, rep)
        ns.owned[rep] = "OK"
    if build == "COOL" and ns.bank >= h4_cool_price(ns):
        ns.bank -= h4_cool_price(ns)
        ns.cools += 1
        h4_add_heat(ns, -HX["_REAL"]["heat_purchase_amount"])
    if build == "CLEAN" and ns.bank >= HX["CLEAN"]:
        ws = [x for x in ns.deck if x[2] == "WOUND"]
        if ws:
            ns.bank -= HX["CLEAN"]
            remove_card(ns, max(ws)[0])
    h4_install_pending(ns)      # cleared Sites are installed with what is left (id order)
    return ns


def h4_cool_price(st: St) -> int:
    """The HQ Heat purchase (GDD 11.4): -heat_purchase_amount Heat for heat_purchase_cost, +increment per purchase."""
    r = HX["_REAL"]
    return r["heat_purchase_cost"] + r["heat_purchase_increment"] * st.cools


def between_options_h4(geo, st: St) -> list:
    downs = sorted(s for s, v in st.owned.items() if v == "DOWN")
    builds = [None] + (["CLEAN"] if wound_count(st.deck) else []) + (["COOL"] if st.heat > 0 else [])
    patches = [False, True] if st.hp < HX["HOME"] else [False]
    out = []
    for r in [None] + downs:
        rc = h4_repair(geo, r) if r else 0
        for b in builds:
            bc = HX["CLEAN"] if b == "CLEAN" else h4_cool_price(st) if b == "COOL" else 0
            for pt in patches:
                if rc + bc + (1 if pt else 0) <= st.bank:
                    out.append((r, b, None, pt))
    return out


def between(geo, c: str, st: St, opt) -> St:
    if c in HFAM:
        return between_h4(geo, st, opt)
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
    if c in HFAM:
        return between_options_h4(geo, st)
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
    if c in HFAM:
        patch = st.hp < HX["HOME"] and st.bank >= HX["PATCH_PT"]
        bank = st.bank - (h4_patch_cost(st)[1] if patch else 0)
        downs = sorted(s for s, v in st.owned.items() if v == "DOWN")
        rep = None
        for s in downs:     # the most valuable affordable DOWN Site: highest tier, then id
            if bank >= h4_repair(geo, s) and (rep is None or geo.tier[s] > geo.tier[rep]):
                rep = s
        return (rep, None, None, patch)
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
    gl = rec.get("golden")          # solace_raid_golden.py: a list to append this raid's phases to
    g = None
    if gl is not None:
        g = {"phase": "RAID", "raid": idx, "before": state_json(st)}
        gl.append(g)
    if idx > 0:
        decay(geo, c, st, greedy, rec)
        if g is not None:
            g["after_decay"] = state_json(st)
        if st.lost:
            return st
    st.raid_n = idx
    ctx = make_ctx(geo, c, st, seed, idx)
    discarded = False
    if is_h(c) and hp(c, "DISCARD"):
        bad = sorted(j for j in ctx.hand if ctx.cards[j][1] == "WOUND")
        if bad:
            s2 = st.copy()
            remove_card(s2, bad[0])
            s2.heat += hp(c, "DISCARD_HEAT")
            if not greedy or value(geo, c, s2) > value(geo, c, st) + EPS:
                st = s2
                ctx.hand = [j for j in ctx.hand if j != bad[0]]
                discarded = True
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
    ctx.trace = g is not None
    ns, tr, sw = play_one(ctx, st, place, resp, k, bi, late, h)
    ctx.trace = False
    if g is not None:
        g.update(draw=draw_json(d, n_known(ctx, st.heat + (GHOST_HEAT if place[1] is not None else 0))),
                 hand=list(ctx.hand), discard=discarded, after_discard=state_json(st),
                 place={"sentries": [[cell, j] for cell, j in sorted(place[0].items())], "ghost": place[1]},
                 response=list(resp), late=late, lean=sw.lean, b_pick=sw.bpick, jam_b=sw.jam_b,
                 home_dmg=sw.home_dmg, trace=sw.trace, tier=tr, after_raid=state_json(ns))
        if ctx.nbrs is not None:     # H5: the DIVERT targets per known beam (pool order)
            g.update(divert_neighbors=[[list(p) for p in x] for x in ctx.nbrs], divert=sw.divert)
    b_flip = None
    if h_dyn_b(c):
        b_flip = sw.bpick != sw.lean
        bi = sw.bpick
        b = [x for x in range(3) if x != k][bi]
    # metrics
    hold = [play_one(ctx, st, place, ("HOLD",), kk, bb, None, hh)
            for kk in range(3) for bb in range(2) for hh in range(2)]
    hold_tiers = [x[1] for x in hold]
    if g is not None:
        g["forecast_hold"] = hold_tiers     # HOLD tiers for A 0..2 x B slot 0..1 x hunter 0..1 (corp B rule applied)
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
        "inf_rows": inf_rows if is_h(c) else None, "inf_fc": inf_fc if is_h(c) else None,
        "discard": discarded, "sac_blocked": not ctx.sac_ok})
    if c in HFAM:
        rec["raids"][-1].update(hp0=st.hp, hp1=ns.hp, heat0=st.heat, bank0=st.bank, band=h4_band(st.heat), inf0=wound_count(st.deck))
        ns.purge_q = False      # the PURGE raid has fired
    if resp[0] == "SACRIFICE":
        ns.last_sac = idx
    if ns.lost:
        return ns
    opt = greedy_between(geo, c, ns) if greedy else naive_between(geo, c, ns)
    rec["between"].append("%s|%s|%s|%s" % (opt[0] is not None, opt[1], opt[2], opt[3]))
    out = between(geo, c, ns, opt)
    if g is not None:
        g.update(between={"repair": opt[0], "build": opt[1], "patch": opt[3]},
                 between_options=[[o[0], o[1], o[3]] for o in between_options(geo, c, ns)], after=state_json(out))
    return out


def campaign(variant: str, policy: str, player: str, seed: int) -> dict:
    geo = geo_for(variant)
    c = concept_of(variant)
    if c in HFAM:
        rec = {"raids": [], "between": []}
        st = campaign_h4(policy, player, seed, rec, c)
        b0 = st.breaches[0] if st.breaches else None
        return {"lost": st.lost, "win": st.won, "hold3": len(st.held) >= 3, "purged": False,
                "spread": rec.get("spread", 0), "netruns": rec["netruns"], "raids": rec["n_raids"],
                "wounds": st.wounds_total, "sites_lost": st.sites_lost, "timer": timer_pct(c, st), "front_downs": 0,
                "exploits": len(st.held), "hp": st.hp, "heat": st.heat, "rec": rec,
                "decay_dose": rec.get("decay_dose", 0), "deaths": st.deaths, "breaches": [list(b) for b in st.breaches],
                "inf_first_breach": b0[1] if b0 else None, "p_first_breach": b0[2] if b0 else None,
                "inf_end": wound_count(st.deck), "capped": not st.lost and not st.won and not st.breaches,
                "breach_failed": not st.lost and not st.won and bool(st.breaches),
                "bank": st.bank}
    st = St()
    if is_h(c):
        st.hp = hp(c, "START_HP") or hp(c, "HOME")
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
        "sac_rate": round(sum(1 for r in raids if r["resp"] == "SACRIFICE") / nr, 3),
        "discard_rate": round(sum(1 for r in raids if r.get("discard")) / nr, 3),
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
        **(_h4_extra(rows) if rows and "deaths" in rows[0] else {}),
    }


def _h4_extra(rows: list) -> dict:
    """G4 metrics: deaths, breaches, the INFECTED count at the first breach and its success chance, campaign length."""
    n = len(rows)
    att = [b for x in rows for b in x["breaches"]]
    first = [x["inf_first_breach"] for x in rows if x["inf_first_breach"] is not None]
    hist = {}
    for v in first:
        k = str(min(v, 8)) if v < 8 else "8+"
        hist[k] = hist.get(k, 0) + 1
    by_inf = {}
    for b in att:
        k = str(min(b[1], 6)) if b[1] < 6 else "6+"
        by_inf.setdefault(k, []).append(b[3])
    nets = sorted(x["netruns"] for x in rows)
    return {
        "deaths": round(stats.mean(x["deaths"] for x in rows), 2),
        "death_per_netrun": round(sum(x["deaths"] for x in rows) / max(1, sum(x["netruns"] for x in rows)), 3),
        "breach_reached": round(sum(1 for x in rows if x["breaches"]) / n, 3),
        "breach_attempts": round(len(att) / n, 2),
        "breach_success": round(sum(1 for b in att if b[3]) / max(1, len(att)), 3),
        "first_breach_p": round(stats.mean(x["p_first_breach"] for x in rows if x["p_first_breach"] is not None), 3)
        if first else None,
        "inf_at_first_breach_mean": round(stats.mean(first), 2) if first else None,
        "inf_at_first_breach_hist": {k: round(v / max(1, len(first)), 3) for k, v in sorted(hist.items())},
        "breach_success_by_inf": {k: [round(sum(v) / len(v), 3), len(v)] for k, v in sorted(by_inf.items())},
        "capped": round(sum(1 for x in rows if x["capped"]) / n, 3),
        "breach_failed_end": round(sum(1 for x in rows if x["breach_failed"]) / n, 3),
        "netruns_median": stats.median(nets),
        "netruns_median_won": stats.median([x["netruns"] for x in rows if x["win"]]) if any(x["win"] for x in rows)
        else None,
        "inf_end": round(stats.mean(x["inf_end"] for x in rows), 2),
        "bank_end": round(stats.mean(x["bank"] for x in rows), 1),
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


TABLE_COLS = ("loss", "breached", "city_lost", "win", "breach_reached", "breach_success", "inf_at_first_breach_mean",
              "deaths", "death_per_netrun", "capped", "netruns_median", "hold3", "purge", "b_flip_rate", "infected_per_campaign", "spread",
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
