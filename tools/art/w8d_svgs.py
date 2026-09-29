"""Art pass W8d: writes the campaign end's baked vector art (ART_BIBLE 11 Campaign end, 3.6,
4.3 rule 5, 7.4 grammar).

    python tools/art/w8d_svgs.py

Deterministic (no randomness: a fixed integer hash places the overspray), original shapes,
no text. Every file is drawn in white and greys on clear, tinted at runtime (modulate), so
one file serves the normal look, high contrast and the colour-blind filter:

- assets/art/campaign_end/landmark_<corp>.svg  each corporation's landmark as a large
      silhouette (200x300; ground at the bottom): white body, grey shading and cut detail
      (a darker shade of the corp hue once tinted). The shape alone names the corp in
      greyscale (3.6): solace = DNA helix tower, meridian = container crane, halcyon = clock
      tower, orbital = satellite dish, rebel_cell = the inverted Cell hexagon.
- assets/art/campaign_end/cell_hex_left.svg / cell_hex_right.svg  the Cell's own hexagon
      (a pointy hexagon ring with the upward chevron: the landmark glyph's Cell mark, the
      right way up) cut along its crack into two halves that part when it breaks.
- assets/art/campaign_end/cell_hex_crack.svg   the crack itself (a jagged split with
      branches), drawn over the halves in INK and revealed from the top.
- assets/art/campaign_end/spray_x.svg          the overspray round a spray-can X (speckle
      and drips); the X's two strokes are drawn by the marker_stroke shader, this texture
      settles in after them.

Written as a file on purpose: never run Python from stdin on this machine.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "art" / "campaign_end"

WHITE = "#FFFFFF"
# Shades: the body is white; these become darker shades of the tint.
SHADE = "#9C9C9C"
DEEP = "#5A5A5A"
LIGHT = "#D2D2D2"

LANDMARK_W = 200
LANDMARK_H = 300
GROUND = 296


def jit(n: int, salt: int, amp: float) -> float:
    """A fixed hash in [-amp, amp] (the same every run)."""
    h = (n * 2654435761 + salt * 40503) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 1274126177) & 0xFFFFFFFF
    return ((h & 0xFFFF) / 0xFFFF * 2.0 - 1.0) * amp


def svg(w: int, h: int, comment: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f"  <!-- {comment} -->\n{body}</svg>\n")


def pts(points) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in points)


def plinth(x0: float, x1: float, step: float = 12.0) -> str:
    """A two-step plinth on the ground line."""
    return (f'  <rect x="{x0:.1f}" y="{GROUND - 10}" width="{x1 - x0:.1f}" height="10" fill="{WHITE}"/>\n'
            f'  <rect x="{x0 + step:.1f}" y="{GROUND - 20}" width="{x1 - x0 - step * 2:.1f}" height="10" fill="{LIGHT}"/>\n')


# --- The five landmarks -------------------------------------------------------------------

def solace() -> str:
    cx, amp, top, bottom = 100.0, 44.0, 34.0, 262.0
    turns = 2.25
    front, back, rungs = [], [], []
    n = 90
    for i in range(n + 1):
        t = i / n
        y = top + (bottom - top) * t
        a = t * turns * math.tau
        front.append((cx + math.sin(a) * amp, y))
        back.append((cx - math.sin(a) * amp, y))
    for k in range(1, 20):
        t = k / 20
        y = top + (bottom - top) * t
        a = t * turns * math.tau
        rungs.append(((cx + math.sin(a) * amp, y), (cx - math.sin(a) * amp, y)))
    body = plinth(44, 156)
    body += f'  <rect x="84" y="{bottom - 4:.1f}" width="32" height="{GROUND - 20 - bottom + 4:.1f}" fill="{WHITE}"/>\n'
    for (a, b) in rungs:
        body += f'  <line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{SHADE}" stroke-width="7" stroke-linecap="round"/>\n'
    body += f'  <polyline points="{pts(back)}" fill="none" stroke="{LIGHT}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round"/>\n'
    body += f'  <polyline points="{pts(front)}" fill="none" stroke="{WHITE}" stroke-width="17" stroke-linecap="round" stroke-linejoin="round"/>\n'
    body += f'  <circle cx="{cx}" cy="{top - 14}" r="13" fill="{WHITE}"/>\n'
    body += f'  <circle cx="{cx}" cy="{top - 14}" r="5" fill="{SHADE}"/>\n'
    return svg(LANDMARK_W, LANDMARK_H, "Solace Biosystems: the DNA helix tower (art pass W8d, ART_BIBLE 3.6, 11 Campaign end). White and greys, tinted in the corp hue at runtime.", body)


def meridian() -> str:
    body = ""
    # Bogies, legs and portal beams.
    for x in (38, 116):
        body += f'  <rect x="{x}" y="{GROUND - 10}" width="46" height="10" rx="3" fill="{LIGHT}"/>\n'
    body += f'  <polygon points="{pts([(48, GROUND - 10), (64, GROUND - 10), (72, 104), (60, 104)])}" fill="{WHITE}"/>\n'
    body += f'  <polygon points="{pts([(136, GROUND - 10), (152, GROUND - 10), (140, 104), (128, 104)])}" fill="{WHITE}"/>\n'
    body += f'  <rect x="52" y="196" width="96" height="12" fill="{SHADE}"/>\n'
    body += f'  <line x1="60" y1="202" x2="140" y2="118" stroke="{SHADE}" stroke-width="5"/>\n'
    body += f'  <line x1="140" y1="202" x2="60" y2="118" stroke="{SHADE}" stroke-width="5"/>\n'
    body += f'  <rect x="50" y="100" width="100" height="18" fill="{WHITE}"/>\n'
    # The A-frame, its stays and the boom.
    body += f'  <polyline points="{pts([(62, 74), (100, 12), (138, 74)])}" fill="none" stroke="{WHITE}" stroke-width="10" stroke-linejoin="round"/>\n'
    body += f'  <line x1="100" y1="12" x2="196" y2="72" stroke="{LIGHT}" stroke-width="4"/>\n'
    body += f'  <line x1="100" y1="12" x2="6" y2="72" stroke="{LIGHT}" stroke-width="4"/>\n'
    body += f'  <line x1="100" y1="12" x2="100" y2="100" stroke="{SHADE}" stroke-width="6"/>\n'
    body += f'  <rect x="4" y="70" width="194" height="16" fill="{WHITE}"/>\n'
    for x in range(12, 196, 16):
        body += f'  <line x1="{x}" y1="72" x2="{x + 8}" y2="84" stroke="{SHADE}" stroke-width="2.5"/>\n'
    # Trolley, cables and the hanging container with its ribs.
    body += f'  <rect x="150" y="86" width="26" height="10" fill="{SHADE}"/>\n'
    body += f'  <line x1="155" y1="96" x2="150" y2="148" stroke="{LIGHT}" stroke-width="3"/>\n'
    body += f'  <line x1="171" y1="96" x2="176" y2="148" stroke="{LIGHT}" stroke-width="3"/>\n'
    body += f'  <rect x="134" y="148" width="58" height="34" fill="{WHITE}"/>\n'
    for x in range(140, 190, 7):
        body += f'  <line x1="{x}" y1="152" x2="{x}" y2="178" stroke="{SHADE}" stroke-width="3"/>\n'
    return svg(LANDMARK_W, LANDMARK_H, "Meridian Freight Systems: the container crane (art pass W8d, ART_BIBLE 3.6, 11 Campaign end). White and greys, tinted in the corp hue at runtime.", body)


def halcyon() -> str:
    body = plinth(34, 166)
    body += f'  <rect x="50" y="236" width="100" height="42" fill="{WHITE}"/>\n'
    body += f'  <rect x="64" y="160" width="72" height="80" fill="{WHITE}"/>\n'
    body += f'  <rect x="90" y="176" width="20" height="44" rx="10" fill="{DEEP}"/>\n'
    for x in (70, 118):
        body += f'  <rect x="{x}" y="184" width="12" height="30" rx="6" fill="{SHADE}"/>\n'
    body += f'  <rect x="80" y="246" width="40" height="32" rx="18" fill="{DEEP}"/>\n'
    # Clock storey, cornice, spire and finial.
    body += f'  <rect x="54" y="84" width="92" height="82" fill="{WHITE}"/>\n'
    body += f'  <rect x="48" y="78" width="104" height="10" fill="{LIGHT}"/>\n'
    body += f'  <polygon points="{pts([(52, 80), (100, 14), (148, 80)])}" fill="{WHITE}"/>\n'
    body += f'  <polygon points="{pts([(100, 14), (148, 80), (122, 80)])}" fill="{LIGHT}"/>\n'
    body += f'  <line x1="100" y1="16" x2="100" y2="0" stroke="{WHITE}" stroke-width="4"/>\n'
    body += f'  <circle cx="100" cy="125" r="33" fill="{SHADE}"/>\n'
    body += f'  <circle cx="100" cy="125" r="26" fill="none" stroke="{WHITE}" stroke-width="3"/>\n'
    body += f'  <circle cx="100" cy="125" r="14" fill="none" stroke="{LIGHT}" stroke-width="2"/>\n'
    for k in range(12):
        a = k / 12 * math.tau
        body += (f'  <line x1="{100 + math.cos(a) * 21:.1f}" y1="{125 + math.sin(a) * 21:.1f}" '
                 f'x2="{100 + math.cos(a) * 25:.1f}" y2="{125 + math.sin(a) * 25:.1f}" stroke="{WHITE}" stroke-width="2.5"/>\n')
    body += f'  <polyline points="{pts([(100, 104), (100, 125), (116, 134)])}" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>\n'
    return svg(LANDMARK_W, LANDMARK_H, "Halcyon Civic: the clock tower (art pass W8d, ART_BIBLE 3.6, 11 Campaign end). White and greys, tinted in the corp hue at runtime.", body)


def orbital() -> str:
    body = plinth(40, 160)
    body += f'  <polygon points="{pts([(82, GROUND - 20), (118, GROUND - 20), (108, 196), (92, 196)])}" fill="{WHITE}"/>\n'
    body += f'  <rect x="96" y="210" width="8" height="54" fill="{SHADE}"/>\n'
    body += f'  <circle cx="100" cy="192" r="14" fill="{WHITE}"/>\n'
    body += f'  <circle cx="100" cy="192" r="6" fill="{SHADE}"/>\n'
    # The dish: a tilted ellipse (the rim), its bowl, struts, the feed arm and horn.
    body += f'  <line x1="100" y1="192" x2="86" y2="138" stroke="{WHITE}" stroke-width="9" stroke-linecap="round"/>\n'
    body += f'  <line x1="100" y1="192" x2="120" y2="150" stroke="{LIGHT}" stroke-width="6" stroke-linecap="round"/>\n'
    body += f'  <ellipse cx="94" cy="112" rx="84" ry="40" transform="rotate(-32 94 112)" fill="{WHITE}"/>\n'
    body += f'  <ellipse cx="100" cy="104" rx="70" ry="28" transform="rotate(-32 100 104)" fill="{SHADE}"/>\n'
    body += f'  <ellipse cx="104" cy="99" rx="46" ry="16" transform="rotate(-32 104 99)" fill="none" stroke="{LIGHT}" stroke-width="2"/>\n'
    body += f'  <line x1="100" y1="104" x2="154" y2="40" stroke="{WHITE}" stroke-width="6" stroke-linecap="round"/>\n'
    body += f'  <line x1="62" y1="126" x2="154" y2="40" stroke="{LIGHT}" stroke-width="3"/>\n'
    body += f'  <line x1="140" y1="78" x2="154" y2="40" stroke="{LIGHT}" stroke-width="3"/>\n'
    body += f'  <circle cx="156" cy="38" r="10" fill="{WHITE}"/>\n'
    body += f'  <circle cx="156" cy="38" r="4" fill="{DEEP}"/>\n'
    # Its signal: three arcs off the horn.
    for k, r in enumerate((20, 30, 40)):
        body += (f'  <path d="M {156 + r * math.cos(-1.25):.1f} {38 + r * math.sin(-1.25):.1f} A {r} {r} 0 0 1 '
                 f'{156 + r * math.cos(0.15):.1f} {38 + r * math.sin(0.15):.1f}" fill="none" stroke="{WHITE if k == 0 else LIGHT}" stroke-width="4" stroke-linecap="round"/>\n')
    return svg(LANDMARK_W, LANDMARK_H, "Orbital Commons: the satellite dish (art pass W8d, ART_BIBLE 3.6, 11 Campaign end). White and greys, tinted in the corp hue at runtime.", body)


def hexagon(cx: float, cy: float, r: float):
    """A pointy-top hexagon's corners (top first, clockwise)."""
    return [(cx + r * math.cos(math.radians(-90 + 60 * k)), cy + r * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]


def rebel_cell() -> str:
    body = plinth(44, 156)
    body += f'  <rect x="80" y="210" width="40" height="70" fill="{WHITE}"/>\n'
    body += f'  <rect x="92" y="222" width="16" height="48" fill="{SHADE}"/>\n'
    outer = hexagon(100, 124, 92)
    inner = hexagon(100, 124, 70)
    body += f'  <polygon points="{pts(outer)}" fill="{WHITE}"/>\n'
    body += f'  <polygon points="{pts(inner)}" fill="{DEEP}"/>\n'
    # The inverted chevron (the Cell's mark upside down) and its scan-glitch cuts.
    body += f'  <polyline points="{pts([(62, 92), (100, 166), (138, 92)])}" fill="none" stroke="{WHITE}" stroke-width="16" stroke-linejoin="miter"/>\n'
    for k, (x0, x1) in enumerate(((56, 88), (108, 146), (70, 130))):
        y = 116 + k * 14
        body += f'  <rect x="{x0}" y="{y}" width="{x1 - x0}" height="3" fill="{DEEP}"/>\n'
    return svg(LANDMARK_W, LANDMARK_H, "REBEL_CELL (handler AI): the inverted Cell hexagon (art pass W8d, ART_BIBLE 3.6, 11 Campaign end). White and greys, tinted in the corp hue at runtime.", body)


# --- The Cell's hexagon, cracked -----------------------------------------------------------

HEX_W = 240
HEX_H = 260
HEX_C = (120.0, 130.0)
HEX_R = 108.0
CRACK = [(120, -8), (120, 22), (111, 50), (128, 78), (113, 104), (127, 132), (108, 160), (125, 188), (112, 214), (122, 240), (121, 270)]


def hex_art() -> str:
    ring = hexagon(*HEX_C, HEX_R)
    body = f'    <polygon points="{pts(ring)}" fill="none" stroke="{WHITE}" stroke-width="20" stroke-linejoin="round"/>\n'
    body += f'    <polygon points="{pts(hexagon(*HEX_C, HEX_R - 24))}" fill="none" stroke="{SHADE}" stroke-width="4" stroke-linejoin="round"/>\n'
    body += f'    <polyline points="{pts([(76, 168), (120, 92), (164, 168)])}" fill="none" stroke="{WHITE}" stroke-width="20" stroke-linecap="round" stroke-linejoin="round"/>\n'
    return body


def cell_half(side: str) -> str:
    edge = 0 if side == "left" else HEX_W
    clip = [(edge, -10)] + CRACK + [(edge, HEX_H + 10)]
    body = (f'  <defs><clipPath id="half"><polygon points="{pts(clip)}"/></clipPath></defs>\n'
            f'  <g clip-path="url(#half)">\n{hex_art()}  </g>\n')
    return svg(HEX_W, HEX_H, f"The Cell's hexagon, {side} half along its crack (art pass W8d, ART_BIBLE 11 Campaign end LOST). White and greys, tinted CELL_PINK at runtime.", body)


def cell_crack() -> str:
    main = CRACK[1:-1]
    body = f'  <polyline points="{pts(main)}" fill="none" stroke="{WHITE}" stroke-width="5" stroke-linejoin="miter" stroke-linecap="round"/>\n'
    branches = [[(111, 50), (92, 40), (78, 44)], [(128, 78), (150, 70), (166, 76)], [(127, 132), (152, 140), (170, 134)],
                [(108, 160), (86, 170), (70, 164)], [(125, 188), (146, 200)], [(113, 104), (94, 98)]]
    for b in branches:
        body += f'  <polyline points="{pts(b)}" fill="none" stroke="{WHITE}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>\n'
    return svg(HEX_W, HEX_H, "The crack through the Cell's hexagon (art pass W8d, ART_BIBLE 11 Campaign end LOST). White, tinted INK at runtime, revealed from the top.", body)


# --- The spray's overspray ------------------------------------------------------------------

SPRAY = 300


def spray_x() -> str:
    body = ""
    # Speckle along both diagonals (a can held too close), fixed by the hash.
    for line, (a, b) in enumerate((((30, 40), (270, 262)), ((272, 36), (28, 264)))):
        for i in range(70):
            t = (i + 0.5) / 70
            x = a[0] + (b[0] - a[0]) * t + jit(i, line * 3 + 1, 22)
            y = a[1] + (b[1] - a[1]) * t + jit(i, line * 3 + 2, 22)
            r = 1.2 + abs(jit(i, line * 3 + 7, 2.4))
            body += f'  <circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{WHITE}"/>\n'
    # Drips off the strokes: a run and a bead.
    for k, (x, y, length) in enumerate(((150, 152, 70), (84, 96, 46), (214, 214, 38), (222, 92, 52), (72, 214, 34))):
        w = 4.5 + abs(jit(k, 11, 1.5))
        body += f'  <rect x="{x - w / 2:.1f}" y="{y}" width="{w:.1f}" height="{length}" rx="{w / 2:.1f}" fill="{WHITE}"/>\n'
        body += f'  <circle cx="{x}" cy="{y + length}" r="{w * 0.85:.1f}" fill="{WHITE}"/>\n'
    return svg(SPRAY, SPRAY, "Overspray and drips round a spray-can X (art pass W8d, ART_BIBLE 11 Campaign end WON). White, tinted CELL_PINK at runtime; the X's strokes are marker_stroke.", body)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    files = {
        "landmark_solace.svg": solace(),
        "landmark_meridian.svg": meridian(),
        "landmark_halcyon.svg": halcyon(),
        "landmark_orbital.svg": orbital(),
        "landmark_rebel_cell.svg": rebel_cell(),
        "cell_hex_left.svg": cell_half("left"),
        "cell_hex_right.svg": cell_half("right"),
        "cell_hex_crack.svg": cell_crack(),
        "spray_x.svg": spray_x(),
    }
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
        print("wrote", (OUT / name).relative_to(ROOT))


if __name__ == "__main__":
    main()
