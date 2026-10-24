"""Lab round 8 (L8) rules oracle: the city raid (SPEC docs/handoff/raid_lab_l8/SPEC.md, designer 2026-10-23).

Rule changes applied in place:
- L9 (docs/handoff/raid_lab_l8/L9_CHANGES.md): DECAY and SENTRY_PRICE 3.
- L10 (docs/handoff/raid_lab_l8/L10_CHANGES.md): POOL_START D1 N1 E0, and new SUMMARY metrics.
- L11 (docs/handoff/raid_lab_l8/L11_CHANGES.md): MAX_PLACED 2 (the rest of the pool is the reserve), the DEPLOY
  response, a lost district returns its sentry to the pool, safe_next, and new SUMMARY metrics.
- L13 (docs/handoff/raid_lab_l8/L13_RULES.md):
  - R2: the hunter street is a second sealed unknown (hunter_cands, hunter_real).
  - R3: the SACRIFICE response.
  - R4: Heat bands in the score, and HOME_LOSS_COST 15.
  - R5: intensity perks (NORMAL: free repair; HOT: two captures next raid).

The map
- A 4 x 3 grid of districts between our HQ (HOME, off-grid at x = -1) and the corp HQ (off-grid at x = 4).
- Rows y = 0..2 are the three ROUTES (north, mid, south). Columns x = 0..3 are the STREETS.
- Each cell has a value v in {4, 6, 8, 10, 12}. 3 cells with x >= 1 carry an EXPLOIT.
- Ownership per cell: NEUTRAL (absent from `owned`), or owned with a status OK / DOWN / TAKEN.
  TAKEN is corp ground for the rest of the leg.
- At leg start we own 2 seeded x = 0 cells (OK).

A leg is 3 raids
- DECAY (every raid after the first, before CAPTURE): every owned cell still DOWN becomes TAKEN. Its sentry leaves the
  placement and goes back to the pool (the pool count is unchanged).
- CAPTURE: claim 1 NEUTRAL cell orthogonally adjacent to an owned non-TAKEN cell, or a cell at x = 0. It works on the
  decayed state.
  - L13 R5: if extra_capture > 0 (set by HOT), claim a second cell from the updated options. Then extra_capture is
    cleared.
- PLAN: place min(pool, live cells, MAX_PLACED = 2) sentries (at most 1 per owned non-TAKEN cell). The pool sentries
  not placed are the RESERVE. Optionally a ghost (kit) on an owned non-TAKEN cell or HOME, for +5 Heat.
- LAUNCH, in order:
  - beam 1;
  - extra 1 (Heat >= 50) and extra 2 (Heat >= 75), using launch Heat with the ghost;
  - the REVEAL of the sealed route;
  - the RESPONSE (chosen without knowing the hunter street);
  - the sealed beam;
  - the HUNTER REVEAL;
  - the hunter.
- BETWEEN (not after raid 3):
  - repair <= 1 DOWN cell (v // 2, free under NORMAL);
  - build <= 1 sentry (3);
  - pick an intensity.
  - Income and Heat are added after that, then the perk flag (HOT: extra_capture = 1).

Beams
- Every beam is typed (D drone, N netrunner, E enforcer) and runs along a line.
  - A ROUTE runs x = 3 -> 0, then reaches HOME.
  - A STREET runs y 0 -> 2 or 2 -> 0 and never reaches HOME.
- The sealed beam is one of the three routes, each carrying a distinct type (a seeded permutation). The real
  candidate is seeded.
- L13 R2: the hunter (typed) runs street(hunter_cands[hunter_real], down) unless JAMMED. The two hunter streets are
  drawn by random.Random(9100 + 13 * seed + raid). The first-touch rule is gone.

Scanning a line
- A ghosted cell: pass.
- A sentry of the beam's type: BLOCK. The line stops, so a stopped route never reaches HOME.
- An owned live cell not yet hit this raid: HIT (OK -> DOWN, DOWN -> TAKEN; a TAKEN cell's sentry leaves the
  placement and returns to the pool).
- Otherwise: pass.
- At the end of a route, unless HOME is ghosted or was already hit this raid:
  - HOME -1;
  - after a SACRIFICE, HOME is unharmed instead and the touch is ("HOME", "shielded").
- No touches at all (and no SACRIFICE) = EVADED: Heat -10.

Response (after the reveal; REDEPLOY / DEPLOY / JAM cost a spoof charge + 2 Heat after the sweep)
- HOLD.
- REDEPLOY s -> c (applies to the sealed beam and the hunter).
- DEPLOY t -> c: a reserve sentry of type t onto an owned live cell with no sentry. It stays placed after the raid.
- SACRIFICE c (L13 R3; no spoof, no Heat):
  - an owned live cell becomes TAKEN now, and its sentry returns to the pool;
  - HOME cannot lose integrity for the rest of this raid.
- JAM (no hunter).
- Order: HOLD, every REDEPLOY, every DEPLOY (types D, N, E, then target cells in cell order), every SACRIFICE (cell
  order), JAM.

safe_next (L11)
- True if some capture, then some placement, with the best response per sealed candidate, keeps HOME above 0 on
  every candidate of the given raid. It takes the post-decay state; True when raid >= RAIDS.

Score (L13 R4)
- bank + sum(v - (v // 2 if DOWN)) over owned non-TAKEN cells
- + 6 per owned non-TAKEN EXPLOIT cell
- - 15 per HOME lost
- - 0.5 per Heat above 44
- - 6 if Heat >= 50
- - 6 if Heat >= 75
- A breach scores -100.

Measured (python sweep_l8.py)
- Greedy against naive, over 20 legs. Greedy plays each phase to maximize EV over 3 sealed candidates x 2 hunter
  streets, with the best response per sealed candidate, and values kit at KIT_VALUE mid-leg.
- Per player:
  - split_raids, response_decides, redeploy_use, deploy_use, decided_cuts;
  - L13: sacrifice_use, hunter_split, intensity_mix, hot_double_captures."""
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

