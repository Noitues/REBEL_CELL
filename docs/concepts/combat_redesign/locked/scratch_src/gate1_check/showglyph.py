import sys
from PIL import Image
src = Image.open(sys.argv[1]).convert('RGBA')
print(src.size)
bg = Image.new('RGBA', src.size, (40, 40, 60, 255)); bg.alpha_composite(src)
bg = bg.resize((src.width * 3, src.height * 3), Image.NEAREST); bg.convert('RGB').save(sys.argv[2])
