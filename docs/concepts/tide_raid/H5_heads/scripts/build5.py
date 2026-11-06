"""H5 beam heads, round 3: board, per-triad detail sheets (with family test row), character sheets.
usage: python build5.py OUTDIR [board|detail|char|all]   (reads metrics.json next to this file)"""
import sys, os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import build as B
from build import (PLATE, F, FONT_T, FONT_M, VIS, PW, CROP_GAME, vis, squint, up, plate, p_game, p_ribbon, p_card, p_motion,
                   construction, label_row, METRICS)
from shapes_h5 import *
from render import paste_head, render_head, mask_at

OUT = sys.argv[1]
TOP2 = ['T1', 'T6']      # set after metrics review (see NOTES.md); override with env H5_TOP2=T1,T2
if os.environ.get('H5_TOP2'):
    TOP2 = os.environ['H5_TOP2'].split(',')
PANEL = {'game': p_game, 'ribbon': p_ribbon, 'card': p_card, 'motion': p_motion}
BG = (10, 6, 20)


def make5(fk):
    fn = FAMILIES[fk]['fn']
    return {k: f(fn) for k, f in PANEL.items()}


# ---------------------------------------------------------------- family test (D N E + mystery 4th unit), 64 px game size at scale S
def p_family(fk, S=2, mode='plate'):
    fam = FAMILIES[fk]
    W, H = 300 * S, 92 * S
    if mode == 'plate':
        base = PLATE.crop((CROP_GAME[0] + 8, CROP_GAME[1] + 4, CROP_GAME[0] + 8 + 300, CROP_GAME[1] + 4 + 92)).resize((W, H), Image.NEAREST).convert('RGBA')
    else:
        base = Image.new('RGBA', (W, H), BONE + (255,))
    d = ImageDraw.Draw(base)
    for i, t in enumerate(TYPES + ('X',)):
        cx = (38 + i * 74) * S
        if t == 'X':
            ops = fam['x']('X')
            d.rounded_rectangle([cx - 34 * S, 8 * S, cx + 34 * S, 84 * S], 6 * S, outline=(230, 230, 250, 230), width=max(1, S))
            if mode == 'plate':
                paste_head(base, ops, cx, 46 * S, 64 * S, 0, 'D', fill=XCOL)
            else:
                paste_head(base, ops, cx, 46 * S, 64 * S, 0, 'D', fill=(40, 34, 60), shade=False, ow=0)
            d.text((cx - 30 * S, 76 * S), '? 4th unit', font=F(FONT_M, 5 * S + 2), fill=(240, 240, 255) if mode == 'plate' else (40, 34, 60))
        else:
            ops = fam['fn'](t)
            if mode == 'plate':
                paste_head(base, ops, cx, 46 * S, 64 * S, 0, t)
            else:
                paste_head(base, ops, cx, 46 * S, 64 * S, 0, t, fill=(40, 34, 60), shade=False, ow=0)
    return base.convert('RGB')


def band_row(rows, W, title, getter, S=2):
    rows.append(label_row(title, W))
    row = Image.new('RGB', (W, getter('normal').height * S), BG)
    for j, v in enumerate(VIS):
        row.paste(up(getter(v), S), (j * (PW * S + 20), 0))
    rows.append(row)