# Cell statuses.
HOME = "HOME"
OK, DOWN, TAKEN = "OK", "DOWN", "TAKEN"
LIVE = (OK, DOWN)

# Economy and Heat.
START_BANK, START_HEAT = 10, 44
EXTRA_AT, STRONG_AT = 50, 75
HOME_HP = 3
GHOST_HEAT, SPOOF_HEAT, EVADE_HEAT = 5, 2, 10
SENTRY_PRICE = 3    # L9 (was 4)
POOL_START = (("D", 1), ("N", 1), ("E", 0))    # L10 (was 1/1/1): one sealed route is always uncovered
MAX_PLACED = 2      # L11: PLAN places at most 2 sentries; the rest of the pool is the reserve
KIT_START = (("ghost", 2), ("spoof", 2))
INTENSITY = {"LOW": (6, 0.5), "NORMAL": (12, 1.0), "HOT": (18, 1.5)}
PERKS = {"LOW": None, "NORMAL": "FREE_REPAIR", "HOT": "EXTRA_CAPTURE"}    # L13 R5
DECAY = True        # L9: DOWN -> TAKEN at the start of every raid after the first, before CAPTURE

# Responses that cost a spoof charge (+ SPOOF_HEAT). SACRIFICE is free (L13 R3).
SPOOF_RESPONSES = ("REDEPLOY", "DEPLOY", "JAM")

# Score.
EXPLOIT_BONUS, HOME_LOSS_COST, HEAT_CARRY, BREACH = 6, 15, 0.5, 100    # L13 R4: HOME 15 (was 8), carry 0.5 (was 1.0)
HEAT_BAND = 6       # L13 R4: -6 at Heat >= EXTRA_AT, another -6 at Heat >= STRONG_AT
KIT_VALUE = 2.5     # planner heuristic only: an unspent kit item (ghost, spoof, pool sentry) mid-leg
EPS = 1e-9          # float ties keep the earlier option
OUT = r"D:/rc_tmp/raid_design_lab/sweep_l13.json"


def ck(c) -> tuple:
    """Sort key: cell order y then x."""
    return (c[1], c[0])


