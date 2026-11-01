"""v3 sheets: sheet.jpg (7 composites + squints), v2_vs_v3_density.jpg, stats.json. usage: python sheet_v3.py"""
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/scripts')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bd_common as B
import kit_gen

V3 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3/'
V2 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/'
f = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf', 22)
fs = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf', 16)
ROOMS = [('bio', 'bio_lab', 11, 'BIO-LAB'), ('srv', 'server_room', 23, 'SERVER ROOM'), ('gh', 'greenhouse', 37, 'GREENHOUSE'),
         ('rec', 'records_office', 41, 'RECORDS / OFFICE'), ('lobby', 'lobby', 53, 'LOBBY / RECEPTION'),
         ('event', 'event_room', 67, 'EVENT ROOM (street proposal)'), ('shop', 'shop', 71, 'SHOP (street proposal, street level)')]
LIME = (150, 255, 70)

stats = {}
for n, rt, sd, t in ROOMS:
    plate = np.asarray(Image.open(V3 + 'room_%s.png' % n).convert('RGB')).astype(np.float32) / 255
    st = B.stats(plate, n)
    sp = kit_gen.generate(rt, sd)
    st.update(sp['rules']); st['seed'] = sd; st['room_type'] = rt
    st['v2_fill'] = kit_gen.generate(rt, sd, v2=True)['rules']['density']
    stats[n] = st
json.dump(stats, open(V3 + 'stats.json', 'w'), indent=1)

W, H = 960, 540
im = Image.new('RGB', (W * 2, (H + 36) * len(ROOMS)), (8, 6, 18))
d = ImageDraw.Draw(im)
for i, (n, rt, sd, t) in enumerate(ROOMS):
    y = i * (H + 36)
    s = stats[n]
    d.text((10, y + 6), 'CUTAWAY v3  %s  seed %d  fill %.2f   squint mean %.2f p95 %.2f loud %.1f%%' % (t, sd, s['density'], s['mean'], s['p95'], 100 * s['loud']), font=f, fill=LIME)
    im.paste(Image.open(V3 + 'room_%s.png' % n).convert('RGB').resize((W, H), Image.LANCZOS), (0, y + 36))
    im.paste(Image.open(V3 + 'squint_%s.png' % n).convert('RGB').resize((W, H), Image.LANCZOS), (W, y + 36))
im.save(V3 + 'sheet.jpg', quality=90)

# v2 vs v3 density: crops of the room, bio / srv / gh
box = (1150, 300, 1850, 1000)
T = 560
im = Image.new('RGB', (T * 2 + 30, (T + 40) * 3 + 230), (8, 6, 18))
d = ImageDraw.Draw(im)
for i, (n, rt, sd, t) in enumerate(ROOMS[:3]):
    y = i * (T + 40)
    s = stats[n]
    d.text((10, y + 8), '%s seed %d   v2 fill %.2f   ->   v3 fill %.2f (hard props %.2f + clutter %d)' % (t, sd, s['v2_fill'], s['density'], s['density_hard'], s['clutter']), font=f, fill=LIME)
    a = Image.open(V2 + 'room_%s_bare.png' % n).convert('RGB').crop(box).resize((T, T), Image.LANCZOS)
    b = Image.open(V3 + 'room_%s_bare.png' % n).convert('RGB').crop(box).resize((T, T), Image.LANCZOS)
    im.paste(a, (10, y + 40)); im.paste(b, (T + 20, y + 40))
# bar chart
y0 = 3 * (T + 40) + 20
d.text((10, y0), 'fill ratio (cells / 63), target band 0.50-0.70 shaded', font=f, fill=LIME)
cx0, cx1 = 60, T * 2 + 20
cy_b, ch = y0 + 200, 150
d.rectangle([cx0, cy_b - 0.70 * ch / 0.8, cx1, cy_b - 0.50 * ch / 0.8], fill=(30, 50, 40))
bw = (cx1 - cx0) / len(ROOMS)
for i, (n, rt, sd, t) in enumerate(ROOMS):
    s = stats[n]
    x = cx0 + i * bw
    for k, (val, col) in enumerate(((s['v2_fill'], (110, 110, 140)), (s['density_hard'], (60, 150, 140)), (s['density'], LIME))):
        h = val * ch / 0.8
        d.rectangle([x + 8 + k * 30, cy_b - h, x + 34 + k * 30, cy_b], fill=col)
    d.text((x + 8, cy_b + 6), n, font=fs, fill=(214, 226, 214))
d.text((cx0, y0 + 24), 'grey = v2 generator   teal = v3 without clutter   lime = v3 total', font=fs, fill=(150, 165, 150))
im.save(V3 + 'v2_vs_v3_density.jpg', quality=90)
for n, s in stats.items():
    print(n, s['seed'], 'v2', s['v2_fill'], 'v3', s['density'], 'hard', s['density_hard'], 'clutter', s['clutter'], 'props', s['props'],
          'mean %.3f p95 %.3f loud %.3f sat %.3f' % (s['mean'], s['p95'], s['loud'], s['sat']))
