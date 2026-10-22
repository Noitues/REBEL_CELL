"""Concept M, round 8: MANHUNT = Pursuit (campaign front) + Ghost Protocol (the raid is a sweep). Each rule is a
designer decision (MEASURE_R8.md):
- Solace's FRONT crawls across the City Grid each netrun at a speed set by Heat (pursuit.py, fast table, LAY LOW holds
  position, the core needs a Schematics key). Cobalt fill = swallowed; hatched cobalt = where it ends after this netrun.
- CADENCE: the front makes contact every CATCH_EVERY netruns (guaranteed beats, not avoidable catches: an avoidable
  catch is never taken, MEASURE_R8). The route decides WHAT you carry when contact lands: every node you ran becomes an
  asset in your cell's network (the cell's standing nodes fill the rest at value 3).
- The raid is a SWEEP of that network (ghost.py): 3 beams shown in advance, the third a hunter that turns down the
  column of the first find. Levers: 2 ghost slots (free), decoys (3 Schematics, stop a beam), go dark (lose that
  node's next income). Found = DOWN (repair = value). Nothing real found = evaded (+6, Heat drop).
Every number comes from pursuit.py / ghost.py."""
from __future__ import annotations

import itertools

from r2_kit import *  # noqa: F403
from concept_h7_bastion import signed_coin
import ghost as GH
import pursuit as PU

NAME = "M8 MANHUNT r8"
MOMENTS = ["1_front", "2_route", "3_sweep_forecast", "4_sweep_playout", "5_aftermath", "6_record"]
CATCH_EVERY = 4
PU.LOW_STAYS, PU.KEY, PU.MAX_TURNS, PU.BEAM = True, 25, 16, 900
_TAB = (1.0, 1.25, 1.5, 1.75)
PU.speed = lambda h: _TAB[0] if h < 25 else _TAB[1] if h < 50 else _TAB[2] if h < 75 else _TAB[3]
SEED = 1003
NODES_ = PU.grid(SEED)


def replay(path):
    s = ((0, 1), 0, PU.FRONT_START, frozenset(), 0, 0, 0)
    out = [s]
    for m, a in path:
        s = PU.step(s, m, a, NODES_)
        out.append(s)
    return out


_res = PU.beam(NODES_)
MINE_PATH = _res[0][1]
MINE = replay(MINE_PATH)
SAFE_PATH = []
_s = MINE[0]
for _ in range(PU.MAX_TURNS):
    if _s[0] == PU.CORE:
        break
    _m, _a = PU.greedy(_s, NODES_)
    SAFE_PATH.append((_m, _a))
    _s = PU.step(_s, _m, _a, NODES_)
SAFE = replay(SAFE_PATH)
NOW = CATCH_EVERY - 2   # the warning frame: two netruns before contact


# ---------- the sweep (contact at netrun CATCH_EVERY) ----------
def haul(state):
    run = sorted(state[3], key=lambda n: (-NODES_[n][0], n))
    return [NODES_[n][0] for n in run if NODES_[n][0] > 0][:GH.ASSETS]


_assets0, BEAMS, OWN3 = GH.network(517)
_cells = sorted(_assets0)
ASSETS = {c: v for c, v in zip(_cells, haul(MINE[CATCH_EVERY]) + [3] * GH.ASSETS)}


def best_alloc(assets):
    best = None
    for g, dk, dc in GH.allocations(assets):
        v = GH.net(assets, BEAMS, OWN3, g, dk, dc)
        if best is None or v > best[0]:
            best = (v, g, dk, dc)
    return best


BEST = best_alloc(ASSETS)
NAIVE_G = tuple(sorted(ASSETS, key=lambda c: -ASSETS[c])[:GH.GHOSTS])
NAIVE = (GH.net(ASSETS, BEAMS, OWN3, NAIVE_G, (), ()), NAIVE_G, (), ())


# ---------- City Grid drawing ----------
def gx(c, r):
    return (110 + c * 104, 200 + r * 92) if c < PU.COLS else (1170, 292)


def front_x(f):
    return max(56, min(1230, 110 + f * 104 + 52))


def _seg(d, a, b, col, dash_line):
    if dash_line:
        dashed(d, a, b, col, width=5)
    else:
        d.line([a, b], fill=col, width=5)


