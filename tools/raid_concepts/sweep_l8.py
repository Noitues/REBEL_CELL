"""Lab round 8 (L8) rules oracle: the city raid (SPEC docs/handoff/raid_lab_l8/SPEC.md, designer 2026-10-23).

Rule changes applied in place:
- L9 (docs/handoff/raid_lab_l8/L9_CHANGES.md): DECAY and SENTRY_PRICE 3.
- L10 (docs/handoff/raid_lab_l8/L10_CHANGES.md): POOL_START D1 N1 E0, and new SUMMARY metrics.
- L11 (docs/handoff/raid_lab_l8/L11_CHANGES.md): MAX_PLACED 2 (the rest of the pool is the reserve), the DEPLOY
  response, a lost district returns its sentry to the pool, safe_next, and new SUMMARY metrics.

The map
- A 4 x 3 grid of districts between our HQ (HOME, off-grid at x = -1) and the corp HQ (off-grid at x = 4).
- Rows y = 0..2 are the three ROUTES (north, mid, south). Columns x = 0..3 are the STREETS.
- Each cell has a value v in {4, 6, 8, 10, 12}. 3 cells with x >= 1 carry an EXPLOIT.
- Ownership per cell: NEUTRAL (absent from `owned`), or owned with a status OK / DOWN / TAKEN.
  TAKEN is corp ground for the rest of the leg.
- At leg start we own 2 seeded x = 0 cells (OK).

A leg is 3 raids
- DECAY (L9; every raid after the first, before CAPTURE): every owned cell still DOWN becomes TAKEN. L11: its sentry
  leaves the placement and goes back to the pool (the pool count is unchanged).
- CAPTURE: claim 1 NEUTRAL cell orthogonally adjacent to an owned non-TAKEN cell, or a cell at x = 0. It works on the
  decayed state.
- PLAN: place min(pool, live cells, MAX_PLACED = 2) sentries (at most 1 per owned non-TAKEN cell). The pool sentries
  not placed are the RESERVE. Optionally a ghost (kit) on an owned non-TAKEN cell or HOME, for +5 Heat.
  - L10: the pool starts at D1 N1 E0.
- LAUNCH: beam 1, then extra 1 (Heat >= 50) and extra 2 (Heat >= 75), using launch Heat with the ghost. Then the
  REVEAL of the sealed route, the RESPONSE, the sealed beam, and the hunter.
- BETWEEN (not after raid 3): repair <= 1 DOWN cell (v // 2), build <= 1 sentry (3), pick an intensity. Income and
  Heat are added after that.

Beams
- Every beam is typed (D drone, N netrunner, E enforcer) and runs along a line.
  - A ROUTE runs x = 3 -> 0, then reaches HOME.
  - A STREET runs y 0 -> 2 or 2 -> 0 and never reaches HOME.
- The sealed beam is one of the three routes, each carrying a distinct type (a seeded permutation). The real
  candidate is seeded.
- The hunter (typed) sweeps top to bottom down the column of the raid's first cell touch (hit or block, HOME never
  counts). With no touch it sweeps its own seeded street.

Scanning a line
- A ghosted cell: pass.
- A sentry of the beam's type: BLOCK. The line stops, so a stopped route never reaches HOME.
- An owned live cell not yet hit this raid: HIT (OK -> DOWN, DOWN -> TAKEN; L11: a TAKEN cell's sentry leaves the
  placement and returns to the pool).
- Otherwise: pass.
- At the end of a route: HOME -1, unless HOME is ghosted or was already hit this raid.
- No touches at all = EVADED: Heat -10.

Response (after the reveal; a spoof charge + 2 Heat after the sweep)
- HOLD.
- REDEPLOY s -> c (applies to the sealed beam and the hunter).
- DEPLOY t -> c (L11): a reserve sentry of type t onto an owned live cell with no sentry, after beam 1 and the extras.
  It stays placed after the raid.
- JAM (no hunter).
- Order: HOLD, every REDEPLOY, every DEPLOY (types D, N, E, then target cells in cell order), JAM.

safe_next (L11)
- True if some capture, then some placement, with the best response per sealed candidate, keeps HOME above 0 on
  every candidate of the given raid. It takes the post-decay state; True when raid >= RAIDS.

Score
- bank + sum(v - (v // 2 if DOWN)) over owned non-TAKEN cells
- + 6 per owned non-TAKEN EXPLOIT cell
- - 8 per HOME lost
- - 1.0 per Heat above 44
- A breach scores -100.

Measured (python sweep_l8.py)
- Greedy (each phase maximizes EV over the sealed candidates with the best response, kit valued KIT_VALUE mid-leg)
  against naive, over 20 legs. Both apply DECAY before every capture after raid 1.
- Per player: split_raids, response_decides, redeploy_use (L10), deploy_use, and decided_cuts (L11: legs where,
  after some between step, safe_next is False for every between option)."""
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
DECAY = True        # L9: DOWN -> TAKEN at the start of every raid after the first, before CAPTURE

