"""RAIN NOIR building blocks: marker ink, spinners, sticker cards, glass panels, rain, shards, city."""
import math, random
import bpy
from mathutils import Vector
from rn_lib import *  # noqa
import stroke_font as SF

R90 = math.radians(90)
SLICE_COL = {"atk": "pink", "crit": "pink", "def": "cyan", "evd": "gain", "afl": "afflict", "dep": "#B08CFF", "miss": "#6A6A6A"}


# ================================================================ marker (Grease Pencil)
def marker(gp, txt, x_px, base_px, h_px, depth=-0.4, progress=1.0, seed=7, drips=None, angle_deg=-3.0,
           color="pink", nib=True, layer="marker"):
    """Pink marker words drawn as GP strokes over the UI.
    drips: None | dict(stage='forming'|'running', count=int, run_px=float, bottom_px=float)"""
    rng = random.Random(seed)
    strokes, width = SF.layout(txt, h_px, seed=seed)
    strokes, nibp = SF.truncate(strokes, progress)
    ca, sa = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))

    def W(p):  # layout px (y up) -> world
        x, y = p.x * ca - p.y * sa, p.x * sa + p.y * ca
        return P(x_px + x, base_px - y, depth)

    r0 = S(h_px * 0.072, depth)
    m_bleed = gp.mat("mk_bleed", "#B0126A", 0.55)
    m_main = gp.mat("mk_main", color)
    m_sheen = gp.mat("mk_sheen", "#FFB3DC", 0.75)
    for s in strokes:
        n = len(s)
        rad = [r0 * (0.78 + 0.3 * math.sin(math.pi * min(1.0, (i / max(1, n - 1)) * 1.15))) * (1 + rng.uniform(-0.05, 0.05)) for i in range(n)]
        pts = [W(p) for p in s]
        gp.stroke(layer + "_bleed", [p + Vector((0.0, 0.01, 0.0)) for p in pts], [r * 1.2 for r in rad], m_bleed, 0.6)
        gp.stroke(layer, pts, rad, m_main, 1.0)
        off = Vector((-r0 * 0.25, -0.01, r0 * 0.3))
        gp.stroke(layer + "_sheen", [p + off for p in pts[1:-1]], [r * 0.22 for r in rad[1:-1]], m_sheen, [0.2 + 0.6 * rng.random() for _ in rad[1:-1]])
    if nib and progress < 1.0 and nibp is not None:
        tip = W(nibp)
        body = gp.mat("nib_body", "#aebfd6", 1.0, fill="#23272f")
        capm = gp.mat("nib_cap", "pink", 1.0, fill="pink")
        d = Vector((S(46, depth), 0, S(80, depth)))
        side = Vector((S(22, depth), 0, -S(12, depth)))
        poly = [tip + side * 0.35, tip + d + side, tip + d * 4.2 + side, tip + d * 4.2 - side, tip + d - side, tip - side * 0.35]
        gp.stroke("nib", poly, S(1.6, depth), body, 1.0, cyclic=True, fill=True)
        gp.stroke("nib", [tip, tip + d * 0.6], S(9, depth), capm, 1.0)
        gp.stroke("nib", [tip + d * 3.2 + side * 1.15, tip + d * 3.2 - side * 1.15], S(10, depth), capm, 1.0)
    if drips and strokes:
        roots = SF.drip_roots(strokes, rng, drips.get("count", 4), h_px)
        for rt in roots:
            start = W(rt)
            stage = drips.get("stage", "forming")
            if stage == "forming":
                L = S(rng.uniform(0.18, 0.5) * h_px, depth)
            else:
                L = S(rng.uniform(0.6, 1.0) * drips.get("run_px", 400), depth)
            n = 22
            pts, rad = [], []
            wob = rng.uniform(-0.03, 0.03)
            for i in range(n + 1):
                t = i / n
                pts.append(start + Vector((wob * t * L + 0.01 * math.sin(t * 9 + rng.random()), -0.005, -L * t)))
                rad.append(r0 * (0.85 - 0.45 * min(1, t * 2.2) + (0.08 if stage == "running" else 0)))
            # bulb
            bulb = r0 * (1.25 if stage == "forming" else 1.0)
            rad[-1] = bulb; rad[-2] = bulb * 0.95; rad[-3] = bulb * 0.7
            gp.stroke(layer + "_bleed", pts, [r * 1.18 for r in rad], m_bleed, 0.55)
            gp.stroke(layer, pts, rad, m_main, 1.0)
            gp.stroke(layer + "_sheen", [p + Vector((-r0 * 0.2, -0.01, 0)) for p in pts[2:-1]], [r * 0.25 for r in rad[2:-1]], m_sheen, 0.5)
            if stage == "running":
                # a second, thinner trailing drip and a separated droplet further down
                d2 = start + Vector((0, -0.005, -L - S(rng.uniform(30, 90), depth)))
                gp.stroke(layer, [d2, d2 + Vector((0, 0, -S(8, depth)))], r0 * 0.75, m_main, 1.0)
    return width


