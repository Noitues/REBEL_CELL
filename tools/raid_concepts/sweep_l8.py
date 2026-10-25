"""Lab round 8 (L8) rules oracle: the city raid (SPEC docs/handoff/raid_lab_l8/SPEC.md, designer 2026-10-23).

Rule changes applied in place:
- L9 (docs/handoff/raid_lab_l8/L9_CHANGES.md): DECAY and SENTRY_PRICE 3.
- L10 (docs/handoff/raid_lab_l8/L10_CHANGES.md): new SUMMARY metrics (its POOL_START is replaced by the L14 deck).
- L11 (docs/handoff/raid_lab_l8/L11_CHANGES.md): MAX_PLACED 2, the DEPLOY response, a lost district keeps its card,
  safe_next, and new SUMMARY metrics.
- L13 (docs/handoff/raid_lab_l8/L13_RULES.md):
  - R2: the hunter street is a sealed unknown (hunter_cands, hunter_real).
  - R3: the SACRIFICE response.
  - R4: Heat bands in the score, and HOME_LOSS_COST 15.
  - R5: intensity perks (NORMAL: free repair; HOT: two captures next raid). L13b: HOT income x0.5.
- L14 (docs/handoff/raid_lab_l8/L14_RULES.md):
  - R9: a dummy run deck feeds the raid. Cards (id, type, verb) with verb GUARD / SHIFT / JAM / WOUND replace the
    sentry pool and the spoof charges. A HAND is drawn every raid; sentries are hand cards; REDEPLOY needs a SHIFT
    card, DEPLOY a card of the type, JAM a JAM card. Every cell that becomes TAKEN adds a WOUND card (-5 each in
    the score). BETWEEN can build a GUARD card or CLEAN a wound.
  - R1: two sealed beams per raid: A (`real`) and B (`real_b`, one of the two other routes).
  - R13: hand size 4, +1 at Heat >= 50, +1 at Heat >= 75.
  - R14: best_response is hidden in the lab; buy_hint sells it for +3 Heat. The planners never buy it.

The map
- A 4 x 3 grid of districts between our HQ (HOME, off-grid at x = -1) and the corp HQ (off-grid at x = 4).
- Rows y = 0..2 are the three ROUTES (north, mid, south). Columns x = 0..3 are the STREETS.
- Each cell has a value v in {4, 6, 8, 10, 12}. 3 cells with x >= 1 carry an EXPLOIT.
- Ownership per cell: NEUTRAL (absent from `owned`), or owned with a status OK / DOWN / TAKEN.
  TAKEN is corp ground for the rest of the leg.
- At leg start we own 2 seeded x = 0 cells (OK).

The deck (R9)
- START_DECK: s0 D GUARD, s1 D GUARD, s2 N GUARD, s3 N GUARD, s4 E GUARD, s5 D SHIFT, s6 E SHIFT, s7 N JAM.
- The deck persists across the leg (sorted by id as strings); no card is ever consumed.
- WOUND ("w<k>", "-", "WOUND"), k = wounds already in the deck: added every time an owned cell becomes TAKEN
  (a HIT on a DOWN cell, DECAY, SACRIFICE). Wounds can't be placed or spent.
- Built cards ("b<k>", t, "GUARD"), k = built cards so far.

A leg is 3 raids
- DECAY (every raid after the first, before CAPTURE): every owned cell still DOWN becomes TAKEN (a wound each). Its
  card leaves the placement.
- CAPTURE: claim 1 NEUTRAL cell orthogonally adjacent to an owned non-TAKEN cell, or a cell at x = 0. It works on the
  decayed state. If extra_capture > 0 (set by HOT), claim a second cell from the updated options; then clear it.
- DRAW: hand(leg, raid, st) = the deck ids in id order, shuffled by random.Random(HAND_SEED + 13 * seed + raid), first
  hand_size(heat) ids (Heat at draw time, without the ghost).
- PLAN: place min(non-wound hand cards, live cells, MAX_PLACED = 2) hand cards as sentries (at most 1 per owned
  non-TAKEN cell; a card's type is the sentry's type). Optionally a ghost (kit) on an owned non-TAKEN cell or HOME,
  for +5 Heat.
- LAUNCH, in order:
  - beam 1;
  - extra 1 (Heat >= 50) and extra 2 (Heat >= 75), using launch Heat with the ghost;
  - REVEAL A (the sealed route `cand`);
  - the RESPONSE (chosen knowing A, not B or the hunter street);
  - sealed A;
  - REVEAL B (one of the two other routes);
  - sealed B;
  - the HUNTER REVEAL;
  - the hunter.
- BETWEEN (not after raid 3):
  - repair <= 1 DOWN cell (v // 2, free under NORMAL);
  - build: None, a D / N / E GUARD card (3), or CLEAN the highest-id wound (4);
  - pick an intensity.
  - Income and Heat are added after that, then the perk flag (HOT: extra_capture = 1).

Beams
- Every beam is typed (D drone, N netrunner, E enforcer) and runs along a line.
  - A ROUTE runs x = 3 -> 0, then reaches HOME.
  - A STREET runs y 0 -> 2 or 2 -> 0 and never reaches HOME.
- The sealed beams are routes, each route carrying a distinct type (a seeded permutation). A is seeded (`real`);
  B (`real_b`) is drawn by random.Random(SEALB_SEED + 13 * seed + raid) among the two others.
- The hunter (typed) runs street(hunter_cands[hunter_real], down) unless JAMMED. The two hunter streets are drawn by
  random.Random(HUNTER_SEED + 13 * seed + raid).

Scanning a line
- A ghosted cell: pass.
- A sentry card of the beam's type: BLOCK. The line stops, so a stopped route never reaches HOME.
- An owned live cell not yet hit this raid: HIT (OK -> DOWN, DOWN -> TAKEN; a TAKEN cell's card leaves the
  placement and a wound joins the deck).
- Otherwise: pass.
- At the end of a route, unless HOME is ghosted or was already hit this raid:
  - HOME -1;
  - after a SACRIFICE, HOME is unharmed instead and the touch is ("HOME", "shielded").
- No touches at all (and no SACRIFICE) = EVADED: Heat -10.

Response (after REVEAL A; the response hand = the hand minus the placed cards; REDEPLOY / DEPLOY / JAM cost +2 Heat
after the sweep)
- HOLD.
- REDEPLOY s -> c: needs a SHIFT card in the response hand.
- DEPLOY t -> c: needs a non-wound response-hand card of type t (the lowest such id is placed); it stays placed.
- SACRIFICE c (no card, no Heat): an owned live cell becomes TAKEN now (a wound); HOME cannot lose integrity for the
  rest of this raid.
- JAM (no hunter): needs a JAM card in the response hand.
- Order: HOLD, every REDEPLOY, every DEPLOY (types D, N, E, then target cells in cell order), every SACRIFICE (cell
  order), JAM.

safe_next (L11, read with R1)
- True if some capture, then some placement, then per sealed A some response, keeps HOME above 0 for both B routes.
  It takes the post-decay state; True when raid >= RAIDS.

Score
- bank + sum(v - (v // 2 if DOWN)) over owned non-TAKEN cells
- + 6 per owned non-TAKEN EXPLOIT cell
- - 15 per HOME lost
- - 0.5 per Heat above 44, - 6 if Heat >= 50, - 6 if Heat >= 75
- - 5 per wound in the deck
- A breach scores -100.
- Planner only (mid=True): + KIT_VALUE per ghost and per built card.

Measured (python sweep_l8.py; LEGS env var, default 20)
- Greedy against naive. Greedy plays each phase to maximize EV over 3 A x 2 B x 2 hunter streets, with the best
  response per A, and values kit at KIT_VALUE mid-leg.
- Per player: the L10-L13 metrics, plus b_split, wounds_end, dead_draws, clean_use, card_response_use,
  response_decides (real cell) and response_decides_table (any of the real A's 4 (B, hunt) cells)."""
from __future__ import annotations

