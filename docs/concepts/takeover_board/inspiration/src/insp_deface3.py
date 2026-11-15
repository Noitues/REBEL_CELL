"""insp_deface3: DEFACE v3, deface-shaped vinyl stickers on the monitor glass + grease pencil for aim and forecast.

    python insp_deface3.py [df3_rest df3_aim df3_play df3_hover sheet]      (default: all)

Designer: "stickers as buttons and grease pen marking up the monitor ... deface shaped stickers, grease pen for targeting
sticker, and grease pen for forecast and such.  Playing the sticker lifts it off the screen, places it on the corp wheel, then
it dissolves into bits and is played."
Bible: ART_BIBLE 1.2 (sticker = fixed objects; grease pencil = plans true to the rules, wax, yellow #FFE200 plan / red #FF1C2C
loss, solid = will happen; bits = 0/1 in the source colour), 2.9 (Anton sticker, Permanent Marker wax, Share Tech Mono bits),
2.10 (focus = peel-back curl), 3.18 (die-cut, gloss band, yellow cost dot, peel / slap / dissolve), 3.19 (pencil 7 px, ink edge),
1.3 (SEND IT over EXECUTE).
Sticker toolkit: the repo's sticker_lib19 (imported read-only, no bytecode written).  Wheel and corp board: tk_render /
insp_render, unchanged.
"""
import copy, math, os, random, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/takeover/inspiration')
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/cohesion/map_pages_r42/scripts')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import insp_render as IR
from insp_render import (TR, S, text, Layer, comp, INK, PAPER, PINK, PINK_D, HARM, FOCUS, CYAN, TEXT_HI, TEXT_MID, ANTON, PLEX, MONO,
                         ACTS, BOARD, PLAY, CX, CY, W, H, SS, plate_cols, tw, wrap, glyph_mask, F_all, base_image, run_health, glass)
from tk_states import FORECAST, GAIN as S_GAIN, HARM as S_HARM, HI as S_HI, PLAN as S_PLAN, MID as S_MID, SCHED as S_SCHED
import sticker_lib19 as SL

OUT = IR.OUT
MARKER = 'D:/rc_art/art-pass/assets/fonts/PermanentMarker-Regular.ttf'
PEN_Y = (255, 226, 0)            # bible 1.2: yellow #FFE200 = our plan / valid
PEN_R = (255, 28, 44)            # bible 1.2: red #FF1C2C = threat / invalid / loss
CELL_PINK = PINK
assert SL.SS == SS


