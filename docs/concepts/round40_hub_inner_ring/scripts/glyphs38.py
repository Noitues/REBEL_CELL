"""Round 38 glyphs: hub-core emblems and inner-ring segment marks, in the locked flat language
(one white silhouette, few dark cut-outs; slicelib.glyph_rgba adds the dark outline).

Ids: CORE_<core id>, HUB_<enemy hub>, SEG_<segment>.  Everything else falls through to glyphs17.
"""
import math
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import glyphs17 as G17
from glyphs13 import _new, _rot, _arrow_arc, _flame_pts
from glyphs14 import _paste, _text_mask

S = 512
BYPASS = set()


def _gap(m, src, r=25):
    _paste(m, src.filter(ImageFilter.MaxFilter(r)), 0)
    _paste(m, src)


def _layer():
    L = Image.new("L", (S, S), 0)
    return L, ImageDraw.Draw(L)


# ======================================================================== class hub cores
def core_breaker():  # crowbar with its claw biting a cracked plate (+spin, Perfect resolves twice)
    m, d = _new()
    d.polygon([(250, 40), (480, 40), (480, 270), (380, 230), (330, 150)], fill=255)  # the plate corner being pried
    d.line([(300, 40), (360, 150), (330, 200)], fill=0, width=18)  # crack in the plate
    d.line([(420, 40), (400, 120), (440, 180)], fill=0, width=14)
    L, dl = _layer()
    dl.line([(80, 470), (310, 170)], fill=255, width=56)
    dl.arc([250, 70, 400, 220], 150, 330, fill=255, width=48)  # the claw hooked under the plate
    dl.polygon([(50, 500), (66, 420), (130, 470)], fill=255)  # chisel end
    _gap(m, L)
    return m


def core_wrecker():  # sledgehammer head striking: 1.5x
    m, d = _new()
    L, dl = _layer()
    dl.rounded_rectangle([110, 70, 410, 210], radius=18, fill=255)
    dl.rectangle([226, 200, 286, 480], fill=255)
    dl.rectangle([86, 110, 120, 170], fill=255)
    dl.rectangle([400, 110, 434, 170], fill=255)
    m.paste(255, (0, 0), L.rotate(-28, resample=Image.BICUBIC, center=(256, 270)))
    for (x0, y0, x1, y1) in ((40, 330, 120, 300), (30, 400, 110, 400), (60, 470, 130, 430)):  # impact lines
        d.line([(x0, y0), (x1, y1)], fill=255, width=26)
    return m


def core_ghost():  # hood with two mesh eyes (ignores resistance)
    m, d = _new()
    d.pieslice([80, 40, 432, 392], 180, 360, fill=255)
    d.rectangle([80, 214, 432, 470], fill=255)
    for i in range(4):
        x = 80 + i * 88
        d.polygon([(x, 472), (x + 44, 420), (x + 88, 472)], fill=0)
    d.ellipse([150, 200, 236, 286], fill=0)
    d.ellipse([276, 200, 362, 286], fill=0)
    return m


