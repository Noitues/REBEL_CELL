"""stack.py <out> <files...>: stack images vertically at 1x (for looking)"""
import sys
from PIL import Image
ims = [Image.open(f).convert('RGB') for f in sys.argv[2:]]
W = max(i.width for i in ims)
H = sum(i.height for i in ims)
c = Image.new('RGB', (W, H), (40, 40, 50))
y = 0
for i in ims:
    c.paste(i, (0, y))
    y += i.height
c.save(sys.argv[1])
print(c.size)
