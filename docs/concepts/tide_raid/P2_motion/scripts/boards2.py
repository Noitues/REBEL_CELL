"""Build the 12 storyboard sheets on the P2 look: frame strip + Gantt timing ruler + beat table.  python boards2.py [slug ...]"""
import sys, os, math, time
sys.dont_write_bytecode = True
H2 = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/scripts'
sys.path.insert(0, H2)
sys.path.append('D:/rc_art/art-pass/docs/concepts/tide_raid/P1_motion/scripts')
import numpy as np
from PIL import Image, ImageDraw
from lib import font
import spec2 as SP
import boardscenes as BS
import scenes as S1

OUTDIR = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P2_motion/'
WORKD = 'D:/rc_scratch/tide_concepts/p2m_work/'


def crop_scale(a, box, size):
    x0, y0, x1, y1 = [int(v) for v in box]
    im = Image.fromarray(a).crop((x0, y0, x1, y1))
    return im.resize(tuple(size), Image.LANCZOS) if im.size != tuple(size) else im


BOARDS_DIR = OUTDIR + 'boards/'
TH = WORKD + 'thumbs/'
os.makedirs(BOARDS_DIR, exist_ok=True)
os.makedirs(TH, exist_ok=True)

VER = {k: '_p2b' for k in ['jackin', 'jackout', 'draw', 'dragv', 'dragi', 'daemon', 'lock', 'hunter', 'shield', 'home', 'poster', 'bloom', 'lost']}
BG = (9, 7, 22)
PAN = (18, 15, 40)
INKC = (232, 228, 244)
DIM = (150, 150, 185)
CY = (127, 239, 255)
AMB = (242, 154, 26)
LIM = (198, 255, 46)
PLM = (255, 63, 168)
GRID = (40, 36, 74)

BW = 2560
M = 40


def F(sz, wght=600, wdth=85):
    return font(sz, False, wght, wdth)


def FM(sz):
    return font(sz, True)


