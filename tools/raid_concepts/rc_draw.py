"""Shared low-fidelity drawing kit for the raid concept mockups (raid design lab, 2026-10-22).

Every concept draws the same scenario (one Solace raid at Heat 50 against a six-node network) so the
critic compares designs, not content. Fidelity is low on purpose; the information layout is real.

SCRAMBLE (set by render_all.py --scramble) swaps every letter for a stable random letter, keeping
digits and math symbols, for the no-words test.
"""

from __future__ import annotations

import math
import random
import zlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
SCRAMBLE = False

# Palette. Threat cobalt is a designer ruling; the Cell is yellow; damage is red.
BG = (14, 16, 32)
BG2 = (22, 26, 48)
PANEL = (26, 30, 54)
PANEL_EDGE = (70, 80, 130)
INK = (232, 236, 245)
DIM = (140, 148, 175)
CELL = (255, 210, 63)
CELL_DIM = (130, 108, 40)
THREAT = (61, 107, 255)
THREAT_LIGHT = (140, 170, 255)
DMG = (255, 77, 77)
HOLD = (90, 220, 200)
DOWN_GREY = (110, 114, 128)
CORP = (61, 107, 255)
PENCIL = (255, 60, 60)
STAMP_HOLD = (255, 170, 40)
STAMP_CLEAN = (90, 220, 200)
STAMP_BREACH = (230, 40, 50)
HEAT = (255, 110, 40)

FONT_DIR = Path("C:/Windows/Fonts")
_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(size: int, kind: str = "ui") -> ImageFont.FreeTypeFont:
    name = {"ui": "bahnschrift.ttf", "mono": "consolab.ttf", "stamp": "impact.ttf", "hand": "segoeprb.ttf"}[kind]
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(str(FONT_DIR / name), size)
    return _font_cache[key]


_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def scramble(s: str) -> str:
    if not SCRAMBLE:
        return s
    rng = random.Random(zlib.crc32(s.encode("utf-8")))
    out = []
    for ch in s:
        if ch.isalpha():
            c = rng.choice(_LETTERS)
            out.append(c if ch.isupper() else c.lower())
        else:
            out.append(ch)
    return "".join(out)


def new_frame(title: str, moment: str) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for x in range(0, W, 40):
        d.line([(x, 0), (x, H)], fill=(18, 21, 40))
    for y in range(0, H, 40):
        d.line([(0, y), (W, y)], fill=(18, 21, 40))
    return img, d


def text(d: ImageDraw.ImageDraw, xy, s: str, size: int = 18, fill=INK, kind: str = "ui", anchor: str = "la") -> None:
    d.text(xy, scramble(s), font=font(size, kind), fill=fill, anchor=anchor)


def text_w(s: str, size: int = 18, kind: str = "ui") -> int:
    return int(font(size, kind).getlength(scramble(s)))


def panel(d, box, fill=PANEL, edge=PANEL_EDGE, width: int = 2, r: int = 8) -> None:
    d.rounded_rectangle(box, radius=r, fill=fill, outline=edge, width=width)


def label_tag(d, xy, s: str, fg=BG, bg=CELL, size: int = 14) -> None:
    x, y = xy
    w = text_w(s, size) + 12
    d.rounded_rectangle((x, y, x + w, y + size + 8), radius=4, fill=bg)
    text(d, (x + 6, y + 3), s, size, fg)


# --- Heat HUD -------------------------------------------------------------------------------------

def heat_bar(d, x: int, y: int, w: int, heat: int, marks=(25, 50, 75, 100), raid_at: int | None = 50, label: bool = True) -> None:
    """Top HUD Heat meter with threshold notches; the crossed threshold gets a cobalt raid tooth."""
    h = 16
    d.rounded_rectangle((x, y, x + w, y + h), radius=6, fill=(40, 30, 30), outline=(110, 70, 50), width=2)
    fw = int(w * heat / 100)
    d.rounded_rectangle((x, y, x + fw, y + h), radius=6, fill=HEAT)
    for m in marks:
        mx = x + int(w * m / 100)
        d.line([(mx, y - 4), (mx, y + h + 4)], fill=INK, width=2)
        if raid_at is not None and m == raid_at:
            shield(d, (mx, y + h + 18), 10, THREAT)
    if label:
        flame(d, (x - 18, y + 8), 9, HEAT)
        text(d, (x + w + 10, y - 2), f"{heat}", 20, HEAT, "mono")


