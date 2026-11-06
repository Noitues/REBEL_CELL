import sys
from PIL import Image, ImageFilter
n = sys.argv[1]
im = Image.open('../frames/%s.png' % n).convert('RGB')
a = im.resize((640, 360), Image.LANCZOS)
b = im.filter(ImageFilter.GaussianBlur(4)).resize((640, 360), Image.LANCZOS)
c = Image.new('RGB', (1290, 360), (0, 0, 0))
c.paste(a, (0, 0)); c.paste(b, (650, 0))
c.save('D:/rc_scratch/tide_concepts/h_work/sq.png')
