"""Build the TILT-SHIFT DIORAMA concept stills end to end.

python build.py [--preview] [--skip-render] [still ...]    stills: combat city heat modem strip sheet
Renders go to a work dir (outside the repo); finals to ../stills/.
"""
import json
import os
import random
import subprocess
import sys
import math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageEnhance  # noqa: E402
import post_lib as PL  # noqa: E402
import voice as V  # noqa: E402

BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
WORK = os.environ.get("TSD_WORK", os.path.join(os.environ.get("TEMP", HERE), "b_tsd_work"))
STILLS = os.path.abspath(os.path.join(HERE, "..", "stills"))
os.makedirs(WORK, exist_ok=True)
os.makedirs(STILLS, exist_ok=True)
ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
PREVIEW = "--preview" in sys.argv
SKIP = "--skip-render" in sys.argv
W, H = PL.W, PL.H


def blender(script, args, log):
    cmd = [BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, script), "--"] + args
    with open(os.path.join(WORK, log), "w") as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=900)
    txt = open(os.path.join(WORK, log)).read()
    if "Traceback" in txt or r.returncode != 0:
        print(txt[-3000:])
        raise SystemExit(f"blender failed: {script}")


def gp_render(name, items):
    spec = {"out": os.path.join(WORK, f"{name}.png"), "res": [W, H], "items": items}
    p = os.path.join(WORK, f"{name}.json")
    with open(p, "w") as f:
        json.dump(spec, f)
    return p


def gp_run(specs, log):
    blender("gp_overlay.py", specs, log)


def over(base, name):
    return PL.alpha_over(base, Image.open(os.path.join(WORK, f"{name}.png")).convert("RGBA"))


def finish(img, name, seed, grain_amt=7):
    img = PL.grain(img, seed, grain_amt)
    out = os.path.join(STILLS, name)
    img.save(out, optimize=True)
    print("wrote", out)
    return img


def washed_digital(base, box, word, spill=None, f=None):
    """A system word on a glass button, washed out, for the marker to be scrawled over (feedback 9)."""
    base = PL.glass_panel(base, box, spill=spill, spill_gain=0.7, alpha=190, radius=3)
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = f or PL.font("mono", int((y1 - y0) * 0.5))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.text((cx, cy), word, font=f, fill=PL.hx("#cff6ff", 150), anchor="mm")
    # scan-dropout: the digital word is losing to the ink
    for yy in range(int(y0), int(y1), 4):
        d.line([(x0 + 2, yy), (x1 - 2, yy)], fill=(5, 13, 28, 90))
    return PL.alpha_over(base, layer)


# ============================================================================ 01 combat

HAND = [
    {"name": "JOLT", "cost": 1, "text": "Spin a wheel\n3 ticks.", "foot": "[1]", "col": V.PAPER, "sweep": 20},
    {"name": "FINE TUNE", "cost": 1, "text": "Two +-1 nudges\non one ring.", "foot": "[2]", "col": V.NOTE_PINK, "sweep": -40},
    {"name": "BRUTE SPIN", "cost": 2, "text": "Spin a wheel\n6 ticks.", "foot": "[3]", "col": V.NOTE_YELLOW, "sweep": 80},
    {"name": "ENCRYPT", "cost": 1, "text": "A chosen slice\nabsorbs a status.", "foot": "[4]", "col": "#1b1d21", "dark": True, "sweep": 0},
    {"name": "TAP TAP", "cost": 2, "text": "Three +-1 nudges\non one ring.", "foot": "[5]", "col": V.STICKER_PINK, "sweep": 40},
]