def flame(d, c, r, col) -> None:
    x, y = c
    d.polygon([(x, y - r * 1.4), (x + r, y + r * 0.3), (x + r * 0.5, y + r), (x - r * 0.5, y + r), (x - r, y + r * 0.3)], fill=col)


def shield(d, c, r, col, outline=INK) -> None:
    """Corporate raid glyph: a cobalt shield with a notch."""
    x, y = c
    pts = [(x - r, y - r), (x + r, y - r), (x + r, y), (x, y + r * 1.3), (x - r, y)]
    d.polygon(pts, fill=col, outline=outline)
    d.line([(x, y - r + 3), (x, y + r * 0.8)], fill=outline, width=2)


# --- Network map ---------------------------------------------------------------------------------

# Base positions in a 760 x 520 map space; concepts map them with a transform.
NODES = {
    "HOME": (110, 260),
    "FW": (300, 140),
    "VAULT": (330, 290),
    "SAFE": (290, 440),
    "RELAY": (510, 150),
    "PROXY": (520, 400),
    "C1": (710, 80),
    "C2": (720, 470),
}
NODE_NAME = {
    "HOME": "HOME SERVER", "FW": "FIREWALL", "VAULT": "VAULT", "SAFE": "SAFEHOUSE",
    "RELAY": "RELAY", "PROXY": "PROXY", "C1": "SOLACE CLINIC", "C2": "SOLACE DEPOT",
}
NODE_HP = {"HOME": 50, "FW": 30, "VAULT": 20, "SAFE": 20, "RELAY": 15, "PROXY": 15}
LINKS = [("HOME", "FW"), ("HOME", "VAULT"), ("HOME", "SAFE"), ("FW", "RELAY"), ("VAULT", "RELAY"),
         ("VAULT", "PROXY"), ("SAFE", "PROXY"), ("RELAY", "C1"), ("PROXY", "C2")]


class MapXf:
    def __init__(self, ox: int, oy: int, s: float = 1.0):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, key_or_xy):
        x, y = NODES[key_or_xy] if isinstance(key_or_xy, str) else key_or_xy
        return (self.ox + x * self.s, self.oy + y * self.s)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def draw_links(d, xf: MapXf, dim: bool = False) -> None:
    for a, b in LINKS:
        col = (70, 64, 40) if dim else CELL_DIM
        if a.startswith("C") or b.startswith("C"):
            col = (40, 50, 90)
        d.line([xf.p(a), xf.p(b)], fill=col, width=4)