# ================================================================ spinner
def spinner(name, cx, cy, r_px, slices, owner, ornament="rivets", label="BREAKER", sub="core", tilt=(8, 0),
            spill=220.0, hp=(60, 60), hp_side="gain", depth=0.0, rot_offset_ticks=0):
    """A 3D layered spinner: console housing, bezel with emissive inlay, slice tray, chrome ring, recessed hub,
    glass dome, pointer. Local XY = screen plane, local +Z = toward camera."""
    R = S(r_px, depth)
    c = P(cx, cy, depth)
    root = empty(name, c, (R90 + math.radians(tilt[0]), 0, math.radians(tilt[1])))
    m_house = mat_pbr("house", "#0b0e14", 0.42, 0.6, coat=0.4)
    m_bezel = mat_pbr("bezel_" + name, "#2a2f38", 0.26, 0.9)
    m_chrome = mat_pbr("chrome", "#d9e2ee", 0.08, 1.0)
    m_tray = mat_pbr("tray", "#030406", 0.6, 0.2)
    m_hub = mat_pbr("hub", "#070a10", 0.12, 0.3, coat=1.0)
    m_inlay = mat_emit("inlay_" + name, owner, 9.0)
    m_inlay2 = mat_emit("inlay2_" + name, owner, 2.5)
    m_tick = mat_emit("tick", "#cfd9e6", 1.6)
    m_tick5 = mat_emit("tick5", "#ffffff", 4.0)
    m_txt = mat_emit("sl_txt", "#ffffff", 3.0)
    m_hubtxt = mat_emit("hub_txt", "text_mid", 1.8)
    # console housing (instrument well)
    disc(name + "_house", R * 1.45, 0.5, m_house, (0, 0, -0.55), parent=root)
    ring_sector(name + "_lip", R * 1.28, R * 1.45, 0, 2 * math.pi, 0.18, m_house, (0, 0, -0.3), parent=root, bevel=0.03)
    # bezel
    ring_sector(name + "_bezel", R * 1.0, R * 1.2, 0, 2 * math.pi, 0.5, m_bezel, (0, 0, -0.25), parent=root, bevel=0.04)
    torus(name + "_inlay", R * 1.11, 0.022, m_inlay, (0, 0, 0.26), parent=root)
    torus(name + "_inlay_in", R * 1.025, 0.012, m_inlay2, (0, 0, 0.255), parent=root)
    if ornament == "rivets":
        for i in range(18):
            a = 2 * math.pi * i / 18 + 0.1
            cyl(name + "_rv%d" % i, 0.05, 0.08, m_chrome, (R * 1.165 * math.cos(a), R * 1.165 * math.sin(a), 0.27), parent=root, seg=12)
    elif ornament == "rings":
        m_orn = mat_emit("orn_" + name, owner, 3.0)
        for k, rr in enumerate((1.06, 1.15, 1.18)):
            torus(name + "_orn%d" % k, R * rr, 0.008, m_orn, (0, 0, 0.255), parent=root)
    # tray under slices
    ring_sector(name + "_tray", R * 0.55, R * 1.0, 0, 2 * math.pi, 0.1, m_tray, (0, 0, -0.25), parent=root)
    # rim light catch on the bezel's upper-left edge and a cool one on the housing lip
    m_rim = mat_emit("rimcatch", "#dfe9ff", 3.5)
    ring_sector(name + "_rimc", R * 1.185, R * 1.205, math.radians(95), math.radians(170), 0.01, m_rim, (0, 0, 0.255), parent=root)
    ring_sector(name + "_rimc2", R * 1.43, R * 1.45, math.radians(60), math.radians(150), 0.01, mat_emit("rimcatch2", "#9fb4d8", 1.6), (0, 0, -0.12), parent=root)
    m_rim_o = mat_emit("rimown_" + name, owner, 1.2)
    ring_sector(name + "_rimo", R * 1.43, R * 1.45, math.radians(-160), math.radians(-20), 0.01, m_rim_o, (0, 0, -0.12), parent=root)
    # ticks
    for t in range(30):
        a = math.radians(90 - t * 12 - 6)
        big = t % 5 == 0
        L = 0.16 if big else 0.08
        box(name + "_tk%d" % t, (R * 0.975 * math.cos(a), R * 0.975 * math.sin(a), 0.02), (0.028 if big else 0.018, L, 0.04),
            m_tick5 if big else m_tick, rot=(0, 0, a - math.pi / 2), parent=root)
    # slices
    t0 = rot_offset_ticks
    gap = math.radians(0.9)
    for i, (kind, n, val) in enumerate(slices):
        a1 = math.radians(90 - t0 * 12)
        a0 = math.radians(90 - (t0 + n) * 12)
        colr = SLICE_COL[kind]
        m = mat_pbr("sl_%s" % kind, "#101318", 0.3, 0.0, emit=colr, emit_str=1.4 if kind != "miss" else 0.4)
        ring_sector("%s_sl%d" % (name, i), R * 0.6, R * 0.94, a0 + gap, a1 - gap, 0.12, m, (0, 0, -0.14), parent=root, bevel=0.012)
        am = (a0 + a1) / 2
        text(str(val), (R * 0.77 * math.cos(am), R * 0.77 * math.sin(am), 0.0), S(34, depth), m_txt, ANTON, "CENTER", "CENTER", rot=(0, 0, 0), parent=root)
        t0 += n
    # chrome ring and recessed hub
    torus(name + "_chrome", R * 0.585, 0.045, m_chrome, (0, 0, 0.02), parent=root)
    disc(name + "_hub", R * 0.56, 0.1, m_hub, (0, 0, -0.26), parent=root)
    ring_sector(name + "_hubarc1", R * 0.44, R * 0.465, math.radians(20), math.radians(160), 0.01, m_inlay2, (0, 0, -0.2), parent=root)
    ring_sector(name + "_hubarc2", R * 0.44, R * 0.465, math.radians(200), math.radians(340), 0.01, m_inlay2, (0, 0, -0.2), parent=root)
    text(label, (0, S(6, depth), -0.19), S(30, depth), m_hubtxt, ANTON, "CENTER", "CENTER", rot=(0, 0, 0), parent=root, spacing=1.1)
    text(sub, (0, -S(26, depth), -0.19), S(16, depth), m_hubtxt, MONO, "CENTER", "CENTER", rot=(0, 0, 0), parent=root)
    # glass dome
    dome(name + "_dome", R * 1.02, 0.55, mat_glass_dome("dome"), (0, 0, 0.25), parent=root)
    # the dome reflects a rain-streaked window: a soft pane highlight on its upper-left shoulder
    m_refl = mat_emit("dome_refl", "#dce8ff", 1.2, alpha=0.16)
    ring_sector(name + "_refl", R * 0.7, R * 0.9, math.radians(112), math.radians(158), 0.0, m_refl, (0, 0, 0.62), parent=root)
    ring_sector(name + "_refl2", R * 0.62, R * 0.67, math.radians(118), math.radians(150), 0.0, m_refl, (0, 0, 0.66), parent=root)
    m_refl3 = mat_emit("dome_refl3", "#ffffff", 2.0, alpha=0.3)
    ring_sector(name + "_refl3", R * 0.91, R * 0.935, math.radians(20), math.radians(70), 0.0, m_refl3, (0, 0, 0.45), parent=root)
    # pointer (acid)
    m_acid = mat_emit("acid", "acid", 6.0)
    ptr = ring_sector(name + "_ptr", R * 1.22, R * 1.34, math.radians(86), math.radians(94), 0.1, m_acid, (0, 0, 0.2), parent=root)
    box(name + "_ptr2", (0, R * 1.05, 0.33), (0.05, 0.3, 0.05), m_acid, parent=root)
    # HP arc on the lip
    frac = hp[0] / hp[1]
    m_hp = mat_emit("hp_" + hp_side, hp_side, 5.0)
    m_hpbg = mat_emit("hpbg", "#1d2430", 1.0)
    a_start, a_end = math.radians(-150), math.radians(-30)
    ring_sector(name + "_hpbg", R * 1.3, R * 1.36, a_start, a_end, 0.02, m_hpbg, (0, 0, -0.1), parent=root)
    ring_sector(name + "_hp", R * 1.3, R * 1.36, a_start, a_start + (a_end - a_start) * frac, 0.03, m_hp, (0, 0, -0.1), parent=root)
    # spill light (feedback 10): the wheel's glow lights neighbouring UI and the wet ground
    point(c + Vector((0, -1.8, 0.2)), owner, spill, radius=R * 0.9, name=name + "_spill", shadow=False)
    point(c + Vector((0, -0.6, -R * 0.9)), owner, spill * 0.35, radius=0.6, name=name + "_spill_lo", shadow=False)
    return root, c, R


