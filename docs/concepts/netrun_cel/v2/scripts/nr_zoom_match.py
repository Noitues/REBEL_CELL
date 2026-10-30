"""zoom_match.jpg: frame 1 (real r43 capture) cropped to the frame-2 camera rectangle, beside frame 2, a 50% blend and a difference-free edge overlay.
Usage: python nr_zoom_match.py <frame1.png> <frame2.png> <out.jpg> [zoom=3.0]"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
f1p, f2p, out = sys.argv[1:4]
Z = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0
PIX = (1330, 560)
f1 = Image.open(f1p).convert('RGB').resize((1920, 1080)); f2 = Image.open(f2p).convert('RGB').resize((1920, 1080))
w, h = 1920 / Z, 1080 / Z
box = (int(PIX[0] - w / 2), int(PIX[1] - h / 2), int(PIX[0] + w / 2), int(PIX[1] + h / 2))
crop = f1.crop(box).resize((1920, 1080), Image.LANCZOS)
blend = Image.blend(crop, f2, 0.5)
# edge overlay: Blender frame's bright edges (neon + ink) drawn over the crop
edges = f2.convert('L').filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0)
ov = crop.copy(); ov.paste((120, 255, 70), mask=edges)
fb = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 28)
W, H = 960, 540
S = Image.new('RGB', (W * 2 + 30, H * 2 + 30 + 2 * 36), (14, 8, 28)); d = ImageDraw.Draw(S)
tiles = [(crop, 'FRAME 1 (r43 capture), cropped to the zoom rectangle'), (f2, 'FRAME 2 (Blender, same camera x%.1f, same lots)' % Z), (blend, '50% BLEND'), (ov, 'FRAME 2 EDGES (green) OVER FRAME 1')]
for k, (im, t) in enumerate(tiles):
    x = 10 + (k % 2) * (W + 10); y = 10 + (k // 2) * (H + 46)
    d.text((x, y), t, font=fb, fill=(150, 255, 70)); S.paste(im.resize((W, H), Image.LANCZOS), (x, y + 36))
S.save(out, quality=92)
# also a simple red rectangle on frame 1 for the report
r = f1.copy(); ImageDraw.Draw(r).rectangle(box, outline=(150, 255, 70), width=4); r.save(out.replace('.jpg', '_rect.png'))
print('box', box)
