import sys
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont
R = 'D:/rc_scratch/combat_redesign/punk_slices/spiderpunk_collage/'
OLD = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/punk/spiderpunk_collage/plate_A.png'
FD = 'D:/rc_art/art-pass/assets/fonts/'
ANT = lambda s: ImageFont.truetype(FD + 'Anton-Regular.ttf', s)
PLX = lambda s: ImageFont.truetype(FD + 'IBMPlexSansCondensed-Medium.ttf', s)
out = sys.argv[1]
srcs = [(OLD, 'OLD  one colour (A as delivered)'), (R + 'sl_out/s2_plate_A.png', 'A  POSTER  one colour per slice type'), (R + 'sl_out/s2_plate_B.png', 'B  GIG FLYER  one colour per slice type')]
cx, cy, r = 535, 540, 262
ims = []
for p, _ in srcs:
    im = Image.open(p).convert('RGB').crop((cx - r, cy - r, cx + r, cy + r))
    ims.append(im.resize((im.width * 2, im.height * 2), Image.LANCZOS))
w, h = ims[0].size
W = Image.new('RGB', (w * 3 + 40, h + 80), (22, 18, 30))
d = ImageDraw.Draw(W)
for i, (im, (_, lab)) in enumerate(zip(ims, srcs)):
    W.paste(im, (10 + i * (w + 10), 70))
    d.text((20 + i * (w + 10), 14), lab, font=ANT(34), fill=(255, 204, 0))
W.save(out, quality=92)
print(W.size)
