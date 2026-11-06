"""F Rebel Tag / Street Hack: build every frame.   python ft_frames.py  (writes ../NN_*.png)"""
import os, sys, math, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from ft_lib import *
from ft_marks import *
from ft_scene import *
from ft_scene import _D


def sh(s):
    return sum(ord(c) * (i + 3) for i, c in enumerate(s)) % 991

OUT = os.path.abspath(os.path.join(HERE, ".."))
CACHE = "D:/rc_scratch/tide_concepts/f_work/plate_graded.png"

LANE.update({"known0": -26, "known1": 26})


def city():
    if os.path.exists(CACHE):
        return Image.open(CACHE).convert("RGBA")
    im = grade(load_plate()).convert("RGB")
    im.save(CACHE)
    return im.convert("RGBA")


# ------------------------------------------------------------------------------------------ shared scene
SITE_ORDER = ["t1_a", "t1_b", "t1_c", "t1_d", "t2_breach", "t2_intel", "t2_virus", "t3_b", "t3_c", "t3_core"]
SITE_TIER = {s["id"]: s["tier"] for s in _D["sites"]}
SITE_TIER["t1_d"] = 1


def pins(base, states, focus=None, dim=(), only=None, big=1.35):
    """corp AR site pins; states: id -> healthy|DOWN|TAKEN.  Back-to-front so nearer pins overlap."""
    tops = {}
    ids = sorted(SITE_ORDER, key=lambda s: A[s][1])
    if only:
        ids = [i for i in ids if i in only]
    for sid in ids:
        L = Layer()
        if sid in WORLD["stub"]:
            L.line(list(WORLD["stub"][sid]), CORP, 2.5, a=170)
        st = states.get(sid, "healthy")
        top = site_pin(L, A[sid], st, SITE_TIER[sid], focus=(sid == focus), big=big, dim=(sid in dim))
        base = commit(base, L)
        tops[sid] = top
        if st == "DOWN":
            base = mark_down(base, top, seed=sh(sid))
        elif st == "TAKEN":
            base = mark_taken(base, top, seed=sh(sid))
    return base, tops


def corp_layer(base, with_lattice=True, t=0.0):
    if with_lattice:
        base = commit(base, corp_lattice(60))
    L = Layer()
    corp_hq(L, A["core"], t)
    return commit(base, L, glow=0.5, glow_r=8)


def order_dot(L, p, n, col=(255, 255, 255)):
    L.circle(p, 12, fill=INK)
    L.circle(p, 10, fill=(20, 34, 56), outline=col, w=2)
    L.text(p, str(n), f2(F_MONO, 17), col)


def head(L, t, pts, s, size=20):
    p, ang = point_at(pts, s)
    g_type(L, t, p, size)
    return p


HS = 0.0


def hunter_layer(base, locked=None, size=1.0):
    """the HUNTER: a corp eye-drone hovering over the fork, two ghost streets (dashed E-style).  locked = 0|1 snaps brackets on one street."""
    L = Layer()
    streets = ["hunter0", "hunter1"]
    ends = []
    for i, n in enumerate(streets):
        pts = WORLD["paths"][n]
        a_ = 90 if (locked is None or locked == i) else 28
        # ghost E street: dashed yellow, black casing
        cl = cum(pts)
        s = 0
        while s < cl[-1]:
            seg = sub_path(pts, s, min(cl[-1], s + 12))
            L.line(seg, INK, 11, a=int(a_ * 2.2))
            L.line(seg, BEAM["E"], 6.5, a=int(a_ * 2.6) if locked is None else (255 if locked == i else 70))
            s += 22
        ends.append(point_at(pts, cl[-1] * .5)[0])
    hub = (sum(e[0] for e in ends) / 2 + 20, min(e[1] for e in ends) - 150)
    for i, e in enumerate(ends):
        on = locked is None or locked == i
        for p in resample([hub, e], 12)[1::2]:
            L.circle(p, 2.6 if on else 1.6, fill=BEAM["E"], a=230 if on else 70)
    # eye drone
    L.circle(hub, 34, fill=INK, a=235)
    L.circle(hub, 34, outline=BEAM["E"], w=4)
    g_eye(L, hub, 21, BEAM["E"])
    for k in range(3):
        L.circle(hub, 44 + k * 9, outline=BEAM["E"], w=1.6, a=90 - k * 25)
    if locked is not None:
        lock_on(L, ends[locked], 54)
        e = ends[1 - locked]
        g_x(L, e, 16, (150, 160, 185), w=4, a=200)
    return commit(base, L, glow=0.35, glow_r=7), hub, ends