# ================================================================ glass panel
def glass_panel(gp, name, x, y, w, h, depth=0.1, edge="cyan", title=None, rule="pink", alpha=0.86, rough=0.22):
    """Terminal glass: dark navy glossy (so spill shows as sheen), 1 px cyan edge (GP), pink title rule."""
    c = P(x + w / 2, y + h / 2, depth)
    m = mat_pbr("glass_panel_%.2f_%.2f" % (alpha, rough), "#050d1c", rough, 0.0, alpha=alpha, coat=0.6 if rough < 0.3 else 0.0)
    ob = rrect(name, S(w, depth), S(h, depth), S(6, depth), c, m)
    em = gp.mat("edge_" + edge, edge, 0.75)
    corners = [P(x, y, depth - 0.02), P(x + w, y, depth - 0.02), P(x + w, y + h, depth - 0.02), P(x, y + h, depth - 0.02)]
    gp.stroke("ui", corners, S(0.8, depth), em, 0.85, cyclic=True)
    if title:
        text(title, P(x + 14, y + 20, depth - 0.03), S(17, depth), mat_emit("ui_hi", "text_mid", 1.6), MONO, "LEFT", "CENTER")
        mr = gp.mat("rule_" + rule, rule, 1.0)
        gp.stroke("ui", [P(x + 14, y + 36, depth - 0.03), P(x + w - 14, y + 36, depth - 0.03)], S(1.1, depth), mr, 0.9)
    return ob


