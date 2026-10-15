"""New corps (exploratory): shared 2D kit for Aurelian Concord (roman) and Tethys Deep (atlantis).

The same file lives in roman/scripts and atlantis/scripts (keep them identical).
It reuses the locked UI kit read-only from route_map_graph/hq_halcyon/scripts (ui31, sticker_lib31):
stickers, terminal panels, paper, stamps, holo, grease pencil. Nothing here is game content.

Glyphs are 512 px L masks (white silhouette, 0 = cut-out), drawn procedurally, seeded where random.
"""
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WT = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass"
KIT = os.path.join(WT, "docs", "concepts", "route_map_graph", "hq_halcyon", "scripts")
if KIT not in sys.path:
    sys.path.insert(0, KIT)

import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont  # noqa: E402

import sticker_lib31 as SL  # noqa: E402
import ui31 as U  # noqa: E402

S = 512
NC = os.path.join(WT, "docs", "concepts", "new_corps")
SCR = r"D:\rc_scratch\new_corps"
os.makedirs(SCR, exist_ok=True)


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# ------------------------------------------------------------------ the existing colour world (ART_BIBLE v2 2.1-2.4)
EXISTING_CORPS = [("MERIDIAN", "#FF8C1A"), ("SOLACE", "#96FF46"), ("HALCYON", "#B06EFF"),
                  ("ORBITAL", "#CDF0FF"), ("REBEL_CELL", "#E8141E")]
ROUTE_STATES = [("walked / ours (lime)", "#D4FF00"), ("next (orange)", "#FF8C1A"), ("ahead (white)", "#F2F6FF"),
                ("past / cut (grey)", "#6A7080"), ("pencil plan", "#FFE200"), ("pencil threat", "#FF1C2C")]
UI_ROLES = [("CELL_PINK", "#FF3DA8"), ("NET_CYAN", "#5CE1FF"), ("GAIN", "#7BE07B"), ("HARM", "#FF4433"),
            ("WARN amber", "#FFB000"), ("Exploit gold", "#FFD24D")]

# ------------------------------------------------------------------ the two new corps
DOT = chr(0xB7)   # the interpunct (kept as a code point so no editor can mangle it)
CORPS = {
    "aurelian": dict(
        name="AURELIAN CONCORD", short="AURELIAN", letterhead="AVRELIAN " + DOT + " CONCORD", folder="roman",
        tagline="Bread. Circus. Terms apply.",
        primary=("VERDIGRIS", "#29DBA6"), secondary=("TRAVERTINE", "#E9D5AA"), dark=("PORPHYRY", "#3A1426"),
        extra=[("GILT", "#C9A35A"), ("MARBLE", "#F3EFE6")],
        server="THE ROSTRUM", hub="THE GRAND STAND", house="VERDICT", raid="LEVIES", lost_verb="PACIFIED",
        crest="LAUREL ARCH",
    ),
    "tethys": dict(
        name="TETHYS DEEP", short="TETHYS", letterhead="tethys / deep", folder="atlantis",
        tagline="Breathe easy. We hold the air.",
        primary=("ABYSS BLUE", "#2F6BFF"), secondary=("LIGHTLESS RED", "#C8264E"), dark=("TRENCH", "#06112A"),
        extra=[("PHOTOPHORE", "#7CF2E4"), ("DIVE-LIGHT", "#FFE9B8")],
        server="THE BLACK SMOKER", hub="THE VENT CAP", house="TIDE", raid="HIGH TIDES", lost_verb="SUBMERGED",
        crest="TIDE WHIRL",
    ),
}


def col(corp, key):
    return hx(CORPS[corp][key][1])


# ------------------------------------------------------------------ mask helpers
def new():
    m = Image.new("L", (S, S), 0)
    return m, ImageDraw.Draw(m)


def leaf(d, cx, cy, length, width, ang, fill=255):
    """A lens-shaped laurel leaf centred at (cx, cy), pointing along ang (radians)."""
    pts = []
    n = 14
    for i in range(n + 1):
        t = -1 + 2 * i / n
        pts.append((t * length / 2, (1 - t * t) * width / 2))
    for i in range(n, -1, -1):
        t = -1 + 2 * i / n
        pts.append((t * length / 2, -(1 - t * t) * width / 2))
    ca, sa = math.cos(ang), math.sin(ang)
    d.polygon([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in pts], fill=fill)


def wreath(d, cx=256, cy=256, r=200, leaves=8, gap_top=40, lw=88, ww=40, stem=14, open_deg=None):
    """Two laurel branches from the bottom up both sides, open at the top."""
    a0 = math.radians(90)                      # bottom (y down)
    a1 = math.radians(-90 + gap_top)           # near the top
    for side in (-1, 1):
        pts = []
        for i in range(40):
            t = i / 39
            a = a0 + (a1 - a0 - (2 * math.pi if side < 0 else 0)) * t if False else None
        # parametrise: angle measured from the bottom, going up each side
        for i in range(41):
            t = i / 40
            phi = math.radians(180 - gap_top) * t          # 0 at the bottom, -> 180-gap at the top
            ang = math.pi / 2 - side * phi                  # screen angle
            pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
        d.line(pts, fill=255, width=stem)
        for k in range(leaves):
            t = (k + 0.7) / (leaves + 0.2)
            phi = math.radians(180 - gap_top) * t
            ang = math.pi / 2 - side * phi
            px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
            tang = ang - side * math.pi / 2               # direction of growth (toward the top)
            for off in (-1, 1):
                la = tang + off * 0.62 * -side * -1
                ox, oy = math.cos(ang) * off * ww * 0.55, math.sin(ang) * off * ww * 0.55
                leaf(d, px + ox + math.cos(la) * lw * 0.32, py + oy + math.sin(la) * lw * 0.32,
                     lw * (0.75 + 0.25 * t), ww * (0.8 + 0.2 * t), la)


def arch_shape(d, x0, y0, x1, y1, open_w=0.42, fill=255, attic=True):
    """Triumphal arch: a block, an attic band, a round-headed opening."""
    w = x1 - x0
    d.rectangle([x0, y0, x1, y1], fill=fill)
    ow = w * open_w
    cx = (x0 + x1) / 2
    top = y0 + (y1 - y0) * 0.42
    d.rectangle([cx - ow / 2, top, cx + ow / 2, y1 + 2], fill=0)
    d.ellipse([cx - ow / 2, top - ow / 2, cx + ow / 2, top + ow / 2], fill=0)
    if attic:
        d.line([(x0, y0 + (y1 - y0) * 0.2), (x1, y0 + (y1 - y0) * 0.2)], fill=0, width=max(6, int(w * 0.04)))
        # two pilasters' cut lines
        for fx in (0.14, 0.86):
            xx = x0 + w * fx
            d.line([(xx, y0 + (y1 - y0) * 0.3), (xx, y1)], fill=0, width=max(5, int(w * 0.03)))


# ------------------------------------------------------------------ AURELIAN glyphs
def g_laurel_arch():
    m, d = new()
    wreath(d, r=196, leaves=7, gap_top=34, lw=92, ww=42, stem=16)
    arch_shape(d, 168, 168, 344, 360, open_w=0.40)
    d.rectangle([150, 360, 362, 384], fill=255)   # the street plinth line
    return m


def g_dole():
    """DOLE (ration depot): the round loaf scored into 8, steam above."""
    m, d = new()
    d.ellipse([86, 150, 426, 470], fill=255)
    for k in range(4):
        a = math.radians(k * 45)
        d.line([(256 - 150 * math.cos(a), 310 - 140 * math.sin(a)), (256 + 150 * math.cos(a), 310 + 140 * math.sin(a))], fill=0, width=18)
    d.ellipse([226, 280, 286, 340], fill=0)
    for x in (196, 256, 316):
        pts = [(x + 14 * math.sin(t / 6.0 * math.pi * 2), 130 - t * 14) for t in range(7)]
        d.line(pts, fill=255, width=20)
    return m


