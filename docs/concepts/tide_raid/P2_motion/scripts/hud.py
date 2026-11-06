"""HUD chips + hand cards (drawn at 1920x1080 then scaled to the 1280x720 output). Wordless: numerals and icons only."""
import math
from m2 import *

_F = {}


def F(sz):
    if sz not in _F:
        _F[sz] = font(sz)
    return _F[sz]


def c8(col, a=1.0):
    c = np.clip(np.asarray(col, np.float32), 0, 1)
    return (int(c[0] * 255 + .5), int(c[1] * 255 + .5), int(c[2] * 255 + .5), int(clamp01(a) * 255 + .5))


def chip(d, box, edge=None, a=0.92):
    d.rounded_rectangle(box, 8, fill=c8(hexc('0B0F2A'), a), outline=c8(edge if edge is not None else PAL['LATT'], .9), width=2)


def house(d, x, y, s, col):
    d.polygon([(x - s, y), (x, y - s * .9), (x + s, y), (x + s * .7, y), (x + s * .7, y + s * .8), (x - s * .7, y + s * .8), (x - s * .7, y)], fill=c8(col))


def flame(d, x, y, s, col):
    d.polygon([(x, y - s), (x + s * .6, y), (x + s * .35, y + s * .8), (x - s * .35, y + s * .8), (x - s * .6, y)], fill=c8(col))
    d.polygon([(x, y - s * .2), (x + s * .25, y + s * .3), (x, y + s * .75), (x - s * .25, y + s * .3)], fill=c8(PAL['INK']))


def bio(d, x, y, s, col):
    d.ellipse([x - s, y - s, x + s, y + s], outline=c8(col), width=3)
    for i in range(3):
        a = math.radians(90 + 120 * i)
        d.ellipse([x + s * .55 * math.cos(a) - s * .28, y + s * .55 * math.sin(a) - s * .28, x + s * .55 * math.cos(a) + s * .28, y + s * .55 * math.sin(a) + s * .28], fill=c8(col))


def hud_chips(hp=44, hpmax=50, heat=80, infected=0, healthy=8, hp_col=None, k=1.0, dy=0.0, hp_flash=0.0, inf_col=None):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    hc = PAL['WARM'] if hp_col is None else hp_col
    chip(d, (22, 14 + dy, 246, 70 + dy))
    house(d, 52, 44 + dy, 16, PAL['WARM'] if hp_col is None else hp_col)
    d.text((82, 26 + dy), str(hp), font=F(38), fill=c8(hc))
    d.text((158, 46 + dy), '/%d' % hpmax, font=F(20), fill=c8(PAL['LATT']))
    chip(d, (262, 14 + dy, 420, 70 + dy))
    flame(d, 290, 44 + dy, 16, PAL['HEAT'])
    d.text((322, 26 + dy), str(heat), font=F(38), fill=c8(PAL['HEAT']))
    chip(d, (1590, 14 + dy, 1898, 70 + dy))
    bio(d, 1622, 44 + dy, 14, PAL['VEIN'] if inf_col is None else inf_col)
    d.text((1650, 26 + dy), str(infected), font=F(34), fill=c8(PAL['VEIN']))
    d.line([(1720, 52 + dy), (1800, 36 + dy)], fill=c8(PAL['WARM']), width=3)
    d.rectangle([1812, 30 + dy, 1830, 58 + dy], outline=c8(PAL['TEAL']), width=3)
    d.text((1840, 26 + dy), str(healthy), font=F(34), fill=c8(PAL['TEAL']))
    a = np.asarray(im, np.float32) / 255
    a[..., 3] *= k
    return a


