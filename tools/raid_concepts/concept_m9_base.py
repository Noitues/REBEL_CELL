"""Round 9 MANHUNT variants, shared frames (rules in ghost2.py, scarce levers; each a designer decision).
The M8 critic's shared fixes are in all three:
- contact is caused by Heat: crossing a Heat threshold (cobalt shield notch) makes the front reach you;
- levers cost different currencies: GHOST costs +GHOST_HEAT Heat (flame), DECOY 3 Schematics (coin), GO DARK the node's
  next income (dimmed coin);
- found assets stay DOWN until repaired, and repairs come out of the core KEY (the bar the run is racing to fill).
Variants: VARIANT = "sealed" (M9a, zero input), "spoof" (M9b, one press), "both" (M9c).
Every number is ghost2.py output for network SEED."""
from __future__ import annotations

import itertools

from r2_kit import *  # noqa: F403
from concept_h7_bastion import signed_coin
import ghost2 as G2
from ghost import H, NODES, W

G2.MAX_GHOST, G2.MAX_DECOY = 1, 1
SEED = 22
KEY, KEY_HAVE = 25, 19
MOMENTS = ["1_contact", "2_plan", "3_forecast", "4_playout", "5_aftermath"]
ASSETS, B1, CANDS, OWN3 = G2.setup(SEED)
ALLOCS = list(G2.allocations(ASSETS))
REVEAL = 0   # the corp's actual pick (deterministic per seed; the player sees only the candidates)


def ev_sealed(a):
    return sum(G2.outcome(ASSETS, B1, c, OWN3, a) for c in CANDS) / len(CANDS)


def best_sealed():
    return max(ALLOCS, key=ev_sealed)


def best_spoof():
    best = None
    for a in ALLOCS:
        miss = G2.outcome(ASSETS, B1, CANDS[0], OWN3, a)
        for sp in G2.SPOOFS[1:]:
            hit = G2.outcome(ASSETS, B1, CANDS[0], OWN3, a, sp)
            e = G2.SPOOF_HIT * hit + (1 - G2.SPOOF_HIT) * miss
            if best is None or e > best[0]:
                best = (e, a, sp, hit, miss)
    return best


def react_plan(a):
    """Per candidate: the best spoof after the reveal, its outcome, and the outcome without it."""
    out = []
    for c in CANDS:
        miss = G2.outcome(ASSETS, B1, c, OWN3, a)
        sp, hit = max(((sp, G2.outcome(ASSETS, B1, c, OWN3, a, sp)) for sp in G2.SPOOFS[1:]), key=lambda x: x[1])
        out.append((sp, hit, miss))
    return out


def best_both():
    def score(a):
        return sum(G2.SPOOF_HIT * h + (1 - G2.SPOOF_HIT) * m for _, h, m in react_plan(a)) / len(CANDS)
    a = max(ALLOCS, key=score)
    return score(a), a


# ---------- drawing ----------
def nx(c):
    return (170 + c[0] * 150, 230 + c[1] * 140)


def beam(d, line, k, col=THREAT, upto=None, dash_line=False, width=6, badge=True):
    pts = [nx(c) for c in line]
    a, b = pts[0], pts[-1]
    if upto is not None:
        b = nx(upto)
    ax, ay = a[0] - (pts[1][0] - pts[0][0]) * 0.45, a[1] - (pts[1][1] - pts[0][1]) * 0.45
    arrow(d, (ax, ay), b, col, width=width, dash_line=dash_line, shorten=0)
    if badge:
        order_badge(d, (ax, ay), k)


def node(d, c, alloc, found=(), down=()):
    v = ASSETS.get(c)
    g, dk, dc = alloc
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
        flame(d, (x + 30, y - 26), 7, HEAT)
    elif c in dk:
        d.ellipse((x - 28, y - 28, x + 28, y + 28), fill=(10, 10, 16), outline=DIM, width=3)
    else:
        d.ellipse((x - 28, y - 28, x + 28, y + 28), fill=(60, 30, 36) if c in down else PANEL,
                  outline=DMG if c in found else CELL, width=4)
    coin(d, (x - 8, y), 8, DIM if c in dk else CELL)
    text(d, (x + 4, y - 11), str(v), 19, DIM if c in dk else INK, "mono")
    if c in found:
        pencil_x(d, (x, y), 30, DMG)


