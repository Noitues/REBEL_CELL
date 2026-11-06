"""R2 sheets: per element, R1 pick | R2 pick | R2 variant, in situ at up to 2.5x (plates from wr2_run), plus glyph size strips for the five unit glyphs.
usage: wr2_sheets.py [element ...]"""
import sys, os, textwrap, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import e8lib as E8
ORIG_TP = E8.token_pos                     # the E10 token rule, captured before any render patches it
from PIL import Image, ImageDraw, ImageFont
import wr_config as CFG
import wr_crops as CR
import wr2_config as C2
import wr2_lib as W2
from wr2_run import states_of, LABOF
from wr2_picks import R1, R2

OUT2 = 'D:/rc_scratch/e10_design/wave_rings/out2/'
DEST = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r2/wave_rings/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
F_T = ImageFont.truetype(FD + 'Anton-Regular.ttf', 30)
F_L = ImageFont.truetype(FD + 'Anton-Regular.ttf', 21)
F_C = ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', 18)
F_S = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 16)
BG = (22, 24, 32)
COLW = 790
COLH = 420
EXT = {'R1': ORIG_TP, 'R2': lambda u: W2.token_pos_r2(u, 'R')}


def unit_of(uid, lab):
    return CR._unit(uid, lab)


def box_for(spec, ver):
    if spec[0] == 'box':
        return tuple(spec[1:5])
    if spec[0] == 'tok':
        lab = spec[3] if len(spec) > 3 else None
        fn = ORIG_TP if ver == 'R1' else (lambda u: W2.token_pos_r2(u, 'R'))
        x, y = fn(unit_of(spec[1], lab))
        h = spec[2]
        return (int(x - h), int(y - h), int(x + h), int(y + h))
    raise ValueError(spec)


def load(ver, state):
    return Image.open(OUT2 + 'pl_%s_%s.png' % (ver, state)).convert('RGB')


def crops(ver, state, specs, sc):
    im = load(ver, state)
    parts = []
    for sp in specs:
        if sp[0] == 'gproof':
            continue
        c = im.crop(box_for(sp, 'R1' if ver == 'R1' else 'R2'))
        parts.append(c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS))
    if not parts:
        return None
    w = sum(p.width for p in parts) + 6 * (len(parts) - 1)
    h = max(p.height for p in parts)
    out = Image.new('RGB', (w, h), (10, 10, 14))
    x = 0
    for p in parts:
        out.paste(p, (x, 0))
        x += p.width + 6
    return out


def fit(specs, ncol, maxh=COLH):
    bs = [box_for(s, 'R2') for s in specs if s[0] != 'gproof']
    if not bs:
        return 1.0
    colw = (COLW * 3 - 0) / 3 if ncol == 3 else COLW * 1.5
    w = sum(b[2] - b[0] for b in bs) + 3 * (len(bs) - 1)
    h = max(b[3] - b[1] for b in bs)
    return min(2.5, colw / w, maxh / h)


def wrap(d, text, font, width, xy, fill=(200, 208, 222), gap=3):
    x, y = xy
    for ln in textwrap.wrap(text, int(width / (font.size * 0.52))):
        d.text((x, y), ln, font=font, fill=fill)
        y += font.size + gap
    return y


