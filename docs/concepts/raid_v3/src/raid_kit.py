"""raid_kit: the Deface v3 raid toolkit (grid, enamel corp tokens, operative / weapon / device stickers, HUD pieces).

Imports the Takeover v3 toolkit read-only (insp_deface3, insp_deface3b, insp_render, tk_render, sticker_lib19); nothing there
is changed.  Layers (bible 1.2 + designer rulings 2026-11-15):
  runner objects  = vinyl stickers  (operatives, weapons, devices, safehouse, site, statuses, verbs)
  player markup   = grease pencil   (routes, forecast, reach, tallies, values beside statuses)
  corp machinery  = enamel          (units, path bands, INCOMING board, path name plates)
  system          = CRT glass       (rows, HUD line, chips)
"""
import math, random, sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/takeover/inspiration')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
import insp_deface3 as D3
import insp_deface3b as D3b
from insp_deface3 import (Wax, PEN_Y, PEN_R, SL, IR, TR, S, text, Layer, comp, INK, PAPER, PINK, HARM, CYAN, TEXT_HI, TEXT_MID,
                          ANTON, MONO, W, H, SS, F_all, base_image, glass, stick)
from tk_states import GAIN as S_GAIN, HARM as S_HARM, HI as S_HI, PLAN as S_PLAN, MID as S_MID, SCHED as S_SCHED

TEAL, TEAL_D, TEAL_HI, GLAZE, K_TYPE = IR.TEAL, IR.TEAL_D, IR.TEAL_HI, IR.GLAZE, IR.K_TYPE
GLASS_ = TR.GLASS
GOLD = (255, 210, 40)
tw = IR.tw


# =============================================================================================== grid
class Grid:
    def __init__(self, cols, rows, x0, y0, cell):
        self.cols, self.rows, self.x0, self.y0, self.cell = cols, rows, x0, y0, cell

    def cc(self, c, r):
        return (self.x0 + self.cell * (c + 0.5), self.y0 + self.cell * (r + 0.5))

    def box(self, c, r):
        return (self.x0 + self.cell * c, self.y0 + self.cell * r, self.x0 + self.cell * (c + 1), self.y0 + self.cell * (r + 1))

    def name(self, c, r):
        return 'abcdefghijk'[c] + str(r + 1)

    @property
    def x1(self):
        return self.x0 + self.cols * self.cell

    @property
    def y1(self):
        return self.y0 + self.rows * self.cell


def thick(d, pts, w, col):
    """a thick polyline with round joins (1x points)"""
    P = [(S(x), S(y)) for x, y in pts]
    d.line(P, fill=col, width=S(w))
    for x, y in P:
        d.ellipse([x - S(w / 2), y - S(w / 2), x + S(w / 2), y + S(w / 2)], fill=col)


def offset_line(pts, off):
    """the polyline moved sideways by off px (left of travel), mitred at the corners"""
    p = np.array(pts, float)
    out = []
    for i in range(len(p)):
        if i == 0:
            t = p[1] - p[0]
        elif i == len(p) - 1:
            t = p[i] - p[i - 1]
        else:
            a = (p[i] - p[i - 1]); a /= np.linalg.norm(a)
            b = (p[i + 1] - p[i]); b /= np.linalg.norm(b)
            t = a + b
            if np.linalg.norm(t) < 1e-6:
                t = a
        t = t / np.linalg.norm(t)
        n = np.array([t[1], -t[0]])
        k = 1.0
        if 0 < i < len(p) - 1:
            a = (p[i] - p[i - 1]); a /= np.linalg.norm(a)
            k = 1.0 / max(0.6, abs(n @ np.array([a[1], -a[0]])))
        out.append(tuple(p[i] + n * off * k))
    return out


def draw_city(img, F, G, paths, open_cells=(), panel=None, seed=4):
    """the raid grid under monitor glass: dark building slabs, asphalt roads, the corp path bands in Solace enamel"""
    L = Layer(); d = L.d
    px0, py0, px1, py1 = panel or (G.x0 - 64, G.y0 - 52, G.x1 + 64, G.y1 + 20)
    d.rectangle([S(px0), S(py0), S(px1), S(py1)], fill=(7, 10, 15, 238))
    road = set(open_cells)
    for p in paths:
        road |= set(p['cells'])
    rng = random.Random(seed)
    for c in range(G.cols):
        for r in range(G.rows):
            x0, y0, x1, y1 = G.box(c, r)
            if (c, r) in road:
                d.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(19, 21, 27, 255))
                continue
            i = 5
            d.rectangle([S(x0 + i + 3), S(y0 + i + 4), S(x1 - i + 3), S(y1 - i + 4)], fill=(3, 3, 6, 255))
            d.rectangle([S(x0 + i), S(y0 + i), S(x1 - i), S(y1 - i)], fill=(34, 39, 50, 255))
            d.line([(S(x0 + i), S(y0 + i)), (S(x1 - i), S(y0 + i))], fill=(60, 67, 82, 255), width=S(2))
            d.line([(S(x0 + i), S(y0 + i)), (S(x0 + i), S(y1 - i))], fill=(50, 56, 70, 255), width=S(2))
            for _ in range(rng.randint(1, 2)):                     # roof plant: vents, water tanks
                w_, h_ = rng.uniform(10, 22), rng.uniform(8, 16)
                vx, vy = rng.uniform(x0 + 14, x1 - 14 - w_), rng.uniform(y0 + 14, y1 - 14 - h_)
                d.rectangle([S(vx), S(vy), S(vx + w_), S(vy + h_)], fill=(42, 48, 60, 255), outline=(26, 30, 38, 255), width=S(1))
    # kerbs between road and slabs
    for (c, r) in road:
        x0, y0, x1, y1 = G.box(c, r)
        for dc, dr, seg in ((0, -1, [(x0, y0), (x1, y0)]), (0, 1, [(x0, y1), (x1, y1)]), (-1, 0, [(x0, y0), (x0, y1)]), (1, 0, [(x1, y0), (x1, y1)])):
            if (c + dc, r + dr) not in road and 0 <= c + dc < G.cols and 0 <= r + dr < G.rows:
                d.line([(S(seg[0][0]), S(seg[0][1])), (S(seg[1][0]), S(seg[1][1]))], fill=(44, 48, 58, 255), width=S(2))
    comp(img, L)
    # the corp path bands: Solace enamel (teal glaze edge, deep teal body, porcelain highlight)
    L = Layer(); d = L.d
    for p in paths:
        pts = p['pts']
        thick(d, pts, 44, INK + (255,))
    for p in paths:
        thick(d, p['pts'], 38, TEAL + (255,))
    for p in paths:
        thick(d, p['pts'], 31, (30, 66, 72, 255))
    for p in paths:
        thick(d, offset_line(p['pts'], 8), 3, GLAZE + (70,))
    comp(img, L)
    # system: coordinates and the glass frame
    L = Layer(); d = L.d
    for c in range(G.cols):
        text(d, (G.cc(c, 0)[0], G.y1 + 10), 'abcdefghijk'[c], F['m16'], CYAN + (120,))
    for r in range(G.rows):
        text(d, (G.x0 - 14, G.cc(0, r)[1]), str(r + 1), F['m16'], CYAN + (120,))
    d.rectangle([S(px0), S(py0), S(px1), S(py1)], outline=(40, 90, 110, 255), width=S(2))
    c_ = 18
    for (x, y, dx, dy) in ((px0, py0, 1, 1), (px1, py0, -1, 1), (px0, py1, 1, -1), (px1, py1, -1, -1)):
        d.line([(S(x), S(y + dy * c_)), (S(x), S(y)), (S(x + dx * c_), S(y))], fill=CYAN + (255,), width=S(4))
    comp(img, L)
    # glass sheen: one soft diagonal band
    a = np.zeros((H * SS, W * SS), np.float32)
    yy, xx = np.mgrid[S(py0):S(py1), S(px0):S(px1)].astype(np.float32) / SS
    u = (xx - px0) + 0.55 * (yy - py0)
    band = np.exp(-((u - (px1 - px0) * 0.42) / 120.0) ** 2) * 0.07
    a[S(py0):S(py1), S(px0):S(px1)] = band
    lay = Image.new('RGBA', (W * SS, H * SS), (200, 240, 255, 0))
    lay.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    img.alpha_composite(lay)


