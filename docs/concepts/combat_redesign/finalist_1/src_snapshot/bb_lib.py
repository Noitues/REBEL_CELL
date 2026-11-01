"""Bible-faithful wheel kit (copies of round41 scripts, patched to the bible's type faces)."""
import sys, os, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
R41 = os.path.join(os.path.dirname(HERE), 'r41', 'scripts')
sys.path.insert(0, R41)
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import slicelib as SL
FD = 'D:/rc_art/art-pass/assets/fonts/'
SL.FONTS = FD
_fc = {}


def _font(name, px):
    k = (name, int(px))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + name, max(4, int(px)))
    return _fc[k]


def anton(px): return _font('Anton-Regular.ttf', px)
def mono(px, b=True): return _font('ShareTechMono-Regular.ttf', px)
def plex(px, b=True): return _font('IBMPlexSansCondensed-Medium.ttf' if b else 'IBMPlexSansCondensed-Regular.ttf', px)


SL.f_num = lambda px: anton(px)
SL.f_ui = lambda px, var=None: plex(px)
SL.f_mono = lambda px, bold=True: mono(px)
import crests15


def _mk(fn):
    def f():
        m = Image.new('L', (512, 512), 0)
        d = ImageDraw.Draw(m)
        fn(d, m)
        return m
    return f


def g_packet(d, m):
    d.rounded_rectangle([80, 80, 432, 432], radius=30, fill=255)
    d.polygon([(150, 256), (300, 256), (300, 200), (400, 290), (300, 380), (300, 320), (150, 320)], fill=0)


def g_worm(d, m):
    pts = [(40, 400), (150, 130), (256, 400), (362, 130), (472, 400)]
    d.line(pts, fill=255, width=96, joint='curve')
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0] - 48, p[1] - 48, p[0] + 48, p[1] + 48], fill=255)


def g_jammer(d, m):
    d.ellipse([50, 50, 462, 462], fill=255)
    d.ellipse([140, 140, 372, 372], fill=0)
    d.line([(90, 440), (440, 90)], fill=255, width=110)


def g_payload(d, m):
    d.polygon([(256, 20), (492, 256), (256, 492), (20, 256)], fill=255)
    d.rectangle([150, 215, 362, 255], fill=0)
    d.rectangle([150, 285, 362, 325], fill=0)


def g_shove(d, m):
    d.polygon([(40, 200), (250, 200), (250, 110), (410, 256), (250, 402), (250, 312), (40, 312)], fill=255)
    d.rectangle([440, 90, 490, 422], fill=255)


def g_stall(d, m):
    d.rectangle([110, 70, 220, 442], fill=255)
    d.rectangle([292, 70, 402, 442], fill=255)


def g_twist(d, m):
    d.arc([70, 90, 442, 400], 200, 340, fill=255, width=70)
    d.polygon([(380, 120), (470, 230), (330, 250)], fill=255)
    d.arc([70, 112, 442, 422], 20, 160, fill=255, width=70)
    d.polygon([(132, 392), (42, 282), (182, 262)], fill=255)


def g_hp(d, m):
    d.rounded_rectangle([60, 60, 452, 452], radius=60, fill=255)
    d.rectangle([216, 120, 296, 392], fill=0)
    d.rectangle([120, 216, 392, 296], fill=0)


def g_eye(d, m):
    d.ellipse([20, 130, 492, 382], fill=255)
    d.ellipse([170, 156, 342, 356], fill=0)
    d.ellipse([214, 200, 298, 312], fill=255)


def g_lock(d, m):
    d.rounded_rectangle([90, 220, 422, 470], radius=30, fill=255)
    d.arc([140, 50, 372, 330], 180, 360, fill=255, width=50)
    d.ellipse([226, 300, 286, 360], fill=0)


def g_skull(d, m):
    d.ellipse([70, 40, 442, 360], fill=255)
    d.rectangle([150, 300, 362, 470], fill=255)
    d.ellipse([140, 170, 240, 270], fill=0)
    d.ellipse([272, 170, 372, 270], fill=0)


for n, f in dict(U_PACKET=g_packet, U_WORM=g_worm, U_JAMMER=g_jammer, U_PAYLOAD=g_payload, C_SHOVE=g_shove, C_STALL=g_stall,
                 C_TWIST=g_twist, X_HP=g_hp, X_EYE=g_eye, X_LOCK=g_lock, X_SKULL=g_skull).items():
    crests15.CUSTOM[n] = _mk(f)
