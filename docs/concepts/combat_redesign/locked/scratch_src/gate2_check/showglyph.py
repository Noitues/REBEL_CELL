"""showglyph.py <rgba.png> <out.png> -- composite an RGBA glyph over dark navy for viewing."""
import sys
from PIL import Image

g = Image.open(sys.argv[1]).convert('RGBA')
bg = Image.new('RGBA', g.size, (12, 16, 30, 255))
bg.alpha_composite(g)
bg.convert('RGB').resize((g.width // 2, g.height // 2)).save(sys.argv[2])
print(g.size)