def path_tag(img, F, x, y, s, anchor='l'):
    """the corp's path name on a small enamel plate (corp machinery): slate, teal edge"""
    L = Layer(); d = L.d
    f = F['a20']
    w = tw(d, s, f) + 22
    x0 = x if anchor == 'l' else x - w
    d.rectangle([S(x0 + 3), S(y - 13), S(x0 + w + 3), S(y + 17)], fill=INK + (255,))
    d.rectangle([S(x0), S(y - 16), S(x0 + w), S(y + 14)], fill=(52, 60, 72, 255), outline=TEAL + (255,), width=S(2))
    text(d, (x0 + 11, y - 1), s, f, K_TYPE + (255,), anchor='lm')
    comp(img, L)


def route(pr, pts, off=24, head=True):
    """a corp route in red pencil along the street, beside the enamel band"""
    o = offset_line(pts, off)
    if head:
        pr.arrow(o, width=5, head=16)
    else:
        pr.stroke(SL.catmull(pr.wobble(o, 1.0), 14), 5)


def entry_mark(pr, x, y, letter):
    pr.circle(x, y, 19, 19, width=5, start=-2.0, over=0.4, tilt=0)
    pr.text(letter, x, y + 1, 28)


# =============================================================================================== enamel corp tokens
_TOK = {}


def _tok_poly(kind, c, r):
    if kind in ('trooper', 'drone'):
        return None
    if kind == 'bike':
        return [(c, c - r * 1.2), (c + r * 1.2, c), (c, c + r * 1.2), (c - r * 1.2, c)]
    if kind == 'heavy':
        return [(c - r * 0.95, c - r * 0.95), (c + r * 0.95, c - r * 0.95), (c + r * 0.95, c + r * 0.95), (c - r * 0.95, c + r * 0.95)]
    if kind == 'riot':
        return [(c - r, c - r * 0.95), (c + r, c - r * 0.95), (c + r * 0.95, c + r * 0.25), (c, c + r * 1.15), (c - r * 0.95, c + r * 0.25)]
    if kind == 'sniper':
        return [(c, c - r * 1.2), (c + r * 1.15, c + r * 0.85), (c - r * 1.15, c + r * 0.85)]
    if kind == 'wrecker':
        return [(c + r * 1.08 * math.cos(math.pi / 3 * k), c + r * 1.08 * math.sin(math.pi / 3 * k)) for k in range(6)]


def token_img(kind, hp, r=21):
    """one corp unit as an enamel token at SS: ink key + drop, slate body, Solace teal glaze edge, engraved hp"""
    key = (kind, hp, r)
    if key in _TOK:
        return _TOK[key]
    sz = S(r * 2 + 44)
    c = sz / 2
    R = S(r)
    m = Image.new('L', (sz, sz), 0); md = ImageDraw.Draw(m)
    poly = _tok_poly(kind, c, R)
    if poly is None:
        rr = R * (0.86 if kind == 'drone' else 1.0)
        md.ellipse([c - rr, c - rr, c + rr, c + rr], fill=255)
    else:
        md.polygon(poly, fill=255)
    im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0))
    k = m.filter(ImageFilter.MaxFilter(S(2) * 2 + 1))
    im = SL.over(im, INK, SL.shift(k, S(3), S(4)))
    im = SL.over(im, INK, k)
    tex = SL.vgrad_tex(sz, sz, (104, 116, 132), (46, 52, 63)); tex.putalpha(m)
    im = Image.alpha_composite(im, tex)
    edge = SL.ImageChops.subtract(m, SL.erode(m, S(2.6)))
    im = SL.over(im, TEAL, edge)
    hl = SL.ImageChops.subtract(SL.erode(m, S(3)), SL.shift(SL.erode(m, S(3)), 0, S(3))).filter(ImageFilter.GaussianBlur(S(0.7)))
    im = SL.over(im, GLAZE, SL.scale_mask(hl, 0.55))
    d = ImageDraw.Draw(im)
    if kind == 'drone':                                     # flies: a dashed halo
        for j in range(12):
            a0 = j * 30
            d.arc([c - R * 1.42, c - R * 1.42, c + R * 1.42, c + R * 1.42], a0, a0 + 17, fill=TEAL_HI + (255,), width=S(2.5))
    f = ImageFont.truetype(ANTON, S(22 if r >= 20 else 18))
    cy = c + (S(3) if kind == 'sniper' else (-S(2) if kind == 'riot' else 0))
    d.text((c, cy + S(1.5)), str(hp), font=f, fill=(150, 165, 182, 255), anchor='mm')        # engraved: lit lower lip
    d.text((c, cy), str(hp), font=f, fill=(16, 19, 25, 255), anchor='mm')
    _TOK[key] = im
    return im


