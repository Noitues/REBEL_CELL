"""Still 04: the Modem cyber shop. The original vertical MODEM / CYBER SHOP neon sign, redrawn as real neon tubes
hanging in the rain; its pink and cyan spill pools on the wet street and sheens the glass shop panels.
Zine stickers and pink marker on the glass. No paper BUY/SHRED stickers (feedback 2)."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rn_lib import *  # noqa
from rn_parts import *  # noqa
import stroke_font as SF

OUT = out_arg(os.path.join(STILLS, "_raw_04_hq_modem.png"))
reset(samples=int(os.environ.get("RN_SAMPLES", "32")))
world("#010203", 1.0, vol_density=0.002, vol_color="#8494ab", aniso=0.5)
sun((math.radians(-62), 0, math.radians(8)), "#9fb2d0", 0.35, name="backlight")
front_camera(50, fstop=0.14)
gp_back = GP("gp_back")
gp_ui = GP("gp_ui")
gp_mk = GP("gp_marker")
rng = random.Random(4)

# ---------------------------------------------------------------- blurred city + wet street
wm = [mat_windows("cw%d" % i, wall="#0a0d13", lit=("#8fa3bd", "#b9aa92"), density=0.2 + 0.05 * i, strength=1.0, scale=2.0 + i * 0.4, seed=i * 3.1) for i in range(3)]


def skyline_h(x, y, r):
    half = 5.4 * (CAM_D + y) / CAM_D
    return max(3.0, r.uniform(-0.3, 0.75) * half + 5.8)


city_blocks(12, (-95, 95), (40, 260), 170, 0, 0, 5, 16, wm, z0=-5.8, hfn=skyline_h)
sky_glow("sky", (0, 330, 124), 900, 260, low="#3a4e6c", strength=2.0)
for i, (cx, cy, h, c) in enumerate([(30, 120, 9, "#2f6f85"), (-60, 180, 14, "#6a5a2a"), (55, 210, 8, "#5a2f70")]):
    box("sign%d" % i, (cx, cy - 6, 4 + i * 5), (1.2, 0.3, h), mat_emit("fsign%d" % i, c, 3.0))
wet_ground("street", (0, 100, -4.75), (300, 220, 0.1), rough=(0.02, 0.2), scale=0.15)

# ---------------------------------------------------------------- the MODEM / CYBER SHOP sign (original redraw, real neon)
SX0, SY0, SX1, SY1, SD = 40, 92, 300, 1000, 0.8
m_back = mat_pbr("sign_back", "#07080c", 0.35, 0.6, coat=0.5)
cx = (SX0 + SX1) / 2
rrect("sign_plate", S(SX1 - SX0, SD), S(SY1 - SY0, SD), S(34, SD), P(cx, (SY0 + SY1) / 2, SD + 0.1), m_back, depth=0.12)
m_pk = mat_emit("neon_pink", "pink", 16.0)
m_pk_dim = mat_emit("neon_pink_dim", "#FF3DA8", 4.0)
m_cy = mat_emit("neon_cyan", "cyan", 14.0)
# frame tube: rounded rectangle
fr = []
for (ccx, ccy, a0) in ((SX1 - 34, SY0 + 34, -90), (SX0 + 34, SY0 + 34, 180), (SX0 + 34, SY1 - 34, 90), (SX1 - 34, SY1 - 34, 0)):
    for k in range(9):
        a = math.radians(a0 - 90 * k / 8)
        fr.append(P(ccx + 26 * math.cos(a), ccy - 26 * math.sin(a), SD))
fr2 = [fr[-1]] + fr
tube("sign_frame", fr2, S(5, SD), m_pk)
# stacked letters M O D E M in the geometric neon cut (no jitter, no slant)
letters = "MODEM"
lh = 118
for i, ch in enumerate(letters):
    strokes, w = SF.layout(ch, lh, tracking=0, slant=0, jitter=0, rot_deg=0, seed=1, smooth_n=5)
    ox = cx - w / 2
    oy = 222 + i * 138
    for s in strokes:
        pts = [P(ox + p.x, oy - p.y, SD) for p in s]
        tube("L%s%d" % (ch, i), pts, S(6.5, SD), m_pk)
# circuit traces with terminals
for i in range(10):
    side = -1 if i % 2 else 1
    y0 = 150 + i * 72 + rng.uniform(-10, 10)
    x0 = SX0 + 22 if side < 0 else SX1 - 22
    run = rng.uniform(18, 40)
    pts = [(x0, y0), (x0 - side * run, y0), (x0 - side * (run + 14), y0 + 14 * rng.choice((-1, 1)))]
    tube("trace%d" % i, [P(px, py, SD) for px, py in pts], S(2.2, SD), m_pk_dim)
    torus("term%d" % i, S(5, SD), S(1.8, SD), m_pk_dim, P(*pts[-1], SD), rot=(R90, 0, 0), seg=24, mseg=8)
# CYBER / SHOP in cyan
for j, word in enumerate(("CYBER", "SHOP")):
    strokes, w = SF.layout(word, 46, tracking=0.12, slant=0, jitter=0, rot_deg=0, seed=2, smooth_n=5)
    ox = cx - w / 2
    oy = 900 + j * 60
    for s in strokes:
        tube("cy%d" % j, [P(ox + p.x, oy - p.y, SD) for p in s], S(4.2, SD), m_cy)
# spill: the sign lights the rain, the street and the glass panels beside it
for i in range(5):
    point(P(cx + 60, 230 + i * 140, SD - 1.2), "pink", 700, radius=1.2, name="sign_spill%d" % i, shadow=False)
point(P(cx + 60, 930, SD - 1.2), "cyan", 500, radius=1.2, name="sign_spill_cy", shadow=False)
point(P(cx, 1040, SD - 2.5), "pink", 500, radius=1.5, name="sign_pool", shadow=False)

# ---------------------------------------------------------------- lights
area((0, -14, 9), (math.radians(55), 0, 0), "#b9c9e4", 700, size=18, size_y=4, name="fill")
area((0, 6, 7), (math.radians(-60), 0, 0), "#9fb4d8", 1200, size=20, size_y=2, name="rim_back")

# ---------------------------------------------------------------- glass shop UI
glass_panel(gp_ui, "p_top", 0, 0, 1920, 46, depth=0.3, rough=0.6, alpha=0.9)
ui_text("05  MODEM CYBER SHOP", 22, 23, 18, "pink", 2.4, depth=0.25)
ui_text("CYCLES 120    HEAT 18    RAM 3/5", 1480, 23, 17, "text_mid", 1.5, depth=0.25)

glass_panel(gp_ui, "p_chips", 360, 92, 540, 340, depth=0.2, title="MICROCHIPS")
m_chip = mat_pbr("chip", "#0c1422", 0.3, 0.6)
for i, (nm, d1, pr) in enumerate((("BARBED WIRE", "DEF slice also deals 2", 141), ("SHUNT", "Resolves the neighbour", 129))):
    x = 380 + i * 260
    glass_panel(gp_ui, "chipcard%d" % i, x, 148, 240, 264, depth=0.15, edge="#3a6a80")
    box("chip%d" % i, P(x + 120, 220, 0.1), (S(70), 0.1, S(70)), m_chip)
    box("chipcore%d" % i, P(x + 120, 220, 0.03), (S(30), 0.05, S(30)), mat_emit("chipcore", "cyan", 5.0))
    for k in range(5):
        box("pin", P(x + 92 + k * 14, 180, 0.1), (S(4), 0.05, S(10)), mat_pbr("pin", "#a8b4c4", 0.2, 1.0))
        box("pin", P(x + 92 + k * 14, 260, 0.1), (S(4), 0.05, S(10)), mat_pbr("pin", "#a8b4c4", 0.2, 1.0))
    ui_text(nm, x + 120, 300, 24, "text_hi", 2.2, ANTON, "CENTER", depth=0.1)
    ui_text(d1, x + 120, 330, 13, "text_mid", 1.4, MONO, "CENTER", depth=0.1)
    glass_panel(gp_ui, "buy%d" % i, x + 70, 360, 100, 36, depth=0.12, edge="acid")
    ui_text("BUY  %d" % pr, x + 120, 378, 16, "acid", 3.0, MONO, "CENTER", depth=0.1)

glass_panel(gp_ui, "p_cards", 940, 92, 940, 340, depth=0.2, title="CARDS")
for i, (t, c, d, pr, acc, r) in enumerate((("MIRROR FLIP", 3, "Flip a wheel.", 69, "pink", -4), ("ENCRYPT", 1, "Absorb next status.", 61, "cyan", 3),
                                          ("TAP TAP", 2, "Three +-1 nudges.", 75, "pink", -2))):
    x = 1060 + i * 190
    sticker_card(gp_ui, "mcard%d" % i, x, 262, 150, 200, r, t, c, accent=acc, desc=d, depth=0.0 - i * 0.01, seed=10 + i)
    ui_text("%d CY" % pr, x, 398, 16, "acid", 3.0, MONO, "CENTER", depth=0.05)
glass_panel(gp_ui, "shred", 1660, 150, 200, 250, depth=0.15, edge="#3a6a80", title="REMOVE A CARD")
ui_text("SHRED  50", 1760, 378, 16, "acid", 3.0, MONO, "CENTER", depth=0.1)
for k in range(7):
    box("shredline", P(1712 + k * 16, 290, 0.1), (S(3), 0.05, S(60)), mat_emit("shredl", "#7a889c", 1.5))

glass_panel(gp_ui, "p_slices", 360, 472, 540, 390, depth=0.2, title="SLICES", rule="cyan")
for i, (kind, val, pr) in enumerate((("def", 5, 100), ("atk", 10, 100), ("evd", 2, 100))):
    x = 450 + i * 180
    c = P(x, 640, 0.12)
    ring_sector("slc%d" % i, S(40), S(120), math.radians(60), math.radians(120), 0.12,
                mat_pbr("sl_%s" % kind, "#101318", 0.3, emit=SLICE_COL[kind], emit_str=1.4), (c.x, c.y, c.z - S(95)), rot=(R90, 0, 0), bevel=0.01)
    ui_text(str(val), x, 668, 34, "#ffffff", 3.0, ANTON, "CENTER", depth=0.0)
    glass_panel(gp_ui, "sbuy%d" % i, x - 50, 760, 100, 36, depth=0.12, edge="acid")
    ui_text("BUY  %d" % pr, x, 778, 16, "acid", 3.0, MONO, "CENTER", depth=0.1)

glass_panel(gp_ui, "p_daemons", 940, 472, 940, 390, depth=0.2, title="DAEMONS", rule="violet")
glass_panel(gp_ui, "dm0", 970, 540, 260, 290, depth=0.15, edge="#6a4a90")
box("dm_icon", P(1100, 620, 0.1), (S(60), 0.1, S(60)), mat_emit("dmicon", "#8C7BFF", 2.5))
ui_text("SCRUBBER", 1100, 700, 22, "text_hi", 2.0, ANTON, "CENTER", depth=0.1)
ui_text("Server Rack: -1 Heat", 1100, 732, 13, "text_mid", 1.4, MONO, "CENTER", depth=0.1)
glass_panel(gp_ui, "dbuy", 1050, 770, 100, 36, depth=0.12, edge="acid")
ui_text("BUY  218", 1100, 788, 16, "acid", 3.0, MONO, "CENTER", depth=0.1)
ui_text("> stock rotates in 2 jobs", 1270, 560, 15, "text_lo", 1.3, MONO, depth=0.1)
ui_text("> the fence takes cycles, not names", 1270, 590, 15, "text_lo", 1.3, MONO, depth=0.1)

# ---------------------------------------------------------------- zine stickers + marker on the glass
def round_sticker(name, x, y, r, face, txt, rot):
    root = empty(name, P(x, y, -0.2), (R90, math.radians(rot), 0))
    disc(name + "_sh", S(r + 4), 0.005, mat_pbr("stk_shadow", "#000000", 1.0, alpha=0.62), (S(8), -S(9), -0.03), parent=root, seg=48)
    disc(name + "_bk", S(r + 5), 0.005, mat_pbr("stk_back", "#f7f5ef", 0.7, emit="#f7f5ef", emit_str=0.25), (0, 0, 0), parent=root, seg=48)
    disc(name + "_fc", S(r), 0.006, mat_pbr("stk_face_" + face, face, 0.7, emit=face, emit_str=0.3), (0, 0, 0.004), parent=root, seg=48)
    text(txt, (0, 0, 0.012), S(r * 0.42), mat_pbr("stk_ink", "ink", 0.8), ANTON, "CENTER", "CENTER", rot=(0, 0, 0), parent=root)


round_sticker("stk_norefund", 905, 462, 52, "sticker_pink", "NO\nREFUNDS", -12)
round_sticker("stk_cell", 1812, 466, 40, "note_yellow", "CELL", 9)
# marker: circle a card, scrawl a note, and the exit verb with drips
loop = [P(1250 + 118 * math.cos(t) + rng.uniform(-4, 4), 262 + 128 * math.sin(t) + rng.uniform(-4, 4), -0.3) for t in [i * 2 * math.pi / 40 - 0.6 for i in range(46)]]
gp_mk.stroke("marker", loop, [S(4.5, -0.3) * (0.7 + 0.3 * math.sin(i / 45 * math.pi)) for i in range(46)], gp_mk.mat("mk_main", "pink"), 1.0)
marker(gp_mk, "THIS ONE!", 1380, 450, 30, depth=-0.3, seed=5, angle_deg=-6, drips=None)
marker(gp_mk, "LEAVE THE MODEM", 1100, 1012, 52, depth=-0.3, seed=21, angle_deg=-3, drips={"stage": "forming", "count": 5})

# ---------------------------------------------------------------- rain: most of it cool, the drops near the sign catch pink
rain(gp_back, 2600, 1, (-60, 60), (4, 120), (-6, 30), length=(2.0, 6.0), radius=(0.006, 0.018), alpha=(0.08, 0.3))
rain(gp_back, 260, 7, (-9.5, -6.2), (-1.5, 1.2), (-5.5, 5.5), length=(0.3, 0.9), radius=(0.004, 0.009), alpha=(0.25, 0.7), layer="rain_pink", color="#ff7ac4")
rain(gp_back, 60, 8, (-9.5, -6.2), (-1.5, 1.2), (-5.5, -3.0), length=(0.3, 0.8), radius=(0.004, 0.009), alpha=(0.25, 0.7), layer="rain_cyan", color="#8ae9ff")
rain(gp_ui, 80, 2, (-10, 10), (-8, -2), (-5, 5), length=(0.4, 1.0), radius=(0.004, 0.01), alpha=(0.08, 0.22))
mb = gp_ui.mat("bead", "#d6e6ff", 0.5)
for _ in range(140):
    x, y = rng.uniform(340, 1900), rng.uniform(60, 900)
    p = P(x, y, -0.05)
    gp_ui.stroke("beads", [p, p + Vector((0, 0, -S(rng.uniform(4, 40))))], [S(1.8), S(1.2)], mb, rng.uniform(0.15, 0.4))

compositor(bloom=0.9, bloom_thresh=1.0, streak=0.35, streak_thresh=3.0)
render(OUT)
