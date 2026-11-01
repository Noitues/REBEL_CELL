"""Option sheets: per element a labelled sheet (current E10 crop, then options A/B/C with a one-line idea), 2x crops, under 2400 px wide."""
import sys, os, math, textwrap
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
from PIL import Image, ImageDraw, ImageFont
import wr_config as CFG
import wr_crops as CR

ROOT = 'D:/rc_scratch/e10_design/wave_rings/'
OUT = ROOT + 'out/'
DEST = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/wave_rings/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
F_T = ImageFont.truetype(FD + 'Anton-Regular.ttf', 30)
F_L = ImageFont.truetype(FD + 'Anton-Regular.ttf', 22)
F_C = ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', 19)
F_S = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 17)
BG = (22, 24, 32)
COLW = 570
COLH = 330


def load(name):
    return Image.open(OUT + name).convert('RGB')


def crop_specs(img, specs, scale, o='E'):
    parts = []
    for sp in specs:
        if sp[0] == 'gproof':
            parts.append(gproof(sp[1], o))
            continue
        box = CR.box_of(sp)
        c = img.crop(box)
        parts.append(c.resize((int(c.width * scale), int(c.height * scale)), Image.LANCZOS))
    w = sum(p.width for p in parts) + 6 * (len(parts) - 1)
    h = max(p.height for p in parts)
    out = Image.new('RGB', (w, h), (10, 10, 14))
    x = 0
    for p in parts:
        out.paste(p, (x, 0))
        x += p.width + 6
    return out


def fit_scale(specs, maxw=COLW, maxh=COLH, top=3.0):
    specs = [s for s in specs if s[0] != 'gproof'] or specs
    ws = [CR.box_of(s) for s in specs]
    w = sum(b[2] - b[0] for b in ws) + 3 * (len(ws) - 1)
    h = max(b[3] - b[1] for b in ws)
    return min(top, maxw / w, maxh / h)


def gproof(kind, o):
    import wr_glyphs as G
    from slicelib import glyph_rgba
    nm = G.glyph_name('', kind, o)
    out = Image.new('RGB', (COLW, 150), (60, 36, 56))
    d = ImageDraw.Draw(out)
    g = glyph_rgba(nm, 130, 10)
    out.paste(g, (14, 6), g)
    for i, (r, px) in enumerate(((27, 38), (24, 37))):
        cx, cy = 230 + i * 130, 75
        d.ellipse([cx - r * 2, cy - r * 2, cx + r * 2, cy + r * 2], fill=(34, 18, 30), outline=(255, 68, 51), width=6)
        g2 = glyph_rgba(nm, int(px * 2), 4)
        out.paste(g2, (int(cx - g2.width / 2), int(cy - g2.height / 2)), g2)
    d.text((395, 6), 'actual', font=F_S, fill=(200, 200, 210))
    sm = glyph_rgba(nm, 38, 3)
    out.paste(sm, (400, 40), sm)
    d.text((395, 100), '2x: 54 / 48 disc', font=F_S, fill=(200, 200, 210))
    return out


def sheet_for(idx, eid):
    row = [e for e in CFG.EL if e[0] == eid][0]
    _, title, beat, lab, caps, base = row
    states = CR.STATES[eid]
    scale = {}
    for lab_, st, specs in states:
        scale[lab_] = fit_scale(specs)
    pad = 10
    W = 4 * COLW + 5 * pad
    rows = []
    heads = ['CURRENT E10', 'A', 'B', 'C']
    capt = ['the approved plate, as drawn today'] + caps
    y = 84
    tiles = []
    for lab_, st, specs in states:
        sc = scale[lab_]
        imgs = []
        for o in ('E', 'A', 'B', 'C'):
            fn = 'pl_%s_%s%s.png' % (eid, o, '' if st == ('lab' if lab else beat) or st == 'p1' and lab else '_' + st)
            if specs[0][0] == 'gproof':
                imgs.append(crop_specs(None, specs, sc, o))
                continue
            if not os.path.exists(OUT + fn):
                imgs.append(None)
                continue
            imgs.append(crop_specs(load(fn), specs, sc, o))
        hh = max(i.height for i in imgs if i is not None)
        tiles.append((lab_, imgs, hh))
    Ht = 84 + sum(hh + 72 for _, _, hh in tiles) + 170
    sheet = Image.new('RGB', (W, Ht), BG)
    d = ImageDraw.Draw(sheet)
    d.text((pad, 14), '%s  |  %s' % (eid, title), font=F_T, fill=(242, 246, 255))
    sub = 'wave_rings R1 | judged on room_bio_bare at 1920x1080 | crops at %s | every number, count and word fixed' % ('x%.1f' % max(scale.values()))
    d.text((pad, 52), sub, font=F_S, fill=(150, 165, 190))
    y = 84
    for st, imgs, hh in tiles:
        d.text((pad, y + 4), st, font=F_S, fill=(255, 226, 0))
        y += 30
        for i, im in enumerate(imgs):
            x = pad + i * (COLW + pad)
            d.text((x, y - 2), heads[i], font=F_L, fill=(255, 140, 26) if i else (170, 190, 215))
            if im is not None:
                sheet.paste(im, (x, y + 24))
        y += 26 + hh + 12
    # captions
    y += 4
    for i in range(4):
        x = pad + i * (COLW + pad)
        d.text((x, y), heads[i], font=F_L, fill=(255, 140, 26) if i else (170, 190, 215))
        lines = textwrap.wrap(capt[i], 44)
        for j, ln in enumerate(lines[:4]):
            d.text((x, y + 26 + j * 23), ln, font=F_C, fill=(220, 228, 240))
    sheet = sheet.crop((0, 0, W, y + 26 + 4 * 23 + 12))
    fn = DEST + 'sheet_%02d_%s.jpg' % (idx, eid)
    sheet.save(fn, quality=90)
    return fn, sheet.size


if __name__ == '__main__':
    os.makedirs(DEST, exist_ok=True)
    els = sys.argv[1:] or CFG.ORDER
    for i, e in enumerate(CFG.ORDER, 1):
        if e in els:
            print(sheet_for(i, e))
