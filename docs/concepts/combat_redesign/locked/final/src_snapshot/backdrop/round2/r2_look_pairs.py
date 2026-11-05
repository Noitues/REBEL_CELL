"""r2_look_pairs.py -- from the PUBLISHED backdrop plates: 1:1 crops of the room under the HUD (x 1060-1920, y 540-860), two plates per
strip (1728 x 340), plus the left city strip (x 0-300, y 0-1080) of all nine plates side by side at 1:1.  Writes
round2/backdrop/work/look/room_<a>__<b>.png and city_all.png."""
import sys, os
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
D = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
OUT = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/work/look/'
os.makedirs(OUT, exist_ok=True)
names = ['p1_bio', 'p1_srv', 'p1_gh', 'p1_rec', 'p1_lobby', 'p1_event', 'p1_shop', 'p1_bio_solace', 'p1_shop_meridian']
fnt = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
ims = {n: Image.open(D + n + '.png').convert('RGB') for n in names}
for i in range(0, len(names), 2):
    pair = names[i:i + 2]
    s = Image.new('RGB', (860 * 2 + 8, 320 + 24), (255, 0, 255))
    d = ImageDraw.Draw(s)
    for j, n in enumerate(pair):
        s.paste(ims[n].crop((1060, 540, 1920, 860)), (j * 868, 24))
        d.text((j * 868 + 4, 2), n, font=fnt, fill=(255, 255, 255))
    s.save(OUT + 'room_%s.png' % '__'.join(pair))
c = Image.new('RGB', (300 * 9 + 8 * 8, 1080), (255, 0, 255))
for j, n in enumerate(names):
    c.paste(ims[n].crop((0, 0, 300, 1080)), (j * 308, 0))
c.save(OUT + 'city_all.png')
print(sorted(os.listdir(OUT)))