# Score.
EXPLOIT_BONUS, HOME_LOSS_COST, HEAT_CARRY, BREACH = 6, 8, 1.0, 100
KIT_VALUE = 2.5     # planner heuristic only: an unspent kit item (ghost, spoof, pool sentry) mid-leg
EPS = 1e-9          # float ties keep the earlier option
OUT = r"D:/rc_tmp/raid_design_lab/sweep_l11.json"


def ck(c) -> tuple:
    """Sort key: cell order y then x."""
    return (c[1], c[0])


def config() -> dict:
    return {"W": W, "H": H, "TYPES": list(TYPES), "VALUES": list(VALUES), "EXPLOITS": EXPLOITS, "START_CELLS": START_CELLS,
            "RAIDS": RAIDS, "START_BANK": START_BANK, "START_HEAT": START_HEAT, "EXTRA_AT": EXTRA_AT,
            "STRONG_AT": STRONG_AT, "HOME_HP": HOME_HP, "GHOST_HEAT": GHOST_HEAT, "SPOOF_HEAT": SPOOF_HEAT,
            "EVADE_HEAT": EVADE_HEAT, "SENTRY_PRICE": SENTRY_PRICE, "POOL_START": dict(POOL_START),
            "MAX_PLACED": MAX_PLACED,
            "KIT_START": dict(KIT_START), "INTENSITY": {k: list(v) for k, v in INTENSITY.items()},
            "EXPLOIT_BONUS": EXPLOIT_BONUS, "HOME_LOSS_COST": HOME_LOSS_COST, "HEAT_CARRY": HEAT_CARRY,
            "BREACH": BREACH, "KIT_VALUE": KIT_VALUE, "DECAY": DECAY}


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
    hunter_street: int      # the hunter's own street when the raid has no touch


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
    """Seeded leg; the draw order is fixed, so a seed always gives the same leg."""
    rng = random.Random(8000 + seed)
    values = tuple((c, rng.choice(VALUES)) for c in CELLS)
    exploits = tuple(sorted(rng.sample([c for c in CELLS if c[0] >= 1], EXPLOITS), key=ck))
    start = tuple(sorted(rng.sample([c for c in CELLS if c[0] == 0], START_CELLS), key=ck))
    raids = []
    for _ in range(RAIDS):
        b1, e1, e2 = _rand_line(rng), _rand_line(rng), _rand_line(rng)
        perm = list(TYPES)
        rng.shuffle(perm)
        real = rng.randrange(CANDIDATES)
        ht = rng.choice(TYPES)
        hs = rng.randrange(W)
        raids.append(Raid(b1, e1, e2, tuple(perm), tuple(route(k, perm[k]) for k in range(CANDIDATES)), real, ht, hs))
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
    cell = tuple(cell)
    if cell not in capture_options(leg, st):
        raise ValueError(f"illegal capture {cell}")
    owned = dict(st.owned)
    owned[cell] = OK
    return replace(st, owned=_otup(owned))


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
    """None / "HOLD" / "JAM" / ("REDEPLOY", s, c) / ("DEPLOY", t, c) (lists accepted) -> a canonical tuple."""
    if r is None:
        return ("HOLD",)
    if isinstance(r, str):
        r = (r,)
    r = tuple(r)
    if r[0] == "REDEPLOY" and len(r) == 3:
        return ("REDEPLOY", tuple(r[1]), tuple(r[2]))
    if r[0] == "DEPLOY" and len(r) == 3:
        return ("DEPLOY", str(r[1]), tuple(r[2]))
    if r[0] in ("HOLD", "JAM") and len(r) == 1:
        return r
    raise ValueError(f"unknown response {r}")


