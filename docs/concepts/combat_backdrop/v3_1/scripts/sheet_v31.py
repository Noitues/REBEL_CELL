"""v3.1 sheets: sheet.jpg (7 composites + squints), v3_vs_v3_1.jpg (per room, crops side by side), stats.json. usage: python sheet_v31.py"""
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/scripts')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bd_common as B
import kit_gen

N = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/'
O = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3/'
f = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf', 22)
fs = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf', 16)
ROOMS = [('bio', 'bio_lab', 11, 'BIO-LAB'), ('srv', 'server_room', 23, 'SERVER ROOM'), ('gh', 'greenhouse', 37, 'GREENHOUSE'),
         ('rec', 'records_office', 41, 'RECORDS / OFFICE'), ('lobby', 'lobby', 53, 'LOBBY / RECEPTION'),
         ('event', 'event_room', 67, 'EVENT ROOM (street proposal)'), ('shop', 'shop', 71, 'SHOP (street proposal, street level)')]
LIME = (150, 255, 70)
v3s = json.load(open(O + 'stats.json'))
stats = {}
for n, rt, sd, t in ROOMS:
    plate = np.asarray(Image.open(N + 'room_%s.png' % n).convert('RGB')).astype(np.float32) / 255
    st = B.stats(plate, n)
    sp = kit_gen.generate(rt, sd)
    st.update(sp['rules']); st['seed'] = sd; st['room_type'] = rt
    st['v3_fill'] = v3s[n]['density']; st['v3_hard'] = v3s[n]['density_hard']
    st['v3_mean'] = v3s[n]['mean']; st['v3_p95'] = v3s[n]['p95']; st['v3_loud'] = v3s[n]['loud']
    st['cable_paths'] = [dict(a=c['a'], b=c['b'], cells=len(c['cells']), new_cells=c['new']) for c in sp['cables']]
    st['puddles'] = len(sp['decals'])
    stats[n] = st
json.dump(stats, open(N + 'stats.json', 'w'), indent=1)

W, H = 960, 540
im = Image.new('RGB', (W * 2, (H + 36) * len(ROOMS)), (8, 6, 18))
d = ImageDraw.Draw(im)
for i, (n, rt, sd, t) in enumerate(ROOMS):
    y = i * (H + 36)
    s = stats[n]
    d.text((10, y + 6), 'CUTAWAY v3.1  %s  seed %d  fill %.2f hard %.2f   squint mean %.2f p95 %.2f loud %.1f%%' % (t, sd, s['density'], s['density_hard'], s['mean'], s['p95'], 100 * s['loud']), font=f, fill=LIME)
    im.paste(Image.open(N + 'room_%s.png' % n).convert('RGB').resize((W, H), Image.LANCZOS), (0, y + 36))
    im.paste(Image.open(N + 'squint_%s.png' % n).convert('RGB').resize((W, H), Image.LANCZOS), (W, y + 36))
im.save(N + 'sheet.jpg', quality=90)

# v3 vs v3.1: per room crop of the room, side by side
box = (1100, 280, 1900, 1000)
CW, CH = 640, 576
im = Image.new('RGB', (CW * 2 + 30, (CH + 40) * len(ROOMS)), (8, 6, 18))
d = ImageDraw.Draw(im)
for i, (n, rt, sd, t) in enumerate(ROOMS):
    y = i * (CH + 40)
    s = stats[n]
    d.text((10, y + 8), '%s seed %d   v3 fill %.2f hard %.2f   ->   v3.1 fill %.2f hard %.2f   (cables %d, clutter %d, extras %s)' % (
        t, sd, s['v3_fill'], s['v3_hard'], s['density'], s['density_hard'], s['cables'], s['clutter'], ','.join(s['extras'])), font=fs, fill=LIME)
    a = Image.open(O + 'room_%s_bare.png' % n).convert('RGB').crop(box).resize((CW, CH), Image.LANCZOS)
    b = Image.open(N + 'room_%s_bare.png' % n).convert('RGB').crop(box).resize((CW, CH), Image.LANCZOS)
    im.paste(a, (10, y + 40)); im.paste(b, (CW + 20, y + 40))
im.save(N + 'v3_vs_v3_1.jpg', quality=90)
for n, s in stats.items():
    print(n, s['seed'], 'v3', s['v3_fill'], s['v3_hard'], 'v3.1', s['density'], 'hard', s['density_hard'], 'clutter', s['clutter'], 'cables', s['cables'], 'props', s['props'],
          'mean %.3f p95 %.3f loud %.3f sat %.3f' % (s['mean'], s['p95'], s['loud'], s['sat']))