def config() -> dict:
    return {"W": W, "H": H, "TYPES": list(TYPES), "VALUES": list(VALUES), "EXPLOITS": EXPLOITS, "START_CELLS": START_CELLS,
            "RAIDS": RAIDS, "HUNTER_CANDS": HUNTER_CANDS, "HUNTER_SEED": HUNTER_SEED,
            "START_BANK": START_BANK, "START_HEAT": START_HEAT, "EXTRA_AT": EXTRA_AT,
            "STRONG_AT": STRONG_AT, "HOME_HP": HOME_HP, "GHOST_HEAT": GHOST_HEAT, "SPOOF_HEAT": SPOOF_HEAT,
            "EVADE_HEAT": EVADE_HEAT, "SENTRY_PRICE": SENTRY_PRICE, "POOL_START": dict(POOL_START),
            "MAX_PLACED": MAX_PLACED,
            "KIT_START": dict(KIT_START), "INTENSITY": {k: list(v) for k, v in INTENSITY.items()},
            "PERKS": dict(PERKS),
            "EXPLOIT_BONUS": EXPLOIT_BONUS, "HOME_LOSS_COST": HOME_LOSS_COST, "HEAT_CARRY": HEAT_CARRY,
            "HEAT_BAND": HEAT_BAND, "BREACH": BREACH, "KIT_VALUE": KIT_VALUE, "DECAY": DECAY}


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
    real: int               # the corp's real sealed candidate
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
    sentries: tuple = ()    # ((cell, type), ...) in cell order: the last placement (with any DEPLOY)
    pool: tuple = POOL_START    # every sentry owned, placed or in reserve
    kit: tuple = KIT_START
    extra_capture: int = 0  # L13 R5: HOT sets 1; the next CAPTURE phase takes a second cell and clears it


def _otup(d: dict) -> tuple:
    return tuple(sorted(d.items(), key=lambda kv: ck(kv[0])))


def _pool_t(d: dict) -> tuple:
    return tuple((t, d[t]) for t in TYPES)


def _kit_t(d: dict) -> tuple:
    return (("ghost", d["ghost"]), ("spoof", d["spoof"]))


def _live(st: State) -> list:
    return [c for c, s in st.owned if s in LIVE]


def _reserve(pool: dict, sent: dict, t: str) -> int:
    """Pool sentries of type t not in the placement `sent`."""
    return pool[t] - sum(1 for v in sent.values() if v == t)


def _rand_line(rng: random.Random) -> Line:
    """Draw order (stable): kind, index, direction (streets only), type."""
    if rng.random() < 0.5:
        y = rng.randrange(H)
        return route(y, rng.choice(TYPES))
    x = rng.randrange(W)
    down = rng.random() < 0.5
    return street(x, down, rng.choice(TYPES))


def make_leg(seed: int) -> Leg:
    """Seeded leg; the draw order is fixed, so a seed always gives the same leg. The L13 hunter streets come from their
    own per-raid rng, so every other draw is unchanged (the old hunter_street draw is still made and discarded)."""
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
        raids.append(Raid(b1, e1, e2, tuple(perm), tuple(route(k, perm[k]) for k in range(CANDIDATES)), real, ht,
                          hc, hreal))
    return Leg(seed, values, exploits, start, tuple(raids))


def initial(leg: Leg) -> State:
    return State(owned=tuple((c, OK) for c in leg.start))


def decay_cells(leg: Leg, st: State) -> list:
    """The owned cells DECAY turns TAKEN (status still DOWN), in cell order."""
    return [c for c, s in st.owned if s == DOWN]


def decay(leg: Leg, st: State) -> State:
    """L9 DECAY, applied at the start of every raid after the first, before CAPTURE: every owned DOWN cell becomes
    TAKEN. L11: its sentry leaves the placement and returns to the pool (pool counts unchanged). The caller decides
    when (raid > 0)."""
    owned = dict(st.owned)
    sent = dict(st.sentries)
    for c in decay_cells(leg, st):
        owned[c] = TAKEN
        sent.pop(c, None)
    return replace(st, owned=_otup(owned), sentries=_otup(sent))


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


def placements(leg: Leg, st: State):
    """Yields (sentries {cell: type}, ghost) with min(pool, live cells, MAX_PLACED) sentries placed (L11 cap; the rest
    is the reserve). Distinct maps only (same-type sentries are not permuted), in the established DFS order (cells in
    cell order, types D, N, E, then skip). Ghost order: None, HOME, then live cells."""
    live = _live(st)
    left = dict(st.pool)
    need = min(sum(left.values()), len(live), MAX_PLACED)
    maps = []

    def rec(idx: int, cur: dict, k: int):
        if k == 0:
            maps.append(dict(cur))
            return
        if len(live) - idx < k:
            return
        c = live[idx]
        for t in TYPES:
            if left[t] > 0:
                left[t] -= 1
                cur[c] = t
                rec(idx + 1, cur, k - 1)
                del cur[c]
                left[t] += 1
        rec(idx + 1, cur, k)

    rec(0, {}, need)
    ghosts = [None] + (([HOME] + live) if dict(st.kit)["ghost"] > 0 else [])
    for g in ghosts:
        for m in maps:
            yield (dict(m), g)