class _Sweep:
    """One raid's mutable sweep: board, sentries, seen cells, HOME, and the trace [(beam, cell, kind)]."""

    def __init__(self, st: State, place):
        self.sent = dict(place[0])
        self.ghost = place[1]
        self.owned = dict(st.owned)
        self.hp = st.home_hp
        self.home_hit = False
        self.seen = set()
        self.trace = []
        self.first = None

    def scan(self, name: str, ln: Line) -> None:
        for c in ln.cells:
            if c == self.ghost:
                continue
            if self.sent.get(c) == ln.type:
                self.trace.append((name, c, "block"))
                if self.first is None:
                    self.first = c
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
                if self.first is None:
                    self.first = c
        if ln.home and self.ghost != HOME and not self.home_hit:
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


def _resolve(leg: Leg, raid: int, st: State, cand: int, place, response):
    resp = norm_response(response)
    kit = dict(st.kit)
    spoof = resp[0] != "HOLD"
    if spoof and kit["spoof"] <= 0:
        raise ValueError("no spoof charge")
    rd, heat, sw = _launch(leg, raid, st, place)
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
    sw.scan("sealed", rd.cands[cand])
    if resp[0] != "JAM":
        col = sw.first[0] if sw.first is not None else rd.hunter_street
        sw.scan("hunter", street(col, True, rd.hunter_type))
    if not sw.trace:
        heat -= EVADE_HEAT
    if spoof:
        heat += SPOOF_HEAT
        kit["spoof"] -= 1
    if place[1] is not None:
        kit["ghost"] -= 1
    ns = State(heat, st.bank, sw.hp, _otup(sw.owned), _otup(sw.sent), st.pool, _kit_t(kit))
    return ns, sw.trace


def resolve(leg: Leg, raid: int, st: State, cand: int, place, response=None):
    """One raid (raid = index into leg.raids) from the post-capture state. place = (sentries {cell: type}, ghost);
    response = HOLD / JAM / ("REDEPLOY", s, c) / ("DEPLOY", t, c), any legal one. Returns (state after the raid,
    touches [(cell | "HOME", "hit" | "block" | "home")])."""
    ns, tr = _resolve(leg, raid, st, cand, place, response)
    return ns, [(c, k) for _, c, k in tr]


def trace(leg: Leg, raid: int, st: State, cand: int, place, response=None) -> list:
    """The touches with their beam: [(beam, cell, kind)], beam in beam1/extra1/extra2/sealed/hunter (lab cues)."""
    return _resolve(leg, raid, st, cand, place, response)[1]


def hunter_line(leg: Leg, raid: int, st: State, cand: int, place, response=None) -> Line | None:
    """The street the hunter runs (None when JAMMED)."""
    resp = norm_response(response)
    if resp[0] == "JAM":
        return None
    tr = [x for x in trace(leg, raid, st, cand, place, resp) if x[0] != "hunter" and x[1] != HOME]
    rd = leg.raids[raid]
    return street(tr[0][1][0] if tr else rd.hunter_street, True, rd.hunter_type)


def response_options(leg: Leg, raid: int, st: State, cand: int, place) -> list:
    """HOLD, then (with a spoof charge) every REDEPLOY (source by cell order, then target), every DEPLOY (types D, N, E
    with a reserve sentry, then target in cell order), then JAM. Legality is read after beam 1 and the extras."""
    out = [("HOLD",)]
    if dict(st.kit)["spoof"] <= 0:
        return out
    _, _, sw = _launch(leg, raid, st, place)
    targets = [c for c in CELLS if sw.owned.get(c) in LIVE and c not in sw.sent]
    for s in sorted(sw.sent, key=ck):
        for c in targets:
            if c != s:
                out.append(("REDEPLOY", s, c))
    pool = dict(st.pool)
    for t in TYPES:
        if _reserve(pool, sw.sent, t) > 0:
            for c in targets:
                out.append(("DEPLOY", t, c))
    out.append(("JAM",))
    return out


