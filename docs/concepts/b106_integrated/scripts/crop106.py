"""Side by side crop of the B-106 map with 3D marks and with the 2D overlays (scratch). Args: dir tag out."""
import sys
from PIL import Image
d, tag, out = sys.argv[1:4]
a = Image.open("%s/%s_3d.png" % (d, tag)).convert("RGB").crop((450, 50, 1920, 1000))
b = Image.open("%s/%s_2d.png" % (d, tag)).convert("RGB").crop((450, 50, 1920, 1000))
w = Image.new("RGB", (a.width, a.height * 2))
w.paste(a, (0, 0)); w.paste(b, (0, a.height))
w.resize((a.width * 2 // 3, a.height * 4 // 3)).save(out, quality=88)