def token(img, kind, x, y, hp, count=None, alpha=1.0, r=21):
    im = token_img(kind, hp, r)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(im, (int(S(x) - im.width / 2), int(S(y) - im.height / 2)))
    if count:
        L = Layer(); d = L.d
        s_ = '\u00d7%d' % count
        f = TR.font(ANTON, 19)
        w = tw(d, s_, f) + 12
        bx, by = x - r * 0.7 - w, y - r * 0.95            # top-left: the route runs on the right of the band
        a = int(255 * alpha)
        d.rounded_rectangle([S(bx - 2 + 2), S(by - 11 + 3), S(bx + w + 2), S(by + 11 + 3)], radius=S(6), fill=INK + (a,))
        d.rounded_rectangle([S(bx - 2), S(by - 11), S(bx + w), S(by + 11)], radius=S(6), fill=TEAL + (a,), outline=INK + (a,), width=S(2))
        text(d, (bx + w / 2 - 1, by), s_, f, INK + (a,))
        comp(img, L)


def kill_burst(img, kind, x, y, hp=0, seed=3, r=21, spread=62):
    """a kill: the token breaks into 0/1 bits in its own enamel colours (slate body, teal edge), a few white-hot"""
    im = token_img(kind, hp, r)
    w, h = im.size
    rng = np.random.default_rng(seed)
    for k, (qx, qy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):            # the shell, cracked in four
        q = im.crop((qx * w // 2, qy * h // 2, (qx + 1) * w // 2, (qy + 1) * h // 2)).rotate(rng.uniform(-30, 30), expand=True, resample=Image.BICUBIC)
        q.putalpha(q.split()[3].point(lambda v: int(v * 0.75)))
        dx, dy = (qx - 0.5) * S(18), (qy - 0.5) * S(18)
        img.alpha_composite(q, (int(S(x) + dx - q.width / 2 + (qx - 0.5) * w / 2), int(S(y) + dy - q.height / 2 + (qy - 0.5) * h / 2)))
    L = Layer(); d = L.d
    f = TR.font(MONO, 20)
    for k in range(30):
        a = rng.uniform(0, 2 * math.pi); rr = rng.uniform(16, spread)
        bx, by = x + rr * math.cos(a), y + rr * math.sin(a) * 0.8
        col = (255, 248, 240) if rr < 26 else (TEAL_HI if k % 3 else (120, 132, 148))
        al = int(255 * (1.0 - 0.6 * (rr - 16) / max(1, spread - 16)))
        d.text((S(bx), S(by)), '1' if rng.random() < 0.5 else '0', font=f, fill=col + (al,), anchor='mm', stroke_width=S(1), stroke_fill=col + (al,))
    comp(img, L)


def pop(img, F, x, y, s, col=HARM):
    """a damage pop: bare Anton (live number)"""
    L = Layer()
    text(L.d, (x, y), s, F['a40'], col + (255,), stroke=2, sfill=INK + (255,))
    comp(img, L)


def tracer(img, p0, p1, col):
    L = Layer(); d = L.d
    d.line([(S(p0[0]), S(p0[1])), (S(p1[0]), S(p1[1]))], fill=col + (150,), width=S(5))
    d.line([(S(p0[0]), S(p0[1])), (S(p1[0]), S(p1[1]))], fill=(255, 250, 240, 230), width=S(1.6))
    comp(img, L)


# =============================================================================================== vinyl stickers
def vinyl(body, top, bot, deco=None, border=8, curl=None, grey=False, ext=6):
    """the D3 sticker recipe on any die-cut body (SS mask with padding): ink key, extrude, gradient vinyl, top light, deco, die-cut
    border, gloss band; grey = greyscale vinyl at 80 % (can't use)"""
    CW, CH = body.size
    art = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    key = body.filter(ImageFilter.MaxFilter(S(2.5) * 2 + 1))
    ex = Image.new('L', (CW, CH), 0)
    for i in range(1, S(ext) + 1, 2):
        ex = SL.ImageChops.lighter(ex, SL.shift(key, i * 0.55, i))
    art = SL.over(art, SL.INK_DEEP, ex)
    art = SL.over(art, INK, key)
    tex = SL.vgrad_tex(CW, CH, top, bot); tex.putalpha(body)
    art = Image.alpha_composite(art, tex)
    hl = SL.ImageChops.subtract(body, SL.shift(body, 0, S(3))).filter(ImageFilter.GaussianBlur(S(0.8)))
    art = SL.over(art, (255, 255, 255), SL.scale_mask(hl, 0.5))
    if deco:
        deco(ImageDraw.Draw(art), art)
    sd = SL.build_sticker(art, border=border, close=border + 2, gloss_k=0.22, gloss_pos=0.30,
                          curl=dict(corner='tr', amount=curl) if curl else None)
    if grey:
        im = sd['img']
        g = ImageOps.grayscale(im.convert('RGB')).convert('RGB')
        g = Image.blend(g, Image.new('RGB', g.size, (90, 90, 96)), 0.15).convert('RGBA')
        g.putalpha(im.split()[3].point(lambda v: int(v * 0.8)))
        sd = dict(sd, img=g)
    return sd


def anton_name(d, x, y, s, size):
    f = ImageFont.truetype(ANTON, S(size))
    d.text((x + S(3), y + S(4)), s, font=f, fill=SL.INK_DEEP + (255,), anchor='mm', stroke_width=S(3), stroke_fill=SL.INK_DEEP + (255,))
    d.text((x, y), s, font=f, fill=PAPER + (255,), anchor='mm', stroke_width=S(3), stroke_fill=INK + (255,))


def cost_dot(d, x, y, n, grey=False):
    d.ellipse([x - S(17), y - S(17), x + S(17), y + S(17)], fill=((255, 210, 40) if not grey else (150, 150, 150)) + (255,), outline=INK + (255,), width=S(3))
    d.text((x, y + S(1)), str(n), font=ImageFont.truetype(ANTON, S(24)), fill=INK + (255,), anchor='mm')


def star_poly(x, y, r, k=0.45):
    return [(x + (r if j % 2 == 0 else r * k) * math.cos(-math.pi / 2 + j * math.pi / 5), y + (r if j % 2 == 0 else r * k) * math.sin(-math.pi / 2 + j * math.pi / 5)) for j in range(10)]


# ---------------------------------------------------------------- operatives
OPS = {
    'KAI': dict(role='GUNNER', wpn='SMG', stars=2, lvl=3, reach=1, shape='oct', g='C_STRIKE', col=((255, 166, 96), (236, 96, 40))),
    'VEX': dict(role='SNIPER', wpn='RAIL', stars=1, lvl=2, reach=2, shape='tag', g='C_TRIG', col=((130, 204, 255), (52, 118, 228))),
    'MOTH': dict(role='TECH', wpn='JAMMER', stars=1, lvl=2, reach=1, shape='hex', g='PI_SPIN_CW', col=((168, 240, 130), (72, 176, 66))),
    'RUNE': dict(role='BRUISER', wpn='SHOTGUN', stars=1, lvl=1, reach=1, shape='shield', g='C_BRACE', col=((222, 176, 255), (146, 88, 232))),
}
OPW, OPH, OPPAD = 176, 156, 60


def _op_body(shape, w, h):
    m = Image.new('L', (S(w), S(h)), 0); d = ImageDraw.Draw(m)
    P = lambda pts: [(S(x * w), S(y * h)) for x, y in pts]
    if shape == 'oct':
        k = 0.2
        d.polygon(P([(k, 0), (1 - k, 0), (1, k * 1.1), (1, 1 - k * 1.1), (1 - k, 1), (k, 1), (0, 1 - k * 1.1), (0, k * 1.1)]), fill=255)
    elif shape == 'tag':
        d.polygon(P([(0.15, 0), (1, 0), (1, 1), (0.15, 1), (0, 0.5)]), fill=255)
    elif shape == 'hex':
        d.polygon(P([(0.22, 0), (0.78, 0), (1, 0.5), (0.78, 1), (0.22, 1), (0, 0.5)]), fill=255)
    else:
        m = D3._shape('shield', w, h, 5)
    return m


_OPS = {}


def op_sticker(oid, curl=None, grey=False):
    key = (oid, curl, grey)
    if key in _OPS:
        return _OPS[key]
    o = OPS[oid]
    w, h, pad = OPW, OPH, OPPAD
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    body.paste(_op_body(o['shape'], w, h), (S(pad), S(pad)))

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        gm = IR.glyph_mask(o['g'], S(36))
        gx, gy = ox + S(w / 2) - gm.width // 2, oy + S(h * 0.22) - gm.height // 2
        art.paste(Image.new('RGBA', gm.size, PAPER + (255,)), (gx + S(2), gy + S(2)), gm)
        art.paste(Image.new('RGBA', gm.size, INK + (255,)), (gx, gy), gm)
        anton_name(d, ox + S(w / 2), oy + S(h * 0.50), oid, 44 if len(oid) <= 3 else 40)
        tf = ImageFont.truetype(ANTON, S(19))
        tx, ty = ox + S(w / 2), oy + S(h * (0.77 if o['shape'] != 'shield' else 0.72))
        tw_ = d.textlength(o['role'], font=tf) + S(16)
        d.polygon([(tx - tw_ / 2 + S(5), ty - S(12)), (tx + tw_ / 2 + S(5), ty - S(12)), (tx + tw_ / 2 - S(5), ty + S(12)), (tx - tw_ / 2 - S(5), ty + S(12))],
                  fill=INK + (255,), outline=INK + (255,), width=S(2))
        d.text((tx, ty + S(1)), o['role'], font=tf, fill=o['col'][0] + (255,), anchor='mm')
        kx, ky = ox + S(w - 14), oy + S(h - 12)                     # the level chip
        d.rectangle([kx - S(18), ky - S(14), kx + S(18), ky + S(14)], fill=INK + (255,), outline=PAPER + (255,), width=S(2))
        d.text((kx, ky + S(1)), 'L%d' % o['lvl'], font=ImageFont.truetype(ANTON, S(20)), fill=PAPER + (255,), anchor='mm')

    sd = vinyl(body, o['col'][0], o['col'][1], deco, border=8, curl=curl, grey=grey)
    _OPS[key] = sd
    return sd


# ---------------------------------------------------------------- weapons (ink gear tags; stars are part of the sticker)
_WP = {}


def wpn_sticker(name, stars, cost=None, curl=None, grey=False):
    key = (name, stars, cost, curl, grey)
    if key in _WP:
        return _WP[key]
    f = ImageFont.truetype(ANTON, S(28))
    tl = ImageDraw.Draw(Image.new('L', (8, 8))).textlength(name, font=f) / SS
    lead = 34 if cost is not None else 0
    w, h, pad = int(lead + 16 + tl + 10 + stars * 22 + 14), 48, 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    ImageDraw.Draw(body).polygon([(S(pad + 10), S(pad)), (S(pad + w), S(pad)), (S(pad + w - 10), S(pad + h)), (S(pad), S(pad + h))], fill=255)

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        x = ox + S(lead + 16)
        d.text((x, oy + S(h / 2 + 1)), name, font=f, fill=PAPER + (255,), anchor='lm')
        x += S(tl + 10 + 10)
        for k in range(stars):
            d.polygon([(S(px) + x - S(0), S(py) + oy) for px, py in star_poly(k * 22, h / 2, 10)], fill=GOLD + (255,), outline=INK + (255,))
        if cost is not None:
            cost_dot(d, ox + S(20), oy + S(h / 2), cost)

    sd = vinyl(body, (58, 52, 70), (22, 19, 28), deco, border=6, curl=curl, grey=grey, ext=4)
    _WP[key] = sd
    return sd


# ---------------------------------------------------------------- devices (they stay on their cell: objects, not one-shot plays)
DEV = {'BARRICADE': ((255, 214, 60), (236, 166, 20)), 'MINE': ((255, 150, 90), (232, 84, 40)), 'SENTRY': ((140, 212, 255), (60, 130, 220)),
       'TAR': ((150, 130, 190), (84, 64, 120))}
_DV = {}


def _dev_body(kind, w, h):
    m = Image.new('L', (S(w), S(h)), 0); d = ImageDraw.Draw(m)
    if kind == 'BARRICADE':
        d.polygon([(S(8), S(0)), (S(w - 8), S(0)), (S(w), S(h * 0.62)), (S(0), S(h * 0.62))], fill=255)
        for fx in (0.16, 0.84):
            d.rectangle([S(w * fx - 7), S(h * 0.5), S(w * fx + 7), S(h)], fill=255)
    elif kind == 'MINE':
        r = min(w, h) * 0.36
        cx, cy = w / 2, h / 2
        d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=255)
        for k in range(8):
            a = k * math.pi / 4
            d.polygon([(S(cx + r * 0.8 * math.cos(a - 0.25)), S(cy + r * 0.8 * math.sin(a - 0.25))), (S(cx + r * 1.38 * math.cos(a)), S(cy + r * 1.38 * math.sin(a))),
                       (S(cx + r * 0.8 * math.cos(a + 0.25)), S(cy + r * 0.8 * math.sin(a + 0.25)))], fill=255)
    elif kind == 'SENTRY':
        r = min(w, h) * 0.40
        cx, cy = w * 0.42, h / 2
        d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], fill=255)
        d.rectangle([S(cx), S(cy - 8), S(w), S(cy + 8)], fill=255)
    else:
        rng = random.Random(9)
        for _ in range(7):
            r = rng.uniform(0.18, 0.3) * h
            x, y = rng.uniform(r, w - r), rng.uniform(r, h - r)
            d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=255)
    return m