import json
import os
import statistics as stats
import random
from dataclasses import dataclass, replace

# Grid: cell order is y, then x.
W, H = 4, 3
CELLS = tuple((x, y) for y in range(H) for x in range(W))
NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))

# Beam types and display names.
TYPES = ("D", "N", "E")
TYPE_NAMES = {"D": "DRONE", "N": "NETRUNNER", "E": "ENFORCER"}
ROUTE_NAMES = ("NORTH", "MID", "SOUTH")

# Leg shape.
VALUES = (4, 6, 8, 10, 12)
EXPLOITS, START_CELLS, RAIDS, CANDIDATES = 3, 2, 3, 3
HUNTER_CANDS = 2        # L13 R2: two sealed hunter streets per raid
HUNTER_SEED = 9100      # L13 R2: random.Random(HUNTER_SEED + 13 * seed + raid)
SEALB_SEED = 9200       # L14 R1: random.Random(SEALB_SEED + 13 * seed + raid) draws real_b
HAND_SEED = 9300        # L14 R9: random.Random(HAND_SEED + 13 * seed + raid) shuffles the hand

# Cell statuses.
HOME = "HOME"
OK, DOWN, TAKEN = "OK", "DOWN", "TAKEN"
LIVE = (OK, DOWN)

# Cards (L14 R9).
GUARD, SHIFT, JAM, WOUND = "GUARD", "SHIFT", "JAM", "WOUND"
VERBS = (GUARD, SHIFT, JAM, WOUND)
WOUND_TYPE = "-"
START_DECK = (("s0", "D", GUARD), ("s1", "D", GUARD), ("s2", "N", GUARD), ("s3", "N", GUARD),
              ("s4", "E", GUARD), ("s5", "D", SHIFT), ("s6", "E", SHIFT), ("s7", "N", JAM))
HAND_BASE = 4           # L14 R13: +1 at Heat >= EXTRA_AT, +1 at Heat >= STRONG_AT

# Economy and Heat.
START_BANK, START_HEAT = 10, 44
EXTRA_AT, STRONG_AT = 50, 75
HOME_HP = 3
GHOST_HEAT, SPOOF_HEAT, EVADE_HEAT = 5, 2, 10
HINT_HEAT = 3       # L14 R14: buy_hint
SENTRY_PRICE = 3    # L9 (was 4): a built GUARD card
CLEAN_PRICE = 4     # L14 R9: remove the highest-id wound
MAX_PLACED = 2      # L11: PLAN places at most 2 sentries
KIT_START = (("ghost", 2),)     # L14 R9: spoof is gone; responses are paid with cards
INTENSITY = {"LOW": (6, 0.5), "NORMAL": (12, 1.0), "HOT": (18, 0.5)}    # L13b: HOT income x0.5 (x1.5 made HOT 38/40)
PERKS = {"LOW": None, "NORMAL": "FREE_REPAIR", "HOT": "EXTRA_CAPTURE"}    # L13 R5
DECAY = True        # L9: DOWN -> TAKEN at the start of every raid after the first, before CAPTURE
BUILDS = ("D", "N", "E", "CLEAN")

# Responses that need a card and cost SPOOF_HEAT. HOLD and SACRIFICE are free.
CARD_RESPONSES = ("REDEPLOY", "DEPLOY", "JAM")

# Score.
EXPLOIT_BONUS, HOME_LOSS_COST, HEAT_CARRY, BREACH = 6, 15, 0.5, 100    # L13 R4: HOME 15 (was 8), carry 0.5 (was 1.0)
HEAT_BAND = 6       # L13 R4: -6 at Heat >= EXTRA_AT, another -6 at Heat >= STRONG_AT
WOUND_COST = 5      # L14 R9: per wound in the deck
KIT_VALUE = 2.5     # planner heuristic only: an unspent ghost or a built card mid-leg
EPS = 1e-9          # float ties keep the earlier option
LEGS = int(os.environ.get("LEGS", 20))     # L14: 20 legs by default; lower it to bound the run time
OUT = r"D:/rc_tmp/raid_design_lab/sweep_l14.json"


def ck(c) -> tuple:
    """Sort key: cell order y then x."""
    return (c[1], c[0])


def config() -> dict:
    return {"W": W, "H": H, "TYPES": list(TYPES), "VALUES": list(VALUES), "EXPLOITS": EXPLOITS, "START_CELLS": START_CELLS,
            "RAIDS": RAIDS, "HUNTER_CANDS": HUNTER_CANDS, "HUNTER_SEED": HUNTER_SEED, "SEALB_SEED": SEALB_SEED,
            "HAND_SEED": HAND_SEED, "HAND_BASE": HAND_BASE, "START_DECK": [list(c) for c in START_DECK],
            "START_BANK": START_BANK, "START_HEAT": START_HEAT, "EXTRA_AT": EXTRA_AT,
            "STRONG_AT": STRONG_AT, "HOME_HP": HOME_HP, "GHOST_HEAT": GHOST_HEAT, "SPOOF_HEAT": SPOOF_HEAT,
            "HINT_HEAT": HINT_HEAT, "EVADE_HEAT": EVADE_HEAT, "SENTRY_PRICE": SENTRY_PRICE,
            "CLEAN_PRICE": CLEAN_PRICE, "MAX_PLACED": MAX_PLACED,
            "KIT_START": dict(KIT_START), "INTENSITY": {k: list(v) for k, v in INTENSITY.items()},
            "PERKS": dict(PERKS),
            "EXPLOIT_BONUS": EXPLOIT_BONUS, "HOME_LOSS_COST": HOME_LOSS_COST, "HEAT_CARRY": HEAT_CARRY,
            "HEAT_BAND": HEAT_BAND, "WOUND_COST": WOUND_COST, "BREACH": BREACH, "KIT_VALUE": KIT_VALUE,
            "DECAY": DECAY}


@dataclass(frozen=True)
class Line:
    kind: str       # "ROUTE" | "STREET"
    index: int      # row for a route, column for a street
    cells: tuple
    type: str       # "D" | "N" | "E"
    home: bool      # True for routes: the line reaches HOME after its cells


def route(y: int, t: str) -> Line:
    return Line("ROUTE", y, tuple((x, y) for x in range(W - 1, -1, -1)), t, True)


def street(x: int, down: bool, t: str) -> Line:
    ys = range(H) if down else range(H - 1, -1, -1)
    return Line("STREET", x, tuple((x, y) for y in ys), t, False)


@dataclass(frozen=True)
class Raid:
    b1: Line
    extra1: Line
    extra2: Line
    perm: tuple             # perm[k] = the type of sealed candidate k (route k)
    cands: tuple            # the three route Lines
    real: int               # sealed A: the corp's real first sealed route
    real_b: int             # L14 R1: sealed B, one of the two other routes
    hunter_type: str
    hunter_cands: tuple     # L13 R2: 2 distinct streets (draw order), both shown to the player
    hunter_real: int        # L13 R2: index into hunter_cands of the street the hunter runs


@dataclass(frozen=True)
class Leg:
    seed: int
    values: tuple           # ((cell, v), ...) in cell order
    exploits: tuple         # cells, in cell order
    start: tuple            # owned OK cells at leg start
    raids: tuple


@dataclass(frozen=True)
class State:
    heat: int = START_HEAT
    bank: int = START_BANK
    home_hp: int = HOME_HP
    owned: tuple = ()       # ((cell, status), ...) in cell order; NEUTRAL cells absent
    sentries: tuple = ()    # ((cell, card_id), ...) in cell order: the last placement (with any DEPLOY)
    deck: tuple = START_DECK    # L14 R9: ((id, type, verb), ...) sorted by id
    kit: tuple = KIT_START
    extra_capture: int = 0  # L13 R5: HOT sets 1; the next CAPTURE phase takes a second cell and clears it


def _otup(d: dict) -> tuple:
    return tuple(sorted(d.items(), key=lambda kv: ck(kv[0])))


def _kit_t(d: dict) -> tuple:
    return (("ghost", d["ghost"]),)