def sealed_fog(base):
    return fog_band(base, ["cand0", "cand1", "cand2"], seed=9)


def sealed_locks(base, opened=None):
    """padlock tags with the Cell's spray letters (the Cell's guesses about the sealed routes)"""
    pos = {"A": A["t1_a"], "B": A["t2_virus"], "C": A["t2_breach"]}
    L = Layer()
    for k, c in pos.items():
        cx = (c[0] - 84, c[1] - 36)
        L.line([c, cx], (170, 180, 200), 2, a=200)
        L.circle(cx, 31, fill=(10, 16, 30), outline=(170, 180, 200), w=3.5)
        g_lock(L, (cx[0], cx[1] - 1), 16, (190, 198, 215))
    base = commit(base, L)
    for k, c in pos.items():
        base = tag_text(base, (c[0] - 84, c[1] - 104), k, 64, BONE, seed=ord(k), tilt=-.18)
    return base


def sealed_layer(base):
    return sealed_locks(sealed_fog(base))


GOFF = {"t1_b": (-66, 6), "t1_c": (66, 8)}


def gpos(sid):
    o = GOFF.get(sid, (0, 16))
    return (A[sid][0] + o[0], A[sid][1] + o[1])


def stencil_ground_all(base, placed):
    """placed: list of (kind, site, type)"""
    for kind, sid, t in placed:
        c = gpos(sid)
        if kind == "guard":
            base = stencil_guard(base, c, t, seed=sh(sid), size=42)
    return base


def hand(base, items, sel=None, lift=0):
    L = Layer()
    n = len(items)
    x0 = W / 2 - (n - 1) * 56
    for i, (kind, t) in enumerate(items):
        c = (x0 + i * 112, 985 - (24 if i == sel else 0) - lift + abs(i - (n - 1) / 2) * 3)
        ang = (i - (n - 1) / 2) * 0.05
        if kind == "guard":
            vinyl_card(L, c, 96, 128, ang, BEAM[t], lambda L_, cc, s_, t=t: (g_shield(L_, cc, s_ * 1.2, (255, 255, 255), INK, lw=2.5), g_type(L_, t, (cc[0], cc[1] + 3), s_ * .55, line=INK)))
        elif kind == "shift":
            vinyl_card(L, c, 96, 128, ang, (246, 240, 222), lambda L_, cc, s_: g_arrow(L_, cc, s_ * 1.4, INK, ang=-.5))
        elif kind == "ghost":
            vinyl_card(L, c, 96, 128, ang, (236, 232, 248), lambda L_, cc, s_: (L_.circle((cc[0] - 3, cc[1] - 5), s_ * .85, fill=(255, 40, 120), a=210), L_.circle((cc[0] + 3, cc[1] - 5), s_ * .85, fill=(40, 230, 255), a=210), L_.circle((cc[0], cc[1] - 5), s_ * .85, fill=(255, 255, 255))))
        if i == sel:
            L.rrect((c[0] - 58, c[1] - 74, c[0] + 58, c[1] + 74), 12, outline=LIME, w=4)
    return commit(base, L)


def route_chips(base):
    """the origin chips (a small legend stack): beam order + type glyph.  PANEL: removed in 11"""
    L = Layer()
    items = [("D", 1), ("D", 2), ("?", 3), ("?", 4), ("eye", 5)]
    x, y = 30, 420
    chip(L, (x - 6, y - 12, x + 74, y + 5 * 54 + 8))
    for i, (t, n) in enumerate(items):
        cy = y + 26 + i * 54
        if t in BEAM:
            g_type(L, t, (x + 22, cy), 17)
        elif t == "eye":
            g_eye(L, (x + 22, cy), 15, BEAM["E"])
        else:
            L.circle((x + 22, cy), 17, fill=(30, 36, 52), outline=(170, 180, 200), w=2.5)
            L.text((x + 22, cy), "?", f2(F_MONO, 24), (190, 198, 215))
        L.text((x + 56, cy), str(n), f2(F_MONO, 22), (200, 225, 240))
    return commit(base, L)