def dashed(d, a, b, col, width=5, dash=14, gap=9) -> None:
    L = math.dist(a, b)
    n = max(1, int(L // (dash + gap)))
    for i in range(n + 1):
        t0 = i * (dash + gap) / L
        t1 = min(1.0, (i * (dash + gap) + dash) / L)
        if t0 >= 1:
            break
        d.line([lerp(a, b, t0), lerp(a, b, t1)], fill=col, width=width)


def arrow(d, a, b, col, width=6, head=16, dash_line: bool = False, shorten: float = 30) -> None:
    L = math.dist(a, b)
    if L < 1:
        return
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    a2 = (a[0] + ux * shorten, a[1] + uy * shorten)
    b2 = (b[0] - ux * shorten, b[1] - uy * shorten)
    if dash_line:
        dashed(d, a2, b2, col, width)
    else:
        d.line([a2, b2], fill=col, width=width)
    px, py = -uy, ux
    tip = b2
    base = (tip[0] - ux * head, tip[1] - uy * head)
    d.polygon([tip, (base[0] + px * head * 0.6, base[1] + py * head * 0.6), (base[0] - px * head * 0.6, base[1] - py * head * 0.6)], fill=col)


def route(d, xf: MapXf, keys: list[str], col=THREAT, width=7, dash_line: bool = False) -> None:
    for a, b in zip(keys, keys[1:]):
        arrow(d, xf.p(a), xf.p(b), col, width, dash_line=dash_line)


def node_icon(d, c, kind: str, r: float, col) -> None:
    """Primitive pictograms per node type, readable without words."""
    x, y = c
    k = r * 0.5
    if kind == "HOME":
        d.polygon([(x - k, y), (x, y - k * 1.1), (x + k, y)], fill=col)
        d.rectangle((x - k * 0.75, y, x + k * 0.75, y + k * 0.9), fill=col)
        d.rectangle((x - k * 0.2, y + k * 0.35, x + k * 0.2, y + k * 0.9), fill=BG)
    elif kind == "FW":
        for row in range(3):
            yy = y - k + row * k * 0.7
            off = (row % 2) * k * 0.4
            for i in range(-1, 2):
                xx = x + i * k * 0.8 + off - k * 0.2
                d.rectangle((xx - k * 0.35, yy, xx + k * 0.35, yy + k * 0.55), fill=col)
    elif kind == "VAULT":
        d.rectangle((x - k, y - k * 0.8, x + k, y + k * 0.9), outline=col, width=4)
        d.ellipse((x - k * 0.4, y - k * 0.35, x + k * 0.4, y + k * 0.45), outline=col, width=3)
    elif kind == "SAFE":
        d.rectangle((x - k * 0.6, y - k, x + k * 0.6, y + k), outline=col, width=4)
        d.ellipse((x + k * 0.15, y - k * 0.1, x + k * 0.4, y + k * 0.15), fill=col)
    elif kind == "RELAY":
        d.line([(x, y + k), (x, y - k * 0.4)], fill=col, width=4)
        for rr in (k * 0.6, k * 1.0):
            d.arc((x - rr, y - k * 0.4 - rr, x + rr, y - k * 0.4 + rr), 220, 320, fill=col, width=3)
    elif kind == "PROXY":
        d.ellipse((x - k, y - k * 0.6, x, y + k * 0.4), outline=col, width=3)
        d.ellipse((x, y - k * 0.6, x + k, y + k * 0.4), outline=col, width=3)
    elif kind in ("C1", "C2"):
        shield(d, (x, y - 2), k * 0.9, CORP)


def hp_pips(d, x, y, hp: int, max_hp: int, lose: int = 0, per: int = 5, w: int = 8, col=HOLD) -> int:
    """Integrity as pips of `per` points; the last `lose` points are striped red (projected loss)."""
    n = math.ceil(max_hp / per)
    full = math.ceil(hp / per)
    lost_to = math.ceil(max(0, hp - lose) / per)
    total_w = n * (w + 2)
    x0 = x - total_w / 2
    for i in range(n):
        bx = x0 + i * (w + 2)
        box = (bx, y, bx + w, y + 10)
        if i < lost_to:
            d.rectangle(box, fill=col)
        elif i < full:
            d.rectangle(box, fill=(70, 20, 20))
            for sx in range(0, w + 10, 4):
                d.line([(bx + sx, y + 10), (bx + sx - 6, y)], fill=DMG, width=2)
            d.rectangle(box, outline=DMG)
        else:
            d.rectangle(box, outline=(60, 64, 80))
    return int(total_w)


def node(d, xf: MapXf, key: str, state: str = "ok", hp: int | None = None, lose: int = 0, r: float = 30,
         show_name: bool = True, show_hp: bool = True, highlight=None) -> None:
    """A network node. state: ok | down | taken | corp. HOLDS/DOWN/TAKEN marks are drawn by the caller."""
    c = xf.p(key)
    x, y = c
    if key.startswith("C"):
        d.regular_polygon((x, y, r * 1.05), 6, fill=(20, 30, 70), outline=CORP, width=3)
        node_icon(d, c, key, r, CORP)
        if show_name:
            text(d, (x, y + r + 6), NODE_NAME[key], 13, THREAT_LIGHT, anchor="ma")
        return
    fill = (34, 36, 58)
    edge = CELL
    icol = CELL
    if state == "down":
        fill, edge, icol = (48, 50, 58), DOWN_GREY, DOWN_GREY
    if state == "taken":
        fill, edge, icol = (20, 30, 70), CORP, THREAT_LIGHT
    if highlight is not None:
        d.ellipse((x - r - 9, y - r - 9, x + r + 9, y + r + 9), outline=highlight, width=4)
    d.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=edge, width=4)
    node_icon(d, c, key, r, icol)
    if state == "down":
        bolt(d, (x, y), r * 0.9)
    if show_name:
        text(d, (x, y + r + 20), NODE_NAME[key], 13, DIM if state != "ok" else INK, anchor="ma")
    if show_hp and key in NODE_HP:
        hp_pips(d, x, y + r + 5, NODE_HP[key] if hp is None else hp, NODE_HP[key], lose,
                w=6 if NODE_HP[key] > 30 else 8)


def bolt(d, c, r, col=INK) -> None:
    x, y = c
    pts = [(x + r * 0.15, y - r), (x - r * 0.45, y + r * 0.1), (x - r * 0.02, y + r * 0.1), (x - r * 0.2, y + r),
           (x + r * 0.45, y - r * 0.15), (x + r * 0.02, y - r * 0.15)]
    d.polygon(pts, fill=col, outline=BG)


def pencil_x(d, c, r, col=PENCIL, seed: int = 1) -> None:
    """Grease-pencil X (D28 TAKEN mark): two jittered strokes."""
    rng = random.Random(seed)
    x, y = c
    for (ax, ay, bx, by) in ((-r, -r, r, r), (r, -r, -r, r)):
        for k in range(3):
            j = lambda: rng.uniform(-3, 3)
            d.line([(x + ax + j(), y + ay + j()), (x + bx + j(), y + by + j())], fill=col, width=5 - k)


def pencil_circle(d, c, r, col=PENCIL, seed: int = 2, width: int = 4) -> None:
    rng = random.Random(seed)
    x, y = c
    pts = []
    for i in range(38):
        a = i / 34 * 2 * math.pi
        rr = r + rng.uniform(-3, 3)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.92))
    d.line(pts, fill=col, width=width)


