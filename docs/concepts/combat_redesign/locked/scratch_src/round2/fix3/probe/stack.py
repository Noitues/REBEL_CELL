"""stack.py out.png in1.png in2.png ...: stack images vertically with a 4 px gap"""
import sys
from PIL import Image
ims = [Image.open(p).convert('RGB') for p in sys.argv[2:]]
w = max(i.width for i in ims); h = sum(i.height for i in ims) + 4 * (len(ims) - 1)
o = Image.new('RGB', (w, h), (255, 0, 255)); y = 0
for i in ims:
    o.paste(i, (0, y)); y += i.height + 4
o.save(sys.argv[1]); print(sys.argv[1], o.size)