def _deck_t(cards) -> tuple:
    return tuple(sorted(cards, key=lambda c: c[0]))


def _live(st: State) -> list:
    return [c for c, s in st.owned if s in LIVE]


def _cards(st: State) -> dict:
    """id -> (type, verb)."""
    return {c[0]: (c[1], c[2]) for c in st.deck}


def wound_count(deck) -> int:
    return sum(1 for c in deck if c[2] == WOUND)


def built_count(deck) -> int:
    return sum(1 for c in deck if c[0].startswith("b"))


def _add_wounds(deck, n: int) -> tuple:
    """Add n wound cards, each ("w<k>", "-", "WOUND") with k = the wounds already in the deck."""
    if n <= 0:
        return deck
    cards = list(deck)
    for _ in range(n):
        cards.append(("w%d" % wound_count(cards), WOUND_TYPE, WOUND))
    return _deck_t(cards)


def sealed_b_options(cand: int) -> list:
    """L14 R1: the two possible B routes for sealed A = cand, in route order."""
    return [k for k in range(CANDIDATES) if k != cand]


def _rand_line(rng: random.Random) -> Line:
    """Draw order (stable): kind, index, direction (streets only), type."""
    if rng.random() < 0.5:
        y = rng.randrange(H)
        return route(y, rng.choice(TYPES))
    x = rng.randrange(W)
    down = rng.random() < 0.5
    return street(x, down, rng.choice(TYPES))


def make_leg(seed: int) -> Leg:
    """Seeded leg; the draw order is fixed, so a seed always gives the same leg. The hunter streets (L13) and real_b
    (L14) come from their own per-raid rngs, so every other draw is unchanged (the old hunter_street draw is still made
    and discarded)."""
    rng = random.Random(8000 + seed)
    values = tuple((c, rng.choice(VALUES)) for c in CELLS)
    exploits = tuple(sorted(rng.sample([c for c in CELLS if c[0] >= 1], EXPLOITS), key=ck))
    start = tuple(sorted(rng.sample([c for c in CELLS if c[0] == 0], START_CELLS), key=ck))
    raids = []
    for i in range(RAIDS):
        b1, e1, e2 = _rand_line(rng), _rand_line(rng), _rand_line(rng)
        perm = list(TYPES)
        rng.shuffle(perm)
        real = rng.randrange(CANDIDATES)
        ht = rng.choice(TYPES)
        rng.randrange(W)        # the removed hunter_street draw, kept so the rest of the leg data is identical
        hr = random.Random(HUNTER_SEED + 13 * seed + i)
        hc = tuple(hr.sample(range(W), HUNTER_CANDS))
        hreal = hr.randrange(HUNTER_CANDS)
        br = random.Random(SEALB_SEED + 13 * seed + i)
        real_b = [k for k in range(CANDIDATES) if k != real][br.randrange(2)]
        raids.append(Raid(b1, e1, e2, tuple(perm), tuple(route(k, perm[k]) for k in range(CANDIDATES)), real, real_b,
                          ht, hc, hreal))
    return Leg(seed, values, exploits, start, tuple(raids))


def initial(leg: Leg) -> State:
    return State(owned=tuple((c, OK) for c in leg.start))


def hand_size(heat: int) -> int:
    """L14 R13: HAND_BASE, +1 at Heat >= EXTRA_AT, +1 at Heat >= STRONG_AT."""
    return HAND_BASE + int(heat >= EXTRA_AT) + int(heat >= STRONG_AT)


def hand(leg: Leg, raid: int, st: State) -> list:
    """L14 R9 DRAW: the deck ids in id order, shuffled by random.Random(HAND_SEED + 13 * seed + raid); the first
    hand_size(st.heat) ids (Heat at draw time, without the ghost)."""
    ids = sorted(c[0] for c in st.deck)
    random.Random(HAND_SEED + 13 * leg.seed + raid).shuffle(ids)
    return ids[:hand_size(st.heat)]


def buy_hint(st: State) -> State:
    """L14 R14: the scan costs HINT_HEAT."""
    return replace(st, heat=st.heat + HINT_HEAT)


def decay_cells(leg: Leg, st: State) -> list:
    """The owned cells DECAY turns TAKEN (status still DOWN), in cell order."""
    return [c for c, s in st.owned if s == DOWN]


def decay(leg: Leg, st: State) -> State:
    """L9 DECAY, applied at the start of every raid after the first, before CAPTURE: every owned DOWN cell becomes
    TAKEN, its card leaves the placement, and a wound joins the deck per cell (L14 R9). The caller decides when
    (raid > 0)."""
    owned = dict(st.owned)
    sent = dict(st.sentries)
    cells = decay_cells(leg, st)
    for c in cells:
        owned[c] = TAKEN
        sent.pop(c, None)
    return replace(st, owned=_otup(owned), sentries=_otup(sent), deck=_add_wounds(st.deck, len(cells)))


def capture_options(leg: Leg, st: State) -> list:
    """NEUTRAL cells adjacent to an owned non-TAKEN cell, or at x = 0 (next to HOME); in cell order."""
    owned = dict(st.owned)
    live = {c for c, s in owned.items() if s in LIVE}
    out = []
    for c in CELLS:
        if c in owned:
            continue
        x, y = c
        if x == 0 or any((x + dx, y + dy) in live for dx, dy in NEIGHBORS):
            out.append(c)
    return out


def capture(leg: Leg, st: State, cell) -> State:
    """One claim. It leaves extra_capture alone; the CAPTURE phase (capture_cells) clears it."""
    cell = tuple(cell)
    if cell not in capture_options(leg, st):
        raise ValueError(f"illegal capture {cell}")
    owned = dict(st.owned)
    owned[cell] = OK
    return replace(st, owned=_otup(owned))


def capture_cells(leg: Leg, st: State, cells) -> State:
    """L13 R5 CAPTURE phase: capture each cell in order (at most 1 + extra_capture; the second uses the updated
    state's options), then clear extra_capture."""
    cells = [tuple(c) for c in (cells or [])]
    if len(cells) > 1 + st.extra_capture:
        raise ValueError(f"too many captures {cells}")
    s = st
    for c in cells:
        s = capture(leg, s, c)
    return replace(s, extra_capture=0)


def capture_plans(leg: Leg, st: State) -> list:
    """Every legal CAPTURE phase as a tuple of cells: () when there is no option, else one cell, or two cells when
    extra_capture > 0 and a second option exists (the second capture is not skippable either). Each set of cells
    appears once: a second cell that was also a first option comes only after the first in cell order."""
    first = capture_options(leg, st)
    if not first:
        return [()]
    out = []
    fset = set(first)
    for c1 in first:
        if st.extra_capture <= 0:
            out.append((c1,))
            continue
        second = capture_options(leg, capture(leg, st, c1))
        if not second:
            out.append((c1,))
            continue
        for c2 in second:
            if c2 in fset and ck(c2) < ck(c1):
                continue
            out.append((c1, c2))
    return out


def placements(leg: Leg, raid: int, st: State):
    """Yields (sentries {cell: card_id}, ghost) with min(non-wound hand cards, live cells, MAX_PLACED) hand cards
    placed (L14 R9).
    - Distinct by the (type, verb) signature on each cell; a signature always uses its lowest remaining id.
    - DFS order: cells in cell order; at a cell, signatures in hand order of first appearance among the remaining
      (unplaced) non-wound hand cards; then skip the cell.
    - Ghost order: None, HOME, then live cells."""
    live = _live(st)
    cards = _cards(st)
    hids = [i for i in hand(leg, raid, st) if cards[i][1] != WOUND]
    need = min(len(hids), len(live), MAX_PLACED)
    used = set()
    maps = []

    def rec(idx: int, cur: dict, k: int):
        if k == 0:
            maps.append(dict(cur))
            return
        if len(live) - idx < k:
            return
        c = live[idx]
        tried = set()
        for i in hids:
            if i in used:
                continue
            sig = cards[i]
            if sig in tried:
                continue
            tried.add(sig)
            pick = min(j for j in hids if j not in used and cards[j] == sig)
            used.add(pick)
            cur[c] = pick
            rec(idx + 1, cur, k - 1)
            del cur[c]
            used.discard(pick)
        rec(idx + 1, cur, k)

    rec(0, {}, need)
    ghosts = [None] + (([HOME] + live) if dict(st.kit)["ghost"] > 0 else [])
    for g in ghosts:
        for m in maps:
            yield (dict(m), g)