def still_combat():
    if not SKIP:
        blender("scene_combat.py", [WORK] + (["preview"] if PREVIEW else []), "combat.log")
    beauty = PL.load_rgb(os.path.join(WORK, "combat_beauty.png"))
    depth = PL.load_depth(os.path.join(WORK, "combat_depth.png"))
    near = depth.point(PL.lut(lambda v: 255 if v < 40 else 0)).filter(ImageFilter.GaussianBlur(0.8))
    # city recedes (feedback 3): heavy defocus, desaturate, dim, cool
    city, _ = PL.tilt_shift(beauty, depth, focus=0, dgain=0.0, vramp=None, radii=(0, 6, 10, 16), spread=2)
    # aerial perspective instead of darkness: soft, lifted, cool, low-saturation
    city = beauty.filter(ImageFilter.GaussianBlur(4.5))
    city = PL.grade(city, sat=0.4, bright=1.0, contrast=0.8, tint="#8aa0d0", tint_amt=0.25)
    city = Image.blend(city, Image.new("RGB", city.size, (22, 30, 52)), 0.28)
    # spinner drop shadow onto the far city
    sh = near.transform(near.size, Image.AFFINE, (1, 0, -26, 0, 1, -34)).filter(ImageFilter.GaussianBlur(26))
    city = ImageChops.multiply(city, Image.merge("RGB", [sh.point(PL.lut(lambda v: 255 - v * 0.75))] * 3))
    img = Image.composite(PL.grade(beauty, sat=1.3, contrast=1.05), city, near)
    img, bright = PL.bloom(img, thresh=165)
    spill = PL.spill_map(bright, 70, 2.2)

    # ---- glass UI
    img = PL.glass_panel(img, (0, 0, W, 54), spill=spill, spill_gain=0.3, alpha=225, radius=0)
    x = 24
    for lab, val in [("HEAT", "12/100"), ("HP", "60/60"), ("CYCLES", "120"), ("CARDS", "10"), ("RANK", "2"), ("RAM", "3/12")]:
        PL.text(img, (x, 9), lab, PL.font("mono", 13), PL.hx("#7a889c"))
        PL.text(img, (x, 23), val, PL.font("mono", 22), PL.hx("#f2f6ff"))
        x += 150
    PL.text(img, (W - 24, 18), "VIEW LOADOUT   SETTINGS [ESC]", PL.font("mono", 17), PL.hx("#cff6ff"), anchor="ra")
    PL.text(img, (24, 66), "TURN 1  //  FREE NUDGE 1  //  Q/E NUDGE YOUR WHEEL  //  W NUDGE THE TARGET",
            PL.font("mono", 16), PL.hx("#afc0d6"))
    img = PL.glass_panel(img, (330, 96, 790, 168), spill=spill, spill_gain=3.2, alpha=205)
    PL.text(img, (348, 106), "DEFEND  .  HALF POWER", PL.font("mono", 20), PL.hx("#5ce1ff"))
    PL.text(img, (348, 136), "+3 BLOCK    CRIT 20%   ATTACK 60%   DEFEND 20%", PL.font("mono", 15), PL.hx("#afc0d6"))
    img = PL.glass_panel(img, (1110, 96, 1570, 168), spill=spill, spill_gain=3.2, alpha=205)
    PL.text(img, (1128, 106), "AFFLICT  .  GOOD AIM", PL.font("mono", 20), PL.hx("#c85aff"))
    PL.text(img, (1128, 136), "PUTS CORRUPTED ON YOU   -12 HP FORECAST", PL.font("mono", 15), PL.hx("#ff4433"))
    for cx, hp in ((560, "60/60"), (1340, "40/40  -12")):
        PL.text(img, (cx, 752), hp, PL.font("anton", 34), PL.hx("#f2f6ff"), anchor="ma")
    img = PL.glass_panel(img, (1480, 800, 1690, 842), spill=spill, spill_gain=0.8, alpha=200)
    PL.text(img, (1496, 810), "RESPIN  4 RAM  [R]", PL.font("mono", 17), PL.hx("#cff6ff"))
    img = PL.glass_panel(img, (1700, 800, 1880, 842), spill=spill, spill_gain=0.8, alpha=200)
    PL.text(img, (1716, 810), "UNDO  [Z]", PL.font("mono", 17), PL.hx("#cff6ff"))
    img = washed_digital(img, (1440, 862, 1880, 1000), "EXECUTE", spill=spill)
    PL.text(img, (1880, 1012), "[SPACE]", PL.font("mono", 15), PL.hx("#7a889c"), anchor="ra")

    # ---- the Cell's voice: sticker hand (feedback 8), GP paper pass
    paper = []
    cards = []
    CW, CH = 168, 228
    xs = [150, 345, 540, 735, 965]
    rots = [-4, 3, -2, 5, -10]
    for k, c in enumerate(HAND):
        lift = 1.0 if k == 4 else 0.0
        sc = 1.14 if k == 4 else 1.0
        cx, cy = xs[k], 928 - (26 if k == 4 else 0)
        w, h = int(CW * sc), int(CH * sc)
        paper += V.sticker(cx, cy, w, h, c["col"], deg=rots[k], border=7, radius=10,
                           peel=26 if k == 2 else 0, lift=lift)
        cards.append((c, cx, cy, w, h, rots[k]))
    paper.append(V.tape(345, 820, 96, 30, 8, 5))
    paper.append(V.tape(735, 818, 90, 28, -6, 6))
    # ---- ink pass: SEND IT scrawled over EXECUTE (feedback 9), drips forming (6), slap marks (8)
    ink = []
    m, full = V.marker_fit("SEND IT", 1450, 1870, 972, 11, 84, rot=-5, width_ratio=0.2)
    ink.append(m)
    ink += V.drips(full, 12, 4, m["width"], [30, 52, 20, 40])
    for a in (-150, -120, -60, -30, 200):  # slap impact ticks around the incoming card
        r0, r1 = 150, 182
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        ink.append({"type": "line", "pts": [(965 + ca * r0 * 0.8, 902 + sa * r0), (965 + ca * r1 * 0.8, 902 + sa * r1)],
                    "color": "#f2eee4", "width": 5})
    gp_run([gp_render("combat_paper", paper), gp_render("combat_ink", ink)], "combat_gp.log")
    img = PL.vignette(img, 0.42)  # before the voice layer: ink and paper stay flat
    img = over(img, "combat_paper")
    for c, cx, cy, w, h, deg in cards:
        img = PL.paste_rotated(img, PL.card_face(c, w, h), cx, cy, deg)
    img = over(img, "combat_ink")
    finish(img, "01_combat.png", 1)


