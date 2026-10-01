"""Quick look: every program tile at one time t, plus a Meridian tile (scratch output)."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from circ_lib import *  # noqa

SCR = r"C:\Users\noitu\AppData\Local\Temp\claude\C--Users-noitu-Documents-Godot-rebel-cell\2fda7edc-043a-4f51-a33f-a1ec952ac703\scratchpad\circ"
os.makedirs(SCR, exist_ok=True)
t = float(sys.argv[1]) if len(sys.argv) > 1 else 0.5
imgs = []
for n in ORDER:
    t0 = time.time()
    b = make_board(n)
    im = render_tile(b, t)
    imgs.append(im.resize((im.width // 2, im.height // 2), Image.LANCZOS))
    print(n, im.size, round(time.time() - t0, 2), flush=True)
b = make_corp_board("EXPLOIT")
im = render_tile(b, t)
imgs.append(im.resize((im.width // 2, im.height // 2), Image.LANCZOS))
sheet = Image.new("RGB", (5 * 240, 2 * 250), (20, 20, 26))
for i, im in enumerate(imgs):
    sheet.paste(im, ((i % 5) * 240, (i // 5) * 250), im)
sheet.save(os.path.join(SCR, f"test_{t}.png"))
