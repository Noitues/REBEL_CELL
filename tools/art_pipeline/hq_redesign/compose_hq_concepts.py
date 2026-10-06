"""HQ-DESIGN (M14): concept images for the HQ redesign directions (docs/art_review/HQ_REDESIGN/).

Designer verdict (2026-10-05): the HQ is reworked entirely; fewer panels, obvious at-a-glance verbs and
selections, the separate City Grid page folds into the live 3D city at the RAID band, Heat lives in the
run-wide Heat indicator, JACK IN uses the same netrun-start flow as every other netrun start.

This script only composes concept images. It draws nothing in the game and changes no game file.

Inputs
- `--shots`: real captures of main's 3D city at the RAID band, 1920x1080, from ONE windowed launch of
  the existing city lab (tools/city/city_lab.tscn, sample network on, RAID band), e.g.
      python tools/run_windowed.py --log <log> -- --resolution 1920x1080 res://tools/city/city_lab.tscn --
          --shots=<dir> --states=meridian:raid,... --size=1920x1080 --settle=120 --quality=2
  The Meridian frame (02_meridian_raid.png) is the base of every direction (same campaign moment, so
  the directions compare fairly).
- `--src`: an extract of tag art-concepts-r43 holding docs/concepts/round33_ui_chrome/scripts and
  docs/concepts/round17_slice_system/glyphs:
      git archive -o <tar> art-concepts-r43 docs/concepts/round33_ui_chrome/scripts \
          docs/concepts/round17_slice_system/glyphs   (then extract it to <src>)
  The v2 kit's own drawing code (ui31.py / sticker_lib31.py: vinyl stickers, CRT terminal panels and
  chips, decrypted holo, corp paper, rubber stamps, grease pencil) is imported and called unchanged;
  only its font paths are re-pointed at assets/fonts (as tools/art/bake_menus_r33.py does).
- Real game assets from main: assets/city/grid_markers (Site markers v4), assets/raid/sockets (the
  Cell's raid sockets), assets/raid/beacons (R3 class beacons), assets/portraits (v2 busts and prints),
  assets/hq_run/keycards (Exploit keycards), assets/fonts.

Usage (never from stdin on this machine):
    python tools/art_pipeline/hq_redesign/compose_hq_concepts.py --src <dir> --shots <dir> \
        [--out docs/art_review/HQ_REDESIGN] [--only A,B,C,heat,flow,B20,Bmarket,Braid,Ctabs]
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
W, H = 1920, 1080

U = None   # ui31 (the round 33 kit), bound in load_kit
SL = None  # sticker_lib31

# ---------------------------------------------------------------------------------------- the moment
# One campaign moment for every direction: Meridian Freight Systems, ICE 5, Heat 58 (FLAGGED), a raid
# pending (ROUTE AUDIT, Heat 50 crossed), three operatives alive and one flatlined. Names and prices are
# the game's own (content/corporations/meridian.tres, content/raids/raid_mer_heat_50.tres, GDD 11.4).
HEAT = 58
BANDS = [(0, 25, "COOL"), (25, 50, "NOTICED"), (50, 75, "FLAGGED"), (75, 100, "HUNTED")]
BAND_COL = {"COOL": (150, 168, 190), "NOTICED": (255, 176, 0), "FLAGGED": (255, 122, 26), "HUNTED": (255, 68, 51)}
MER = (255, 140, 26)
ORANGE_RING = (255, 150, 40)
CLASS_COL = {"breaker": (255, 61, 168), "ghost": (91, 224, 255), "rigger": (122, 224, 122), "botnet": (96, 114, 255)}
# Nodes of the city lab's sample network on the Meridian frame (screen px, measured on the capture).
N = {
    "drone": (1365, 645),     # T1 corporate, selectable (orange ring): the selected Site
    "returns": (1230, 765),   # the Cell's Safehouse (NOVA stationed)
    "core": (985, 818),       # CORE, the home server
    "customs": (685, 765),    # the Cell's Firewall Relay
    "lose": (550, 645),       # Heat objective, selectable
    "parcel": (685, 520),     # cleared (patrol)
    "vault": (960, 450),      # T2 Exploit Site (INTEL), selectable
    "keyauth": (1230, 520),   # T2 corporate, not yet
}
NAMES = {"drone": "DRONE CHARGING YARD", "returns": "RETURNS PROCESSING CENTRE", "core": "CORE",
         "customs": "CUSTOMS PRE-CLEARANCE", "lose": "LOSE THE TRACKING", "parcel": "PARCEL SORTING HALL",
         "vault": "SHIPPING MANIFEST VAULT", "keyauth": "CUSTOMS KEY AUTHORITY"}
# Corner points of the decal's links (screen px), for pencil that follows the real links.
ROUTE_A = [N["drone"], (1395, 665), N["returns"], (1150, 712), N["core"]]
ROUTE_B = [N["lose"], (540, 670), N["customs"], (795, 695), N["core"]]
JACK_LINK = [N["returns"], (1395, 665), N["drone"]]
CASTLE = (1592, 488)       # the Meridian HQ (The Master Manifest) on the frame
CREW = [
    {"name": "CELL-9", "cls": "breaker", "rank": 2, "hp": "60/60", "status": "READY", "var": 0},
    {"name": "NOVA", "cls": "ghost", "rank": 1, "hp": "50/50", "status": "ON RETURNS PROC.", "var": 1},
    {"name": "RIG-4", "cls": "rigger", "rank": 0, "hp": "55/55", "status": "READY", "var": 2},
    {"name": "HEX", "cls": "botnet", "rank": 1, "hp": "--", "status": "FLATLINED", "var": 3, "dead": True},
]


# ---------------------------------------------------------------------------------------- the kit
def load_kit(src: Path) -> None:
    """Import the round 33 kit from the tag extract and re-point its fonts at assets/fonts."""
    global U, SL
    scripts = src / "docs" / "concepts" / "round33_ui_chrome" / "scripts"
    sys.path.insert(0, str(scripts))
    import sticker_lib31 as sl  # noqa: E402
    import ui31 as u  # noqa: E402
    faces = {"Anton-Regular.ttf", "PermanentMarker-Regular.ttf", "IBMPlexSansCondensed-Medium.ttf",
             "IBMPlexSansCondensed-Regular.ttf", "ShareTechMono-Regular.ttf"}

    def fix(p):
        if isinstance(p, str):
            n = p.replace("\\", "/").rsplit("/", 1)[-1]
            if n in faces:
                return str(FONTS / n)
        return p

    for mod in (sl, u):
        for k in ("ANTON", "MARKER", "PLEX", "PLEX_M", "MONO"):
            if hasattr(mod, k):
                setattr(mod, k, fix(getattr(mod, k)))
    for fn in (sl.lettering, sl.Pen.text):
        if fn.__defaults__:
            fn.__defaults__ = tuple(fix(d) for d in fn.__defaults__)
    u.COUR = str(FONTS / "CourierPrime-Regular.ttf")
    u.COUR_B = str(FONTS / "CourierPrime-Bold.ttf")
    u.GLYPHS = str(src / "docs" / "concepts" / "round17_slice_system" / "glyphs")
    u._fc.clear()
    U, SL = u, sl


def A(rel: str) -> Image.Image:
    return Image.open(ROOT / rel).convert("RGBA")


def scaled(im: Image.Image, k: float) -> Image.Image:
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


def paste_c(img: Image.Image, im: Image.Image, cx: float, cy: float) -> Image.Image:
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    lay.paste(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))), im)
    return Image.alpha_composite(img, lay)


def mono(size):
    return U.F(U.MONO, size)


def plex(size, medium=False):
    return U.F(U.PLEX_M if medium else U.PLEX, size)


def bust(cls: str, var: int, size: int, frame: int = 0, grey: bool = False) -> Image.Image:
    """A v2 bust (assets/portraits/busts_<class>.png: columns = frames, rows = rookie variants)."""
    sheet = A("assets/portraits/busts_%s.png" % cls)
    cw, ch = 240, 266
    im = sheet.crop((frame * cw, var * ch, frame * cw + cw, var * ch + ch))
    im = im.resize((size, round(size * ch / cw)), Image.LANCZOS)
    if grey:
        a = im.split()[3]
        im = im.convert("L").convert("RGBA")
        im.putalpha(a)
    return im


def print_photo(cls: str, var: int, w: int) -> Image.Image:
    """The corp's photo print of the variant (assets/portraits/prints_<class>.jpg, one column)."""
    sheet = Image.open(ROOT / ("assets/portraits/prints_%s.jpg" % cls)).convert("RGBA")
    im = sheet.crop((0, var * 266, 240, var * 266 + 266))
    return im.resize((w, round(w * 266 / 240)), Image.LANCZOS)