def g_ludus():
    """LUDUS (arena gym / stream studio): the gladiator helmet in profile, plume ridge on top, grille visor."""
    m, d = new()
    d.pieslice([110, 170, 390, 450], 180, 360, fill=255)            # skull dome
    d.rectangle([110, 308, 390, 420], fill=255)                       # face + cheek
    d.polygon([(110, 300), (60, 330), (40, 440), (120, 430)], fill=255)   # neck guard (back, left)
    d.polygon([(390, 300), (440, 300), (452, 360), (390, 360)], fill=255) # visor brim (front, right)
    for r_ in range(3):                                               # grille holes on the visor
        for c_ in range(3):
            x, y = 268 + c_ * 40, 334 + r_ * 30
            d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=0)
    d.line([(130, 312), (240, 312)], fill=0, width=10)
    # the plume: a thick arc ridge with brush cuts
    d.arc([90, 70, 410, 350], 195, 345, fill=255, width=62)
    for k in range(9):
        a = math.radians(200 + k * 17)
        d.line([(250 + 128 * math.cos(a), 210 + 112 * math.sin(a)), (250 + 166 * math.cos(a), 210 + 146 * math.sin(a))], fill=0, width=8)
    d.rectangle([60, 444, 452, 470], fill=255)
    return m


def g_aqueduct():
    """AQUEDUCT (data conduit pump station): three arches, the channel on top carries packets."""
    m, d = new()
    d.rectangle([40, 140, 472, 214], fill=255)
    for i in range(3):
        x0 = 40 + i * 144
        d.rectangle([x0, 214, x0 + 144, 440], fill=255)
        d.rectangle([x0 + 30, 300, x0 + 114, 444], fill=0)
        d.ellipse([x0 + 30, 258, x0 + 114, 342], fill=0)
    for x in range(70, 460, 64):                                   # packets in the channel
        d.rectangle([x, 166, x + 34, 188], fill=0)
    d.rectangle([24, 440, 488, 470], fill=255)
    return m


def g_atrium():
    """ATRIUM (patron's debt office): an ionic column holding a sealed contract."""
    m, d = new()
    d.rectangle([186, 150, 326, 420], fill=255)                    # shaft
    for x in (214, 242, 270, 298):
        d.line([(x, 168), (x, 404)], fill=0, width=10)               # flutes
    d.rectangle([130, 112, 382, 150], fill=255)                    # capital
    for cx in (138, 374):
        d.ellipse([cx - 40, 112, cx + 40, 192], fill=255)            # volutes
        d.ellipse([cx - 16, 136, cx + 16, 168], fill=0)
    d.rectangle([150, 70, 362, 102], fill=255)                     # abacus
    d.rectangle([150, 420, 362, 450], fill=255)
    d.rectangle([120, 452, 392, 480], fill=255)                    # base
    return m


def g_thermae():
    """THERMAE (bath-spa clinic): a basin with three steam curls."""
    m, d = new()
    d.pieslice([70, 220, 442, 470], 0, 180, fill=255)
    d.rectangle([60, 330, 452, 360], fill=255)
    d.rectangle([110, 360, 402, 372], fill=0)
    for x in (170, 256, 342):
        pts = [(x + 26 * math.sin(t / 10.0 * math.pi * 2.2), 300 - t * 22) for t in range(11)]
        d.line(pts, fill=255, width=26)
    return m


def g_tollgate():
    """TOLL GATE (triumph-gate toll): a coin slot pillar and a raised striped barrier."""
    m, d = new()
    d.rounded_rectangle([60, 250, 180, 470], radius=14, fill=255)
    d.rectangle([96, 292, 144, 304], fill=0)                        # coin slot
    d.ellipse([92, 330, 148, 386], fill=0)
    d.ellipse([106, 344, 134, 372], fill=255)
    a = math.radians(-30)
    x0, y0 = 150, 270
    x1, y1 = x0 + 340 * math.cos(a), y0 + 340 * math.sin(a)
    d.line([(x0, y0), (x1, y1)], fill=255, width=44)
    for t in (0.3, 0.55, 0.8):
        cx, cy = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        d.line([(cx - 16 * math.cos(a), cy - 16 * math.sin(a)), (cx + 16 * math.cos(a), cy + 16 * math.sin(a))], fill=0, width=30)
    d.ellipse([128, 248, 172, 292], fill=255)
    d.rectangle([30, 470, 482, 494], fill=255)
    return m


def g_verdict():
    """Boss emblem: VERDICT, the thumb turned down under a laurel crown."""
    m, d = new()
    # drawn as a thumbs-UP then flipped: fingers stacked on the left, the thumb rising, the cuff on the right
    d.rounded_rectangle([118, 200, 330, 430], radius=46, fill=255)    # curled fingers
    for y in (256, 314, 372):
        d.line([(118, y), (236, y)], fill=0, width=14)                # finger splits
    d.rounded_rectangle([200, 40, 290, 260], radius=45, fill=255)     # the thumb
    d.line([(214, 238), (300, 238)], fill=0, width=12)                # thumb crease
    d.rectangle([330, 226, 396, 420], fill=255)                       # cuff
    d.line([(342, 226), (342, 420)], fill=0, width=10)
    m = m.transpose(Image.FLIP_TOP_BOTTOM)
    d = ImageDraw.Draw(m)
    # two laurel sprigs under the cuff (the crowd's crown)
    for k in range(4):
        leaf(d, 416, 120 + k * 46, 64, 28, math.radians(-60 + (k % 2) * 120))
    d.line([(416, 100), (416, 290)], fill=255, width=12)
    return m


# ------------------------------------------------------------------ TETHYS glyphs
def g_nautilus():
    m, d = new()
    cx, cy = 262, 270
    b = 0.168
    def R(t):
        return 26 * math.exp(b * t)
    # body: overlapping discs along the log spiral (the tube)
    t = 0.0
    while t < 4 * math.pi + 0.6:
        r = R(t)
        tr = r * 0.40
        x, y = cx + (r - tr) * math.cos(t), cy + (r - tr) * math.sin(t)
        d.ellipse([x - tr, y - tr, x + tr, y + tr], fill=255)
        t += 0.05
    # the seam (outer edge of the previous whorl)
    pts = [(cx + R(t) * math.cos(t), cy + R(t) * math.sin(t)) for t in np.linspace(1.2, 2 * math.pi + 2.2, 120)]
    d.line(pts, fill=0, width=16)
    # septa: curved chamber walls across the last whorl
    for t0 in np.linspace(2 * math.pi + 0.7, 4 * math.pi - 0.5, 7):
        r_in, r_out = R(t0 - 2 * math.pi) + 10, R(t0) - 16
        pts = []
        for s in np.linspace(0, 1, 10):
            rr = r_in + (r_out - r_in) * s
            tt = t0 - 0.35 * math.sin(s * math.pi)
            pts.append((cx + rr * math.cos(tt), cy + rr * math.sin(tt)))
        d.line(pts, fill=0, width=11)
    return m


def g_air():
    """AIR LEASE (oxygen depot): a tank with a valve and rising bubbles."""
    m, d = new()
    d.rounded_rectangle([150, 150, 330, 470], radius=80, fill=255)
    d.rectangle([206, 96, 274, 160], fill=255)
    d.rectangle([170, 70, 310, 100], fill=255)
    d.rectangle([150, 250, 330, 276], fill=0)
    d.rectangle([150, 360, 330, 372], fill=0)
    for (x, y, r) in ((392, 360, 34), (420, 250, 26), (384, 160, 20), (418, 90, 14)):
        d.ellipse([x - r, y - r, x + r, y + r], outline=255, width=14)
    return m


