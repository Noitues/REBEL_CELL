import sys
from PIL import Image
# usage: wr_view.py out.png x0 y0 x1 y1 scale file1 file2 ...
out = sys.argv[1]; x0, y0, x1, y1 = map(int, sys.argv[2:6]); sc = float(sys.argv[6]); files = sys.argv[7:]
ims = []
for f in files:
    im = Image.open('D:/rc_scratch/e10_design/wave_rings/out/pl_%s.png' % f if not f.endswith('.png') else f).convert('RGB').crop((x0, y0, x1, y1))
    ims.append(im.resize((int((x1 - x0) * sc), int((y1 - y0) * sc)), Image.LANCZOS))
cols = min(len(ims), 2 if (x1 - x0) * sc > 700 else 4)
rows = (len(ims) + cols - 1) // cols
w, h = ims[0].size
sheet = Image.new('RGB', (cols * w + (cols + 1) * 6, rows * h + (rows + 1) * 6), (30, 30, 36))
for i, im in enumerate(ims):
    sheet.paste(im, (6 + (i % cols) * (w + 6), 6 + (i // cols) * (h + 6)))
sheet.save(out)
print(sheet.size)