def mark(d, xf: MapXf, key: str, verdict: str, r: float = 30) -> None:
    """Per-node outcome tag above a node: HOLDS (teal check), DOWN (bolt chip), TAKEN (cobalt flag + pencil X)."""
    x, y = xf.p(key)
    ty = y - r - 30
    if verdict == "HOLDS":
        d.rounded_rectangle((x - 34, ty, x + 34, ty + 22), radius=5, fill=(20, 60, 60), outline=HOLD, width=2)
        check(d, (x - 22, ty + 11), 7, HOLD)
        text(d, (x + 6, ty + 3), "HOLDS", 14, HOLD, anchor="ma")
    elif verdict == "DOWN":
        d.rounded_rectangle((x - 34, ty, x + 34, ty + 22), radius=5, fill=(50, 50, 58), outline=INK, width=2)
        bolt(d, (x - 22, ty + 11), 9)
        text(d, (x + 6, ty + 3), "DOWN", 14, INK, anchor="ma")
    elif verdict == "TAKEN":
        d.rounded_rectangle((x - 38, ty, x + 38, ty + 22), radius=5, fill=(20, 30, 80), outline=THREAT_LIGHT, width=2)
        flag(d, (x - 26, ty + 11), 8, THREAT_LIGHT)
        text(d, (x + 6, ty + 3), "TAKEN", 14, THREAT_LIGHT, anchor="ma")
        pencil_x(d, (x, y), r * 0.9, seed=hash(key) & 0xFF)


def check(d, c, r, col) -> None:
    x, y = c
    d.line([(x - r, y), (x - r * 0.3, y + r * 0.7), (x + r, y - r * 0.8)], fill=col, width=4)


def flag(d, c, r, col) -> None:
    x, y = c
    d.line([(x - r * 0.6, y + r), (x - r * 0.6, y - r)], fill=col, width=3)
    d.polygon([(x - r * 0.6, y - r), (x + r, y - r * 0.5), (x - r * 0.6, y)], fill=col)


