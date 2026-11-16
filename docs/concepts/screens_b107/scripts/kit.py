"""B-107 screens: shared components (PIL, 2x supersampled via ui_lib). REBEL_CELL's own vocabulary: die-cut vinyl stickers,
corp paper, navy terminal glass, pencil marks, the round 17 glyphs, the old-pass portrait busts. Solace only."""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps
from ui_lib import *   # noqa: F401,F403  (K, W, H, font, text, rrect, rect, line, poly, ellipse, layer, rotate_paste, glow, sticker, postit, stamp, ...)

ART = 'D:/rc_art/art-pass/docs/concepts/'
A = 'D:/rc_scratch/b107/assets/'
OUT = ART + 'screens_b107/'

INK = (14, 10, 22, 255); INK2 = (24, 18, 36, 255); PAPER = (238, 233, 220, 255); PAPER2 = (226, 219, 202, 255)
NAVY = (7, 15, 30, 238); CYAN = (92, 225, 255, 255); LIME = (212, 255, 0, 255); PINK = (255, 62, 160, 255)
SOL = (61, 255, 139, 255); TEAL = (40, 170, 160, 255); AMB = (255, 176, 0, 255); RED = (232, 32, 40, 255)
WHITE = (246, 246, 250, 255); DIM = (150, 160, 182, 255); GREY = (92, 98, 116, 255); CORP_INK = (22, 120, 92, 255)
YEL = (255, 222, 40, 255)

CLASS = {
    'GUNNER': {'col': (255, 128, 40, 255), 'shape': 'octa', 'bust': 'breaker', 'glyph': 'picto_target'},
    'HACKER': {'col': (70, 150, 255, 255), 'shape': 'tile', 'bust': 'ghost', 'glyph': 'placeholder_key'},
    'FIXER': {'col': (80, 220, 110, 255), 'shape': 'hex', 'bust': 'rigger', 'glyph': 'placeholder_vault'},
    'SAPPER': {'col': (170, 100, 255, 255), 'shape': 'shield', 'bust': 'wrecker', 'glyph': 'placeholder_bomb'},
}
CREW = [  # the four operatives of the in-game captures (seed 2): name, class, level, xp, bust variant
    ('MAKO', 'GUNNER', 2, (6, 10), 5), ('URSA', 'SAPPER', 1, (3, 6), 1), ('OZZY', 'HACKER', 1, (0, 6), 9), ('NYX', 'FIXER', 1, (2, 6), 6)]

# weapon -> (glyph, family). Only SMG / RAIL / SHOTGUN / JAMMER / SENTRY have draft glyphs; others reuse a LOCKED glyph (glyph review item 5).
WGLYPH = {'SMG': 'raid_smg', 'Rail Rifle': 'raid_rail', 'Breach Shotgun': 'raid_shotgun', 'Jammer Rig': 'raid_jammer',
          'Grenade Launcher': 'placeholder_bomb', 'Mortar Tube': 'placeholder_bomb', 'Flamer': 'placeholder_burn',
          'Barrier Kit': 'picto_block', 'Bulwark Plate': 'placeholder_shield', 'Marksman Rifle': 'raid_rail', 'Long Rifle': 'raid_rail',
          'Slick Grenade': 'placeholder_bomb', 'Overload Coil': 'raid_jammer', 'Pulse Beam': 'raid_jammer', 'Razor Wire': 'picto_block',
          'Lane Gun': 'raid_smg', 'Suppressed Pistol': 'raid_smg', 'Shaped Charge': 'placeholder_bomb', 'Drone Swarm': 'raid_sentry'}
FAMILY = {'AUTO': (92, 225, 255, 255), 'HEAVY': (255, 128, 40, 255), 'BUILD': (255, 222, 40, 255), 'TECH': (170, 100, 255, 255), 'BLAST': (255, 62, 160, 255)}


def R(seed):
    return random.Random(seed)


# ---------------------------------------------------------------- loading
_gc = {}


def glyph(name, size, col=WHITE):
    k = (name, size, col)
    if k not in _gc:
        g = Image.open(A + 'glyphs_%s.png' % name).convert('RGBA').resize((S(size), S(size)), Image.LANCZOS)
        a = g.split()[3]
        out = Image.new('RGBA', g.size, col[:3] + (0,)); out.putalpha(a.point(lambda v: int(v * col[3] / 255)))
        _gc[k] = out
    return _gc[k]