DEVSZ = {'BARRICADE': (150, 70), 'MINE': (96, 96), 'SENTRY': (118, 92), 'TAR': (120, 86)}


def dev_sticker(kind, cost=None, curl=None):
    key = (kind, cost, curl)
    if key in _DV:
        return _DV[key]
    w, h = DEVSZ[kind]
    pad = 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    body.paste(_dev_body(kind, w, h), (S(pad), S(pad)))

    def deco(d, art):
        ox, oy = S(pad), S(pad)
        if kind == 'BARRICADE':                                  # hazard stripes, clipped to the body
            st = Image.new('L', art.size, 0); sd_ = ImageDraw.Draw(st)
            for k in range(-4, 14):
                x = ox + S(k * 22)
                sd_.polygon([(x, oy), (x + S(11), oy), (x + S(11) - S(h * 0.62), oy + S(h * 0.62)), (x - S(h * 0.62), oy + S(h * 0.62))], fill=255)
            st = SL.ImageChops.multiply(st, body.point(lambda v: 255 if v > 128 else 0))
            art.paste(Image.new('RGBA', art.size, INK + (255,)), (0, 0), st)
            fy = oy + S(h * 0.31)
            ff = ImageFont.truetype(ANTON, S(22))
            tl = d.textlength(kind, font=ff)
            d.rectangle([ox + S(w / 2) - tl / 2 - S(8), fy - S(14), ox + S(w / 2) + tl / 2 + S(8), fy + S(14)], fill=INK + (255,))
            d.text((ox + S(w / 2), fy + S(1)), kind, font=ff, fill=PAPER + (255,), anchor='mm')
        else:
            anton_name(d, ox + S(w * (0.42 if kind == 'SENTRY' else 0.5)), oy + S(h / 2), kind, 22 if kind != 'SENTRY' else 20)
        if cost is not None:
            cost_dot(d, ox + S(8), oy + S(6), cost)

    top, bot = DEV[kind]
    sd = vinyl(body, top, bot, deco, border=6, curl=curl, ext=4)
    _DV[key] = sd
    return sd


