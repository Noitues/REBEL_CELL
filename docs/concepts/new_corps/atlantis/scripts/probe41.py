"""Debug: print a round 41 boss spec and render the stock Meridian boss once (scratch only, read-only use of round41)."""
import os
import pprint
import sys
sys.dont_write_bytecode = True
R41 = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\round41_wheel_stack\scripts"
sys.path.insert(0, R41)
os.chdir(R41)
import roster as RS
p1, p2, m = RS.boss_specs("meridian")
pprint.pprint(p1, width=160)
pprint.pprint(m, width=160)
import d4corp
im, c, meta = d4corp.render(p1, ss=1)
im.save(r"D:\rc_scratch\new_corps\probe41.png")
print(im.size, c, meta)