def _check_place(st: State, place, hids: list, cards: dict) -> None:
    sent, ghost = place
    live = set(_live(st))
    if len(sent) > MAX_PLACED:
        raise ValueError(f"more than {MAX_PLACED} sentries placed")
    if len(set(sent.values())) != len(sent):
        raise ValueError("a card placed twice")
    hset = set(hids)
    for c, j in sent.items():
        if c not in live or j not in hset or cards[j][1] == WOUND:
            raise ValueError(f"illegal sentry {c} {j}")
    if ghost is not None and (dict(st.kit)["ghost"] <= 0 or (ghost != HOME and ghost not in live)):
        raise ValueError(f"illegal ghost {ghost}")


def norm_response(r) -> tuple:
    """None / "HOLD" / "JAM" / ("REDEPLOY", s, c) / ("DEPLOY", t, c) / ("SACRIFICE", c) (lists accepted) -> a
    canonical tuple."""
    if r is None:
        return ("HOLD",)
    if isinstance(r, str):
        r = (r,)
    r = tuple(r)
    if r[0] == "REDEPLOY" and len(r) == 3:
        return ("REDEPLOY", tuple(r[1]), tuple(r[2]))
    if r[0] == "DEPLOY" and len(r) == 3:
        return ("DEPLOY", str(r[1]), tuple(r[2]))
    if r[0] == "SACRIFICE" and len(r) == 2:
        return ("SACRIFICE", tuple(r[1]))
    if r[0] in ("HOLD", "JAM") and len(r) == 1:
        return r
    raise ValueError(f"unknown response {r}")


class _Sweep:
    """One raid's mutable sweep: board, sentry cards, seen cells, HOME, the SACRIFICE shield, new wounds, and the
    trace [(beam, cell, kind)]."""
    __slots__ = ("sent", "ctype", "ghost", "owned", "hp", "home_hit", "shield", "seen", "trace", "wounds")

    def __init__(self, st: State, place, ctype: dict):
        self.sent = dict(place[0])
        self.ctype = ctype          # card id -> type (shared, read-only)
        self.ghost = place[1]
        self.owned = dict(st.owned)
        self.hp = st.home_hp
        self.home_hit = False
        self.shield = False
        self.seen = set()
        self.trace = []
        self.wounds = 0

    def copy(self) -> "_Sweep":
        o = _Sweep.__new__(_Sweep)
        o.sent = dict(self.sent)
        o.ctype = self.ctype
        o.ghost = self.ghost
        o.owned = dict(self.owned)
        o.hp = self.hp
        o.home_hit = self.home_hit
        o.shield = self.shield
        o.seen = set(self.seen)
        o.trace = list(self.trace)
        o.wounds = self.wounds
        return o

    def scan(self, name: str, ln: Line) -> None:
        for c in ln.cells:
            if c == self.ghost:
                continue
            j = self.sent.get(c)
            if j is not None and self.ctype[j] == ln.type:
                self.trace.append((name, c, "block"))
                return
            s = self.owned.get(c)
            if s in LIVE and c not in self.seen:
                if s == OK:
                    self.owned[c] = DOWN
                else:
                    self.owned[c] = TAKEN
                    self.sent.pop(c, None)      # the card leaves the placement (it stays in the deck)
                    self.wounds += 1            # L14 R9
                self.trace.append((name, c, "hit"))
                self.seen.add(c)
        if ln.home and self.ghost != HOME and not self.home_hit:
            if self.shield:
                self.trace.append((name, HOME, "shielded"))     # L13 R3: HOME is unharmed
            else:
                self.hp = max(0, self.hp - 1)
                self.home_hit = True
                self.trace.append((name, HOME, "home"))


def _launch(leg: Leg, raid: int, st: State, place):
    """Draw, check the placement, then beam 1 and the extras (before REVEAL A).
    Returns (raid, launch heat, sweep, response hand [(id, type, verb)] in hand order)."""
    cards = _cards(st)
    hids = hand(leg, raid, st)
    _check_place(st, place, hids, cards)
    rd = leg.raids[raid]
    heat = st.heat + (GHOST_HEAT if place[1] is not None else 0)
    sw = _Sweep(st, place, {i: tv[0] for i, tv in cards.items()})
    sw.scan("beam1", rd.b1)
    if heat >= EXTRA_AT:
        sw.scan("extra1", rd.extra1)
    if heat >= STRONG_AT:
        sw.scan("extra2", rd.extra2)
    used = set(place[0].values())
    rhand = [(j,) + cards[j] for j in hids if j not in used]
    return rd, heat, sw, rhand


def _has_verb(rhand: list, verb: str) -> bool:
    return any(c[2] == verb for c in rhand)


def _deploy_card(rhand: list, t: str):
    """The lowest-id non-wound response-hand card of type t, or None."""
    ids = [c[0] for c in rhand if c[1] == t and c[2] != WOUND]
    return min(ids) if ids else None


def _respond(st: State, sw: _Sweep, resp: tuple, rhand: list) -> None:
    """Apply a canonical response to a sweep after beam 1 and the extras (validates it against the response hand)."""
    if resp[0] == "REDEPLOY":
        s, c = resp[1], resp[2]
        if not _has_verb(rhand, SHIFT):
            raise ValueError("REDEPLOY needs a SHIFT card")
        if s not in sw.sent or c == s or c in sw.sent or sw.owned.get(c) not in LIVE:
            raise ValueError(f"illegal redeploy {s} -> {c}")
        sw.sent[c] = sw.sent.pop(s)
    elif resp[0] == "DEPLOY":
        t, c = resp[1], resp[2]
        j = _deploy_card(rhand, t) if t in TYPES else None
        if j is None or c in sw.sent or sw.owned.get(c) not in LIVE:
            raise ValueError(f"illegal deploy {t} -> {c}")
        sw.sent[c] = j
    elif resp[0] == "SACRIFICE":
        c = resp[1]
        if sw.owned.get(c) not in LIVE:
            raise ValueError(f"illegal sacrifice {c}")
        sw.owned[c] = TAKEN
        sw.sent.pop(c, None)
        sw.wounds += 1                          # L14 R9
        sw.shield = True
    elif resp[0] == "JAM":
        if not _has_verb(rhand, JAM):
            raise ValueError("JAM needs a JAM card")


def _close(st: State, place, heat: int, sw: _Sweep, resp: tuple) -> State:
    """The state after a finished sweep: EVADED Heat (no touches and no SACRIFICE), card-response Heat, ghost spent,
    wounds added."""
    kit = dict(st.kit)
    if not sw.trace and not sw.shield:
        heat -= EVADE_HEAT
    if resp[0] in CARD_RESPONSES:
        heat += SPOOF_HEAT
    if place[1] is not None:
        kit["ghost"] -= 1
    return State(heat, st.bank, sw.hp, _otup(sw.owned), _otup(sw.sent), _add_wounds(st.deck, sw.wounds),
                 _kit_t(kit), st.extra_capture)


def _hunter_street(rd: Raid, hunt: int) -> Line:
    return street(rd.hunter_cands[hunt], True, rd.hunter_type)


def _check_cands(cand: int, cand_b: int, hunt: int) -> None:
    if cand not in range(CANDIDATES) or cand_b not in range(CANDIDATES) or hunt not in range(HUNTER_CANDS):
        raise ValueError(f"illegal cand/cand_b/hunt {cand} {cand_b} {hunt}")
    if cand_b == cand:
        raise ValueError(f"cand_b equals cand {cand}")