# ---------------------------------------------------------------- the safehouse, a site, small word stickers
_MISC = {}


def place_sticker(word, sub, top, bot, shape='house', w=118, h=104):
    key = (word, sub, shape)
    if key in _MISC:
        return _MISC[key]
    pad = 44
    body = Image.new('L', (S(w + 2 * pad), S(h + 2 * pad)), 0)
    d0 = ImageDraw.Draw(body)
    P = lambda pts: [(S(pad + x * w), S(pad + y * h)) for x, y in pts]
    if shape == 'house':
        d0.polygon(P([(0.5, 0), (1, 0.36), (1, 1), (0, 1), (0, 0.36)]), fill=255)
    elif shape == 'socket':
        d0.rounded_rectangle([S(pad), S(pad), S(pad + w), S(pad + h)], radius=S(20), fill=255)
    else:
        d0.polygon(P([(0.25, 0), (0.75, 0), (1, 0.5), (0.75, 1), (0.25, 1), (0, 0.5)]), fill=255)

    def deco(d, art):
        anton_name(d, S(pad + w / 2), S(pad + h * (0.58 if shape == 'house' else 0.44)), word, 30 if len(word) > 3 else 40)
        if sub:
            tf = ImageFont.truetype(ANTON, S(17))
            tx, ty = S(pad + w / 2), S(pad + h * (0.84 if shape == 'house' else 0.78))
            tl = d.textlength(sub, font=tf) + S(14)
            d.rectangle([tx - tl / 2, ty - S(11), tx + tl / 2, ty + S(11)], fill=INK + (255,))
            d.text((tx, ty + S(1)), sub, font=tf, fill=top + (255,), anchor='mm')

    sd = vinyl(body, top, bot, deco, border=7, ext=5)
    _MISC[key] = sd
    return sd


def word_sticker(word, top, bot, size=22, curl=False):
    """a temporary word / status as a small pill sticker (D3b.mini_sticker with our colours)"""
    D3b.STAT[word] = (top, bot)
    return D3b.mini_sticker(word, curl=curl)


STATUS = {'H': ((110, 170, 255), (52, 104, 220)), 'S': ((120, 220, 245), (40, 160, 200)), 'J': ((168, 240, 130), (72, 176, 66))}


def status_sticker(code):
    return word_sticker(code, *STATUS[code])


_VERB = {}


def verb_sticker(word, top=(255, 110, 196), bot=(222, 24, 136), size=72):
    k = (word, top)
    if k not in _VERB:
        art = SL.lettering([word], size, [('grad', top, bot)], key_w=5, extrude=7, seed=3, jitter=3)
        _VERB[k] = SL.build_sticker(art, border=10, gloss_k=0.22)
    return _VERB[k]


def greyed(sd, k=0.55):
    im = sd['img']
    g = ImageOps.grayscale(im.convert('RGB')).convert('RGB')
    g = Image.blend(g, Image.new('RGB', g.size, (70, 70, 78)), 0.35).convert('RGBA')
    g.putalpha(im.split()[3].point(lambda v: int(v * k)))
    return dict(sd, img=g)


