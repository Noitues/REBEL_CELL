"""Quick test: render each frame (player + boss) at ss=1 into scratch/ for checking."""
import os
import sys
import time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
SCR = os.path.join(os.path.dirname(HERE), "scratch")
os.makedirs(SCR, exist_ok=True)
from PIL import Image
import frames as F
import combat_specs as CS

which = sys.argv[1:] or ["d1", "d2", "d3", "d4"]
ss = 1
P = CS.player(41, 14)[0]
B = CS.boss(340, 8)[0]
for fr in which:
    t = time.time()
    a, ca, _ = F.render(fr, P, ss=ss, hp_number=True)
    b, cb, _ = F.render(fr, B, ss=ss, hp_number=True)
    s, cs, _ = F.render(fr, P, ss=2, lod=True)
    s, cs = F.fit(s, cs, 2, 60)
    W = a.width + b.width + 200
    sheet = Image.new("RGBA", (W, max(a.height, b.height)), (24, 22, 30, 255))
    sheet.alpha_composite(a, (0, 0))
    sheet.alpha_composite(b, (a.width, 0))
    sheet.alpha_composite(s, (a.width + b.width + 20, 20))
    sheet.convert("RGB").save(os.path.join(SCR, "t_%s.png" % fr))
    print(fr, "%.1fs" % (time.time() - t), flush=True)
