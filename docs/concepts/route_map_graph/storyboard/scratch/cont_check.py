import os, sys
import numpy as np
from PIL import Image
FR = "D:/rc_scratch/storyboard/full_frames"
prev = None
d = []
for f in range(614):
    im = np.asarray(Image.open(os.path.join(FR, "f_%04d.png" % f)).convert("L").resize((320, 180)), np.float32) / 255
    if prev is not None:
        d.append((float(np.abs(im - prev).mean()), f))
    prev = im
v = np.array([x for x, _ in d])
med = float(np.median(v))
print("median diff %.4f" % med)
for x, f in sorted(d, reverse=True)[:14]:
    print("f %d t %.2f diff %.4f" % (f, f / 24, x))
# contact strip every 24 frames
th = [Image.open(os.path.join(FR, "f_%04d.png" % f)).convert("RGB").resize((320, 180)) for f in range(0, 614, 24)]
cols = 6
sheet = Image.new("RGB", (320 * cols, 180 * ((len(th) + cols - 1) // cols)))
for k, im in enumerate(th):
    sheet.paste(im, (320 * (k % cols), 180 * (k // cols)))
sheet.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), "contact.jpg"), quality=80)