def _check_place(st: State, place) -> None:
    sent, ghost = place
    live = set(_live(st))
    if len(sent) > MAX_PLACED:
        raise ValueError(f"more than {MAX_PLACED} sentries placed")
    counts = {t: 0 for t in TYPES}
    for c, t in sent.items():
        if c not in live or t not in TYPES:
            raise ValueError(f"illegal sentry {c} {t}")
        counts[t] += 1
    pool = dict(st.pool)
    if any(counts[t] > pool[t] for t in TYPES):
        raise ValueError("more sentries than the pool")
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
    """One raid's mutable sweep: board, sentries, seen cells, HOME, the SACRIFICE shield, and the trace
    [(beam, cell, kind)]."""
    __slots__ = ("sent", "ghost", "owned", "hp", "home_hit", "shield", "seen", "trace")

    def __init__(self, st: State, place):
        self.sent = dict(place[0])
        self.ghost = place[1]
        self.owned = dict(st.owned)
        self.hp = st.home_hp
        self.home_hit = False
        self.shield = False
        self.seen = set()
        self.trace = []

    def copy(self) -> "_Sweep":
        o = _Sweep.__new__(_Sweep)
        o.sent = dict(self.sent)
        o.ghost = self.ghost
        o.owned = dict(self.owned)
        o.hp = self.hp
        o.home_hit = self.home_hit
        o.shield = self.shield
        o.seen = set(self.seen)
        o.trace = list(self.trace)
        return o

    def scan(self, name: str, ln: Line) -> None:
        for c in ln.cells:
            if c == self.ghost:
                continue
            if self.sent.get(c) == ln.type:
                self.trace.append((name, c, "block"))
                return
            s = self.owned.get(c)
            if s in LIVE and c not in self.seen:
                if s == OK:
                    self.owned[c] = DOWN
                else:
                    self.owned[c] = TAKEN
                    self.sent.pop(c, None)      # L11: the sentry returns to the pool (count unchanged)
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
    """Beam 1 and the extras (before the reveal). Returns (raid, launch heat, sweep)."""
    _check_place(st, place)
    rd = leg.raids[raid]
    heat = st.heat + (GHOST_HEAT if place[1] is not None else 0)
    sw = _Sweep(st, place)
    sw.scan("beam1", rd.b1)
    if heat >= EXTRA_AT:
        sw.scan("extra1", rd.extra1)
    if heat >= STRONG_AT:
        sw.scan("extra2", rd.extra2)
    return rd, heat, sw


def _respond(st: State, sw: _Sweep, resp: tuple) -> None:
    """Apply a canonical response to a sweep after beam 1 and the extras (validates it)."""
    if resp[0] in SPOOF_RESPONSES and dict(st.kit)["spoof"] <= 0:
        raise ValueError("no spoof charge")
    if resp[0] == "REDEPLOY":
        s, c = resp[1], resp[2]
        if s not in sw.sent or c == s or c in sw.sent or sw.owned.get(c) not in LIVE:
            raise ValueError(f"illegal redeploy {s} -> {c}")
        sw.sent[c] = sw.sent.pop(s)
    elif resp[0] == "DEPLOY":
        t, c = resp[1], resp[2]
        if t not in TYPES or _reserve(dict(st.pool), sw.sent, t) <= 0 or c in sw.sent or sw.owned.get(c) not in LIVE:
            raise ValueError(f"illegal deploy {t} -> {c}")
        sw.sent[c] = t
    elif resp[0] == "SACRIFICE":
        c = resp[1]
        if sw.owned.get(c) not in LIVE:
            raise ValueError(f"illegal sacrifice {c}")
        sw.owned[c] = TAKEN
        sw.sent.pop(c, None)                    # L11: the sentry returns to the pool (count unchanged)
        sw.shield = True


def _close(st: State, place, heat: int, sw: _Sweep, resp: tuple) -> State:
    """The state after a finished sweep: EVADED Heat (no touches and no SACRIFICE), spoof cost, ghost spent."""
    kit = dict(st.kit)
    if not sw.trace and not sw.shield:
        heat -= EVADE_HEAT
    if resp[0] in SPOOF_RESPONSES:
        heat += SPOOF_HEAT
        kit["spoof"] -= 1
    if place[1] is not None:
        kit["ghost"] -= 1
    return State(heat, st.bank, sw.hp, _otup(sw.owned), _otup(sw.sent), st.pool, _kit_t(kit), st.extra_capture)