def detail5(fk):
    fam = FAMILIES[fk]
    panels = make5(fk)
    W = PW * 6 + 60
    rows = []
    hd = Image.new('RGB', (W, 150), BG)
    d = ImageDraw.Draw(hd)
    d.text((20, 10), 'H5 HEADS  |  ' + fam['name'], font=F(FONT_T, 44), fill=(120, 230, 255))
    d.text((20, 66), 'THEME: ' + fam['theme'] + '    SHARED MOTIF: ' + fam['motif'], font=F(FONT_M, 18), fill=(235, 235, 250))
    m24, m32 = METRICS[fk + '_24'], METRICS[fk + '_32']
    d.text((20, 94), f"24px worst-case pair overlap (IoU over rotations, lower = more distinct, target <= .55): D/N {m24['iouworst_DN']}  D/E {m24['iouworst_DE']}  N/E {m24['iouworst_NE']}   |   32px: {m32['iouworst_DN']} / {m32['iouworst_DE']} / {m32['iouworst_NE']}", font=F(FONT_M, 15), fill=(170, 180, 210))
    d.text((20, 116), f"pieces at 24px: D{m24['pieces_D']} N{m24['pieces_N']} E{m24['pieces_E']}   |   area at 24px (mass ramp): D{m24['area_D']} N{m24['area_N']} E{m24['area_E']}   |   frame delta at 24px: D{m24['motion_D']} N{m24['motion_N']} E{m24['motion_E']}", font=F(FONT_M, 15), fill=(170, 180, 210))
    rows.append(hd)
    con = construction(fk, W // 3, 440, 330)
    d = ImageDraw.Draw(con)
    for i, t in enumerate(fam['units']):
        d.text((W // 3 * i + 10, 412), t, font=F(FONT_M, 15), fill=(200, 200, 225))
    rows.append(label_row('CONSTRUCTION  (green = silhouette vertices, red = ink detail, ring = unit radius, arrow = travel)', W))
    rows.append(con)
    # family test
    rows.append(label_row('FAMILY TEST  D | N | E | hypothetical 4th unit: 64 px on the city (normal, deutan, tritan) and as flat silhouettes (no colour at all)', W))
    row = Image.new('RGB', (W, 92 * 2), BG)
    row.paste(p_family(fk, 2), (0, 0))
    row.paste(vis(p_family(fk, 2).convert('RGBA'), 'deutan'), (600 + 20, 0))
    row.paste(p_family(fk, 2, 'flat'), (1240, 0))
    rows.append(row)
    rows.append(label_row('mystery 4th unit: ' + fam['mystery'] + '  (drawn in the same grammar: radius, dot, light, class; neutral hue)', W))
    gm, rb, cd, mo = panels['game'], panels['ribbon'], panels['card'], panels['motion']
    band_row(rows, W, 'GAME SIZE on the real city: 24 px top row, 32 px bottom row, two headings. normal | deutan | tritan (2x, nearest)', lambda v: vis(gm, v))
    band_row(rows, W, '4 px BLUR SQUINT of the same crops', lambda v: vis(squint(gm.convert('RGB')), v))
    band_row(rows, W, 'LEADING A RIBBON: head 30 px, ribbon 11 px, type pattern (D chain, N braid, E chevrons)', lambda v: vis(rb, v))
    band_row(rows, W, 'RIBBON at 4 px BLUR', lambda v: vis(squint(rb.convert('RGB')), v))
    band_row(rows, W, 'CARD-TAB GLYPH: ink silhouette on the type tab, detail cut in the tab hue (22 px)', lambda v: vis(cd, v))
    band_row(rows, W, 'MOTION, 2 frames per head: 40 px heading 0 (top) and 24 px iso heading (bottom)', lambda v: vis(mo, v))
    rows.append(label_row('MOTION at 120 px: frame 1 | frame 2 | difference (grey shared, red only frame 1, cyan only frame 2)', W))
    rows.append(B.big_motion(fk, W))
    h = sum(r.height for r in rows)
    out = Image.new('RGB', (W, h), BG)
    y = 0
    for r in rows:
        out.paste(r, (0, y))
        y += r.height
    return out


# ---------------------------------------------------------------- board
def column5(fk, S=2):
    fam = FAMILIES[fk]
    colw = PW * S
    pn = make5(fk)
    c = []
    hd = Image.new('RGB', (colw, 60 * S), BG)
    d = ImageDraw.Draw(hd)
    d.text((6, 2 * S), fam['name'], font=F(FONT_T, 17 * S), fill=(120, 230, 255))
    d.text((6, 26 * S), fam['theme'], font=F(FONT_M, 6 * S + 1), fill=(235, 235, 250))
    d.text((6, 38 * S), 'motif: ' + fam['motif'], font=F(FONT_M, 5 * S + 2), fill=(200, 200, 225))
    m = METRICS[fk + '_24']
    d.text((6, 48 * S), f"IoU D/N {m['iouworst_DN']} D/E {m['iouworst_DE']} N/E {m['iouworst_NE']}  pieces {m['pieces_D']}/{m['pieces_N']}/{m['pieces_E']}", font=F(FONT_M, 5 * S + 2), fill=(255, 220, 120))
    c.append(hd)
    c.append(construction(fk, colw // 3 + 1, 240, 150).resize((colw, 120 * S)))
    c.append(p_family(fk, S))
    rows = [vis(pn['game'], 'normal'), vis(pn['game'], 'deutan'), vis(pn['game'], 'tritan'), vis(squint(pn['game'].convert('RGB')), 'normal'),
            vis(pn['ribbon'], 'normal'), vis(pn['ribbon'], 'deutan'), vis(squint(pn['ribbon'].convert('RGB')), 'normal'),
            vis(pn['card'], 'normal'), vis(pn['card'], 'tritan'), vis(pn['motion'], 'normal')]
    for im in rows:
        c.append(up(im, S))
    return c


def board5():
    G = 24
    S = 2
    cols = [column5(k, S) for k in ORDER]
    tags = ['', 'construction', 'FAMILY TEST 64px + mystery 4th', 'game 24/32 normal', 'game deutan', 'game tritan', 'game 4px blur', 'ribbon normal', 'ribbon deutan', 'ribbon 4px blur', 'card tab normal', 'card tab tritan', 'MOTION 2 frames (40px / 24px)']
    gap = 10
    ys, y = [], 34
    for im in cols[0]:
        ys.append(y)
        y += im.height + gap
    W = len(ORDER) * PW * S + (len(ORDER) + 1) * G
    out = Image.new('RGB', (W, y + 6), BG)
    d = ImageDraw.Draw(out)
    d.text((G, 4), 'H5 BEAM HEADS, ROUND 3: SIX FAMILY SYSTEMS  |  D drone blue  N netrunner magenta  E enforcer yellow  |  D long, N branched, E round-massive; one corner radius, one core dot, one light  |  panels are real game px at 2x nearest', font=F(FONT_M, 18), fill=(150, 220, 255))
    x = G
    for fk, c in zip(ORDER, cols):
        for ri, im in enumerate(c):
            out.paste(im, (x, ys[ri]))
            if ri > 1:
                d.text((x + 4, ys[ri] + im.height - 16), tags[ri], font=F(FONT_M, 11), fill=(255, 255, 255))
        x += PW * S + G
    return out


# ---------------------------------------------------------------- character sheets
def xform(ops, sx=1.0, sy=1.0, deg=0.0):
    a = math.radians(deg)
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for k, p in ops:
        q = [(x * sx, y * sy) for x, y in p]
        out.append((k, [(x * ca - y * sa, x * sa + y * ca) for x, y in q]))
    return out


def explode(ops, k):
    """burst the silhouette parts outward by k (parts are the 'add' polygons); inks drop out once k > .3."""
    out = []
    for i, (kind, p) in enumerate(ops):
        if kind != 'add':
            if kind == 'ink' and k <= .3:
                out.append((kind, p))
            continue
        cx = sum(x for x, y in p) / len(p)
        cy = sum(y for x, y in p) / len(p)
        r = math.hypot(cx, cy)
        if r < .08:
            ang = 2.4 * i
            dx, dy = math.cos(ang), math.sin(ang)
        else:
            dx, dy = cx / r, cy / r
        sh = k * (.5 + 1.0 * r)
        out.append((kind, [(x + dx * sh, y + dy * sh) for x, y in p]))
    return out


def mixw(c, w):
    return tuple(int(v + (255 - v) * w) for v in c)


def dimc(c, w):
    return tuple(int(v * w) for v in c)


def paste_alpha(base, im, cx, cy, a):
    im = im.copy()
    al = im.split()[3].point(lambda v: int(v * a))
    im.putalpha(al)
    base.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))


def sparks(d, cx, cy, r0, r1, n, col, w=4, a0=0.0):
    for i in range(n):
        a = a0 + 2 * math.pi * i / n
        d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a))], fill=col, width=w)