# =============================================================================================== grease pencil (wax)
class Wax(SL.Pen):
    """the repo pen's stroke geometry (stroke / circle / arrow / text), inked as the bible's wax: opaque (0.96), rough edge with
    dropouts and a sheen line, an ink edge, a dark under-shadow"""

    def __init__(self, color, seed=21):
        super().__init__((W, H), color, seed)

    def text(self, s, x, y, size, angle=0.0, anchor='mm'):
        super().text(s, x, y, size, angle, font_path=MARKER, anchor=anchor)

    def tick(self, x, y, s=16, w=7):
        self.stroke(SL.catmull(self.wobble([(x - s, y), (x - s * 0.3, y + s * 0.75), (x + s * 1.1, y - s * 0.9)], 0.8), 6), w, taper=False)

    def x(self, x, y, s=12, w=7):
        self.stroke(self.wobble([(x - s, y - s), (x + s, y + s)], 0.6), w, taper=False)
        self.stroke(self.wobble([(x + s, y - s), (x - s, y + s)], 0.6), w, taper=False)

    def ink_ss(self, img):
        m = self.mask
        if not m.getbbox():
            return
        ma = np.asarray(m, np.float32) / 255.0
        rng = np.random.default_rng(7)
        h, w = ma.shape
        nz = np.asarray(Image.fromarray((rng.random((h // 2, w // 2)) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255.0
        streak = np.asarray(Image.fromarray((rng.random((h // 6, w // 2)) * 255).astype(np.uint8)).resize((w, h), Image.BILINEAR), np.float32) / 255.0
        al = np.clip(0.96 - np.where(nz > 0.88, 0.42, 0.0) - 0.06 * streak, 0, 1)
        edge = np.asarray(m.filter(ImageFilter.MaxFilter(S(2.2) * 2 + 1)), np.float32) / 255.0
        sh = np.asarray(m.filter(ImageFilter.MaxFilter(S(1.5) * 2 + 1)).filter(ImageFilter.GaussianBlur(S(3))), np.float32) / 255.0
        sh = np.roll(np.roll(sh, S(3), 0), S(2), 1)
        L = Layer()
        L.im.paste(Image.new('RGBA', m.size, (5, 3, 8, 255)), (0, 0), Image.fromarray((sh * 0.55 * 255).astype(np.uint8)))
        L.im.paste(Image.new('RGBA', m.size, (6, 3, 8, 255)), (0, 0), Image.fromarray((edge * 0.92 * 255).astype(np.uint8)))
        c = np.array(self.color, np.float32)
        rgb = np.broadcast_to(c, (h, w, 3)) * (0.92 + 0.08 * streak[..., None])
        wax = np.dstack([rgb, ma * al * 255]).clip(0, 255).astype(np.uint8)
        L.im.alpha_composite(Image.fromarray(wax, 'RGBA'))
        # the sheen: a thin light line on the top-left edge of the wax
        hl = np.clip(ma - np.roll(np.roll(ma, S(1.5), 0), S(1), 1), 0, 1) * 0.5
        L.im.paste(Image.new('RGBA', m.size, (255, 255, 240, 255)), (0, 0), Image.fromarray((hl * 255).astype(np.uint8)))
        comp(img, L)


# =============================================================================================== deface-shaped stickers
def _shape(kind, w, h, seed):
    """the die-cut silhouette of an action: a street-sticker / tag shape that reads as the action (1x units, centred)"""
    rng = random.Random(seed)
    m = Image.new('L', (S(w), S(h)), 0); d = ImageDraw.Draw(m)
    cx, cy = w / 2, h / 2
    P = lambda x, y: (S(x), S(y))
    if kind == 'burst':            # BREACH: a jagged impact burst
        pts = []
        for k in range(26):
            a = 2 * math.pi * k / 26
            r = (1.0 if k % 2 == 0 else 0.66) * rng.uniform(0.9, 1.06)
            pts.append(P(cx + r * w * 0.48 * math.cos(a), cy + r * h * 0.47 * math.sin(a)))
        d.polygon(pts, fill=255)
    elif kind == 'shield':         # GUARD: a shield
        pts = [(0.08, 0.08), (0.5, 0.0), (0.92, 0.08), (0.9, 0.52), (0.5, 1.0), (0.1, 0.52)]
        d.polygon([P(x * w, y * h) for x, y in pts], fill=255)
    elif kind == 'bomb':           # TIME BOMB: a round bomb with a fuse and a spark
        r = h * 0.40
        bx, by = cx - w * 0.06, cy + h * 0.08
        d.ellipse([P(bx - r, by - r), P(bx + r, by + r)], fill=255)
        d.rectangle([P(bx + r * 0.35, by - r * 1.05), P(bx + r * 0.75, by - r * 0.65)], fill=255)
        d.line([P(bx + r * 0.6, by - r * 1.0), P(bx + r * 1.05, by - r * 1.35), P(bx + r * 1.35, by - r * 1.2)], fill=255, width=S(12))
        sx, sy = bx + r * 1.42, by - r * 1.25
        d.polygon([P(sx + 22 * math.cos(a) * (1 if k % 2 == 0 else 0.45), sy + 22 * math.sin(a) * (1 if k % 2 == 0 else 0.45))
                   for k, a in enumerate(np.linspace(0, 2 * math.pi, 13)[:-1])], fill=255)
    elif kind == 'worm':           # WORM: a fat wriggle with a head
        pts = [P(w * (0.1 + 0.8 * t), cy + h * 0.2 * math.sin(t * 2 * math.pi * 1.2)) for t in np.linspace(0, 1, 30)]
        d.line(pts, fill=255, width=S(h * 0.56), joint='curve')
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - S(h * 0.28), p[1] - S(h * 0.28), p[0] + S(h * 0.28), p[1] + S(h * 0.28)], fill=255)
    elif kind == 'spin':           # NUDGE: a round spin tag with an arrowhead tab
        r = h * 0.44
        d.ellipse([P(cx - r, cy - r), P(cx + r, cy + r)], fill=255)
        d.polygon([P(cx + r * 0.55, cy - r * 1.12), P(cx + r * 1.22, cy - r * 0.62), P(cx + r * 0.62, cy - r * 0.2)], fill=255)
    return m


KIND = {'NUDGE': 'spin', 'WORM': 'worm', 'BREACH': 'burst', 'GUARD': 'shield', 'TIMEBOMB': 'bomb'}
SIZE = {'NUDGE': (176, 164), 'WORM': (236, 150), 'BREACH': (226, 176), 'GUARD': (168, 186), 'TIMEBOMB': (200, 176)}
FILL = {'NUDGE': ((200, 192, 255), (150, 136, 240)), 'WORM': ((150, 236, 120), (80, 178, 70)), 'BREACH': ((255, 92, 186), (226, 30, 140)),
        'GUARD': ((110, 170, 255), (52, 104, 220)), 'TIMEBOMB': ((255, 170, 70), (236, 110, 30))}


def sticker(a, curl=False, grey=False):
    """one action as a die-cut vinyl sticker: the action-shaped body (ink key, extrude), its glyph, the name in Anton, the type
    word on the locked plate, the yellow cost dot and the key.  Returns the sticker_lib dict (SS)."""
    w, h = SIZE[a['id']]
    pad = 70
    CW, CH = S(w + 2 * pad), S(h + 2 * pad)
    body = Image.new('L', (CW, CH), 0)
    body.paste(_shape(KIND[a['id']], w, h, len(a['nm'])), (S(pad), S(pad)))
    art = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    key = body.filter(ImageFilter.MaxFilter(S(2.5) * 2 + 1))
    ext = Image.new('L', (CW, CH), 0)
    for i in range(1, S(6) + 1, 2):
        ext = SL.ImageChops.lighter(ext, SL.shift(key, i * 0.55, i))
    art = SL.over(art, SL.INK_DEEP, ext)
    art = SL.over(art, INK, key)
    top, bot = FILL[a['id']]
    tex = SL.vgrad_tex(CW, CH, top, bot); tex.putalpha(body)
    art = Image.alpha_composite(art, tex)
    hl = SL.ImageChops.subtract(body, SL.shift(body, 0, S(3))).filter(ImageFilter.GaussianBlur(S(0.8)))
    art = SL.over(art, (255, 255, 255), SL.scale_mask(hl, 0.5))
    d = ImageDraw.Draw(art)
    ox, oy = S(pad), S(pad)
    # glyph (the borrowed card icon) in ink, upper part
    gm = glyph_mask(a['g'], S(min(w, h) * 0.30))
    gx, gy = ox + S(w / 2) - gm.width // 2, oy + S(h * 0.30) - gm.height // 2
    if a['id'] == 'TIMEBOMB':
        gx -= S(w * 0.06)
    art.paste(Image.new('RGBA', gm.size, PAPER + (255,)), (gx + S(2), gy + S(2)), gm)
    art.paste(Image.new('RGBA', gm.size, INK + (255,)), (gx, gy), gm)
    # the name: Anton, paper fill, ink key line, a hard drop
    fs = 40 if len(a['nm']) <= 6 else 33
    f = ImageFont.truetype(ANTON, S(fs))
    nx, ny = ox + S(w / 2 - (w * 0.05 if a['id'] == 'TIMEBOMB' else 0)), oy + S(h * 0.60)
    d.text((nx + S(3), ny + S(4)), a['nm'], font=f, fill=SL.INK_DEEP + (255,), anchor='mm', stroke_width=S(3), stroke_fill=SL.INK_DEEP + (255,))
    d.text((nx, ny), a['nm'], font=f, fill=PAPER + (255,), anchor='mm', stroke_width=S(3), stroke_fill=INK + (255,))
    # the type word on its locked plate
    col, dk, tc = plate_cols(a['fam'])
    tf = ImageFont.truetype(ANTON, S(20))
    tw_ = d.textlength(a['fam'], font=tf) + S(16)
    tx, ty = nx, ny + S(32)
    d.polygon([(tx - tw_ / 2 + S(5), ty - S(13)), (tx + tw_ / 2 + S(5), ty - S(13)), (tx + tw_ / 2 - S(5), ty + S(13)), (tx - tw_ / 2 - S(5), ty + S(13))],
              fill=col + (255,), outline=INK + (255,), width=S(2))
    d.text((tx, ty + S(1)), a['fam'], font=tf, fill=tc + (255,), anchor='mm')
    # the yellow cost dot (bible 3.18), top-left; greyed when it can't be afforded
    cx_, cy_ = ox + S(16), oy + S(14)
    d.ellipse([cx_ - S(19), cy_ - S(19), cx_ + S(19), cy_ + S(19)], fill=((255, 210, 40) if not grey else (150, 150, 150)) + (255,), outline=INK + (255,), width=S(3))
    d.text((cx_, cy_ + S(1)), str(a['cost']), font=ImageFont.truetype(ANTON, S(26)), fill=INK + (255,), anchor='mm')
    # the key, bottom-right, as a small ink chip
    kx, ky = ox + S(w - 12), oy + S(h - 10)
    d.rectangle([kx - S(14), ky - S(14), kx + S(14), ky + S(14)], fill=INK + (255,), outline=PAPER + (255,), width=S(2))
    d.text((kx, ky + S(1)), a['key'], font=ImageFont.truetype(MONO, S(20)), fill=PAPER + (255,), anchor='mm')
    # die-cut white border (bible: thin at hand size), gloss 0.22, optional peel curl
    sd = SL.build_sticker(art, border=8, close=10, gloss_k=0.22, gloss_pos=0.30,
                          curl=dict(corner='tr', amount=0.48) if curl else None)
    if grey:                        # can't afford: greyscale vinyl at 80 %
        im = sd['img']
        g = ImageOps.grayscale(im.convert('RGB')).convert('RGB')
        g = Image.blend(g, Image.new('RGB', g.size, (90, 90, 96)), 0.15).convert('RGBA')
        g.putalpha(im.split()[3].point(lambda v: int(v * 0.8)))
        sd = dict(sd, img=g)
    return sd


def stick(img, sd, cx, cy, ang, scale=1.0, lift=0.0, squash=(1.0, 1.0)):
    """put a sticker on the glass at (cx, cy) 1x: contact shadow, plus a long soft shadow when lifted"""
    im = sd['img']
    if scale != 1.0 or squash != (1.0, 1.0):
        im = im.resize((int(im.width * scale * squash[0]), int(im.height * scale * squash[1])), Image.BICUBIC)
    im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    a = im.split()[3]
    x, y = int(S(cx) - im.width / 2), int(S(cy) - im.height / 2)
    for blur, op, off in ((S(2), 0.55 * (1 - lift), (S(2), S(3))), (S(10 + 22 * lift), 0.38 + 0.1 * lift, (S(6 + 26 * lift), S(10 + 34 * lift)))):
        if op <= 0:
            continue
        sh = Image.new('RGBA', im.size, (6, 4, 10, 0))
        sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * op)))
        img.alpha_composite(sh, (x + off[0], y + off[1]))
    img.alpha_composite(im, (x, y))
    return (x, y, im)


def liner_outline(img, a, cx, cy, ang):
    """the faint liner outline left on the glass where a sticker was peeled from (bible 3.18 step 3)"""
    w, h = SIZE[a['id']]
    m = Image.new('L', (S(w + 60), S(h + 60)), 0)
    m.paste(_shape(KIND[a['id']], w, h, len(a['nm'])), (S(30), S(30)))
    m = m.filter(ImageFilter.MaxFilter(S(9) * 2 + 1))
    edge = SL.ImageChops.subtract(m, SL.erode(m, S(1.4)))
    edge = edge.rotate(ang, resample=Image.BICUBIC, expand=True)
    fill = m.rotate(ang, resample=Image.BICUBIC, expand=True)
    L = Layer()
    x, y = int(S(cx) - edge.width / 2), int(S(cy) - edge.height / 2)
    L.im.paste(Image.new('RGBA', fill.size, (230, 228, 220, 255)), (x, y), fill.point(lambda v: int(v * 0.10)))
    L.im.paste(Image.new('RGBA', edge.size, (210, 208, 200, 255)), (x, y), edge.point(lambda v: int(v * 0.55)))
    comp(img, L)


# where each sticker is slapped on the glass (x, y, angle): varied, overlapping where it still reads
POS = {'NUDGE': (122, 262, 8), 'WORM': (368, 250, -6), 'BREACH': (146, 470, -5), 'GUARD': (388, 488, 7), 'TIMEBOMB': (190, 676, 4)}


# =============================================================================================== HUD pieces (bible: RAM terminal pips, SEND IT over EXECUTE)
def ram_row(img, F, cost=0, paid=0):
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 24, 112, 516, 152
    glass(d, (x0, y0, x1, y1))
    ym = (y0 + y1) / 2
    text(d, (x0 + 16, ym), 'RAM', F['m20'], TEXT_MID + (255,), anchor='lm')
    en, emax = BOARD['hud']['energy']
    en -= paid
    for k in range(emax):
        x = x0 + 72 + k * 34
        box = [S(x), S(ym - 11), S(x + 26), S(ym + 11)]
        if k < en - cost:
            d.rectangle(box, fill=(26, 143, 184, 255), outline=CYAN + (255,), width=S(2))
        elif k < en:
            d.rectangle(box, fill=GLASS_ + (255,), outline=CYAN + (255,), width=S(2))
            for t in range(0, 4):
                d.line([(S(x + t * 7), S(ym + 11)), (S(x + t * 7 + 8), S(ym - 11))], fill=HARM + (255,), width=S(2))
        else:
            d.rectangle(box, outline=(60, 110, 130, 255), width=S(2))
    text(d, (x0 + 186, ym), '%d/%d' % (en, emax) if not cost else '%d \u2192 %d' % (en, en - cost), F['a26'], (TEXT_HI if not cost else (255, 120, 110)) + (255,), anchor='lm')
    sx = x0 + 290
    for wd, side in BOARD['hud']['status']:
        col = CYAN if side == 'buff' else (255, 181, 71)
        w_ = tw(d, wd, F['m18'])
        d.rounded_rectangle([S(sx - 6), S(ym - 13), S(sx + w_ + 6), S(ym + 13)], radius=S(11), outline=col + (255,), width=S(2))
        text(d, (sx, ym), wd, F['m18'], col + (255,), anchor='lm')
        sx += w_ + 22
    comp(img, L)


GLASS_ = TR.GLASS


def piles(img, F, disc=None):
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 24, 824, 516, 872
    glass(d, (x0, y0, x1, y1))
    dr, dc = BOARD['hud']['piles']
    if disc is not None:
        dc = disc
    x = x0 + 18
    for wd, n in (('DRAW', dr), ('DISCARD', dc), ('EXHAUST', 0)):
        text(d, (x, (y0 + y1) / 2), wd, F['m20'], TEXT_MID + (255,), anchor='lm')
        x += tw(d, wd, F['m20']) + 10
        text(d, (x, (y0 + y1) / 2), str(n), F['a28'], TEXT_HI + (255,), anchor='lm')
        x += 54
    # UNDO: a terminal chip (bible 3.1)
    ux0, uy0 = 24, 892
    d.rectangle([S(ux0), S(uy0), S(ux0 + 150), S(uy0 + 44)], fill=GLASS_ + (230,), outline=CYAN + (255,), width=S(2))
    text(d, (ux0 + 14, uy0 + 22), 'UNDO', F['a24'], TEXT_HI + (255,), anchor='lm')
    text(d, (ux0 + 100, uy0 + 23), '[Z]', F['m18'], TEXT_MID + (255,), anchor='lm')
    comp(img, L)


_SEND = {}


def send_it(img, F):
    """SEND IT: the pink vinyl verb over the washed-out system word EXECUTE (bible 1.3, 3.1)"""
    L = Layer(); d = L.d
    text(d, (1770, 984), 'EXECUTE', TR.font(MONO, 64), (120, 200, 230, 70), anchor='mm')
    text(d, (1770, 1062), '> turn_resolve.exe [SPACE]', F['m18'], (120, 200, 230, 150), anchor='mm')
    comp(img, L)
    if 'sd' not in _SEND:
        art = SL.lettering(['SEND IT'], 72, [('grad', (255, 110, 196), (222, 24, 136))], key_w=5, extrude=7, seed=3, jitter=3)
        _SEND['sd'] = SL.build_sticker(art, border=10, gloss_k=0.22)
    stick(img, _SEND['sd'], 1772, 994, 4, scale=0.9)


# =============================================================================================== the right flank: corp board + HUD (insp_render), our HUD bits
MODE = {'panel': None}
_fp = IR.forecast_panel


def _panel(d, F, box, st, aim_hint=None):
    x0, y0, x1, y1 = box
    hint = MODE.get('hint')
    if MODE.get('steps'):           # hover: the totals line, then the hovered wedge's numbered steps (designer ruling)
        steps = MODE['steps']
        h = 136 + 31 * len(steps) + 12
        glass(d, (x0, y0, x1, y0 + h))
        _fp_head(d, F, x0, y0, x1, st)
        d.line([(S(x0 + 14), S(y0 + 128)), (S(x1 - 14), S(y0 + 128))], fill=(40, 90, 110, 255), width=S(1.5))
        for k, line in enumerate(steps):
            x = x0 + 18
            f = F['a26'] if k == 0 else F['a24']
            for s_, col in line:
                text(d, (x, y0 + 150 + 31 * k), s_, f, col + (255,), anchor='lm')
                x += tw(d, s_, f) + 10
        return
    h = 136 + (52 if len(st['hud']['forecast']) > 1 else 0) + 28 * len(hint or []) + (10 if hint else 0)
    _fp(d, F, (x0, y0, x1, y0 + h), st, aim_hint=hint)


def _fp_head(d, F, x0, y0, x1, st):
    owned = sum(1 for g in st['segs'] if g['owner'] == 'us')
    text(d, (x0 + 18, y0 + 24), 'OWNED', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (x0 + 18, y0 + 62), '%d/12' % owned, F['num'], TEXT_HI + (255,), anchor='lm')
    text(d, (x0 + 128, y0 + 64), '\u2192 2', F['mid'], HARM + (255,), anchor='lm')
    text(d, (x0 + 230, y0 + 24), 'END TURN FORECAST', F['m20'], TEXT_MID + (255,), anchor='lm')
    IR.spans(d, x0 + 230, y0 + 62, [('+0 taken', S_GAIN), ('\u22121 lost', S_HARM)], F['a28'], gap=16)
    text(d, (x0 + 230, y0 + 100), 'health 27 \u2192 26', F['a28'], S_HARM + (255,), anchor='lm')


IR.forecast_panel = _panel
IR.end_turn_btn = lambda *a, **k: None


# =============================================================================================== the wheel and the pen forecast
def draw_wheel(img, st, F):
    s2 = copy.deepcopy(st)
    TR.draw_rim(img, s2)
    L = Layer()
    for i, g in enumerate(s2['segs']):
        if g['owner'] != 'us':
            a0, a1, am = TR.seg_angles(i, s2['rot'])
            TR.draw_corp_seg(L, g, a0, a1, am)
    comp(img, L)
    TR.draw_runner_segs(img, s2['segs'], s2['rot'])
    TR.draw_segment_marks(img, s2, F['seg_type'], F['seg_num'], F['seg_small'])
    TR.draw_hub(img, s2, F['hub_big'], F['mid'], F['hub_small'])
    TR.draw_pointers(img, s2)
    hv = s2.get('hover')
    if hv is not None:              # the hovered wedge: the system layer's cyan inspect outline
        L = Layer()
        a0, a1, am = TR.seg_angles(hv, s2['rot'])
        L.d.polygon(TR.wedge(TR.R_IN - 2, TR.R_OUT + 2, a0 - 0.006, a1 + 0.006), outline=CYAN + (255,), width=S(5))
        comp(img, L)


def pen_outcomes(py, pr, st, skip=()):
    """B-088 outcome marks as grease pencil on the glass, straddling each wedge's inner edge:
    yellow '→ n' / 'TAKEN' + tick (our plan's result), red 'LOST −1 HP' with a slash (a loss)"""
    for i, o in (st.get('outcomes') or {}).items():
        if i in skip:
            continue
        a0, a1, am = TR.seg_angles(i, st['rot'])
        x, y = CX + (TR.R_IN + 8) * math.cos(am), CY + (TR.R_IN + 8) * math.sin(am)
        t = o['t'].replace('\n', ' ').replace('\u2212', '-')
        if o['k'] == 'hp':
            # the marker font has no arrow glyph: the arrow is a pencil stroke, then the number
            py.arrow([(x - 34, y + 2), (x - 18, y), (x - 4, y + 1)], width=5, head=11)
            py.text(t.split()[-1], x + 14, y, 36, angle=4)
        elif o['k'] == 'take':
            x, y = CX + (TR.R_IN - 30) * math.cos(am), CY + (TR.R_IN - 30) * math.sin(am)      # on the dark ring, clear of the wedge word
            py.text('TAKEN', x, y, 30, angle=-6)
            py.tick(x + 52, y - 2, 11, 6)
        else:
            pr.text('LOST -1 HP', x, y, 28, angle=-4)
            pr.stroke(pr.wobble([(x - 62, y + 18), (x + 62, y + 15)], 0.8), 5)


def legal_marks(py, st):
    """legal targets: a grease-pencil loop round each legal wedge's label (bible 3.18: a pencil loop writes round a valid target)"""
    for i in st.get('focus', []):
        a0, a1, am = TR.seg_angles(i, st['rot'])
        x, y = CX + 280 * math.cos(am), CY + 280 * math.sin(am)
        py.circle(x, y, 62, 74, width=6, tilt=am + math.pi / 2, start=-2.0 + i)


def qpts(p0, mid, p1, n=10):
    return [tuple(np.array(p0) * (1 - u) ** 2 + np.array(mid) * 2 * u * (1 - u) + np.array(p1) * u * u) for u in np.linspace(0, 1, n)]


def polar(r, a):
    return (CX + r * math.cos(a), CY + r * math.sin(a))


def pen_badge(p, n, x, y, size=26):
    """a resolution number in pencil: the number with a hand loop round it"""
    p.text(n, x, y, size)
    p.circle(x, y, 30, 19, width=4, tilt=-0.1, over=0.4)


# =============================================================================================== left flank
def left(img, F, held=None, cost=0, paid=0, disc=None, skip=()):
    L = Layer(); run_health(L.d, F, 24, 516, 18); comp(img, L)
    ram_row(img, F, cost=cost, paid=paid)
    order = ['WORM', 'NUDGE', 'GUARD', 'BREACH', 'TIMEBOMB']        # stacking order on the glass
    for aid in order:
        a = [x for x in ACTS if x['id'] == aid][0]
        x, y, ang = POS[aid]
        if aid == held or aid in skip:
            liner_outline(img, a, x, y, ang)
            continue
        stick(img, sticker(a, curl=False, grey=bool(a.get('why'))), x, y, ang)
    piles(img, F, disc)
    # the can't-use reason, scrawled next to TIME BOMB in red pencil
    pr = Wax(PEN_R, 31)
    pr.text('needs 4', 380, 672, 34, angle=-8)
    pr.arrow([(330, 690), (300, 698), (282, 694)], width=5, head=14)
    pr.ink_ss(img)


def right(img, F, st):
    IR.df_right(img, F, st, False)
    send_it(img, F)


# =============================================================================================== the plates
def render_rest():
    F = F_all(); st = copy.deepcopy(BOARD)
    MODE.update(hint=None, steps=None)
    img = base_image()
    draw_wheel(img, st, F)
    py, pr = Wax(PEN_Y, 1), Wax(PEN_R, 2)
    pen_outcomes(py, pr, st)
    py.ink_ss(img); pr.ink_ss(img)
    left(img, F)
    right(img, F, st)
    return img


HELD = (668, 138, -8)             # where the peeled BREACH is held (1x), its tilt: above the wheel's top left, clear of every pencil mark


def render_aim():
    F = F_all(); st = copy.deepcopy(PLAY)
    MODE.update(hint=['rule: 3 damage to a corp segment next to', 'yours.  Enter: slap  \u00b7  Esc: stick back'], steps=None)
    img = base_image()
    draw_wheel(img, st, F)
    left(img, F, held='BREACH', cost=1)
    a = [x for x in ACTS if x['id'] == 'BREACH'][0]
    # the plan in yellow pencil: loops round the legal wedges, the line from the sticker over the rim to FIREWALL, the outcome
    py, pr = Wax(PEN_Y, 3), Wax(PEN_R, 4)
    legal_marks(py, st)
    am = TR.seg_angles(st['aim'], st['rot'])[2]
    route = [(HELD[0] + 116, HELD[1] - 16)] + [polar(446, a_) for a_ in np.linspace(math.radians(-104), am - 0.10, 9)] + [polar(330, am - 0.02)]
    py.arrow(route, width=7, head=24)
    py.text('-3', polar(486, math.radians(-50))[0], polar(486, math.radians(-50))[1], 36, angle=-10)
    pen_outcomes(py, pr, st)
    py.ink_ss(img); pr.ink_ss(img)
    # the peeled sticker: lifted, scaled up, straightened, the peel curl, the long soft shadow
    stick(img, sticker(a, curl=True), HELD[0], HELD[1], HELD[2], scale=1.04, lift=1.0)
    right(img, F, st)
    return img


def frame_play(step):
    """one frame of the play: place | dissolve | resolved (full screen; df3_play crops the wheel from it)"""
    F = F_all()
    st = copy.deepcopy(PLAY)
    a = [x for x in ACTS if x['id'] == 'BREACH'][0]
    if step != 'resolved':
        st['segs'][2]['hp'] = 5
    MODE.update(hint=None, steps=None)
    img = base_image()
    draw_wheel(img, st, F)
    am = TR.seg_angles(2, st['rot'])[2]
    sx, sy = polar(298, am)
    rot = -math.degrees(am) - 2                  # the sticker's long axis along the wedge's radius, a little off-true
    py, pr = Wax(PEN_Y, 5), Wax(PEN_R, 6)
    if step == 'place':
        # slapped: squash 1.13 / 0.86, white contact ring; the pencil wipes off stroke-first (only the outcome is left)
        L = Layer()
        L.d.ellipse([S(sx - 92), S(sy - 92), S(sx + 92), S(sy + 92)], outline=(255, 255, 255, 200), width=S(4))
        comp(img, L)
        stick(img, sticker(a), sx, sy, rot, scale=0.68, squash=(1.13, 0.86))
        pen_outcomes(py, pr, st)
    elif step == 'dissolve':
        dissolve(img, F, a, sx, sy, rot, am)
        pen_outcomes(py, pr, st)
    else:
        pen_outcomes(py, pr, st)
        # the result: the damage as a bare Anton number (bible: live big numbers), the wedge at 2
        L = Layer()
        x, y = polar(440, am + 0.10)
        text(L.d, (x, y), '\u22123', F['a48'], HARM + (255,), stroke=2, sfill=INK + (255,))
        comp(img, L)
    py.ink_ss(img); pr.ink_ss(img)
    left(img, F, skip=('BREACH',), paid=1, disc=4)
    st2 = copy.deepcopy(st)
    right(img, F, st2)
    return img


def dissolve(img, F, a, sx, sy, rot, am):
    """Dissolve A (bible 3.18): a scan front runs down the sticker; behind it each 17 px cell decodes to a 0/1 in the source
    colour (white-hot just behind the front), then the bits stream round the rim, never across the wheel face"""
    sd = sticker(a)
    im0 = sd['img']; im0 = im0.resize((int(im0.width * 0.68), int(im0.height * 0.68)), Image.BICUBIC)      # the placed size
    im = im0.rotate(rot, resample=Image.BICUBIC, expand=True)
    a_ = np.asarray(im.split()[3], np.float32) / 255.0
    h_, w_ = a_.shape
    ys = np.nonzero(a_.max(1) > 0.5)[0]
    front = ys.min() + (ys.max() - ys.min()) * 0.55
    keep = a_.copy(); keep[: int(front), :] = 0
    im2 = im.copy(); im2.putalpha(Image.fromarray((keep * 255).astype(np.uint8)))
    x0, y0 = int(S(sx) - im.width / 2), int(S(sy) - im.height / 2)
    img.alpha_composite(im2, (x0, y0))
    L = Layer(); d = L.d
    rng = np.random.default_rng(5)
    src = FILL['BREACH'][1]
    f = TR.font(MONO, 22)
    cell = S(17)
    rgb = np.asarray(im.convert('RGB'))
    for yy in range(0, int(front), cell):
        for xx in range(0, w_, cell):
            if a_[min(h_ - 1, yy + cell // 2), min(w_ - 1, xx + cell // 2)] < 0.5 or rng.random() < 0.18:
                continue
            hot = front - yy < cell * 2.2
            ch = '1' if rng.random() < 0.5 else '0'
            jx, jy = rng.normal(0, S(3)), -rng.uniform(0, S(10)) * (1 - (front - yy) / max(front, 1))
            col = (255, 248, 240) if hot else src
            d.text((x0 + xx + jx, y0 + yy + jy), ch, font=f, fill=col + (255,), anchor='mm', stroke_width=S(1), stroke_fill=col + (255,))
    # the stream: bits leaving round the rim, toward the wedge's own edge (they go round the rim, never across the face)
    for k in range(26):
        t = k / 25
        aa = am - 0.55 + 0.5 * t
        r = TR.R_RIM + 4 + 6 * math.sin(t * 9)
        x, y = polar(r, aa)
        ch = '1' if k % 3 else '0'
        d.text((S(x), S(y)), ch, font=f, fill=src + (int(110 + 140 * t),), anchor='mm', stroke_width=S(1), stroke_fill=src + (int(110 + 140 * t),))
    comp(img, L)


def render_play():
    """three panels across: place, dissolve, resolved, cropped from full frames; a small full-screen copy of the result"""
    frames = [frame_play(s) for s in ('place', 'dissolve', 'resolved')]
    out = Image.new('RGB', (W, H), (14, 14, 18))
    d = ImageDraw.Draw(out)
    fb = ImageFont.truetype(ANTON, 40); fa = ImageFont.truetype(ANTON, 30); fm = ImageFont.truetype(MONO, 20)
    d.text((40, 26), 'PLAY: BREACH on FIREWALL.  1 peel (see df3_aim)  \u2192  2 place  \u2192  3 dissolve  \u2192  4 resolve', font=fb, fill=TEXT_HI)
    box = (880, 150, 1400, 670)                     # the wheel's upper right, around wedge 2 (stops short of the corp board)
    caps = [('2  PLACE', 'slapped on FIREWALL: squash, white contact ring;', 'the pencil wipes off; RAM is paid'),
            ('3  DISSOLVE', 'a scan front decodes the sticker into 0/1 bits', 'in its own pink; they run round the rim'),
            ('4  RESOLVE', 'the effect plays from the slap point: -3,', 'FIREWALL 5 -> 2, TAKEN in pencil')]
    for k, fr in enumerate(frames):
        c = fr.crop((S(box[0]), S(box[1]), S(box[2]), S(box[3]))).resize((600, 600), Image.LANCZOS).convert('RGB')
        x = 30 + k * 630
        out.paste(c, (x, 96))
        d.rectangle([x - 2, 94, x + 601, 697], outline=(80, 90, 104), width=2)
        d.text((x + 4, 712), caps[k][0], font=fa, fill=PINK)
        d.text((x + 4, 756), caps[k][1], font=fm, fill=TEXT_MID)
        d.text((x + 4, 782), caps[k][2], font=fm, fill=TEXT_MID)
    small = frames[2].resize((448, 252), Image.LANCZOS).convert('RGB')
    out.paste(small, (1442, 812))
    d.rectangle([1440, 810, 1891, 1065], outline=(80, 90, 104), width=2)
    d.text((40, 830), 'After the play (full screen, right):', font=fa, fill=TEXT_HI)
    for k, ln in enumerate(['the BREACH sticker is gone from the glass; only its liner outline is left', 'RAM 3 -> 2, DISCARD 3 -> 4; the wedge result is in pencil (TAKEN)',
                            'the HUD totals line updates: +1 taken, -1 lost, owned 3, health 27 -> 26']):
        d.text((40, 880 + 32 * k), ln, font=fm, fill=TEXT_MID)
    return out


def render_hover():
    F = F_all(); st = copy.deepcopy(FORECAST)
    steps = [[('YOUR ICE', (92, 225, 255)), ('3 \u2192 retaken', S_HARM), ('\u00b7 health \u22121', S_HARM)],
             [('11.1', S_SCHED), ('plan STRIKE: \u22122', S_MID)], [('11.2', S_SCHED), ('your GUARD blocks 2', S_MID)],
             [('13.1', S_SCHED), ('CORE counterattack: \u22123 \u2192 retaken', S_MID)], [('16.1', S_SCHED), ('lost: run health 27 \u2192 26', S_MID)]]
    MODE.update(hint=None, steps=steps)
    img = base_image()
    draw_wheel(img, st, F)
    py, pr = Wax(PEN_Y, 7), Wax(PEN_R, 8)
    a_ice = TR.seg_angles(11, st['rot'])[2]
    a_core = TR.seg_angles(10, st['rot'])[2]
    # 11.1: the plan STRIKE from the hub (red: a hit on yours)
    # 11.1: the plan STRIKE from the hub (red: a hit on yours), entering the wedge's right side, clear of the LOST mark
    p0 = polar(TR.R_HUB + 12, math.radians(-90)); p1 = polar(236, math.radians(-109))
    pr.arrow(qpts(p0, polar(196, math.radians(-94)), p1, 8), width=7, head=20)
    pen_badge(pr, '11.1', 1018, 422, 24); pr.text('-2', 1074, 424, 32)
    # 13.1: CORE's counterattack (red), round the outside of the labels; its label outside the rim
    q0 = polar(334, a_core + 0.04); q1 = polar(336, math.radians(-129))
    pr.arrow(qpts(q0, polar(410, math.radians(-138)), q1, 10), width=7, head=20)
    lx, ly = polar(474, math.radians(-146))
    pen_badge(pr, '13.1', lx - 12, ly, 24); pr.text('-3', lx + 46, ly + 2, 32)
    # 11.2: your GUARD blocks 2 (yellow: ours), a bracket on the wedge's outer edge, its label above the rim
    a0, a1, _ = TR.seg_angles(11, st['rot'])
    py.stroke(py.wobble([polar(TR.R_OUT - 14, a) for a in np.linspace(a0 + 0.06, a1 - 0.06, 10)], 0.6), 7)
    bx, by = polar(478, math.radians(-118))
    pen_badge(py, '11.2', bx - 40, by, 24); py.text('BLOCK 2', bx + 64, by + 2, 30, angle=-3)
    py.stroke(py.wobble([(bx + 10, by + 18), polar(TR.R_OUT + 4, a_ice + 0.02)], 0.6), 4)
    # 16.1: the loss, on the outcome (moved left of the 11.1 arrow) and (in the HUD) on health
    pen_outcomes(py, pr, st, skip=(11,))
    x, y = polar(TR.R_IN + 10, math.radians(-128))
    pr.text('LOST -1 HP', x, y, 28, angle=-4)
    pen_badge(pr, '16.1', 874, 442, 22)
    py.ink_ss(img); pr.ink_ss(img)
    left(img, F)
    right(img, F, st)
    return img


def sheet():
    names = [('df3_rest', 'DEFACE v3, rest', 'deface stickers on the glass; forecast in grease pencil'),
             ('df3_aim', 'DEFACE v3, aim', 'BREACH peeled and held; yellow pencil to FIREWALL'),
             ('df3_play', 'DEFACE v3, play', 'place, dissolve into bits, resolve (TAKEN)'),
             ('df3_hover', 'DEFACE v3, hover', 'your ICE: numbered pencil arrows + HUD steps')]
    tw_, th_ = 940, 529
    pad, cap = 14, 64
    sh = Image.new('RGB', (2 * tw_ + 3 * pad, 2 * (th_ + cap) + 3 * pad + 50), (14, 14, 18))
    d = ImageDraw.Draw(sh)
    f = ImageFont.truetype(MONO, 18); fa = ImageFont.truetype(ANTON, 22); fb = ImageFont.truetype(ANTON, 30)
    d.text((pad, 14), 'DEFACE v3: vinyl stickers on the glass, grease pencil for aim and forecast', font=fb, fill=TEXT_HI)
    for k, (n, t, c) in enumerate(names):
        im = Image.open(OUT + n + '.png').resize((tw_, th_), Image.LANCZOS)
        x = pad + (k % 2) * (tw_ + pad); y = 60 + pad + (k // 2) * (th_ + cap + pad)
        sh.paste(im, (x, y))
        d.text((x + 4, y + th_ + 6), '%s   %s.png' % (t, n), font=fa, fill=TEXT_HI)
        d.text((x + 4, y + th_ + 38), c, font=f, fill=TEXT_MID)
    sh.save(OUT + 'df3_sheet.jpg', quality=90)
    print('ok', OUT + 'df3_sheet.jpg')


R = dict(df3_rest=render_rest, df3_aim=render_aim, df3_play=render_play, df3_hover=render_hover)

if __name__ == '__main__':
    for n in (sys.argv[1:] or ['df3_rest', 'df3_aim', 'df3_play', 'df3_hover', 'sheet']):
        if n == 'sheet':
            sheet(); continue
        img = R[n]()
        if img.size != (W, H):
            img = img.resize((W, H), Image.LANCZOS)
        img.convert('RGB').save(OUT + n + '.png')
        print('ok', OUT + n + '.png')