def liner(img, sd, cx, cy, ang, scale=1.0):
    """the faint liner outline left on the glass / backing where a sticker was peeled from (bible 3.18 step 3)"""
    a = sd['img'].split()[3]
    if scale != 1.0:
        a = a.resize((int(a.width * scale), int(a.height * scale)), Image.BICUBIC)
    a = a.point(lambda v: 255 if v > 90 else 0).rotate(ang, resample=Image.BICUBIC, expand=True)
    edge = SL.ImageChops.subtract(a, SL.erode(a, S(1.4)))
    L = Layer()
    x, y = int(S(cx) - a.width / 2), int(S(cy) - a.height / 2)
    L.im.paste(Image.new('RGBA', a.size, (230, 228, 220, 255)), (x, y), a.point(lambda v: int(v * 0.08)))
    L.im.paste(Image.new('RGBA', a.size, (210, 208, 200, 255)), (x, y), edge.point(lambda v: int(v * 0.55)))
    comp(img, L)


def paste_flat(img, sd, cx, cy, ang=0.0, scale=1.0):
    """a sticker still on its backing sheet: no lift, a hairline cut shadow only"""
    im = sd['img']
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.BICUBIC)
    im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    x, y = int(S(cx) - im.width / 2), int(S(cy) - im.height / 2)
    sh = Image.new('RGBA', im.size, (60, 50, 40, 0))
    sh.putalpha(im.split()[3].filter(ImageFilter.GaussianBlur(S(1.2))).point(lambda v: int(v * 0.35)))
    img.alpha_composite(sh, (x + S(1), y + S(1)))
    img.alpha_composite(im, (x, y))


# =============================================================================================== pencil helpers
def pen_arrow_num(p, a, b, x, y, size=34, angle=-4):
    """'a → b' in pencil: the marker font has no arrow, so the arrow is a stroke"""
    p.text(str(a), x, y, size, angle=angle)
    p.arrow([(x + 16, y + 2), (x + 30, y), (x + 46, y + 1)], width=5, head=10)
    p.text(str(b), x + 64, y, size, angle=angle)


def pen_star(p, x, y, r=11, w=4):
    pts = star_poly(x, y, r, 0.42)
    p.stroke(p.wobble(pts + [pts[0], pts[1]], 0.5), w, taper=False)


def pen_hatch_box(p, x0, y0, x1, y1, step=18, w=6):
    """reach: a yellow pencil outline with short hatch ticks along its inside"""
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0 + 6)]
    p.stroke(p.wobble(pts, 1.2), w, taper=False)
    for x in np.arange(x0 + 10, x1 - 6, step):
        p.stroke([(x, y0 + 3), (x + 9, y0 + 13)], 3, taper=False)
        p.stroke([(x, y1 - 13), (x + 9, y1 - 3)], 3, taper=False)
    for y in np.arange(y0 + 22, y1 - 10, step):
        p.stroke([(x0 + 3, y), (x0 + 13, y + 9)], 3, taper=False)
        p.stroke([(x1 - 13, y), (x1 - 3, y + 9)], 3, taper=False)


def pen_stop(p, x, y0, y1, horiz=False):
    """the yellow stop bar where a path holds"""
    if horiz:
        p.stroke(p.wobble([(y0, x), (y1, x)], 0.8), 9, taper=False)
        for e in (y0, y1):
            p.stroke([(e, x - 12), (e, x + 12)], 6, taper=False)
    else:
        p.stroke(p.wobble([(x, y0), (x, y1)], 0.8), 9, taper=False)
        for e in (y0, y1):
            p.stroke([(x - 12, e), (x + 12, e)], 6, taper=False)


# =============================================================================================== HUD (left / right / bottom)
def core_tape(img, F, title, core, cmax, lose=0, gain_word=None):
    """the Safehouse core as the paper tape (the Takeover run-health tape); the forecast loss hatched red"""
    L = Layer(); d = L.d
    x0, x1, y0, h = 24, 516, 18, 86
    tape = [(S(x0 + 4), S(y0)), (S(x1 - 4), S(y0 + 4)), (S(x1 - 8), S(y0 + h)), (S(x0), S(y0 + h - 4))]
    IR.poly_shadow(d, tape, 4, 5)
    d.polygon(tape, fill=PAPER + (255,), outline=INK + (255,), width=S(3))
    text(d, (x0 + 18, y0 + 26), title, F['a26'], INK + (255,), anchor='lm')
    s_ = 'CORE %d/%d' % (core, cmax) if not lose else 'CORE %d \u2192 %d' % (core, core - lose)
    text(d, (x1 - 20, y0 + 26), s_, F['a28'], (INK if not lose else (200, 24, 30)) + (255,), anchor='rm')
    pw = (x1 - x0 - 40 - 6 * (cmax - 1)) / cmax
    for k in range(cmax):
        x = x0 + 18 + k * (pw + 6); box = [S(x), S(y0 + 50), S(x + pw), S(y0 + 74)]
        if k < core - lose:
            d.rectangle(box, fill=IR.GAIN + (255,), outline=INK + (255,), width=S(2))
        elif k < core:
            d.rectangle(box, fill=PAPER + (255,))
            for t in range(-1, 8):
                d.line([(S(x + t * 7), S(y0 + 74)), (S(x + t * 7 + 10), S(y0 + 50))], fill=HARM + (255,), width=S(2.2))
            d.rectangle(box, outline=INK + (255,), width=S(2))
        else:
            d.rectangle(box, fill=(196, 190, 176, 255), outline=INK + (255,), width=S(2))
    comp(img, L)


def rows(img, F, rnd, rmax, credits, cost=0):
    L = Layer(); d = L.d
    glass(d, (24, 112, 236, 152))
    text(d, (40, 132), 'ROUND', F['m20'], TEXT_MID + (255,), anchor='lm')
    text(d, (118, 132), '%d/%d' % (rnd, rmax), F['a28'], TEXT_HI + (255,), anchor='lm')
    glass(d, (248, 112, 516, 152))
    text(d, (264, 132), 'CREDITS', F['m20'], TEXT_MID + (255,), anchor='lm')
    IR.ram_coin(d, 374, 132, None, F['m16'], r=12, dim=False)
    s_ = str(credits) if not cost else '%d \u2192 %d' % (credits, credits - cost)
    text(d, (396, 132), s_, F['a28'], (TEXT_HI if not cost else (255, 120, 110)) + (255,), anchor='lm')
    comp(img, L)