def _resolve(leg: Leg, raid: int, st: State, cand: int, cand_b: int, hunt: int, place, response):
    resp = norm_response(response)
    _check_cands(cand, cand_b, hunt)
    rd, heat, sw, rhand = _launch(leg, raid, st, place)
    _respond(st, sw, resp, rhand)
    sw.scan("sealed", rd.cands[cand])
    sw.scan("sealed_b", rd.cands[cand_b])
    if resp[0] != "JAM":
        sw.scan("hunter", _hunter_street(rd, hunt))
    return _close(st, place, heat, sw, resp), sw.trace


def resolve(leg: Leg, raid: int, st: State, cand: int, cand_b: int, hunt: int, place, response=None):
    """One raid (raid = index into leg.raids) from the post-capture state.
    - cand: sealed A; cand_b: sealed B (!= cand); hunt: the index into hunter_cands.
    - place = (sentries {cell: card_id}, ghost).
    - response: any legal response.
    Returns (state after the raid, touches [(cell | "HOME", "hit" | "block" | "home" | "shielded")])."""
    ns, tr = _resolve(leg, raid, st, cand, cand_b, hunt, place, response)
    return ns, [(c, k) for _, c, k in tr]


def trace(leg: Leg, raid: int, st: State, cand: int, cand_b: int, hunt: int, place, response=None) -> list:
    """The touches with their beam: [(beam, cell, kind)], beam in beam1/extra1/extra2/sealed/sealed_b/hunter."""
    return _resolve(leg, raid, st, cand, cand_b, hunt, place, response)[1]


def hunter_line(leg: Leg, raid: int, st: State, cand: int, cand_b: int, hunt: int, place,
                response=None) -> Line | None:
    """The street the hunter runs: hunter_cands[hunt], top to bottom (None when JAMMED)."""
    resp = norm_response(response)
    _check_cands(cand, cand_b, hunt)
    if resp[0] == "JAM":
        return None
    return _hunter_street(leg.raids[raid], hunt)


def _options_from(st: State, sw: _Sweep, rhand: list) -> list:
    """Response options read from a sweep after beam 1 and the extras (see response_options)."""
    out = [("HOLD",)]
    live = [c for c in CELLS if sw.owned.get(c) in LIVE]
    targets = [c for c in live if c not in sw.sent]
    if _has_verb(rhand, SHIFT):
        for s in sorted(sw.sent, key=ck):
            for c in targets:
                if c != s:
                    out.append(("REDEPLOY", s, c))
    for t in TYPES:
        if _deploy_card(rhand, t) is not None:
            for c in targets:
                out.append(("DEPLOY", t, c))
    for c in live:
        out.append(("SACRIFICE", c))
    if _has_verb(rhand, JAM):
        out.append(("JAM",))
    return out


def response_options(leg: Leg, raid: int, st: State, cand: int, place) -> list:
    """In order:
    - HOLD;
    - with a SHIFT card in the response hand: every REDEPLOY (source by cell order, then target);
    - every DEPLOY (types D, N, E with a non-wound response-hand card of that type, then target in cell order);
    - every SACRIFICE (owned live cells in cell order; no card needed);
    - with a JAM card in the response hand: JAM.
    Legality is read after beam 1 and the extras (it does not depend on cand)."""
    _, _, sw, rhand = _launch(leg, raid, st, place)
    return _options_from(st, sw, rhand)


def _grid(leg: Leg, raid: int, st: State, place, opts=None, prune: bool = False):
    """Fast batch resolve sharing one launch: (opts, res), res[i][k][bi][h] = (state, touches) for response opts[i],
    sealed A = k, sealed B = sealed_b_options(k)[bi] and hunter street h. opts=None uses response_options.
    prune=True (planner only) puts None for SACRIFICE entries that can't beat HOLD. Such an entry is never chosen
    (HOLD is earlier and >=). The cases: HOME is ghosted, HOME was already hit before the response, or HOLD on that
    A keeps HOME for both B routes."""
    rd, heat, sw0, rhand = _launch(leg, raid, st, place)
    if opts is None:
        opts = _options_from(st, sw0, rhand)
    opts = [norm_response(r) for r in opts]
    hunters = [_hunter_street(rd, h) for h in range(HUNTER_CANDS)]
    skip_sac = prune and (sw0.ghost == HOME or sw0.home_hit)
    hold_safe = None
    res = []
    for r in opts:
        sac = r[0] == "SACRIFICE"
        if sac and skip_sac:
            res.append([None] * CANDIDATES)
            continue
        sw1 = sw0.copy()
        _respond(st, sw1, r, rhand)
        row = []
        for k in range(CANDIDATES):
            if sac and prune and hold_safe is not None and hold_safe[k]:
                row.append(None)
                continue
            sw2 = sw1.copy()
            sw2.scan("sealed", rd.cands[k])
            bs = sealed_b_options(k)
            tab = []
            for bi, b in enumerate(bs):
                sw3 = sw2.copy() if bi < len(bs) - 1 else sw2
                sw3.scan("sealed_b", rd.cands[b])
                outs = []
                for h in range(HUNTER_CANDS):
                    sw4 = sw3.copy() if h < HUNTER_CANDS - 1 else sw3
                    if r[0] != "JAM":
                        sw4.scan("hunter", hunters[h])
                    outs.append((_close(st, place, heat, sw4, r), [(c, kd) for _, c, kd in sw4.trace]))
                tab.append(outs)
            row.append(tab)
        if r[0] == "HOLD" and hold_safe is None:
            hold_safe = [all(row[k][bi][0][0].home_hp >= sw0.hp for bi in range(len(row[k])))
                         for k in range(CANDIDATES)]
        res.append(row)
    return opts, res


def tier(before: State, after: State, touches) -> str:
    """BREACHED, DAMAGED, EVADED (no touches and no newly TAKEN cell, so a SACRIFICE is never EVADED), BATTERED, HOLDS."""
    if after.home_hp <= 0:
        return "BREACHED"
    if after.home_hp < before.home_hp:
        return "DAMAGED"
    b, a = dict(before.owned), dict(after.owned)
    new_down = sum(1 for c, s in a.items() if s == DOWN and b.get(c) == OK)
    new_taken = sum(1 for c, s in a.items() if s == TAKEN and b.get(c) != TAKEN)
    if not touches and new_taken == 0:
        return "EVADED"
    return "BATTERED" if new_down >= 2 or new_taken >= 1 else "HOLDS"