def g_pump():
    """PUMP HOUSE (seawall lock): a breaking wave held back by a gate wall with a valve wheel."""
    m, d = new()
    d.rectangle([40, 300, 472, 480], fill=255)
    for y in (360, 420):
        d.line([(40, y), (472, y)], fill=0, width=10)
    for i, y in enumerate((300, 360, 420)):
        for x in range(70 + (i % 2) * 60, 472, 120):
            d.line([(x, y), (x, y + 60)], fill=0, width=10)
    for k, yb in enumerate((90, 170, 250)):                         # three swells held back above the wall
        pts = [(40 + i * 10.8, yb + 26 * math.sin(i / 40 * math.pi * 3 + k * 1.1)) for i in range(41)]
        d.line(pts, fill=255, width=34)
    d.ellipse([196, 330, 316, 450], fill=0)                          # the valve wheel on the wall
    d.ellipse([214, 348, 298, 432], fill=255)
    d.ellipse([234, 368, 278, 412], fill=0)
    d.line([(256, 340), (256, 440)], fill=255, width=12)
    d.line([(206, 390), (306, 390)], fill=255, width=12)
    return m


def g_cable():
    """CABLE HEAD (transoceanic landing station): a heavy plug on a wavy sea cable."""
    m, d = new()
    d.rounded_rectangle([170, 60, 342, 250], radius=30, fill=255)
    d.rectangle([200, 20, 230, 70], fill=255)
    d.rectangle([282, 20, 312, 70], fill=255)
    d.rectangle([196, 140, 316, 160], fill=0)
    pts = [(256 + 90 * math.sin(t * 0.09), 250 + t * 4.4) for t in range(60)]
    d.line(pts, fill=255, width=48)
    return m


def g_coldvault():
    """COLD VAULT (submerged data pod): a capsule with three portholes on a seabed skid."""
    m, d = new()
    d.rounded_rectangle([40, 170, 472, 360], radius=95, fill=255)
    for x in (150, 256, 362):
        d.ellipse([x - 42, 223, x + 42, 307], fill=0)
        d.ellipse([x - 24, 241, x + 24, 289], fill=255)
    d.rectangle([110, 360, 140, 420], fill=255)
    d.rectangle([372, 360, 402, 420], fill=255)
    d.rectangle([60, 420, 452, 446], fill=255)
    for (x, y, r) in ((300, 120, 22), (340, 70, 15)):
        d.ellipse([x - r, y - r, x + r, y + r], outline=255, width=12)
    return m


def g_desal():
    """DESAL (desalination plant): a drop through filter bars."""
    m, d = new()
    pts = []
    for i in range(61):
        a = math.radians(-30 + 240 * i / 60)
        pts.append((256 + 150 * math.cos(a + math.pi / 2 - math.radians(90)), 320 + 150 * math.sin(a)))
    d.ellipse([106, 220, 406, 470], fill=255)
    d.polygon([(256, 40), (130, 300), (382, 300)], fill=255)
    for y in (250, 312, 374):
        d.rectangle([90, y, 422, y + 22], fill=0)
    return m


def g_airlock():
    """DOCK LOCK (sub dock airlock): a hatch with its hand-wheel and bolts."""
    m, d = new()
    d.ellipse([46, 46, 466, 466], fill=255)
    d.ellipse([96, 96, 416, 416], fill=0)
    d.ellipse([120, 120, 392, 392], fill=255)
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        x, y = 256 + 186 * math.cos(a), 256 + 186 * math.sin(a)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=0)
    d.ellipse([170, 170, 342, 342], fill=0)
    d.ellipse([186, 186, 326, 326], fill=255)
    d.ellipse([204, 204, 308, 308], fill=0)
    for k in range(4):
        a = math.radians(k * 45)
        d.line([(256 - 80 * math.cos(a), 256 - 80 * math.sin(a)), (256 + 80 * math.cos(a), 256 + 80 * math.sin(a))], fill=255, width=20)
    d.ellipse([232, 232, 280, 280], fill=255)
    return m


def g_smoker():
    """Boss emblem: THE BLACK SMOKER, a vent chimney with its billowing plume."""
    m, d = new()
    d.polygon([(170, 490), (200, 330), (186, 300), (226, 230), (290, 230), (316, 300), (304, 340), (342, 490)], fill=255)
    for y, w in ((300, 10), (370, 10), (430, 10)):
        d.line([(196, y), (318, y + 8)], fill=0, width=w)
    rng = random.Random(71)
    for k in range(13):
        t = k / 12
        x = 258 + 70 * math.sin(t * 3.4) * t + rng.uniform(-10, 10)
        y = 210 - t * 180
        r = 34 + 70 * t
        d.ellipse([x - r, y - r * 0.75, x + r, y + r * 0.75], fill=255)
    d.ellipse([228, 214, 288, 244], fill=0)                         # the vent mouth
    return m


# ------------------------------------------------------------------ round 2 (designer review): new + reworked glyphs
def g_dole2():
    """DOLE v2: the loaf in PROFILE (side view): a domed loaf on a flat base, three slashes scored in the crust."""
    m, d = new()
    d.pieslice([40, 130, 472, 690], 180, 360, fill=255)          # the dome (top half of a wide ellipse)
    d.rounded_rectangle([40, 380, 472, 440], radius=28, fill=255)  # the flat bottom
    for k in range(3):                                             # scoring slashes
        x = 150 + k * 100
        d.line([(x - 34, 230 + k * 6), (x + 40, 310 + k * 6)], fill=0, width=24)
    d.line([(64, 400), (448, 400)], fill=0, width=10)             # the base crease
    d.rectangle([20, 462, 492, 486], fill=255)                     # the board it sits on
    return m


def g_dole3():
    """DOLE v3 (review 2): the profile loaf with NO board under it, steam rising from the crust again."""
    m, d = new()
    d.pieslice([40, 200, 472, 760], 180, 360, fill=255)          # the dome
    d.rounded_rectangle([40, 450, 472, 504], radius=26, fill=255)  # flat bottom
    for k in range(3):
        x = 150 + k * 100
        d.line([(x - 34, 300 + k * 6), (x + 40, 380 + k * 6)], fill=0, width=24)
    d.line([(64, 470), (448, 470)], fill=0, width=10)
    for k, x in enumerate((176, 256, 336)):                        # three steam curls rising from the crust
        pts = [(x + 22 * math.sin(t / 7.0 * math.pi * 2 + k), 178 - t * 22) for t in range(8)]
        d.line(pts, fill=255, width=24, joint="curve")
    return m


def g_ludus2():
    """LUDUS v2 (review 2): a FRONT-FACING centurion helmet: the transverse crest plume fanned across the top, the dome,
    the brow band, cheek guards down both sides, eye slits and a nose guard."""
    m, d = new()
    d.pieslice([24, 20, 488, 260], 180, 360, fill=255)              # the plume: a wide fan across the top
    for k in range(13):                                             # brush cuts in the plume
        a = math.radians(188 + k * 13.4)
        d.line([(256 + 120 * math.cos(a), 140 + 60 * math.sin(a)), (256 + 228 * math.cos(a), 140 + 116 * math.sin(a))], fill=0, width=8)
    d.rectangle([236, 120, 276, 170], fill=255)                     # plume holder
    d.ellipse([110, 150, 402, 420], fill=255)                       # the dome
    d.rectangle([96, 262, 416, 300], fill=255)                      # brow band
    d.line([(96, 262), (416, 262)], fill=0, width=8)
    d.polygon([(110, 300), (196, 300), (192, 470), (126, 440)], fill=255)   # left cheek guard
    d.polygon([(402, 300), (316, 300), (320, 470), (386, 440)], fill=255)   # right cheek guard
    d.rectangle([196, 300, 316, 330], fill=255)                     # the mask's upper face
    d.rounded_rectangle([156, 316, 238, 344], radius=12, fill=0)    # eye slits
    d.rounded_rectangle([274, 316, 356, 344], radius=12, fill=0)
    d.rectangle([244, 300, 268, 420], fill=255)                     # nose guard
    d.ellipse([150, 380, 172, 402], fill=0)                         # cheek rivets
    d.ellipse([340, 380, 362, 402], fill=0)
    return m