# ---------------------------------------------------------------------------------------- base
def base(shots: Path, sink=((0, 0, 0, 0),)) -> Image.Image:
    """The real capture, with the panel edges sunk a little (as the round 32 HUD concept does)."""
    import numpy as np
    img = Image.open(shots / "02_meridian_raid.png").convert("RGB").resize((W, H), Image.LANCZOS)
    a = np.asarray(img, np.float32)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    k = np.ones((H, W), np.float32) * 0.96
    for (l, t, r, b) in sink:
        if l:
            k -= l * np.clip(1 - x / 460, 0, 1)
        if r:
            k -= r * np.clip((x - 1460) / 460, 0, 1)
        if t:
            k -= t * np.clip(1 - y / 160, 0, 1)
        if b:
            k -= b * np.clip((y - 860) / 220, 0, 1)
    a = a * np.clip(k, 0.4, 1)[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")


# ---------------------------------------------------------------------------------------- map layer
def ring(img, c, r, col, w=3, glow=0.4):
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline=255, width=w)
    img = U.add_glow(img, m, col, 6, glow)
    return U.over(img, col, m)


def pips(img, c, n, col, y_off):
    d = U.BD(img)
    for k in range(n):
        px = c[0] - (n - 1) * 8 + k * 16
        d.rectangle([px - 5, c[1] + y_off, px + 5, c[1] + y_off + 10], fill=col + (255,), outline=(8, 8, 12, 255), width=2)
    return img


def site(img, key, kind, state, tier=1, k=0.72):
    """Site marker v4 from main's assets: pad + icon disc + availability ring + tier pips."""
    c = N[key]
    pad = {"cleared": "pad_cleared"}.get(state, "pad_corporate_meridian")
    img = paste_c(img, scaled(A("assets/city/grid_markers/%s.png" % pad), k), c[0], c[1])
    disc = {"site": "disc_site_meridian", "heat": "disc_heat", "intel": "disc_exploit_intel"}[kind]
    if state == "cleared":
        disc += "_cleared"
    dk = k * (0.75 if state == "notyet" else 1.0)
    d = scaled(A("assets/city/grid_markers/%s.png" % disc), dk)
    dy = c[1] - 16
    img = paste_c(img, d, c[0], dy)
    rc = {"next": ORANGE_RING, "notyet": (236, 236, 236), "cleared": (150, 150, 158)}[state]
    img = ring(img, (c[0], dy), d.width / 2 + 5, rc, 4 if state == "next" else 3, 0.5 if state == "next" else 0.2)
    if state == "cleared":
        img = paste_c(img, scaled(A("assets/city/grid_markers/badge_cleared.png"), k), c[0] + d.width / 2, dy - d.height / 2 + 4)
    if tier and state != "cleared":
        img = pips(img, (c[0], dy), tier, (255, 210, 77) if kind == "intel" else (236, 236, 236), d.height / 2 + 7)
    return img


def socket(img, key, kind, k=0.68, beacon=None, state="hp100"):
    """The Cell's node at the RAID band: its raid socket (assets/raid/sockets) and a class beacon."""
    c = N[key]
    if key in DOWN:
        state, beacon = "down", None
    if beacon:
        strip = A("assets/raid/beacons/%s.png" % beacon)
        fr = strip.crop((0, 0, 220, 260))
        fr = scaled(fr, 0.62)
        # the beacon's pad point (110, 210) on the socket
        img = paste_c(img, fr, c[0], c[1] - (210 - 130) * 0.62 - 6)
    s = scaled(A("assets/raid/sockets/%s_%s.png" % (kind, state)), k)
    return paste_c(img, s, c[0], c[1] - 4)


# Q11: the Cell's nodes drawn DOWN (the white bolt over a greyed socket, ruling 11).
DOWN: set = set()


def name_chip(img, xy, words, col=ORANGE_RING, anchor="l", size=15, sub=None):
    """A terminal name chip by a Site (selectable Sites only: what can be run reads at a glance)."""
    f = mono(size)
    tw = U.tw(words, f, 1.0)
    x, y = xy
    if anchor == "r":
        x -= tw + 26
    box = (x, y - 13, x + tw + 26, y + 13 + (16 if sub else 0))
    m = U.rect_mask(img.size, box, chamfer=6)
    img = U.over(img, U.NAVY, m, 0.84)
    d = U.BD(img)
    d.rectangle([box[0], box[1], box[0] + 4, box[3]], fill=col + (255,))
    U.text(img, (box[0] + 14, y), words, f, U.WHITE, "lm", 1.0)
    if sub:
        U.text(img, (box[0] + 14, y + 17), sub, mono(13), col, "lm", 0.8)
    return img


def map_layer(img, selected="drone", raid=True, chips=True, select_circle=True, jack_link=True):
    img = site(img, "drone", "site", "next", 1)
    img = site(img, "lose", "heat", "next", 1)
    img = site(img, "vault", "intel", "next", 2)
    img = site(img, "keyauth", "site", "notyet", 2)
    img = site(img, "parcel", "site", "cleared", 1)
    img = socket(img, "customs", "firewall")
    img = socket(img, "returns", "safehouse", beacon="ghost")
    img = socket(img, "core", "core", k=0.66)
    # pencil: the Central Server (red TARGET), the raid's forecast routes (red dashed = what-if until set up)
    pr = U.Pencil(img.size, U.PEN_R, seed=17)
    pr.circle(CASTLE[0], CASTLE[1], 232, 176, width=8, start=-2.6)
    pr.text("TARGET", 1290, 352, 40, angle=12)
    if raid:
        dashed(pr, [(x + 7, y - 9) for x, y in ROUTE_B], 6)
        pr.circle(N["lose"][0], N["lose"][1] - 14, 40, 30, width=5, start=-1.0)
        pr.text("A", N["lose"][0] - 52, N["lose"][1] + 18, 30)
    img = pr.ink(img)
    if select_circle or jack_link:
        py = U.Pencil(img.size, U.PEN_Y, seed=18)
        if select_circle:
            c = N[selected]
            py.circle(c[0], c[1] - 14, 62, 46, width=7, start=-2.2)
        if jack_link:
            dashed(py, [(x - 8, y + 10) for x, y in JACK_LINK], 5, dash=14, gap=11, head=False)
        img = py.ink(img)
    img = target_chip(img)
    if chips:
        img = name_chip(img, (N["lose"][0] + 46, N["lose"][1] - 62), "T1  " + NAMES["lose"], sub="HEAT OBJECTIVE  -6")
        img = name_chip(img, (N["vault"][0] + 50, N["vault"][1] - 46), "T2  " + NAMES["vault"], col=U.GOLD, sub="EXPLOIT: INTEL")
        img = name_chip(img, (N["drone"][0] - 74, N["drone"][1] - 70), "T1  " + NAMES["drone"], anchor="r")
    return img


def target_chip(img):
    """`CENTRAL SERVER // <name>` yellow chip with EXPLOITS n/3 above the red TARGET circle (bible 4.5)."""
    words = "CENTRAL SERVER // THE MASTER MANIFEST"
    f = mono(16)
    tw = U.tw(words, f, 1.2)
    x0, y = CASTLE[0] - tw / 2 - 70, 262
    box = (x0, y - 15, x0 + tw + 150, y + 15)
    m = U.rect_mask(img.size, box, chamfer=6)
    img = U.over(img, (20, 16, 4), m, 0.9)
    e = ImageChops.subtract(m, SL.erode(m, 2))
    img = U.over(img, U.GOLD, e)
    U.text(img, (x0 + 12, y), words, f, U.GOLD, "lm", 1.2)
    U.text(img, (box[2] - 12, y), "EXPLOITS 1/3", f, U.WHITE, "rm", 1.2)
    return img


def dashed(pen, pts, width=6, dash=24, gap=15, head=True):
    path = SL.catmull(pen.wobble(pts, 1.0), 14)
    acc, on, seg = 0.0, True, [path[0]]
    for i in range(1, len(path)):
        a, b = path[i - 1], path[i]
        acc += math.hypot(b[0] - a[0], b[1] - a[1])
        seg.append(b)
        if acc >= (dash if on else gap):
            if on and len(seg) > 1:
                pen.stroke(seg, width, taper=False)
            on, acc, seg = not on, 0.0, [b]
    if on and len(seg) > 1:
        pen.stroke(seg, width, taper=False)
    if head:
        ex, ey = path[-1]
        px, py = path[-6]
        ang = math.atan2(ey - py, ex - px)
        for s in (-0.5, 0.5):
            hx, hy = ex + 22 * math.cos(ang + math.pi + s), ey + 22 * math.sin(ang + math.pi + s)
            pen.stroke([(hx, hy), (ex, ey)], width, taper=False)