def network(d, alloc, b2=None, cands=False, found=(), hunter=True, spoof=None, faded=()):
    for c in NODES:
        node(d, c, alloc, found)
    g, dk, dc = alloc
    stop1 = next((c for c in B1 if c in dc and spoof != (0, c)), None)
    beam(d, B1, 1, upto=stop1)
    if cands:
        for i, c in enumerate(CANDS):
            col = (50, 60, 110) if i in faded else THREAT_LIGHT
            beam(d, c, 2, col, dash_line=True, width=4, badge=i == 0)
            ex, ey = nx(c[-1])
            dx, dy = (nx(c[-1])[0] - nx(c[-2])[0]) * 0.35, (nx(c[-1])[1] - nx(c[-2])[1]) * 0.35
            disc(d, (ex + dx, ey + dy), i + 1, (50, 60, 110) if i in faded else THREAT)
    if b2 is not None:
        stop2 = next((c for c in b2 if c in dc and spoof != (1, c)), None)
        beam(d, b2, 2, upto=stop2)
        if hunter:
            hc = hunter_col(alloc, b2, spoof)
            line = [(hc, y) for y in range(H)] if hc is not None else OWN3
            beam(d, line, 3, THREAT_LIGHT, dash_line=True)
    if spoof is not None:
        x, y = nx(spoof[1])
        d.ellipse((x - 40, y - 40, x + 40, y + 40), outline=STAMP_CLEAN, width=4)
        text(d, (x + 30, y + 26), "SPACE", 13, STAMP_CLEAN)


def hunter_col(alloc, b2, spoof=None):
    g, dk, dc = alloc
    hidden = set(g) | set(dk)
    for k, ln in enumerate((B1, b2)):
        for c in ln:
            if spoof == (k, c):
                continue
            if c in dc:
                return c[0]
            if c in ASSETS and c not in hidden:
                return c[0]
    return None


def found_by(alloc, b2, spoof=None):
    g, dk, dc = alloc
    return G2.sweep(ASSETS, B1, b2, OWN3, set(g) | set(dk), set(dc), spoof)


def tray(d, x, y, alloc):
    g, dk, dc = alloc
    panel(d, (x, y, x + 330, y + 130))
    for a in range(0, 360, 30):
        d.arc((x + 24, y + 24, x + 64, y + 64), a, a + 15, fill=CELL if g else DIM, width=3)
    flame(d, (x + 44, y + 92), 8, HEAT)
    text(d, (x + 56, y + 82), f"+{G2.GHOST_HEAT}", 16, HEAT, "mono")
    cx = x + 150
    col = CELL if dc else DIM
    d.polygon([(cx, y + 24), (cx + 20, y + 44), (cx, y + 64), (cx - 20, y + 44)], outline=col, width=3)
    coin(d, (cx - 8, y + 92), 7, col)
    text(d, (cx + 2, y + 82), "-3", 16, col, "mono")
    cx = x + 260
    d.ellipse((cx - 20, y + 24, cx + 20, y + 64), fill=(10, 10, 16), outline=DIM, width=3)
    text(d, (cx - 10, y + 82), f"x{len(dk)}", 16, INK, "mono")


def key_bar(d, x, y, have, lose=0):
    w = 360
    d.rounded_rectangle((x, y, x + w, y + 18), radius=6, fill=(30, 34, 56), outline=PANEL_EDGE, width=2)
    fw = int(w * min(have, KEY) / KEY)
    d.rounded_rectangle((x, y, x + fw, y + 18), radius=6, fill=CELL)
    if lose:
        lw = int(w * min(lose, have) / KEY)
        d.rectangle((x + fw - lw, y + 2, x + fw, y + 16), fill=DMG)
    d.regular_polygon((x + w + 22, y + 9, 14), 6, outline=THREAT_LIGHT, fill=(40, 30, 70))
    text(d, (x + w + 44, y - 2), f"{have - lose}/{KEY}", 18, INK, "mono")


def contact_hud(d, heat=52):
    heat_bar(d, 60, 24, 420, heat, raid_at=50)
    key_bar(d, 700, 24, KEY_HAVE)


def frame_contact(name, note):
    img, d = new_frame(name, "contact")
    contact_hud(d)
    for c in NODES:
        node(d, c, ((), (), ()))
    panel(d, (820, 130, 1240, 420))
    text(d, (840, 144), "HAUL", 15, DIM)
    for i, (c, v) in enumerate(sorted(ASSETS.items(), key=lambda kv: -kv[1])):
        coin(d, (860 + (i % 3) * 120, 200 + (i // 3) * 70), 13)
        text(d, (880 + (i % 3) * 120, 188 + (i // 3) * 70), str(v), 22, INK, "mono")
    header(d, name, 1, f"Contact: Heat crossed 50 (cobalt notch), so the front reached the cell; every node you ran is an asset here. {note}")
    return img


def aftermath(name, alloc, b2, spoof=None, note=""):
    img, d = new_frame(name, "aftermath")
    found = found_by(alloc, b2, spoof)
    network(d, alloc, b2=b2, found=found, spoof=spoof)
    loss = sum(ASSETS[c] for c in found)
    v = G2.value(ASSETS, found, *alloc)
    stamp(img, (1040, 190), "CELL HOLDS", STAMP_HOLD if found else STAMP_CLEAN, 52,
          sub=f"{len(found)} DOWN" if found else "EVADED")
    signed_coin(d, (960, 300), int(round(v)), 36)
    key_bar(d, 700, 420, KEY_HAVE, lose=loss)
    text(d, (700, 450), "DOWN until repaired", 14, DMG)
    header(d, name, 5, f"Aftermath: {len(found)} assets DOWN (stay down until repaired; repair {loss} comes out of the key); net {v:+.0f}. {note}")
    return img