def g_aqueduct3():
    """AQUEDUCT v3 (review 2): two big arches below, a stacked tier of smaller arches above, the channel with water on
    top, and the piers standing in water (a water line at the base)."""
    m, d = new()
    d.rectangle([30, 92, 482, 124], fill=255)                       # the channel
    pts = [(30 + i * 11.3, 78 + 8 * math.sin(i * 0.8)) for i in range(41)]
    d.line(pts, fill=255, width=14)                                 # water riding in it
    d.rectangle([30, 124, 482, 236], fill=255)                      # upper tier
    for i in range(4):                                              # four small arches
        x0 = 52 + i * 108
        d.rectangle([x0, 176, x0 + 72, 236], fill=0)
        d.ellipse([x0, 140, x0 + 72, 212], fill=0)
    d.rectangle([30, 236, 482, 256], fill=255)                      # the string course
    d.rectangle([30, 256, 482, 420], fill=255)                      # lower tier
    for i in range(2):                                              # two big arches
        x0 = 70 + i * 206
        d.rectangle([x0, 336, x0 + 166, 430], fill=0)
        d.ellipse([x0, 254, x0 + 166, 420], fill=0)
    for k, yb in enumerate((436, 474)):                             # the water line at the piers' feet
        wave_band(d, 10, 502, yb, 9, 70, 18, phase=k * 1.7)
    return m


def emblem_emoji(kind="thumb", size=512):
    """Boss emblem v4 (review 2), EMOJI style: flat colour shapes with one highlight and a thick ink outline.
    thumb: a thumbs-down hand with a laurel cuff (the VERDICT). emperor: a smug round face under a laurel wreath."""
    s = size / 512
    ink = (12, 10, 16)
    trav, trav_hi, trav_lo = (236, 214, 168), (255, 244, 214), (196, 166, 116)
    verd, verd_lo = (41, 219, 166), (20, 140, 104)
    layers = []

    def shape(fn):
        m = Image.new("L", (size, size), 0)
        fn(ImageDraw.Draw(m))
        return m
    if kind == "thumb":
        hand = shape(lambda d: thumb_down(d, 220 * s, 236 * s, 1.25 * s))
        cuff = shape(lambda d: d.rounded_rectangle([(220 - 76 * 1.25) * s, (236 - 156 * 1.25) * s, (220 + 96 * 1.25) * s,
                                                    (236 - 92 * 1.25) * s], radius=14 * s, fill=255))
        leaves = Image.new("L", (size, size), 0)
        dl = ImageDraw.Draw(leaves)
        y = (236 - 124 * 1.25) * s
        for k in range(7):
            x = (220 - 62 * 1.25) * s + k * 34 * s
            leaf(dl, x, y, 70 * s, 32 * s, math.radians(-40 if k % 2 else 40))
        body = ImageChops.lighter(hand, cuff)
        out = ImageChops.lighter(body, leaves)
        layers = [(hand, trav), (cuff, verd_lo), (leaves, verd)]
        hl = shape(lambda d: d.rounded_rectangle([(220 - 60 * 1.25) * s, (236 - 80 * 1.25) * s, (220 - 30 * 1.25) * s,
                                                  (236 + 20 * 1.25) * s], radius=12 * s, fill=255))
        layers.append((ImageChops.multiply(hl, hand), trav_hi))
    else:
        face = shape(lambda d: d.ellipse([96 * s, 120 * s, 416 * s, 456 * s], fill=255))
        wreath = Image.new("L", (size, size), 0)
        dw = ImageDraw.Draw(wreath)
        for side in (-1, 1):
            for k in range(6):
                a = math.radians(-90 + side * (24 + k * 22))
                x, y = 256 * s + 176 * s * math.cos(a), 270 * s + 170 * s * math.sin(a)
                leaf(dw, x, y, 74 * s, 32 * s, a + side * math.pi / 2 * 0.9)
        feat = shape(lambda d: (d.line([(160 * s, 270 * s), (226 * s, 286 * s)], fill=255, width=int(16 * s)),       # smug lids
                                d.line([(286 * s, 286 * s), (352 * s, 270 * s)], fill=255, width=int(16 * s)),
                                d.line([(150 * s, 236 * s), (228 * s, 254 * s)], fill=255, width=int(14 * s)),       # brows
                                d.line([(284 * s, 254 * s), (362 * s, 236 * s)], fill=255, width=int(14 * s)),
                                d.arc([200 * s, 330 * s, 330 * s, 400 * s], 10, 150, fill=255, width=int(14 * s))))  # smirk
        out = ImageChops.lighter(face, wreath)
        hl = shape(lambda d: d.ellipse([140 * s, 160 * s, 230 * s, 230 * s], fill=255))
        layers = [(face, trav), (ImageChops.multiply(hl, face), trav_hi), (wreath, verd), (feat, ink)]
    keyl = out.filter(ImageFilter.MaxFilter(int(29 * s) | 1))
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img.alpha_composite(tint(keyl, ink))
    for m_, c in layers:
        img.alpha_composite(tint(m_, c))
    return img