CREW_POS = {'KAI': (136, 300, -6), 'VEX': (378, 292, 5), 'MOTH': (142, 548, 4), 'RUNE': (380, 556, -4)}
WPN_OFF = (78, -66, 10)                      # the weapon sticker on the operative's top-right corner (dx, dy, angle)


def crew(img, F, where, kills=None, skip=(), weapons=None, scale=1.0):
    """the CREW column: operatives on the bench are full stickers; placed ones leave a liner outline with their cell in pencil;
    'away:X' = at another site (grey vinyl, red pencil reason)"""
    L = Layer(); text(L.d, (26, 182), 'CREW', F['m20'], TEXT_MID + (255,), anchor='lm'); comp(img, L)
    py, pr = Wax(PEN_Y, 81), Wax(PEN_R, 82)
    for oid, (x, y, ang) in CREW_POS.items():
        st = where.get(oid)
        if oid in skip:
            continue
        sd = op_sticker(oid, grey=bool(st and st.startswith('away')))
        if st and not st.startswith('away'):
            liner(img, sd, x, y, ang, scale)
            py.text('on ' + st, x, y + 4, 34, angle=-5)
            continue
        stick(img, sd, x, y, ang, scale=scale)
        o = OPS[oid]
        wst = (weapons or {}).get(oid, o['stars'])
        if wst:
            stick(img, wpn_sticker(o['wpn'], wst, grey=bool(st)), x + WPN_OFF[0], y + WPN_OFF[1], WPN_OFF[2], scale=0.82)
        if st and st.startswith('away'):
            pr.text('at ' + st.split(':')[1], x + 20, y + 96, 30, angle=-6)
        if kills and oid in kills:
            kx, ky = x - 66, y + 92
            py.x(kx, ky, 11, 6)
            py.text(str(kills[oid]), kx + 36, ky + 2, 36, angle=-6)
    py.ink_ss(img); pr.ink_ss(img)


def left_foot(img, F, counts, undo=True):
    L = Layer(); d = L.d
    x0, y0, x1, y1 = 24, 824, 516, 872
    glass(d, (x0, y0, x1, y1))
    x = x0 + 16
    for wd, n in counts:
        text(d, (x, (y0 + y1) / 2), wd, F['m18'], TEXT_MID + (255,), anchor='lm')
        x += tw(d, wd, F['m18']) + 8
        text(d, (x, (y0 + y1) / 2), str(n), F['a26'], TEXT_HI + (255,), anchor='lm')
        x += 34
    if undo:
        ux0, uy0 = 24, 892
        d.rectangle([S(ux0), S(uy0), S(ux0 + 170), S(uy0 + 44)], fill=GLASS_ + (230,), outline=CYAN + (255,), width=S(2))
        text(d, (ux0 + 14, uy0 + 22), 'UNDO', F['a24'], TEXT_HI + (255,), anchor='lm')
        text(d, (ux0 + 120, uy0 + 23), '[Z]', F['m18'], TEXT_MID + (255,), anchor='lm')
    comp(img, L)


def chip(img, F, x0, y0, word, key, w=None, sub=None):
    L = Layer(); d = L.d
    w = w or (tw(d, word, F['a24']) + tw(d, key, F['m18']) + 46)
    d.rectangle([S(x0), S(y0), S(x0 + w), S(y0 + 44)], fill=GLASS_ + (230,), outline=CYAN + (255,), width=S(2))
    text(d, (x0 + 14, y0 + 22), word, F['a24'], TEXT_HI + (255,), anchor='lm')
    text(d, (x0 + w - 14, y0 + 23), key, F['m18'], TEXT_MID + (255,), anchor='rm')
    if sub:
        text(d, (x0 + 2, y0 + 62), sub, F['m18'], TEXT_MID + (255,), anchor='lm')
    comp(img, L)
    return x0 + w


def hud_line(img, F, label, spans, box=(556, 956, 1364, 1006), ticks=None):
    """the system forecast line under the map: the same facts as the pencil, one line"""
    L = Layer(); d = L.d
    x0, y0, x1, y1 = box
    glass(d, box)
    ym = (y0 + y1) / 2
    text(d, (x0 + 16, ym), label, F['m18'], TEXT_MID + (255,), anchor='lm')
    x = x0 + 22 + tw(d, label, F['m18'])
    for s_, col in spans:
        text(d, (x, ym), s_, F['a26'], col + (255,), anchor='lm')
        x += tw(d, s_, F['a26']) + 12
    if ticks:
        n, m = ticks
        sw = (x1 - x0 - 24) / m
        for k in range(m):
            bx = x0 + 12 + k * sw
            d.rectangle([S(bx + 2), S(y1 - 7), S(bx + sw - 2), S(y1 - 3)], fill=(CYAN if k < n else (40, 70, 84)) + (255,))
    comp(img, L)


# ---------------------------------------------------------------- right: the corp's INCOMING board (enamel)
def mini_shape(d, kind, x, y, r=9):
    c = 0
    poly = _tok_poly(kind, 0, r)
    if poly is None:
        d.ellipse([S(x - r), S(y - r), S(x + r), S(y + r)], fill=(70, 80, 94, 255), outline=TEAL + (255,), width=S(2))
        if kind == 'drone':
            d.ellipse([S(x - r * 1.5), S(y - r * 1.5), S(x + r * 1.5), S(y + r * 1.5)], outline=TEAL_HI + (255,), width=S(1.2))
    else:
        d.polygon([(S(x + px), S(y + py)) for px, py in poly], fill=(70, 80, 94, 255), outline=TEAL + (255,))