# ---------------------------------------------------------------------------------------- top bar
def heat_gauge(img, x0, y0, hq=True, open_=False, scale=1.0):
    """The run-wide HEAT indicator: the same tag, the same place, on every screen (HQ and run).
    Number = bare Anton in the band colour; the band word printed; the five-band strip with the
    marker. At the HQ the tag is a button (a caret): it opens the Heat terminal (Scrub Heat)."""
    s = scale
    band = "FLAGGED"
    col = BAND_COL[band]
    x1, y1 = x0 + 356 * s, y0 + 66 * s
    m = U.rect_mask(img.size, (x0, y0, x1, y1), chamfer=int(10 * s))
    img = U.over(img, U.NAVY, m, 0.94)
    e = ImageChops.subtract(m, SL.erode(m, 2))
    img = U.add_glow(img, e, col, 7, 0.45 if not open_ else 0.9)
    img = U.over(img, col, e, 0.95)
    U.text(img, (x0 + 12 * s, y0 + 16 * s), "HEAT", mono(round(14 * s)), (200, 170, 150), "lm", 1.4)
    img = U.live_number(img, (x0 + 12 * s, y0 + 44 * s), str(HEAT), round(40 * s), col, glow=0.4)
    U.text(img, (x0 + 86 * s, y0 + 20 * s), band, mono(round(19 * s)), col, "lm", 1.8)
    U.text(img, (x1 - 12 * s, y0 + 20 * s), "/100", mono(round(14 * s)), (150, 150, 160), "rm", 1.0)
    bx0, bx1, by = x0 + 86 * s, x1 - 14 * s, y0 + 48 * s
    d = U.BD(img)
    for lo, hi, word in BANDS:
        xa, xb = bx0 + (bx1 - bx0) * lo / 100, bx0 + (bx1 - bx0) * hi / 100
        bc = BAND_COL[word]
        d.rectangle([xa + 1, by - 5 * s, xb - 1, by + 5 * s], fill=bc + (60,))
        fill_to = min(xb, bx0 + (bx1 - bx0) * HEAT / 100)
        if fill_to > xa:
            d.rectangle([xa + 1, by - 5 * s, fill_to - 1, by + 5 * s], fill=bc + (235,))
    for th in (25, 50, 75):
        tx = bx0 + (bx1 - bx0) * th / 100
        d.line([(tx, by - 9 * s), (tx, by + 8 * s)], fill=(235, 235, 240, 255), width=2)
    mx = bx0 + (bx1 - bx0) * HEAT / 100
    d.polygon([(mx - 6 * s, by - 14 * s), (mx + 6 * s, by - 14 * s), (mx, by - 6 * s)], fill=(255, 255, 255, 255))
    if hq:
        d.polygon([(x1 - 22 * s, y1 - 14 * s), (x1 - 10 * s, y1 - 14 * s), (x1 - 16 * s, y1 - 7 * s)], fill=col + (255,))
    return img, (x0, y0, x1, y1)


def stat_tag(img, x, y, name, value, sub, glyph, col, w):
    box = (x, y, x + w, y + 66)
    m = U.rect_mask(img.size, box, chamfer=8)
    img = U.over(img, U.NAVY, m, 0.9)
    e = ImageChops.subtract(m, SL.erode(m, 2))
    img = U.over(img, U.CYAN, e, 0.55)
    img = U.paste_glyph(img, glyph, (x + 22, y + 40), 26, col)
    U.text(img, (x + 40, y + 16), name, mono(15), (130, 160, 190), "lm", 1.0)
    end = U.text(img, (x + 40, y + 44), value, mono(28), U.WHITE, "lm", 1.0)
    if sub:
        U.text(img, (end + 4, y + 49), sub, mono(15), (130, 150, 170), "lm", 0.6)
    return img


def top_bar(img, run=False, heat_open=False):
    """The HudBar every screen shares: HEAT always first at the same spot, then the group's numbers."""
    m = U.rect_mask(img.size, (0, 0, W, 86))
    img = U.over(img, (3, 8, 20), m, 0.9)
    d = U.BD(img)
    d.line([(0, 86), (W, 86)], fill=U.CYAN + (200,), width=2)
    img, hb = heat_gauge(img, 14, 10, hq=not run, open_=heat_open)
    x = 352
    if run:
        tags = [("HP", "52", "/60", "picto_hp", U.PINK, 132), ("CYCLES", "85", None, "placeholder_vault", U.GOLD, 136),
                ("CARDS", "14", None, "picto_draw", U.CYAN, 120), ("RANK", "2", None, "picto_perfect", U.LIME, 110),
                ("BANKED", "12", None, "placeholder_key", U.GOLD, 132)]
    else:
        tags = [("SCHEMATICS", "142", None, "placeholder_vault", U.GOLD, 170), ("HOME", "44", "/50", "placeholder_shield", U.PINK, 140),
                ("EXPLOITS", "1", "/3", "picto_breach", U.GOLD, 140), ("RAIDS", "1", None, "picto_target", U.HARM, 116),
                ("ICE", "5", None, "state_frozen", U.CYAN, 100), ("CREW", "3", "/4", "picto_all_targets", U.CYAN, 120)]
    x += 40
    for name, v, sub, g, col, w in tags:
        img = stat_tag(img, x, 10, name, v, sub, g, col, w)
        x += w + 8
    img = U.term_button(img, (1600, 16, 1820, 70), "VIEW LOADOUT", None, "idle")
    d = U.BD(img)
    d.ellipse([1836, 18, 1890, 72], outline=(176, 110, 255, 255), width=3)
    U.text(img, (1863, 45), "D", U.F(U.ANTON, 26), (176, 110, 255), "mm")
    U.text(img, (1890, 70), "2", mono(14), U.WHITE, "rm")
    return img


# ---------------------------------------------------------------------------------------- stickers
_stk = {}


def stk(word, size, fill, seed, focus=False):
    key = (word, size, seed, focus, str(fill))
    if key not in _stk:
        sd = U.sticker(word, size, fill, seed=seed)
        _stk[key] = U.focus_sticker(sd) if focus else sd
    return _stk[key]


def jack_in(img, cx, cy, focus=True, size=84, angle=-3):
    return U.place(img, stk("JACK IN", size, U.FILL_PINK, 31, focus), cx, cy, angle=angle)


def title(img, word, cx, cy, size=50, seed=22):
    return U.place(img, stk(word, size, U.FILL_YELLOW, seed), cx, cy, angle=-3)


def key_hint(img, xy, key, words, anchor="la"):
    x, y = xy
    f = mono(15)
    kw = U.tw(key, f) + 14
    d = U.BD(img)
    d.rounded_rectangle([x, y - 12, x + kw, y + 12], 4, outline=(200, 214, 230, 255), width=2)
    U.text(img, (x + kw / 2, y), key, f, U.WHITE, "mm")
    U.text(img, (x + kw + 8, y), words, f, (180, 196, 214), "lm", 0.6)
    return x + kw + 8 + U.tw(words, f, 0.6) + 22


def pad_prompts(img, items, y=1056, x=24):
    for k, w in items:
        x = key_hint(img, (x, y), k, w)
    return img


# ---------------------------------------------------------------------------------------- shared panels
def site_holo(img, box, gains=True, compact=False):
    """The selected Site as decrypted holo (bible 1.2: hacked corp intel), its IF CLEARED inside."""
    x0, y0, x1, y1 = box
    img = U.holo_panel(img, box, "meridian", None, seed=12, alpha=0.86)
    U.text(img, (x0 + 18, y0 + 24), "T1  //  DRONE CHARGING YARD", mono(21), (255, 200, 140), "lm", 1.4)
    img = pips(img, (x1 - 46, y0 + 16), 1, (236, 236, 236), 0)
    rows = [("TYPE", "Logistics yard  //  Router run"), ("REWARDS", "+10 Schematics, Firmware"), ("LINK", "from RETURNS PROCESSING CENTRE")]
    yy = y0 + 58
    for a, b in rows[: 2 if compact else 3]:
        U.text(img, (x0 + 18, yy), a, mono(15), (255, 190, 130), "lm", 1.0)
        U.text(img, (x1 - 18, yy), b, mono(17), U.WHITE, "rm", 0.6)
        yy += 27
    if gains:
        yy += 4
        d = U.BD(img)
        d.line([(x0 + 14, yy - 10), (x1 - 14, yy - 10)], fill=MER + (120,), width=1)
        U.text(img, (x0 + 18, yy + 6), "IF CLEARED", mono(15), U.CYAN, "lm", 1.6)
        chips = [("+10", U.GOLD, "placeholder_vault"), ("HEAT +2", BAND_COL["FLAGGED"], "placeholder_burn"),
                 ("OPENS 1", U.LIME, "picto_all_targets"), ("NODE", U.LIME, "placeholder_key")]
        cx = x0 + 18
        cy = yy + 34
        for words, col, g in chips:
            wv = U.tw(words, mono(15), 0.8) + 40
            if cx + wv > x1 - 14:
                cx, cy = x0 + 18, cy + 30
            m = U.rect_mask(img.size, (cx, cy - 12, cx + wv, cy + 12), chamfer=5)
            img = U.over(img, U.NAVY, m, 0.85)
            e = ImageChops.subtract(m, SL.erode(m, 1))
            img = U.over(img, col, e, 0.8)
            img = U.paste_glyph(img, g, (cx + 13, cy), 16, col)
            U.text(img, (cx + 25, cy), words, mono(15), col, "lm", 0.8)
            cx += wv + 8
    st = U.rubber_stamp("DECRYPTED", 14, U.GREEN, angle=-4, seed=3, font=U.MONO, pad=5)
    img = U.paste_rgba(img, st, (x1 - 70, y0 - 2))
    return img


