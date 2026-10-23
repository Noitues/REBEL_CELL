import sys, colorsys
sys.path.insert(0, ".")
import numpy as np
KINDS = {"fight": (108, 247, 255), "elite": (255, 140, 26), "event": (78, 255, 158), "shop": (98, 169, 255), "rack": (255, 160, 42),
         "rest": (191, 115, 255), "workshop": (255, 209, 77),
         "r_router": (56, 158, 255), "r_terminal": (77, 242, 128), "r_mainframe": (102, 115, 255), "r_rack": (255, 148, 51), "r_elite": (255, 89, 31)}
# also the state ring colours and walked lime
KINDS.update({"ring_walked": (212, 255, 0), "ring_next": (255, 140, 26), "ring_unavail": (242, 246, 255), "pink": (255, 61, 168)})
vis = ("normal","protan","deutan","tritan")
from metrics import de
res = {}
for r in range(40, 256, 10):
    for g in range(0, 256, 10):
        for b in range(0, 256, 10):
            c = (r, g, b)
            mx = max(c); mn = min(c)
            if (mx - mn) < 70: continue
            worst = {v: min(de(c, k, v) for k in KINDS.values()) for v in vis}
            m = min(worst.values())
            if m < 30: continue
            h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
            key = int(h * 12)
            res.setdefault(key, []).append((m, c, worst))
for k in sorted(res):
    res[k].sort(key=lambda t: -t[0])
    print("hue bucket", k*30, len(res[k]))
    for m, c, w in res[k][:3]:
        print("   ", c, "%.0f" % m, {a: round(b_) for a, b_ in w.items()})