def grid_base(d, st, ghost_front=None, route=None, alt=None, top=150):
    f = st[2]
    d.rectangle((56, top, front_x(f), 440), fill=(24, 36, 92))
    if ghost_front is not None and ghost_front > f:
        x0, x1 = front_x(f), front_x(ghost_front)
        for y in range(top, 440, 14):
            d.line([(x0, y), (x1, y)], fill=(44, 66, 170), width=3)
        d.line([(x1, top), (x1, 440)], fill=THREAT_LIGHT, width=3)
    for c, r in itertools.product(range(PU.COLS), range(PU.ROWS)):
        for m in PU.nbrs((c, r)):
            if m > (c, r):
                d.line([gx(c, r), gx(*m)], fill=(52, 58, 92), width=2)
    for path, col, dash_line in ((alt, DIM, True), (route, CELL, False)):
        if path:
            pts = [gx(*p) for p in path]
            for a, b in zip(pts, pts[1:]):
                if a != b:
                    _seg(d, a, b, col, dash_line)
    for (c, r), (v, h) in NODES_.items():
        if (c, r) == PU.CORE:
            continue
        x, y = gx(c, r)
        swallowed = c <= f
        ran = (c, r) in st[3]
        rad = 14 + v * 1.6
        d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=(40, 46, 80) if swallowed else PANEL,
                  outline=THREAT if swallowed else (CELL if ran else PANEL_EDGE), width=3)
        if v and not swallowed and not ran:
            coin(d, (x - 7, y), 7, CELL)
            text(d, (x + 3, y - 10), str(v), 17, INK, "mono")
        if ran:
            check(d, (x, y), 9, CELL)
    cx, cy = gx(PU.COLS, 1)
    d.regular_polygon((cx, cy, 34), 6, fill=(40, 30, 70), outline=THREAT_LIGHT)
    shield(d, (cx, cy - 4), 13, THREAT)
    x, y = gx(*st[0])
    d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=CELL, outline=BG, width=2)


def speed_link(d, x, y, heat):
    """The Heat-to-speed link drawn on the Heat meter: a chevron count per band."""
    heat_bar(d, x, y, 360, heat, raid_at=None)
    for i, b in enumerate((0, 25, 50, 75)):
        bx = x + int(360 * (b + 12) / 100)
        n = i + 1
        on = b <= heat < b + 25
        for k in range(n):
            px = bx - n * 5 + k * 10
            d.polygon([(px, y + 26), (px + 7, y + 32), (px, y + 38)], fill=THREAT_LIGHT if on else (60, 66, 100))


def contact_pips(d, x, y, left, of=CATCH_EVERY):
    for i in range(of):
        col = THREAT if i >= of - left else (50, 54, 80)
        d.rectangle((x + i * 22, y, x + i * 22 + 16, y + 16), fill=col)
    shield(d, (x + of * 22 + 14, y + 6), 11, THREAT)


# ---------- network (sweep) drawing ----------
def nx(c):
    return (170 + c[0] * 150, 210 + c[1] * 140)


def beam_line(d, line, k, col=THREAT, upto=None, dash_line=False):
    pts = [nx(c) for c in line]
    a, b = pts[0], pts[-1]
    if upto is not None:
        b = nx(upto)
    ax, ay = a[0] - (pts[1][0] - pts[0][0]) * 0.45, a[1] - (pts[1][1] - pts[0][1]) * 0.45
    arrow(d, (ax, ay), b, col, width=6, dash_line=dash_line, shorten=0)
    order_badge(d, (ax, ay), k)


def net_node(d, c, alloc, found=(), near=()):
    v = ASSETS.get(c)
    _, g, dk, dc = alloc
    x, y = nx(c)
    if c in dc:
        d.polygon([(x, y - 26), (x + 26, y), (x, y + 26), (x - 26, y)], outline=CELL, width=4)
        d.polygon([(x, y - 10), (x + 10, y), (x, y + 10), (x - 10, y)], fill=CELL)
        return
    if v is None:
        d.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(40, 46, 80))
        return
    if c in g:
        for a in range(0, 360, 30):
            d.arc((x - 28, y - 28, x + 28, y + 28), a, a + 15, fill=CELL, width=4)
    elif c in dk:
        d.ellipse((x - 28, y - 28, x + 28, y + 28), fill=(10, 10, 16), outline=DIM, width=3)
        d.arc((x - 9, y - 9, x + 9, y + 9), 300, 240, fill=DIM, width=3)
        d.line([(x, y - 12), (x, y - 2)], fill=DIM, width=3)
    else:
        d.ellipse((x - 28, y - 28, x + 28, y + 28), fill=PANEL, outline=DMG if c in found else CELL, width=4)
    if c not in dk:
        coin(d, (x - 8, y), 8, CELL)
        text(d, (x + 4, y - 11), str(v), 19, INK, "mono")
    if c in found:
        pencil_x(d, (x, y), 30, DMG)
    if c in near:
        d.ellipse((x - 40, y - 40, x + 40, y + 40), outline=THREAT_LIGHT, width=2)


