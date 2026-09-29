"""Card illustration concepts (W4, ART_BIBLE 7.3; designer ruling Q6).

Draws one PIXEL-ART concept thumbnail per card effect family in the two-ink risograph
style of the final art: a key pass in INK and a spot pass in CELL_PINK, each screened as
pixel halftone dots, the spot pass two pixels off register, on photocopy paper. Each
thumbnail is 192x128 (the 768x512 master at a quarter), scaled x3 nearest-neighbour. Also
writes a labelled contact sheet. Deterministic (no randomness beyond a fixed hash).

These are concepts for the painted/printed finals only, never game assets.

    python tools/art_concepts/card_concepts.py            # -> docs/art_review/W4/concepts/

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import math
import os
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "art_review" / "W4" / "concepts"
W, H = 192, 128
SCALE = 3
# Palette tokens (scripts/ui/kit/palette.gd).
INK = (0x11, 0x11, 0x11)
PAPER_ALT = (0xE9, 0xE4, 0xD6)
CELL_PINK = (0xFF, 0x3D, 0xA8)
NIGHT_SKY = (0x06, 0x08, 0x16)
TEXT_MID = (0xAF, 0xC0, 0xD6)
MISREG = (2, 1)
# 4x4 clustered-dot threshold matrices (0..15): key at 45 degrees, spot at 0 degrees.
DOT_45 = [[12, 5, 6, 13], [4, 0, 1, 7], [11, 3, 2, 8], [15, 10, 9, 14]]
DOT_0 = [[15, 11, 7, 14], [10, 3, 2, 6], [9, 1, 0, 5], [13, 8, 4, 12]]

FAMILIES = ["spin", "spin_heavy", "backspin", "gear", "nudge", "jam", "inner_ring", "snap", "flip", "respin",
            "freeze", "strip", "breach", "damage", "arc", "overload", "block", "shield", "evade", "heal", "cleanse",
            "corrupt", "overclock", "encrypt", "parasite", "ram", "drain", "draw", "drone", "calibrate", "ring_lock",
            "steady", "undock", "amplify", "chip"]


def ihash(v: int) -> int:
    h = (v ^ 0x5BD1E995) & 0x7FFFFFFF
    h = ((h ^ (h >> 15)) * 0x2C1B3C6D) & 0x7FFFFFFF
    h = ((h ^ (h >> 12)) * 0x297A2D39) & 0x7FFFFFFF
    return (h ^ (h >> 15)) & 0x7FFFFFFF


class Plate:
    """Two tone plates (key, spot) drawn in unit space: x 0..1.5, y 0..1."""

    def __init__(self) -> None:
        self.key = Image.new("L", (W, H), 0)
        self.spot = Image.new("L", (W, H), 0)
        self.k = ImageDraw.Draw(self.key)
        self.s = ImageDraw.Draw(self.spot)

    @staticmethod
    def p(x: float, y: float) -> tuple[float, float]:
        return (x * H, y * H)

    def d(self, spot: bool) -> ImageDraw.ImageDraw:
        return self.s if spot else self.k

    def disc(self, cx, cy, r, tone=255, spot=False):
        self.d(spot).ellipse([(cx - r) * H, (cy - r) * H, (cx + r) * H, (cy + r) * H], fill=tone)

    def ring(self, cx, cy, r, w, tone=255, spot=False, a0=0.0, a1=360.0):
        box = [(cx - r) * H, (cy - r) * H, (cx + r) * H, (cy + r) * H]
        self.d(spot).arc(box, a0, a1, fill=tone, width=max(1, round(w * H)))

    def rect(self, x0, y0, x1, y1, tone=255, spot=False):
        self.d(spot).rectangle([x0 * H, y0 * H, x1 * H, y1 * H], fill=tone)

    def line(self, x0, y0, x1, y1, w, tone=255, spot=False):
        self.d(spot).line([self.p(x0, y0), self.p(x1, y1)], fill=tone, width=max(1, round(w * H)))

    def poly(self, pts, tone=255, spot=False):
        self.d(spot).polygon([self.p(x, y) for x, y in pts], fill=tone)

    def glow(self, cx, cy, r, tone, spot=True):
        for k in range(12, 0, -1):
            rr = r * k / 12
            self.disc(cx, cy, rr, round(tone * (1 - k / 12)) + 1, spot)

    def head(self, tx, ty, dx, dy, s, tone=255, spot=False):
        n = math.hypot(dx, dy) or 1
        dx, dy = dx / n, dy / n
        ox, oy = -dy, dx
        self.poly([(tx + dx * s * 0.3, ty + dy * s * 0.3), (tx - dx * s * 0.7 + ox * s * 0.55, ty - dy * s * 0.7 + oy * s * 0.55),
                   (tx - dx * s * 0.7 - ox * s * 0.55, ty - dy * s * 0.7 - oy * s * 0.55)], tone, spot)

    def arrow_arc(self, cx, cy, r, a0, a1, w, spot=False):
        self.ring(cx, cy, r, w, 255, spot, min(a0, a1), max(a0, a1))
        a = math.radians(a1)
        tx, ty = cx + math.cos(a) * r, cy + math.sin(a) * r
        sgn = 1 if a1 > a0 else -1
        self.head(tx, ty, -math.sin(a) * sgn, math.cos(a) * sgn, w * 3.2, 255, spot)

    def arrow(self, x0, y0, x1, y1, w, spot=False):
        self.line(x0, y0, x1, y1, w, 255, spot)
        self.head(x1, y1, x1 - x0, y1 - y0, w * 3.4, 255, spot)

    def wheel(self, cx, cy, r, n, rot, hi=0):
        step = 360 / n
        self.ring(cx, cy, r * 0.5, r * 0.62, 150, True, rot + hi * step, rot + (hi + 1) * step)
        self.ring(cx, cy, r, r * 0.09)
        for k in range(n):
            a = math.radians(rot + k * step)
            self.line(cx + math.cos(a) * r * 0.2, cy + math.sin(a) * r * 0.2, cx + math.cos(a) * r, cy + math.sin(a) * r, r * 0.05)
        self.disc(cx, cy, r * 0.2)
        self.disc(cx, cy, r * 0.09, 0)

    def bolt(self, x0, y0, x1, y1, n, amp, w, spot=False, k0=0):
        pts = []
        ox, oy = -(y1 - y0), (x1 - x0)
        ln = math.hypot(ox, oy) or 1
        ox, oy = ox / ln, oy / ln
        for k in range(n + 1):
            t = k / n
            side = 0 if k in (0, n) else (1 if k % 2 == 0 else -1) * amp * (0.6 + 0.8 * (ihash(k0 + k) % 100) / 100)
            pts.append((x0 + (x1 - x0) * t + ox * side, y0 + (y1 - y0) * t + oy * side))
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], w, 255, spot)

    def hexagon(self, cx, cy, r, tone=255, spot=False, rot=30):
        self.poly([(cx + math.cos(math.radians(rot + k * 60)) * r, cy + math.sin(math.radians(rot + k * 60)) * r) for k in range(6)], tone, spot)

    def burst(self, cx, cy, r0, r1, n, tone=255, spot=True):
        for k in range(n):
            a = 2 * math.pi * k / n
            b = a + math.pi / n
            self.poly([(cx + math.cos(a - 0.12) * r0, cy + math.sin(a - 0.12) * r0), (cx + math.cos(b) * r1, cy + math.sin(b) * r1),
                       (cx + math.cos(a + 0.12) * r0, cy + math.sin(a + 0.12) * r0)], tone, spot)
        self.disc(cx, cy, r0, tone, spot)

    def chip(self, cx, cy, s):
        for k in range(5):
            o = -s * 0.4 + k * s * 0.2
            self.line(cx + o, cy - s * 0.7, cx + o, cy + s * 0.7, s * 0.07)
            self.line(cx - s * 0.7, cy + o, cx + s * 0.7, cy + o, s * 0.07)
        self.rect(cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.5)
        self.rect(cx - s * 0.4, cy - s * 0.4, cx + s * 0.4, cy + s * 0.4, 0)
        self.rect(cx - s * 0.4, cy - s * 0.4, cx + s * 0.4, cy + s * 0.4, 130, True)
        self.rect(cx - s * 0.18, cy - s * 0.18, cx + s * 0.18, cy + s * 0.18)

    def lock(self, cx, cy, s):
        self.ring(cx, cy - s * 0.35, s * 0.32, s * 0.12, 255, False, 180, 360)
        self.line(cx - s * 0.32, cy - s * 0.35, cx - s * 0.32, cy - s * 0.1, s * 0.12)
        self.line(cx + s * 0.32, cy - s * 0.35, cx + s * 0.32, cy - s * 0.1, s * 0.12)
        self.rect(cx - s * 0.5, cy - s * 0.12, cx + s * 0.5, cy + s * 0.6)
        self.rect(cx - s * 0.42, cy - s * 0.04, cx + s * 0.42, cy + s * 0.52, 190, True)
        self.disc(cx, cy + s * 0.2, s * 0.1, 0)

    def card(self, cx, cy, w, rot, fill):
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        def quad(ww, hh):
            return [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-ww / 2, -hh / 2), (ww / 2, -hh / 2), (ww / 2, hh / 2), (-ww / 2, hh / 2))]
        self.poly(quad(w, w * 1.35))
        self.poly(quad(w * 0.84, w * 1.19), 0)
        self.poly(quad(w * 0.84, w * 1.19), fill, True)


def compose(p: Plate, fam: str) -> None:
    cx, cy = 0.75, 0.52
    p.glow(cx, cy, 0.7, 60)
    if fam == "spin":
        p.wheel(cx - 0.12, cy, 0.3, 6, 10, 1)
        p.arrow_arc(cx - 0.12, cy, 0.4, -140, 35, 0.05)
    elif fam == "spin_heavy":
        p.wheel(cx, cy, 0.3, 8, 0, 2)
        p.arrow_arc(cx, cy, 0.38, -160, 70, 0.06)
        p.arrow_arc(cx, cy, 0.46, -100, 125, 0.05, True)
    elif fam == "backspin":
        p.wheel(cx + 0.1, cy, 0.3, 6, 0, 4)
        p.arrow_arc(cx + 0.1, cy, 0.4, 45, -125, 0.05)
    elif fam == "gear":
        for g, (gx, gy, gr) in enumerate(((cx - 0.2, cy + 0.08, 0.2), (cx + 0.22, cy - 0.1, 0.16))):
            p.burst(gx, gy, gr * 0.85, gr * 1.18, 10, 255, False)
            p.disc(gx, gy, gr * 0.55, 0)
            p.disc(gx, gy, gr * 0.55, 170 if g == 0 else 90, True)
            p.disc(gx, gy, gr * 0.18)
    elif fam == "nudge":
        p.wheel(cx, cy + 0.12, 0.42, 10, -90, 0)
        for sd in (-1, 1):
            p.head(cx + sd * 0.34, cy - 0.3, sd, 0, 0.12)
            p.head(cx + sd * 0.46, cy - 0.3, sd, 0, 0.1, 220, True)
    elif fam == "jam":
        p.wheel(cx + 0.15, cy, 0.34, 8, 0, 3)
        p.line(cx - 0.55, cy + 0.34, cx + 0.05, cy - 0.12, 0.07)
        p.burst(cx + 0.06, cy - 0.14, 0.05, 0.16, 7)
    elif fam == "inner_ring":
        p.ring(cx, cy, 0.38, 0.05)
        p.ring(cx, cy, 0.24, 0.04)
        p.disc(cx, cy, 0.24, 180, True)
        p.arrow_arc(cx, cy, 0.3, -70, 57, 0.035)
        p.disc(cx, cy, 0.06)
    elif fam == "snap":
        p.wheel(cx, cy, 0.34, 6, 0, 0)
        p.ring(cx, cy - 0.2, 0.12, 0.03, 255, True)
        p.line(cx, cy - 0.46, cx, cy + 0.06, 0.02)
        p.line(cx - 0.16, cy - 0.2, cx + 0.16, cy - 0.2, 0.02)
    elif fam == "flip":
        p.ring(cx - 0.2, cy, 0.24, 0.05, 255, False, 90, 270)
        p.ring(cx + 0.2, cy, 0.24, 0.05, 255, False, -90, 90)
        p.disc(cx - 0.2, cy, 0.2, 160, True)
        p.line(cx, cy - 0.42, cx, cy + 0.42, 0.015)
        p.arrow(cx - 0.2, cy - 0.34, cx + 0.2, cy - 0.34, 0.03)
        p.arrow(cx + 0.2, cy + 0.34, cx - 0.2, cy + 0.34, 0.03)
    elif fam == "respin":
        for d, (dx, dy) in enumerate(((cx - 0.2, cy + 0.06), (cx + 0.16, cy - 0.12))):
            p.rect(dx - 0.14, dy - 0.14, dx + 0.14, dy + 0.14)
            p.rect(dx - 0.11, dy - 0.11, dx + 0.11, dy + 0.11, 0)
            p.rect(dx - 0.11, dy - 0.11, dx + 0.11, dy + 0.11, 120, True)
            for k in range(3 if d == 0 else 5):
                p.disc(dx - 0.06 + (k % 3) * 0.06, dy - 0.05 + (k // 3) * 0.1, 0.022)
        p.arrow_arc(cx, cy, 0.42, 205, 330, 0.035)
    elif fam == "freeze":
        for k in range(6):
            a = math.radians(k * 60)
            tx, ty = cx + math.cos(a) * 0.38, cy + math.sin(a) * 0.38
            p.line(cx, cy, tx, ty, 0.035)
            mx, my = cx + math.cos(a) * 0.24, cy + math.sin(a) * 0.24
            for sd in (-0.7, 0.7):
                p.line(mx, my, mx + math.cos(a + sd) * 0.12, my + math.sin(a + sd) * 0.12, 0.025)
        p.glow(cx, cy, 0.5, 200)
    elif fam == "strip":
        for k in range(4):
            o = k * 0.07
            p.rect(cx - 0.35 + o, cy - 0.28 + o, cx + 0.15 + o, cy + 0.04 + o, 255 if k == 0 else 150 - k * 25, k > 0)
            if k == 0:
                p.rect(cx - 0.32, cy - 0.25, cx + 0.12, cy + 0.01, 0)
        p.arrow(cx + 0.15, cy - 0.3, cx + 0.5, cy - 0.42, 0.03)
    elif fam == "breach":
        p.hexagon(cx, cy, 0.3)
        p.hexagon(cx, cy, 0.24, 0)
        p.hexagon(cx, cy, 0.24, 130, True)
        for k in range(5):
            a = math.radians(k * 72 + 10)
            p.bolt(cx, cy, cx + math.cos(a) * 0.46, cy + math.sin(a) * 0.46, 3, 0.04, 0.022, False, 100 + k * 10)
    elif fam == "damage":
        p.disc(cx + 0.25, cy + 0.05, 0.2)
        p.disc(cx + 0.25, cy + 0.05, 0.14, 0)
        p.disc(cx + 0.25, cy + 0.05, 0.06)
        p.bolt(cx - 0.55, cy - 0.38, cx + 0.2, cy + 0.02, 4, 0.08, 0.05, False, 120)
        p.burst(cx + 0.22, cy + 0.03, 0.1, 0.34, 12, 230)
    elif fam == "arc":
        nodes = [(cx - 0.45, cy + 0.2), (cx, cy - 0.25), (cx + 0.45, cy + 0.18)]
        for x, y in nodes:
            p.disc(x, y, 0.2, 130, True)
            p.disc(x, y, 0.1)
        for k, (a, b) in enumerate(zip(nodes, nodes[1:])):
            p.bolt(a[0], a[1], b[0], b[1], 5, 0.05, 0.022, False, 140 + k * 10)
    elif fam == "overload":
        p.rect(cx - 0.2, cy - 0.28, cx + 0.2, cy + 0.36)
        p.rect(cx - 0.14, cy - 0.22, cx + 0.14, cy + 0.3, 0)
        p.rect(cx - 0.14, cy - 0.22, cx + 0.14, cy + 0.3, 230, True)
        p.rect(cx - 0.07, cy - 0.35, cx + 0.07, cy - 0.28)
        p.bolt(cx - 0.06, cy - 0.15, cx + 0.04, cy + 0.2, 2, 0.06, 0.04, False, 190)
        p.arrow_arc(cx, cy + 0.05, 0.42, 23, 150, 0.03)
    elif fam == "block":
        for row in range(4):
            for col in range(4):
                bx = cx - 0.4 + col * 0.2 + (0.08 if row % 2 else 0)
                by = cy - 0.3 + row * 0.16
                if bx > cx + 0.4:
                    continue
                p.rect(bx, by, bx + 0.18, by + 0.14)
                p.rect(bx + 0.02, by + 0.02, bx + 0.16, by + 0.12, 0)
                p.rect(bx + 0.02, by + 0.02, bx + 0.16, by + 0.12, 70 + (ihash(row * 4 + col) % 110), True)
    elif fam == "shield":
        p.hexagon(cx, cy, 0.36, 255, False, 0)
        p.hexagon(cx, cy, 0.3, 0, False, 0)
        p.hexagon(cx, cy, 0.3, 160, True, 0)
        for k in range(3):
            a = math.radians(k * 60)
            p.line(cx + math.cos(a) * 0.3, cy + math.sin(a) * 0.3, cx - math.cos(a) * 0.3, cy - math.sin(a) * 0.3, 0.02)
    elif fam == "evade":
        for k in range(3):
            ex = cx - 0.3 + k * 0.24
            tone = 70 + k * 90
            p.disc(ex, cy - 0.26, 0.08, tone, k < 2)
            p.poly([(ex - 0.14, cy - 0.12), (ex + 0.12, cy - 0.12), (ex + 0.2, cy + 0.36), (ex - 0.08, cy + 0.36)], tone, k < 2)
        p.arrow(cx - 0.6, cy + 0.1, cx - 0.25, cy + 0.1, 0.025)
    elif fam == "heal":
        p.rect(cx - 0.3, cy - 0.13, cx + 0.3, cy + 0.13)
        p.rect(cx - 0.27, cy - 0.1, cx + 0.27, cy + 0.1, 0)
        p.rect(cx - 0.27, cy - 0.1, cx + 0.27, cy + 0.1, 110, True)
        p.rect(cx - 0.04, cy - 0.14, cx + 0.04, cy + 0.14)
        p.rect(cx - 0.14, cy - 0.04, cx + 0.14, cy + 0.04)
        for k in range(3):
            px, py = cx + 0.4 + k * 0.1, cy - 0.3 - (k % 2) * 0.06
            p.rect(px - 0.012, py - 0.04, px + 0.012, py + 0.04, 255, True)
            p.rect(px - 0.04, py - 0.012, px + 0.04, py + 0.012, 255, True)
    elif fam == "cleanse":
        p.rect(cx - 0.4, cy + 0.08, cx + 0.3, cy + 0.2, 210, True)
        p.rect(cx + 0.2, cy - 0.36, cx + 0.38, cy - 0.05)
        p.rect(cx + 0.16, cy - 0.42, cx + 0.3, cy - 0.36)
        for k in range(6):
            p.disc(cx - 0.05 - k * 0.08, cy - 0.34 + k * 0.035, 0.018)
    elif fam == "corrupt":
        for k in range(9):
            by = 0.1 + k * 0.09
            bx = 0.15 + (ihash(230 + k) % 70) / 100
            p.rect(bx, by, bx + 0.2 + (ihash(240 + k) % 50) / 100, by + 0.05, 255 if k % 3 == 0 else 200, k % 3 != 0)
        p.disc(cx, cy - 0.04, 0.16)
        p.disc(cx - 0.06, cy - 0.06, 0.04, 0)
        p.disc(cx + 0.06, cy - 0.06, 0.04, 0)
        p.rect(cx - 0.08, cy + 0.1, cx + 0.08, cy + 0.2)
    elif fam == "overclock":
        p.chip(cx, cy + 0.1, 0.36)
        for k in range(3):
            hx = cx - 0.12 + k * 0.12
            pts = [(hx + (0.03 if q % 2 == 0 else -0.03), cy - 0.16 - q * 0.05) for q in range(6)]
            for a, b in zip(pts, pts[1:]):
                p.line(a[0], a[1], b[0], b[1], 0.025, 255, True)
    elif fam == "encrypt":
        for k in range(7):
            for q in range(5):
                if ihash(250 + k * 5 + q) % 100 > 45:
                    p.rect(0.1 + k * 0.19, 0.1 + q * 0.18, 0.2 + k * 0.19, 0.2 + q * 0.18, 130, True)
        p.lock(cx, cy + 0.02, 0.36)
    elif fam == "parasite":
        p.ring(cx, cy + 0.1, 0.3, 0.2, 140, True, -137, -40)
        pts = [(cx - 0.45 + t / 11 * 0.9, cy + math.sin(t / 11 * 2 * math.pi * 1.5) * 0.12) for t in range(12)]
        for a, b in zip(pts, pts[1:]):
            p.line(a[0], a[1], b[0], b[1], 0.07)
        p.disc(pts[-1][0], pts[-1][1], 0.07)
    elif fam in ("ram", "drain"):
        y0 = -0.12 if fam == "ram" else -0.2
        p.rect(cx - 0.5, cy + y0, cx + 0.5, cy + y0 + 0.26)
        p.rect(cx - 0.46, cy + y0 + 0.04, cx + 0.46, cy + y0 + 0.22, 0)
        for k in range(4):
            p.rect(cx - 0.42 + k * 0.22, cy + y0 + 0.06, cx - 0.26 + k * 0.22, cy + y0 + 0.2, 230 - (k * 50 if fam == "drain" else 0), True)
        if fam == "ram":
            p.arrow(cx, cy - 0.44, cx, cy - 0.18, 0.035)
        else:
            p.disc(cx + 0.1, cy + 0.28, 0.06, 255, True)
            p.poly([(cx + 0.05, cy + 0.26), (cx + 0.1, cy + 0.12), (cx + 0.15, cy + 0.26)], 255, True)
    elif fam == "draw":
        for k in range(3):
            p.card(cx - 0.2 + k * 0.2, cy + 0.05, 0.24, -20 + k * 20, 50 + k * 60)
        p.arrow(cx + 0.45, cy + 0.3, cx + 0.45, cy - 0.3, 0.03)
    elif fam == "drone":
        p.rect(cx - 0.14, cy - 0.06, cx + 0.14, cy + 0.08)
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            rx, ry = cx + sx * 0.28, cy + sy * 0.2
            p.line(cx, cy, rx, ry, 0.03)
            p.disc(rx, ry, 0.1, 130, True)
            p.ring(rx, ry, 0.1, 0.02)
    elif fam == "calibrate":
        for k in range(13):
            tx = cx - 0.48 + k * 0.08
            p.line(tx, cy + 0.2, tx, cy + 0.2 - (0.14 if k % 4 == 0 else 0.07), 0.018)
        p.line(cx - 0.5, cy + 0.2, cx + 0.5, cy + 0.2, 0.025)
        p.poly([(cx, cy + 0.02), (cx - 0.06, cy - 0.14), (cx + 0.06, cy - 0.14)], 255, True)
        p.line(cx - 0.1, cy - 0.2, cx + 0.38, cy - 0.35, 0.06)
    elif fam == "ring_lock":
        p.ring(cx - 0.1, cy, 0.3, 0.06)
        p.ring(cx - 0.1, cy, 0.3, 0.14, 100, True)
        p.lock(cx + 0.5, cy + 0.1, 0.22)
    elif fam == "steady":
        p.ring(cx, cy, 0.3, 0.03)
        p.ring(cx, cy, 0.12, 0.02)
        p.line(cx - 0.42, cy, cx + 0.42, cy, 0.02)
        p.line(cx, cy - 0.42, cx, cy + 0.42, 0.02)
        p.disc(cx, cy, 0.1, 255, True)
        p.rect(cx - 0.4, cy + 0.34, cx + 0.4, cy + 0.44)
        p.disc(cx, cy + 0.39, 0.035, 255, True)
    elif fam == "undock":
        p.ring(cx - 0.15, cy + 0.05, 0.22, 0.04)
        p.disc(cx - 0.15, cy + 0.05, 0.08)
        p.ring(cx - 0.15, cy + 0.05, 0.38, 0.012, 255, True)
        p.disc(cx + 0.2, cy - 0.26, 0.07)
        p.arrow_arc(cx - 0.15, cy + 0.05, 0.46, -23, 52, 0.03)
    elif fam == "amplify":
        for k in range(3):
            ax = cx - 0.36 + k * 0.24
            p.head(ax + 0.14, cy, 1, 0, 0.34, 255 if k == 2 else 100 + k * 60, k < 2)
        p.ring(cx, cy, 0.42, 0.02, 180, False, -34, 34)
    else:
        p.chip(cx, cy, 0.42)


def screen(tone: int, x: int, y: int, mat) -> bool:
    return tone > 0 and (tone >= 240 or tone / 256 * 16 > mat[y % 4][x % 4] + 0.5)


def render(fam: str) -> Image.Image:
    p = Plate()
    compose(p, fam)
    out = Image.new("RGB", (W, H), PAPER_ALT)
    px = out.load()
    key, spot = p.key.load(), p.spot.load()
    seed = ihash(sum(map(ord, fam)))
    for y in range(H):
        streak = (ihash(y * 7919 + seed) % 1024) < 14
        for x in range(W):
            n = ihash(y * W + x + seed)
            g = (n & 15) - 8 - (10 if streak else 0)
            c = [max(0, min(255, v + g)) for v in PAPER_ALT]
            if (n >> 8) % 1024 < 4:
                c = list(INK)
            sx, sy = x - MISREG[0], y - MISREG[1]
            if 0 <= sx < W and 0 <= sy < H and screen(spot[sx, sy], x, y, DOT_0):
                c = [c[i] * CELL_PINK[i] // 255 for i in range(3)]
            if screen(key[x, y], x, y, DOT_45):
                c = list(INK)
            px[x, y] = tuple(c)
    return out.resize((W * SCALE, H * SCALE), Image.NEAREST)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for fam in FAMILIES:
        img = render(fam)
        img.save(OUT / f"{fam}.png", optimize=True)
        thumbs.append((fam, img))
    # Contact sheet: 5 columns of half-size thumbnails, labelled.
    cols = 5
    tw, th = W * SCALE // 2, H * SCALE // 2
    pad, label = 16, 22
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (pad + cols * (tw + pad), pad + rows * (th + label + pad) + 30), NIGHT_SKY)
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype(str(ROOT / "assets" / "fonts" / "ShareTechMono-Regular.ttf"), 16)
    except OSError:
        font = ImageFont.load_default()
    d.text((pad, 6), "W4 CARD ILLUSTRATION CONCEPTS  //  pixel-art riso, one per effect family  //  concepts only, never shipped", fill=TEXT_MID, font=font)
    for i, (fam, img) in enumerate(thumbs):
        x = pad + (i % cols) * (tw + pad)
        y = 30 + pad + (i // cols) * (th + label + pad)
        sheet.paste(img.resize((tw, th), Image.NEAREST), (x, y))
        d.text((x, y + th + 3), fam, fill=TEXT_MID, font=font)
    sheet.save(OUT / "contact_sheet.png", optimize=True)
    print(f"card_concepts: {len(thumbs)} concepts and a contact sheet in {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
