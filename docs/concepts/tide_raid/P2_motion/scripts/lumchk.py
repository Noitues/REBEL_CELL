import numpy as np
from PIL import Image
FR = 'D:/rc_scratch/tide_concepts/p2m_work/frames/'
for f in (0, 30, 35, 40, 50, 60, 64, 70, 100, 120):
    a = np.asarray(Image.open(FR + 'home_normal_%03d.png' % f), np.float32)
    print(f, round(float(a.mean()), 1))