def runner_line(img, box, op, label="RUNNER", pick=True):
    x0, y0, x1, y1 = box
    img = U.term_panel(img, box, None, hexbg=False, chamfer=8, header=False, glow=0.3)
    U.text(img, (x0 + 14, (y0 + y1) / 2), label, mono(14), (130, 160, 190), "lm", 1.2)
    b = bust(op["cls"], op["var"], 46)
    img = paste_c(img, b.crop((0, 0, 46, 46)), x0 + 112, (y0 + y1) / 2)
    d = U.BD(img)
    d.rectangle([x0 + 89, (y0 + y1) / 2 - 23, x0 + 135, (y0 + y1) / 2 + 23], outline=CLASS_COL[op["cls"]] + (255,), width=2)
    U.text(img, (x0 + 148, (y0 + y1) / 2), "%s  %s R%d" % (op["name"], op["cls"].upper(), op["rank"]), mono(18), U.WHITE, "lm", 0.8)
    if pick:
        U.text(img, (x1 - 14, (y0 + y1) / 2), "< LB  RB >", mono(14), (130, 160, 190), "rm", 0.6)
    return img


def work_order(img, xy, angle=-2.0, w=360, h=250, chip=True):
    """RAID INCOMING as the raid's own intercepted work order (paper), with RAID SETUP."""
    p = U.paper_tex(w, h, seed=8)
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, w, 44], fill=(250, 246, 236, 255))
    d.text((16, 12), "MERIDIAN FREIGHT", font=U.F(U.PLEX_M, 18), fill=MER + (255,))
    d.text((16, 31), "YARD SECURITY  //  WORK ORDER 52-MF", font=U.F(U.COUR, 12), fill=(80, 70, 60, 255))
    d.text((16, 56), "ROUTE AUDIT", font=U.F(U.ANTON, 34), fill=(24, 20, 22, 255))
    rows = [("TARGET", "CORE (CELL)"), ("UNITS", "4 IN 1 WAVE"), ("ENTRY SITES", "1 (A)"), ("TRIGGER", "HEAT 50 CROSSED")]
    yy = 106
    for a, b in rows:
        d.text((16, yy), a, font=U.F(U.COUR, 15), fill=(70, 62, 56, 255))
        d.text((w - 16, yy), b, font=U.F(U.COUR_B, 16), fill=(30, 26, 26, 255), anchor="ra")
        yy += 24
    for k in range(3):
        d.rectangle([16 + k * 104, h - 34, 16 + k * 104 + 86, h - 24], fill=(18, 16, 18, 255))
    st = U.rubber_stamp("INTERCEPTED", 24, (200, 30, 40), angle=-10, seed=6)
    p.alpha_composite(st, (w - st.width - 6, h - st.height - 2))
    img = U.paste_paper(img, p, xy, angle=angle)
    if chip:
        x, y = xy
        img = U.term_button(img, (x + 18, y + h + 12, x + w - 18, y + h + 64), "RAID SETUP", "[R]", "idle", accent=U.HARM)
    return img


def scrub_note(img, box):
    """The Heat terminal the HEAT tag opens at the HQ (heat_indicator.png)."""
    x0, y0, x1, y1 = box
    img = U.term_panel(img, box, "HEAT  //  SUSPECT FILE", accent=BAND_COL["FLAGGED"], tag="FLAGGED", tag_col=BAND_COL["FLAGGED"], seed=5)
    lines = [("IN FORCE", "Elites more frequent (25+)", (230, 220, 210)), ("", "All enemies +1 resistance (50+)", (230, 220, 210)),
             ("NEXT", "60 complication  //  75 RAID", BAND_COL["NOTICED"]), ("SINKS", "Heat objective Sites, Proxy Relay", (170, 180, 196))]
    yy = y0 + 56
    for a, b, c in lines:
        U.text(img, (x0 + 16, yy), a, mono(15), (200, 160, 130), "lm", 1.2)
        U.text(img, (x0 + 120, yy), b, plex(19), c, "lm")
        yy += 30
    img = U.term_button(img, (x0 + 16, y1 - 66, x1 - 16, y1 - 16), "SCRUB HEAT  -5", "pay 25 Schematics  (next 35)", "focus", accent=BAND_COL["FLAGGED"])
    return img


# ---------------------------------------------------------------------------------------- direction A
def crew_rows(img, box, sel=0, tabs=True):
    x0, y0, x1, y1 = box
    img = U.term_panel(img, box, "CREW", tag="3 ALIVE / 4", seed=7)
    for k, op in enumerate(CREW):
        ry = y0 + 46 + k * 92
        dead = op.get("dead", False)
        if k == sel:
            m = U.rect_mask(img.size, (x0 + 10, ry - 4, x1 - 10, ry + 82), chamfer=8)
            img = U.over(img, U.PINK, m, 0.14)
            img = U.over(img, U.PINK, ImageChops.subtract(m, SL.erode(m, 2)))
        b = bust(op["cls"], op["var"], 74, frame=1 if dead else 0, grey=dead)
        img = paste_c(img, b.crop((0, 0, 74, 74)), x0 + 54, ry + 39)
        d = U.BD(img)
        d.rectangle([x0 + 17, ry + 2, x0 + 91, ry + 76], outline=(CLASS_COL[op["cls"]] if not dead else (90, 90, 100)) + (255,), width=2)
        U.text(img, (x0 + 104, ry + 16), op["name"], mono(24), U.WHITE if not dead else (130, 130, 140), "lm", 1.4)
        U.text(img, (x0 + 104, ry + 44), "%s  R%d" % (op["cls"].upper(), op["rank"]), mono(16), (130, 160, 190), "lm", 1.0)
        for p in range(3):
            d.rectangle([x0 + 228 + p * 12, ry + 39, x0 + 236 + p * 12, ry + 49], fill=(U.GOLD if p < op["rank"] else (50, 54, 66)) + (255,))
        U.text(img, (x1 - 18, ry + 16), op["hp"], mono(18), U.WHITE if not dead else (110, 110, 120), "rm", 0.8)
        col = U.GREEN if op["status"] == "READY" else (U.CYAN if not dead else (150, 150, 160))
        U.text(img, (x1 - 18, ry + 44), op["status"], mono(14), col, "rm", 0.6)
        if k == sel:
            U.text(img, (x0 + 104, ry + 68), "RUNS DRONE CHARGING YARD", mono(13), U.PINK, "lm", 1.0)
        if dead:
            d.line([(x0 + 102, ry + 16), (x0 + 200, ry + 16)], fill=(160, 160, 170, 255), width=2)
    img = U.term_button(img, (x0 + 14, y1 - 58, x0 + 186, y1 - 14), "RECRUIT", "15", "idle")
    img = U.term_button(img, (x0 + 196, y1 - 58, x1 - 14, y1 - 14), "LOADOUT", "[L]", "idle")
    return img


def direction_a(shots: Path) -> Image.Image:
    img = base(shots, ((0.3, 0.25, 0.3, 0.3),))
    img = map_layer(img)
    img = top_bar(img)
    img = title(img, "THE GRID", 160, 140)
    # left: CREW | MARKET tabs over one column (the market is the crew column's second tab)
    img, _ = U.tabs(img, (20, 188), ["CREW", "MARKET"], 0)
    img = crew_rows(img, (20, 236, 420, 690))
    # left foot: the map key as one strip
    img = U.term_panel(img, (20, 708, 420, 800), "MAP KEY", seed=8)
    U.text(img, (34, 770), "orange: run now  white: not yet  lime: yours", mono(14), (190, 204, 220), "lm", 0.2)
    # right: the selected Site (holo + IF CLEARED inside), the runner, JACK IN
    img = site_holo(img, (1452, 700, 1900, 900))
    img = runner_line(img, (1452, 912, 1900, 962), CREW[0])
    img = jack_in(img, 1716, 1018, size=70)
    # bottom centre: the pending raid (terminal strip with RAID SETUP)
    rb = (452, 952, 1180, 1064)
    img = U.term_panel(img, rb, "RAID PENDING", accent=U.HARM, tag="HEAT 50 CROSSED", tag_col=U.HARM, seed=21)
    U.text(img, (472, 996), "ROUTE AUDIT  //  4 units  //  entry A", mono(18), U.WHITE, "la", 0.8)
    U.text(img, (472, 1024), "set it up now, or it hits mid-run", mono(15), (220, 170, 170), "la", 0.4)
    img = U.term_button(img, (976, 992, 1166, 1050), "RAID SETUP", "[R]", "idle", accent=U.HARM)
    img = U.term_button(img, (20, 818, 210, 870), "< PREV", "[Q]", "idle")
    img = U.term_button(img, (220, 818, 420, 870), "NEXT >", "[E]", "idle")
    return img


