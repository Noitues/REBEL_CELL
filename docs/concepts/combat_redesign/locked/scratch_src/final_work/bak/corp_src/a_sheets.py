import sys, os
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
from e10lib import ROOT
from a_opts import ELEMS
from a_caps import CAP
FD = 'D:/rc_art/art-pass/assets/fonts/'
OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/actions/'
os.makedirs(OUTD, exist_ok=True)
F1 = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 22)
F2 = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 17)
F3 = ImageFont.truetype(FD + 'Anton-Regular.ttf', 28)
BGC = (20, 22, 30)
def wrap(d, s, f, w):
    out, cur = [], ''
    for wd in s.split():
        t = (cur + ' ' + wd).strip()
        if d.textlength(t, font=f) > w and cur:
            out.append(cur); cur = wd
        else:
            cur = t
    out.append(cur)
    return out
def build(el):
    cw = 0; ch = 0; chs = []
    for vi in range(len(el['views'])):
        im = Image.open(OUTD + 'crops/%s__cur__v%d.png' % (el['id'], vi))
        cw = max(cw, im.width); ch = max(ch, im.height); chs.append(min(im.height, int(im.height * min(1, 580 / im.width))))
    pad = 12
    cols = 4
    cw = min(cw, (2380 - pad * 5) // cols)
    scale = 1.0
    W_ = cols * cw + (cols + 1) * pad
    caps = CAP.get(el['id'], {})
    d0 = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    capl = {o: wrap(d0, caps.get(o, ''), F2, cw - 4) for o in ['cur', 'A', 'B', 'C']}
    caph = 26 + 21 * max(len(v) for v in capl.values())
    head = 60
    H_ = head + sum(h + caph + pad for h in chs) + pad
    sh = Image.new('RGB', (W_, H_), BGC)
    d = ImageDraw.Draw(sh)
    d.text((pad, 14), el['title'], font=F1, fill=(240, 244, 255))
    state = ''
    y = head
    for vi, v in enumerate(el['views']):
        for ci, o in enumerate(['cur', 'A', 'B', 'C']):
            im = Image.open(OUTD + 'crops/%s__%s__v%d.png' % (el['id'], o, vi))
            if im.width > cw:
                im = im.resize((cw, int(im.height * cw / im.width)), Image.LANCZOS)
            x = pad + ci * (cw + pad)
            sh.paste(im, (x, y))
            d.rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=(70, 76, 96))
            lab = 'CURRENT E10' if o == 'cur' else 'OPTION ' + o
            beat = v[0] + ((' - ' + v[6]['label']) if v[6].get('label') else '')
            d.text((x, y + chs[vi] + 2), lab + ('   [%s]' % beat if ci == 0 else ''), font=F2, fill=(255, 200, 90) if o == 'cur' else (120, 230, 255))
            for li, ln in enumerate(capl[o]):
                d.text((x, y + chs[vi] + 24 + li * 21), ln, font=F2, fill=(200, 210, 226))
        y += chs[vi] + caph + pad
    sh.save(OUTD + 'sheet_%s.jpg' % el['id'], quality=88)
    return sh.size
if __name__ == '__main__':
    ids = sys.argv[1:]
    for el in ELEMS:
        if ids and el['id'] not in ids: continue
        print(el['id'], build(el))