# ------------------------------------------------------------------------------- Cell's grease tally at HOME
def tally(base, counts, c, seed=3, size=17, gap=40, dim=0.0):
    """12 outcome glyphs in grease pencil, in tier order: the odds (a tally, not a chart)"""
    order = ["untouched", "holds", "lost", "damaged", "breach"]
    seq = []
    for t in order:
        seq += [t] * counts.get(t, 0)
    n = len(seq)
    x0 = c[0] - (n - 1) * gap / 2
    L = Layer()
    for i, t in enumerate(seq):
        tier_glyph(L, t, (x0 + i * gap, c[1]), size)
    out = spray_layer(base, L, (255, 255, 255), seed, outline=None, over_r=1.5, rough=.2)  # silhouette halo
    # recolour: draw the glyphs themselves again, crisp, atop a dark halo for contrast
    L2 = Layer()
    for i, t in enumerate(seq):
        p = (x0 + i * gap, c[1])
        L2.circle(p, size + 5, fill=INK, a=215)
    out = commit(base, L2)
    L3 = Layer()
    for i, t in enumerate(seq):
        tier_glyph(L3, t, (x0 + i * gap, c[1]), size)
    out = commit(out, L3)
    return out


def dock(base, launch=True):
    """bottom dock: the launch chip + the outcome strip (panels).  Removed in 11"""
    L = Layer()
    chip(L, (1160, 962, 1790, 1052))
    for k, (t, n) in enumerate((("untouched", 4), ("holds", 4), ("lost", 3), ("damaged", 1), ("breach", 0))):
        cx = 1206 + k * 124
        tier_glyph(L, t, (cx, 1007), 19)
        L.text((cx + 32, 1007), str(n), f2(F_MONO, 32), TIER[t] if n else (110, 120, 140), anchor="lm")
    chip(L, (800, 962, 1120, 1052))
    g_arrow(L, (960, 1007), 30, (255, 255, 255), line=INK)
    chip(L, (700, 982, 780, 1042))
    g_arrow(L, (740, 1012), 18, (160, 190, 210), ang=math.pi)
    return commit(base, L)


# ----------------------------------------------------------------------------------------------- frames
def f_decay():
    base = city()
    base = corp_layer(base)
    base, tops = pins(base, {"t1_a": "TAKEN", "t1_b": "TAKEN"})
    c = [A["t1_a"], A["t1_b"]]
    base = bloom(base.convert("RGB"), [(c[0][0], c[0][1] + 6), (c[1][0] + 10, c[1][1] + 8)], [120, 110], seed=5)
    base, tops = pins(base.convert("RGBA"), {"t1_a": "TAKEN", "t1_b": "TAKEN"}, only=("t1_a", "t1_b"))
    base = base.convert("RGBA")
    # cards fly: plum INFECTED stickers leave the sites for the HUD counter, spray trails
    L = Layer()
    tgt = (1580, 48)
    for k, (sp, ang) in enumerate(((tops["t1_a"], -.35), (tops["t1_b"], .3))):
        mid = ((sp[0] + tgt[0]) / 2, sp[1] - 260 - 60 * k)
        trail = []
        for t_ in np.linspace(0.03, 0.55 - .12 * k, 26):
            x = (1 - t_) ** 2 * sp[0] + 2 * (1 - t_) * t_ * mid[0] + t_ * t_ * tgt[0]
            y = (1 - t_) ** 2 * sp[1] + 2 * (1 - t_) * t_ * mid[1] + t_ * t_ * tgt[1]
            trail.append((x, y))
        for i, p in enumerate(trail[::2]):
            L.circle(p, 3 + i * .35, fill=VEIN, a=int(60 + i * 12))
        p = trail[-1]
        vinyl_card(L, p, 74, 98, ang, PLUM2, lambda L_, cc, s_: g_bio(L_, cc, s_ * 1.5, (255, 120, 205)))
    base = commit(base, L, glow=0.3)
    base = hud(base, inf=2, healthy=8)
    L = Layer()
    L.text((1664, 104), "+2", f2(F_MONO, 30), (255, 150, 215), anchor="mm", stroke=3, stroke_fill=INK)
    base = commit(base, L)
    return base


def f_draw():
    base = city()
    base = corp_layer(base)
    base = sealed_fog(base)
    base, hub, ends = hunter_layer(base)
    L = Layer()
    for n, num, prog in (("known0", 1, 1.0), ("known1", 2, 0.74)):
        pts = lane_path(n)
        tot = path_len(pts)
        draw_beam(L, pts, "D", 0, tot * prog)
        head(L, "D", pts, tot * prog, 26)
    base = commit(base, L, glow=0.45, glow_r=7)
    base, tops = pins(base, {"t1_a": "DOWN"})
    base = sealed_locks(base)
    # the corp 'drawing' sparks at the K2 head
    L = Layer()
    p, ang = point_at(lane_path("known1"), path_len(lane_path("known1")) * .74)
    for k in range(9):
        a2 = ang + math.pi + (k - 4) * .35
        L.line([p, (p[0] + math.cos(a2) * 26, p[1] + math.sin(a2) * 26)], (255, 255, 255), 2, a=180)
    base = commit(base, L, glow=.6)
    L = Layer()
    corp_ports = A["core"]
    order_dot(L, (corp_ports[0] - 28, corp_ports[1] + 24), 1)
    order_dot(L, (corp_ports[0] - 28, corp_ports[1] + 58), 2)
    base = commit(base, L)
    base = home_mark(base, A["home"])
    return hud(base)