def emblem_thumb_cartoon(size=512):
    """Boss emblem v5 (review 2b, the designer's clarification): a chunky cartoon thumbs-down in the familiar emoji
    STYLE (an original drawing): a puffy rounded fist at a slight 3/4 turn, the thumb pointing down, flat colour with one
    shadow side and one highlight, a thick dark outline; Roman flavour: a gilt cuff with a verdigris laurel, an
    imperial-purple sleeve edge. Drawn upright at 2x, then turned -12 degrees."""
    S2 = 1024
    k = S2 / 512
    ink = (14, 10, 18)
    skin, skin_sh, skin_hi = (246, 204, 128), (214, 152, 76), (255, 240, 200)
    gold, gold_sh = (226, 182, 82), (170, 124, 44)
    verd, purple, purple_hi = (41, 219, 166), (92, 30, 92), (150, 70, 140)

    def M():
        m = Image.new("L", (S2, S2), 0)
        return m, ImageDraw.Draw(m)

    def R(d, x0, y0, x1, y1, r, fill=255):
        d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r * k, fill=fill)
    sleeve, ds = M()
    R(ds, 236, 8, 470, 92, 30)
    sleeve_edge, de = M()
    R(de, 236, 62, 470, 92, 10)
    cuff, dc = M()
    R(dc, 222, 82, 478, 140, 24)
    fist, df = M()
    R(df, 132, 120, 440, 338, 96)                                # the puffy fist
    for j in range(4):                                           # finger rolls bulging on the right (3/4: we see their ends)
        y = 132 + j * 50
        df.ellipse([368 * k, y * k, 458 * k, (y + 62) * k], fill=255)
    thumb, dt = M()
    R(dt, 134, 236, 236, 486, 50)                                # the fat thumb, pointing down
    body = ImageChops.lighter(ImageChops.lighter(fist, thumb), ImageChops.lighter(cuff, sleeve))
    # flat shading: a shadow side (right / underside) and one highlight
    sh, dsh = M()
    R(dsh, 300, 120, 470, 340, 80)
    dsh.rectangle([186 * k, 300 * k, 236 * k, 486 * k], fill=255)
    shade = ImageChops.multiply(sh, ImageChops.lighter(fist, thumb))
    hi, dh = M()
    dh.ellipse([170 * k, 150 * k, 262 * k, 214 * k], fill=255)
    dh.ellipse([150 * k, 290 * k, 186 * k, 400 * k], fill=255)
    hi = ImageChops.multiply(hi, ImageChops.lighter(fist, thumb))
    lines, dl = M()                                              # inner ink lines: finger creases, thumb crease, nail
    for j in range(1, 4):
        y = 132 + j * 50
        dl.arc([300 * k, (y - 30) * k, 452 * k, (y + 16) * k], 20, 160, fill=255, width=int(10 * k))
    dl.arc([140 * k, 236 * k, 236 * k, 296 * k], 200, 340, fill=255, width=int(10 * k))
    dl.rounded_rectangle([154 * k, 410 * k, 214 * k, 470 * k], radius=22 * k, outline=255, width=int(9 * k))
    leaves, dlv = M()                                            # the laurel on the cuff
    for j in range(6):
        x = 246 + j * 40
        leaf(dlv, x * k, 111 * k, 50 * k, 22 * k, math.radians(-35 if j % 2 else 35))
    img = Image.new("RGBA", (S2, S2), (0, 0, 0, 0))
    out = body.filter(ImageFilter.MaxFilter(int(34 * k) | 1))
    img.alpha_composite(tint(out, ink))
    for m_, c in ((sleeve, purple), (sleeve_edge, purple_hi), (cuff, gold), (fist, skin), (thumb, skin), (shade, skin_sh),
                  (hi, skin_hi), (leaves, verd)):
        img.alpha_composite(tint(m_, c))
    cuff_sh = ImageChops.multiply(cuff, ImageChops.offset(cuff, 0, int(-18 * k)).point(lambda v: 255 - v))
    img.alpha_composite(tint(cuff_sh, gold_sh))
    # separation lines between the parts + the inner creases, all in ink
    sep = ImageChops.subtract(cuff.filter(ImageFilter.MaxFilter(int(9 * k) | 1)), cuff)
    sep = ImageChops.lighter(sep, ImageChops.subtract(thumb.filter(ImageFilter.MaxFilter(int(9 * k) | 1)), thumb))
    sep = ImageChops.multiply(sep, body)
    img.alpha_composite(tint(ImageChops.lighter(sep, lines), ink))
    img = img.rotate(12, Image.BICUBIC, center=(S2 / 2, S2 / 2))
    return img.resize((size, size), Image.LANCZOS)


def g_emoji_thumb():
    return emblem_thumb_cartoon().split()[3]


def g_emoji_emperor():
    return emblem_emoji("emperor").split()[3]


def g_aqueduct2():
    """AQUEDUCT v2: a long straight run of TALL arches carrying a channel; water rides on top and pours off the end."""
    m, d = new()
    d.rectangle([14, 150, 420, 196], fill=255)                     # the channel
    pts = [(14 + i * 10.15, 132 + 9 * math.sin(i * 0.9)) for i in range(41)]
    d.line(pts, fill=255, width=16)                                # water riding on the channel
    d.rectangle([14, 196, 420, 214], fill=255)
    for i in range(5):                                             # five tall piers + four tall openings
        x0 = 14 + i * 96
        d.rectangle([x0, 214, x0 + 26, 476], fill=255)
    for i in range(4):
        x0 = 40 + i * 96
        d.rectangle([x0, 214, x0 + 70, 260], fill=255)
        d.ellipse([x0, 236, x0 + 70, 306], fill=0)                 # the arch head
        d.rectangle([x0 - 2, 270, x0 + 72, 280], fill=0)
    # the end spout: water pours off the right end in a falling ribbon
    spout = [(420 + t * 3.2, 150 + (t / 18) ** 2 * 300) for t in range(19)]
    d.line(spout, fill=255, width=22)
    d.ellipse([440, 452, 500, 482], fill=255)                      # the splash pool
    d.rectangle([4, 476, 430, 494], fill=255)
    return m


def g_curia():
    """CURIA (the senate house): a columned temple front, pediment, four columns, three steps."""
    m, d = new()
    d.polygon([(40, 170), (256, 50), (472, 170)], fill=255)        # pediment
    d.polygon([(110, 152), (256, 84), (402, 152)], fill=0)         # tympanum
    d.ellipse([236, 108, 276, 148], fill=255)                      # a roundel in it
    d.rectangle([52, 170, 460, 206], fill=255)                     # entablature
    for i in range(4):
        x = 92 + i * 109
        d.rectangle([x - 22, 206, x + 22, 410], fill=255)
        d.rectangle([x - 32, 206, x + 32, 222], fill=255)          # capitals
    for k in range(3):                                              # steps
        d.rectangle([40 - k * 14, 410 + k * 26, 472 + k * 14, 432 + k * 26], fill=255)
    return m


def g_annona():
    """ANNONA (granary / grain office): a tied wheat sheaf, five ears fanning out over splayed stalks."""
    m, d = new()
    base = (256, 330)
    for k, ang in enumerate((-34, -17, 0, 17, 34)):
        a = math.radians(ang - 90)
        L = 230 if k in (1, 2, 3) else 205
        tip = (base[0] + L * math.cos(a), base[1] + L * math.sin(a))
        d.line([base, tip], fill=255, width=12)
        # the ear: kernels (lens leaves) both sides along the top 55 %
        for j in range(6):
            t = 0.45 + j * 0.095
            px, py = base[0] + L * t * math.cos(a), base[1] + L * t * math.sin(a)
            for s in (-1, 1):
                la = a + s * 0.55
                leaf(d, px + math.cos(la) * 16, py + math.sin(la) * 16, 46, 22, la)
        leaf(d, tip[0] + math.cos(a) * 14, tip[1] + math.sin(a) * 14, 44, 18, a)
    for ang in (-24, -12, 0, 12, 24):                               # splayed stalk ends below the tie
        a = math.radians(ang + 90)
        d.line([base, (base[0] + 160 * math.cos(a), base[1] + 160 * math.sin(a))], fill=255, width=13)
    d.rounded_rectangle([206, 318, 306, 356], radius=12, fill=255)   # the tie
    d.line([(214, 337), (298, 337)], fill=0, width=8)
    return m


def thumb_down(d, cx, cy, s):
    """The classic thumbs-down: the cuff on top, the palm block, four finger rolls stacked on the right,
    the thumb pointing straight down on the left. (cx, cy) = the palm centre."""
    def R(x0, y0, x1, y1, r, fill=255):
        d.rounded_rectangle([cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s], radius=r * s, fill=fill)
    R(-70, -150, 90, -96, 8)                       # the cuff (toga sleeve)
    d.line([(cx - 70 * s, cy - 110 * s), (cx + 90 * s, cy - 110 * s)], fill=0, width=int(8 * s))
    R(-70, -92, 70, 60, 26)                        # the palm / back of the hand
    for k in range(4):                             # four finger rolls stacked on the right
        y0 = -90 + k * 38
        R(30, y0, 128, y0 + 40, 20)
        d.line([(cx + 40 * s, cy + (y0 + 40) * s), (cx + 120 * s, cy + (y0 + 40) * s)], fill=0, width=int(7 * s))
    R(-70, 0, -8, 190, 30)                         # the thumb, pointing down
    d.line([(cx - 64 * s, cy + 52 * s), (cx - 14 * s, cy + 52 * s)], fill=0, width=int(8 * s))
    d.rounded_rectangle([cx - 56 * s, cy + 138 * s, cx - 22 * s, cy + 176 * s], radius=10 * s, fill=0)   # the nail
    d.rounded_rectangle([cx - 51 * s, cy + 143 * s, cx - 27 * s, cy + 171 * s], radius=7 * s, fill=255)