# ============================================================================ 02/03 city

def city_post(mode):
    beauty = PL.load_rgb(os.path.join(WORK, f"{mode}_beauty.png"))
    depth = PL.load_depth(os.path.join(WORK, f"{mode}_depth.png"))
    lay = json.load(open(os.path.join(WORK, f"{mode}_layout.json")))
    sx = W / lay["res"][0]
    vr = PL.vertical_ramp(520, 210, 2.6)
    img, bmap = PL.tilt_shift(beauty, depth, focus=120, dgain=2.2, vramp=vr)
    img, bright = PL.bloom(img, thresh=150)
    img = PL.grade(img, sat=1.08, bright=1.02, contrast=1.06)
    spill = PL.spill_map(bright, 70, 1.8)
    return img, spill, lay, sx


def top_bar(img, spill, tags, title):
    img = PL.glass_panel(img, (0, 0, W, 54), spill=spill, spill_gain=0.25, alpha=225, radius=0)
    PL.text(img, (24, 8), title[0], PL.font("mono", 14), PL.hx("#ff3da8"))
    PL.text(img, (24, 25), title[1], PL.font("mono", 20), PL.hx("#f2f6ff"))
    x = 260
    for lab, val, col in tags:
        PL.text(img, (x, 9), lab, PL.font("mono", 13), PL.hx("#7a889c"))
        PL.text(img, (x, 23), val, PL.font("mono", 22), PL.hx(col))
        x += 140
    PL.text(img, (W - 24, 18), "VIEW LOADOUT", PL.font("mono", 17), PL.hx("#cff6ff"), anchor="ra")
    return img


def node_labels(img, lay, sx, spill, heat=False):
    for name, kind, x, y in lay["nodes"]:
        x, y = x * sx, y * sx
        f = PL.font("mono", 15)
        if name == "CORE":
            name = "CORE // THE CELL"
        tw = int(f.getlength(name)) + 16
        bx0, by0 = int(x + 30), int(y - 38)
        img = PL.glass_panel(img, (bx0, by0, bx0 + tw, by0 + 24), spill=spill, spill_gain=0.5, alpha=205, radius=2,
                             blur=4, scan=False, edge={"cell": "#d4ff00", "boss": "#ff4433", "corp": "#3dff8b"}.get(kind, "#5ce1ff"))
        PL.text(img, (bx0 + 8, by0 + 4), name, f, PL.hx("#f2f6ff"))
        d = ImageDraw.Draw(img)
        d.line([(x + 8, y - 8), (bx0, by0 + 12)], fill=PL.hx("#cff6ff", 160), width=1)
    return img


def site_panel(img, spill, heat=False):
    x0, y0, x1, y1 = 1500, 84, 1890, 560
    img = PL.glass_panel(img, (x0, y0, x1, y1), spill=spill, spill_gain=0.5, alpha=215,
                         title="KILL-SWITCH AUTHORITY        T2 // CORP")
    rows = [("CORP", "SOLACE BIOSYSTEMS"), ("DEFENDERS", "BREAKER II, SENTRY"), ("REWARD", "22 SCHEMATICS"),
            ("HEAT ON WIN", "+8"), ("ROUTE", "3 JUMPS FROM CORE")]
    if heat:
        rows[3] = ("HEAT ON WIN", "+8   (HUNTED: x1.5)")
    y = y0 + 52
    for k, v in rows:
        PL.text(img, (x0 + 16, y), k, PL.font("mono", 15), PL.hx("#7a889c"))
        PL.text(img, (x0 + 170, y), v, PL.font("mono", 16), PL.hx("#ff4433" if heat and k == "HEAT ON WIN" else "#f2f6ff"))
        y += 30
    PL.text(img, (x0 + 16, y + 10), "RUNS OPEN NOW", PL.font("mono", 15), PL.hx("#ff3da8"))
    for k, r in enumerate(["T1  Continuum Billing Farm", "T1  Scrub Records", "T2  Kill-Switch Authority", "T3  Renewal Engine (BOSS)"]):
        PL.text(img, (x0 + 16, y + 40 + k * 26), r, PL.font("mono", 16), PL.hx("#cff6ff" if k != 2 else "#d4ff00"))
    return img