def hunter_target(alloc):
    hidden = set(alloc[1]) | set(alloc[2])
    first = None
    for b in BEAMS:
        for c in b:
            if c in alloc[3]:
                first = first or c
                break
            if c in ASSETS and c not in hidden:
                first = first or c
    return first[0] if first else None


def network(d, alloc, found=(), near=(), beams=3):
    for c in GH.NODES:
        net_node(d, c, alloc, found, near)
    for k, b in enumerate(BEAMS[:beams]):
        stop = next((c for c in b if c in alloc[3]), None)
        beam_line(d, b, k + 1, upto=stop)
    if beams >= 3:
        hc = hunter_target(alloc)
        line = [(hc, y) for y in range(GH.H)] if hc is not None else OWN3
        beam_line(d, line, 3, THREAT_LIGHT, upto=next((c for c in line if c in alloc[3]), None), dash_line=True)


def found_by(alloc):
    return GH.sweep(ASSETS, BEAMS, OWN3, set(alloc[1]) | set(alloc[2]), set(alloc[3]))


def tray(d, x, y, alloc):
    panel(d, (x, y, x + 320, y + 230))
    text(d, (x + 16, y + 12), "HIDE", 16, DIM)
    for i in range(GH.GHOSTS):
        cx = x + 44 + i * 64
        for a in range(0, 360, 30):
            d.arc((cx - 20, y + 50, cx + 20, y + 90), a, a + 15, fill=CELL if i < len(alloc[1]) else DIM, width=3)
    for i in range(2):
        cx = x + 210 + i * 56
        col = CELL if i < len(alloc[3]) else DIM
        d.polygon([(cx, y + 50), (cx + 18, y + 70), (cx, y + 90), (cx - 18, y + 70)], outline=col, width=3)
        coin(d, (cx - 7, y + 112), 6, col)
        text(d, (cx + 3, y + 102), f"{GH.DECOY_COST}", 14, col, "mono")
    cx = x + 44
    d.ellipse((cx - 18, y + 150, cx + 18, y + 186), fill=(10, 10, 16), outline=DIM, width=3)
    text(d, (cx + 30, y + 156), f"x{len(alloc[2])}", 20, INK, "mono")


def forecast(d, x, y, alloc, label="PLAN"):
    found = found_by(alloc)
    panel(d, (x, y, x + 320, y + 150))
    text(d, (x + 16, y + 12), label, 16, DIM)
    for i, c in enumerate(found):
        pencil_x(d, (x + 40 + i * 44, y + 62), 16, DMG)
        text(d, (x + 32 + i * 44, y + 84), str(ASSETS[c]), 16, DMG, "mono")
    if not found:
        check(d, (x + 40, y + 62), 16, STAMP_CLEAN)
    signed_coin(d, (x + 200, y + 70), alloc[0], 34)


# ---------- frames ----------
def f1():
    img, d = new_frame(NAME, "front")
    st, nxt = MINE[NOW], MINE[NOW + 1]
    grid_base(d, st, ghost_front=nxt[2], route=[s[0] for s in MINE[NOW:CATCH_EVERY + 1]])
    speed_link(d, 120, 40, st[1])
    contact_pips(d, 640, 40, CATCH_EVERY - NOW)
    panel(d, (56, 470, 1230, 680))
    text(d, (80, 486), "HAUL", 16, DIM)
    for i, v in enumerate(haul(st)):
        coin(d, (100 + i * 70, 540), 14)
        text(d, (120 + i * 70, 528), str(v), 22, INK, "mono")
    header(d, NAME, 1, f"Netrun {NOW}: Heat {st[1]} sets the front's speed (chevrons); hatched = where it ends this netrun; contact in {CATCH_EVERY - NOW} (cobalt pips)")
    return img