def ui_text(body, x, y, size, color="text_hi", strength=1.8, fnt=MONO, align="LEFT", depth=0.05, name="uit", alpha=1.0):
    key = "uitx_%s_%.2f_%.2f" % (color, strength, alpha)
    return text(body, P(x, y, depth), S(size, depth), mat_emit(key, color, strength, alpha), fnt, align, "CENTER", name=name)


# ================================================================ sticker card
def sticker_card(gp, name, x, y, w, h, rot_deg, title, cost, accent="pink", desc="", depth=0.0, slap=False, seed=3):
    """A card slapped on as a die-cut sticker: white backing, paper face, hard shadow, tape."""
    rng = random.Random(seed)
    c = P(x, y, depth)
    th = math.radians(rot_deg)
    root = empty(name, c, (R90, th, 0))
    k = lambda px: S(px, depth)
    m_back = mat_pbr("stk_back", "#f7f5ef", 0.7, emit="#f7f5ef", emit_str=0.25)
    m_paper = mat_pbr("stk_paper", "paper", 0.75, emit="paper", emit_str=0.3)
    m_ink = mat_pbr("stk_ink", "ink", 0.8)
    m_shadow = mat_pbr("stk_shadow", "#000000", 1.0, alpha=0.62 if not slap else 0.38)
    m_acc = mat_pbr("stk_acc_" + accent, accent, 0.6, emit=accent, emit_str=0.35)
    m_tape = mat_pbr("stk_tape", "#e8dcb8", 0.9, alpha=0.55, emit="#e8dcb8", emit_str=0.15)
    so = (k(10), -k(13)) if not slap else (k(26), -k(34))
    rrect(name + "_sh", k(w + 14), k(h + 14), k(16), (so[0], so[1], -0.03), m_shadow, rot=(0, 0, 0), parent=root)
    rrect(name + "_bk", k(w + 14), k(h + 14), k(16), (0, 0, 0), m_back, rot=(0, 0, 0), parent=root)
    rrect(name + "_pp", k(w), k(h), k(10), (0, 0, 0.004), m_paper, rot=(0, 0, 0), parent=root)
    # title + cost
    text(title, (-k(w / 2 - 12), k(h / 2 - 22), 0.01), k(22), m_ink, ANTON, "LEFT", "CENTER", rot=(0, 0, 0), parent=root)
    disc(name + "_cost", k(15), 0.01, mat_pbr("stk_acid", "acid", 0.6, emit="acid", emit_str=0.4), (k(w / 2 - 22), k(h / 2 - 22), 0.01), rot=(0, 0, 0), parent=root, seg=32)
    text(str(cost), (k(w / 2 - 22), k(h / 2 - 23), 0.018), k(20), m_ink, ANTON, "CENTER", "CENTER", rot=(0, 0, 0), parent=root)
    # art window: two-colour riso wheel
    rrect(name + "_art", k(w - 22), k(h * 0.42), k(4), (0, k(h * 0.02), 0.008), mat_pbr("stk_artbg", "#efe6d6", 0.8, emit="#efe6d6", emit_str=0.3), rot=(0, 0, 0), parent=root)
    ring_sector(name + "_w", k(h * 0.1), k(h * 0.155), 0, 2 * math.pi, 0.004, m_acc, (0, k(h * 0.02), 0.012), parent=root)
    ring_sector(name + "_w2", k(h * 0.1), k(h * 0.155), math.radians(40), math.radians(130), 0.004, m_ink, (0, k(h * 0.02), 0.014), parent=root)
    for i in range(6):
        a = math.radians(i * 60 + 15)
        box(name + "_sp%d" % i, (k(h * 0.13) * math.cos(a), k(h * 0.02) + k(h * 0.13) * math.sin(a), 0.016), (k(3), k(h * 0.055), 0.002), m_ink, rot=(0, 0, a - math.pi / 2), parent=root)
    if desc:
        text(desc, (-k(w / 2 - 12), -k(h * 0.3), 0.01), k(13), m_ink, MONO, "LEFT", "CENTER", rot=(0, 0, 0), parent=root)
    # tape
    rrect(name + "_tape", k(w * 0.45), k(18), k(1), (k(rng.uniform(-10, 10)), k(h / 2 + 2), 0.02), m_tape, rot=(0, 0, math.radians(rng.uniform(-6, 6))), parent=root)
    if slap:
        # speed lines + water spray off the wet glass as it lands
        ml = gp.mat("slap", "#e9f1ff", 0.8)
        mdrop = gp.mat("drop", "#bcd3ee", 0.9)
        for i in range(14):
            a = math.radians(18 + i * 11 + rng.uniform(-4, 4))
            r1 = rng.uniform(0.6, 0.66) * max(w, h)
            r2 = r1 + rng.uniform(40, 90)
            p1 = P(x + r1 * math.cos(a), y - r1 * math.sin(a) * 0.8, depth - 0.1)
            p2 = P(x + r2 * math.cos(a), y - r2 * math.sin(a) * 0.8, depth - 0.1)
            gp.stroke("fx", [p1, p2], [S(3.2, depth), S(0.5, depth)], ml, 0.85)
        for i in range(40):
            a = rng.uniform(0, 2 * math.pi)
            r = rng.uniform(0.55, 0.95) * max(w, h) * 0.75
            p = P(x + r * math.cos(a), y + r * math.sin(a) * 0.85, depth - 0.12)
            gp.stroke("fx", [p, p + Vector((S(3, depth) * math.cos(a), 0, -S(3, depth) * math.sin(a)))], S(rng.uniform(1.8, 4.5), depth), mdrop, rng.uniform(0.4, 0.9))
    return root


