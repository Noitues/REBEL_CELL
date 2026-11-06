"""H4 heads board + per-family detail sheets (round 2).
usage: python build.py OUTDIR [board|detail]   (reads metrics.json next to this file)"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cb
from shapes import *
from render import *

OUT = sys.argv[1]
PLATE = Image.open('D:/rc_scratch/tide_concepts/plates/clean/default/plan_placed.png').convert('RGBA')
FONT_T = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/scripts/Anton-Regular.ttf'
FONT_M = 'C:/Windows/Fonts/consola.ttf'
METRICS = json.load(open(os.path.join(os.path.dirname(__file__), 'metrics.json')))
VIS = ('normal', 'deutan', 'tritan')
PW = 300  # native panel width
CROP_GAME = (40, 745)      # plate crop origin for game-size panels (dense purple city, no routes)
CROP_RIB = (20, 640)
BONE = (236, 228, 208)


def F(p, s):
    return ImageFont.truetype(p, s)


def vis(im, mode):
    if mode == 'normal':
        return im.convert('RGB')
    return cb.sim(im, cb.DEUT if mode == 'deutan' else cb.TRIT)


def plate(x, y, w, h):
    return PLATE.crop((x, y, x + w, y + h)).copy()


def label(im, scale=1):
    return im


# ---------------------------------------------------------------- panels (native 1:1 resolution)
def p_game(fn):
    """24 px row and 32 px row, two headings, on the real city."""
    im = plate(CROP_GAME[0], CROP_GAME[1], PW, 100)
    for size, y in ((24, 30), (32, 72)):
        for g, (ang, x0) in enumerate(((-26, 30), (154, 172))):
            for i, t in enumerate(TYPES):
                paste_head(im, fn(t), x0 + i * 46, y, size, ang, t)
    return im


def ribbon_path(x0, y0, n):
    """street-like path: iso diagonal, one turn."""
    segs = [(-26, 55), (26, 45), (-26, 80)]
    pts = [(x0, y0)]
    for ang, L in segs:
        a = math.radians(ang)
        x, y = pts[-1]
        pts.append((x + L * math.cos(a), y + L * math.sin(a)))
    return pts


def p_ribbon(fn):
    S = 3
    W, H = PW, 150
    base = plate(CROP_RIB[0], CROP_RIB[1], W, H)
    lay = Image.new('RGBA', (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    heads = []
    for k, t in enumerate(TYPES):
        pts = [(x * S, (y + 8 + k * 46 - 30 * k) * S) for x, y in ribbon_path(8, 62 + 0 * k, k)]
        pts = [(x, y + (k - 1) * 18 * S) for x, y in pts]
        col = HUE[t]
        d.line(pts, fill=INK + (255,), width=17 * S, joint='curve')
        d.line(pts, fill=col + (255,), width=11 * S, joint='curve')
        # type pattern (second channel): D dark cross-cuts, N braid dots, E hazard chevrons
        L = [0]
        for a, b in zip(pts[:-1], pts[1:]):
            L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        step = {'D': 9, 'N': 7, 'E': 12}[t] * S
        s = step
        while s < L[-1] - 14 * S:
            i = max(j for j in range(len(L) - 1) if L[j] <= s)
            a, b = pts[i], pts[i + 1]
            f = (s - L[i]) / (L[i + 1] - L[i])
            x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
            dx, dy = (b[0] - a[0]) / (L[i + 1] - L[i]), (b[1] - a[1]) / (L[i + 1] - L[i])
            nx, ny = -dy, dx
            if t == 'D':
                d.line([(x - nx * 5 * S, y - ny * 5 * S), (x + nx * 5 * S, y + ny * 5 * S)], fill=INK + (200,), width=int(1.6 * S))
            elif t == 'N':
                sg = 1 if int(s / step) % 2 else -1
                d.ellipse([x + nx * 2.4 * S * sg - 1.7 * S, y + ny * 2.4 * S * sg - 1.7 * S, x + nx * 2.4 * S * sg + 1.7 * S, y + ny * 2.4 * S * sg + 1.7 * S], fill=(255, 190, 245, 255))
            else:
                p = [(x - nx * 4.5 * S - dx * 3 * S, y - ny * 4.5 * S - dy * 3 * S), (x + dx * 3 * S, y + dy * 3 * S), (x + nx * 4.5 * S - dx * 3 * S, y + ny * 4.5 * S - dy * 3 * S)]
                d.line(p, fill=INK + (230,), width=int(1.8 * S))
            s += step
        ang = math.degrees(math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]))
        heads.append((t, pts[-1][0] / S, pts[-1][1] / S, ang))
    glow = lay.filter(ImageFilter.GaussianBlur(5 * S))
    lay = lay.resize((W, H), Image.LANCZOS)
    glow = glow.resize((W, H), Image.LANCZOS)
    base.alpha_composite(glow)
    base.alpha_composite(lay)
    for t, x, y, ang in heads:
        paste_head(base, fn(t), x, y, 30, ang, t)
    return base


def p_card(fn):
    im = plate(CROP_GAME[0] + 20, CROP_GAME[1] + 10, PW, 128)
    im = Image.alpha_composite(im, Image.new('RGBA', im.size, (10, 6, 20, 150)))
    d = ImageDraw.Draw(im)
    for i, t in enumerate(TYPES):
        cx = 52 + i * 98
        x0, y0, x1, y1 = cx - 35, 8, cx + 35, 118
        d.rounded_rectangle([x0 - 1.5, y0 - 1.5, x1 + 1.5, y1 + 1.5], 6, fill=INK + (255,))
        d.rounded_rectangle([x0, y0, x1, y1], 5, fill=BONE + (255,))
        d.rounded_rectangle([x0, y0, x1, y0 + 28], 5, fill=HUE[t] + (255,))
        d.rectangle([x0, y0 + 20, x1, y0 + 28], fill=HUE[t] + (255,))
        # card body hint: a guard brick glyph
        for r in range(3):
            d.rectangle([cx - 19 + (r % 2) * 5, y0 + 44 + r * 14, cx + 13 + (r % 2) * 5, y0 + 53 + r * 14], outline=INK + (255,), width=2)
        paste_head(im, fn(t), cx, y0 + 14, 22, 0, t, fill=INK, ow=0, detail=HUE[t])
    return im


def p_motion(fn):
    """two frames per head: 40 px heading 0 (mot details on) and 24 px at an iso heading, on the real city."""
    im = plate(CROP_GAME[0], CROP_GAME[1], PW, 112)
    for i, t in enumerate(TYPES):
        cx = 50 + i * 100
        for f in (0, 1):
            paste_head(im, fn(t, f), cx + (f * 2 - 1) * 24, 32, 40, 0, t)
            paste_head(im, fn(t, f), cx + (f * 2 - 1) * 24, 84, 24, -26, t)
    return im


def squint(im, r=4):
    return im.filter(ImageFilter.GaussianBlur(r))


PANEL = {'game': p_game, 'ribbon': p_ribbon, 'card': p_card, 'motion': p_motion}


def make(fk):
    fn = FAMILIES[fk]['fn']
    return {k: f(fn) for k, f in PANEL.items()}


def up(im, s):
    return im.resize((im.width * s, im.height * s), Image.NEAREST)


# ---------------------------------------------------------------- construction view
def construction(fk, cell_w, cell_h, hsize):
    fam = FAMILIES[fk]
    im = Image.new('RGB', (cell_w * 3, cell_h), (20, 14, 36))
    d = ImageDraw.Draw(im)
    f = F(FONT_M, 14)
    for i, t in enumerate(TYPES):
        cx, cy = cell_w * i + cell_w // 2, cell_h // 2 + 8
        ops = fam['fn'](t)
        u = (hsize - 2 * hsize * .075) / FOOT
        for gx in range(-int(cell_w / 2 / 40), int(cell_w / 2 / 40) + 1):
            d.line([(cx + gx * 40, 0), (cx + gx * 40, cell_h)], fill=(30, 24, 52))
        d.line([(cx - cell_w / 2 + 10, cy), (cx + cell_w / 2 - 10, cy)], fill=(60, 50, 96))
        d.ellipse([cx - u * 1.05, cy - u * 1.05, cx + u * 1.05, cy + u * 1.05], outline=(60, 50, 96))
        big = Image.new('RGBA', (cell_w, cell_h), (0, 0, 0, 0))
        paste_head(big, ops, cell_w // 2, cell_h // 2 + 8, hsize, 0, t)
        tmp = im.convert('RGBA')
        tmp.alpha_composite(big, (cell_w * i, 0))
        im = tmp.convert('RGB')
        d = ImageDraw.Draw(im)
        for k, p in ops:
            for x, y in p:
                if k == 'mot':
                    continue
                px, py = cx + x * u, cy + y * u
                d.rectangle([px - 2, py - 2, px + 2, py + 2], outline=(120, 255, 200) if k == 'add' else (255, 120, 120))
        d.line([(cx - 20, cy + u * 1.12), (cx + 40, cy + u * 1.12)], fill=(150, 150, 190), width=2)
        d.polygon([(cx + 40, cy + u * 1.12), (cx + 32, cy + u * 1.12 - 5), (cx + 32, cy + u * 1.12 + 5)], fill=(150, 150, 190))
        d.text((cx - cell_w / 2 + 10, 8), {'D': 'D  DRONE', 'N': 'N  NETRUNNER', 'E': 'E  ENFORCER'}[t], font=f, fill=HUE[t])
    return im




def label_row(txt, W):
    im = Image.new('RGB', (W, 28), (22, 16, 40))
    ImageDraw.Draw(im).text((14, 6), txt, font=F(FONT_M, 15), fill=(130, 220, 255))
    return im


def big_motion(fk, W):
    """both frames of every head at 120 px, plus the frame difference (red = only frame 1, cyan = only frame 2)."""
    fam = FAMILIES[fk]
    cw = W // 3
    im = Image.new('RGB', (W, 170), (20, 14, 36))
    for i, t in enumerate(TYPES):
        for f in (0, 1):
            tmp = Image.new('RGBA', (140, 170), (20, 14, 36, 255))
            paste_head(tmp, fam['fn'](t, f), 70, 85, 120, 0, t)
            im.paste(tmp.convert('RGB'), (i * cw + f * 140, 0))
        a = mask_at(fam['fn'](t, 0), 96, 0)
        b = mask_at(fam['fn'](t, 1), 96, 0)
        h, w = a.shape
        diff = np.zeros((h, w, 3), np.uint8) + np.array((20, 14, 36), np.uint8)
        diff[(a > .5) & (b > .5)] = (150, 150, 170)
        diff[(a > .5) & (b <= .5)] = (255, 90, 90)
        diff[(a <= .5) & (b > .5)] = (90, 230, 255)
        im.paste(Image.fromarray(diff).resize((110, 110)), (i * cw + 285, 30))
    return im


def detail(fk):
    fam = FAMILIES[fk]
    panels = make(fk)
    W = PW * 6 + 60
    rows = []
    hd = Image.new('RGB', (W, 120), (10, 6, 20))
    d = ImageDraw.Draw(hd)
    d.text((20, 10), 'H4 HEADS  |  ' + fam['name'], font=F(FONT_T, 44), fill=(120, 230, 255))
    d.text((20, 66), fam['concept'], font=F(FONT_M, 20), fill=(220, 220, 240))
    m24, m32 = METRICS[fk + '_24'], METRICS[fk + '_32']
    d.text((20, 94), f"24px worst-case pair overlap (IoU over rotations, lower = more distinct): D/N {m24['iouworst_DN']}  D/E {m24['iouworst_DE']}  N/E {m24['iouworst_NE']}   |   32px: {m32['iouworst_DN']} / {m32['iouworst_DE']} / {m32['iouworst_NE']}   |   pieces at 24px: D{m24['pieces_D']} N{m24['pieces_N']} E{m24['pieces_E']}   |   frame delta at 24px: D{m24['motion_D']} N{m24['motion_N']} E{m24['motion_E']}", font=F(FONT_M, 15), fill=(170, 180, 210))
    rows.append(hd)
    con = construction(fk, W // 3, 440, 330)
    d = ImageDraw.Draw(con)
    for i, t in enumerate(UNITS[fk]):
        d.text((W // 3 * i + 10, 412), t, font=F(FONT_M, 15), fill=(200, 200, 225))
    rows.append(label_row('CONSTRUCTION  (green = silhouette vertices, red = ink detail, ring = unit radius, arrow = travel)', W))
    rows.append(con)
    S = 2

    def band(title, getter):
        rows.append(label_row(title, W))
        row = Image.new('RGB', (W, getter('normal').height * S), (10, 6, 20))
        for j, v in enumerate(VIS):
            row.paste(up(getter(v), S), (j * (PW * S + 20), 0))
        rows.append(row)
    gm, rb, cd, mo = panels['game'], panels['ribbon'], panels['card'], panels['motion']
    band('GAME SIZE on the real city: 24 px top row, 32 px bottom row, two headings. normal | deutan | tritan (shown 2x, nearest)', lambda v: vis(gm, v))
    band('4 px BLUR SQUINT of the same crops', lambda v: vis(squint(gm.convert('RGB')), v))
    band('LEADING A RIBBON: head 30 px, ribbon 11 px, type pattern as in H2 (D chain, N braid, E chevrons)', lambda v: vis(rb, v))
    band('RIBBON at 4 px BLUR', lambda v: vis(squint(rb.convert('RGB')), v))
    band('CARD-TAB GLYPH: ink silhouette on the type tab, detail cut in the tab hue (22 px)', lambda v: vis(cd, v))
    band('MOTION, 2 frames per head: 40 px heading 0 (top) and 24 px iso heading (bottom). normal | deutan | tritan', lambda v: vis(mo, v))
    rows.append(label_row('MOTION at 120 px: frame 1 | frame 2 | difference (grey shared, red only frame 1, cyan only frame 2)', W))
    rows.append(big_motion(fk, W))
    h = sum(r.height for r in rows)
    out = Image.new('RGB', (W, h), (10, 6, 20))
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height
    return out


# ---------------------------------------------------------------- the board: 2 reference columns (1x) + 6 new families (2x)
def column(fk, S):
    fam = FAMILIES[fk]
    colw = PW * S
    pn = make(fk)
    c = []
    hd = Image.new('RGB', (colw, 48 * S), (10, 6, 20))
    d = ImageDraw.Draw(hd)
    d.text((6, 2 * S), fam['name'], font=F(FONT_T, 17 * S), fill=(200, 200, 210) if fam.get('ref') else (120, 230, 255))
    d.text((6, 28 * S), fam['concept'][:60], font=F(FONT_M, 6 * S + 1), fill=(220, 220, 240))
    c.append(hd)
    c.append(construction(fk, colw // 3 + 1, 240, 150).resize((colw, 120 * S)))
    rows = [vis(pn['game'], 'normal'), vis(pn['game'], 'deutan'), vis(pn['game'], 'tritan'), vis(squint(pn['game'].convert('RGB')), 'normal'),
            vis(pn['ribbon'], 'normal'), vis(pn['ribbon'], 'deutan'), vis(squint(pn['ribbon'].convert('RGB')), 'normal'),
            vis(pn['card'], 'normal'), vis(pn['card'], 'tritan')]
    for im in rows:
        c.append(up(im, S))
    if fam.get('ref'):
        c.append(Image.new('RGB', (colw, 112 * S), (14, 10, 26)))
    else:
        c.append(up(vis(pn['motion'], 'normal'), S))
    return c


def board():
    keys = list(FAMILIES)
    G = 24
    scales = {k: (1 if FAMILIES[k].get('ref') else 2) for k in keys}
    W = sum(PW * scales[k] for k in keys) + (len(keys) + 1) * G
    cols = [column(k, scales[k]) for k in keys]
    tags = ['', 'construction', 'game 24/32 normal', 'game deutan', 'game tritan', 'game 4px blur', 'ribbon normal', 'ribbon deutan', 'ribbon 4px blur', 'card tab normal', 'card tab tritan', 'MOTION 2 frames (40px / 24px)']
    gap = 10
    ys = []
    y = 34
    for im in cols[keys.index('H1')]:
        ys.append(y)
        y += im.height + gap
    out = Image.new('RGB', (W, y + 6), (10, 6, 20))
    d = ImageDraw.Draw(out)
    d.text((G, 4), 'H4 BEAM HEADS, ROUND 2  |  D drone blue  N netrunner magenta  E enforcer yellow  |  grey = round 1 reference (1x); new families 2x; panels are real game px, nearest', font=F(FONT_M, 18), fill=(150, 220, 255))
    x = G
    for fk, c in zip(keys, cols):
        for ri, im in enumerate(c):
            out.paste(im, (x, ys[ri]))
            if ri > 1 and not FAMILIES[fk].get('ref'):
                d.text((x + 4, ys[ri] + im.height - 16), tags[ri], font=F(FONT_M, 11), fill=(255, 255, 255))
        x += PW * scales[fk] + G
    return out


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if mode in ('all', 'board'):
        board().save(os.path.join(OUT, 'heads_board.jpg'), quality=88)
    if mode in ('all', 'detail'):
        for fk in NEW:
            detail(fk).save(os.path.join(OUT, FILES[fk] + '.png'))