def core_phantom():  # mask with an offset afterimage (free nudge, evade)
    m, d = _new()
    for off, f in ((58, 255), (0, 255)):
        L, dl = _layer()
        dl.ellipse([96 + off, 56 - off // 3, 380 + off, 456 - off // 3], fill=255)
        dl.polygon([(150 + off, 200), (236 + off, 186), (226 + off, 246)], fill=0)
        dl.polygon([(326 + off, 200), (240 + off, 186), (250 + off, 246)], fill=0)
        dl.rounded_rectangle([196 + off, 330, 280 + off, 350], radius=8, fill=0)
        if off:
            _paste(m, L)
            hole, dh = _layer()
            dh.ellipse([110 + off, 70 - off // 3, 366 + off, 442 - off // 3], fill=255)
            _paste(m, hole, 0)
        else:
            _gap(m, L, 21)
    return m


def core_rig():  # jack plug with a cable (RAM, free nudge)
    m, d = _new()
    d.rounded_rectangle([170, 150, 342, 330], radius=20, fill=255)
    d.rectangle([200, 40, 230, 160], fill=255)
    d.rectangle([282, 40, 312, 160], fill=255)
    d.rounded_rectangle([206, 326, 306, 380], radius=10, fill=255)
    pts = [(256, 378)] + [(256 - 120 * math.sin(k / 10 * math.pi) * (k / 10), 378 + k * 12) for k in range(1, 11)]
    d.line(pts, fill=255, width=36, joint="curve")
    d.rectangle([214, 196, 298, 230], fill=0)
    return m


def core_overclock():  # chip with heat-sink fins and a bolt (+max RAM)
    m, d = _new()
    d.rounded_rectangle([110, 190, 402, 470], radius=20, fill=255)
    for i in range(5):
        x = 126 + i * 56
        h = 150 if i == 2 else 110
        d.rectangle([x, 190 - h, x + 36, 200], fill=255)
    for k in range(4):
        y = 230 + k * 60
        d.rectangle([60, y, 112, y + 22], fill=255)
        d.rectangle([400, y, 452, y + 22], fill=255)
    d.polygon([(282, 230), (196, 350), (254, 350), (226, 440), (318, 312), (262, 312), (300, 230)], fill=0)
    return m


def core_swarm():  # three drones in a triangle, linked (drones persist)
    m, d = _new()
    pts = [(256, 96), (100, 380), (412, 380)]
    for a, b in ((0, 1), (1, 2), (2, 0)):
        d.line([pts[a], pts[b]], fill=255, width=22)
    for (x, y) in pts:
        d.ellipse([x - 82, y - 82, x + 82, y + 82], fill=0)
        d.ellipse([x - 70, y - 70, x + 70, y + 70], fill=255)
        d.ellipse([x - 32, y - 32, x + 32, y + 32], fill=0)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=255)
    return m


def core_hive():  # hex cell holding four node dots (up to 4 drones)
    m, d = _new()
    hexo = [(256 + 236 * math.cos(math.radians(a)), 256 + 236 * math.sin(math.radians(a))) for a in range(30, 390, 60)]
    hexi = [(256 + 176 * math.cos(math.radians(a)), 256 + 176 * math.sin(math.radians(a))) for a in range(30, 390, 60)]
    d.polygon(hexo, fill=255)
    d.polygon(hexi, fill=0)
    for (x, y) in ((256, 172), (176, 300), (336, 300), (256, 256)):
        d.ellipse([x - 40, y - 40, x + 40, y + 40], fill=255)
    for a, b in (((256, 172), (176, 300)), ((256, 172), (336, 300)), ((176, 300), (336, 300))):
        d.line([a, b], fill=255, width=18)
    return m


# ======================================================================== enemy hub passives
def hub_compliance_lock():  # rubber stamp coming down (resistance 3)
    m, d = _new()
    d.ellipse([196, 30, 316, 150], fill=255)
    d.rectangle([228, 130, 284, 260], fill=255)
    d.rounded_rectangle([110, 250, 402, 330], radius=16, fill=255)
    d.rectangle([90, 330, 422, 390], fill=255)
    d.rounded_rectangle([60, 430, 452, 480], radius=10, fill=255)  # the stamped mark
    d.rectangle([130, 444, 382, 466], fill=0)
    return m


def hub_priority_routing():  # an express arrow overtaking two stacked lanes (The Manifest)
    m, d = _new()
    for y in (120, 392):
        d.rounded_rectangle([40, y - 26, 300, y + 26], radius=26, fill=255)
    L, dl = _layer()
    dl.polygon([(40, 210), (330, 210), (330, 130), (490, 256), (330, 382), (330, 302), (40, 302)], fill=255)
    _gap(m, L, 31)
    return m


def hub_emergency_powers():  # siren dome with rays (The Civic Core)
    m, d = _new()
    d.pieslice([126, 150, 386, 410], 180, 360, fill=255)
    d.rectangle([126, 278, 386, 300], fill=255)
    d.rounded_rectangle([86, 320, 426, 400], radius=14, fill=255)
    d.rectangle([186, 200, 216, 270], fill=0)
    for a in (-160, -125, -90, -55, -20):
        r = math.radians(a)
        d.line([(256 + 170 * math.cos(r), 280 + 170 * math.sin(r)), (256 + 240 * math.cos(r), 280 + 240 * math.sin(r))], fill=255, width=34)
    return m


def hub_station_keeping():  # satellite with panels (The Commons Array)
    m, d = _new()
    L, dl = _layer()
    dl.rounded_rectangle([196, 196, 316, 316], radius=18, fill=255)
    for x0 in (30, 340):
        dl.rectangle([x0, 206, x0 + 142, 306], fill=255)
        for k in range(1, 3):
            dl.line([(x0 + k * 47, 206), (x0 + k * 47, 306)], fill=0, width=12)
    dl.rectangle([172, 246, 196, 266], fill=255)
    dl.rectangle([316, 246, 340, 266], fill=255)
    dl.ellipse([230, 230, 282, 282], fill=0)
    m.paste(255, (0, 0), L.rotate(-30, resample=Image.BICUBIC))
    d.arc([300, 20, 500, 220], 280, 360, fill=255, width=26)  # signal arcs
    d.arc([350, 70, 450, 170], 280, 360, fill=255, width=26)
    return m


def hub_auto_renew():  # renew loop around a plus (Renewal Engine)
    m, d = _new()
    _arrow_arc(d, (256, 256), 210, 52, 200, 470, 1.1)
    d.rectangle([226, 150, 286, 362], fill=255)
    d.rectangle([150, 226, 362, 286], fill=255)
    return m


def hub_root_access():  # terminal prompt "#_" (DISPATCH)
    m, d = _new()
    d.rounded_rectangle([20, 70, 492, 442], radius=36, fill=255)
    d.rounded_rectangle([60, 140, 452, 402], radius=16, fill=0)
    d.ellipse([60, 92, 88, 120], fill=0)
    d.ellipse([104, 92, 132, 120], fill=0)
    t = _text_mask("#_", (100, 170, 412, 380))
    _paste(m, t)
    return m


# ======================================================================== inner-ring segments
def seg_x2():
    return _text_mask("×2", (30, 70, 482, 442))


def seg_pierce():  # an arrow through a brick slab (ignores block + shield)
    m, d = _new()
    d.rectangle([206, 40, 306, 472], fill=255)
    for y in (140, 256, 372):
        d.line([(200, y), (312, y)], fill=0, width=16)
    d.line([(256, 40), (256, 140)], fill=0, width=14)
    d.line([(256, 256), (256, 372)], fill=0, width=14)
    L, dl = _layer()
    dl.rectangle([20, 226, 360, 286], fill=255)
    dl.polygon([(340, 150), (492, 256), (340, 362)], fill=255)
    dl.polygon([(20, 226), (60, 196), (100, 226)], fill=255)
    dl.polygon([(20, 286), (60, 316), (100, 286)], fill=255)
    _gap(m, L, 27)
    return m


def seg_corrupt():  # a data block glitched into shifted slabs (applies CORRUPTED)
    m, d = _new()
    rows = [(60, 150, 0), (150, 230, 60), (230, 300, -46), (300, 380, 30), (380, 452, -18)]
    for (y0, y1, dx) in rows:
        d.rectangle([96 + dx, y0, 416 + dx, y1 - 14], fill=255)
    d.rectangle([180, 170, 236, 210], fill=0)
    d.rectangle([300, 316, 340, 352], fill=0)
    return m


def seg_anchor():  # anchor (on Perfect, skip the next respin) - never drawn before
    m, d = _new()
    d.ellipse([200, 20, 312, 132], fill=255)
    d.ellipse([230, 50, 282, 102], fill=0)
    d.rectangle([228, 120, 284, 450], fill=255)
    d.rounded_rectangle([140, 160, 372, 206], radius=16, fill=255)
    d.arc([70, 196, 442, 480], 15, 165, fill=255, width=50)
    for s in (-1, 1):
        x = 256 + s * 192
        d.polygon([(x - s * 6, 260), (x + s * 54, 360), (x - s * 46, 352)], fill=255)
    return m


def seg_accelerator():  # a gear with speed lines (nudge cards next turn trigger twice)
    m, d = _new()
    c = (300, 256)
    teeth = []
    for i in range(16):
        r = 200 if i % 2 == 0 else 160
        a = math.radians(i * 22.5)
        teeth.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
    d.polygon(teeth, fill=255)
    d.ellipse([c[0] - 70, c[1] - 70, c[0] + 70, c[1] + 70], fill=0)
    for y, x0 in ((150, 20), (256, 0), (362, 20)):
        d.rounded_rectangle([x0, y - 18, 108, y + 18], radius=18, fill=0)
    L, dl = _layer()
    for y, x0 in ((150, 20), (256, 0), (362, 20)):
        dl.rounded_rectangle([x0, y - 16, 96, y + 16], radius=16, fill=255)
    _paste(m, L)
    return m


def seg_echo():  # a source block + two fading echo arcs (outer slice again at half)
    m, d = _new()
    d.rounded_rectangle([40, 186, 170, 326], radius=20, fill=255)
    for r, w in ((150, 44), (250, 44)):
        d.arc([105 - r, 256 - r, 105 + r, 256 + r], -50, 50, fill=255, width=w)
    return m


def seg_blank():
    m, d = _new()
    d.rounded_rectangle([130, 228, 382, 284], radius=26, fill=255)
    return m


NEW = {
    "CORE_breaker_core": core_breaker, "CORE_wrecker_core": core_wrecker, "CORE_ghost_core": core_ghost,
    "CORE_phantom_core": core_phantom, "CORE_rig_core": core_rig, "CORE_overclock_core": core_overclock,
    "CORE_swarm_core": core_swarm, "CORE_hive_core": core_hive,
    "HUB_compliance_lock": hub_compliance_lock, "HUB_priority_routing": hub_priority_routing,
    "HUB_emergency_powers": hub_emergency_powers, "HUB_station_keeping": hub_station_keeping,
    "HUB_auto_renew": hub_auto_renew, "HUB_root_access": hub_root_access,
    "SEG_x2": seg_x2, "SEG_pierce": seg_pierce, "SEG_corrupt": seg_corrupt, "SEG_anchor": seg_anchor,
    "SEG_accelerator": seg_accelerator, "SEG_echo": seg_echo, "SEG_blank": seg_blank,
}
CHOICE = G17.CHOICE
SMALL = {}
_cache = {}


def resolve(name, px=None):
    return CHOICE.get(name, name)


def mask(name):
    if name in BYPASS:
        return None
    f = NEW.get(name)
    if f is None:
        return G17.mask(name)
    if name not in _cache:
        _cache[name] = f()
    return _cache[name].copy()


tick_mask = G17.tick_mask