# ================================================================ rain
def rain(gp, n, seed, xr, yr, zr, length=(0.4, 1.4), radius=(0.004, 0.012), slant=0.16, alpha=(0.12, 0.45), layer="rain", color="rain"):
    rng = random.Random(seed)
    m = gp.mat("rain_" + color, color)
    for _ in range(n):
        p = Vector((rng.uniform(*xr), rng.uniform(*yr), rng.uniform(*zr)))
        L = rng.uniform(*length)
        d = Vector((slant, 0, -1)).normalized() * L
        r = rng.uniform(*radius)
        a = rng.uniform(*alpha)
        gp.stroke(layer, [p, p + d * 0.5, p + d], [r * 0.5, r, r * 0.4], m, [a * 0.4, a, a * 0.2])


def splashes(gp, n, seed, xr, yr, z, size=(0.05, 0.18), layer="splash", alpha=0.5):
    rng = random.Random(seed)
    m = gp.mat("splash", "#9fb6d4")
    for _ in range(n):
        c = Vector((rng.uniform(*xr), rng.uniform(*yr), z + 0.01))
        s = rng.uniform(*size)
        pts = [c + Vector((s * math.cos(t), s * 0.35 * math.sin(t), 0)) for t in [i * math.pi / 8 for i in range(17)]]
        gp.stroke(layer, pts, s * 0.08, m, rng.uniform(0.2, alpha))