def card_img(typ, glyph='wall', back=False, lime=False):
    cw, ch = 104, 150
    ss = 2
    im = Image.new('RGBA', (cw * ss + 40, ch * ss + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = 20, 20
    box = [ox, oy, ox + cw * ss, oy + ch * ss]
    if lime:
        d.rounded_rectangle([ox - 8, oy - 8, ox + cw * ss + 8, oy + ch * ss + 8], 24, outline=c8(PAL['LIME']), width=6)
    if back:
        d.rounded_rectangle(box, 18, fill=c8(hexc('0B1236')), outline=c8(PAL['LATT']), width=4)
        for i in range(-3, 8):
            d.line([(ox + i * 40, oy), (ox + i * 40 + 120, oy + ch * ss)], fill=c8(PAL['LATT'], .5), width=3)
        d.ellipse([ox + cw - 34, oy + ch - 34, ox + cw + 34, oy + ch + 34], outline=c8(PAL['LATT']), width=5)
    else:
        d.rounded_rectangle(box, 18, fill=c8(PAL['BONE']), outline=c8(PAL['INK']), width=3)
        d.rounded_rectangle([ox + 3, oy + 3, ox + cw * ss - 3, oy + 56], 16, fill=c8(PAL[typ]))
        d.rectangle([ox + 3, oy + 36, ox + cw * ss - 3, oy + 56], fill=c8(PAL[typ]))
        gx, gy = ox + cw, oy + 30
        ink = c8(PAL['INK'])
        if typ == 'D':
            d.line([(gx - 16, gy - 12), (gx + 6, gy), (gx - 16, gy + 12)], fill=ink, width=7)
        elif typ == 'N':
            d.arc([gx - 20, gy - 12, gx, gy + 12], 180, 360, fill=ink, width=6)
            d.arc([gx, gy - 12, gx + 20, gy + 12], 0, 180, fill=ink, width=6)
        else:
            d.polygon([(gx - 14, gy - 12), (gx + 8, gy - 12), (gx + 8, gy + 12), (gx - 14, gy + 12)], outline=ink, width=6)
        # body glyph: shield (wall) or arrow (move) in ink
        cx, cy = ox + cw, oy + 140
        if glyph == 'wall':
            d.polygon([(cx - 44, cy - 40), (cx + 44, cy - 40), (cx + 44, cy + 14), (cx, cy + 52), (cx - 44, cy + 14)], outline=ink, width=7)
            for yy in (cy - 22, cy - 4):
                d.line([(cx - 36, yy), (cx + 36, yy)], fill=ink, width=5)
        else:
            d.arc([cx - 40, cy - 40, cx + 40, cy + 40], 180, 400, fill=ink, width=8)
            d.polygon([(cx + 36, cy + 4), (cx + 52, cy + 24), (cx + 22, cy + 24)], fill=ink)
    return im


def hand(slots, hud_k=1.0):
    """slots: list of dict(x,y,ang,sc,typ,glyph,k,back,lime) in 1920 px."""
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for s in slots:
        ci = card_img(s['typ'], s.get('glyph', 'wall'), s.get('back', False), s.get('lime', False))
        sc = s.get('sc', 1.0) * 0.5 * 0.9
        n = (max(4, int(ci.width * sc * s.get('sx', 1.0))), max(4, int(ci.height * sc)))
        ci = ci.resize(n, Image.LANCZOS)
        # soft drop shadow
        al = ci.split()[3].filter(ImageFilter.GaussianBlur(9))
        sh = Image.new('RGBA', ci.size, c8(PAL['INK'], 1))
        sh.putalpha(al.point(lambda v: int(v * .55)))
        if s.get('ang', 0):
            ci = ci.rotate(s['ang'], expand=True, resample=Image.BICUBIC)
            sh = sh.rotate(s['ang'], expand=True, resample=Image.BICUBIC)
        x, y = int(s['x'] - ci.width / 2), int(s['y'] - ci.height / 2)
        k = s.get('k', 1.0)
        if k < 1:
            ci.putalpha(ci.split()[3].point(lambda v: int(v * k)))
            sh.putalpha(sh.split()[3].point(lambda v: int(v * k)))
        im.alpha_composite(sh, (x + 4, y + 10)) if 0 <= x and 0 <= y else None
        try:
            im.alpha_composite(ci, (x, y))
        except ValueError:
            pass
    return np.asarray(im, np.float32) / 255


def slots_default(lift=0.0, spread=108, y=1000):
    out = []
    types = [('D', 'wall'), ('N', 'wall'), ('E', 'move'), ('N', 'move'), ('E', 'wall')]
    for i, (t, g) in enumerate(types):
        tt = i - 2
        out.append(dict(x=W / 2 + tt * spread, y=y + abs(tt) ** 1.6 * 8 - lift, ang=-tt * 3.4, typ=t, glyph=g))
    return out


def comp_hud(img720, layers):
    """layers: list of (RGBA 1920x1080 float arrays); downscale to the output and composite over img720."""
    for a in layers:
        if a is None:
            continue
        pil = Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA').resize((OW, OH), Image.LANCZOS)
        q = np.asarray(pil, np.float32) / 255
        al = q[..., 3:4]
        img720 = img720 * (1 - al) + q[..., :3] * al
    return img720