# --- Threat silhouettes ---------------------------------------------------------------------------

THREATS = {
    # id: name, integrity, damage, speed, routing, entry, target, silhouette
    "COLLECTOR": ("COLLECTOR", 12, 5, 1, "shortest to home", "C1", "HOME"),
    "AUDITOR": ("AUDITOR", 8, 3, 2, "richest node", "C2", "VAULT"),
    "ENFORCER": ("ENFORCER", 25, 9, 1, "weakest node", "C2", "PROXY"),
    "LOCKDOWN": ("LOCKDOWN", 18, 6, 1, "weakest node", "C1", "PROXY"),
    "COURIER": ("COURIER", 8, 3, 2, "richest node", "C2", "VAULT"),
    "INSPECTOR": ("INSPECTOR", 10, 4, 2, "richest node", "C1", "VAULT"),
    "BAILIFF": ("BAILIFF", 30, 10, 1, "weakest node", "C2", "PROXY"),
    "HAULER": ("HAULER", 28, 10, 1, "weakest node", "C1", "PROXY"),
}


def threat(d, c, tid: str, r: float = 20, hp: int | None = None, show_hp: bool = True, col=THREAT, ghost: bool = False) -> None:
    """Threat silhouettes, distinct by shape: Collector = hook claw, Auditor = eye diamond, Enforcer = heavy spiked block."""
    x, y = c
    fill = (20, 28, 60) if ghost else col
    edge = col if ghost else INK
    if tid == "COLLECTOR":
        d.rounded_rectangle((x - r, y - r * 0.8, x + r, y + r * 0.8), radius=5, fill=fill, outline=edge, width=3)
        d.arc((x - r * 0.6, y - r * 0.5, x + r * 0.4, y + r * 0.6), 200, 90, fill=edge, width=4)
        d.polygon([(x + r * 0.4, y + r * 0.05), (x + r * 0.7, y - r * 0.2), (x + r * 0.55, y + r * 0.3)], fill=edge)
    elif tid == "AUDITOR":
        d.polygon([(x, y - r * 1.1), (x + r * 1.1, y), (x, y + r * 1.1), (x - r * 1.1, y)], fill=fill, outline=edge, width=3)
        d.ellipse((x - r * 0.5, y - r * 0.3, x + r * 0.5, y + r * 0.3), outline=edge, width=3)
        d.ellipse((x - r * 0.15, y - r * 0.15, x + r * 0.15, y + r * 0.15), fill=edge)
    elif tid == "ENFORCER":
        R = r * 1.25
        d.polygon([(x - R, y - R * 0.6), (x - R * 0.5, y - R), (x + R * 0.5, y - R), (x + R, y - R * 0.6),
                   (x + R, y + R * 0.5), (x, y + R), (x - R, y + R * 0.5)], fill=fill, outline=edge, width=3)
        for sx in (-0.5, 0, 0.5):
            d.polygon([(x + R * sx - 5, y - R), (x + R * sx, y - R - 9), (x + R * sx + 5, y - R)], fill=edge)
        d.rectangle((x - R * 0.5, y - R * 0.15, x + R * 0.5, y + R * 0.1), fill=edge)
    elif tid == "COURIER":
        # Courier: a dart (fast, fragile)
        d.polygon([(x + r * 1.2, y), (x - r, y - r * 0.8), (x - r * 0.4, y), (x - r, y + r * 0.8)], fill=fill, outline=edge, width=3)
    elif tid == "INSPECTOR":
        # Inspector: a magnifier
        d.ellipse((x - r * 0.9, y - r * 0.9, x + r * 0.5, y + r * 0.5), fill=fill, outline=edge, width=3)
        d.line([(x + r * 0.35, y + r * 0.35), (x + r * 1.05, y + r * 1.05)], fill=edge, width=5)
    elif tid in ("BAILIFF", "HAULER"):
        # Bailiff / Hauler: an armored truck (the bailiff with a clamp jaw)
        d.rounded_rectangle((x - r * 1.2, y - r * 0.7, x + r * 0.6, y + r * 0.5), radius=3, fill=fill, outline=edge, width=3)
        d.rectangle((x + r * 0.6, y - r * 0.3, x + r * 1.2, y + r * 0.5), fill=fill, outline=edge, width=3)
        for wx in (-0.7, 0.7):
            d.ellipse((x + r * wx - r * 0.3, y + r * 0.4, x + r * wx + r * 0.3, y + r * 1.0), fill=edge)
        if tid == "BAILIFF":
            d.polygon([(x + r * 1.2, y - r * 0.6), (x + r * 1.6, y - r * 0.9), (x + r * 1.6, y + r * 0.1)], fill=edge)
    elif tid == "LOCKDOWN":
        # Lockdown Unit: a padlock block (it freezes a home link)
        d.rounded_rectangle((x - r, y - r * 0.4, x + r, y + r), radius=4, fill=fill, outline=edge, width=3)
        d.arc((x - r * 0.6, y - r * 1.1, x + r * 0.6, y + r * 0.2), 180, 360, fill=edge, width=4)
        d.ellipse((x - r * 0.18, y + r * 0.1, x + r * 0.18, y + r * 0.46), fill=edge)
    if show_hp:
        name, mhp, *_ = THREATS[tid]
        hpv = mhp if hp is None else hp
        hp_pips(d, x, y + r * 1.4 + 4, hpv, mhp, per=4 if mhp <= 12 else 5, w=7, col=THREAT_LIGHT)


