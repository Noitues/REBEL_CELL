"""render options in situ, crop, label, write sheets.  Output: D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/wheel_core/"""
import sys, os, json
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
import wc_base as WB

OUT = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/wheel_core/'
CROPS = OUT + 'crops/'
os.makedirs(CROPS, exist_ok=True)
FONT = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/IBMPlexSansCondensed-Medium.ttf', 20)
FONT_S = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/IBMPlexSansCondensed-Medium.ttf', 17)
FONT_B = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/Anton-Regular.ttf', 26)
_cur = {}


def cur_render(beat, state_key=None, show=None, core='e10'):
    k = (beat, state_key, core)
    if k not in _cur:
        _cur[k] = WB.render(beat, show=show, core=core)
    return _cur[k]


def wrap(txt, font, w, d):
    words, lines, cur = txt.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=font) <= w:
            cur = t
        else:
            lines.append(cur); cur = wd
    lines.append(cur)
    return lines


def make_sheet(eid, title, region, opts, beats=('p1',), k=2, show=None, state_key=None, cur_label='CURRENT E10', note=None):
    """opts: list of (label, idea, render_kwargs).  region: (x0,y0,x1,y1) 1x.  Returns {label: crop_path}"""
    cells = {b: [] for b in beats}
    paths = {}
    for b in beats:
        cur = cur_render(b, state_key, show)
        cells[b].append((cur_label, WB.crop(cur, region, k)))
    for lab, idea, kw in opts:
        for b in beats:
            kw2 = dict(kw)
            if show is not None and 'show' not in kw2:
                kw2['show'] = show
            im = WB.render(b, **kw2)
            c = WB.crop(im, region, k)
            cells[b].append((lab, c))
            if b == beats[0]:
                p = CROPS + '%s_%s.png' % (eid, lab)
                c.save(p); paths[lab] = p
    cw, ch = cells[beats[0]][0][1].size
    n = len(cells[beats[0]])
    gap = 14
    tmp = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    capw = cw
    caps = [cur_label + ' (E10 as approved)'] + ['%s: %s' % (l, i) for l, i, _ in opts]
    caplines = [wrap(c, FONT_S, capw, tmp) for c in caps]
    caph = 22 * max(len(x) for x in caplines) + 8
    head = 44
    Wd = n * cw + (n + 1) * gap
    Wd = min(Wd, 2400)
    rows = len(beats)
    Ht = head + rows * (ch + 28 + gap) + caph + gap
    im = Image.new('RGB', (n * cw + (n + 1) * gap, Ht), (14, 16, 24))
    d = ImageDraw.Draw(im)
    d.text((gap, 8), title, font=FONT_B, fill=(242, 246, 255))
    y = head
    for bi, b in enumerate(beats):
        d.text((gap, y), 'state ' + b, font=FONT_S, fill=(255, 226, 0))
        for i, (lab, c) in enumerate(cells[b]):
            im.paste(c, (gap + i * (cw + gap), y + 22))
        y += ch + 28 + gap
    for i, ls in enumerate(caplines):
        for j, l in enumerate(ls):
            d.text((gap + i * (cw + gap), y + j * 22), l, font=FONT_S, fill=(207, 246, 255) if i else (175, 192, 214))
    if im.width > 2400:
        im = im.resize((2400, int(im.height * 2400 / im.width)), Image.LANCZOS)
    im.save(OUT + 'sheet_%s.jpg' % eid, quality=88)
    meta = [(l, i, paths.get(l)) for l, i, _ in opts]
    return meta
