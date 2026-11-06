"""bd_verify.py <params.json> <room> : render the real p1 plate through the corp/src generator (neutral) with
r2_ground.grade swapped for bd_grade.grade(room params); compare with the published composite p1_<room>.png."""
import sys, os, json, time
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
sys.path.insert(0, SRC)
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
PJ = json.load(open(sys.argv[1]))
room = sys.argv[2]
os.chdir(SRC)
os.environ['CORP'] = 'neutral'
import numpy as np
from PIL import Image
import lw_render as LW
import bd_grade as BG
HERE = 'D:/rc_scratch/combat_redesign/locked/backdrop/'
WK = HERE + 'work/cache_neutral/'
R = LW.R
R.WORK = WK
LW.FH.CACHE = WK
G2 = R.A.G2
V31 = 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/v3_1/'
G2.grade = lambda opt='P': BG.grade(G2.bare(), PJ[room])
t = time.time()
im = R.render('p1', room=V31 + 'room_%s_bare.png' % room)
im.save(HERE + 'work/verify_%s.png' % room)
pub = np.asarray(Image.open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/p1_%s.png' % room), np.float32)
e = np.abs(np.asarray(im, np.float32) - pub)
print(json.dumps(dict(room=room, mean_abs=float(e.mean()), p999=float(np.percentile(e, 99.9)), max=float(e.max()), secs=round(time.time() - t))))