def tier(before: State, after: State, touches) -> str:
    if after.home_hp <= 0:
        return "BREACHED"
    if after.home_hp < before.home_hp:
        return "DAMAGED"
    if not touches:
        return "EVADED"
    b, a = dict(before.owned), dict(after.owned)
    new_down = sum(1 for c, s in a.items() if s == DOWN and b.get(c) == OK)
    new_taken = sum(1 for c, s in a.items() if s == TAKEN and b.get(c) != TAKEN)
    return "BATTERED" if new_down >= 2 or new_taken >= 1 else "HOLDS"


def score(leg: Leg, st: State, mid: bool = False) -> float:
    """Leg score; mid=True adds KIT_VALUE per unspent ghost, spoof and pool sentry (planner heuristic only)."""
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
    if mid:
        s += KIT_VALUE * (sum(v for _, v in st.kit) + sum(v for _, v in st.pool))
    return s


def between(leg: Leg, st: State, repair=None, build=None, intensity: str = "NORMAL") -> State:
    """Repair (<= 1 DOWN cell, v // 2), then build (<= 1 sentry, SENTRY_PRICE), then income and Heat. An unaffordable or
    illegal repair or build is skipped."""
    vals = dict(leg.values)
    owned = dict(st.owned)
    bank = st.bank
    if repair is not None:
        repair = tuple(repair)
        if owned.get(repair) == DOWN and bank >= vals[repair] // 2:
            bank -= vals[repair] // 2
            owned[repair] = OK
    pool = dict(st.pool)
    if build is not None and build in TYPES and bank >= SENTRY_PRICE:
        bank -= SENTRY_PRICE
        pool[build] += 1
    dh, mult = INTENSITY[intensity]
    income = int(sum(vals[c] // 3 for c, s in owned.items() if s == OK) * mult)
    return State(st.heat + dh, bank + income, st.home_hp, _otup(owned), st.sentries, _pool_t(pool), st.kit)


def between_options(leg: Leg, st: State):
    """Yields (repair, build, intensity), all affordable: repair None then DOWN cells; build None then D, N, E."""
    vals = dict(leg.values)
    reps = [None] + [c for c, s in st.owned if s == DOWN and st.bank >= vals[c] // 2]
    for r in reps:
        left = st.bank - (vals[r] // 2 if r is not None else 0)
        for b in [None] + (list(TYPES) if left >= SENTRY_PRICE else []):
            for inten in INTENSITY:
                yield (r, b, inten)


def safe_next(leg: Leg, raid: int, st: State) -> bool:
    """L11: True if some capture option (none = no capture), then some placement, with the best response per sealed
    candidate, keeps HOME above 0 on every sealed candidate of raid `raid`. `st` is the post-decay state (the caller
    applies DECAY). True when raid >= RAIDS. Two exact shortcuts: HOME loses at most 1 per raid (so home_hp >= 2 is
    safe), and a ghost on HOME (kit ghost > 0) always keeps HOME; otherwise the search stops at the first safe plan."""
    if raid >= RAIDS:
        return True
    if st.home_hp <= 0:
        return False
    if st.home_hp >= 2 or dict(st.kit)["ghost"] > 0:
        return True
    for cap in capture_options(leg, st) or [None]:
        s1 = capture(leg, st, cap) if cap is not None else st
        for place in placements(leg, s1):
            opts = response_options(leg, raid, s1, 0, place)
            if all(any(resolve(leg, raid, s1, k, place, r)[0].home_hp > 0 for r in opts) for k in range(CANDIDATES)):
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
    """Per sealed candidate: (value, best response, after, touches), with the earliest response kept on ties."""
    opts = response_options(leg, raid, st, 0, place)
    per = []
    for k in range(CANDIDATES):
        best = None
        for r in opts:
            ns, t = resolve(leg, raid, st, k, place, r)
            v = score(leg, ns, mid)
            if best is None or v > best[0] + EPS:
                best = (v, r, ns, t)
        per.append(best)
    return per


def forecast(leg: Leg, raid: int, st: State, place) -> list:
    """Per sealed candidate: the HOLD result and the best response's result (ranked by the mid-leg value)."""
    mid = raid < RAIDS - 1
    out = []
    for k, best in enumerate(_best_per_cand(leg, raid, st, place, mid)):
        hs, ht = resolve(leg, raid, st, k, place, ("HOLD",))
        v, r, ns, t = best
        out.append({"cand": k, "route": ROUTE_NAMES[k], "type": leg.raids[raid].cands[k].type,
                    "hold": {"touches": ht, "tier": tier(st, hs, ht), "after": hs, "score": score(leg, hs)},
                    "best": {"response": r, "touches": t, "tier": tier(st, ns, t), "after": ns, "score": score(leg, ns),
                             "value": v}})
    return out


def _next_value(leg: Leg, raid: int, st: State) -> float:
    """Between-step lookahead: DECAY (raid > 0), then the next raid's best EV with no capture, no ghost and HOLD."""
    if raid > 0:
        st = decay(leg, st)
    mid = raid < RAIDS - 1
    best = None
    for place in placements(leg, st):
        if place[1] is not None:
            break       # ghost placements come after every no-ghost placement
        ev = sum(score(leg, resolve(leg, raid, st, k, place, ("HOLD",))[0], mid) for k in range(CANDIDATES)) / CANDIDATES
        if best is None or ev > best + EPS:
            best = ev
    return best if best is not None else score(leg, st, mid)


def _entry(i, cap, place, resp, k, touches, tr, after, decayed=()) -> dict:
    return {"raid": i, "decayed": list(decayed), "capture": cap,
            "place": {"sentries": dict(place[0]), "ghost": place[1]}, "response": resp,
            "cand_real": k, "touches": touches, "tier": tr, "after_raid": after, "between": None}


def greedy_leg(leg: Leg):
    """DECAY (raid > 0), then capture + plan jointly maximize the EV over the 3 candidates with the best response per
    candidate (kit valued mid-leg); the real candidate is then played with its best response. Between: the best
    one-raid lookahead (which sees the next DECAY)."""
    st = initial(leg)
    log = []
    for i in range(RAIDS):
        dec = []
        if i > 0:
            dec = decay_cells(leg, st)
            st = decay(leg, st)
        mid = i < RAIDS - 1
        best = None
        for cap in capture_options(leg, st) or [None]:
            s1 = capture(leg, st, cap) if cap is not None else st
            for place in placements(leg, s1):
                per = _best_per_cand(leg, i, s1, place, mid)
                ev = sum(p[0] for p in per) / CANDIDATES
                if best is None or ev > best[0] + EPS:
                    best = (ev, cap, s1, place, per)
        _, cap, s1, place, per = best
        k = leg.raids[i].real
        _, resp, ns, t = per[k]
        entry = _entry(i, cap, place, resp, k, t, tier(s1, ns, t), ns, dec)
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
    """DECAY (raid > 0); capture the highest value (first in cell order); keep sentries; never ghost or respond;
    repair the biggest affordable DOWN cell; build nothing; NORMAL."""
    vals = dict(leg.values)
    st = initial(leg)
    log = []
    for i in range(RAIDS):
        dec = []
        if i > 0:
            dec = decay_cells(leg, st)
            st = decay(leg, st)
        cap = None
        for c in capture_options(leg, st):
            if cap is None or vals[c] > vals[cap]:
                cap = c
        s1 = capture(leg, st, cap) if cap is not None else st
        place = (_naive_sentries(s1), None)
        k = leg.raids[i].real
        resp = ("HOLD",)
        ns, t = resolve(leg, i, s1, k, place, resp)
        entry = _entry(i, cap, place, resp, k, t, tier(s1, ns, t), ns, dec)
        log.append(entry)
        if ns.home_hp <= 0 or i == RAIDS - 1:
            return ns, log
        rep = None
        for c, s in ns.owned:
            if s == DOWN and ns.bank >= vals[c] // 2 and (rep is None or vals[c] > vals[rep]):
                rep = c
        entry["between"] = {"repair": rep, "build": None, "intensity": "NORMAL"}
        st = between(leg, ns, rep, None, "NORMAL")
    return st, log


def replay_befores(leg: Leg, log: list) -> list:
    """The post-capture state of every raid in a log (DECAY, then capture, for raids after the first)."""
    st = initial(leg)
    out = []
    for x in log:
        if x["raid"] > 0:
            st = decay(leg, st)
        s1 = capture(leg, st, x["capture"]) if x["capture"] is not None else st
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
            "pool": dict(st.pool), "kit": dict(st.kit)}


def _outcome(touches, tr: str) -> tuple:
    """A comparable raid outcome: (touches, tier)."""
    return (tuple((tuple(c) if c != HOME else c, k) for c, k in touches), tr)


def _raid_metrics(leg: Leg, before: State, x: dict) -> tuple:
    """L10 metrics for one logged raid: (split, response decides)."""
    place = (dict(x["place"]["sentries"]), x["place"]["ghost"])
    outs = []
    for k in range(CANDIDATES):
        ns, t = resolve(leg, x["raid"], before, k, place, ("HOLD",))
        outs.append(_outcome(t, tier(before, ns, t)))
    split = len(set(outs)) > 1
    decides = _outcome(x["touches"], x["tier"]) != outs[x["cand_real"]]
    return split, decides


def _leg_stats(leg: Leg, end: State, log: list) -> dict:
    vals = dict(leg.values)
    ex = set(leg.exploits)
    befores = replay_befores(leg, log)
    launch = [b.heat + (GHOST_HEAT if x["place"]["ghost"] is not None else 0) for b, x in zip(befores, log)]
    caps = [x["capture"] for x in log if x["capture"] is not None]
    bw = [x["between"] for x in log if x["between"]]
    metrics = [_raid_metrics(leg, b, x) for b, x in zip(befores, log)]
    cut = any(decided(leg, x["raid"] + 1, x["after_raid"]) for x in log if x["between"])
    return {"score": score(leg, end), "breach": end.home_hp <= 0, "raids": len(log),
            "tiers": [x["tier"] for x in log],
            "blocks": sum(1 for x in log for _, k in x["touches"] if k == "block"),
            "responses": [x["response"][0] for x in log],
            "ghosts": sum(x["place"]["ghost"] is not None for x in log),
            "ghost_home": sum(x["place"]["ghost"] == HOME for x in log),
            "cap_values": [vals[c] for c in caps], "cap_x": [c[0] for c in caps],
            "cap_exploits": sum(c in ex for c in caps),
            "intensity": [b["intensity"] for b in bw], "builds": [b["build"] for b in bw],
            "repairs": sum(b["repair"] is not None for b in bw), "home_lost": HOME_HP - end.home_hp,
            "decayed": sum(len(x["decayed"]) for x in log),
            "taken_end": sum(s == TAKEN for _, s in end.owned), "down_end": sum(s == DOWN for _, s in end.owned),
            "extra_raids": sum(h >= EXTRA_AT for h in launch), "strong_raids": sum(h >= STRONG_AT for h in launch),
            "split": sum(m[0] for m in metrics), "decides": sum(m[1] for m in metrics),
            "redeploys": sum(x["response"][0] == "REDEPLOY" for x in log),
            "deploys": sum(x["response"][0] == "DEPLOY" for x in log),
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
            "response_use": {k: resp.count(k) for k in ("HOLD", "REDEPLOY", "DEPLOY", "JAM")},
            "ghost_per_raid": round(sum(r[p]["ghosts"] for r in rows) / raids, 2),
            "ghost_home": sum(r[p]["ghost_home"] for r in rows),
            "tier_mix": {t: tiers.count(t) for t in ("BREACHED", "DAMAGED", "EVADED", "BATTERED", "HOLDS")},
            "capture_mean_value": round(stats.mean(capv), 2) if capv else 0,
            "capture_x_mix": {str(x): capx.count(x) for x in range(W)},
            "capture_exploit_share": round(sum(r[p]["cap_exploits"] for r in rows) / max(1, len(capv)), 2),
            "intensity_mix": {k: ints.count(k) for k in INTENSITY},
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
            "redeploy_use": round(sum(r[p]["redeploys"] for r in rows) / raids, 2),
            "deploy_use": round(sum(r[p]["deploys"] for r in rows) / raids, 2),
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
    print("SUMMARY", json.dumps(summ), flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"config": config(), "summary": summ, "rows": rows}, f, indent=1)