# ================================================================ binary shards
def shards(gp, hit_px, n, seed, depth=0.0, spread=(40, 380), dir_deg=180, cone=120, colors=("#FFFFFF", "#FFD2E8", "pink", "harm", "amber")):
    """0/1 glyph shards bursting from a hit point, trailing like embers in rain."""
    rng = random.Random(seed)
    hx, hy = hit_px
    mats = [mat_emit("shard_%d" % i, c, s) for i, (c, s) in enumerate(zip(colors, (14, 10, 12, 10, 8)))]
    trail = [gp.mat("trail_%d" % i, c, 0.8) for i, c in enumerate(colors)]
    for i in range(n):
        a = math.radians(dir_deg + rng.uniform(-cone / 2, cone / 2))
        d = rng.uniform(*spread) * (rng.random() ** 0.6)
        dz = rng.uniform(-2.5, 1.2)  # some fly toward the camera
        fall = (d / spread[1]) ** 2 * rng.uniform(20, 120)
        x = hx + d * math.cos(a)
        y = hy - d * math.sin(a) + fall
        k = rng.randrange(len(colors)) if i > 6 else 0
        size = rng.uniform(14, 34) * (1.0 - dz * 0.12)
        p = P(x, y, depth + dz)
        rot = (R90, math.radians(rng.uniform(-40, 40)), 0)
        text(rng.choice("01"), p, S(size, depth + dz), mats[k], MONO, "CENTER", "CENTER", rot=rot, name="shard")
        # motion trail back toward the hit point (curving with the fall)
        tl = rng.uniform(0.25, 0.6)
        pts = []
        for j in range(8):
            t = 1.0 - tl * j / 7
            xx = hx + d * t * math.cos(a)
            yy = hy - d * t * math.sin(a) + fall * t * t
            pts.append(P(xx, yy, depth + dz * t + 0.02))
        gp.stroke("shards", pts, [S(size * 0.09, depth + dz) * (1 - j / 8) for j in range(8)], trail[k], [0.85 * (1 - j / 8) for j in range(8)])
    # impact flash core + crack lines on the glass (crit = shattered glass)
    point(P(hx, hy, depth - 1.0), "#FFB8D8", 400, radius=0.3, name="hit_light", shadow=False)
    mcrack = gp.mat("crack", "#EAF4FF", 0.9)
    for i in range(11):
        a = rng.uniform(0, 2 * math.pi)
        pts = [P(hx, hy, depth - 0.02)]
        r = 0
        ang = a
        for j in range(4):
            r += rng.uniform(14, 32)
            ang += rng.uniform(-0.35, 0.35)
            pts.append(P(hx + r * math.cos(ang), hy + r * math.sin(ang), depth - 0.02))
        gp.stroke("crack", pts, [S(1.6 - j * 0.3, depth) for j in range(len(pts))], mcrack, 0.8)


