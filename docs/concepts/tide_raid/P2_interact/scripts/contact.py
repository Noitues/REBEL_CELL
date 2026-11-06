"""contact sheet: python contact.py out.jpg cols scale file1 file2 ..."""
import sys
from PIL import Image
out, cols, sc = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
fs = sys.argv[4:]
ims = [Image.open(f).convert('RGB') for f in fs]
w, h = int(1920 * sc), int(1080 * sc)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * h), (8, 6, 20))
for i, im in enumerate(ims):
    sheet.paste(im.resize((w, h), Image.LANCZOS), ((i % cols) * w, (i // cols) * h))
sheet.save(out, quality=90)