def _hunter_street(rd: Raid, hunt: int) -> Line:
    return street(rd.hunter_cands[hunt], True, rd.hunter_type)


def _resolve(leg: Leg, raid: int, st: State, cand: int, hunt: int, place, response):
    resp = norm_response(response)
    if hunt not in range(HUNTER_CANDS) or cand not in range(CANDIDATES):
        raise ValueError(f"illegal cand/hunt {cand} {hunt}")
    rd, heat, sw = _launch(leg, raid, st, place)
    _respond(st, sw, resp)
    sw.scan("sealed", rd.cands[cand])
    if resp[0] != "JAM":
        sw.scan("hunter", _hunter_street(rd, hunt))
    return _close(st, place, heat, sw, resp), sw.trace


def resolve(leg: Leg, raid: int, st: State, cand: int, hunt: int, place, response=None):
    """One raid (raid = index into leg.raids) from the post-capture state.
    - cand: the sealed route; hunt: the index into hunter_cands.
    - place = (sentries {cell: type}, ghost).
    - response: any legal response.
    Returns (state after the raid, touches [(cell | "HOME", "hit" | "block" | "home" | "shielded")])."""
    ns, tr = _resolve(leg, raid, st, cand, hunt, place, response)
    return ns, [(c, k) for _, c, k in tr]


def trace(leg: Leg, raid: int, st: State, cand: int, hunt: int, place, response=None) -> list:
    """The touches with their beam: [(beam, cell, kind)], beam in beam1/extra1/extra2/sealed/hunter (lab cues)."""
    return _resolve(leg, raid, st, cand, hunt, place, response)[1]


def hunter_line(leg: Leg, raid: int, st: State, cand: int, hunt: int, place, response=None) -> Line | None:
    """The street the hunter runs: hunter_cands[hunt], top to bottom (None when JAMMED)."""
    resp = norm_response(response)
    if resp[0] == "JAM":
        return None
    return _hunter_street(leg.raids[raid], hunt)


def _options_from(st: State, sw: _Sweep) -> list:
    """Response options read from a sweep after beam 1 and the extras (see response_options)."""
    out = [("HOLD",)]
    spoof = dict(st.kit)["spoof"] > 0
    live = [c for c in CELLS if sw.owned.get(c) in LIVE]
    if spoof:
        targets = [c for c in live if c not in sw.sent]
        for s in sorted(sw.sent, key=ck):
            for c in targets:
                if c != s:
                    out.append(("REDEPLOY", s, c))
        pool = dict(st.pool)
        for t in TYPES:
            if _reserve(pool, sw.sent, t) > 0:
                for c in targets:
                    out.append(("DEPLOY", t, c))
    for c in live:
        out.append(("SACRIFICE", c))
    if spoof:
        out.append(("JAM",))
    return out


def response_options(leg: Leg, raid: int, st: State, cand: int, place) -> list:
    """In order:
    - HOLD;
    - with a spoof charge: every REDEPLOY (source by cell order, then target);
    - with a spoof charge: every DEPLOY (types D, N, E with a reserve sentry, then target in cell order);
    - every SACRIFICE (owned live cells in cell order; no spoof needed);
    - with a spoof charge: JAM.
    Legality is read after beam 1 and the extras."""
    _, _, sw = _launch(leg, raid, st, place)
    return _options_from(st, sw)


def _grid(leg: Leg, raid: int, st: State, place, opts=None, prune: bool = False):
    """Fast batch resolve sharing one launch: (opts, res), res[i][k][h] = (state, touches) for response opts[i],
    sealed candidate k and hunter street h. opts=None uses response_options.
    prune=True (planner only) puts None for SACRIFICE rows that can't beat HOLD. Such a row is never chosen
    (HOLD is earlier and >=). The cases: HOME is ghosted, HOME was already hit before the response, or HOLD on that
    candidate keeps HOME."""
    rd, heat, sw0 = _launch(leg, raid, st, place)
    if opts is None:
        opts = _options_from(st, sw0)
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
        _respond(st, sw1, r)
        row = []
        for k in range(CANDIDATES):
            if sac and prune and hold_safe is not None and hold_safe[k]:
                row.append(None)
                continue
            sw2 = sw1.copy()
            sw2.scan("sealed", rd.cands[k])
            outs = []
            for h in range(HUNTER_CANDS):
                sw3 = sw2.copy() if h < HUNTER_CANDS - 1 else sw2
                if r[0] != "JAM":
                    sw3.scan("hunter", hunters[h])
                outs.append((_close(st, place, heat, sw3, r), [(c, kd) for _, c, kd in sw3.trace]))
            row.append(outs)
        if r[0] == "HOLD" and hold_safe is None:
            hold_safe = [row[k][0][0].home_hp >= sw0.hp for k in range(CANDIDATES)]
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
    """Leg score (L13 R4 Heat bands); mid=True adds KIT_VALUE per unspent ghost, spoof and pool sentry (planner
    heuristic only)."""
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
    if mid:
        s += KIT_VALUE * (sum(v for _, v in st.kit) + sum(v for _, v in st.pool))
    return s