import roster_wheel as RW
import combat_wheel as CW
from slicelib import R_IN, R_OUT, CORPS, PROGRAMS, render_slice, glyph_rgba, number_rgba
P = RW.P
ORANGE = CORPS['meridian']['col']
CYAN = (92, 225, 255)
PINK = (255, 61, 168)
YEL = (255, 226, 0)
RED = (255, 68, 51)
GREEN = (123, 224, 123)
INK = (12, 10, 22)


def pill(d, box, fill=(8, 14, 28, 235), outline=CYAN, w=2, r=8):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline + (255,), width=w)


def text(d, xy, s, font, fill=(255, 255, 255), anchor='la', stroke=0, sf=(10, 8, 16)):
    d.text(xy, s, font=font, fill=fill + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=sf + (255,))


def code_wheel(slots, hp=(60, 60), pred=0, ss=2):
    """Player wheel = CW.render with Breaker styling; slots = list of dict(program,value) per sector 0..5."""
    spec = dict(theme='player', cls='breaker',
                slots=[dict(program=s['program'], value=s['value'], special=None, badge=None) for s in slots],
                pointers=[0], orbit=0, hub=dict(name='Breaker', sub='Code base', emblem=RW.CLASS_STYLE['breaker']['emblem']),
                ring=None, hp=hp, pred=pred, seed=3, key='breaker', hp_number=False)
    return CW.render(spec, ss=ss)


def wave_wheel(cells, ss=2):
    """cells[dep][s] = None | dict(prog). 3 rings (dep 0 innermost)."""
    RW.CW, RW.CH, RW.CX, RW.CY = 1100, 1200, 550, 610
    CWd, CH = RW.CW, RW.CH
    canvas = np.zeros((CH * ss, CWd * ss, 4), np.float32)
    acc = ORANGE
    Rt = R_OUT + 40
    RW.ring_base(canvas, ss, R_OUT + 1, Rt, (0.025, 0.03, 0.04), acc, rim=1.4)
    span = (R_OUT - R_IN) / 3.0
    geo = []
    for dep in range(3):
        ri, ro = R_IN + dep * span, R_IN + (dep + 1) * span
        geo.append((ri, ro))
        SL.R_IN, SL.R_OUT = ri, ro
        for s in range(6):
            c = cells[dep][s]
            if c is None:
                continue
            render_slice(canvas, RW.CX * ss, RW.CY * ss, c['prog'], 60 * s - 30, 60, None, (0.3 + 0.137 * (s + 6 * dep)) % 1,
                         'meridian', ss, dict(icons=False, glyph_scale=1.0, tex_gain=0.8), seed=s + 7 * dep + 3)
    SL.R_IN, SL.R_OUT = R_IN, R_OUT
    over = Image.new('RGBA', (CWd * ss, CH * ss), (0, 0, 0, 0))
    glow = Image.new('RGBA', (CWd * ss, CH * ss), (0, 0, 0, 0))
    d, gd = ImageDraw.Draw(over), ImageDraw.Draw(glow)
    for dep in range(3):
        ri, ro = geo[dep]
        for s in range(6):
            if cells[dep][s] is None:
                poly = RW.arc_poly(ri + 3, ro - 3, 60 * s - 28, 60 * s + 28, ss, 14)
                d.polygon(poly, fill=(10, 16, 28, 235), outline=tuple(int(v * 0.45) for v in acc) + (255,))
    CW.telemetry_ring(over, d, gd, dict(pointers=[0]), R_OUT + 1, Rt, ss, acc, 'route_optimizer', RW.CORP_EMBLEM['meridian'])
    RW.draw_hub(over, d, gd, ss, 126, acc, 'EM_MERIDIAN', 'WAVE', 'Shifting')
    RW.draw_pointer(d, gd, 0, R_OUT + 30, ss, acc)
    glow = glow.filter(ImageFilter.GaussianBlur(7 * ss))
    g = np.asarray(glow, np.float32) / 255
    o = np.asarray(over, np.float32) / 255
    canvas[..., :3] += g[..., :3] * g[..., 3:] * 0.9
    canvas[..., 3:] = np.maximum(canvas[..., 3:], g[..., 3:] * 0.9)
    oa = o[..., 3:]
    canvas[..., :3] = canvas[..., :3] * (1 - oa) + o[..., :3] * oa
    canvas[..., 3:] = canvas[..., 3:] * (1 - oa) + oa
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA').resize((CWd, CH), Image.LANCZOS)
    return im, (RW.CX, RW.CY), geo