def beams_known(base, prog=(1.0, 1.0), alpha=255, heads=True, order=True):
    L = Layer()
    for n, num, pr in (("known0", 1, prog[0]), ("known1", 2, prog[1])):
        pts = lane_path(n)
        tot = path_len(pts)
        draw_beam(L, pts, "D", 0, tot * pr, alpha=alpha)
        if heads:
            head(L, "D", pts, tot * pr, 20)
    return commit(base, L, glow=0.4, glow_r=7)


def f_plan(panels=True, final=True):
    base = city()
    base = corp_layer(base)
    base = sealed_fog(base)
    base, hub, ends = hunter_layer(base)
    base = beams_known(base, heads=False)
    # valid drop targets: corp white brackets on sites along K1/K2 (the corp 'knows' where you might act)
    placed = [("guard", "t1_b", "N")]
    base, tops = pins(base, {"t1_a": "DOWN"}, focus="t1_c")
    base = stencil_ground_all(base, placed)
    base = spray_shift(base, (A["t2_virus"][0] - 30, A["t2_virus"][1] + 28), (A["t2_virus"][0] + 80, A["t2_virus"][1] - 22), seed=7)
    base = glitch_sticker(base, (A["t2_breach"][0] - 6, A["t2_breach"][1] + 22), seed=4, size=44)
    base = sealed_locks(base)
    # drag: card in flight from the hand to the focused district, spray arrow trail
    cardp = (820, 800)
    tgt = gpos("t1_c")
    trail = []
    for t_ in np.linspace(0.0, 1.0, 30):
        x = (1 - t_) ** 2 * cardp[0] + 2 * (1 - t_) * t_ * 600 + t_ * t_ * tgt[0]
        y = (1 - t_) ** 2 * cardp[1] + 2 * (1 - t_) * t_ * 640 + t_ * t_ * tgt[1]
        trail.append((x, y))
    base = spray_path(base.convert("RGB"), trail[3:-3], BONE, 7, seed=11, drip_n=0, outline=INK, over_r=5).convert("RGBA")
    L = Layer()
    L.circle(tgt, 30, outline=INK, w=8)
    ground_ring(L, tgt, 38, LIME, w=4)
    base = commit(base, L, glow=0.3)
    L = Layer()
    vinyl_card(L, cardp, 104, 138, -.18, BEAM["D"], lambda L_, cc, s_: (g_shield(L_, cc, s_ * 1.2, (255, 255, 255), INK, lw=2.5), g_type(L_, "D", (cc[0], cc[1] + 3), s_ * .55)))
    base = commit(base, L)
    base = home_mark(base, A["home"])
    if panels:
        base = hand(base, [("guard", "D"), ("guard", "N"), ("guard", "E"), ("shift", None), ("ghost", None), ("guard", "D")], sel=None, lift=-10)
        base = route_chips(base)
    return hud(base)