# ---------------------------------------------------------------------------------------- direction B
def crew_card(img, cx, cy, op, sel=False, lift=0.0, angle=0.0, w=170, hire=None):
    """A crew card in the hand: the corp's photo print of the operative on a Cell card (paper-like
    sticker card, the raid's defence-card size), name plate, HP, status chip."""
    h = int(w * 1.32)
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    dead = op.get("dead", False)
    cc = CLASS_COL[op["cls"]]
    d.rounded_rectangle([0, 0, w - 1, h - 1], 10, fill=(22, 24, 34, 255), outline=(246, 243, 236, 255), width=4)
    d.rectangle([4, 4, w - 5, 12], fill=cc + (255,))
    ph = print_photo(op["cls"], op["var"], w - 24)
    if dead:
        a = ph.split()[3]
        ph = ph.convert("L").convert("RGBA")
        ph.putalpha(a)
    ph = ph.crop((0, 0, ph.width, int(ph.width * 0.9)))
    card.alpha_composite(ph, (12, 20))
    dd = ImageDraw.Draw(card)
    dd.rectangle([12, 20, w - 13, 20 + ph.height], outline=(10, 10, 14, 255), width=2)
    ny = 26 + ph.height
    dd.text((14, ny), op["name"], font=U.F(U.ANTON, 26), fill=(246, 243, 236, 255))
    dd.text((w - 14, ny + 8), "R%d" % op["rank"], font=U.F(U.MONO, 16), fill=(255, 210, 77, 255), anchor="ra")
    dd.text((14, ny + 36), op["cls"].upper(), font=U.F(U.MONO, 14), fill=cc + (255,))
    dd.text((w - 14, ny + 36), op["hp"], font=U.F(U.MONO, 14), fill=(230, 230, 236, 255), anchor="ra")
    stc = (123, 224, 123) if op["status"] == "READY" else ((91, 224, 255) if not dead else (160, 160, 168))
    dd.rectangle([12, h - 30, w - 13, h - 10], fill=(8, 12, 22, 255), outline=stc + (255,), width=1)
    dd.text((w / 2, h - 20), op["status"], font=U.F(U.MONO, 13), fill=stc + (255,), anchor="mm")
    if dead:
        st = U.rubber_stamp("FLATLINED", 22, (220, 40, 40), angle=-14, seed=4)
        card.alpha_composite(st, ((w - st.width) // 2, 40))
    if hire:
        st = U.rubber_stamp("HIRE", 30, (255, 61, 168), angle=-10, seed=5)
        card.alpha_composite(st, ((w - st.width) // 2, 50))
    if sel:
        m = card.split()[3]
        glow = Image.new("RGBA", (w + 40, h + 40), U.LIME + (0,))
        mm = Image.new("L", glow.size, 0)
        mm.paste(m, (20, 20))
        halo = ImageChops.subtract(SL.dilate(mm, 9), SL.dilate(mm, 4))
        glow.putalpha(halo)
        g2 = Image.new("RGBA", glow.size, (0, 0, 0, 0))
        g2.alpha_composite(glow)
        g2.alpha_composite(card, (20, 20))
        card = g2
    card = card.rotate(angle, Image.BICUBIC, expand=True)
    sh = card.split()[3].filter(ImageFilter.GaussianBlur(8 + 10 * lift))
    shl = Image.new("RGBA", card.size, (4, 2, 8, 0))
    shl.putalpha(sh.point(lambda v: int(v * 0.6)))
    img = paste_c(img, shl, cx + 6 + 14 * lift, cy + 10 + 22 * lift)
    return paste_c(img, card, cx, cy - 26 * lift)


def hand_tabs(img, x, y, active=0, names=("CREW", "MARKET", "DEFENCE"), raid=True):
    for k, n in enumerate(names):
        st = "focus" if k == active else "idle"
        acc = U.HARM if n == "DEFENCE" else U.CYAN
        sub = {"CREW": "3 / 4", "MARKET": "142", "DEFENCE": "RAID 1" if raid else "ARMORY"}[n]
        img = U.term_button(img, (x, y + k * 64, x + 190, y + k * 64 + 54), n, sub, "pressed" if k == active else "idle", accent=acc)
    return img


def direction_b(shots: Path, mode="crew") -> Image.Image:
    img = base(shots, ((0.0, 0.2, 0.25, 0.42),))
    sel_site = "drone"
    defence = mode == "defence"
    img = map_layer(img, selected=sel_site, raid=not defence, chips=not defence, select_circle=not defence, jack_link=not defence)
    if defence:
        img = raid_setup_marks(img)
    img = top_bar(img)
    # the raid pending: its own paper, top left (where the raid setup's work order lives)
    img = work_order(img, (26, 112), angle=-2.0, w=340, h=236, chip=not defence)
    # the hand: CREW / MARKET / DEFENCE (the raid setup's card row; one hand, three decks)
    img = hand_tabs(img, 24, 856, active={"crew": 0, "market": 1, "defence": 2}[mode])
    if mode == "crew":
        xs = [380, 580, 780, 980]
        for k, op in enumerate(CREW):
            if k == 0:
                continue
            img = crew_card(img, xs[k], 966, op, angle=[0, 1.5, -1.0, 2.0][k])
        # the picked runner: lifted (parked) with the yellow plan arrow to the selected Site
        img = crew_card(img, 380, 940, CREW[0], sel=True, lift=1.0, angle=-2.0)
        py = U.Pencil(img.size, U.PEN_Y, seed=40)
        py.arrow([(452, 830), (760, 700), (1080, 640), (1290, 640)], width=7, head=24)
        img = py.ink(img)
        img = site_holo(img, (1452, 700, 1900, 900))
        img = jack_in(img, 1716, 990, size=84)
        U.text(img, (1716, 1062), "> jack --from RETURNS_PROC --to DRONE_YARD", mono(14), (150, 176, 200), "mm", 0.6)
    elif mode == "market":
        img = market_hand(img)
        img = site_holo(img, (1452, 700, 1900, 900))
        img = jack_in(img, 1716, 990, size=84, focus=False)
    else:
        img = defence_hand(img)
    return img


def market_hand(img):
    """The hand turned to MARKET: recruits (greyscale + HIRE, bible 4.12 recruit state), the next
    run's boosts and the Profile unlocks; one row, prices as gold terminal tags."""
    x = 300
    recruits = [{"name": "ROOKIE", "cls": "breaker", "rank": 0, "hp": "60/60", "status": "15 SCHEMATICS", "var": 3},
                {"name": "ROOKIE", "cls": "rigger", "rank": 0, "hp": "55/55", "status": "15 SCHEMATICS", "var": 1}]
    for k, op in enumerate(recruits):
        img = crew_card(img, x + 80 + k * 190, 966, op, angle=[1.0, -1.5][k], hire=True, sel=k == 0)
    boosts = [("WARM CACHE", "10"), ("OVERCLOCKED DECK", "15"), ("FIELD KIT", "20")]
    bx = 700
    for k, (n, p) in enumerate(boosts):
        sd = stk(n, 26, U.FILL_CYAN, 70 + k)
        img = U.place(img, sd, bx + 80 + k * 200, 930, angle=[-2, 1.5, -1][k])
        img = gold_price(img, bx + 80 + k * 200, 1000, p)
    ux = 1330
    for cx, words in ((x + 20, "RECRUIT"), (bx + 10, "NEXT RUN'S BOOSTS"), (ux - 30, "PROFILE UNLOCKS")):
        f = mono(16)
        m = U.rect_mask(img.size, (cx - 8, 818, cx + U.tw(words, f, 1.4) + 8, 842), chamfer=4)
        img = U.over(img, U.NAVY, m, 0.85)
        U.text(img, (cx, 830), words, f, U.CYAN, "lm", 1.4)
    img = U.term_button(img, (ux - 30, 892, ux + 110, 948), "GHOST", "class 80", "idle")
    img = U.term_button(img, (ux - 30, 958, ux + 110, 1014), "COMPILER", "node 30", "idle")
    return img


def gold_price(img, cx, cy, p):
    f = mono(17)
    words = p + "  SCHEMATICS"
    tw = U.tw(words, f, 0.8)
    m = U.rect_mask(img.size, (cx - tw / 2 - 12, cy - 13, cx + tw / 2 + 12, cy + 13), chamfer=5)
    img = U.over(img, U.NAVY, m, 0.9)
    img = U.over(img, U.GOLD, ImageChops.subtract(m, SL.erode(m, 1)))
    U.text(img, (cx, cy), words, f, U.GOLD, "mm", 0.8)
    return img


def raid_setup_marks(img):
    """The raid setup on the same map: the threat route solid (what will happen), the forecast ring
    on the node it reaches, a yellow plan circle on the node a card is being placed on."""
    pr = U.Pencil(img.size, U.PEN_R, seed=27)
    pts = [(x + 7, y - 9) for x, y in ROUTE_B]
    path = SL.catmull(pr.wobble(pts, 1.0), 14)
    pr.stroke(path, 6, taper=False)
    ex, ey = path[-1]
    px, py_ = path[-6]
    ang = math.atan2(ey - py_, ex - px)
    for s in (-0.5, 0.5):
        pr.stroke([(ex + 22 * math.cos(ang + math.pi + s), ey + 22 * math.sin(ang + math.pi + s)), (ex, ey)], 6, taper=False)
    pr.circle(N["lose"][0], N["lose"][1] - 14, 40, 30, width=5, start=-1.0)
    pr.text("A", N["lose"][0] - 52, N["lose"][1] + 18, 30)
    img = pr.ink(img)
    py = U.Pencil(img.size, U.PEN_Y, seed=28)
    py.circle(N["customs"][0], N["customs"][1] - 8, 56, 40, width=6)
    py.arrow([(600, 818), (628, 796), (652, 784)], width=6, head=18)
    img = py.ink(img)
    img = name_chip(img, (705, 606), "IF PLACED: ICE LOCK", col=U.CYAN, sub="CORE 44 > 44 HOLDS")
    return img


def defence_hand(img, y=966, x0=380):
    """The hand turned to DEFENCE: the raid setup in place (same page): the Armory's defence cards,
    the routes solid, START DEFENSE where JACK IN was. Only the hand and the verb change."""
    names = [("TURRET", "4 dmg, range 1"), ("ICE LOCK", "holds 2 steps"), ("DECOY", "pulls 3 threats")]
    for k, (n, d) in enumerate(names):
        cx = x0 + k * 200
        card = Image.new("RGBA", (170, 220), (0, 0, 0, 0))
        dd = ImageDraw.Draw(card)
        dd.rounded_rectangle([0, 0, 169, 219], 10, fill=(22, 24, 34, 255), outline=(246, 243, 236, 255), width=4)
        dd.rectangle([4, 4, 165, 12], fill=(91, 224, 255, 255))
        g = {"TURRET": "picto_target", "ICE LOCK": "state_frozen", "DECOY": "placeholder_spoof"}[n]
        card.alpha_composite(U.glyph(g, 70, (91, 224, 255)), (50, 36))
        dd.text((14, 124), n, font=U.F(U.ANTON, 26), fill=(246, 243, 236, 255))
        dd.text((14, 160), d, font=U.F(U.PLEX, 15), fill=(200, 210, 222, 255))
        dd.text((155, 196), "x1", font=U.F(U.MONO, 14), fill=(230, 230, 236, 255), anchor="ra")
        lift = 34 if k == 1 else 0
        img = paste_c(img, card.rotate([1, -1.5, 0.5][k], Image.BICUBIC, expand=True), cx, y - lift)
    img = U.place(img, stk("START DEFENSE", 60, U.FILL_PINK, 33, True), 1716, 958, angle=-3)
    # Speed / Skip: the terminal strip under START DEFENSE (bible 4.8)
    x = 1520
    for k, s in enumerate(("1x", "2x", "4x", "SKIP")):
        img = U.term_button(img, (x, 1018, x + (70 if k < 3 else 96), 1066), s, None, "pressed" if k == 0 else "idle")
        x += (78 if k < 3 else 104)
    return img


# ---------------------------------------------------------------------------------------- direction C
VERBS = [("RUN", "pick a Site"), ("CREW", "station, loadout"), ("MARKET", "142 Schematics"), ("DEFEND", "RAID PENDING")]


def verb_bar(img, active=0, y=990):
    x = 470
    for k, (n, sub) in enumerate(VERBS):
        acc = U.HARM if n == "DEFEND" else U.CYAN
        w = 220
        state = "pressed" if k == active else "idle"
        img = U.term_button(img, (x, y, x + w, y + 66), "%d  %s" % (k + 1, n), sub, state, accent=acc)
        x += w + 10
    key_hint(img, (418, y + 33), "LB", "")
    key_hint(img, (x + 6, y + 33), "RB", "")
    return img


def run_panel(img, box):
    x0, y0, x1, y1 = box
    img = site_holo(img, (x0, y0, x1, y0 + 200))
    img = U.term_panel(img, (x0, y0 + 214, x1, y1), "WHO RUNS IT", seed=31)
    for k, op in enumerate(CREW):
        cx = x0 + 60 + k * 104
        dead = op.get("dead", False)
        b = bust(op["cls"], op["var"], 84, grey=dead or op["status"] != "READY")
        img = paste_c(img, b.crop((0, 0, 84, 84)), cx, y0 + 300)
        d = U.BD(img)
        col = U.PINK if k == 0 else (90, 96, 110)
        d.rectangle([cx - 43, y0 + 257, cx + 43, y0 + 343], outline=col + (255,), width=3 if k == 0 else 2)
        U.text(img, (cx, y0 + 360), op["name"], mono(15), U.WHITE if not dead else (120, 120, 130), "mm", 1.0)
        U.text(img, (cx, y0 + 380), "READY" if op["status"] == "READY" else ("POSTED" if not dead else "FLATLINED"), mono(12),
               U.GREEN if op["status"] == "READY" else (140, 140, 150), "mm", 0.8)
    return img


def direction_c(shots: Path, tab=0) -> Image.Image:
    img = base(shots, ((0.0, 0.2, 0.3, 0.38),))
    img = map_layer(img, raid=tab != 3, chips=tab == 0, select_circle=tab == 0, jack_link=tab == 0)
    if tab == 3:
        img = raid_setup_marks(img)
    if tab in (1, 2):
        img = dim_map(img, keep=[N["customs"], N["returns"], N["core"]] if tab == 1 else [])
    img = top_bar(img)
    img = verb_bar(img, tab)
    if tab == 0:
        img = run_panel(img, (20, 112, 468, 506))
        img = jack_in(img, 1716, 985, size=78)
    elif tab == 1:
        img = crew_rows(img, (20, 112, 420, 566), sel=1)
        img = U.term_button(img, (20, 584, 420, 640), "RECALL NOVA", "back to the crew", "idle")
        py = U.Pencil(img.size, U.PEN_Y, seed=41)
        py.circle(N["returns"][0], N["returns"][1] - 20, 64, 48, width=6)
        img = py.ink(img)
        img = name_chip(img, (N["returns"][0] + 70, N["returns"][1] + 40), "SAFEHOUSE: NOVA ON POST", col=U.LIME, sub="threats entering: delayed 1 step")
    elif tab == 2:
        img = market_panel(img, (20, 112, 470, 676))
    else:
        img = work_order(img, (26, 112), angle=-2.0, w=340, h=236, chip=False)
        img = defence_hand(img, y=850, x0=380)
    return img


def dim_map(img, keep):
    m = Image.new("L", img.size, 150)
    d = ImageDraw.Draw(m)
    for c in keep:
        d.ellipse([c[0] - 90, c[1] - 80, c[0] + 90, c[1] + 70], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(30))
    return U.over(img, (4, 6, 14), m, 0.9)


def market_panel(img, box):
    x0, y0, x1, y1 = box
    img = U.term_panel(img, box, "BLACK MARKET", accent=U.GOLD, tag="142 SCHEMATICS", tag_col=U.GOLD, seed=40)
    groups = [("RECRUIT", [("Breaker rookie", "15"), ("Rigger rookie", "15")]),
              ("NEXT RUN", [("Warm Cache", "10"), ("Overclocked Deck", "15"), ("Field Kit", "20")]),
              ("PROFILE", [("Class: Ghost", "80"), ("Node: Compiler Rack", "30")])]
    yy = y0 + 56
    for g, items in groups:
        U.text(img, (x0 + 16, yy), g, mono(16), U.GOLD, "lm", 1.6)
        yy += 30
        for n, p in items:
            img = U.term_button(img, (x0 + 16, yy - 4, x1 - 16, yy + 40), n.upper(), None, "focus" if n == "Breaker rookie" else "idle")
            U.text(img, (x1 - 30, yy + 18), p, mono(20), U.GOLD, "rm", 0.6)
            yy += 52
        yy += 10
    return img


# ---------------------------------------------------------------------------------------- boards
def heat_board(shots: Path) -> Image.Image:
    """The HEAT tag in the run (route) and at the HQ, same spot; the HQ's tag opens Scrub Heat."""
    img = base(shots, ((0.3, 0.2, 0.3, 0.3),))
    img = U.over(img, (4, 6, 14), Image.new("L", img.size, 255), 0.45)
    # strip 1: a run's top bar
    strip = top_bar(Image.new("RGBA", (W, 100), (0, 0, 0, 0)), run=True)
    img.alpha_composite(strip, (0, 120))
    U.text(img, (W - 30, 236), "IN A RUN (route, fight, shop: the same bar)", mono(18), U.CYAN, "ra", 1.0)
    # strip 2: the HQ's
    strip = top_bar(Image.new("RGBA", (W, 100), (0, 0, 0, 0)), run=False, heat_open=True)
    img.alpha_composite(strip, (0, 300))
    U.text(img, (W - 30, 416), "AT THE HQ (the city): the same tag, the same pixels", mono(18), U.CYAN, "ra", 1.0)
    img = scrub_note(img, (14, 392, 560, 690))
    U.text(img, (600, 470), "Press the HEAT tag (or pad: View) at the HQ:", plex(26, True), U.WHITE, "la")
    U.text(img, (600, 510), "the Heat terminal drops from it. Band, rules in force, next threshold,", plex(24), (200, 210, 222), "la")
    U.text(img, (600, 542), "and the one Heat action the GDD gives the HQ: SCRUB HEAT -5 (11.4).", plex(24), (200, 210, 222), "la")
    U.text(img, (600, 590), "No WANTED poster, no CELL STATUS badges: the rules in force live in", plex(24), (200, 210, 222), "la")
    U.text(img, (600, 622), "this terminal; the city shows Heat in the world (searchlights, bible 4.3).", plex(24), (200, 210, 222), "la")
    img = title(img, "HEAT", 120, 60, size=46)
    return img


def flow_board(shots: Path) -> list:
    """JACK IN like every netrun start: select -> runner -> JACK IN -> the 4.6 jack along the link."""
    frames = []
    # 1: hover / select
    f1 = base(shots, ((0.0, 0.2, 0.25, 0.42),))
    f1 = map_layer(f1, raid=False, chips=True, select_circle=False, jack_link=False)
    f1 = top_bar(f1)
    f1 = U.focus_brackets(f1, (N["drone"][0] - 40, N["drone"][1] - 60, N["drone"][0] + 40, N["drone"][1] + 26))
    frames.append(("1  POINT AT A SITE (pad: right stick / D-pad steps Sites)", f1))
    # 2: selected: pencil circle, holo, the link the jack will ride
    f2 = base(shots, ((0.0, 0.2, 0.25, 0.42),))
    f2 = map_layer(f2, raid=False)
    f2 = top_bar(f2)
    f2 = site_holo(f2, (1452, 700, 1900, 900))
    f2 = jack_in(f2, 1716, 990, size=84, focus=False)
    frames.append(("2  SELECTED: holo + IF CLEARED; the jack's link is drawn (dashed)", f2))
    # 3: runner picked, JACK IN focused
    f3 = direction_b(shots)
    frames.append(("3  RUNNER PICKED (card lifts, plan arrow); JACK IN takes focus", f3))
    # 4: the jack sequence (bible 4.6): terminal types on the link, rain on the link only
    f4 = base(shots, ((0.0, 0.2, 0.25, 0.42),))
    f4 = map_layer(f4, raid=False, chips=False, select_circle=False, jack_link=False)
    f4 = U.over(f4, (2, 4, 10), Image.new("L", f4.size, 255), 0.35)
    f4 = jack_terminal(f4)
    frames.append(("4  JACK IN: the same jack as every netrun start (4.6), on this city", f4))
    return frames


def jack_terminal(img):
    a, b = N["returns"], N["drone"]
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).line([a, (1395, 665), b], fill=255, width=8)
    img = U.add_glow(img, m, U.LIME, 14, 1.2)
    img = U.over(img, U.LIME, m)
    # bits falling onto the link
    import random
    r = random.Random(4)
    for _ in range(90):
        t = r.random()
        p0, p1 = (a, (1395, 665)) if t < 0.6 else ((1395, 665), b)
        tt = r.random()
        x = p0[0] + (p1[0] - p0[0]) * tt + r.uniform(-6, 6)
        y = p0[1] + (p1[1] - p0[1]) * tt - r.uniform(0, 160)
        U.text(img, (x, y), r.choice("01"), mono(r.choice([14, 16, 18])), (230, 255, 160) if r.random() < 0.3 else U.LIME, "mm")
    box = (1050, 420, 1560, 560)
    img = U.term_panel(img, box, "JACK", seed=9, accent=U.CYAN)
    lines = ["> jack --from RETURNS_PROC --to DRONE_YARD", "  routing ......... ok", "  handshake ....... ok", "  CONNECTED"]
    for k, s in enumerate(lines):
        U.text(img, (box[0] + 16, box[1] + 50 + k * 22), s, mono(17), U.LIME if k == 3 else U.WHITE, "lm", 0.6)
    return img


# ---------------------------------------------------------------------------------------- text 2.0
def direction_b_text20(shots: Path) -> Image.Image:
    """Direction B at text scale 2.0: words grow, drawn objects stop at x1.3 (STYLE 5.6); the hand
    shows the runner and pages the rest; the holo shows the IF CLEARED chips on two rows."""
    img = base(shots, ((0.0, 0.2, 0.25, 0.42),))
    img = map_layer(img, chips=False)
    img = name_chip(img, (N["drone"][0] - 470, N["drone"][1] - 100), "T1  " + NAMES["drone"], size=26)
    # a 2.0 top bar: HEAT keeps its full gauge; the other tags drop their captions (icons + numbers)
    m = U.rect_mask(img.size, (0, 0, W, 110))
    img = U.over(img, (3, 8, 20), m, 0.92)
    img, _ = heat_gauge(img, 14, 8, scale=1.42)
    x = 540
    for g, v, col in (("placeholder_vault", "142", U.GOLD), ("placeholder_shield", "44", U.PINK), ("picto_breach", "1/3", U.GOLD),
                      ("picto_target", "1", U.HARM), ("state_frozen", "5", U.CYAN), ("picto_all_targets", "3", U.CYAN)):
        box = (x, 14, x + 150, 96)
        mm = U.rect_mask(img.size, box, chamfer=8)
        img = U.over(img, U.NAVY, mm, 0.9)
        img = U.over(img, U.CYAN, ImageChops.subtract(mm, SL.erode(mm, 2)), 0.55)
        img = U.paste_glyph(img, g, (x + 34, 55), 40, col)
        U.text(img, (x + 64, 55), v, mono(44), U.WHITE, "lm", 0.6)
        x += 160
    img = U.term_button(img, (1520, 22, 1900, 92), "LOADOUT", None, "idle")
    img = work_order(img, (26, 140), w=420, h=280, chip=False)
    img = U.term_button(img, (40, 440, 440, 512), "RAID SETUP  [R]", None, "idle", accent=U.HARM)
    img = hand_tabs(img, 24, 800, 0)
    img = crew_card(img, 420, 920, CREW[0], sel=True, lift=1.0, angle=-2.0, w=220)
    img = crew_card(img, 680, 950, CREW[2], angle=1.5, w=220)
    img = U.term_button(img, (830, 900, 930, 1000), "+2", "more", "idle")
    py = U.Pencil(img.size, U.PEN_Y, seed=40)
    py.arrow([(520, 790), (900, 690), (1290, 640)], width=8, head=26)
    img = py.ink(img)
    # holo at 2.0: the name and the gains only; the rest in its tooltip
    box = (1300, 704, 1900, 920)
    img = U.holo_panel(img, box, "meridian", None, seed=12, alpha=0.88)
    U.text(img, (1320, 738), "T1  DRONE CHARGING YARD", mono(30), (255, 200, 140), "lm", 1.0)
    U.text(img, (1320, 784), "IF CLEARED", mono(24), U.CYAN, "lm", 1.2)
    cx, cy = 1320, 830
    for words, col in (("+10 SCHEM.", U.GOLD), ("HEAT +2", BAND_COL["FLAGGED"]), ("OPENS 1", U.LIME), ("YOUR NODE", U.LIME)):
        wv = U.tw(words, mono(26), 0.6) + 26
        if cx + wv > 1890:
            cx, cy = 1320, cy + 48
        mm = U.rect_mask(img.size, (cx, cy - 20, cx + wv, cy + 20), chamfer=5)
        img = U.over(img, U.NAVY, mm, 0.85)
        img = U.over(img, col, ImageChops.subtract(mm, SL.erode(mm, 1)), 0.8)
        U.text(img, (cx + 13, cy), words, mono(26), col, "lm", 0.6)
        cx += wv + 10
    img = jack_in(img, 1660, 1004, size=84)
    return img


# ---------------------------------------------------------------------------------------- Q11
# Designer ruling 2026-10-05 asked for examples before deciding Q11 (node verbs as stickers or chips).
# Every sticker word below is baked by the kit's own sticker code (ui31.sticker, as 4C baked its titles);
# the price never sits on the sticker (bible 1.2: values that change are never stickers): it is a gold
# terminal tag under it.
def node_card(img, box, title, rows, accent=None):
    """The Cell's own node as a CRT terminal (bible 1.2: the Cell's systems), cyan accent."""
    x0, y0, x1, y1 = box
    img = U.term_panel(img, box, title, accent=accent or U.CYAN, seed=51)
    yy = y0 + 54
    for a, b, col in rows:
        U.text(img, (x0 + 16, yy), a, mono(15), (130, 160, 190), "lm", 1.2)
        U.text(img, (x1 - 16, yy), b, mono(18), col or U.WHITE, "rm", 0.6)
        yy += 28
    return img, yy


def verb_slot(img, word, price, seed, cx=1716, cy=976):
    img = U.place(img, stk(word, 84, U.FILL_PINK, seed, True), cx, cy, angle=-3)
    return gold_price(img, cx, cy + 74, price.split(" ")[0])


def b_frame(shots, selected, tag_words=None):
    """Direction B's page with `selected` circled and the crew hand at rest (no runner lifted)."""
    img = base(shots, ((0.0, 0.2, 0.25, 0.42),))
    img = map_layer(img, selected=selected, raid=True, chips=False, select_circle=True, jack_link=False)
    img = top_bar(img)
    img = work_order(img, (26, 112), angle=-2.0, w=340, h=236)
    img = hand_tabs(img, 24, 856, active=0)
    xs = [380, 580, 780, 980]
    for k, op in enumerate(CREW):
        img = crew_card(img, xs[k], 966, op, angle=[-1.0, 1.5, -1.0, 2.0][k])
    if tag_words:
        c = N[selected]
        img = name_chip(img, (c[0] + 70, c[1] - 70), tag_words[0], col=tag_words[1], sub=tag_words[2])
    return img


def q11_claim(shots):
    img = b_frame(shots, "parcel", ("CLEARED  //  " + NAMES["parcel"], U.LIME, "CAN BE YOUR NODE"))
    box = (20, 430, 470, 840)
    img, yy = node_card(img, box, "CLAIM  //  PARCEL SORTING HALL", [("STATUS", "CLEARED (neutral)", None),
                                                                      ("LINK", "next to CUSTOMS PRE-CLEARANCE", None)])
    U.text(img, (box[0] + 16, yy + 2), "PICK THE NODE TO BUILD", mono(15), U.CYAN, "lm", 1.4)
    tiles = [("RELAY", "20", "ok"), ("FIREWALL RELAY", "30", "sel"), ("SAFEHOUSE", "20", "ok"),
             ("VAULT TERMINAL", "25", "ok"), ("PROXY RELAY", "25", "ok"), ("COMPILER RACK", "unlock 30", "lock")]
    for k, (n, p, st) in enumerate(tiles):
        x = box[0] + 16 + (k % 2) * 212
        y = yy + 26 + (k // 2) * 52
        state = {"ok": "idle", "sel": "pressed", "lock": "disabled"}[st]
        img = U.term_button(img, (x, y, x + 204, y + 44), n, p + ("" if st == "lock" else " SCHEM."), state)
    img = U.term_button(img, (box[0] + 16, box[3] - 58, box[2] - 16, box[3] - 14), "PATROL IT INSTEAD", "a full run, no objective", "idle")
    return verb_slot(img, "CLAIM", "30 SCHEMATICS", 81)


def q11_repair(shots):
    DOWN.add("customs")
    img = b_frame(shots, "customs", ("DOWN  //  " + NAMES["customs"], (240, 240, 240), "no bonus until repaired"))
    DOWN.discard("customs")
    box = (1452, 690, 1900, 900)
    img, yy = node_card(img, box, "CUSTOMS PRE-CLEARANCE", [("OWNER", "YOUR NODE", U.LIME),
        ("TYPE", "Firewall Relay (turret 3 dmg)", None), ("STATE", "DOWN", (240, 240, 240)),
        ("INTEGRITY", "0 / 30", U.HARM), ("RAID", "on route A: repair before it", U.HARM)])
    return verb_slot(img, "REPAIR", "15 SCHEMATICS", 82)


def q11_compare(shots):
    """UPGRADE (the Safehouse) and PATCH (CORE): as terminal chips on the node card (left) vs as the
    sticker in the verb slot (right)."""
    frames = []
    for key, title, rows, word, price, chip_words, chip_sub, seed in (
            ("returns", "RETURNS PROCESSING CENTRE",
             [("TYPE", "Safehouse (1 post)", None), ("POST", "NOVA (Ghost R1)", U.CYAN), ("LEVEL", "0  ->  1", None), ("INTEGRITY", "20 / 20", U.GREEN)],
             "UPGRADE", "30 SCHEMATICS", "UPGRADE  ->  LEVEL 1", "30 Schematics", 83),
            ("core", "CORE  //  YOUR HOME SERVER",
             [("TYPE", "Home server", None), ("INTEGRITY", "44 / 50", U.AMBER), ("AT 0", "the campaign is lost", U.HARM), ("PATCH", "1 Schematic a point", None)],
             "PATCH", "6 SCHEMATICS", "PATCH  +6  ->  50 / 50", "6 Schematics", 84)):
        for as_sticker in (False, True):
            img = b_frame(shots, key)
            box = (1452, 680, 1900, 910)
            img, yy = node_card(img, box, title, rows)
            if as_sticker:
                img = verb_slot(img, word, price, seed)
            else:
                img = U.term_button(img, (box[0] + 16, box[3] - 74, box[2] - 16, box[3] - 18), chip_words, chip_sub, "focus")
                U.text(img, (1716, 980), "(verb slot empty)", mono(16), (130, 150, 170), "mm", 0.4)
            cap = "%s as %s" % (word, "the STICKER in the verb slot" if as_sticker else "a TERMINAL CHIP on the node card")
            frames.append((cap, img))
    return strip(frames)


# ---------------------------------------------------------------------------------------- main
def save(img: Image.Image, out: Path, name: str, w: int = W) -> None:
    out.mkdir(parents=True, exist_ok=True)
    im = img.convert("RGB")
    if im.width != w:
        im = im.resize((w, round(w * im.height / im.width)), Image.LANCZOS)
    if name.endswith(".jpg"):
        im.save(out / name, quality=90, optimize=True)
    else:
        im.save(out / name, optimize=True)
    print("wrote", out / name)


def strip(frames, cols=2, w=960):
    h = round(w * H / W)
    cap = 40
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGBA", (w * cols + 10 * (cols - 1), (h + cap) * rows + 10 * (rows - 1)), (10, 10, 16, 255))
    for k, (words, f) in enumerate(frames):
        x, y = (k % cols) * (w + 10), (k // cols) * (h + cap + 10)
        sheet.alpha_composite(f.resize((w, h), Image.LANCZOS), (x, y + cap))
        U.text(sheet, (x + 10, y + cap / 2), words, U.F(U.MONO, 20), U.WHITE, "lm", 0.6)
    return sheet


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path)
    ap.add_argument("--shots", required=True, type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "docs" / "art_review" / "HQ_REDESIGN")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    load_kit(a.src)
    only = set(s for s in a.only.split(",") if s)

    def want(k):
        return not only or k in only

    if want("A"):
        save(direction_a(a.shots), a.out, "direction_A.png")
    if want("B"):
        save(direction_b(a.shots), a.out, "direction_B.png")
    if want("Bmarket"):
        save(direction_b(a.shots, "market"), a.out, "direction_B_market.jpg")
    if want("Braid"):
        save(direction_b(a.shots, "defence"), a.out, "direction_B_defence.jpg")
    if want("B20"):
        save(direction_b_text20(a.shots), a.out, "direction_B_text20.jpg")
    if want("C"):
        save(direction_c(a.shots, 0), a.out, "direction_C.png")
    if want("Ctabs"):
        frames = [("RUN (tab 1)", direction_c(a.shots, 0)), ("CREW (tab 2): your nodes lit, the rest dims", direction_c(a.shots, 1)),
                  ("MARKET (tab 3)", direction_c(a.shots, 2)), ("DEFEND (tab 4): the raid setup in place", direction_c(a.shots, 3))]
        save(strip(frames), a.out, "direction_C_tabs.jpg", 1920)
    if want("q11"):
        save(q11_claim(a.shots), a.out, "q11_a_claim.png")
        save(q11_repair(a.shots), a.out, "q11_b_repair.png")
        save(q11_compare(a.shots), a.out, "q11_c_upgrade_patch_chips_vs_stickers.png", 1920)
    if want("heat"):
        save(heat_board(a.shots), a.out, "heat_indicator.jpg")
    if want("flow"):
        frames = flow_board(a.shots)
        save(strip(frames), a.out, "jack_in_flow.jpg", 1920)
        gif = [f.convert("RGB").resize((960, 540), Image.LANCZOS) for _, f in frames]
        gif[0].save(a.out / "jack_in_flow.gif", save_all=True, append_images=gif[1:], duration=[1400, 1400, 1600, 2000], loop=0, optimize=True)
        print("wrote", a.out / "jack_in_flow.gif")


if __name__ == "__main__":
    main()