def repair_cost(leg: Leg, cell, intensity: str) -> int:
    """v // 2, or 0 under the NORMAL perk (L13 R5)."""
    if PERKS[intensity] == "FREE_REPAIR":
        return 0
    return dict(leg.values)[tuple(cell)] // 2


def between(leg: Leg, st: State, repair=None, build=None, intensity: str = "NORMAL") -> State:
    """In order:
    1. repair (<= 1 DOWN cell, v // 2, free under NORMAL);
    2. build (<= 1 sentry, SENTRY_PRICE);
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
    pool = dict(st.pool)
    if build is not None and build in TYPES and bank >= SENTRY_PRICE:
        bank -= SENTRY_PRICE
        pool[build] += 1
    dh, mult = INTENSITY[intensity]
    income = int(sum(vals[c] // 3 for c, s in owned.items() if s == OK) * mult)
    extra = 1 if PERKS[intensity] == "EXTRA_CAPTURE" else st.extra_capture
    return State(st.heat + dh, bank + income, st.home_hp, _otup(owned), st.sentries, _pool_t(pool), st.kit, extra)


def between_options(leg: Leg, st: State):
    """Yields (repair, build, intensity), all affordable under that intensity (NORMAL repairs free): repair None then
    DOWN cells (cell order); build None then D, N, E; intensity LOW, NORMAL, HOT."""
    downs = [c for c, s in st.owned if s == DOWN]
    for r in [None] + downs:
        for b in [None] + list(TYPES):
            for inten in INTENSITY:
                cost = repair_cost(leg, r, inten) if r is not None else 0
                if st.bank < cost:
                    continue
                if b is not None and st.bank - cost < SENTRY_PRICE:
                    continue
                yield (r, b, inten)


def safe_next(leg: Leg, raid: int, st: State) -> bool:
    """L11: True if some CAPTURE phase (capture_plans), then some placement, with the best response per sealed
    candidate, keeps HOME above 0 on every sealed candidate of raid `raid`. `st` is the post-decay state (the caller
    applies DECAY). True when raid >= RAIDS.
    - The hunter runs a street and never reaches HOME, so the hunter street does not matter (hunt 0 is used).
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
        for place in placements(leg, s1):
            opts = response_options(leg, raid, s1, 0, place)
            if all(any(resolve(leg, raid, s1, k, 0, place, r)[0].home_hp > 0 for r in opts) for k in range(CANDIDATES)):
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


def _best_per_cand(leg: Leg, raid: int, st: State, place, mid: bool) -> list:
    """Per sealed candidate: (value = mean over the 2 hunter streets, best response, [(after, touches) per hunt]).
    The response is chosen before the hunter reveal; the earliest response is kept on ties."""
    opts, res = _grid(leg, raid, st, place, None, prune=True)
    per = []
    for k in range(CANDIDATES):
        best = None
        for i, r in enumerate(opts):
            outs = res[i][k]
            if outs is None:
                continue
            v = sum(score(leg, s, mid) for s, _ in outs) / HUNTER_CANDS
            if best is None or v > best[0] + EPS:
                best = (v, r, outs)
        per.append(best)
    return per


def forecast(leg: Leg, raid: int, st: State, place) -> list:
    """L13 R2: per sealed candidate, {cand, outcomes: [HOLD result for hunt 0, HOLD result for hunt 1]}, each
    {state, touches, tier}."""
    _, res = _grid(leg, raid, st, place, [("HOLD",)])
    return [{"cand": k, "outcomes": [{"state": s, "touches": t, "tier": tier(st, s, t)} for s, t in res[0][k]]}
            for k in range(CANDIDATES)]