# ================================================================ city
def city_blocks(seed, xr, yr, count, hmin, hmax, wmin, wmax, mats, z0=0.0, avoid=None, parent=None, lines=None, line_mat=None, hfn=None):
    """Random box towers. Returns list of (center, size). Optional GP silhouette linework on roof edges."""
    rng = random.Random(seed)
    out = []
    for i in range(count):
        w = rng.uniform(wmin, wmax)
        d = rng.uniform(wmin, wmax)
        h = rng.uniform(hmin, hmax) * (rng.random() ** 0.7 * 0.8 + 0.2)
        x = rng.uniform(*xr)
        y = rng.uniform(*yr)
        if hfn:
            h = hfn(x, y, rng)
        if avoid and avoid(x, y, w, d):
            continue
        m = mats[rng.randrange(len(mats))]
        box("bld%d" % i, (x, y, z0 + h / 2), (w, d, h), m, parent=parent)
        out.append(((x, y, z0 + h / 2), (w, d, h)))
        if lines is not None:
            zt = z0 + h
            c = [(x - w / 2, y - d / 2, zt), (x + w / 2, y - d / 2, zt), (x + w / 2, y + d / 2, zt), (x - w / 2, y + d / 2, zt)]
            lines.stroke("lines", [Vector(p) for p in c], 0.1, line_mat, 0.55, cyclic=True)
    return out


def sky_glow(name, loc, w, h, low="#34465f", high="#05070b", strength=1.4, rot=(R90, 0, 0)):
    """Light-polluted night sky behind the skyline: bright haze at the horizon so towers read as silhouettes."""
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["UV"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = col(low)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = col(high)
    nt.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    return rrect(name, w, h, 0.01, loc, m, rot=rot)


def wet_ground(name, loc, size, rough=(0.03, 0.3), base="#06080c", scale=0.08):
    """Wet asphalt: near-black, puddle-noise roughness so neon streaks reflect in patches."""
    m = bpy.data.materials.new(name)
    if not m.node_tree:
        m.use_nodes = True
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = col(base)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 4
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.42
    mr.inputs["From Max"].default_value = 0.58
    mr.inputs["To Min"].default_value = rough[0]
    mr.inputs["To Max"].default_value = rough[1]
    nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
    nt.links.new(mr.outputs[0], b.inputs["Roughness"])
    return box(name, loc, size, m)