def g_verdict2():
    """Boss emblem v2 (THE ROSTRUM, colosseum wheel): the thumb turned down inside the emperor's box arch."""
    m, d = new()
    # the box: a thick round-headed arch frame (the arena's imperial box), plinth
    d.rounded_rectangle([60, 140, 452, 470], radius=10, fill=255)
    d.pieslice([60, 20, 452, 290], 180, 360, fill=255)
    d.rectangle([108, 160, 404, 470], fill=0)
    d.pieslice([108, 66, 404, 290], 180, 360, fill=0)
    d.rectangle([40, 466, 472, 496], fill=255)
    thumb_down(d, 236, 250, 1.0)
    return m


def g_verdict3():
    """Boss emblem v3 (final): the thumbs-down alone, big, the toga cuff on top with a purple-stripe cut. Reads at 16 px."""
    m, d = new()
    thumb_down(d, 198, 250, 1.48)
    d.line([(198 - 70 * 1.48, 250 - 136 * 1.48), (198 + 90 * 1.48, 250 - 136 * 1.48)], fill=0, width=10)
    return m


def g_arena_gate():
    """Option B emblem: the gladiator gate: a portcullis in an arch, two crossed swords."""
    m, d = new()
    d.pieslice([90, 40, 422, 330], 180, 360, fill=255)
    d.rectangle([90, 184, 422, 470], fill=255)
    d.pieslice([140, 92, 372, 330], 180, 360, fill=0)
    d.rectangle([140, 210, 372, 470], fill=0)
    for x in range(160, 372, 42):
        d.rectangle([x, 110, x + 14, 456], fill=255)
    for y in (220, 300, 380):
        d.rectangle([150, y, 362, y + 14], fill=255)
    for s in (-1, 1):
        a = math.radians(90 + s * 40)
        d.line([(256 - s * 210, 480), (256 + s * 120, 140)], fill=255, width=26)
        d.line([(256 - s * 200 + s * 30, 420), (256 - s * 150 - s * 30, 440)], fill=255, width=20)
    d.rectangle([40, 470, 472, 496], fill=255)
    return m


def g_emperor():
    """Option C emblem: the marble emperor bust in profile (facing right), a laurel crown."""
    m, d = new()
    d.ellipse([150, 70, 360, 300], fill=255)                       # skull
    d.polygon([(340, 170), (392, 236), (350, 244), (356, 270), (336, 286), (300, 300)], fill=255)  # nose + mouth
    d.rectangle([210, 270, 320, 360], fill=255)                    # neck
    d.pieslice([90, 330, 430, 560], 180, 360, fill=255)            # shoulders (the bust's cut)
    d.rectangle([150, 440, 370, 470], fill=255)
    d.rectangle([180, 470, 340, 500], fill=255)                    # socle
    d.ellipse([288, 156, 312, 176], fill=0)                        # the eye
    for k in range(6):                                             # laurel crown round the back of the head
        a = math.radians(160 + k * 26)
        x, y = 255 + 118 * math.cos(a), 185 + 112 * math.sin(a)
        leaf(d, x, y, 66, 28, a + math.pi / 2 * 0.6, fill=0)
        leaf(d, x, y, 56, 20, a + math.pi / 2 * 0.6, fill=255)
    d.arc([140, 60, 370, 310], 150, 300, fill=0, width=10)
    return m


# ---- TETHYS: wave crests (the new crest), new Site icons, boss emblems
def curl(d, cx, cy, r, a0, sweep, w0, w1, shrink=0.62, fill=255, n=60):
    """A curling wave crest: a stroke along an inward spiral, tapering from w0 to w1 (degrees, y down)."""
    for i in range(n + 1):
        t = i / n
        a = math.radians(a0 + sweep * t)
        rr = r * (1 - shrink * t)
        w = w0 + (w1 - w0) * t
        x, y = cx + rr * math.cos(a), cy + rr * math.sin(a)
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=fill)


def wave_band(d, x0, x1, y, amp, period, w, fill=255, phase=0.0):
    pts = [(x, y + amp * math.sin((x - x0) / period * 2 * math.pi + phase)) for x in np.linspace(x0, x1, 80)]
    d.line(pts, fill=fill, width=int(w), joint="curve")


def g_wave_a():
    """Crest option A, TIDE WHIRL: three breaking crests turning round a calm centre (the tide cycle), in a ring."""
    m, d = new()
    d.ellipse([20, 20, 492, 492], fill=255)
    d.ellipse([52, 52, 460, 460], fill=0)
    for k in range(3):
        rot = k * 120
        a = math.radians(rot - 90)
        # each crest: a body sweeping along the ring, curling inward at its head
        cx, cy = 256 + 92 * math.cos(a), 256 + 92 * math.sin(a)
        curl(d, cx, cy, 120, rot + 90, 250, 70, 14, shrink=0.78)
    d.ellipse([224, 224, 288, 288], fill=255)
    return m


def g_wave_b():
    """Crest option B, MOONWAVE: a full round 'moon' disc cut by three stacked rolling crests rising across it."""
    m, d = new()
    d.ellipse([30, 30, 482, 482], fill=255)
    for k in range(3):
        y = 190 + k * 92
        wave_band(d, 20, 492, y, 18, 160, 34, fill=0, phase=k * 1.4)
        curl(d, 120 + k * 120, y - 8, 46, 200, 230, 30, 8, fill=0, shrink=0.7)
    d.ellipse([60, 60, 452, 452], outline=0, width=10)
    return m


def g_wave_c():
    """Crest option C, CRESCENT SURF: a crescent whose inner curve is one big breaking wave, spray dots at its lip."""
    m, d = new()
    d.ellipse([30, 30, 482, 482], fill=255)
    d.ellipse([130, 10, 520, 400], fill=0)                         # the bite: a crescent
    # the wave: a tail riding up the crescent's inner edge, then a crest that rolls over into a barrel
    curl(d, 318, 228, 150, 130, 330, 70, 10, shrink=0.74)
    d.ellipse([292, 186, 344, 238], fill=0)                        # the barrel's hollow
    for (x, y, r) in ((452, 118, 20), (478, 176, 13), (414, 74, 13)):    # spray
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return m


def g_wave_d():
    """Crest option D, DEEP SWELL: concentric swell bands stacked into a round seal, the top band breaking."""
    m, d = new()
    d.ellipse([24, 24, 488, 488], fill=255)
    d.ellipse([58, 58, 454, 454], fill=0)
    mk = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mk)
    for k in range(4):
        wave_band(md, 40, 472, 170 + k * 80, 22 - k * 3, 150, 40, phase=k * 0.9)
    curl(md, 196, 150, 70, 180, 260, 40, 10, shrink=0.7)
    clip = Image.new("L", (S, S), 0)
    ImageDraw.Draw(clip).ellipse([70, 70, 442, 442], fill=255)
    m.paste(255, (0, 0), ImageChops.multiply(mk, clip))
    return m


def g_buoy():
    """BUOY RELAY (the sea-cable head's relay buoy): a striped buoy riding a swell, its mast light sending arcs."""
    m, d = new()
    d.polygon([(150, 330), (362, 330), (330, 420), (182, 420)], fill=255)     # the hull
    d.rectangle([150, 330, 362, 346], fill=255)
    d.polygon([(196, 330), (236, 170), (276, 170), (316, 330)], fill=255)     # the cage / tower
    d.rectangle([214, 230, 298, 262], fill=0)                                # a stripe cut
    d.rectangle([236, 120, 276, 172], fill=255)                              # lantern
    d.ellipse([228, 92, 284, 148], fill=255)
    for k, r in enumerate((90, 140)):                                        # signal arcs
        for s in (-1, 1):
            a0, a1 = (-60, -20) if s > 0 else (200, 240)
            d.arc([256 - r, 120 - r, 256 + r, 120 + r], a0, a1, fill=255, width=20)
    wave_band(d, 20, 492, 446, 16, 120, 30)
    return m


