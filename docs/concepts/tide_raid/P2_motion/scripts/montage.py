import sys
from PIL import Image
name, var = sys.argv[1], sys.argv[2]
fs = [int(x) for x in sys.argv[3:]]
FR = 'D:/rc_scratch/tide_concepts/p2m_work/frames/'
tw, th = 640, 360
cols = 3
rows = (len(fs) + cols - 1) // cols
im = Image.new('RGB', (tw * cols, th * rows))
for i, f in enumerate(fs):
    t = Image.open(FR + '%s_%s_%03d.png' % (name, var, f)).convert('RGB').resize((tw, th), Image.LANCZOS)
    im.paste(t, ((i % cols) * tw, (i // cols) * th))
im.save('D:/rc_scratch/tide_concepts/p2m_work/mont.png')