def wrap(d, text, fnt, width):
    words = text.split(' ')
    lines, cur = [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if fnt.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def ms(f):
    return int(round(f * 1000 / 30.0))


BOX = {
    'jackin': (0, 0, 1920, 1080), 'jackout': (0, 0, 1920, 1080), 'draw': (700, 560, 1900, 1080),
    'dragv': (330, 300, 1230, 1010), 'dragi': (330, 300, 1230, 1010), 'daemon': (330, 300, 1290, 840),
    'lock': (1100, 330, 1700, 668), 'hunter': (700, 250, 1500, 800), 'shield': (330, 300, 1000, 760),
    'home': (0, 420, 960, 960), 'poster': (580, 300, 1280, 900), 'bloom': (100, 230, 1180, 905), 'lost': (0, 0, 1920, 1080),
}
_R = BS.board_renderers()
RENDER = {k: (_R[k], BOX[k]) for k in _R}


def thumb(rkey, f, tw):
    fn, box = RENDER[rkey]
    p = TH + '%s%s_%d_%d.png' % (rkey, VER.get(rkey, ''), f, tw)
    if os.path.exists(p):
        return Image.open(p).convert('RGB')
    t = time.time()
    a = fn(f)
    th = int(round(tw * (box[3] - box[1]) / (box[2] - box[0])))
    im = crop_scale(a, box, (tw, th))
    im.save(p)
    print('  thumb', rkey, f, round(time.time() - t, 1), flush=True)
    return im


# ------------------------------------------------------------------ drawing helpers
def curve(d, x, y, w, h, name, col=CY):
    d.rectangle((x, y, x + w, y + h), outline=GRID)
    fn = SP.__dict__.get('_c') or None
    from tl import EASE
    f = EASE[name]
    pts = []
    if name == 'STEP':
        pts = [(x, y + h), (x + w * .5, y + h), (x + w * .5, y), (x + w, y)]
    elif name == 'HOLD':
        pts = [(x, y + h * .5), (x + w, y + h * .5)]
    else:
        for i in range(41):
            t = i / 40
            v = f(t)
            pts.append((x + t * w, y + h - (min(max(v, -.05), 1.3) / 1.3 * (h - 6)) - 3 - h * .0))
    d.line(pts, fill=col, width=2)


def hatch(d, x0, y0, x1, y1, col):
    for xx in range(int(x0) - 20, int(x1), 8):
        d.line([(max(x0, xx), min(y1, y1 - (max(x0, xx) - xx) + 0) if False else y1), (min(x1, xx + (y1 - y0)), y0 + max(0, (xx + (y1 - y0)) - x1) * 0 if False else y0)], fill=col, width=1)


def hatch_rect(d, x0, y0, x1, y1, col):
    h = y1 - y0
    xx = x0 - h
    while xx < x1:
        xa, ya = xx, y1
        xb, yb = xx + h, y0
        # clip to rect
        if xa < x0:
            ya = y1 - (x0 - xa)
            xa = x0
        if xb > x1:
            yb = y0 + (xb - x1)
            xb = x1
        if xb > xa:
            d.line([(xa, ya), (xb, yb)], fill=col, width=1)
        xx += 7


def build(bd):
    slug = bd['slug']
    rows = [(bd['render'], bd['frames'])]
    if bd.get('two_rows'):
        rows = [('dragv', bd['frames']), ('dragi', bd['frames_invalid'])]
    # ---- layout
    thumbs_rows = []
    for rk, frs in rows:
        n = len(frs)
        cols = n if n <= 6 else int(math.ceil(n / 2.0))
        if bd.get('two_rows'):
            cols = n
        tw = int((BW - 2 * M - (cols - 1) * 16) / cols)
        ims = [thumb(rk, f, tw) for f in frs]
        thumbs_rows.append((rk, frs, cols, tw, ims))
    beats = bd['beats']
    total = bd['total']
    # ---- measure beat table
    cw = [62, 330, 190, 120, 560, 250, 520, 120, 250]
    d0 = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    fT = F(17, 500, 80)
    fH = F(15, 700, 80)
    rowh = []
    wrapped = []
    for b in beats:
        key, label, f0, f1, ease, means, sound, cite, skip, red = b
        cols_txt = [label, means, sound, cite, skip, red]
        ws = [cw[1] - 14, cw[4] - 14, cw[5] - 14, cw[6] - 14, cw[7] - 14, cw[8] - 14]
        wl = [wrap(d0, t, fT, wd) for t, wd in zip(cols_txt, ws)]
        wrapped.append(wl)
        rowh.append(max(len(x) for x in wl) * 22 + 20)
    thumbs_h = sum(max(im.size[1] for im in ims) * (1 if len(ims) <= len(ims) else 1) for _, _, _, _, ims in thumbs_rows)
    # rows of thumbs (a strip may wrap to 2 lines)
    strip_hs = []
    for rk, frs, cols, tw, ims in thumbs_rows:
        nl = int(math.ceil(len(ims) / float(cols)))
        th = ims[0].size[1]
        strip_hs.append(nl * (th + 64))
    gantt_h = 60 + len(beats) * 32 + 20
    tab_h = 54 + sum(rowh)
    extras = bd.get('extras', [])
    foot_h = 40 + 26 * len(extras)
    hdr = 150
    Ht = hdr + sum(strip_hs) + 20 * len(strip_hs) + gantt_h + tab_h + foot_h + 40
    im = Image.new('RGB', (BW, Ht), BG)
    d = ImageDraw.Draw(im)
    # ---- header
    d.text((M, 20), 'BOARD %s' % bd['id'], font=F(54, 800, 75), fill=CY)
    d.text((M + 230, 20), bd['title'], font=F(54, 800, 75), fill=INKC)
    d.text((BW - M, 30), '30 fps  |  %d f = %.2f s  |  interactive from f%d (%.2f s)' % (total, total / 30.0, bd['ready'], bd['ready'] / 30.0),
           font=F(30, 700, 80), fill=AMB, anchor='ra')
    ml = wrap(d, 'MEANS, WITH NO TEXT:  ' + bd['means'], F(26, 500, 85), BW - 2 * M)
    for i, l in enumerate(ml[:3]):
        d.text((M, 88 + i * 32), l, font=F(26, 500, 85), fill=(206, 214, 255))
    y = hdr
    chip_i = 1
    # ---- thumbs
    for si, (rk, frs, cols, tw, ims) in enumerate(thumbs_rows):
        th = ims[0].size[1]
        if bd.get('two_rows'):
            d.text((M, y - 6), 'VALID DROP' if si == 0 else 'INVALID DROP (the Site refuses)', font=F(24, 800, 80), fill=LIM if si == 0 else (255, 90, 100))
            y += 24
        for i, (f, ti) in enumerate(zip(frs, ims)):
            cx = M + (i % cols) * (tw + 16)
            cy = y + (i // cols) * (th + 64)
            im.paste(ti, (cx, cy))
            d.rectangle((cx - 1, cy - 1, cx + tw, cy + th), outline=GRID)
            d.rectangle((cx, cy, cx + 54, cy + 34), fill=(9, 7, 22))
            d.text((cx + 27, cy + 17), '%d' % (i + 1), font=F(26, 800, 80), fill=CY, anchor='mm')
            beat_now = [b[1] for b in beats if b[2] <= f < max(b[3], b[2] + 1)]
            cap = 'f%03d  %.2fs' % (f, f / 30.0)
            d.text((cx, cy + th + 6), cap, font=FM(21), fill=AMB)
            nm = beat_now[0] if beat_now else ''
            d.text((cx, cy + th + 32), nm[:60], font=F(19, 600, 80), fill=DIM)
        y += strip_hs[si] + 20
    # ---- Gantt ruler
    d.rectangle((M, y, BW - M, y + gantt_h - 10), fill=PAN)
    gx0, gx1 = 760, BW - M - 20
    sc = (gx1 - gx0) / float(total * 1.14 + 2)
    d.text((M + 14, y + 8), 'TIMING RULER  (1 tick = 1 f, long tick = 5 f)', font=F(20, 800, 80), fill=INKC)
    yy = y + 40
    # ticks
    for f in range(0, total + 1):
        x = gx0 + f * sc
        h_ = 12 if f % 5 == 0 else 5
        d.line([(x, yy), (x, yy + h_)], fill=DIM if f % 5 == 0 else GRID, width=1)
        if f % 10 == 0 or (total <= 40 and f % 5 == 0):
            d.text((x, yy + 14), str(f), font=FM(16), fill=DIM, anchor='ma')
    # key frame lines
    allkf = []
    for rk, frs, cols, tw, ims in thumbs_rows[:1]:
        allkf = frs
    for i, f in enumerate(allkf):
        x = gx0 + min(f, total) * sc
        d.line([(x, yy + 28), (x, y + gantt_h - 16)], fill=(70, 120, 140), width=1)
        d.rectangle((x - 13, yy - 18, x + 13, yy - 1), fill=CY)
        d.text((x, yy - 10), str(i + 1), font=F(15, 800, 80), fill=BG, anchor='mm')
    by = yy + 36
    for bi, b in enumerate(beats):
        key, label, f0, f1, ease, means, sound, cite, skip, red = b
        ry = by + bi * 32
        d.text((M + 14, ry + 2), '%s' % label[:44], font=F(19, 600, 80), fill=INKC)
        d.text((M + 14 + 440, ry + 4), key, font=FM(16), fill=DIM)
        x0 = gx0 + f0 * sc
        x1 = gx0 + max(f1, f0 + .6) * sc
        if ease == 'HOLD':
            d.rectangle((x0, ry + 2, x1, ry + 24), fill=(60, 44, 20), outline=AMB)
            hatch_rect(d, x0 + 1, ry + 3, x1 - 1, ry + 23, (140, 100, 40))
        elif ease == 'STEP':
            d.rectangle((x0, ry + 2, max(x1, x0 + 6), ry + 24), fill=(240, 240, 255))
        else:
            d.rectangle((x0, ry + 2, x1, ry + 24), fill=(28, 90, 110), outline=CY)
            curve(d, x0 + 2, ry + 4, max(10, x1 - x0 - 4), 18, ease, col=(200, 250, 255))
        d.text((x1 + 8, ry + 3), '%d f / %d ms / %s' % (f1 - f0, ms(f1 - f0), ease), font=FM(16), fill=DIM)
    y += gantt_h
    # ---- table
    d.rectangle((M, y, BW - M, y + tab_h - 10), fill=PAN)
    heads = ['#', 'BEAT', 'FRAMES', 'EASE', 'WHAT IT MEANS (no text)', 'SOUND CUE', 'REFERENCE NUMBER BEATEN / BORROWED', 'SKIP', 'REDUCE-MOTION']
    x = M
    xs = []
    for hname, wd_ in zip(heads, cw):
        d.text((x + 8, y + 12), hname, font=fH, fill=CY)
        xs.append(x)
        x += wd_
    yy = y + 44
    for bi, b in enumerate(beats):
        key, label, f0, f1, ease, means, sound, cite, skip, red = b
        wl = wrapped[bi]
        d.line([(M, yy - 4), (BW - M, yy - 4)], fill=GRID)
        d.text((xs[0] + 8, yy + 2), str(bi + 1), font=F(20, 800, 80), fill=AMB)
        for ci, lines in zip((1, 4, 5, 6, 7, 8), wl):
            for li, l in enumerate(lines):
                col = INKC if ci in (1, 4) else (190, 195, 225)
                d.text((xs[ci] + 8, yy + 2 + li * 22), l, font=fT, fill=col)
        d.text((xs[2] + 8, yy + 2), 'f%d-f%d' % (f0, f1), font=FM(18), fill=INKC)
        d.text((xs[2] + 8, yy + 26), '%d f  %d ms' % (f1 - f0, ms(f1 - f0)), font=FM(16), fill=DIM)
        curve(d, xs[3] + 8, yy + 4, 90, 40, ease)
        d.text((xs[3] + 8, yy + 48), ease, font=FM(13), fill=DIM)
        yy += rowh[bi]
    y += tab_h
    # ---- footer: extras
    d.text((M, y + 4), 'tide_look.tres extras', font=F(18, 800, 80), fill=CY)
    for i, (k, v, note) in enumerate(extras):
        d.text((M, y + 30 + i * 26), '%s = %s' % (k, v), font=FM(18), fill=AMB)
        d.text((M + 560, y + 30 + i * 26), note, font=F(17, 500, 80), fill=DIM)
    out = BOARDS_DIR + 'board_%s_%s.png' % (bd['id'], slug)
    im.save(out)
    print('saved', out, im.size, flush=True)


if __name__ == '__main__':
    want = sys.argv[1:]
    for bd in SP.BOARDS:
        if want and bd['slug'] not in want:
            continue
        if bd['slug'] == 'daemon':
            D = S1.dmn()
            bd["frames"] = [0, 30, 36, 45, 58, D.f_arr - 3, D.f_arr, D.f_arr + 2, D.f_arr + 8, D.f_arr + 40]
        build(bd)