def swords(d, c, r, col=DMG) -> None:
    """Attack intent glyph."""
    x, y = c
    d.line([(x - r, y + r), (x + r, y - r)], fill=col, width=4)
    d.line([(x + r, y + r), (x - r, y - r)], fill=col, width=4)
    d.line([(x - r * 0.9, y - r * 0.3), (x - r * 0.3, y - r * 0.9)], fill=col, width=3)
    d.line([(x + r * 0.9, y - r * 0.3), (x + r * 0.3, y - r * 0.9)], fill=col, width=3)


def dmg_badge(d, c, n: int, col=DMG, size: int = 20) -> None:
    x, y = c
    s = f"-{n}"
    w = text_w(s, size, "mono") + 14
    d.rounded_rectangle((x - w / 2, y - size / 2 - 4, x + w / 2, y + size / 2 + 4), radius=6, fill=col)
    text(d, (x, y - size / 2 - 1), s, size, INK, "mono", anchor="ma")


def order_badge(d, c, n: int, col=THREAT) -> None:
    x, y = c
    d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=INK, outline=col, width=3)
    text(d, (x, y - 10), str(n), 18, BG, "mono", anchor="ma")


# --- Defense assets -------------------------------------------------------------------------------

ASSETS = {"TURRET": ("TURRET", "4 dmg, reach 1"), "ICE": ("ICE LOCK", "hold 2 steps"), "DECOY": ("DECOY", "pull threats"),
          "CREW": ("BREAKER", "+3 dmg on node")}


def asset_icon(d, c, aid: str, r: float, col=CELL) -> None:
    x, y = c
    if aid == "TURRET":
        d.ellipse((x - r, y - r, x + r, y + r), outline=col, width=3)
        d.line([(x - r - 4, y), (x + r + 4, y)], fill=col, width=3)
        d.line([(x, y - r - 4), (x, y + r + 4)], fill=col, width=3)
    elif aid == "ICE":
        for a in range(3):
            ang = a * math.pi / 3
            d.line([(x - math.cos(ang) * r, y - math.sin(ang) * r), (x + math.cos(ang) * r, y + math.sin(ang) * r)], fill=col, width=3)
    elif aid == "DECOY":
        d.arc((x - r * 0.7, y - r, x + r * 0.7, y + r * 0.4), 180, 360, fill=col, width=4)
        d.line([(x + r * 0.7, y - r * 0.3), (x + r * 0.7, y + r * 0.6)], fill=col, width=4)
        d.line([(x - r * 0.7, y - r * 0.3), (x - r * 0.7, y + r)], fill=col, width=4)
        d.arc((x - r * 0.7 - r * 0.5, y + r * 0.5, x - r * 0.7 + r * 0.5, y + r * 1.3), 0, 180, fill=col, width=4)
    elif aid == "CREW":
        d.ellipse((x - r * 0.45, y - r, x + r * 0.45, y - r * 0.1), fill=col)
        d.pieslice((x - r * 0.9, y - r * 0.05, x + r * 0.9, y + r * 1.6), 180, 360, fill=col)