def still_city():
    if not SKIP:
        blender("scene_city.py", [WORK, "city"] + (["preview"] if PREVIEW else []), "city.log")
    img, spill, lay, sx = city_post("city")
    img.save(os.path.join(WORK, "city_base.png"))
    img = top_bar(img, spill, [("HEAT", "18/100", "#afc0d6"), ("SCHEMATICS", "20", "#f2f6ff"), ("HOME", "50/50", "#7be07b"),
                               ("EXPLOITS", "0/3", "#f2f6ff"), ("RAIDS", "0", "#f2f6ff"), ("CREW", "2", "#f2f6ff")],
                  ("02", "CITY GRID // NIGHT"))
    img = node_labels(img, lay, sx, spill)
    img = site_panel(img, spill)
    img = washed_digital(img, (1520, 452, 1870, 540), "CONNECT", spill=spill)
    # legend
    img = PL.glass_panel(img, (24, 900, 420, 1056), spill=spill, spill_gain=0.4, alpha=210, title="MAP LEGEND")
    leg = [("#d4ff00", "your network / claimed"), ("#5ce1ff", "open net link"), ("#3dff8b", "corp site"), ("#ff4433", "boss / threat route")]
    for k, (c, t) in enumerate(leg):
        d = ImageDraw.Draw(img)
        yy = 948 + k * 26
        d.line([(40, yy + 9), (80, yy + 9)], fill=PL.hx(c), width=4)
        PL.text(img, (94, yy), t, PL.font("mono", 16), PL.hx("#cff6ff"))
    ink = []
    m, full = V.marker_fit("JACK IN", 1530, 1860, 528, 21, 70, rot=-4)
    ink.append(m)
    ink += V.drips(full, 22, 3, m["width"], [26, 40, 18])
    # spray ring around the claimed node (the Cell's mark on its turf)
    cn = [n for n in lay["nodes"] if n[0] == "Scrub Records"][0]
    cx, cy = cn[2] * sx, cn[3] * sx
    rng = random.Random(4)
    ring = [(cx + math.cos(a / 40 * 2 * math.pi) * (38 + rng.uniform(-3, 3)), cy + math.sin(a / 40 * 2 * math.pi) * (22 + rng.uniform(-2, 2)))
            for a in range(0, 38)]
    ink.append({"type": "line", "pts": ring, "color": "#d4ff00", "width": 5, "alpha": 0.9})
    gp_run([gp_render("city_ink", ink)], "city_gp.log")
    img = PL.vignette(img, 0.42)
    img = over(img, "city_ink")
    finish(img, "02_city_night.png", 2)


def heat_glitch(img, seed, amount=1.0, bands=True):
    """Screen-wide Heat glitch (feedback 11): RGB split, slice displacement, flicker bands. Options can disable it."""
    rng = random.Random(seed)
    r, g, b = img.split()
    r = ImageChops.offset(r, max(1, int(4 * amount)), 0)
    b = ImageChops.offset(b, -max(1, int(4 * amount)), 0)
    out = Image.merge("RGB", (r, g, b))
    for _ in range(max(2, int(10 * amount))):
        y = rng.randint(60, H - 40)
        h = rng.randint(3, 22)
        dx = int(rng.randint(-40, 40) * min(1.0, amount * 1.4))
        band = out.crop((0, y, W, y + h))
        out.paste(ImageChops.offset(band, dx, 0), (0, y))
    d = ImageDraw.Draw(out, "RGBA")
    for _ in range(3):
        y = rng.randint(80, H - 80)
        d.rectangle((0, y, W, y + rng.randint(1, 3)), fill=(255, 80, 60, 70))
    if not bands:
        return out
    # a flicker band: a brighter, slightly offset horizontal strip
    y = int(H * 0.62)
    band = out.crop((0, y, W, y + 70))
    band = ImageEnhance.Brightness(band).enhance(1.25)
    out.paste(ImageChops.offset(band, 8, 0), (0, y))
    return out


