import sys, numpy as np
from PIL import Image, ImageDraw
mode = sys.argv[1]
W = 'D:/rc_scratch/combat_redesign/locked/fx_o30/work/'
tiles = []
for i in range(1, 15):
    a = np.load(W + 'canvas_%s_%02d.npy' % (mode, i))
    tiles.append(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((640, 360)))
sh = Image.new('RGB', (640 * 4, 360 * 4))
for k, t in enumerate(tiles):
    sh.paste(t, ((k % 4) * 640, (k // 4) * 360))
    ImageDraw.Draw(sh).text(((k % 4) * 640 + 6, (k // 4) * 360 + 340), 'canvas %d' % (k + 1), fill=(255, 255, 0))
sh.save(W + 'sheet_cv_%s.jpg' % mode, quality=85)
