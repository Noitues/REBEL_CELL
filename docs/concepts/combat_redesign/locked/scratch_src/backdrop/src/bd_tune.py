"""bd_tune.py <params.json> [room ...]   compose the after grade under the neutral p1 board, measure, and write a
look sheet work/tune_<tag>.jpg (per room: before | after room crop, and the after plate at 1/2)."""
import sys, json, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import bd_measure as M

pf = sys.argv[1]
PJ = json.load(open(pf))
tag = os.path.splitext(os.path.basename(pf))[0]
rooms = sys.argv[2:] or M.ROOMS
B = json.load(open(M.HERE + 'work/before.json'))
reg = M.regions('neutral')
CROP = (1120, 360, 1920, 860)
fnt = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
rows = []
res = {}
for r in rooms:
    P = dict(PJ.get('_common', {}), **PJ.get(r, {}))
    pl = M.compose(M.after_backdrop(r, P))
    Image.fromarray(pl.astype(np.uint8)).save(M.HERE + 'work/after_%s_%s.png' % (tag, r))
    st = M.measure(pl, 'neutral', reg)
    res[r] = st
    b = B['%s_neutral' % r]
    print('%-6s room mean %.3f->%.3f p95 %.3f->%.3f loud %.3f->%.3f | vis %.3f->%.3f | plate loud %.3f->%.3f | detail %.4f->%.4f sat %.3f->%.3f | b/r mean %.2f->%.2f rings %.3f' % (
        r, b['room']['mean'], st['room']['mean'], b['room']['p95'], st['room']['p95'], b['room']['loud'], st['room']['loud'],
        b['backdrop_visible']['mean'], st['backdrop_visible']['mean'], b['plate']['loud'], st['plate']['loud'],
        b['room_detail']['detail_rms'], st['room_detail']['detail_rms'], b['room_detail']['sat'], st['room_detail']['sat'],
        b['board_vs_room']['mean_ratio'], st['board_vs_room']['mean_ratio'], st['rings']['mean']), flush=True)
    bef = Image.open(M.HERE + 'work/before_%s_neutral.png' % r).crop(CROP)
    aft = Image.fromarray(pl.astype(np.uint8))
    row = Image.new('RGB', (800 * 2 + 960, 540), (0, 0, 0))
    row.paste(bef, (0, 20))
    row.paste(aft.crop(CROP), (800, 20))
    row.paste(aft.resize((960, 540), Image.LANCZOS), (1600, 0))
    d = ImageDraw.Draw(row)
    d.text((6, 0), '%s before  room mean %.3f p95 %.3f' % (r, b['room']['mean'], b['room']['p95']), font=fnt, fill=(255, 255, 255))
    d.text((806, 0), 'after  room mean %.3f p95 %.3f detail %.3f' % (st['room']['mean'], st['room']['p95'], st['room_detail']['detail_rms']), font=fnt, fill=(255, 255, 255))
    rows.append(row)
sheet = Image.new('RGB', (rows[0].width, 540 * len(rows)))
for i, rw in enumerate(rows):
    sheet.paste(rw, (0, 540 * i))
sheet.save(M.HERE + 'work/tune_%s.jpg' % tag, quality=88)
json.dump(res, open(M.HERE + 'work/tune_%s.json' % tag, 'w'), indent=1)