def f2():
    img, d = new_frame(NAME, "route")
    st = MINE[NOW]
    grid_base(d, st, ghost_front=MINE[CATCH_EVERY][2], route=[s[0] for s in MINE[NOW:CATCH_EVERY + 1]],
              alt=[s[0] for s in SAFE[NOW:CATCH_EVERY + 1]])
    speed_link(d, 120, 40, MINE[CATCH_EVERY][1])
    panel(d, (56, 470, 640, 680))
    panel(d, (660, 470, 1230, 680))
    for (x0, line, col) in ((80, MINE, CELL), (684, SAFE, DIM)):
        e = line[min(CATCH_EVERY, len(line) - 1)]
        d.line([(x0, 500), (x0 + 60, 500)], fill=col, width=5)
        flame(d, (x0 + 100, 506), 9, HEAT)
        text(d, (x0 + 116, 492), f"{e[1]}", 22, HEAT, "mono")
        coin(d, (x0 + 200, 506), 10)
        text(d, (x0 + 216, 492), f"{e[4]}", 22, INK, "mono")
        for i, v in enumerate(haul(e)):
            coin(d, (x0 + 20 + i * 60, 580), 12)
            text(d, (x0 + 36 + i * 60, 568), str(v), 20, INK, "mono")
    header(d, NAME, 2, f"Route: yours (solid) hauls {MINE[CATCH_EVERY][4]} at Heat {MINE[CATCH_EVERY][1]}; the greedy line (dashed) {SAFE[CATCH_EVERY][4]} at Heat {SAFE[CATCH_EVERY][1]}; more haul = more to hide")
    return img


def f3():
    img, d = new_frame(NAME, "sweep forecast")
    network(d, BEST)
    tray(d, 900, 40, BEST)
    forecast(d, 900, 300, BEST, "YOUR PLAN")
    forecast(d, 900, 480, NAIVE, "GHOST THE BIGGEST")
    header(d, NAME, 3, f"Contact: the sweep is shown (beams 1-2, hunter 3 turns down the first find's column); your plan nets {BEST[0]:+d}, ghosting the two biggest nets {NAIVE[0]:+d}")
    return img


def f4():
    img, d = new_frame(NAME, "sweep playout")
    near = [c for c in ASSETS if c in BEST[1] and any(c in b for b in BEAMS)]
    network(d, BEST, found=[], near=near)
    step_track(d, 900, 120, 280, 3, 3, "BEAM")
    speed_controls(d, 900, 160)
    header(d, NAME, 4, "Playout (hands-off): beams stop on decoys, the hunter turns down the first find's column; rings = near misses on ghosted assets")
    return img


def f5():
    img, d = new_frame(NAME, "aftermath")
    found = found_by(BEST)
    network(d, BEST, found=found)
    stamp(img, (1040, 200), "CELL HOLDS", STAMP_HOLD if found else STAMP_CLEAN, 54,
          sub=f"{len(found)} DOWN" if found else "EVADED")
    signed_coin(d, (980, 330), BEST[0], 40)
    flame(d, (990, 470), 12, HEAT)
    text(d, (1010, 452), "-10" if not found else "+0", 30, STAMP_CLEAN if not found else DIM, "mono")
    header(d, NAME, 5, f"Aftermath: found assets DOWN (repair = value), dark nodes skip their next income; net {BEST[0]:+d}" + ("; evaded, Heat -10" if not found else ""))
    return img


def f6():
    img, d = new_frame(NAME, "record")
    end = MINE[-1]
    grid_base(d, end, route=[s[0] for s in MINE])
    for k, t in enumerate(range(CATCH_EVERY, len(MINE), CATCH_EVERY)):
        x, y = gx(*MINE[t][0])
        shield(d, (x, y - 34), 11, THREAT)
        disc(d, (x + 22, y - 40), k + 1, THREAT)
    panel(d, (56, 470, 1230, 680))
    coin(d, (100, 520), 14)
    text(d, (124, 506), f"{end[4]}", 28, INK, "mono")
    text(d, (230, 506), f"{PU.score(end):+d}", 28, STAMP_CLEAN, "mono")
    header(d, NAME, 6, f"Record: the route (yellow), each contact where it landed (cobalt shields); reached the core with {end[4]} Schematics, score {PU.score(end):+d}")
    return img


FRAMES = [f1, f2, f3, f4, f5, f6]

if __name__ == "__main__":
    print("mine", [(s[0], s[1], round(s[2], 2), s[4]) for s in MINE])
    print("haul", haul(MINE[CATCH_EVERY]), "assets", ASSETS)
    print("best", BEST, "naive", NAIVE[0], "found", found_by(BEST))