def forecast_marks(base, dim=False):
    """shared by 04 and 11"""
    base = city() if base is None else base
    base = corp_layer(base)
    base = sealed_fog(base)
    base, hub, ends = hunter_layer(base)
    # K1 (D) stopped at t1_c by the D guard; K2 (D) lands t1_b
    L = Layer()
    p1 = lane_path("known0")
    s1 = site_s("known0", "t1_c")
    draw_beam(L, p1, "D", 0, s1)
    dead_beam(L, p1, s1, "D")
    p2 = lane_path("known1")
    s2 = site_s("known1", "t1_b")
    draw_beam(L, p2, "D", 0, s2)
    dead_beam(L, p2, s2, "D")
    pe, ae = point_at(p1, s1)
    flat_end(L, pe, ae, HOLDS)
    base = commit(base, L, glow=.4, glow_r=7)
    placed = [("guard", "t1_c", "D"), ("guard", "t1_b", "N")]
    base, tops = pins(base, {"t1_a": "DOWN"})
    base = stencil_ground_all(base, placed)
    base = spray_shift(base, (A["t2_virus"][0] - 30, A["t2_virus"][1] + 28), (A["t2_virus"][0] + 80, A["t2_virus"][1] - 22), seed=7)
    base = glitch_sticker(base, (A["t2_breach"][0] - 6, A["t2_breach"][1] + 22), seed=4, size=44)
    base = sealed_locks(base)
    # intent tiles (ITB): tier glyph + number on the target
    L = Layer()
    intent_tile(L, (tops["t1_c"][0] + 70, tops["t1_c"][1] - 20), "holds", s=30)
    intent_tile(L, (tops["t1_b"][0] - 70, tops["t1_b"][1] - 34), "lost", 1, s=30)
    hm = (A["home"][0] + 130, A["home"][1] - 60)
    intent_tile(L, hm, "damaged", -6, s=34)
    base = commit(base, L, glow=.35, glow_r=6)
    base = home_mark(base, A["home"])
    base = tally(base, {"untouched": 4, "holds": 4, "lost": 3, "damaged": 1}, (A["home"][0] + 150, A["home"][1] + 110))
    # corp 'computing': percent glyph streams at threatened Sites
    L = Layer()
    for sid, pct, off in (("t1_b", 100, (-60, -64)), ("t1_c", 100, (-74, -34))):
        pass
    base = commit(base, L)
    base = scan_band(base.convert("RGB"), 640, 130, x0=60, x1=1700).convert("RGBA")
    # computing numbers
    L = Layer()
    for sid, txt in (("t2_breach", "50%"), ("t2_virus", "50%"), ("t3_b", "100%")):
        p = tops[sid]
        L.text((p[0] + 36, p[1] - 6), txt, f2(F_MONO, 27), CORP, anchor="lm", stroke=4, stroke_fill=INK)
    base = commit(base, L, glow=.3)
    return hud(base)


def f_forecast():
    base = forecast_marks(None)
    return dock(base)


def f_panels_removed():
    return forecast_marks(None)


def response_discs(base, sel=1):
    verbs = [("DEPLOY", "deploy"), ("HOLD", "hold"), ("MOVE", "move"), ("SACRIFICE", "sac")]
    outs = {"deploy": ["untouched", "lost", "damaged"], "hold": ["holds", "lost", "damaged"], "move": ["untouched", "holds", "lost"], "sac": ["holds", "lost", "breach"]}
    for i, (word, key) in enumerate(verbs):
        c = (760 + i * 240, 925)
        L = Layer()
        L.circle(c, 68, fill=(10, 16, 30), a=240)
        L.circle(c, 68, outline=INK, w=8)
        if i == sel:
            L.circle(c, 78, outline=INK, w=8)
            L.circle(c, 78, outline=LIME, w=4)
        base = commit(base, L)
        base = glyph_disc(base, c, key, seed=40 + i).convert("RGBA")
        L = Layer()
        chip(L, (c[0] - 56, c[1] - 128, c[0] + 56, c[1] - 88), a=235)
        for k, t in enumerate(outs[key]):
            tier_glyph(L, t, (c[0] + (k - 1) * 34, c[1] - 108), 13)
        base = commit(base, L)
        base = tag_text(base, (c[0], c[1] + 100), word, 30 if word != "SACRIFICE" else 25, BONE, seed=60 + i, tilt=-.05, drip=False)
    return base


def f_response():
    base = forecast_marks(None)
    base = darken(base, 0.62).convert("RGBA")
    base = response_discs(base)
    # the worst case at HOME stays loud
    return hud(base)


def ring_pulse(base, c, r, col, w=5, a=200):
    L = Layer()
    ground_ring(L, c, r, col, w=w, a=a)
    return commit(base, L, glow=.6, glow_r=10)


def f_playout_impact():
    base = city()
    base = corp_layer(base)
    base = commit(base, Layer())
    L = Layer()
    p1 = lane_path("known0")
    s1 = site_s("known0", "t1_c")
    draw_beam(L, p1, "D", 0, s1)
    p2 = lane_path("known1")
    draw_beam(L, p2, "D", 0, path_len(p2), alpha=60, chev=False)
    base = commit(base, L, glow=.5, glow_r=7)
    base, tops = pins(base, {"t1_a": "DOWN"}, dim=("t2_breach", "t2_virus", "t3_b", "t3_c", "t3_core", "t2_intel"))
    c = gpos("t1_c")
    base = stencil_guard(base, c, "D", seed=sh("t1_c"), size=42)
    base = stencil_ground_all(base, [("guard", "t1_b", "N")])
    base = hex_flash(base, (c[0], c[1] - 10), 86, col=(90, 170, 255))
    base = splat(base.convert("RGB"), (c[0] + 8, c[1] + 4), 70, BEAM["D"], seed=21, outline=INK).convert("RGBA")
    base = shatter(base, (c[0] + 4, c[1] - 24), 108, seed=3)
    L = Layer()
    pe, ang = point_at(p1, s1 - 20)
    g_type(L, "D", pe, 22)
    base = commit(base, L, glow=.5)
    L = Layer()
    intent_tile(L, (tops["t1_c"][0] + 70, tops["t1_c"][1] - 20), "holds", s=30)
    base = commit(base, L, glow=.4)
    base = home_mark(base, A["home"])
    return hud(base)