def put_glyph(img, name, cx, cy, size, col=WHITE, shadow=None):
    g = glyph(name, size, col)
    if shadow:
        s = glyph(name, size, shadow)
        img.alpha_composite(s, (S(cx - size / 2 + 2), S(cy - size / 2 + 3)))
    img.alpha_composite(g, (S(cx - size / 2), S(cy - size / 2)))


def unit_icon(kind, size):
    g = Image.open(A + 'unit_%s.png' % kind).convert('RGBA')
    return g.resize((S(size), S(size)), Image.LANCZOS)


def bust(cls_or_set, idx=0):
    """One 240 x 266 bust (transparent) from an old-pass 4 x 4 bust sheet."""
    s = CLASS[cls_or_set]['bust'] if cls_or_set in CLASS else cls_or_set
    im = Image.open(A + 'portraits_busts_%s.png' % s).convert('RGBA')
    r, c = divmod(idx % 16, 4)
    return im.crop((c * 240, r * 266, c * 240 + 240, r * 266 + 266))


def load_bg(rel, size=None):
    p = rel if ':' in rel else ART + rel
    im = Image.open(p).convert('RGBA')
    return im.resize(size or (W * K, H * K), Image.LANCZOS)


def bg_map(dim=0.42, blur=7, keep_hud=True):
    """hq_idle (r42, Solace) as the context under HQ / map screens: dimmed and softened, the top HUD kept crisp."""
    base = load_bg('cohesion/map_pages_r42/hq_idle.png')
    soft = ImageEnhance.Brightness(base.filter(ImageFilter.GaussianBlur(S(blur)))).enhance(dim)
    soft = ImageEnhance.Color(soft).enhance(0.7)
    if keep_hud:
        hud = base.crop((0, 0, S(1125), S(88)))
        soft.paste(hud, (0, 0))
    return soft


def bg_raid(dim=0.5, blur=0, sat=0.85, src='transitions/v4/plates/raid_city_capture.jpg'):
    base = load_bg(src)
    if blur:
        base = base.filter(ImageFilter.GaussianBlur(S(blur)))
    base = ImageEnhance.Color(base).enhance(sat)
    return ImageEnhance.Brightness(base).enhance(dim)


def shade_rect(img, box, col=(0, 0, 0), a=150, feather=0):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rectangle(S(box), fill=col + (a,))
    if feather:
        lay = lay.filter(ImageFilter.GaussianBlur(S(feather)))
    img.alpha_composite(lay)


def vgrad(w, h, c0, c1):
    t = np.linspace(0, 1, int(h))[:, None, None]
    a = np.array(c0, np.float32)[None, None, :] * (1 - t) + np.array(c1, np.float32)[None, None, :] * t
    a = np.repeat(a, int(w), axis=1)
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'), 'RGBA')


def halftone(w, h, col, step=7, rmax=2.6, fall=(0.0, 1.0), seed=0):
    """Halftone dot field, dot size falling from top (fall[0]) to bottom (fall[1])."""
    L = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    st = step * K
    for y in range(0, int(h), st):
        t = y / max(1, h)
        r = rmax * K * (fall[0] + (fall[1] - fall[0]) * t)
        if r < .4:
            continue
        off = st / 2 if (y // st) % 2 else 0
        for x in range(0, int(w) + st, st):
            d.ellipse((x + off - r, y - r, x + off + r, y + r), fill=col)
    return L


def scanlines(L, a=26, step=3):
    d = ImageDraw.Draw(L)
    for y in range(0, L.height, step * K):
        d.line((0, y, L.width, y), fill=(0, 0, 0, a), width=K)


# ---------------------------------------------------------------- chrome
def glass(img, box, edge=CYAN, title=None, fill=NAVY, ticks=True, tsize=20, rule=PINK):
    """Navy terminal glass: cyan edge, corner ticks, scanlines, mono title, pink rule under the title."""
    x0, y0, x1, y1 = box
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(S([x0 + 6, y0 + 10, x1 + 6, y1 + 12]), radius=S(10), fill=(0, 0, 0, 150))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(S(10))))
    rrect(img, box, 8, fill=fill, outline=edge[:3] + (210,), width=2)
    d = draw(img)
    for y in range(int(y0 + 4), int(y1 - 4), 3):
        d.line(S([x0 + 4, y, x1 - 4, y]), fill=(0, 0, 0, 30), width=1)
    if ticks:
        for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            line(img, [(cx + sx * 2, cy + sy * 18), (cx + sx * 2, cy + sy * 2), (cx + sx * 18, cy + sy * 2)], edge, 4)
    if title:
        text(img, (x0 + 18, y0 + 12), title, font('mono', tsize), edge)
        if rule:
            line(img, [(x0 + 16, y0 + 18 + tsize * 1.25), (x1 - 16, y0 + 18 + tsize * 1.25)], rule[:3] + (190,), 2)