def _next_value(leg: Leg, raid: int, st: State) -> float:
    """Between-step lookahead:
    - DECAY (raid > 0);
    - the best CAPTURE phase (so HOT's double capture counts);
    - then the next raid's best EV over 3 x 2 outcomes, with no ghost and HOLD."""
    if raid > 0:
        st = decay(leg, st)
    mid = raid < RAIDS - 1
    best = None
    for cap in capture_plans(leg, st):
        s1 = capture_cells(leg, st, cap)
        for place in placements(leg, s1):
            if place[1] is not None:
                break       # ghost placements come after every no-ghost placement
            _, res = _grid(leg, raid, s1, place, [("HOLD",)])
            ev = sum(score(leg, s, mid) for outs in res[0] for s, _ in outs) / (CANDIDATES * HUNTER_CANDS)
            if best is None or ev > best + EPS:
                best = ev
    return best if best is not None else score(leg, st, mid)


def _entry(i, cap, place, resp, k, h, touches, tr, after, decayed=()) -> dict:
    return {"raid": i, "decayed": list(decayed), "capture": [tuple(c) for c in cap],
            "place": {"sentries": dict(place[0]), "ghost": place[1]}, "response": resp,
            "cand_real": k, "hunt": h, "touches": touches, "tier": tr, "after_raid": after, "between": None}