def incoming(img, F, site, heat, rounds, y1=470, now=0):
    """rounds: list of (head, [(path, kind, label, n)]); the NOW ticket carries the live schedule edge"""
    L = Layer(); d = L.d
    x0, x1, y0 = 1404, 1898, 18
    d.rectangle([S(x0 + 4), S(y0 + 5), S(x1 + 4), S(y1 + 5)], fill=INK + (255,))
    d.rectangle([S(x0), S(y0), S(x1), S(y1)], fill=(48, 55, 66, 255), outline=TEAL + (255,), width=S(3))
    d.rectangle([S(x0 + 3), S(y0 + 3), S(x1 - 3), S(y0 + 44)], fill=(70, 80, 94, 255))
    d.line([(S(x0 + 3), S(y0 + 44)), (S(x1 - 3), S(y0 + 44))], fill=TEAL + (255,), width=S(2))
    for rx, ry in ((x0 + 12, y0 + 12), (x1 - 12, y0 + 12), (x0 + 12, y1 - 12), (x1 - 12, y1 - 12)):
        d.ellipse([S(rx - 4), S(ry - 4), S(rx + 4), S(ry + 4)], fill=IR.CLOCK_LT + (255,), outline=INK + (255,), width=S(1))
    text(d, (x0 + 28, y0 + 23), 'SOLACE', F['a24'], TEAL_HI + (255,), anchor='lm')
    text(d, (x0 + 118, y0 + 24), 'raid order', F['m20'], K_TYPE + (255,), anchor='lm')
    text(d, (x1 - 28, y0 + 24), site, F['m20'], TEXT_MID + (255,), anchor='rm')
    text(d, (x0 + 22, y0 + 76), 'INCOMING', F['a30'], K_TYPE + (255,), anchor='lm')
    text(d, (x1 - 22, y0 + 76), 'HEAT %d' % heat, F['a26'], TEXT_MID + (255,), anchor='rm')
    y = y0 + 106
    th = 78 if len(rounds) > 3 else 92
    for k, (head, groups) in enumerate(rounds):
        v = (1.0, 0.74, 0.6, 0.5)[min(3, abs(k - now))]
        body = tuple(int(c * v) for c in (196, 205, 214))
        edge = S_SCHED if k == now else tuple(int(c * v) for c in TEAL)
        pts = [(S(x0 + 22), S(y)), (S(x1 - 22), S(y)), (S(x1 - 22), S(y + th - 10)), (S(x0 + 22), S(y + th - 10))]
        IR.poly_shadow(d, pts, 3, 4)
        d.polygon(pts, fill=body + (255,), outline=edge + (255,), width=S(4 if k == now else 2))
        text(d, (x0 + 36, y + 20), head, F['tick'], INK + (255,), anchor='lm')
        gx = x0 + 44
        for path, kind, label, n in groups:
            gy = y + 48
            if path:
                text(d, (gx, gy), path, F['a20'], (150, 20, 30, 255), anchor='lm')
                gx += 18
            mini_shape(d, kind, gx + 8, gy)
            s_ = '%s \u00d7%d' % (label, n)
            text(d, (gx + 22, gy), s_, F['m18'], (34, 40, 50, 255), anchor='lm')
            gx += 22 + tw(d, s_, F['m18']) + 22
        y += th
    comp(img, L)


# ---------------------------------------------------------------- right: the shop as a peel-off sticker sheet
SHOP = [('w', 'SHOTGUN', 1, 3, (1530, 572)), ('w', 'RAIL', 1, 4, (1770, 572)),
        ('d', 'BARRICADE', None, 3, (1500, 688)), ('d', 'MINE', None, 2, (1660, 688)), ('d', 'SENTRY', None, 4, (1800, 688))]
SHEET_BOX = (1410, 498, 1892, 768)


def offer_sd(o, curl=None):
    k, nm, stars, cost, _ = o
    return wpn_sticker(nm, stars, cost=cost, curl=curl) if k == 'w' else dev_sticker(nm, cost=cost, curl=curl)


def shop_sheet(img, F, peeled=None, reroll=True, credits_left=None):
    x0, y0, x1, y1 = SHEET_BOX
    L = Layer(); d = L.d
    pts = [(x0 + 4, y0), (x1, y0 + 6), (x1 - 3, y1), (x0, y1 - 4)]
    d.polygon([(S(x + 5), S(y + 7)) for x, y in pts], fill=(4, 3, 6, 200))
    d.polygon([(S(x), S(y)) for x, y in pts], fill=(232, 228, 218, 255), outline=(150, 144, 132, 255))
    # the printed liner: header, perforation
    text(d, (x0 + 18, y0 + 24), 'BLACK MARKET', F['a24'], INK + (255,), anchor='lm')
    text(d, (x0 + 160, y0 + 25), 'peel to buy', F['m18'], (110, 104, 96, 255), anchor='lm')
    text(d, (x1 - 16, y0 + 25), '5 offers', F['m18'], (110, 104, 96, 255), anchor='rm')
    for xx in range(int(x0 + 10), int(x1 - 10), 14):
        d.line([(S(xx), S(y0 + 44)), (S(xx + 7), S(y0 + 44))], fill=(170, 164, 152, 255), width=S(1.5))
    rng = np.random.default_rng(2)
    for _ in range(260):                                    # paper tooth
        px, py = rng.uniform(x0 + 6, x1 - 6), rng.uniform(y0 + 6, y1 - 6)
        d.point((S(px), S(py)), fill=(200, 194, 182, 255))
    comp(img, L)
    for o in SHOP:
        sd = offer_sd(o)
        x, y = o[4]
        if peeled == o[1]:
            a = sd['img'].split()[3].resize((int(sd['img'].width * 0.82), int(sd['img'].height * 0.82))).point(lambda v: 255 if v > 90 else 0)
            Lh = Layer()
            xx, yy = int(S(x) - a.width / 2), int(S(y) - a.height / 2)
            Lh.im.paste(Image.new('RGBA', a.size, (246, 244, 236, 255)), (xx, yy), a)          # the glossy liner where it was
            e = SL.ImageChops.subtract(a, SL.erode(a, S(1.3)))
            Lh.im.paste(Image.new('RGBA', a.size, (160, 154, 142, 255)), (xx, yy), e)
            comp(img, Lh)
            continue
        paste_flat(img, sd, x, y, 0, 0.82)
    if reroll:
        chip(img, F, 1410, 784, 'REROLL (Q)', '2c', w=236)
    if credits_left is not None:
        pass


def send_it(img, F, system='START ROUND 1', state='ready', word='SEND IT', key='[SPACE]'):
    """the pink verb sticker over the washed-out system word (bible 1.3); 'busy' = greyed with a RESOLVING chip"""
    cx, cy = 1716, 930
    L = Layer(); d = L.d
    if system:
        text(d, (cx, cy - 2), system, TR.font(MONO, 52), (120, 200, 230, 95), anchor='mm')
    if state != 'busy':
        text(d, (cx, cy + 66), key, F['m18'], (120, 200, 230, 170), anchor='mm')
    comp(img, L)
    sd = verb_sticker(word)
    if state == 'busy':
        stick(img, greyed(sd), cx + 4, cy, 4, scale=0.9)
        chip(img, F, cx - 96, cy + 44, 'RESOLVING', '', w=192)
    else:
        stick(img, sd, cx + 4, cy, 4, scale=0.9)