def paper(img, box, rot=0, col=PAPER, edge=True, clip=False, seed=3, tear=False):
    """A sheet of corp paper (soft fibre, darker edge, optional paperclip). Drawn on its own layer and rotated."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    L = layer(w + 40, h + 40)
    base = vgrad(S(w), S(h), col, tuple(max(0, c - 10) for c in col[:3]) + (255,))
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 5, (S(h), S(w)))
    arr = np.asarray(base).astype(np.float32); arr[..., :3] += n[..., None]
    base = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), 'RGBA')
    if tear:
        m = Image.new('L', base.size, 255); md = ImageDraw.Draw(m)
        r = R(seed); pts = [(0, base.height)]
        for x in range(0, base.width + 1, S(9)):
            pts.append((x, base.height - S(4 + r.random() * 7)))
        pts.append((base.width, base.height)); md.polygon(pts, fill=0)
        base.putalpha(m)
    L.alpha_composite(base, (S(20), S(20)))
    if clip:
        cx = w * 0.82 + 20
        d = draw(L)
        d.rounded_rectangle(S([cx - 9, 4, cx + 9, 70]), radius=S(9), outline=(150, 155, 165, 255), width=S(3))
        d.rounded_rectangle(S([cx - 4, 12, cx + 4, 58]), radius=S(4), outline=(190, 195, 205, 255), width=S(2))
    rotate_paste(img, L, (x0 + x1) / 2, (y0 + y1) / 2, rot, sh=(8, 12, 18, 150))


def tape(img, cx, cy, w=110, h=30, rot=-6, col=(250, 240, 200, 150)):
    L = layer(w + 8, h + 8)
    d = draw(L)
    pts = [(4, 4), (w + 4, 6), (w + 2, h + 4), (6, h + 2)]
    d.polygon([tuple(S(list(p))) for p in pts], fill=col)
    for i in range(0, int(w), 6):
        d.line(S([4 + i, 4, 4 + i, 8]), fill=(255, 255, 255, 60), width=1)
    rotate_paste(img, L, cx, cy, rot, shadow=False)


def chip(img, x, y, s, f, fg, bg=INK, edge=None, pad=10, h=None, r=6):
    w = tw(s, f) + pad * 2
    hh = h or f.size / K * 1.35
    rrect(img, [x, y, x + w, y + hh], r, fill=bg, outline=edge, width=2)
    text(img, (x + pad, y + hh / 2 + 1), s, f, fg, 'lm')
    return x + w


def die_sticker(img, label, cx, cy, w, h, fill, rot=-2, size=40, fg=None, sub=None):
    """Pink / lime action stickers (SEND IT, CONTINUE...): ui_lib's vinyl sticker, coloured lettering."""
    sticker(img, label, cx, cy, w, h, fill, fg, rot=rot, size=size)
    if sub:
        text(img, (cx, cy + h / 2 + 22), sub, font('mono', 15), DIM, 'mm')