def greedy_leg(leg: Leg):
    """Per raid:
    - DECAY (raid > 0).
    - The CAPTURE phase and the plan jointly maximize the EV over 3 sealed candidates x 2 hunter streets, with the
      best response per sealed candidate (kit valued mid-leg).
    - The real candidate and hunter street are then played with that candidate's response.
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
            for place in placements(leg, s1):
                per = _best_per_cand(leg, i, s1, place, mid)
                ev = sum(p[0] for p in per) / CANDIDATES
                if best is None or ev > best[0] + EPS:
                    best = (ev, cap, s1, place, per)
        _, cap, s1, place, per = best
        rd = leg.raids[i]
        k, h = rd.real, rd.hunter_real
        _, resp, outs = per[k]
        ns, t = outs[h]
        entry = _entry(i, cap, place, resp, k, h, t, tier(s1, ns, t), ns, dec)
        log.append(entry)
        if ns.home_hp <= 0 or i == RAIDS - 1:
            return ns, log
        bb = None
        for opt in between_options(leg, ns):
            v = _next_value(leg, i + 1, between(leg, ns, *opt))
            if bb is None or v > bb[0] + EPS:
                bb = (v, opt)
        r, b, inten = bb[1]
        entry["between"] = {"repair": r, "build": b, "intensity": inten}
        st = between(leg, ns, r, b, inten)
    return st, log


def _naive_sentries(st: State) -> dict:
    """Keep pool sentries where they were (cell order, at most MAX_PLACED); fill up to MAX_PLACED on the first free
    live cells (cell order, type order)."""
    live = _live(st)
    left = dict(st.pool)
    out = {}
    for c, t in st.sentries:
        if len(out) >= MAX_PLACED:
            break
        if c in live and left[t] > 0:
            out[c] = t
            left[t] -= 1
    free = [c for c in live if c not in out]
    rest = [t for t in TYPES for _ in range(left[t])]
    for c, t in zip(free, rest):
        if len(out) >= MAX_PLACED:
            break
        out[c] = t
    return out


def naive_leg(leg: Leg):
    """Per raid:
    - DECAY (raid > 0);
    - capture the highest value (first in cell order; again if extra_capture);
    - keep sentries; never ghost or respond.
    Between: repair the biggest affordable DOWN cell (free under NORMAL), build nothing, NORMAL."""
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
        place = (_naive_sentries(s1), None)
        rd = leg.raids[i]
        k, h = rd.real, rd.hunter_real
        resp = ("HOLD",)
        ns, t = resolve(leg, i, s1, k, h, place, resp)
        entry = _entry(i, cells, place, resp, k, h, t, tier(s1, ns, t), ns, dec)
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
            "owned": [[c[0], c[1], s] for c, s in st.owned], "sentries": [[c[0], c[1], t] for c, t in st.sentries],
            "pool": dict(st.pool), "kit": dict(st.kit), "extra_capture": st.extra_capture}


def _outcome(touches, tr: str) -> tuple:
    """A comparable raid outcome: (touches, tier)."""
    return (tuple((tuple(c) if c != HOME else c, k) for c, k in touches), tr)


def _raid_metrics(leg: Leg, before: State, x: dict) -> tuple:
    """Metrics for one logged raid: (split, response decides, hunter split).
    - split: the candidates' HOLD outcome pairs (both hunter streets) differ.
    - response decides: on the real candidate and hunter street, the chosen response's outcome differs from HOLD's.
    - hunter split: on the real candidate, the 2 hunter streets give different HOLD outcomes."""
    place = (dict(x["place"]["sentries"]), x["place"]["ghost"])
    _, res = _grid(leg, x["raid"], before, place, [("HOLD",)])
    outs = [tuple(_outcome(t, tier(before, s, t)) for s, t in res[0][k]) for k in range(CANDIDATES)]
    split = len(set(outs)) > 1
    k, h = x["cand_real"], x["hunt"]
    decides = _outcome(x["touches"], x["tier"]) != outs[k][h]
    hsplit = outs[k][0] != outs[k][1]
    return split, decides, hsplit


def _leg_stats(leg: Leg, end: State, log: list) -> dict:
    vals = dict(leg.values)
    ex = set(leg.exploits)
    befores = replay_befores(leg, log)
    launch = [b.heat + (GHOST_HEAT if x["place"]["ghost"] is not None else 0) for b, x in zip(befores, log)]
    caps = [c for x in log for c in x["capture"]]
    bw = [x["between"] for x in log if x["between"]]
    metrics = [_raid_metrics(leg, b, x) for b, x in zip(befores, log)]
    cut = any(decided(leg, x["raid"] + 1, x["after_raid"]) for x in log if x["between"])
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
            "hunter_split": sum(m[2] for m in metrics),
            "redeploys": sum(x["response"][0] == "REDEPLOY" for x in log),
            "deploys": sum(x["response"][0] == "DEPLOY" for x in log),
            "sacrifices": sum(x["response"][0] == "SACRIFICE" for x in log),
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
            "ghost_per_raid": round(sum(r[p]["ghosts"] for r in rows) / raids, 2),
            "ghost_home": sum(r[p]["ghost_home"] for r in rows),
            "tier_mix": {t: tiers.count(t) for t in ("BREACHED", "DAMAGED", "EVADED", "BATTERED", "HOLDS")},
            "capture_mean_value": round(stats.mean(capv), 2) if capv else 0,
            "capture_x_mix": {str(x): capx.count(x) for x in range(W)},
            "capture_exploit_share": round(sum(r[p]["cap_exploits"] for r in rows) / max(1, len(capv)), 2),
            "intensity_mix": {k: ints.count(k) for k in INTENSITY},
            "hot_double_captures": sum(r[p]["double_caps"] for r in rows),
            "builds": {str(b): builds.count(b) for b in (None,) + TYPES},
            "repairs": sum(r[p]["repairs"] for r in rows),
            "home_lost": round(stats.mean(r[p]["home_lost"] for r in rows), 2),
            "decayed_per_leg": round(stats.mean(r[p]["decayed"] for r in rows), 2),
            "taken_end": round(stats.mean(r[p]["taken_end"] for r in rows), 2),
            "down_end": round(stats.mean(r[p]["down_end"] for r in rows), 2),
            "extra_raid_share": round(sum(r[p]["extra_raids"] for r in rows) / raids, 2),
            "strong_raid_share": round(sum(r[p]["strong_raids"] for r in rows) / raids, 2),
            "split_raids": round(sum(r[p]["split"] for r in rows) / raids, 2),
            "response_decides": round(sum(r[p]["decides"] for r in rows) / raids, 2),
            "hunter_split": round(sum(r[p]["hunter_split"] for r in rows) / raids, 2),
            "redeploy_use": round(sum(r[p]["redeploys"] for r in rows) / raids, 2),
            "deploy_use": round(sum(r[p]["deploys"] for r in rows) / raids, 2),
            "sacrifice_use": round(sum(r[p]["sacrifices"] for r in rows) / raids, 2),
            "decided_cuts": sum(r[p]["decided_cut"] for r in rows)}


if __name__ == "__main__":
    rows = []
    for seed in range(20):
        leg = make_leg(seed)
        g_end, g_log = greedy_leg(leg)
        n_end, n_log = naive_leg(leg)
        row = {"seed": seed, "greedy": _leg_stats(leg, g_end, g_log), "naive": _leg_stats(leg, n_end, n_log)}
        row["gap"] = row["greedy"]["score"] - row["naive"]["score"]
        rows.append(row)
        print(json.dumps(row), flush=True)
    summ = {"greedy": _agg(rows, "greedy"), "naive": _agg(rows, "naive"),
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
    print("SUMMARY", json.dumps(summ), flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"config": config(), "summary": summ, "rows": rows}, f, indent=1)