def asset_card(d, x, y, aid: str, count: int = 1, w: int = 96, h: int = 120, selected: bool = False, used: bool = False) -> None:
    edge = CELL if selected else PANEL_EDGE
    fill = (50, 46, 30) if selected else PANEL
    if used:
        fill, edge = (24, 26, 40), (50, 54, 70)
    d.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=edge, width=3 if selected else 2)
    asset_icon(d, (x + w / 2, y + 40), aid, 18, CELL if not used else DIM)
    name, eff = ASSETS[aid]
    text(d, (x + w / 2, y + 72), name, 14, INK if not used else DIM, anchor="ma")
    text(d, (x + w / 2, y + 92), eff, 11, DIM, anchor="ma")
    if count > 1:
        text(d, (x + w - 8, y + 6), f"x{count}", 13, CELL, "mono", anchor="ra")


# --- Stamps & chrome ------------------------------------------------------------------------------

def stamp(img: Image.Image, c, s: str, col, size: int = 64, angle: float = -8, sub: str | None = None) -> None:
    f = font(size, "stamp")
    s2 = scramble(s)
    tw = int(f.getlength(s2))
    sub2 = scramble(sub) if sub else None
    fs = font(int(size * 0.34), "ui")
    sw = int(fs.getlength(sub2)) if sub2 else 0
    bw = max(tw, sw) + 50
    bh = size + 40 + (int(size * 0.45) if sub else 0)
    layer = Image.new("RGBA", (bw + 20, bh + 20), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle((10, 10, bw + 10, bh + 10), radius=10, outline=col, width=7)
    ld.text((10 + bw / 2, 22), s2, font=f, fill=col, anchor="ma")
    if sub2:
        ld.text((10 + bw / 2, 26 + size), sub2, font=fs, fill=col, anchor="ma")
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    img.paste(layer, (int(c[0] - layer.width / 2), int(c[1] - layer.height / 2)), layer)


def header(d, concept: str, moment_no: int, moment: str) -> None:
    """Thin mockup strip at the bottom: concept and moment. Kept outside the game UI area."""
    d.rectangle((0, H - 26, W, H), fill=(8, 9, 18))
    text(d, (12, H - 21), f"{concept}   |   {moment_no}/5  {moment}", 14, DIM)


def button(d, box, s: str, primary: bool = True, size: int = 18) -> None:
    fill = CELL if primary else PANEL
    fg = BG if primary else INK
    d.rounded_rectangle(box, radius=6, fill=fill, outline=CELL, width=2)
    text(d, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - size / 2 - 1), s, size, fg, anchor="ma")


def speed_controls(d, x, y) -> None:
    for i, s in enumerate(("1x", "2x", "4x", ">>|")):
        d.rounded_rectangle((x + i * 50, y, x + i * 50 + 44, y + 28), radius=5, fill=PANEL if i else (60, 56, 30),
                            outline=CELL if i == 0 else PANEL_EDGE, width=2)
        text(d, (x + i * 50 + 22, y + 5), s, 15, INK, "mono", anchor="ma")


def step_track(d, x, y, w, steps: int, now: int, label: str = "STEP") -> None:
    """Step-locked playout ruler (D26)."""
    text(d, (x, y - 22), label, 13, DIM)
    seg = w / steps
    for i in range(steps):
        col = CELL if i < now else (50, 54, 80)
        d.rectangle((x + i * seg + 2, y, x + (i + 1) * seg - 2, y + 10), fill=col)
    text(d, (x + w + 10, y - 5), f"{now}/{steps}", 16, CELL, "mono")


def save(img: Image.Image, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
