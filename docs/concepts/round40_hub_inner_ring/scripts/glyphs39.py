"""Round 39 glyphs: Breaker / Wrecker / Phantom / Rigger / Overclocker cores redone; new inner-ring
segment PROPOSALS (not in game). Falls through to glyphs38 (approved Ghost / Swarm / Hive and enemy hubs).
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import glyphs38 as G38
from glyphs13 import _new, _rot, _arrow_arc
from glyphs14 import _paste, _text_mask
from glyphs38 import _gap, _layer

S = 512
BYPASS = set()


def core_breaker():  # a crowbar striking an empty glass square that cracks from the hit
    m, d = _new()
    d.rectangle([200, 40, 480, 320], outline=255, width=30)  # the glass pane: outline only, unfilled
    hit = (262, 258)
    for ang, L in ((-80, 170), (-30, 200), (10, 190), (55, 120), (-125, 90)):
        a = math.radians(ang)
        pts = [hit]
        x, y = hit
        for k in range(3):
            a += 0.25 * (1 if k % 2 else -1)
            x += math.cos(a) * L / 3
            y += math.sin(a) * L / 3
            pts.append((min(470, max(210, x)), min(310, max(50, y))))
        d.line(pts, fill=255, width=14, joint="curve")
    L, dl = _layer()
    dl.line([(60, 480), (250, 270)], fill=255, width=50)  # the bar, its claw end striking the glass
    dl.arc([196, 196, 316, 316], 160, 330, fill=255, width=42)
    dl.polygon([(34, 500), (48, 430), (104, 470)], fill=255)
    _gap(m, L, 23)
    return m


def core_wrecker():  # the sledgehammer alone (the round 38 speed lines read as noise and are dropped)
    m, d = _new()
    L, dl = _layer()
    dl.rounded_rectangle([100, 60, 412, 214], radius=18, fill=255)
    dl.rectangle([226, 204, 286, 486], fill=255)
    dl.rectangle([76, 104, 112, 170], fill=255)
    dl.rectangle([400, 104, 436, 170], fill=255)
    dl.rectangle([226, 400, 286, 412], fill=0)  # grip band
    m.paste(255, (0, 0), L.rotate(-28, resample=Image.BICUBIC, center=(256, 270)))
    return m


def core_phantom():  # the round 38 mask, front only (the echo trail is drawn by the hub as motion)
    m, d = _new()
    d.ellipse([116, 46, 396, 466], fill=255)
    d.polygon([(170, 196), (256, 182), (246, 242)], fill=0)
    d.polygon([(342, 196), (266, 182), (276, 242)], fill=0)
    d.rounded_rectangle([206, 330, 306, 352], radius=8, fill=0)
    return m


def core_phantom_echo():  # static glyph form for icons: mask + two hollow echo outlines trailing left
    m, d = _new()
    for off, w, top in ((-150, 18, 120), (-80, 24, 80)):  # echoes: shorter, offset arcs (motion), not full ovals
        d.arc([116 + off, 46 + top // 2, 396 + off, 466 - top // 2], 100, 260, fill=255, width=w)
    L = core_phantom()
    _gap(m, L, 25)
    return m


def core_rig():  # a firmware chip dropping into its socket
    m, d = _new()
    d.rounded_rectangle([80, 330, 432, 480], radius=16, fill=255)  # socket
    d.rectangle([130, 330, 382, 384], fill=0)  # the open slot
    for k in range(6):
        x = 146 + k * 42
        d.rectangle([x, 342, x + 18, 384], fill=255)  # socket contacts
    d.rounded_rectangle([140, 40, 372, 250], radius=14, fill=255)  # chip body
    for k in range(6):
        x = 150 + k * 40
        d.rectangle([x, 250, x + 18, 300], fill=255)  # chip legs pointing down into the slot
    d.ellipse([162, 62, 196, 96], fill=0)  # pin-1 dot
    d.rectangle([200, 120, 312, 170], fill=0)  # die window
    d.polygon([(232, 306), (280, 306), (256, 324)], fill=0) if False else None
    for y in (296, 316):  # motion: it is going in
        pass
    return m


def core_overclock():  # RPM gauge: numbered tick scale, red zone wedge, needle buried in the red
    m, d = _new()
    c = (256, 300)
    d.pieslice([c[0] - 236, c[1] - 236, c[0] + 236, c[1] + 236], 160, 380, fill=255)
    d.pieslice([c[0] - 196, c[1] - 196, c[0] + 196, c[1] + 196], 160, 380, fill=0)
    d.pieslice([c[0] - 196, c[1] - 196, c[0] + 196, c[1] + 196], 320, 380, fill=255)  # the red zone, solid
    d.pieslice([c[0] - 150, c[1] - 150, c[0] + 150, c[1] + 150], 300, 400, fill=0)
    for k in range(7):  # tick scale
        a = math.radians(160 + k * 22)
        d.line([(c[0] + 160 * math.cos(a), c[1] + 160 * math.sin(a)), (c[0] + 196 * math.cos(a), c[1] + 196 * math.sin(a))], fill=255, width=16)
    a = math.radians(-12)
    d.line([c, (c[0] + 210 * math.cos(a), c[1] + 210 * math.sin(a))], fill=0, width=54)
    d.line([c, (c[0] + 200 * math.cos(a), c[1] + 200 * math.sin(a))], fill=255, width=30)
    d.ellipse([c[0] - 44, c[1] - 44, c[0] + 44, c[1] + 44], fill=255)
    d.rounded_rectangle([110, 380, 402, 440], radius=14, fill=255)
    d.rectangle([150, 398, 362, 422], fill=0)  # x1000 RPM window
    return m


# ---------------------------------------------------------- inner-ring segment PROPOSALS (not in game)
def seg_hangar():  # DRONE-focused: a dock bracket with a drone in it (deploy into the aligned slice)
    m, d = _new()
    d.line([(60, 140), (60, 420), (452, 420), (452, 140)], fill=255, width=46)
    for (x, y) in ((176, 220), (336, 220)):
        d.ellipse([x - 70, y - 50, x + 70, y + 50], fill=255)
        d.ellipse([x - 44, y - 28, x + 44, y + 28], fill=0)
    d.rounded_rectangle([196, 250, 316, 340], radius=18, fill=255)
    d.ellipse([236, 276, 276, 316], fill=0)
    return m


def seg_double_status():  # status-themed: a status diamond doubled (statuses land twice / stack 2)
    m, d = _new()
    for cx, f in ((200, 255), (330, 255)):
        d.polygon([(cx, 60), (cx + 150, 256), (cx, 452), (cx - 150, 256)], fill=255)
    d.polygon([(330, 130), (426, 256), (330, 382), (234, 256)], fill=0)
    d.polygon([(330, 182), (386, 256), (330, 330), (274, 256)], fill=255)
    return m


def seg_splash():  # AOE adjacent: one block with two side bursts
    m, d = _new()
    d.rounded_rectangle([196, 176, 316, 336], radius=16, fill=255)
    for s in (-1, 1):
        x = 256 + s * 150
        for k in (-1, 0, 1):
            a = math.radians(90 - 90 * s + k * 30)
            d.line([(256 + s * 80, 256), (256 + s * 80 + 150 * math.cos(a), 256 + 150 * math.sin(a))], fill=255, width=36)
        d.ellipse([x + s * 60 - 40, 216, x + s * 60 + 40, 296], fill=255)
    return m


def seg_broadcast():  # AOE global: a mast radiating to every target
    m, d = _new()
    d.polygon([(256, 200), (330, 480), (182, 480)], fill=255)
    d.polygon([(256, 290), (290, 440), (222, 440)], fill=0)
    d.ellipse([222, 164, 290, 232], fill=255)
    for r in (110, 190):
        d.arc([256 - r, 198 - r, 256 + r, 198 + r], 200, 340, fill=255, width=36)
    return m


def seg_sub_needle():  # ACCELERATOR proposal: a small second needle riding the segment
    m, d = _new()
    d.arc([40, 250, 472, 682], 220, 320, fill=255, width=60)  # the segment band
    d.polygon([(256, 30), (304, 236), (208, 236)], fill=255)  # mini needle pointing out
    d.ellipse([214, 210, 298, 294], fill=255)
    d.ellipse([240, 236, 272, 268], fill=0)
    return m


NEW = {"CORE_breaker_core": core_breaker, "CORE_wrecker_core": core_wrecker, "CORE_phantom_core": core_phantom,
       "CORE_phantom_echo": core_phantom_echo, "CORE_rig_core": core_rig, "CORE_overclock_core": core_overclock,
       "SEG_hangar": seg_hangar, "SEG_double_status": seg_double_status, "SEG_splash": seg_splash,
       "SEG_broadcast": seg_broadcast, "SEG_sub_needle": seg_sub_needle}
OLD = {k: G38.NEW[k] for k in ("CORE_breaker_core", "CORE_wrecker_core", "CORE_phantom_core", "CORE_rig_core", "CORE_overclock_core")}
CHOICE = G38.CHOICE
SMALL = {}
_cache = {}


def resolve(name, px=None):
    return CHOICE.get(name, name)


def mask(name):
    if name in BYPASS:  # the round 38 shape (for the before / after panel)
        return G38.mask(name)
    f = NEW.get(name)
    if f is None:
        return G38.mask(name)
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()


tick_mask = G38.tick_mask