def still_heat():
    if not SKIP:
        blender("scene_city.py", [WORK, "heat"] + (["preview"] if PREVIEW else []), "heat.log")
    img, spill, lay, sx = city_post("heat")
    img = PL.grade(img, sat=0.85, bright=0.95, contrast=1.1, tint="#ff7a66", tint_amt=0.16)
    img = heat_glitch(img, 33, 0.35)
    # police wash: red from the left, blue from the right, low and soft
    wash = Image.new("RGB", (W, H), 0)
    wd = ImageDraw.Draw(wash)
    for k in range(60):
        a = int(90 * (1 - k / 60) ** 2)
        wd.line([(k * 6, 0), (k * 6, H)], fill=(a, int(a * 0.1), int(a * 0.12)), width=6)
        wd.line([(W - k * 6, 0), (W - k * 6, H)], fill=(int(a * 0.1), int(a * 0.3), a), width=6)
    img = ImageChops.screen(img, wash)  # the city layer takes the full glitch; UI gets a light pass below
    img = top_bar(img, spill, [("HEAT", "82/100", "#ff4433"), ("SCHEMATICS", "20", "#f2f6ff"), ("HOME", "31/50", "#ffb000"),
                               ("EXPLOITS", "1/3", "#f2f6ff"), ("RAIDS", "2", "#ff4433"), ("CREW", "2", "#f2f6ff")],
                  ("02", "CITY GRID // HUNTED"))
    img = node_labels(img, lay, sx, spill, heat=True)
    img = site_panel(img, spill, heat=True)
    img = washed_digital(img, (1520, 452, 1870, 540), "PROCEED", spill=spill)
    # Heat poster (glass meter)
    img = PL.glass_panel(img, (24, 84, 380, 214), spill=spill, spill_gain=0.4, alpha=215, title="HEAT // HUNTED",
                         title_col="#ff4433", edge="#ff4433")
    d = ImageDraw.Draw(img)
    for k in range(20):
        c = "#ff4433" if k < 16 else "#34383e"
        d.rectangle((40 + k * 16, 136, 52 + k * 16, 160), fill=PL.hx(c))
    PL.text(img, (40, 172), "82 / 100   RAID LIKELY   SWEEPS ACTIVE", PL.font("mono", 16), PL.hx("#ffb000"))
    img = PL.glass_panel(img, (24, 1010, 460, 1052), alpha=200, radius=3, spill=spill, spill_gain=0.3)
    PL.text(img, (40, 1020), "HEAT GLITCH FX: ON   OPTIONS > VIDEO", PL.font("mono", 17), PL.hx("#afc0d6"))
    img = heat_glitch(img, 34, 0.25, bands=False)
    ink = []
    m, full = V.marker_fit("LAY LOW", 1530, 1860, 528, 31, 70, rot=-3)
    ink.append(m)
    ink += V.drips(full, 32, 4, m["width"], [40, 62, 30, 52])
    gp_run([gp_render("heat_ink", ink)], "heat_gp.log")
    img = PL.vignette(img, 0.55)
    img = over(img, "heat_ink")
    finish(img, "03_heat.png", 3)


# ============================================================================ 04 modem

SHOP_CARDS = [
    {"name": "MIRROR FLIP", "cost": 3, "text": "Flip a wheel.\nBlocked by resist.", "foot": "", "col": V.PAPER, "sweep": 60},
    {"name": "ENCRYPT", "cost": 1, "text": "A chosen slice\nabsorbs a status.", "foot": "", "col": "#1b1d21", "dark": True},
    {"name": "TAP TAP", "cost": 2, "text": "Three +-1 nudges\non one ring.", "foot": "", "col": V.STICKER_PINK, "sweep": -30},
]


def chip_icon(img, cx, cy, s, col):
    d = ImageDraw.Draw(img)
    d.rectangle((cx - s, cy - s, cx + s, cy + s), outline=PL.hx(col), width=2)
    d.rectangle((cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5), fill=PL.hx(col, 90), outline=PL.hx(col), width=1)
    for k in range(5):
        o = -s + (k + 0.5) * (2 * s / 5)
        for a, b in (((cx + o, cy - s - 8), (cx + o, cy - s)), ((cx + o, cy + s), (cx + o, cy + s + 8)),
                     ((cx - s - 8, cy + o), (cx - s, cy + o)), ((cx + s, cy + o), (cx + s + 8, cy + o))):
            d.line([a, b], fill=PL.hx(col), width=2)


def buy_button(img, box, label, spill):
    img = PL.glass_panel(img, box, spill=spill, spill_gain=0.5, alpha=170, radius=3, edge="#d4ff00", blur=4, scan=False)
    PL.text(img, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), label, PL.font("mono", 17), PL.hx("#d4ff00"), anchor="mm")
    return img