def shape_pts(shape, cx, cy, r):
    if shape == 'octa':
        return [(cx + r * math.cos(math.radians(22.5 + 45 * i)), cy + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    if shape == 'hex':
        return [(cx + r * math.cos(math.radians(30 + 60 * i)), cy + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    if shape == 'tile':
        k = r * .86
        return [(cx - k, cy - k + 10), (cx - k + 10, cy - k), (cx + k, cy - k), (cx + k, cy + k - 10), (cx + k - 10, cy + k), (cx - k, cy + k)]
    if shape == 'shield':
        return [(cx - r * .9, cy - r * .8), (cx + r * .9, cy - r * .8), (cx + r * .9, cy + r * .1), (cx, cy + r), (cx - r * .9, cy + r * .1)]
    return shape_pts('hex', cx, cy, r)


def class_badge(img, cls, cx, cy, r=34, rot=-6, label=None, glyph_on=True):
    """Class sticker in its raid shape (set 8): white die-cut, ink keyline, class colour, LOCKED glyph in ink."""
    c = CLASS[cls]
    pad = 14
    L = layer(2 * r + pad * 2, 2 * r + pad * 2)
    o = r + pad
    for rr, col in ((r + 9, WHITE), (r + 4, INK), (r + 1, WHITE), (r - 3, c['col'])):
        poly(L, shape_pts(c['shape'], o, o, rr), fill=col)
    poly(L, shape_pts(c['shape'], o, o - r * .25, r * .55), fill=(255, 255, 255, 50))
    if glyph_on:
        g = glyph(c['glyph'], int(r * 1.0), INK)
        L.alpha_composite(g, (S(o - r * .5), S(o - r * .5 - (6 if label else 0))))
    if label:
        text(L, (o, o + r * .55), label, font('anton', max(12, int(r * .42))), INK, 'mm')
    rotate_paste(img, L, cx, cy, rot, sh=(3, 5, 8, 120))


def stars(img, x, y, n, of=3, size=16, col=YEL, off=(176, 176, 190, 120)):
    for i in range(of):
        cx = x + i * size * 1.15 + size / 2; cy = y + size / 2
        pts = []
        for k in range(10):
            rr = size / 2 if k % 2 == 0 else size / 4.6
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        poly(img, pts, fill=col if i < n else off, outline=INK, width=1.5)


def price_tag(img, cx, cy, amount, rot=8, unit='cr', col=PAPER, fg=INK, sale=None, w=92, h=44):
    """Our price tag: a paper swing tag with an eyelet and string (never a coin)."""
    L = layer(w + 60, h + 40)
    d = draw(L)
    x0, y0 = 40, 16
    pts = [(x0, y0 + h / 2), (x0 + 18, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0 + 18, y0 + h)]
    poly(L, pts, fill=col, outline=INK, width=2)
    ellipse(L, [x0 + 12, y0 + h / 2 - 5, x0 + 22, y0 + h / 2 + 5], fill=(40, 34, 30, 255))
    line(L, [(x0 + 17, y0 + h / 2), (x0 - 8, y0 + h / 2 - 12), (2, y0 + h / 2 - 4)], (200, 190, 170, 255), 2)
    text(L, (x0 + 22 + (w - 22) / 2, y0 + h / 2 + 2), '%s %s' % (amount, unit), font('anton', int(h * .58)), fg, 'mm')
    if sale is not None:
        line(L, [(x0 + 30, y0 + h * .7), (x0 + w - 6, y0 + h * .3)], RED, 3)
    rotate_paste(img, L, cx, cy, rot, sh=(3, 5, 6, 110))
    if sale is not None:
        text(img, (cx + 8, cy - h * .95), '%s' % sale, font('marker', 26), RED, 'mm')


def hand(img, xy, s, size=30, col=YEL, anchor='la', rot=0, f='marker'):
    if rot == 0:
        text(img, xy, s, font(f, size), col, anchor)
        return
    fnt = font(f, size)
    w = tw(s, fnt) + 20; h = size * 1.6
    L = layer(w, h)
    text(L, (10, h / 2), s, fnt, col, 'lm')
    rotate_paste(img, L, xy[0] + w / 2 - 10, xy[1], rot, shadow=False)


def pencil_line(img, pts, col=YEL, w=5, seed=1, jitter=1.6):
    r = R(seed)
    for k in range(2):
        q = [(x + r.uniform(-jitter, jitter), y + r.uniform(-jitter, jitter)) for x, y in pts]
        line(img, q, col[:3] + (230 if k == 0 else 120,), w if k == 0 else w * .5)


def pencil_circle(img, cx, cy, rx, ry, col=YEL, w=5, seed=2, turns=1.15):
    r = R(seed)
    pts = []
    n = 60
    for i in range(int(n * turns)):
        a = i / n * math.tau - 1.9
        k = 1 + .05 * math.sin(i * .3 + r.random())
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    pencil_line(img, pts, col, w, seed)


def tick(img, x, y, s=26, col=YEL, w=6):
    pencil_line(img, [(x, y), (x + s * .35, y + s * .45), (x + s, y - s * .55)], col, w, seed=int(x))


def cross(img, x, y, s=24, col=RED, w=6):
    pencil_line(img, [(x - s / 2, y - s / 2), (x + s / 2, y + s / 2)], col, w, seed=int(x))
    pencil_line(img, [(x + s / 2, y - s / 2), (x - s / 2, y + s / 2)], col, w, seed=int(y))


def arrow_hand(img, pts, col=YEL, w=6, head=22, seed=4):
    pencil_line(img, pts, col, w, seed)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    a = math.atan2(y1 - y0, x1 - x0)
    for s in (-.5, .5):
        pencil_line(img, [(x1, y1), (x1 - head * math.cos(a + s), y1 - head * math.sin(a + s))], col, w, seed + 1)


def bar(img, x, y, w, h, frac, col, back=(40, 44, 58, 255), seg=0, edge=INK):
    rect(img, [x, y, x + w, y + h], fill=back, outline=edge, width=1.5)
    if seg:
        sw = w / seg
        for i in range(seg):
            c = col if (i + .5) / seg <= frac else back
            rect(img, [x + i * sw + 2, y + 2, x + (i + 1) * sw - 1, y + h - 2], fill=c)
    else:
        rect(img, [x + 2, y + 2, x + 2 + (w - 4) * frac, y + h - 2], fill=col)


def hud_strip(img, credits=7, heat=36, hq=(20, 20), rnd=None, crumbs=None):
    """Raid / HQ top strip: our heart + HQ, credits, Heat; optional ROUND."""
    glass(img, [18, 14, 600, 86], edge=CYAN, ticks=True)
    put_glyph(img, 'picto_hp', 52, 50, 38, PINK)
    text(img, (80, 50), 'HQ', font('mono', 18), DIM, 'lm')
    bar(img, 112, 38, 190, 24, hq[0] / hq[1], (120, 230, 90, 255), seg=10)
    text(img, (312, 51), '%d/%d' % hq, font('anton', 28), WHITE, 'lm')
    text(img, (392, 51), 'CR', font('mono', 18), DIM, 'lm')
    text(img, (424, 51), str(credits), font('anton', 34), LIME, 'lm')
    put_glyph(img, 'placeholder_burn', 494, 50, 30, (255, 110, 60, 255))
    text(img, (514, 51), str(heat), font('anton', 34), (255, 150, 90, 255), 'lm')


def raid_steps(img, cur, x=640, y=22, labels=('REVIEW', 'SHOP', 'PLACE', 'EXECUTE', 'RESULT'), lost=False):
    """The five raid screens as one strip of numbered stickers on a tape line; the current one is big and lit."""
    xs = []
    cx = x
    for i, lb in enumerate(labels):
        big = i == cur
        f = font('anton', 30 if big else 22)
        w = tw(lb, f) + (74 if big else (78 if i < cur else 54))
        xs.append((cx, w, big))
        cx += w + 16
    line(img, [(x - 6, y + 32), (cx - 10, y + 32)], (255, 255, 255, 60), 3)
    for i, (sx, w, big) in enumerate(xs):
        h = 54 if big else 42
        yy = y + 32 - h / 2
        done = i < cur
        if big:
            fill = (RED if lost and i == 4 else LIME)
            rrect(img, [sx - 4, yy - 4, sx + w + 4, yy + h + 4], 12, fill=WHITE)
            rrect(img, [sx, yy, sx + w, yy + h], 9, fill=INK)
            ellipse(img, [sx + 8, yy + 9, sx + 8 + h - 18, yy + h - 9], fill=fill)
            text(img, (sx + 8 + (h - 18) / 2, yy + h / 2 + 1), str(i + 1), font('anton', 24), INK, 'mm')
            text(img, (sx + h - 2, yy + h / 2 + 1), labels[i], font('anton', 30), fill, 'lm')
        else:
            rrect(img, [sx, yy, sx + w, yy + h], 8, fill=(18, 20, 30, 230), outline=(110, 120, 140, 200) if not done else (212, 255, 0, 160), width=2)
            text(img, (sx + 16, yy + h / 2 + 1), str(i + 1), font('anton', 20), DIM if not done else LIME, 'mm')
            text(img, (sx + 32, yy + h / 2 + 1), labels[i], font('anton', 22), (170, 176, 196, 255) if not done else (220, 240, 160, 255), 'lm')
            if done:
                tick(img, sx + w - 26, yy + h / 2 + 2, 18, LIME, 4)


def title_plate(img, x, y, kicker, title, sub=None, col=LIME):
    text(img, (x, y), kicker, font('mono', 18), col)
    text(img, (x - 2, y + 22), title, font('anton', 60), WHITE)
    if sub:
        text(img, (x, y + 104), sub, font('plex', 22), DIM)


def bits_field(img, box, n=300, cols=(LIME, PINK, CYAN), size=16, seed=5, alpha=230):
    r = R(seed)
    x0, y0, x1, y1 = box
    f = font('mono', size)
    d = draw(img)
    for i in range(n):
        x = r.uniform(x0, x1); y = r.uniform(y0, y1)
        c = r.choice(cols)
        d.text((S(x), S(y)), r.choice('01'), font=f, fill=c[:3] + (alpha,))


def frame_caption(img, s, col=AMB):
    """Small plate id at the bottom-left edge: what this plate is (kept off the play area)."""
    f = font('mono', 13)
    rect(img, [0, 1060, tw(s, f) + 24, 1080], fill=(6, 6, 10, 220))
    text(img, (12, 1075), s, f, col[:3] + (200,), 'ls')


def portrait_art(cls, w, h, idx=0, bset=None, tone=None, dim=False):
    """Portrait window art: class-colour duotone backdrop, halftone, faint class glyph, the bust with a rim light."""
    c = tone or CLASS[cls]['col']
    L = Image.new('RGBA', (S(w), S(h)), (0, 0, 0, 0))
    top = tuple(int(v * .55) for v in c[:3]) + (255,)
    L.alpha_composite(vgrad(S(w), S(h), top, (16, 12, 26, 255)))
    L.alpha_composite(halftone(S(w), S(h), tuple(min(255, int(v * 1.1)) for v in c[:3]) + (90,), step=8, rmax=3.0, fall=(1.0, .1)))
    g = glyph(CLASS[cls]['glyph'], int(w * .9), c[:3] + (40,))
    L.alpha_composite(g, (S(w * .05), S(h * .02)))
    b = bust(bset or cls, idx)
    sc = (h * 1.05) / b.height
    b = b.resize((S(b.width * sc), S(b.height * sc)), Image.LANCZOS)
    b = ImageEnhance.Contrast(b).enhance(1.12)
    a = b.split()[3]
    rim = Image.new('RGBA', b.size, c[:3] + (0,)); rim.putalpha(a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(S(5))))
    bx = (S(w) - b.width) // 2; by = S(h) - b.height + S(h * .06)
    L.alpha_composite(rim, (bx, by)); L.alpha_composite(b, (bx, by))
    scanlines(L, 22)
    if dim:
        L = ImageEnhance.Brightness(L).enhance(.45)
        L = ImageEnhance.Color(L).enhance(.2)
    return L


def op_card(img, x, y, w, h, name, cls, lvl=1, xp=(0, 6), idx=0, bset=None, traits=(), weapons=(), talents=(), cost=None,
            rot=0, state='', hp=None, sel=False, compact=False, tag=None, trait_desc=None):
    """Operative card: portrait window, class badge, name tape, level + XP, traits, weapon slots. Our card craft:
    white die-cut border, ink body, class colour spine."""
    c = CLASS[cls]['col']
    L = layer(w + 30, h + 30)
    o = 15
    if sel:
        gl = layer(w + 30, h + 30)
        rrect(gl, [o - 6, o - 6, o + w + 6, o + h + 6], 18, fill=LIME[:3] + (255,))
        L = glow(L, gl, 9, 1.4)
        rrect(L, [o - 7, o - 7, o + w + 7, o + h + 7], 18, outline=LIME, width=4)
    rrect(L, [o, o, o + w, o + h], 16, fill=WHITE)
    rrect(L, [o + 5, o + 5, o + w - 5, o + h - 5], 12, fill=INK)
    ph = h * (.50 if not compact else .62)
    art = portrait_art(cls, w - 14, ph, idx, bset, dim=state in ('down', 'locked'))
    m = Image.new('L', art.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, art.width, art.height + S(20)), radius=S(10), fill=255)
    L.paste(art, (S(o + 7), S(o + 7)), m)
    rect(L, [o + 7, o + 7 + ph - 4, o + w - 7, o + 7 + ph], fill=c)
    # name tape
    f = font('anton', 30 if not compact else 24)
    nw = tw(name, f) + 26
    tx, ty = o + 14, o + ph - 22
    rect(L, [tx - 2, ty - 2, tx + nw + 2, ty + 40], fill=INK)
    rect(L, [tx, ty, tx + nw, ty + 38], fill=WHITE)
    text(L, (tx + 13, ty + 20), name, f, INK, 'lm')
    text(L, (o + w - 16, o + ph + 30), 'LV %d' % lvl, font('anton', 24), WHITE, 'rm')
    yy = o + ph + 22
    text(L, (o + 16, yy + 8), cls, font('mono', 17), c, 'lm')
    if xp:
        bar(L, o + 16, yy + 24, w - 32, 10, xp[0] / xp[1], c, seg=xp[1])
    yy += 44
    if not compact:
        for t in traits[:3]:
            yy2 = yy
            text(L, (o + 18, yy2 + 10), '+ ' + t, font('plex', 18) if not trait_desc else font('anton', 22), (230, 230, 240, 255), 'lm')
            yy += 26
            if trait_desc and t in trait_desc:
                for ln_ in wrap(trait_desc[t], font('plex', 16), w - 44)[:2]:
                    text(L, (o + 30, yy + 8), ln_, font('plex', 16), (160, 166, 188, 255), 'lm')
                    yy += 20
                yy += 8
        if talents:
            for t in talents[:2]:
                text(L, (o + 18, yy + 10), '* ' + t, font('plex', 18), YEL, 'lm')
                yy += 26
    # weapon slots row
    if weapons is not None:
        ny = o + h - 58
        n = max(2, len(weapons))
        sw = (w - 32 - (n - 1) * 8) / n
        for i in range(n):
            sx = o + 16 + i * (sw + 8)
            if i < len(weapons) and weapons[i]:
                wn, st = weapons[i]
                rrect(L, [sx, ny, sx + sw, ny + 42], 6, fill=WHITE, outline=INK, width=2)
                g = glyph(WGLYPH.get(wn, 'raid_smg'), 30, INK)
                L.alpha_composite(g, (S(sx + 6), S(ny + 6)))
                stars(L, sx + 40, ny + 13, st, 3, 12)
            else:
                rrect(L, [sx, ny, sx + sw, ny + 42], 6, fill=(30, 26, 44, 255), outline=(90, 90, 120, 255), width=2)
                text(L, (sx + sw / 2, ny + 21), 'EMPTY', font('mono', 14), (120, 120, 150, 255), 'mm')
    rotate_paste(img, L, x + w / 2, y + h / 2, rot, sh=(6, 10, 14, 150))
    class_badge(img, cls, x + 4, y + 8, 30 if not compact else 24, rot=-8)
    if cost is not None:
        price_tag(img, x + w - 26, y + 14, cost, rot=10)
    if tag:
        text(img, (x + w / 2, y + h + 26), tag, font('mono', 16), DIM, 'mm')
    if state == 'down':
        stamp(img, 'DOWN', x + w / 2, y + h * .33, RED, rot=-12, size=46)


def weapon_card(img, x, y, w, h, name, fam, cost, star=1, dmg=1, shots=1, reach=1, kw=(), text_=None, rot=0, sold=False,
                partner=None, sel=False, locked=False):
    """Shop weapon card: sticker border, family colour field with the glyph big, name, stars, DMG / SHOTS / REACH pips,
    keyword chips, price tag."""
    fc = FAMILY[fam]
    L = layer(w + 30, h + 30)
    o = 15
    if sel:
        gl = layer(w + 30, h + 30)
        rrect(gl, [o - 6, o - 6, o + w + 6, o + h + 6], 18, fill=LIME)
        L = glow(L, gl, 10, 1.5)
    rrect(L, [o, o, o + w, o + h], 16, fill=WHITE)
    rrect(L, [o + 5, o + 5, o + w - 5, o + h - 5], 12, fill=INK)
    fh = h * .42
    fld = vgrad(S(w - 14), S(fh), tuple(int(v * .75) for v in fc[:3]) + (255,), tuple(int(v * .25) for v in fc[:3]) + (255,))
    fld.alpha_composite(halftone(S(w - 14), S(fh), (255, 255, 255, 40), step=7, rmax=2.2, fall=(.2, 1.0)))
    m = Image.new('L', fld.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fld.width, fld.height + S(20)), radius=S(10), fill=255)
    L.paste(fld, (S(o + 7), S(o + 7)), m)
    gname = WGLYPH.get(name, 'raid_smg')
    gs = min(w * .62, fh * .78)
    gx, gy = o + w / 2 - gs / 2, o + 7 + fh / 2 - gs / 2
    L.alpha_composite(glyph(gname, int(gs), (0, 0, 0, 120)), (S(gx + 4), S(gy + 6)))
    L.alpha_composite(glyph(gname, int(gs), WHITE), (S(gx), S(gy)))
    chip(L, o + 14, o + 14, fam, font('mono', 14), INK, bg=fc, pad=7)
    stars(L, o + w - 14 - 3 * 18.4, o + 16, star, 3, 16)
    yy = o + 7 + fh + 12
    f = font('anton', 30 if len(name) < 14 else 25)
    text(L, (o + 16, yy + 16), name.upper(), f, WHITE, 'lm')
    yy += 42
    for i, (lab, v, gl_) in enumerate((('DMG', dmg, None), ('SHOTS', shots, None), ('REACH', reach, None))):
        text(L, (o + 16, yy + 9), lab, font('mono', 15), DIM, 'lm')
        for k in range(6):
            px = o + 82 + k * 17
            on = v >= 0 and k < v
            rect(L, [px, yy + 2, px + 12, yy + 16], fill=fc if on else (46, 46, 62, 255))
        text(L, (o + w - 16, yy + 9), str(v) if v >= 0 else '-', font('anton', 18), WHITE, 'rm')
        yy += 22
    yy += 6
    if text_:
        for ln in wrap(text_, font('plex', 16), w - 32)[:2]:
            text(L, (o + 16, yy + 8), ln, font('plex', 16), (210, 212, 225, 255), 'lm')
            yy += 21
    kx = o + 16
    for k_ in kw:
        kx = chip(L, kx, o + h - 38, k_, font('mono', 13), WHITE, bg=(40, 36, 60, 255), pad=6) + 6
    if locked:
        shade = layer(w + 30, h + 30)
        rrect(shade, [o, o, o + w, o + h], 16, fill=(6, 6, 12, 160))
        L.alpha_composite(shade)
    rotate_paste(img, L, x + w / 2, y + h / 2, rot, sh=(6, 10, 14, 150))
    if partner:
        class_badge(img, partner, x + w - 8, y + h * .42, 22, rot=8)
    if sold:
        stamp(img, 'BOUGHT', x + w / 2, y + h * .24, LIME, rot=-14, size=40)
    elif cost is not None:
        price_tag(img, x + w / 2 + 6, y + h + 4, cost, rot=-4)


def wrap(s, f, width):
    words = s.split(); out = []; cur = ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if tw(t, f) <= width:
            cur = t
        else:
            out.append(cur); cur = wd
    if cur:
        out.append(cur)
    return out


def rich(img, x, y, s, f, width, col=(220, 222, 232, 255), hi=YEL, lh=None):
    """Wrapped text; words in [brackets] are drawn in the highlight colour (keywords, classes, numbers)."""
    lh = lh or f.size / K * 1.32
    words = s.split()
    cx, cy = x, y
    sp = tw(' ', f)
    for wd in words:
        h = wd.startswith('[')
        clean = wd.replace('[', '').replace(']', '')
        ww = tw(clean, f)
        if cx + ww > x + width and cx > x:
            cx = x; cy += lh
        text(img, (cx, cy), clean, f, hi if (h or ']' in wd) else col)
        cx += ww + sp
    return cy + lh


def finish_save(img, name, g=4, seed=1, vig=.35):
    img = vignette(img, vig)
    out = finish(img, OUT + name, g=g, seed=seed)
    print('wrote', name)
    return out
