"""Round 18 raid grid: the finished concept frames (1920 x 1080) and the contact sheet.

python screens.py            -> ../raid_options.png, ../raid_setup_night.png, ../raid_setup_day.png,
                                ../raid_wave_night.png, ../raid_heat_levels.png, ../contact_sheet.jpg
Base: finish.finish() over the Blender passes in ../scratch/bl (run run_blender.py first).
Overlay (locked kit, imported in place from round3_overlay/combined_v2): vinyl stickers for every word
and object (panels, unit cards, labels), opaque waxy grease pencil (yellow = plans, red = threats).
The grid itself is NOT overlay: nodes and links are decals on the street plane (netdecal.py).
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
KIT = os.path.abspath(os.path.join(HERE, "..", "..", "round3_overlay", "combined_v2", "scripts"))
sys.path.insert(1, KIT)

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont, ImageFilter  # noqa: E402

import layout as LY  # noqa: E402
import finish as FN  # noqa: E402
import netdecal as ND  # noqa: E402
import kit as K  # noqa: E402

SL, T, PC = K.SL, K.T, K.PC
OUT = os.path.dirname(HERE)
GLYPHS = ND.GLYPHS
S = SL.SS

# MODEM / UI colours
PINK, CYAN, GREEN, VIOLET, AMBER = (255, 61, 168), (92, 225, 255), (123, 224, 123), (200, 90, 255), (255, 176, 0)
HARM, HALCYON, INKC, PAPER = (255, 68, 51), (140, 123, 255), (14, 12, 20), (244, 241, 233)
FACE = (16, 15, 24)
STATUS = {"holds": ("HOLDS", GREEN), "disabled": ("DISABLED", AMBER), "seized": ("SEIZED", HARM), "home": ("HOME", PINK)}
Y_PEN, R_PEN = K.PAL_F["yellow"], K.PAL_F["red"]


# ------------------------------------------------------------------ sticker drawing helpers
def F(path, size):
    return ImageFont.truetype(path, int(size * S))


class Pen:
    """Draw on sticker art in 1x units."""

    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img)

    def text(self, x, y, s, font=SL.PLEX, size=16, col=PAPER, anchor="la"):
        self.d.text((x * S, y * S), s, font=F(font, size), fill=tuple(col) + (255,), anchor=anchor)

    def rect(self, x0, y0, x1, y1, col, r=0, outline=None, width=0):
        if r:
            self.d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], r * S, fill=None if col is None else tuple(col) + (255,),
                                     outline=None if outline is None else tuple(outline) + (255,), width=int(width * S))
        else:
            self.d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=None if col is None else tuple(col) + (255,),
                             outline=None if outline is None else tuple(outline) + (255,), width=int(width * S))

    def line(self, pts, col, w=1.0):
        self.d.line([(x * S, y * S) for x, y in pts], fill=tuple(col) + (255,), width=max(1, int(w * S)))

    def ellipse(self, x0, y0, x1, y1, col=None, outline=None, width=0):
        self.d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=None if col is None else tuple(col) + (255,),
                       outline=None if outline is None else tuple(outline) + (255,), width=int(width * S))

    def glyph(self, name, cx, cy, size, col):
        g = Image.open(os.path.join(GLYPHS, name + ".png")).convert("RGBA").split()[3]
        g = g.resize((int(size * S), int(size * S)), Image.LANCZOS)
        lay = Image.new("RGBA", g.size, tuple(col) + (255,))
        lay.putalpha(g)
        self.img.alpha_composite(lay, (int((cx - size / 2) * S), int((cy - size / 2) * S)))

    def chip(self, x, y, label, col, size=15, pad=7, txt=INKC):
        f = F(SL.ANTON, size)
        w = f.getlength(label) / S + 2 * pad
        self.rect(x, y, x + w, y + size * 1.45, col, r=4)
        self.text(x + w / 2, y + size * 0.74, label, SL.ANTON, size, txt, "mm")
        return w


def panel(w, h, fn, face=FACE, material="gloss", border=9, radius=12, seed=5, curl=None):
    art = Image.new("RGBA", (int(w * S), int(h * S)), (0, 0, 0, 0))
    p = Pen(art)
    p.rect(0, 0, w - 1, h - 1, face, r=radius)
    fn(p)
    return SL.build_sticker(art, border=border, material=material, seed=seed, curl=curl)


def put(img, sd, x, y, angle=0.0, **kw):
    return K.place_sticker(img, sd, x, y, angle=angle, **kw)


def P(x, y, z=0.0):
    p = LY.project(x, y, z)
    return p[0], p[1]


# ------------------------------------------------------------------ the shared pieces
def title(img, big, sub, col=K.FILL_YELLOW, x=40, y=26):
    sd = K.word_sticker([big], 52, [col], seed=11, border=14)
    w = sd["img"].size[0] / S
    img = put(img, sd, x + w / 2 - 20, y + 40, angle=-1.5)
    lab = panel(len(sub) * 9.2 + 28, 30, lambda p: p.text(14, 15, sub, SL.MONO, 15, CYAN, "lm"), border=6, seed=12)
    return put(img, lab, x + 14 + (len(sub) * 9.2 + 28) / 2, y + 100, angle=0.6)


def node_label(key, st, extra=None):
    n = LY.NODES[key]
    word, col = STATUS[st]
    name = n[3]

    def fn(p):
        p.text(10, 9, name, SL.MONO, 13, INKC)
        f = F(SL.MONO, 13)
        x = 10
        if extra:
            p.text(10, 27, extra, SL.MONO, 11, (90, 86, 100))
        wl = f.getlength(name) / S
        p.chip(max(wl + 18, 10), 6, word if st != "home" else "HOME -8", col, size=13)
    f = F(SL.MONO, 13)
    wl = f.getlength(name) / S
    wc = F(SL.ANTON, 13).getlength(word if st != "home" else "HOME -8") / S + 14
    w = wl + wc + 30
    return panel(w, 44 if extra else 30, fn, face=PAPER, border=6, radius=6, seed=sum(map(ord, key)) % 97)


def integrity_bar(key, now, mx, col):
    def fn(p):
        p.text(8, 11, "%d/%d" % (now, mx), SL.MONO, 12, PAPER, "lm")
        segs = 10
        for i in range(segs):
            on = i < round(now / mx * segs)
            x = 58 + i * 9
            p.rect(x, 5, x + 7, 17, col if on else (52, 48, 62), r=1)
    return panel(152, 22, fn, border=5, radius=5, seed=31 + len(key))


def asset_card(name, glyph, hp, copies, desc, col, seed, placed=None):
    def fn(p):
        p.rect(10, 10, 140, 76, (30, 28, 42), r=8)
        p.glyph(glyph, 75, 43, 54, col)
        p.text(12, 84, name, SL.ANTON, 21, PAPER)
        p.text(12, 114, "HP %d" % hp, SL.MONO, 13, col)
        p.text(138, 114, "x%d" % copies, SL.MONO, 13, PAPER, "ra")
        y = 134
        for line in desc:
            p.text(12, y, line, SL.PLEX, 12, (190, 186, 205))
            y += 15
        p.rect(0, 0, 149, 5, col, r=2)
        if placed:
            p.chip(78, 14, placed, col, size=11)
    return panel(150, 172, fn, border=7, radius=10, seed=seed)


TRAY = [("TURRET", "picto_target", 12, 1, ["4 dmg, range 1", "first in path"], CYAN),
        ("RAILGUN", "slice_zero_day", 10, 0, ["8 dmg, range 2", "hardest hitter"], CYAN),
        ("ICE LOCK", "state_frozen", 8, 1, ["holds a threat", "for 2 steps"], (170, 230, 255)),
        ("FLAK ARRAY", "placeholder_storm", 9, 1, ["2 dmg x3, range 1", "weakest threat"], AMBER),
        ("DECOY", "placeholder_phishing", 6, 1, ["pull 3: drags", "routes to it"], VIOLET),
        ("TAR PIT", "state_locked", 4, 2, ["holds 3 steps", "fragile"], GREEN)]


def tray(img, dragged="FLAK ARRAY", y=985, x0=560):
    lab = panel(300, 30, lambda p: p.text(12, 15, "DEFENCE LOADOUT  //  ARMORY 5/6", SL.MONO, 15, AMBER, "lm"), border=6, seed=40)
    img = put(img, lab, x0 + 4 * 162 + 40, y - 110, angle=-0.8)
    x = x0
    for i, (nm, gl, hp, cp, ds, col) in enumerate(TRAY):
        if nm == dragged:
            x += 162
            continue
        placed = "PLACED" if cp == 0 else None
        sd = asset_card(nm, gl, hp, cp, ds, col, 50 + i, placed=placed)
        img = put(img, sd, x, y, angle=[-2, 1.5, -1, 2, -1.5, 1][i])
        x += 162
    return img


def start_button(img, x, y):
    sd = K.word_sticker(["START DEFENSE"], 40, [K.FILL_PINK], seed=21, border=13)
    return put(img, sd, x, y, angle=-2)


# ------------------------------------------------------------------ grease pencil helpers
def jitter_path(pts, rng, amp=2.0, step=6):
    p = T.resample(np.array(pts, float), step)
    n = len(p)
    t = np.linspace(0, 1, n)
    for f in (0.8, 1.7):
        ph = rng.random() * 6
        d = np.stack([np.sin(2 * math.pi * (f * t * n / 40 + ph)), np.cos(2 * math.pi * (f * t * n / 47 + ph))], 1)
        p = p + d * amp * rng.uniform(0.5, 1.0)
    return T.chaikin(p, 2)


def route_screen(rid):
    """The threat lane polyline (world, offset like the decal lane), trimmed at the pads, projected."""
    pts = LY.route_points(rid)
    linkset = set()
    for a, b in LY.LINKS:
        linkset.add((LY.pt(a), LY.pt(b)))
        linkset.add((LY.pt(b), LY.pt(a)))
    out = []
    for i in range(len(pts) - 1):
        a, b = np.array(pts[i], float), np.array(pts[i + 1], float)
        d = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-d[1], d[0]])
        off = -5.6 if (pts[i], pts[i + 1]) in linkset else 0.0
        trim0 = ND.PAD_R * 0.9
        trim1 = ND.PAD_R * (1.3 if i == len(pts) - 2 else 0.2)
        out.append(a + d * trim0 + nrm * off)
        out.append(b - d * trim1 + nrm * off)
    return [P(x, y) for x, y in out]


def pencil_routes(L, rng, alpha_scale=1.0, letters=True):
    for i, rid in enumerate(["r1", "r2", "r3"]):
        pts = route_screen(rid)
        path = jitter_path(pts, rng, 1.6)
        L.strokes(T.arrow_strokes(path, 6.5, R_PEN, rng, head=22))
        e = LY.pt(LY.ROUTES[rid][0])
        ex, ey = P(*e)
        L.wax_stroke(T.hand_circle(ex, ey, 46, 30, rng, turns=1.15), 6.0, R_PEN)
        if letters:
            lx, ly = ex + (-62 if ex > 960 else 62), ey - 34
            if rid == "r3":
                lx, ly = ex + 58, ey - 30
            L.strokes(T.letter_strokes("ABC"[i], lx, ly, 30, 5.5, R_PEN, rng))


# ------------------------------------------------------------------ frames
SETUP_ST = {k: v[4] for k, v in LY.NODES.items()}
LABEL_POS = {"core": (960, 672), "relay": (640, 820), "firewall": (640, 352), "vault": (1310, 455),
             "proxy": (410, 640), "safe": (1295, 820)}


def setup_frame(mode):
    base = FN.finish("setup_h1", mode, "C", SETUP_ST, heat=1, seed=1)
    img = base
    rng = np.random.default_rng(1801)
    # ---- grease pencil (under the stickers)
    L = T.Layer(rng)
    pencil_routes(L, rng)
    # plan: flak array onto the proxy (yellow)
    px, py = P(-60, 20)
    L.wax_stroke(T.hand_circle(px, py, 74, 48, rng, turns=1.2), 7.0, Y_PEN)
    L.strokes(T.arrow_strokes(T.bezier((470, 712), (440, 650), (500, 622)), 7.0, Y_PEN, rng, head=20))
    L.strokes(T.letter_strokes("FLAK HERE?", 450, 488, 22, 4.6, Y_PEN, rng, angle=-0.05))
    # threat note on the vault
    vx, vy = P(80, -50)
    L.strokes(T.letter_strokes("THEY WANT\nTHE VAULT", vx + 10, vy - 210, 19, 4.2, R_PEN, rng, angle=0.04, align="left"))
    L.strokes(T.arrow_strokes(T.bezier((vx - 30, vy - 168), (vx - 60, vy - 100), (vx - 30, vy - 50)), 5.0, R_PEN, rng, head=14))
    L.light()
    img = K.pencil_composite(img, L)
    # ---- node labels (stickers beside the pads, never on rooftops)
    for key, (lx, ly) in LABEL_POS.items():
        img = put(img, node_label(key, SETUP_ST[key]), lx, ly, angle=rng.uniform(-2, 2))
    # ---- left: YOUR NODES + THREAT INTEL
    img = title(img, "RAID SETUP", "03 CELL DEFENSE  //  COMPLIANCE SWEEP")
    img = put(img, nodes_panel(), 175, 330, angle=-1.0)
    img = put(img, intel_panel(), 1752, 582, angle=1.2)
    # ---- right: raid card + START DEFENSE
    img = put(img, raid_card(), 1752, 288, angle=1.4)
    img = start_button(img, 1690, 1010)
    # ---- bottom: loadout tray, the dragged card hovering over the map
    img = tray(img)
    img = put(img, asset_card(*TRAY[3][:5], TRAY[3][5], 53), 462, 800, angle=-9, hover=0.7)
    return img


def nodes_panel():
    rows = [("CORE", "home", "TURRET", "50"), ("FIREWALL RELAY", "holds", "TURRET+ICE", "30"),
            ("RELAY", "holds", "-", "15"), ("SAFEHOUSE", "holds", "SENTRY", "20"),
            ("VAULT TERMINAL", "disabled", "RAILGUN", "20"), ("PROXY RELAY", "seized", "-", "15")]

    def fn(p):
        p.text(14, 14, "YOUR NODES", SL.ANTON, 24, PAPER)
        p.text(292, 22, "IF IT RAN NOW", SL.MONO, 11, (150, 146, 170), "ra")
        y = 56
        for nm, st, assets, integ in rows:
            word, col = STATUS[st]
            p.rect(14, y - 2, 18, y + 30, col)
            p.text(26, y, nm, SL.MONO, 14, PAPER)
            p.text(26, y + 17, assets + "   INT " + integ, SL.MONO, 11, (150, 146, 170))
            lab = word if st != "home" else "HOME -8"
            fw = F(SL.ANTON, 13).getlength(lab) / S + 14
            p.chip(292 - fw, y + 4, lab, col, size=13)
            y += 40
    return panel(306, 300, fn, seed=61)


def intel_panel():
    rows = [("A", "EAST", "BAILIFF  COURIER", "armour + fast, go for the vault"),
            ("B", "WEST", "HAULER  INSPECTOR", "slow truck + quick inspector"),
            ("C", "SOUTH", "CUSTOMS  LANDER", "seals a link, drops in")]

    def fn(p):
        p.text(14, 14, "THREAT INTEL", SL.ANTON, 24, PAPER)
        p.glyph("special_citation", 280, 30, 30, HALCYON)
        p.text(14, 48, "HALCYON CIVIC  //  6 THREATS  //  STRENGTH 52", SL.MONO, 11, HALCYON)
        y = 72
        for k, d, who, what in rows:
            p.ellipse(14, y, 40, y + 26, col=HARM)
            p.text(27, y + 13, k, SL.ANTON, 17, INKC, "mm")
            p.text(50, y, who, SL.MONO, 14, PAPER)
            p.text(50, y + 17, d + "  " + what, SL.PLEX, 11, (175, 170, 192))
            y += 44
    return panel(306, 210, fn, seed=62)


def raid_card():
    def fn(p):
        p.rect(0, 0, 299, 36, HARM, r=10)
        p.rect(0, 20, 299, 36, HARM)
        p.text(150, 19, "RAID INCOMING", SL.ANTON, 22, INKC, "mm")
        p.text(16, 48, "COMPLIANCE SWEEP", SL.ANTON, 26, PAPER)
        p.text(16, 82, "HALCYON CIVIC  //  HEAT 50 RAID", SL.MONO, 12, HALCYON)
        # forecast ring stamp
        p.ellipse(16, 106, 136, 226, outline=AMBER, width=3)
        p.ellipse(24, 114, 128, 218, outline=AMBER, width=1)
        p.text(76, 134, "IF IT RUNS", SL.MONO, 10, AMBER, "mm")
        p.text(76, 147, "NOW:", SL.MONO, 10, AMBER, "mm")
        p.text(76, 176, "HOME", SL.ANTON, 18, PAPER, "mm")
        p.text(76, 202, "50 > 42", SL.ANTON, 20, PINK, "mm")
        y = 112
        for k, v, col in (("DISABLED", "1", AMBER), ("SEIZED", "1", HARM), ("HOLD", "3", GREEN), ("ROUTES", "3", PAPER)):
            p.text(152, y, k, SL.MONO, 13, (170, 166, 188))
            p.text(284, y - 4, v, SL.ANTON, 22, col, "ra")
            y += 28
        p.line([(16, 240), (284, 240)], (60, 56, 74), 1)
        p.text(16, 252, "ENTRY SITES 3   FROZEN LINKS 0", SL.MONO, 12, (170, 166, 188))
        p.text(16, 272, "WAVE 1 / 2   PLAYOUT 30 STEPS", SL.MONO, 12, (170, 166, 188))
    return panel(300, 300, fn, seed=63)


def wave_frame():
    st = dict(SETUP_ST)
    st["proxy"] = "seized"
    scene0 = json.load(open(os.path.join(FN.SRC, "wave_h2_scene.json")))
    marks = [tuple(scene0["spots"][k][:2]) for k in ("bailiff", "hauler", "inspector", "customs", "lander", "courier")]
    base = FN.finish("wave_h2", "night", "C", st, wave=True, heat=2, seed=3, threats=marks)
    img = base
    rng = np.random.default_rng(1802)
    scene = json.load(open(os.path.join(FN.SRC, "wave_h2_scene.json")))
    sp = {k: P(*v[:2], v[2]) for k, v in scene["spots"].items()}
    L = T.Layer(rng)
    # during the playout the routes live on the street (red decal lanes); the pencil only marks
    # where each live threat is heading next
    heads = {"bailiff": (-1, 0), "hauler": (1, 0), "inspector": (1, 0), "customs": (-1, 0)}
    for k, (hx_, hy_) in heads.items():
        wx, wy = scene0["spots"][k][:2]
        a = P(wx + hx_ * 12, wy + hy_ * 12)
        b = P(wx + hx_ * 34, wy + hy_ * 34)
        L.strokes(T.arrow_strokes(jitter_path([a, b], rng, 0.8, 3), 6.0, R_PEN, rng, head=16))
    # destroyed courier: red X
    cx, cy = sp["courier"]
    for a, b in (((cx - 20, cy - 18), (cx + 20, cy + 16)), ((cx + 20, cy - 18), (cx - 18, cy + 18))):
        L.wax_stroke(np.array([a, b]), 6.5, R_PEN)
    L.strokes(T.letter_strokes("DOWN", cx + 4, cy - 44, 17, 4.0, R_PEN, rng))
    # lander: circle + INCOMING
    lx, ly = sp["lander"]
    L.wax_stroke(T.hand_circle(lx, ly + 20, 52, 64, rng), 6.0, R_PEN)
    L.strokes(T.letter_strokes("INCOMING", lx + 10, ly - 70, 18, 4.2, R_PEN, rng))
    # yellow: the flak worked, hold the proxy
    hx, hy = sp["hauler"]
    L.strokes(T.letter_strokes("HOLD IT!", hx + 120, hy + 150, 22, 4.8, Y_PEN, rng, angle=-0.06))
    L.light()
    img = K.pencil_composite(img, L)
    # integrity bars above the pads (on the street side of each node)
    integ = {"core": (50, 50), "firewall": (27, 30), "relay": (15, 15), "safe": (14, 20), "vault": (6, 20), "proxy": (5, 15)}
    for key, (lx, ly) in LABEL_POS.items():
        now, mx = integ[key]
        stt = st[key]
        col = STATUS[stt][1] if key != "core" else PINK
        if key == "vault":
            col = AMBER
        if key == "proxy":
            col = HARM
        img = put(img, integrity_bar(key, now, mx, col), lx, ly - 26, angle=rng.uniform(-1.5, 1.5))
        img = put(img, small_tag(LY.NODES[key][3]), lx, ly + 4, angle=rng.uniform(-1.5, 1.5))
    # damage numbers (red vinyl) at hits
    for k, txt, dx, dy in (("bailiff", "-8", -56, -40), ("inspector", "-3", 52, -46), ("hauler", "-6", -60, -50),
                           ("customs", "-3", -58, -40)):
        x, y = sp[k]
        img = put(img, K.word_sticker([txt], 30, [K.FILL_RED], seed=70 + len(k), border=9), x + dx, y + dy, angle=rng.uniform(-8, 8))
    # threat tags
    for k, nm, hp in (("bailiff", "BAILIFF", (4, 12)), ("hauler", "HAULER", (9, 15)), ("inspector", "INSPECTOR", (3, 6)),
                      ("customs", "CUSTOMS", (5, 8)), ("lander", "LANDER", (10, 10))):
        x, y = sp[k]
        ox, oy = TAG_OFF[k]
        img = put(img, threat_tag(nm, *hp), x + ox, y + oy, angle=rng.uniform(-2, 2))
    img = title(img, "RAID IN PROGRESS", "03 CELL DEFENSE  //  COMPLIANCE SWEEP  //  STEP 07/30", col=K.FILL_RED)
    img = put(img, feed_panel(), 175, 470, angle=-1.0)
    img = put(img, heat_badge(52, "CHOPPERS UP"), 1760, 170, angle=2.0)
    img = put(img, result_card(), 1752, 470, angle=1.2)
    img = put(img, speed_strip(), 960, 1022, angle=-0.6)
    return img


TAG_OFF = {"bailiff": (40, -72), "hauler": (-30, -78), "inspector": (40, -84), "customs": (60, 50), "lander": (150, 40)}


def small_tag(name):
    f = F(SL.MONO, 12)
    w = f.getlength(name) / S + 20
    return panel(w, 22, lambda p: p.text(10, 11, name, SL.MONO, 12, INKC, "lm"), face=PAPER, border=5, radius=5, seed=len(name))


def threat_tag(name, hp, mx):
    def fn(p):
        p.rect(0, 0, 6, 34, HALCYON)
        p.text(12, 4, name, SL.MONO, 12, PAPER)
        for i in range(mx if mx <= 15 else 15):
            p.rect(12 + i * 7, 22, 17 + i * 7, 29, HARM if i < hp else (60, 54, 70))
    return panel(max(118, 14 + 7 * mx + 10), 34, fn, border=5, radius=5, seed=len(name) + 3)


def feed_panel():
    rows = [("07", "RAILGUN > BAILIFF", "-8", CYAN), ("07", "FLAK x3 > HAULER", "-6", AMBER),
            ("07", "FW TURRET > INSPECTOR", "-3", CYAN), ("06", "COURIER DESTROYED", "", GREEN),
            ("06", "HAULER ON PROXY", "INT -4", HARM), ("06", "LANDER DROPS SOUTH", "", HARM),
            ("05", "CUSTOMS SEALS LINK S2", "", HARM), ("05", "VAULT HIT", "INT -6", AMBER)]

    def fn(p):
        p.text(14, 14, "LIVE RAID FEED", SL.ANTON, 24, PAPER)
        y = 54
        for st, msg, v, col in rows:
            p.text(14, y, st, SL.MONO, 12, (120, 116, 140))
            p.rect(38, y + 2, 41, y + 14, col)
            p.text(48, y, msg, SL.MONO, 13, PAPER)
            p.text(292, y, v, SL.MONO, 13, col, "ra")
            y += 25
    return panel(306, 262, fn, seed=64)


def heat_badge(v, word):
    def fn(p):
        p.rect(0, 0, 219, 30, HARM, r=8)
        p.rect(0, 16, 219, 30, HARM)
        p.text(110, 15, "HEAT", SL.ANTON, 20, INKC, "mm")
        p.text(18, 40, str(v), SL.ANTON, 60, PAPER)
        p.text(118, 50, "BAND 2", SL.MONO, 13, HARM)
        p.text(118, 70, word, SL.MONO, 13, PAPER)
        for i in range(10):
            p.rect(18 + i * 19, 122, 32 + i * 19, 132, HARM if i < 5 else (60, 54, 70))
    return panel(220, 144, fn, seed=65)


def result_card():
    def fn(p):
        p.text(16, 12, "FORECAST > RESULT", SL.ANTON, 22, PAPER)
        p.ellipse(16, 46, 116, 146, outline=GREEN, width=3)
        p.text(66, 82, "HOME", SL.ANTON, 18, PAPER, "mm")
        p.text(66, 110, "50", SL.ANTON, 26, PINK, "mm")
        y = 50
        for k, v, col in (("DESTROYED", "1/6", GREEN), ("ON NODES", "2", HARM), ("REACHED HOME", "0", PINK)):
            p.text(132, y, k, SL.MONO, 12, (170, 166, 188))
            p.text(284, y - 3, v, SL.ANTON, 20, col, "ra")
            y += 30
    return panel(300, 162, fn, seed=66)


def speed_strip():
    def fn(p):
        x = 12
        for lab, on in (("1x", False), ("2x", True), ("4x", False), ("SKIP", False)):
            w = 64 if lab != "SKIP" else 84
            p.rect(x, 8, x + w, 44, PINK if on else (36, 34, 50), r=6)
            p.text(x + w / 2, 26, lab, SL.ANTON, 22, INKC if on else PAPER, "mm")
            x += w + 10
        p.text(x + 8, 26, "STEP 07 / 30", SL.MONO, 15, CYAN, "lm")
    return panel(470, 52, fn, seed=67)


# ------------------------------------------------------------------ options sheet
OPT_TXT = {
    "A": ("A  PAINTED LIGHT", ["road paint that glows: double lane", "line + flow chevrons, roundel pads", "+ cheapest: one decal texture",
                               "- reads as traffic paint, flat", "- chevrons fight the real lanes"]),
    "B": ("B  HOLO FLOOR TILES", ["tiles projected on the asphalt,", "hex-tile pads, glyph built of tiles", "+ most 'cyber', packets read well",
                                 "- busy: tiles x fog x rain", "- glows white, status hue washes"]),
    "C": ("C  CIRCUIT INLAY", ["3-trace bus cut into the street,", "pads are CHIP SOCKETS at crossings", "+ units plug into the socket",
                               "+ status hue stays readable", "+ = the net reading of the city"]),
}


def options_sheet():
    W, H = LY.W, LY.H
    canvas = np.zeros((H, W, 3), np.float32) + np.array([0.035, 0.03, 0.06], np.float32)
    crop = (500, 150, 1300, 1050)       # the network, same window for all three
    pw, ph = 600, int(600 * (crop[3] - crop[1]) / (crop[2] - crop[0]))
    xs = [40 + i * 620 for i in range(3)]
    y0 = 136
    for i, ap in enumerate("ABC"):
        base = FN.finish("setup_h1", "night", ap, SETUP_ST, heat=1, seed=1, fog=0.7)
        im = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8)).crop(crop).resize((pw, ph), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255
        canvas[y0:y0 + ph, xs[i]:xs[i] + pw] = a
    img = canvas
    rng = np.random.default_rng(1803)
    L = T.Layer(rng)
    # recommendation in yellow pencil around C
    cx = xs[2] + pw / 2
    L.wax_stroke(T.hand_circle(cx, y0 + ph / 2, pw * 0.53, ph * 0.54, rng, turns=1.08), 8.0, Y_PEN)
    L.light()
    img = K.pencil_composite(img, L)
    img = title(img, "NODES ON THE STREET", "ROUND 18  //  RAID GRID: 3 WAYS TO PUT NODES + LINKS ON THE ROAD PLANE", x=40, y=8)
    for i, ap in enumerate("ABC"):
        head, lines = OPT_TXT[ap]

        def fn(p, head=head, lines=lines, ap=ap):
            p.text(14, 12, head, SL.ANTON, 26, CYAN if ap != "C" else GREEN)
            y = 52
            for ln in lines:
                col = (200, 196, 214)
                if ln.startswith("+"):
                    col = GREEN
                elif ln.startswith("-"):
                    col = (255, 120, 100)
                p.text(14, y, ln, SL.MONO, 14, col)
                y += 20
        sd = panel(420, 160, fn, seed=80 + i)
        img = put(img, sd, xs[i] + pw / 2, y0 + ph + 64, angle=[-1.2, 0.8, -0.6][i])
    img = put(img, K.word_sticker(["PICK C"], 46, [K.FILL_YELLOW], seed=91, border=14, curl=dict(corner="tr", amount=0.12)),
              xs[2] + pw - 70, y0 + 40, angle=8)
    return img


# ------------------------------------------------------------------ heat strip
HEAT_TXT = {1: ("HEAT 25  WATCHED", ["1 chopper, 1 searchlight", "a few drones", "billboards still sell"]),
            2: ("HEAT 50  HUNTED", ["3 choppers sweep nodes", "drone swarm, corner strobes", "corp ads take the holos", "violet creep from entries"]),
            3: ("HEAT 75  MANHUNT", ["gunship over CORE", "every node in a spotlight", "26 drones, sky beams", "creep floods the streets"])}


def heat_strip():
    W, H = LY.W, LY.H
    canvas = np.zeros((H, W, 3), np.float32) + np.array([0.035, 0.03, 0.06], np.float32)
    crop = (510, 30, 1410, 1070)
    pw, ph = 600, int(600 * 1040 / 900)
    xs = [40 + i * 620 for i in range(3)]
    y0 = 150
    for i, hlev in enumerate((1, 2, 3)):
        base = FN.finish("setup_h%d" % hlev, "night", "C", SETUP_ST, heat=hlev, seed=1)
        im = Image.fromarray((np.clip(base, 0, 1) * 255).astype(np.uint8)).crop(crop).resize((pw, ph), Image.LANCZOS)
        canvas[y0:y0 + ph, xs[i]:xs[i] + pw] = np.asarray(im, np.float32) / 255
    img = canvas
    img = title(img, "HEAT ESCALATION", "SAME DISTRICT  //  HEAT BANDS 25 / 50 / 75  //  EVERYTHING ABOVE THE STREET, NOTHING ON THE GRID", x=40, y=8)
    for i, hlev in enumerate((1, 2, 3)):
        head, lines = HEAT_TXT[hlev]

        def fn(p, head=head, lines=lines, hlev=hlev):
            p.rect(0, 0, 9, 129, [AMBER, (255, 120, 60), HARM][hlev - 1])
            p.text(20, 10, head, SL.ANTON, 26, PAPER)
            y = 48
            for ln in lines:
                p.text(20, y, ln, SL.MONO, 14, (200, 196, 214))
                y += 19
        img = put(img, panel(330, 130, fn, seed=100 + i), xs[i] + 190, y0 + ph + 60, angle=[-1.5, 1, -0.8][i])
    return img


def save(img, name):
    Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, name), optimize=True)
    print("saved", name, flush=True)


def contact():
    names = ["raid_options.png", "raid_setup_night.png", "raid_setup_day.png", "raid_wave_night.png", "raid_heat_levels.png"]
    tw, th = 640, 360
    sheet = Image.new("RGB", (tw * 3 + 40, th * 2 + 30 + 60), (10, 9, 16))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "ROUND 18  RAID GRID ON THE STREET PLANE", font=ImageFont.truetype(SL.ANTON, 30), fill=(255, 222, 30))
    for i, n in enumerate(names):
        im = Image.open(os.path.join(OUT, n)).convert("RGB").resize((tw, th), Image.LANCZOS)
        x, y = 10 + (i % 3) * (tw + 10), 60 + (i // 3) * (th + 10)
        sheet.paste(im, (x, y))
        d.text((x + 8, y + th - 26), n, font=ImageFont.truetype(SL.MONO, 16), fill=(92, 225, 255))
    sheet.save(os.path.join(OUT, "contact_sheet.jpg"), quality=88)
    print("saved contact_sheet.jpg")


if __name__ == "__main__":
    which = sys.argv[1:] or ["options", "setup_night", "setup_day", "wave", "heat", "contact"]
    if "options" in which:
        save(options_sheet(), "raid_options.png")
    if "setup_night" in which:
        save(setup_frame("night"), "raid_setup_night.png")
    if "setup_day" in which:
        save(setup_frame("day"), "raid_setup_day.png")
    if "wave" in which:
        save(wave_frame(), "raid_wave_night.png")
    if "heat" in which:
        save(heat_strip(), "raid_heat_levels.png")
    if "contact" in which:
        contact()