def glyph_strip(names, sizes=(16, 20, 28, 37, 44, 70)):
    from slicelib import glyph_rgba
    w = sum(s for s in sizes) + 16 * (len(sizes) + 1)
    out = Image.new('RGB', (w, 96), (92, 50, 78))
    x = 16
    for s in sizes:
        g = glyph_rgba(names, s, max(2, int(s * 0.075)))
        out.paste(g, (x, 8 + (80 - s) // 2 if s < 80 else 8), g)
        x += s + 16
    return out


GL_KIND = {'glyph_packet': 'PACKET', 'glyph_worm': 'WORM', 'glyph_payload': 'PAYLOAD', 'glyph_jammer': 'JAMMER', 'glyph_ring': 'RING'}


def sheet(eid):
    title = [e for e in CFG.EL if e[0] == eid][0][1]
    ad, r_txt, v_txt, fn = C2.EL2[eid]
    has_v = v_txt != '-'
    ncol = 3 if has_v else 2
    colw = COLW if ncol == 3 else int(COLW * 1.5)
    rows = []
    r1k = R1[eid]
    for (label, st, specs) in CR.STATES[eid]:
        state = LABOF[eid] if st == 'lab' else st
        specs_ = [s for s in specs if s[0] != 'gproof']
        if not specs_:
            continue
        sc = fit(specs_, ncol)
        ims = [crops('R1', state, specs_, sc), crops('R2', state, specs_, sc)]
        if has_v:
            ims.append(crops('V_' + eid, state, specs_, sc))
        rows.append((label, ims))
    if eid in GL_KIND:
        k = GL_KIND[eid]
        strips = [glyph_strip('WR_%s_%s' % (k, R1[eid]) if False else _r1name(eid)), glyph_strip('WR_%s_R' % k)]
        if has_v:
            strips.append(glyph_strip('WR_%s_V' % k))
        rows.append(('glyph at 16 / 20 / 28 / 37 / 44 / 70 px on the unit mauve (R1 pick | R2 pick | variant)', strips))
    W = ncol * colw + (ncol + 1) * 10
    hdr = 170
    H = hdr + 12
    for (label, ims) in rows:
        H += 30 + max(i.height for i in ims) + 8
    H += 14
    sh = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(sh)
    d.text((12, 8), title.upper(), font=F_T, fill=(255, 255, 255))
    d.text((12 + d.textlength(title.upper(), font=F_T) + 16, 18), eid, font=F_S, fill=(140, 150, 170))
    y = 46
    d.text((12, y), 'AD direction', font=F_S, fill=(255, 200, 80)); y = wrap(d, ad, F_C, W - 160, (150, y - 2))
    d.text((12, y + 2), 'R2 pick (R)', font=F_S, fill=(120, 230, 150)); y = wrap(d, r_txt, F_C, W - 160, (150, y))
    if has_v:
        d.text((12, y + 2), 'variant (V)', font=F_S, fill=(120, 190, 255)); y = wrap(d, v_txt, F_C, W - 160, (150, y))
    d.text((12, y + 4), 'code: ' + fn, font=F_S, fill=(140, 150, 170))
    y = hdr + 12
    heads = ['R1 pick (%s)' % r1k, 'R2 pick (R)', 'R2 variant (V)'] if has_v else ['R1 pick (%s)' % r1k, 'R2 pick (R)']
    for (label, ims) in rows:
        d.text((12, y), label, font=F_L, fill=(230, 235, 245))
        y += 30
        hh = max(i.height for i in ims)
        for ci, im in enumerate(ims):
            x = 10 + ci * (colw + 10)
            sh.paste(im, (x, y))
            d.text((x + 4, y + 2), heads[ci], font=F_S, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        y += hh + 8
    sh = sh.crop((0, 0, W, y + 6))
    return sh


def _r1name(eid):
    import wr_glyphs as G
    k = GL_KIND[eid]
    o = R1[eid]
    return G.glyph_name(eid, k.capitalize() if k != 'PAYLOAD' else 'Payload', o) if False else 'WR_%s_%s' % (k, o)


if __name__ == '__main__':
    import wr2_glyphs  # registers WR_*_R / V
    import wr_glyphs
    els = sys.argv[1:] or CFG.ORDER
    for i, eid in enumerate(CFG.ORDER):
        if eid not in els:
            continue
        if eid in ('unit_screen_bezel', 'unit_screen_code_text', 'screen_motif_skull'):
            continue
        try:
            sh = sheet(eid)
            n = CFG.ORDER.index(eid) + 1
            fnm = DEST + 'sheet_%02d_%s.jpg' % (n, eid)
            sh.save(fnm, quality=88)
            print(fnm, sh.size, flush=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
