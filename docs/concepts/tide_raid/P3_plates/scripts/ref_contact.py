import os, glob
from PIL import Image, ImageDraw
out = []
for g in ('cp2077', 'frostpunk', 'wd2'):
    for f in sorted(glob.glob('D:/rc_scratch/tide_concepts/refs/%s/s*.jpg' % g)):
        out.append((g + '/' + os.path.basename(f), f))
cols = 6
tw, th = 320, 180
rows = (len(out) + cols - 1) // cols
sh = Image.new('RGB', (cols * tw, rows * (th + 14)), (10, 10, 20))
d = ImageDraw.Draw(sh)
for i, (n, f) in enumerate(out):
    r, c = divmod(i, cols)
    sh.paste(Image.open(f).convert('RGB').resize((tw, th)), (c * tw, r * (th + 14) + 14))
    d.text((c * tw + 3, r * (th + 14) + 1), n, fill=(200, 220, 255))
sh.save('D:/rc_scratch/tide_concepts/p3_work/ref_contact.png')
print(len(out))