def slice_icon(img, cx, cy, r, col, val, glyph):
    d = ImageDraw.Draw(img, "RGBA")
    pts = []
    for k in range(13):
        a = math.radians(-120 + 60 * k / 12)
        pts.append((cx + math.cos(a) * r, cy + r * 0.9 + math.sin(a) * r))
    for k in range(13):
        a = math.radians(-60 - 60 * k / 12)
        pts.append((cx + math.cos(a) * r * 0.45, cy + r * 0.9 + math.sin(a) * r * 0.45))
    d.polygon(pts, fill=PL.hx(col, 150), outline=PL.hx(col))
    d.text((cx, cy + r * 0.22), val, font=PL.font("anton", 34), fill=PL.hx("#f2f6ff"), anchor="mm")
    d.text((cx, cy - r * 0.3), glyph, font=PL.font("mono", 18), fill=PL.hx(col), anchor="mm")


def still_modem():
    if not SKIP:
        blender("scene_modem.py", [WORK] + (["preview"] if PREVIEW else []), "modem.log")
    beauty = PL.load_rgb(os.path.join(WORK, "modem_beauty.png"))
    depth = PL.load_depth(os.path.join(WORK, "modem_depth.png"))
    img, _ = PL.tilt_shift(beauty, depth, focus=72, dgain=3.2, vramp=PL.vertical_ramp(420, 260, 1.6))
    img, bright = PL.bloom(img, thresh=150)
    img = PL.grade(img, sat=1.05, contrast=1.05)
    spill = PL.spill_map(bright, 80, 2.0)
    img = top_bar(img, spill, [("HEAT", "18/100", "#afc0d6"), ("SCHEMATICS", "20", "#f2f6ff"), ("HP", "60/60", "#7be07b"),
                               ("CYCLES", "120", "#f2f6ff"), ("CARDS", "10", "#f2f6ff"), ("RANK", "2", "#f2f6ff")],
                  ("05", "MODEM CYBER SHOP"))
    # --- MICROCHIPS
    img = PL.glass_panel(img, (640, 84, 1180, 420), spill=spill, spill_gain=1.0, title="MICROCHIPS")
    for k, (nm, desc, price) in enumerate([("BARBED WIRE", "DEF slice also deals\n2 damage to the\npointer target.", "BUY 141"),
                                           ("SHUNT", "Resolves the neighbour\non the side you landed.\nx1.5 on Perfect.", "BUY 129")]):
        x0 = 660 + k * 262
        img = PL.glass_panel(img, (x0, 136, x0 + 246, 404), spill=spill, spill_gain=0.6, alpha=150, blur=3, scan=False)
        chip_icon(img, x0 + 123, 186, 26, "#5ce1ff")
        PL.text(img, (x0 + 123, 232), nm, PL.font("mono", 18), PL.hx("#f2f6ff"), anchor="ma")
        PL.text(img, (x0 + 123, 258), desc, PL.font("mono", 14), PL.hx("#afc0d6"), anchor="ma")
        img = buy_button(img, (x0 + 58, 350, x0 + 188, 388), price, spill)
    # --- CARDS (paper stickers on the glass)
    img = PL.glass_panel(img, (1200, 84, 1890, 420), spill=spill, spill_gain=1.0, title="CARDS")
    # --- SLICES
    img = PL.glass_panel(img, (640, 440, 1180, 760), spill=spill, spill_gain=1.0, title="SLICES", title_col="#ffb000",
                         edge="#ffb000")
    for k, (col, val, gl, nm) in enumerate([("#5ce1ff", "5", "[#]", "SHD 5"), ("#ff3da8", "10", "/!\\", "ATK 10"),
                                            ("#7be07b", "2", ">>", "EVD 2")]):
        cx = 740 + k * 170
        slice_icon(img, cx, 540, 92, col, val, gl)
        PL.text(img, (cx, 640), nm, PL.font("mono", 16), PL.hx("#cff6ff"), anchor="ma")
        img = buy_button(img, (cx - 62, 680, cx + 62, 716), "BUY 100", spill)
    # --- REMOVE A CARD
    img = PL.glass_panel(img, (1200, 440, 1890, 760), spill=spill, spill_gain=1.0, title="REMOVE A CARD", title_col="#d4ff00",
                         edge="#d4ff00")
    d = ImageDraw.Draw(img)
    d.rectangle((1250, 520, 1400, 560), outline=PL.hx("#d4ff00"), width=2)
    for k in range(9):
        d.line([(1262 + k * 16, 566), (1262 + k * 16, 600 + (k % 3) * 8)], fill=PL.hx("#cff6ff"), width=2)
    PL.text(img, (1325, 620), "SHRED A CARD", PL.font("mono", 16), PL.hx("#cff6ff"), anchor="ma")
    img = buy_button(img, (1262, 680, 1392, 716), "SHRED 50", spill)
    PL.text(img, (1450, 520), "CYCLES", PL.font("mono", 14), PL.hx("#7a889c"))
    PL.text(img, (1450, 540), "120", PL.font("anton", 44), PL.hx("#f2f6ff"))
    PL.text(img, (1450, 610), "Shredding is permanent.\nThe card leaves your deck\nfor this campaign.", PL.font("mono", 15),
            PL.hx("#afc0d6"))
    img = washed_digital(img, (1480, 790, 1890, 900), "EXIT")
    img = PL.vignette(img, 0.4)
    # --- voice: card stickers, a Cell sticker on the chips panel, marker LEAVE over EXIT, THIS ONE circle
    paper, cards = [], []
    for k, (c, cx, deg) in enumerate(zip(SHOP_CARDS, (1330, 1545, 1760), (-3, 2, 4))):
        paper += V.sticker(cx, 238, 150, 200, c["col"], deg=deg, border=6, radius=9, peel=22 if k == 1 else 0)
        cards.append((c, cx, 238, 150, 200, deg))
    paper.append(V.tape(1330, 138, 80, 26, 6, 41))
    hexp = [(1140 + 34 * math.cos(math.radians(60 * k + 30)), 118 + 34 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    paper.append({"type": "poly", "pts": [(x + 5, y + 7) for x, y in hexp], "fill": "#000000", "alpha": 0.4})
    paper.append({"type": "poly", "pts": hexp, "fill": "#fbfaf6"})
    paper.append({"type": "poly", "pts": [(1140 + 27 * math.cos(math.radians(60 * k + 30)),
                                           118 + 27 * math.sin(math.radians(60 * k + 30))) for k in range(6)], "fill": V.PINK})
    ink = []
    m, full = V.marker_fit("LEAVE", 1500, 1870, 880, 51, 86, rot=-4)
    ink.append(m)
    ink += V.drips(full, 52, 3, m["width"], [34, 56, 24])
    rng = random.Random(54)
    ring = [(1545 + 100 * math.cos(a / 30 * 2 * math.pi) + rng.uniform(-3, 3),
             236 + 114 * math.sin(a / 30 * 2 * math.pi) + rng.uniform(-3, 3)) for a in range(-2, 29)]
    ink.append({"type": "line", "pts": ring, "color": V.PINK, "width": 6})
    gp_run([gp_render("modem_paper", paper), gp_render("modem_ink", ink)], "modem_gp.log")
    img = over(img, "modem_paper")
    PL.text(img, (1140, 118), "C", PL.font("anton", 34), PL.hx("#fbfaf6"), anchor="mm")
    for c, cx, cy, w, h, deg in cards:
        img = PL.paste_rotated(img, PL.card_face(c, w, h), cx, cy, deg)
    for cx, price in ((1330, "BUY 69"), (1545, "BUY 61"), (1760, "BUY 75")):
        img = buy_button(img, (cx - 58, 360, cx + 58, 396), price, spill)
    img = over(img, "modem_ink")
    finish(img, "04_hq_modem.png", 4)


# ============================================================================ 05 marker strip

def smear_up(im, dist, steps=10):
    acc = None
    for k in range(steps):
        sh = ImageChops.offset(im, 0, -int(dist * k / steps))
        acc = sh if acc is None else Image.blend(acc, sh, 1 / (k + 1))
    return acc


def washed_digital_local(panel, box, word):
    x0, y0, x1, y1 = box
    panel = PL.glass_panel(panel, box, alpha=190, radius=3)
    layer = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(((x0 + x1) / 2, (y0 + y1) / 2), word, font=PL.font("mono", int((y1 - y0) * 0.5)), fill=PL.hx("#cff6ff", 150),
           anchor="mm")
    for yy in range(int(y0), int(y1), 4):
        d.line([(x0 + 2, yy), (x1 - 2, yy)], fill=(5, 13, 28, 90))
    b = panel.convert("RGBA")
    b.alpha_composite(layer)
    return b.convert("RGB")


def still_strip():
    base_p = os.path.join(WORK, "city_base.png")
    if not os.path.exists(base_p):
        still_city()
    city = Image.open(base_p).convert("RGB")
    city = PL.grade(city, sat=0.55, bright=0.55)
    PW, G = 620, 15
    canvas = Image.new("RGB", (W, H), (8, 10, 16))
    ink = []
    captions = [("1", "WRITE-ON", "stroke by stroke, 0.0 - 0.45 s"),
                ("2", "DRIPS FORM, THEN HOLD", "idle: bulbs swell, then wait for input"),
                ("3", "ON PRESS: PAGE LEAVES", "the ink keeps running down the screen")]
    for k in range(3):
        x0 = G + k * (PW + G)
        crop = city.crop((300 + k * 260, 0, 300 + k * 260 + PW, H))
        panel = crop.copy()
        btn = (60, 520, PW - 60, 660)
        panel = washed_digital_local(panel, btn, "EXECUTE")
        if k == 2:
            panel = smear_up(panel, 220)
            panel = ImageEnhance.Brightness(panel).enhance(0.75)
            panel = PL.glass_panel(panel, (0, 860, PW, H), alpha=235, title="LOOT // RESOLVING", radius=0)
        canvas.paste(panel, (x0, 0))
        canvas = PL.glass_panel(canvas, (x0 + 20, 24, x0 + PW - 20, 104), alpha=220, radius=3)
        PL.text(canvas, (x0 + 38, 34), captions[k][0] + "   " + captions[k][1], PL.font("mono", 24), PL.hx("#f2f6ff"))
        PL.text(canvas, (x0 + 38, 70), captions[k][2], PL.font("mono", 16), PL.hx("#afc0d6"))
        bx0, bx1 = x0 + 90, x0 + PW - 90
        if k == 0:
            m, full = V.marker_fit("SEND IT", bx0, bx1, 632, 11, 90, rot=-5, frac=0.62)
            ink.append(m)
            last = m["strokes"][-1][-1]
            ink += V.pen_nib(last[0], last[1])
        elif k == 1:
            m, full = V.marker_fit("SEND IT", bx0, bx1, 632, 11, 90, rot=-5)
            ink.append(m)
            ink += V.drips(full, 12, 5, m["width"], [40, 70, 28, 55, 36])
        else:
            m, full = V.marker_fit("SEND IT", bx0, bx1, 632 - 190, 11, 90, rot=-5)
            m["alpha"] = 0.55
            ink.append(m)
            src = V.drips(full, 12, 5, m["width"], [40, 70, 28, 55, 36])
            for dd in src:  # the drips detach and keep running down, over the next page
                dd["y"] += 190
                dd["len"] = H - dd["y"] + 60 + random.Random(int(dd["x"])).uniform(-120, 0)
                dd["streak"] = True
            ink += src
    gp_run([gp_render("strip_ink", ink)], "strip_gp.log")
    canvas = over(canvas, "strip_ink")
    finish(canvas, "05_marker_strip.png", 5)


# ============================================================================ contact sheet

def contact_sheet():
    names = [("01_combat.png", "01  COMBAT: machined spinners over a receding city, binary shards, sticker hand, SEND IT over EXECUTE"),
             ("02_city_night.png", "02  CITY GRID, NIGHT: ortho tilt-shift, highways on pylons, holo billboards, map on one plane"),
             ("03_heat.png", "03  HIGH HEAT: helicopters, searchlights, drones, threat routes, heat glitch"),
             ("04_hq_modem.png", "04  MODEM: the original vertical sign redrawn in neon tube, shop glass with zine voice"),
             ("05_marker_strip.png", "05  MARKER LIFE: write-on, drips hold, drips run as the page leaves")]
    TW, TH, LB, M = 900, 506, 40, 24
    sheet = Image.new("RGB", (M + 2 * (TW + M), 90 + 3 * (TH + LB + M)), (10, 12, 18))
    d = ImageDraw.Draw(sheet)
    d.text((M, 26), "B  //  TILT-SHIFT DIORAMA  --  REBEL_CELL concept round", font=PL.font("mono", 30), fill=PL.hx("#f2f6ff"))
    for k, (fn, lab) in enumerate(names):
        im = Image.open(os.path.join(STILLS, fn)).convert("RGB").resize((TW, TH), Image.LANCZOS)
        col, row = k % 2, k // 2
        x = M + col * (TW + M)
        y = 90 + row * (TH + LB + M)
        if k == 4:
            x = M + (TW + M) // 2
        sheet.paste(im, (x, y))
        d.text((x, y + TH + 8), lab, font=PL.font("mono", 15), fill=PL.hx("#afc0d6"))
    out = os.path.abspath(os.path.join(HERE, "..", "contact_sheet.jpg"))
    sheet.save(out, quality=86, optimize=True)
    print("wrote", out)


STEPS = {"combat": still_combat, "city": still_city, "heat": still_heat, "modem": still_modem, "strip": still_strip,
         "sheet": contact_sheet}

if __name__ == "__main__":
    for s in (ARGS or list(STEPS)):
        STEPS[s]()