def char_cell(fam, t, row, i, cell, size=128):
    """one 3-frame cell image (RGBA) for a row in {'idle','travel','hit'} and frame i in 0..2."""
    img = Image.new('RGBA', (cell, cell), (20, 14, 36, 255))
    d = ImageDraw.Draw(img)
    c = cell // 2
    fr = (0, 2 / 3, 4 / 3)[i]
    fn = fam['fn']
    hue = HUE[t]
    if row == 'idle':
        ops = fn(t, fr)
        bob = 3 * math.sin(math.pi * fr)
        paste_head(img, ops, c, c + bob, size, 0, t)
    elif row == 'travel':
        ang = -26
        ops = xform(fn(t, fr), 1.12, .92)
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for k in (3, 2, 1):
            g = render_head(xform(fn(t, fr), 1.0, .9), size * .92, ang, hue)
            paste_alpha(img, g, c - ca * k * 30 - 12, c - sa * k * 30 + 6, [0, .16, .26, .42][k])
        paste_head(img, ops, c + 14 + 4 * math.sin(math.pi * fr), c - 2 + 3 * math.cos(math.pi * fr), size, ang, t)
        for j in range(3):
            y0 = c + 38 + j * 9
            d.line([(8 + j * 8, y0), (50 + j * 8, y0)], fill=(120, 110, 170), width=2)
    else:
        if i == 0:   # impact: white flash, squash, jolt
            ops = xform(fn(t, 0), .84, 1.14, -6)
            paste_head(img, ops, c + 5, c, size, 0, t, fill=mixw(hue, .8), ow=None)
            sparks(d, c - 62, c - 20, 12, 30, 7, (255, 255, 255), 4, .3)
        elif i == 1:  # recoil: parts loosen, dim, tilted
            ops = explode(xform(fn(t, 0), .94, .94, 14), .22)
            paste_head(img, ops, c - 6, c + 4, size, 0, t, fill=dimc(hue, .72))
            sparks(d, c, c, 74, 90, 10, dimc(hue, .8), 3, .15)
        else:         # burst: parts scattered, small, hollow dark
            ops = explode(xform(fn(t, 0), .72, .72, 24), .75)
            paste_head(img, ops, c, c + 6, size, 0, t, fill=dimc(hue, .38), ink=(40, 30, 70))
            for j in range(9):
                a = 1.3 * j
                r = 70 + 6 * (j % 3)
                x, y = c + r * math.cos(a), c + r * math.sin(a)
                d.rectangle([x - 3, y - 3, x + 3, y + 3], fill=dimc(hue, .55))
    return img


