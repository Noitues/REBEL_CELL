"""campaign_slots.png: three saved campaigns as the Cell's own manila case files (build: PARITY/fixes/SLOTS_c.jpg).

Media: CAMPAIGN SLOTS = yellow title sticker; the folders are the Cell's own files, so they carry the CELL's
marks: a terminal tab-clip label on the tab (a little CRT label holder, mono) and the Cell's red hex/fist
rubber stamp, never a corp letterhead. Field text is Share Tech Mono (the Cell's printer), not Courier.
Designer ruling (round 44): LOAD and DELETE stickers on every folder, each DELETE with the red grease-pencil
CAN'T UNDO. Focus = the peel curl on the focused LOAD; one sticker (that LOAD) carries the scheduled sweep.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import b44 as K  # noqa: E402

U, SL = K.U, K.SL
MANILA = (222, 192, 138)
CELL_RED = (214, 24, 34)
INKP = (40, 34, 30)

SLOTS = [dict(n=1, corp='solace', name='SOLACE BIOSYSTEMS', heat=58, band='FLAGGED', ice=0, runs=9, filed='2026-10-06',
              crew=['breaker', 'ghost'], state='ACTIVE'),
         dict(n=2, corp='halcyon', name='HALCYON CIVIC', heat=22, band='COOL', ice=3, runs=4, filed='2026-10-02',
              crew=['phantom'], state='ACTIVE'),
         dict(n=3, corp='meridian', name='MERIDIAN FREIGHT', heat=81, band='HUNTED', ice=1, runs=14, filed='2026-09-28',
              crew=['wrecker', 'rigger', 'botnet'], state='ACTIVE')]


def cell_stamp(word, size=30, seed=5, angle=-7):
    """The Cell's rubber stamp: a hex frame with the raised fist and a mono word, in Cell red, inked unevenly."""
    w, h = 340, 120
    m = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(m)
    cx, cy, r = 58, 60, 48
    pts = [(cx + r * math.cos(math.radians(60 * k + 30)), cy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    d.polygon(pts, outline=255)
    for k in range(6):
        d.line([pts[k], pts[(k + 1) % 6]], fill=255, width=5)
    f = K.crest('rebel_cell', 52).split()[3]
    m.paste(255, (cx - 26, cy - 26), f)
    d.text((118, 44), word, font=U.F(U.MONO, size), fill=255, anchor='lm')
    d.text((118, 82), 'REBEL_CELL // OWN FILE', font=U.F(U.MONO, 17), fill=255, anchor='lm')
    d.line([(118, 64), (290, 64)], fill=255, width=2)
    rng = np.random.default_rng(seed)
    n = rng.random((h, w))
    n2 = np.asarray(Image.fromarray((rng.random((h // 5 + 1, w // 5 + 1)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
    a = np.asarray(m, np.float32) / 255 * (n > 0.16) * (0.6 + 0.4 * (n2 > 0.3))
    out = Image.new('RGBA', (w, h), CELL_RED + (0,))
    out.putalpha(Image.fromarray((a * 225).astype(np.uint8)))
    return out.rotate(angle, Image.BICUBIC, expand=True)


def tab_clip(img, box, label):
    """Terminal tab clip: a small navy CRT label holder clipped over the folder tab (the Cell's label)."""
    x0, y0, x1, y1 = box
    img = U.term_panel(img, box, None, accent=U.CYAN, hexbg=False, chamfer=5, header=False, glow=0.25, alpha=245)
    d = U.BD(img)
    for xx in (x0 + 2, x1 - 8):
        d.rectangle([xx, y0 - 5, xx + 6, y0 + 3], fill=(150, 160, 176, 255), outline=(40, 44, 54, 255))
    U.text(img, ((x0 + x1) / 2, (y0 + y1) / 2 + 1), label, U.F(U.MONO, 16), U.CYAN, 'mm', 1.4)
    return img


def folder(s, focus=False):
    """Draw one folder on its own RGBA layer (so it can tilt as a whole)."""
    fw, fh = 500, 430
    lay = Image.new('RGBA', (fw + 40, fh + 70), (0, 0, 0, 0))
    ox, oy = 20, 46
    # back cover + tab
    tab = Image.new('L', lay.size, 0)
    ImageDraw.Draw(tab).polygon([(ox + 18, oy), (ox + 38, oy - 40), (ox + 250, oy - 40), (ox + 270, oy)], fill=255)
    back = U.paper_tex(lay.width, lay.height, seed=10 + s['n'], col=tuple(int(c * 0.88) for c in MANILA), fold=False)
    back.putalpha(tab)
    lay = Image.alpha_composite(lay, back)
    front = U.paper_tex(fw, fh, seed=20 + s['n'], col=MANILA, fold=False)
    fm = Image.new('L', (fw, fh), 0)
    ImageDraw.Draw(fm).rounded_rectangle([0, 0, fw - 1, fh - 1], 8, fill=255)
    front.putalpha(fm)
    # front edge shading (the cover sits on the back)
    lay.alpha_composite(front, (ox, oy))
    d = ImageDraw.Draw(lay)
    d.line([(ox + 4, oy + 1), (ox + fw - 4, oy + 1)], fill=(255, 240, 210, 140), width=2)
    # field text (mono, the Cell's printer)
    fx, fy = ox + 28, oy + 30
    f_t = U.F(U.MONO, 28)
    d.text((fx, fy), s['name'], font=f_t, fill=INKP + (255,), anchor='la')
    cr = K.crest(s['corp'], 30, INKP)
    lay.alpha_composite(cr, (ox + fw - 58, fy))
    d.line([(fx, fy + 44), (ox + fw - 28, fy + 44)], fill=INKP + (160,), width=2)
    rows = [('HEAT', '%d  %s' % (s['heat'], s['band'])), ('ICE', str(s['ice'])), ('RUNS', str(s['runs'])), ('FILED', s['filed'])]
    for k, (a, b) in enumerate(rows):
        y = fy + 64 + k * 34
        d.text((fx, y), a, font=U.F(U.MONO, 18), fill=(96, 80, 60, 255), anchor='la')
        d.text((fx + 96, y), b, font=U.F(U.MONO, 21), fill=INKP + (255,), anchor='la')
    # heat ink bar
    bx, by = fx + 240, fy + 70
    d.rectangle([bx, by, bx + 180, by + 12], outline=INKP + (220,), width=2)
    hc = {'COOL': (40, 120, 140), 'FLAGGED': (210, 110, 20), 'HUNTED': (200, 30, 36)}[s['band']]
    d.rectangle([bx + 3, by + 3, bx + 3 + int(174 * s['heat'] / 100), by + 9], fill=hc + (255,))
    # crew polaroids
    for k, cls in enumerate(s['crew']):
        px, py = fx + k * 100, oy + 250
        pol = Image.new('RGBA', (84, 102), (246, 244, 238, 255))
        b = K.bust(cls, 72).crop((0, 0, 72, 78))
        bg = Image.new('RGBA', (72, 78), (34, 30, 44, 255))
        bg.alpha_composite(b)
        pol.paste(bg, (6, 6))
        ImageDraw.Draw(pol).text((42, 93), cls.upper(), font=U.F(U.MONO, 12), fill=INKP + (255,), anchor='mm')
        pol = pol.rotate(random.Random(k + s['n']).uniform(-5, 5), Image.BICUBIC, expand=True)
        sh = Image.new('RGBA', pol.size, (0, 0, 0, 0))
        sh.putalpha(pol.split()[3].filter(ImageFilter.GaussianBlur(3)).point(lambda v: v * 0.45))
        lay.alpha_composite(sh, (px + 3, py + 4))
        lay.alpha_composite(pol, (px, py))
    # the Cell's stamp
    st = cell_stamp(s['state'], seed=s['n'], angle=-6 + s['n'] * 2)
    st = st.resize((int(st.width * 0.74), int(st.height * 0.74)), Image.LANCZOS)
    lay.alpha_composite(st, (ox + fw - st.width - 4, oy + 128))
    return lay


def main():
    img = K.city_backdrop()
    P = (100, 150, 1820, 985)
    img = K.darken(img, P, 0.45, 50)
    img = U.term_panel(img, P, 'CAMPAIGN SLOTS  //  3 OF 3 FILED', seed=45, alpha=232, glow=0.45)
    t = K.stk('CAMPAIGN SLOTS', 58, U.FILL_YELLOW, seed=91)
    img = K.place(img, t, 100 + K.sw(t)[0] / 2, 84, angle=-2)
    FX = [160, 720, 1280]
    for k, s in enumerate(SLOTS):
        foc = k == 0
        lay = folder(s, foc)
        ang = random.Random(70 + k).uniform(-1.4, 1.4) if not foc else 0.0
        lay = lay.rotate(ang, Image.BICUBIC, expand=True)
        x, y = FX[k] - 20, 254 - 46 + (0 if foc else 6)
        full = Image.new('L', img.size, 0)
        full.paste(lay.split()[3], (x, y))
        img = U.shadow(img, full, (8, 14) if not foc else (14, 24), 14 if not foc else 22, 0.6)
        img = K.paste_at(img, lay, x, y)
        tl = 'SLOT %d  //  CELL-0%d' % (s['n'], 3 + k)
        img = tab_clip(img, (FX[k] + 40, 218 + (0 if foc else 6), FX[k] + 262, 246 + (0 if foc else 6)), tl)
    # verbs (designer ruling: LOAD + DELETE on every folder, each DELETE with CAN'T UNDO in red pencil)
    pen = U.Pencil(img.size, U.PEN_R, seed=33)
    for k, s in enumerate(SLOTS):
        foc = k == 0
        cx = FX[k]
        ld = K.stk('LOAD', 50, U.FILL_PINK, seed=100 + k, focus=foc, sweep=foc)
        img = K.place(img, ld, cx + 90, 800, angle=-3 + k, focus=foc)
        dl = K.stk('DELETE', 34, K.FILL_WHITE, seed=110 + k)
        img = K.place(img, dl, cx + 412, 802, angle=2 - k)
        pen.text("CAN'T UNDO", cx + 270, 888, 26, angle=-4)
        pen.arrow([(cx + 352, 882), (cx + 392, 868), (cx + 412, 838)], width=5, head=14)
    img = pen.ink(img, 0.85)
    img = K.term_row(img, (130, 928, 420, 966), 'BACK', key='[Esc]', size=20)
    img = K.pad_hints(img, 1240, 1036, [('A', 'load'), ('X', 'delete'), ('B', 'back')])
    U.text(img, (130, 1036), 'Files sit in user://campaigns  //  autosave after every node', U.F(U.MONO, 16), (140, 160, 184), 'lm', 0.6)
    K.save(img, 'campaign_slots.png')


if __name__ == '__main__':
    main()