def f_playout_home():
    base = city()
    base = corp_layer(base)
    L = Layer()
    p = WORLD["paths"]["cand1"]  # the N beam arrives by the sealed route C (revealed N)
    pn = lane_path("cand2", 0)
    draw_beam(L, pn, "N", 0, path_len(pn))
    base = commit(base, L, glow=.6, glow_r=8)
    base, tops = pins(base, {"t1_a": "DOWN"}, dim=("t2_breach", "t2_virus", "t3_b", "t3_c", "t3_core", "t2_intel"))
    h = A["home"]
    base = home_mark(base, h)
    # impact at HOME: glass shatter over the whole HOME region, orange paint splat
    base = splat(base.convert("RGB"), (h[0], h[1] - 10), 96, DAMAGED, seed=31, outline=INK).convert("RGBA")
    base = shatter(base, (h[0], h[1] - 52), 200, seed=7, tint=(255, 214, 170), shard_a=2.2)
    base = ring_pulse(base, h, 120, (255, 190, 120), 6, 220)
    base = ring_pulse(base, h, 190, (255, 190, 120), 3, 120)
    L = Layer()
    g_heart(L, (h[0], h[1] - 92 * 1.0), 34, (255, 110, 120), INK)
    pe, ang = point_at(pn, path_len(pn) - 12)
    g_type(L, "N", pe, 24)
    base = commit(base, L, glow=.6)
    # -6 and the damaged tile
    L = Layer()
    intent_tile(L, (h[0] + 140, h[1] - 130), "damaged", s=30)
    base = commit(base, L, glow=.5)
    base = tag_text(base, (h[0] + 270, h[1] - 128), "-6", 78, DAMAGED, seed=44, tilt=-.1, over_r=5)
    # corp sterile alert frame (cold, exact): corner brackets + scan hairlines, tinted by the tier
    L = Layer()
    for (x, y, sx, sy) in ((14, 100, 1, 1), (W - 14, 100, -1, 1), (14, H - 14, 1, -1), (W - 14, H - 14, -1, -1)):
        L.line([(x, y + sy * 70), (x, y), (x + sx * 70, y)], CORP, 4, a=230)
    base = commit(base, L, glow=.4)
    base = hud(base, home=38, home_col=DAMAGED)
    return base


def verdict_poster(c, tier, w=360, h=330, ang=-.07):
    col = TIER[tier]
    x0, y0 = c[0] - w / 2, c[1] - h / 2

    def draw(L, rect, a_, cc):
        x0, y0, x1, y1 = rect
        L.rrect((x0 + 16, y0 + 16, x1 - 16, y1 - 16), 4, fill=col)
        g = lambda x, y: max(0.0, min(1.0, 1.0 - (y - y0) / (y1 - y0))) * 0.95
        halftone(L, (x0 + 16, y0 + 16, x1 - 16, y1 - 16), (150, 52, 8), ang=.6, step=11, grad=g)
        if tier == "damaged":
            g_heart_broken(L, (cc[0], cc[1] - 22), 92, (252, 246, 232), line=INK)
        elif tier == "holds":
            g_shield(L, (cc[0], cc[1] - 22), 92, (252, 246, 232), INK, lw=4)
        elif tier == "lost":
            g_square_slash(L, (cc[0], cc[1] - 22), 88, (252, 246, 232))
        L.text((cc[0], y1 - 62), tier_word(tier), f2(F_ANTON, 64), (252, 246, 232), stroke=3, stroke_fill=INK)
        L.rrect((x0 + 8, y0 + 8, x1 - 8, y1 - 8), 6, outline=INK, w=3)
    return draw, (x0, y0, x0 + w, y0 + h), ang


def tier_word(t):
    return {"untouched": "UNTOUCHED", "holds": "HOLDS", "lost": "SITES LOST", "damaged": "DAMAGED", "breach": "BREACHED"}[t]