def g_tap():
    """TAP HOUSE (fresh water by the litre): a tap on a wall plate, its handle, a drop falling from the spout."""
    m, d = new()
    d.rounded_rectangle([40, 120, 110, 330], radius=16, fill=255)            # wall plate
    d.rounded_rectangle([100, 180, 350, 252], radius=30, fill=255)           # the body
    d.pieslice([270, 180, 430, 340], 270, 360, fill=255)                     # the spout bend
    d.pieslice([318, 228, 382, 292], 270, 360, fill=0)
    d.rectangle([350, 256, 430, 300], fill=255)
    d.rectangle([382, 256, 430, 300], fill=255)
    d.rectangle([186, 110, 226, 182], fill=255)                              # handle stem
    d.rounded_rectangle([130, 84, 282, 120], radius=16, fill=255)            # handle bar
    # the drop
    d.ellipse([370, 380, 446, 456], fill=255)
    d.polygon([(408, 326), (373, 400), (443, 400)], fill=255)
    return m


def g_helmet():
    """Option A emblem: the brass diving helmet, front porthole visor, side ports, bolted collar."""
    m, d = new()
    d.ellipse([86, 50, 426, 390], fill=255)
    d.rectangle([110, 330, 402, 420], fill=255)
    d.rounded_rectangle([60, 400, 452, 470], radius=20, fill=255)            # collar
    for x in range(96, 440, 60):
        d.ellipse([x - 12, 423, x + 12, 447], fill=0)
    d.ellipse([166, 120, 346, 300], fill=0)                                  # the visor
    d.ellipse([186, 140, 326, 280], fill=255)
    d.ellipse([200, 154, 312, 266], fill=0)
    d.line([(256, 154), (256, 266)], fill=255, width=12)                     # visor grille
    d.line([(200, 210), (312, 210)], fill=255, width=12)
    for x in (110, 402):                                                     # side ports
        d.ellipse([x - 34, 176, x + 34, 244], fill=0)
        d.ellipse([x - 18, 192, x + 18, 228], fill=255)
    d.rectangle([236, 20, 276, 60], fill=255)                                # the air fitting
    return m


def g_octopus():
    """Option B emblem (THE BLACK SMOKER): an octopus, mantle up, two eyes, eight arms curling, an ink cloud."""
    m, d = new()
    d.ellipse([150, 30, 362, 250], fill=255)                                 # mantle
    d.rectangle([170, 160, 342, 280], fill=255)
    for x in (214, 298):                                                     # eyes
        d.ellipse([x - 26, 200, x + 26, 248], fill=0)
        d.ellipse([x - 14, 212, x + 2, 232], fill=255)
    # six thick arms: each leaves the mantle base, sweeps out and curls back up at its tip (tapered stroke)
    for k, th in enumerate((-78, -48, -18, 18, 48, 78)):
        s = 1 if th > 0 else -1
        x, y = 256 + th * 1.0, 262
        ang = math.radians(90 - th * 0.9)
        L = 260 if abs(th) > 30 else 230
        n = 70
        for i in range(n + 1):
            t = i / n
            w = 46 * (1 - t) + 10
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=255)
            curlk = max(0.0, (t - 0.45) / 0.55)
            a = ang - s * curlk * curlk * math.radians(300)
            x += math.cos(a) * L / n
            y += math.sin(a) * L / n
    for (x, y, r) in ((112, 70, 30), (74, 120, 20)):                         # ink puffs: the black smoke
        d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    return m


def g_jelly():
    """Option C emblem: a jellyfish: scalloped bell, a glowing rim, five tendrils trailing."""
    m, d = new()
    d.pieslice([70, 40, 442, 400], 180, 360, fill=255)
    for k in range(7):                                                       # scalloped rim
        x = 92 + k * 54.6
        d.ellipse([x - 28, 196, x + 28, 248], fill=255)
    d.pieslice([140, 100, 372, 330], 180, 360, fill=0)                       # inner bell
    d.pieslice([170, 130, 342, 300], 180, 360, fill=255)
    for k in range(5):
        x0 = 150 + k * 53
        pts = [(x0 + 24 * math.sin(i / 6.0 + k), 244 + i * 13) for i in range(20)]
        d.line(pts, fill=255, width=20 if k % 2 == 0 else 13)
    return m


GLYPHS = {
    "aurelian": dict(crest=g_laurel_arch, boss=g_emoji_thumb,
                     sites=[("DOLE", "bread ration depot", g_dole3), ("ANNONA", "granary + grain office", g_annona),
                            ("LUDUS", "arena gym + stream studio", g_ludus2), ("AQUEDUCT", "data conduit pump station", g_aqueduct3),
                            ("ATRIUM", "patron's debt office", g_atrium), ("CURIA", "the patrons' senate house", g_curia),
                            ("TOLL GATE", "triumph-gate toll", g_tollgate)]),
    "tethys": dict(crest=g_wave_a, boss=g_octopus, sub_mark=g_nautilus,
                   sites=[("AIR LEASE", "oxygen depot", g_air), ("PUMP HOUSE", "seawall lock + pumps", g_pump),
                          ("BUOY RELAY", "sea-cable head relay", g_buoy), ("COLD VAULT", "submerged data pod", g_coldvault),
                          ("TAP HOUSE", "fresh water by the litre", g_tap), ("DOCK LOCK", "sub dock airlock", g_airlock)]),
}
OLD = {"aurelian": dict(boss=g_verdict, boss2=g_verdict2, boss3=g_verdict3, dole=g_dole, dole2=g_dole2, ludus=g_ludus,
                         aqueduct=g_aqueduct, aqueduct2=g_aqueduct2, thermae=g_thermae),
       "tethys": dict(crest=g_nautilus, crest2=g_wave_c, boss=g_smoker, cable=g_cable, desal=g_desal)}
CREST_OPTIONS = [("A  TIDE WHIRL", g_wave_a), ("B  MOONWAVE", g_wave_b), ("C  CRESCENT SURF", g_wave_c), ("D  DEEP SWELL", g_wave_d)]
BOSS_OPTIONS = {"aurelian": [("A  COLOSSEUM", g_verdict3), ("B  ARENA", g_arena_gate), ("C  EMPEROR", g_emperor)],
                "tethys": [("A  DIVER", g_helmet), ("B  OCTOPUS", g_octopus), ("C  JELLYFISH", g_jelly)]}

_mc = {}


def mask(fn, px=None):
    if fn not in _mc:
        _mc[fn] = fn()
    m = _mc[fn]
    return m if px is None else m.resize((px, px), Image.LANCZOS)


def tint(m, c):
    im = Image.new("RGBA", m.size, tuple(c[:3]) + (0,))
    im.putalpha(m)
    return im


