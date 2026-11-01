import glob, sys
import numpy as np
from PIL import Image
boxes = {"TEA": (1085, 750, 1180, 792), "PHA": (1190, 750, 1230, 792), "HOTEL": (655, 748, 735, 792), "NOODLE": (315, 745, 370, 790), "SPOREBAR": (265, 630, 355, 665), "LEAFLET": (470, 745, 540, 792), "KARAOKE": (1138, 550, 1160, 650), "TEAv": (1437, 365, 1456, 458), "DATA": (1550, 748, 1612, 792), "BAR": (1620, 748, 1672, 792)}
files = sorted(glob.glob(sys.argv[1] + "/gif_*.png"))
rows = {k: [] for k in boxes}
for f in files:
    a = np.asarray(Image.open(f).convert("L")).astype(np.float32)
    for k, (x0, y0, x1, y1) in boxes.items():
        rows[k].append(a[y0:y1, x0:x1].mean())
for k, v in rows.items():
    v = np.array(v)
    print("%-9s min %.1f max %.1f  ratio %.2f  " % (k, v.min(), v.max(), v.min() / v.max()), " ".join("%d" % x for x in v[:48:2]))