def f_aftermath():
    base = city()
    L = Layer()
    base = commit(base, corp_lattice(26))
    L = Layer()
    corp_hq(L, A["core"])
    base = commit(base, L, glow=.3)
    base, tops = pins(base, {"t1_a": "DOWN", "t1_b": "DOWN"})
    L = Layer()
    for sid in ("t1_a", "t1_b"):
        L.circle(tops[sid], 30, outline=INK, w=8)
        ring = tops[sid]
        for k in range(10):
            a0 = k / 10 * 360
            L.d.arc([(ring[0] - 30) * SS, (ring[1] - 30) * SS, (ring[0] + 30) * SS, (ring[1] + 30) * SS], a0, a0 + 22, fill=GREASE + (255,), width=int(5 * SS))
    base = commit(base, L)
    # burned beams: dim ghost trails
    L = Layer()
    for n in ("known0", "known1"):
        for p in resample(lane_path(n), 18):
            L.circle(p, 3.6, fill=(140, 150, 178), a=150)
    base = commit(base, L)
    h = A["home"]
    base = home_mark(base, h)
    L = Layer()
    for dx in (-26, 6):  # cracks in the ring
        L.line([(h[0] + dx, h[1] + 20), (h[0] + dx + 12, h[1] + 30), (h[0] + dx + 4, h[1] + 44)], INK, 3)
    base = commit(base, L)
    draw, rect, ang = verdict_poster((760, 820), "damaged", 380, 340)
    base = poster(base.convert("RGBA"), rect, ang, (240, 228, 200), INK, draw, seed=5).convert("RGBA")
    base = hud(base, home=38, home_col=DAMAGED)
    return base


def f_hq_step():
    base = city()
    base = commit(base, corp_lattice(30))
    L = Layer()
    corp_hq(L, A["core"])
    base = commit(base, L, glow=.3)
    base, tops = pins(base, {"t1_a": "DOWN", "t1_b": "DOWN"}, focus="t1_b")
    h = A["home"]
    base = home_mark(base, h)
    # ghost preview: a repaired t1_b shown as a mint stencil outline on the DOWN pin
    L = Layer()
    tb = tops["t1_b"]
    g_hex(L, tb, 24, fill=None, line=UNTOUCHED, w=3, a=255)
    tier_glyph(L, "untouched", (tb[0] + 60, tb[1] - 30), 15)
    base = commit(base, L, glow=.4)
    # spray arrow from the wrench disc to the DOWN site
    discs = [(h[0] + 110, h[1] - 190, "wrench", 10), (h[0] + 290, h[1] - 120, "shield+", 20), (h[0] + 390, h[1] + 20, "flame-", 25), (h[0] + 330, h[1] + 170, "card", 15), (h[0] + 170, h[1] + 215, "plus", 30)]
    base = spray_shift(base, (discs[0][0] + 30, discs[0][1] - 52), (tops["t1_b"][0] - 40, tops["t1_b"][1] + 55), seed=15, col=UNTOUCHED)
    for i, (x, y, key, price) in enumerate(discs):
        c = (x, y)
        L = Layer()
        L.circle(c, 58, fill=(10, 16, 30), a=240)
        L.circle(c, 58, outline=INK, w=8)
        if i == 0:
            L.circle(c, 68, outline=INK, w=8)
            L.circle(c, 68, outline=LIME, w=4)
        base = commit(base, L)
        base = glyph_disc(base, c, key, seed=70 + i).convert("RGBA")
        L = Layer()
        chip(L, (c[0] + 20, c[1] + 36, c[0] + 84, c[1] + 74), a=240)
        L.text((c[0] + 52, c[1] + 55), str(price), f2(F_MONO, 28), (255, 235, 200))
        base = commit(base, L)
    # continue chip
    L = Layer()
    chip(L, (1700, 972, 1880, 1052))
    g_arrow(L, (1790, 1012), 28, (255, 255, 255), line=INK)
    base = commit(base, L)
    return hud(base, home=38, home_col=(230, 250, 255))