# ------------------------------------------------------------------ vinyl icon stickers
def icon_sticker(fn, fg, bg, px=150, seed=5, border=10, ring_col=None, gloss_k=0.22, curl=None):
    """A die-cut vinyl icon: a coloured disc, the white (or fg) glyph, an ink keyline; built at SL.SS."""
    SS = SL.SS
    P = px * SS
    pad = 40 * SS
    art = Image.new("RGBA", (P + 2 * pad, P + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(art)
    o = pad
    d.ellipse([o, o, o + P, o + P], fill=SL.INK + (255,))
    k = int(5 * SS)
    d.ellipse([o + k, o + k, o + P - k, o + P - k], fill=tuple(bg) + (255,))
    if ring_col:
        d.ellipse([o + k * 2.2, o + k * 2.2, o + P - k * 2.2, o + P - k * 2.2], outline=tuple(ring_col) + (255,), width=int(3 * SS))
    gpx = int(P * 0.62)
    g = mask(fn, gpx)
    keyl = SL.dilate(g, 6 * SS)
    gx, gy = o + (P - gpx) // 2, o + (P - gpx) // 2
    art.alpha_composite(tint(keyl, SL.INK), (gx, gy))
    art.alpha_composite(tint(g, fg), (gx, gy))
    # a soft bevel highlight on the disc
    hl = Image.new("L", art.size, 0)
    ImageDraw.Draw(hl).ellipse([o + P * 0.12, o + P * 0.06, o + P * 0.88, o + P * 0.5], fill=40)
    hl = hl.filter(ImageFilter.GaussianBlur(P * 0.06))
    art = SL.over(art, (255, 255, 255), ImageChops.multiply(hl, art.split()[3]))
    return SL.build_sticker(art, border=border, gloss_k=gloss_k, seed=seed, curl=curl)


def word_sticker(lines, size, fill, seed=7, font=None, border=12, jitter=2.0, track=-1):
    return U.sticker(lines, size=size, fill=fill, seed=seed, jitter=jitter, border=border, font_path=font, track=track)


def grad(c, k_top=1.25, k_bot=0.78):
    t = tuple(min(255, int(v * k_top + 18)) for v in c)
    b = tuple(int(v * k_bot) for v in c)
    return ("grad", t, b)


# ------------------------------------------------------------------ City Grid site marker (bible 4.5 grammar)
def site_marker(img, x, y, corp, glyph_fn=None, tier=1, avail="next", k=1.0, label=None, cleared=False, glyph_col=None):
    """Pad (corp dark + corp pins), icon disc (the crest in the corp colour), state ring, tier pips."""
    pc = col(corp, "primary")
    dark = col(corp, "dark")
    d = ImageDraw.Draw(img)
    # pad: a flat diamond socket, corp pins
    r = 30 * k
    q = [(x, y - r * 0.5), (x + r, y), (x, y + r * 0.5), (x - r, y)]
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).polygon(q, fill=tuple(int(v * 0.5) for v in dark) + (225,), outline=pc + (200,))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    for i in range(6):
        t = (i + 0.5) / 6
        px_, py_ = q[3][0] + (q[2][0] - q[3][0]) * t, q[3][1] + (q[2][1] - q[3][1]) * t
        d.rectangle([px_ - 1.5 * k, py_ + 1 * k, px_ + 1.5 * k, py_ + 5 * k], fill=pc + (230,))
    # disc
    px = int(54 * k)
    cy = y - 26 * k
    SSx = 4
    P = px * SSx
    disc = Image.new("RGBA", (P, P), (0, 0, 0, 0))
    dd = ImageDraw.Draw(disc)
    dd.ellipse([SSx, SSx, P - SSx, P - SSx], fill=dark + (255,), outline=(8, 8, 12, 255), width=3 * SSx)
    g = mask(glyph_fn or GLYPHS[corp]["crest"], int(P * 0.70))
    gc = glyph_col or pc
    if cleared:
        gc = (150, 150, 160)
    disc.alpha_composite(tint(g, gc), ((P - g.width) // 2, (P - g.height) // 2))
    disc = disc.resize((px, px), Image.LANCZOS)
    img.alpha_composite(disc, (int(x - px / 2), int(cy - px / 2)))
    rc = {"next": hx("#FF8C1A"), "notyet": hx("#F2F6FF"), "yours": hx("#D4FF00")}[avail]
    m = Image.new("L", img.size, 0)
    rr = px / 2 + 6 * k
    ImageDraw.Draw(m).ellipse([x - rr, cy - rr, x + rr, cy + rr], outline=255, width=max(3, int(5 * k)))
    if avail != "notyet":
        img = SL.over(img, rc, SL.scale_mask(m.filter(ImageFilter.GaussianBlur(6 * k)), 0.8))
    img = SL.over(img, (6, 5, 10), SL.shift(m, 1, 2))
    img = SL.over(img, rc, m)
    d = ImageDraw.Draw(img)
    s, gap = 7 * k, 5 * k
    w = tier * s + (tier - 1) * gap
    for i in range(tier):
        x0 = x - w / 2 + i * (s + gap)
        yy = cy + rr + 7 * k
        d.rectangle([x0 - 1, yy - 1, x0 + s + 1, yy + s + 1], fill=(8, 8, 12, 255))
        d.rectangle([x0, yy, x0 + s, yy + s], fill=(rc if avail != "notyet" else (210, 206, 220)) + (255,))
    if cleared:
        bx, by, br = x + rr * 0.72, cy - rr * 0.72, 11 * k
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=(40, 40, 48, 255), outline=(200, 200, 210, 255), width=2)
        d.line([(bx - br * 0.5, by), (bx - br * 0.1, by + br * 0.45), (bx + br * 0.55, by - br * 0.45)], fill=(230, 230, 240, 255), width=3)
    if label:
        f = U.F(U.MONO, int(15 * k))
        tw_ = U.tw(label, f, 1.0)
        d.rectangle([x - tw_ / 2 - 8, y + 18 * k, x + tw_ / 2 + 8, y + 18 * k + 24 * k], fill=(5, 13, 28, 235), outline=rc + (220,))
        U.text(img, (x, y + 30 * k), label, f, rc if avail != "notyet" else (220, 218, 228), "mm", 1.0)
    return img


# ------------------------------------------------------------------ board helpers
def board(w=2560, h=1440, top=(10, 9, 16), bot=(4, 4, 8), seed=1):
    a = np.zeros((h, w, 3), np.float32)
    t = np.linspace(0, 1, h)[:, None]
    a[:] = (np.array(top) * (1 - t) + np.array(bot) * t)[:, None, :] if False else 0
    for c in range(3):
        a[..., c] = (top[c] * (1 - t) + bot[c] * t)
    rng = np.random.default_rng(seed)
    a += rng.normal(0, 2.2, (h, w, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


def section(img, xy, title, sub=None, accent=(92, 225, 255)):
    x, y = xy
    d = U.BD(img)
    d.rectangle([x, y + 4, x + 7, y + 34], fill=accent + (255,))
    U.text(img, (x + 18, y), title, U.F(U.PLEX_M, 30), (240, 238, 232), "la", 1.2)
    if sub:
        U.text(img, (x + 18, y + 40), sub, U.F(U.MONO, 17), (150, 160, 178), "la", 0.8)
    return img


def swatch(img, x, y, c, name, hexs, w=150, h=96, dark_text=None):
    d = ImageDraw.Draw(img)
    d.rectangle([x, y, x + w, y + h], fill=tuple(c) + (255,), outline=(0, 0, 0, 255), width=2)
    lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
    tc = (14, 12, 18) if lum > 140 else (240, 238, 232)
    U.text(img, (x + 10, y + h - 46), name, U.F(U.PLEX_M, 18), tc, "la", 0.6)
    U.text(img, (x + 10, y + h - 24), hexs, U.F(U.MONO, 17), tc, "la", 0.6)
    return img


def para(img, xy, lines, size=19, col=(214, 220, 232), font=None, lh=1.38, track=0.0):
    x, y = xy
    f = U.F(font or U.PLEX, size)
    for ln in lines:
        if ln.startswith("**"):
            U.text(img, (x, y), ln.strip("*"), U.F(U.PLEX_M, size), (255, 255, 255), "la", track)
        else:
            U.text(img, (x, y), ln, f, col, "la", track)
        y += size * lh
    return y


def wrap(s, n):
    out, cur = [], ""
    for w in s.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


def save(img, path):
    img.convert("RGB").save(path, optimize=True)
    print("wrote", path, img.size)
