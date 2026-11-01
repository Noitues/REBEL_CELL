import sys
from PIL import Image
b = Image.open(sys.argv[1]).convert("RGB"); a = Image.open(sys.argv[2]).convert("RGB")
box = (700, 380, 1240, 720)
cb, ca = b.crop(box), a.crop(box)
w, h = cb.size
out = Image.new("RGB", (w * 2 * 2 + 10, h * 2), (20, 20, 20))
out.paste(cb.resize((w * 2, h * 2), Image.LANCZOS), (0, 0)); out.paste(ca.resize((w * 2, h * 2), Image.LANCZOS), (w * 2 + 10, 0))
out.save(sys.argv[3])
