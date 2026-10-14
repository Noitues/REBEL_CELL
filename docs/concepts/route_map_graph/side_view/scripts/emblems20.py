"""Export the round 6 class + corp emblems (slicelib EM_*) as alpha PNGs into ../scratch/emblems (read-only use of round6)."""
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\round6_roster\scripts")
import slicelib as S
from PIL import Image
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scratch", "emblems")
os.makedirs(out, exist_ok=True)
names = ["BREAKER","WRECKER","GHOST","PHANTOM","RIGGER","OVERCLOCKER","BOTNET","HIVEMIND","MERIDIAN","SOLACE","HALCYON","ORBITAL","REBEL_CELL"]
row = Image.new("L", (128*len(names), 128))
for i, n in enumerate(names):
    m = S.glyph_mask("EM_" + n)
    im = Image.new("RGBA", m.size, (255,255,255,0)); im.putalpha(m)
    im.save(os.path.join(out, n.lower() + ".png"))
    row.paste(m.resize((128,128)), (i*128, 0))
row.save(os.path.join(out, "_row.png"))
print("ok")