def f_city_lost():
    base = city()
    base = commit(base, corp_lattice(40))
    L = Layer()
    corp_hq(L, A["core"])
    base = commit(base, L, glow=.3)
    cs = [A[s] for s in ("t1_a", "t1_b", "t1_c", "t1_d", "t2_breach", "t2_virus")] + [A["home"]]
    rs = [150, 160, 150, 120, 170, 150, 190]
    base = bloom(base.convert("RGB"), cs, rs, seed=9, glyph=False).convert("RGBA")
    # the flood keeps running along the corridor toward the corp
    cs2 = [A["t2_intel"], A["t3_b"], A["t3_c"], A["t3_core"]]
    base = bloom(base.convert("RGB"), cs2, [90, 80, 80, 70], seed=12, glyph=False).convert("RGBA")
    base, tops = pins(base, {s: "TAKEN" for s in ("t1_a", "t1_b", "t1_c", "t1_d")})
    # AR glass: the corp's projection cracked from edge to edge
    base = shatter(base, (1130, 470), 430, seed=17, tint=(190, 170, 235), bits=True, shard_a=1.4)
    # the skull: white stencil, plum drips, big
    L = Layer()
    g_skull(L, (700, 520), 210, (250, 246, 238))
    m = layer_to_mask(L)
    rng = np.random.default_rng(3)
    mi = Image.fromarray((m * 255).astype(np.uint8))
    d = ImageDraw.Draw(mi)
    ys, xs = np.where(m > .5)
    for _ in range(14):
        i = rng.integers(0, len(xs))
        if ys[i] < 560:
            continue
        x, y = xs[i], ys[i]
        ln = rng.uniform(40, 120)
        d.line([(x, y), (x, y + ln)], fill=255, width=5)
        d.ellipse((x - 5, y + ln - 4, x + 5, y + ln + 7), fill=255)
    mm = mask_np(mi)
    base = over(base, spray_rgba(np.clip(gaussian_filter(mm, 4) * 3, 0, 1), INK, 8, over_r=3, over_k=.1, rough=.3, alpha=.92))
    base = over(base, spray_rgba(mm, (250, 246, 238), 6, over_r=9, rough=.55), glow=.3, glow_r=14)
    base = hud(base, inf=9, healthy=8)
    return base


def f_reveal():
    """12: the SEALED reveal (lock A opens, its fog tears away, the route lights in its type) and the HUNTER lock-on (brackets snap on one street, the other is crossed out)"""
    base = city()
    base = corp_layer(base)
    base = fog_band(base, ["cand1", "cand2"], seed=9)
    L = Layer()
    pa = WORLD["paths"]["cand0"]
    draw_beam(L, pa, "E", 0, path_len(pa) * 0.8)
    base = commit(base, L, glow=.7, glow_r=8)
    base, hub, ends = hunter_layer(base, locked=1)
    base, tops = pins(base, {"t1_a": "DOWN"})
    # locks: B and C still shut, A is open and breaking
    pos = {"B": A["t2_virus"], "C": A["t2_breach"]}
    L = Layer()
    for k, c in pos.items():
        cx = (c[0] - 84, c[1] - 36)
        L.line([c, cx], (170, 180, 200), 2, a=200)
        L.circle(cx, 31, fill=(10, 16, 30), outline=(170, 180, 200), w=3.5)
        g_lock(L, (cx[0], cx[1] - 1), 16, (190, 198, 215))
    ca = (A["t1_a"][0] - 84, A["t1_a"][1] - 36)
    L.line([A["t1_a"], ca], BEAM["E"], 3)
    L.circle(ca, 33, fill=(10, 16, 30), outline=BEAM["E"], w=4)
    g_lock_open(L, (ca[0], ca[1] + 2), 16, BEAM["E"])
    base = commit(base, L, glow=.5, glow_r=6)
    base = bitburst(base, ca, 70, 5, col=(255, 240, 160), n=26)
    for k, c in pos.items():
        base = tag_text(base, (c[0] - 84, c[1] - 104), k, 64, BONE, seed=ord(k), tilt=-.18)
    base = tag_text(base, (ca[0], ca[1] - 68), "A", 78, BEAM["E"], seed=ord("A"), tilt=-.18)
    # E head arrives
    L = Layer()
    p = point_at(pa, path_len(pa) * 0.8)[0]
    g_type(L, "E", p, 26)
    base = commit(base, L, glow=.6)
    base = home_mark(base, A["home"])
    return hud(base)


FRAMES = [
    ("01_decay", f_decay), ("02_draw", f_draw), ("03_plan", f_plan), ("04_forecast", f_forecast),
    ("05_response", f_response), ("06_playout_impact", f_playout_impact), ("07_playout_home", f_playout_home),
    ("08_aftermath", f_aftermath), ("09_hq_step", f_hq_step), ("10_city_lost", f_city_lost),
    ("11_panels_removed", f_panels_removed), ("12_reveal_sealed_hunter", f_reveal),
]

if __name__ == "__main__":
    only = sys.argv[1:]
    for n, fn in FRAMES:
        if only and not any(n.startswith(o) for o in only):
            continue
        t = time.time()
        im = fn().convert("RGB")
        im.save(os.path.join(OUT, n + ".png"))
        print(n, round(time.time() - t, 1), "s", flush=True)