def char_sheet(fk):
    fam = FAMILIES[fk]
    cell = 210
    W = 3 * 3 * cell + 4 * 30
    rows_name = [('idle', 'IDLE  3 frames (phase 0 / 120 / 240 deg of the 2-frame cycle)'), ('travel', 'TRAVEL  iso heading, stretch + afterimage, 3 frames'), ('hit', 'HIT  >  RECOIL  >  BURST (death)')]
    Hh = 130 + len(rows_name) * (cell + 34) + 34 + 190 + 40
    out = Image.new('RGB', (W, Hh), BG)
    d = ImageDraw.Draw(out)
    d.text((20, 8), 'H5 CHARACTER SHEET  |  ' + fam['name'], font=F(FONT_T, 44), fill=(120, 230, 255))
    d.text((20, 62), 'THEME: ' + fam['theme'] + '    MOTIF: ' + fam['motif'], font=F(FONT_M, 17), fill=(235, 235, 250))
    d.text((20, 88), 'heads at 128 px; every frame is the same shape language: outline, corner radius, core dot, light; hit and death reuse the live polygons (parts burst, no new art)', font=F(FONT_M, 14), fill=(170, 180, 210))
    y = 130
    for rname, rt in rows_name:
        d.text((20, y), rt, font=F(FONT_M, 16), fill=(130, 220, 255))
        y += 26
        for ti, t in enumerate(TYPES):
            for i in range(3):
                x = 30 + ti * (3 * cell + 30) + i * cell
                out.paste(char_cell(fam, t, rname, i, cell).convert('RGB'), (x, y))
            d.text((30 + ti * (3 * cell + 30) + 6, y + 4), {'D': 'D DRONE', 'N': 'N NETRUNNER', 'E': 'E ENFORCER'}[t], font=F(FONT_M, 14), fill=HUE[t])
        y += cell + 8
    # game-size strip: all nine states per head at 32 px on the real city
    d.text((20, y), 'SAME STATES AT GAME SIZE: 32 px on the city (idle x3, travel x3, hit/recoil/burst x3), per head', font=F(FONT_M, 16), fill=(130, 220, 255))
    y += 26
    strip = plate(CROP_GAME[0], CROP_GAME[1] - 20, 3 * 9 * 50 + 60, 190).convert('RGBA')
    sm = Image.new('RGBA', (1, 1))
    for ti, t in enumerate(TYPES):
        for k, rname in enumerate(('idle', 'travel', 'hit')):
            for i in range(3):
                fr = (0, 2 / 3, 4 / 3)[i]
                cx = 30 + (ti * 9 + k * 3 + i) * 50 - (0 if True else 0)
                cx = 22 + (ti * 9 + k * 3 + i) * 48 + ti * 12
                if rname == 'idle':
                    paste_head(strip, fam['fn'](t, fr), cx, 36, 32, 0, t)
                elif rname == 'travel':
                    paste_head(strip, xform(fam['fn'](t, fr), 1.12, .92), cx, 36, 32, -26, t)
                else:
                    if i == 0:
                        paste_head(strip, xform(fam['fn'](t, 0), .84, 1.14, -6), cx, 36, 32, 0, t, fill=mixw(HUE[t], .8))
                    elif i == 1:
                        paste_head(strip, explode(xform(fam['fn'](t, 0), .94, .94, 14), .22), cx, 36, 32, 0, t, fill=dimc(HUE[t], .72))
                    else:
                        paste_head(strip, explode(xform(fam['fn'](t, 0), .72, .72, 24), .75), cx, 36, 32, 0, t, fill=dimc(HUE[t], .38), ink=(40, 30, 70))
    strip = strip.crop((0, 0, strip.width, 72)).convert('RGB')
    out.paste(strip.crop((0, 0, min(strip.width, W - 40), strip.height)), (20, y))
    return out.crop((0, 0, W, y + strip.height + 14))


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if mode in ('all', 'board'):
        board5().save(os.path.join(OUT, 'heads_board.jpg'), quality=88)
    if mode in ('all', 'detail'):
        for fk in ORDER:
            detail5(fk).save(os.path.join(OUT, 'triad_%s_%s.png' % (fk, FAMILIES[fk]['short'])))
    if mode in ('all', 'char'):
        for fk in TOP2:
            char_sheet(fk).save(os.path.join(OUT, 'character_%s_%s.png' % (fk, FAMILIES[fk]['short'])))