def score(leg: Leg, st: State, mid: bool = False) -> float:
    """Leg score (L13 R4 Heat bands, L14 R9 wounds); mid=True adds KIT_VALUE per unspent ghost and per built card
    (planner heuristic only)."""
    if st.home_hp <= 0:
        return float(-BREACH)
    vals = dict(leg.values)
    ex = set(leg.exploits)
    s = float(st.bank)
    for c, stat in st.owned:
        if stat in LIVE:
            s += vals[c] - (vals[c] // 2 if stat == DOWN else 0) + (EXPLOIT_BONUS if c in ex else 0)
    s -= HOME_LOSS_COST * (HOME_HP - st.home_hp)
    s -= HEAT_CARRY * max(0, st.heat - START_HEAT)
    s -= HEAT_BAND * (int(st.heat >= EXTRA_AT) + int(st.heat >= STRONG_AT))
    s -= WOUND_COST * wound_count(st.deck)
    if mid:
        s += KIT_VALUE * (dict(st.kit)["ghost"] + built_count(st.deck))
    return s


def repair_cost(leg: Leg, cell, intensity: str) -> int:
    """v // 2, or 0 under the NORMAL perk (L13 R5)."""
    if PERKS[intensity] == "FREE_REPAIR":
        return 0
    return dict(leg.values)[tuple(cell)] // 2


def build_price(build) -> int:
    return CLEAN_PRICE if build == "CLEAN" else SENTRY_PRICE


def between(leg: Leg, st: State, repair=None, build=None, intensity: str = "NORMAL") -> State:
    """In order:
    1. repair (<= 1 DOWN cell, v // 2, free under NORMAL);
    2. build: a D / N / E GUARD card ("b<k>", SENTRY_PRICE) or CLEAN (the highest-id wound, CLEAN_PRICE);
    3. income and Heat;
    4. the perk flag (HOT: extra_capture = 1).
    An unaffordable or illegal repair or build is skipped."""
    vals = dict(leg.values)
    owned = dict(st.owned)
    bank = st.bank
    if repair is not None:
        repair = tuple(repair)
        cost = repair_cost(leg, repair, intensity) if repair in vals else 0
        if owned.get(repair) == DOWN and bank >= cost:
            bank -= cost
            owned[repair] = OK
    deck = list(st.deck)
    if build in TYPES and bank >= SENTRY_PRICE:
        bank -= SENTRY_PRICE
        deck.append(("b%d" % built_count(deck), build, GUARD))
    elif build == "CLEAN" and bank >= CLEAN_PRICE:
        wounds = [c for c in deck if c[2] == WOUND]
        if wounds:
            bank -= CLEAN_PRICE
            deck.remove(max(wounds, key=lambda c: c[0]))
    dh, mult = INTENSITY[intensity]
    income = int(sum(vals[c] // 3 for c, s in owned.items() if s == OK) * mult)
    extra = 1 if PERKS[intensity] == "EXTRA_CAPTURE" else st.extra_capture
    return State(st.heat + dh, bank + income, st.home_hp, _otup(owned), st.sentries, _deck_t(deck), st.kit, extra)


def between_options(leg: Leg, st: State):
    """Yields (repair, build, intensity), all affordable under that intensity (NORMAL repairs free): repair None then
    DOWN cells (cell order); build None, D, N, E, then CLEAN (only with a wound in the deck); intensity LOW, NORMAL,
    HOT."""
    downs = [c for c, s in st.owned if s == DOWN]
    builds = [None] + list(TYPES) + (["CLEAN"] if wound_count(st.deck) > 0 else [])
    for r in [None] + downs:
        for b in builds:
            for inten in INTENSITY:
                cost = repair_cost(leg, r, inten) if r is not None else 0
                if st.bank < cost:
                    continue
                if b is not None and st.bank - cost < build_price(b):
                    continue
                yield (r, b, inten)


def safe_next(leg: Leg, raid: int, st: State) -> bool:
    """L11 (read with L14 R1): True if some CAPTURE phase (capture_plans), then some placement, then per sealed A some
    response, keeps HOME above 0 for both B routes of raid `raid`. `st` is the post-decay state (the caller applies
    DECAY). True when raid >= RAIDS.
    - The hunter runs a street and never reaches HOME, so the hunter street does not matter (hunt 0 is read).
    - Exact shortcuts: HOME loses at most 1 per raid (home_hp >= 2 is safe), and a ghost on HOME (kit ghost > 0)
      always keeps HOME.
    - Otherwise the search stops at the first safe plan."""
    if raid >= RAIDS:
        return True
    if st.home_hp <= 0:
        return False
    if st.home_hp >= 2 or dict(st.kit)["ghost"] > 0:
        return True
    for cap in capture_plans(leg, st):
        s1 = capture_cells(leg, st, cap)
        for place in placements(leg, raid, s1):
            _, res = _grid(leg, raid, s1, place, None, prune=True)
            if all(any(row[k] is not None and all(tab[0][0].home_hp > 0 for tab in row[k]) for row in res)
                   for k in range(CANDIDATES)):
                return True
    return False


def safe_after_between(leg: Leg, nxt: int, st: State, repair=None, build=None, intensity: str = "NORMAL") -> bool:
    """safe_next for raid `nxt` after a between step on the post-raid state `st`: between, DECAY (nxt > 0), safe_next."""
    s = between(leg, st, repair, build, intensity)
    if nxt > 0:
        s = decay(leg, s)
    return safe_next(leg, nxt, s)


def decided(leg: Leg, nxt: int, st: State) -> bool:
    """L11 "decided" cut: True when no between option on the post-raid state `st` makes raid `nxt` safe."""
    return not any(safe_after_between(leg, nxt, st, *opt) for opt in between_options(leg, st))


_N_OUTS = (CANDIDATES - 1) * HUNTER_CANDS


def _best_per_cand(leg: Leg, raid: int, st: State, place, mid: bool) -> list:
    """Per sealed A: (value = mean over the 4 (B, hunt) outcomes, best response, [[(after, touches) per hunt] per B]).
    The response is chosen before REVEAL B and the hunter reveal; the earliest response is kept on ties."""
    opts, res = _grid(leg, raid, st, place, None, prune=True)
    per = []
    for k in range(CANDIDATES):
        best = None
        for i, r in enumerate(opts):
            tab = res[i][k]
            if tab is None:
                continue
            v = sum(score(leg, s, mid) for outs in tab for s, _ in outs) / _N_OUTS
            if best is None or v > best[0] + EPS:
                best = (v, r, tab)
        per.append(best)
    return per


def best_response(leg: Leg, raid: int, st: State, cand: int, place) -> tuple:
    """L14 R14: the planner's response for sealed A = cand: the best mean over the 4 (B, hunt) outcomes, earliest on
    ties; kit valued mid-leg (mid=True) except in the final raid."""
    mid = raid < RAIDS - 1
    return _best_per_cand(leg, raid, st, place, mid)[cand][1]


def forecast(leg: Leg, raid: int, st: State, place) -> list:
    """L14 R1: per sealed A, {cand, outcomes: [[HOLD result for (b, hunt 0), (b, hunt 1)] for b in
    sealed_b_options(cand)]}, each {state, touches, tier}."""
    _, res = _grid(leg, raid, st, place, [("HOLD",)])
    return [{"cand": k, "outcomes": [[{"state": s, "touches": t, "tier": tier(st, s, t)} for s, t in outs]
                                     for outs in res[0][k]]}
            for k in range(CANDIDATES)]


def _type_map_key(sent: dict, cards: dict) -> tuple:
    return tuple(sorted((ck(c), cards[j][0]) for c, j in sent.items()))


def _place_key(place, cards: dict, hids: list) -> tuple:
    """Planner cache key: placements with the same sentry types, ghost and response-hand abilities score the same
    (card ids never enter the score)."""
    sent, g = place
    used = set(sent.values())
    rh = [(j,) + cards[j] for j in hids if j not in used]
    return (_type_map_key(sent, cards), g, _has_verb(rh, SHIFT), _has_verb(rh, JAM),
            tuple(t for t in TYPES if _deploy_card(rh, t) is not None))


def _next_value(leg: Leg, raid: int, st: State) -> float:
    """Between-step lookahead:
    - DECAY (raid > 0);
    - the best CAPTURE phase (so HOT's double capture counts);
    - then the next raid's best EV over 3 x 2 x 2 outcomes, with no ghost and HOLD."""
    if raid > 0:
        st = decay(leg, st)
    mid = raid < RAIDS - 1
    best = None
    for cap in capture_plans(leg, st):
        s1 = capture_cells(leg, st, cap)
        cards = _cards(s1)
        seen = set()
        for place in placements(leg, raid, s1):
            if place[1] is not None:
                break       # ghost placements come after every no-ghost placement
            key = _type_map_key(place[0], cards)
            if key in seen:
                continue    # same sentry types: same HOLD outcomes
            seen.add(key)
            _, res = _grid(leg, raid, s1, place, [("HOLD",)])
            ev = sum(score(leg, s, mid) for tab in res[0] for outs in tab for s, _ in outs) / (CANDIDATES * _N_OUTS)
            if best is None or ev > best + EPS:
                best = ev
    return best if best is not None else score(leg, st, mid)


def _entry(i, cap, place, resp, k, b, h, hand_ids, touches, tr, after, decayed=()) -> dict:
    return {"raid": i, "decayed": list(decayed), "capture": [tuple(c) for c in cap], "hand": list(hand_ids),
            "place": {"sentries": dict(place[0]), "ghost": place[1]}, "response": resp,
            "cand_real": k, "cand_b": b, "hunt": h, "touches": touches, "tier": tr, "after_raid": after,
            "between": None}


def greedy_leg(leg: Leg):
    """Per raid:
    - DECAY (raid > 0).
    - The CAPTURE phase and the plan jointly maximize the EV over 3 A x 2 B x 2 hunter streets, with the best
      response per A (kit valued mid-leg). Never buys a hint.
    - The real A, B and hunter street are then played with that A's response.
    - Between: the best one-raid lookahead (it sees the next DECAY and the next CAPTURE phase)."""
    st = initial(leg)
    log = []
    for i in range(RAIDS):
        dec = []
        if i > 0:
            dec = decay_cells(leg, st)
            st = decay(leg, st)
        mid = i < RAIDS - 1
        best = None
        for cap in capture_plans(leg, st):
            s1 = capture_cells(leg, st, cap)
            cards = _cards(s1)
            hids = hand(leg, i, s1)
            cache = {}
            for place in placements(leg, i, s1):
                key = _place_key(place, cards, hids)
                ev = cache.get(key)
                if ev is None:
                    per = _best_per_cand(leg, i, s1, place, mid)
                    ev = sum(p[0] for p in per) / CANDIDATES
                    cache[key] = ev
                if best is None or ev > best[0] + EPS:
                    best = (ev, cap, s1, place)
        _, cap, s1, place = best
        per = _best_per_cand(leg, i, s1, place, mid)
        rd = leg.raids[i]
        k, b, h = rd.real, rd.real_b, rd.hunter_real
        _, resp, tab = per[k]
        ns, t = tab[sealed_b_options(k).index(b)][h]
        entry = _entry(i, cap, place, resp, k, b, h, hand(leg, i, s1), t, tier(s1, ns, t), ns, dec)
        log.append(entry)
        if ns.home_hp <= 0 or i == RAIDS - 1:
            return ns, log
        bb = None
        for opt in between_options(leg, ns):
            v = _next_value(leg, i + 1, between(leg, ns, *opt))
            if bb is None or v > bb[0] + EPS:
                bb = (v, opt)
        r, bld, inten = bb[1]
        entry["between"] = {"repair": r, "build": bld, "intensity": inten}
        st = between(leg, ns, r, bld, inten)
    return st, log


def _naive_place(leg: Leg, raid: int, st: State) -> dict:
    """L14 R9 naive: the first min(MAX_PLACED, live) non-wound hand cards in hand order, on live cells by descending
    value, then cell order."""
    vals = dict(leg.values)
    cards = _cards(st)
    live = _live(st)
    ids = [j for j in hand(leg, raid, st) if cards[j][1] != WOUND][:min(MAX_PLACED, len(live))]
    cells = sorted(live, key=lambda c: (-vals[c], ck(c)))
    return dict(zip(cells, ids))


def naive_leg(leg: Leg):
    """Per raid:
    - DECAY (raid > 0);
    - capture the highest value (first in cell order; again if extra_capture);
    - place the first hand cards on the most valuable cells; never ghost, respond or buy a hint.
    Between: repair the biggest affordable DOWN cell (free under NORMAL), build and clean nothing, NORMAL."""
    vals = dict(leg.values)
    st = initial(leg)
    log = []
    for i in range(RAIDS):
        dec = []
        if i > 0:
            dec = decay_cells(leg, st)
            st = decay(leg, st)
        cells = []
        cur = st
        for _ in range(1 + st.extra_capture):
            cap = None
            for c in capture_options(leg, cur):
                if cap is None or vals[c] > vals[cap]:
                    cap = c
            if cap is None:
                break
            cells.append(cap)
            cur = capture(leg, cur, cap)
        s1 = capture_cells(leg, st, cells)
        place = (_naive_place(leg, i, s1), None)
        rd = leg.raids[i]
        k, b, h = rd.real, rd.real_b, rd.hunter_real
        resp = ("HOLD",)
        ns, t = resolve(leg, i, s1, k, b, h, place, resp)
        entry = _entry(i, cells, place, resp, k, b, h, hand(leg, i, s1), t, tier(s1, ns, t), ns, dec)
        log.append(entry)
        if ns.home_hp <= 0 or i == RAIDS - 1:
            return ns, log
        rep = None
        for c, s in ns.owned:
            if s == DOWN and ns.bank >= repair_cost(leg, c, "NORMAL") and (rep is None or vals[c] > vals[rep]):
                rep = c
        entry["between"] = {"repair": rep, "build": None, "intensity": "NORMAL"}
        st = between(leg, ns, rep, None, "NORMAL")
    return st, log


def replay_befores(leg: Leg, log: list) -> list:
    """The post-capture state of every raid in a log (DECAY, then the CAPTURE phase, for raids after the first)."""
    st = initial(leg)
    out = []
    for x in log:
        if x["raid"] > 0:
            st = decay(leg, st)
        s1 = capture_cells(leg, st, x["capture"])
        out.append(s1)
        if x["between"]:
            b = x["between"]
            st = between(leg, x["after_raid"], b["repair"], b["build"], b["intensity"])
    return out


def cell_json(c):
    return c if c is None or c == HOME else [c[0], c[1]]


def state_json(st: State) -> dict:
    return {"heat": st.heat, "bank": st.bank, "home_hp": st.home_hp,
            "owned": [[c[0], c[1], s] for c, s in st.owned], "sentries": [[c[0], c[1], j] for c, j in st.sentries],
            "deck": [[i, t, v] for i, t, v in st.deck], "kit": dict(st.kit), "extra_capture": st.extra_capture}


def _outcome(touches, tr: str) -> tuple:
    """A comparable raid outcome: (touches, tier)."""
    return (tuple((tuple(c) if c != HOME else c, k) for c, k in touches), tr)


def _raid_metrics(leg: Leg, before: State, x: dict) -> tuple:
    """Metrics for one logged raid: (split, response decides, response decides table, hunter split, b split).
    - split: the A candidates' HOLD outcome tables (both B, both hunter streets) differ.
    - response decides: on the real (A, B, hunt), the chosen response's outcome differs from HOLD's.
    - response decides table: on the real A, it differs on at least one of the 4 (B, hunt) cells.
    - hunter split: on the real A and B, the 2 hunter streets give different HOLD outcomes.
    - b split: on the real A, the 2 B routes give different HOLD outcomes (over both hunter streets)."""
    place = (dict(x["place"]["sentries"]), x["place"]["ghost"])
    _, res = _grid(leg, x["raid"], before, place, [("HOLD",), x["response"]])
    tabs = [[tuple(tuple(_outcome(t, tier(before, s, t)) for s, t in outs) for outs in row[k]) for k in range(CANDIDATES)]
            for row in res]
    hold, chosen = tabs[0], tabs[1]
    split = len(set(hold)) > 1
    k, b, h = x["cand_real"], x["cand_b"], x["hunt"]
    bi = sealed_b_options(k).index(b)
    decides = _outcome(x["touches"], x["tier"]) != hold[k][bi][h]
    decides_table = chosen[k] != hold[k]
    hsplit = hold[k][bi][0] != hold[k][bi][1]
    bsplit = hold[k][0] != hold[k][1]
    return split, decides, decides_table, hsplit, bsplit


def _leg_stats(leg: Leg, end: State, log: list) -> dict:
    vals = dict(leg.values)
    ex = set(leg.exploits)
    befores = replay_befores(leg, log)
    launch = [b.heat + (GHOST_HEAT if x["place"]["ghost"] is not None else 0) for b, x in zip(befores, log)]
    caps = [c for x in log for c in x["capture"]]
    bw = [x["between"] for x in log if x["between"]]
    metrics = [_raid_metrics(leg, b, x) for b, x in zip(befores, log)]
    cut = any(decided(leg, x["raid"] + 1, x["after_raid"]) for x in log if x["between"])
    dead = 0
    for b, x in zip(befores, log):
        cards = _cards(b)
        dead += sum(1 for j in x["hand"] if cards[j][1] == WOUND)
    return {"score": score(leg, end), "breach": end.home_hp <= 0, "raids": len(log),
            "tiers": [x["tier"] for x in log],
            "blocks": sum(1 for x in log for _, k in x["touches"] if k == "block"),
            "shields": sum(1 for x in log for _, k in x["touches"] if k == "shielded"),
            "responses": [x["response"][0] for x in log],
            "ghosts": sum(x["place"]["ghost"] is not None for x in log),
            "ghost_home": sum(x["place"]["ghost"] == HOME for x in log),
            "cap_values": [vals[c] for c in caps], "cap_x": [c[0] for c in caps],
            "cap_exploits": sum(c in ex for c in caps),
            "double_caps": sum(len(x["capture"]) == 2 for x in log),
            "intensity": [b["intensity"] for b in bw], "builds": [b["build"] for b in bw],
            "repairs": sum(b["repair"] is not None for b in bw), "home_lost": HOME_HP - end.home_hp,
            "decayed": sum(len(x["decayed"]) for x in log),
            "taken_end": sum(s == TAKEN for _, s in end.owned), "down_end": sum(s == DOWN for _, s in end.owned),
            "extra_raids": sum(h >= EXTRA_AT for h in launch), "strong_raids": sum(h >= STRONG_AT for h in launch),
            "split": sum(m[0] for m in metrics), "decides": sum(m[1] for m in metrics),
            "decides_table": sum(m[2] for m in metrics),
            "hunter_split": sum(m[3] for m in metrics), "b_split": sum(m[4] for m in metrics),
            "redeploys": sum(x["response"][0] == "REDEPLOY" for x in log),
            "deploys": sum(x["response"][0] == "DEPLOY" for x in log),
            "jams": sum(x["response"][0] == "JAM" for x in log),
            "sacrifices": sum(x["response"][0] == "SACRIFICE" for x in log),
            "wounds_end": wound_count(end.deck), "dead_draws": dead,
            "cleans": sum(b["build"] == "CLEAN" for b in bw),
            "decided_cut": cut}


def _agg(rows: list, p: str) -> dict:
    raids = sum(r[p]["raids"] for r in rows)
    tiers = [t for r in rows for t in r[p]["tiers"]]
    resp = [x for r in rows for x in r[p]["responses"]]
    capv = [v for r in rows for v in r[p]["cap_values"]]
    capx = [x for r in rows for x in r[p]["cap_x"]]
    ints = [x for r in rows for x in r[p]["intensity"]]
    builds = [x for r in rows for x in r[p]["builds"]]
    return {"mean_score": round(stats.mean(r[p]["score"] for r in rows), 1),
            "mean_score_unbreached": round(stats.mean([r[p]["score"] for r in rows if not r[p]["breach"]] or [0]), 1),
            "breach_rate": sum(r[p]["breach"] for r in rows) / len(rows),
            "raids": raids, "blocks_per_raid": round(sum(r[p]["blocks"] for r in rows) / raids, 2),
            "shields": sum(r[p]["shields"] for r in rows),
            "response_use": {k: resp.count(k) for k in ("HOLD", "REDEPLOY", "DEPLOY", "SACRIFICE", "JAM")},
            "card_response_use": {k: resp.count(k) for k in CARD_RESPONSES},
            "ghost_per_raid": round(sum(r[p]["ghosts"] for r in rows) / raids, 2),
            "ghost_home": sum(r[p]["ghost_home"] for r in rows),
            "tier_mix": {t: tiers.count(t) for t in ("BREACHED", "DAMAGED", "EVADED", "BATTERED", "HOLDS")},
            "capture_mean_value": round(stats.mean(capv), 2) if capv else 0,
            "capture_x_mix": {str(x): capx.count(x) for x in range(W)},
            "capture_exploit_share": round(sum(r[p]["cap_exploits"] for r in rows) / max(1, len(capv)), 2),
            "intensity_mix": {k: ints.count(k) for k in INTENSITY},
            "hot_double_captures": sum(r[p]["double_caps"] for r in rows),
            "builds": {str(b): builds.count(b) for b in (None,) + BUILDS},
            "clean_use": sum(r[p]["cleans"] for r in rows),
            "repairs": sum(r[p]["repairs"] for r in rows),
            "home_lost": round(stats.mean(r[p]["home_lost"] for r in rows), 2),
            "decayed_per_leg": round(stats.mean(r[p]["decayed"] for r in rows), 2),
            "taken_end": round(stats.mean(r[p]["taken_end"] for r in rows), 2),
            "down_end": round(stats.mean(r[p]["down_end"] for r in rows), 2),
            "wounds_end": round(stats.mean(r[p]["wounds_end"] for r in rows), 2),
            "dead_draws": round(sum(r[p]["dead_draws"] for r in rows) / raids, 2),
            "extra_raid_share": round(sum(r[p]["extra_raids"] for r in rows) / raids, 2),
            "strong_raid_share": round(sum(r[p]["strong_raids"] for r in rows) / raids, 2),
            "split_raids": round(sum(r[p]["split"] for r in rows) / raids, 2),
            "response_decides": round(sum(r[p]["decides"] for r in rows) / raids, 2),
            "response_decides_table": round(sum(r[p]["decides_table"] for r in rows) / raids, 2),
            "hunter_split": round(sum(r[p]["hunter_split"] for r in rows) / raids, 2),
            "b_split": round(sum(r[p]["b_split"] for r in rows) / raids, 2),
            "redeploy_use": round(sum(r[p]["redeploys"] for r in rows) / raids, 2),
            "deploy_use": round(sum(r[p]["deploys"] for r in rows) / raids, 2),
            "jam_use": round(sum(r[p]["jams"] for r in rows) / raids, 2),
            "sacrifice_use": round(sum(r[p]["sacrifices"] for r in rows) / raids, 2),
            "decided_cuts": sum(r[p]["decided_cut"] for r in rows)}


if __name__ == "__main__":
    rows = []
    for seed in range(LEGS):
        leg = make_leg(seed)
        g_end, g_log = greedy_leg(leg)
        n_end, n_log = naive_leg(leg)
        row = {"seed": seed, "greedy": _leg_stats(leg, g_end, g_log), "naive": _leg_stats(leg, n_end, n_log)}
        row["gap"] = row["greedy"]["score"] - row["naive"]["score"]
        rows.append(row)
        print(json.dumps(row), flush=True)
    summ = {"legs": LEGS, "greedy": _agg(rows, "greedy"), "naive": _agg(rows, "naive"),
            "mean_gap": round(stats.mean(r["gap"] for r in rows), 1),
            "gap_share_ge3": sum(r["gap"] >= 3 for r in rows) / len(rows)}
    summ["decay"] = {p: {"decayed_per_leg": summ[p]["decayed_per_leg"], "taken_end": summ[p]["taken_end"]}
                     for p in ("greedy", "naive")}
    summ["l10"] = {p: {k: summ[p][k] for k in ("split_raids", "response_decides", "redeploy_use")}
                   for p in ("greedy", "naive")}
    summ["l11"] = {p: {k: summ[p][k] for k in ("split_raids", "response_decides", "deploy_use", "decided_cuts")}
                   for p in ("greedy", "naive")}
    summ["l13"] = {p: {k: summ[p][k] for k in ("sacrifice_use", "hunter_split", "intensity_mix", "hot_double_captures",
                                                "split_raids", "response_decides", "breach_rate", "mean_score")}
                   for p in ("greedy", "naive")}
    summ["l14"] = {p: {k: summ[p][k] for k in ("b_split", "wounds_end", "dead_draws", "clean_use",
                                                "card_response_use", "response_decides", "response_decides_table",
                                                "breach_rate", "mean_score")}
                   for p in ("greedy", "naive")}
    print("SUMMARY", json.dumps(summ), flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"config": config(), "summary": summ, "rows": rows}, f, indent=1)
