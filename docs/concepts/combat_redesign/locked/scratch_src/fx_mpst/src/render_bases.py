"""render_bases.py <skin> <kind> [<kind> ...]
Base plates for the M/P/S/T effects, rendered with the shared locked generator (imported read-only from corp/src;
caches redirected to fx_mpst/work).  kinds:
  p2, p3          the stock beats (corp skins only need these; neutral ones are the published finals)
  p1_empty        decide board f1 with no units (ring material + schedule + HUD + hand): the background the unit layer slides over
  p1_noguns       neutral p1 without the gun preview marks (spin turns the tower; the guns re-solve after it)
  p1_hold         f1 with schedule [0,2,0]: the end state of Hold (a 0 put in the live cell, the +2 slides one slot later)
out: fx_mpst/work/base_<skin>_<kind>.png"""
import sys, os, copy, time, shutil, glob
sys.dont_write_bytecode = True
skin = sys.argv[1]
kinds = sys.argv[2:]
os.environ['CORP'] = skin
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
ME = 'D:/rc_scratch/combat_redesign/locked/fx_mpst/'
sys.path.insert(0, SRC)
os.chdir(SRC)
W = ME + 'work/cache_%s/' % skin
os.makedirs(W, exist_ok=True)
for fp in glob.glob('D:/rc_scratch/combat_redesign/locked/corp/work/tower_*.png'):
    dst = W + os.path.basename(fp)
    if not os.path.exists(dst):
        shutil.copy(fp, dst)
import lw_render as LW
from PIL import Image
R = LW.R
R.WORK = W
LW.FH.CACHE = W
A = R.A
for kind in kinds:
    t = time.time()
    out = ME + 'work/base_%s_%s.png' % (skin, kind)
    if kind in ('p1', 'p2', 'p3', 'p2b'):
        im = R.render(kind)
    elif kind == 'p1_empty':
        f = copy.deepcopy(A.J['f1'])
        f['units'] = []
        im = R.render('p1', frame=f, tag='f1empty')
    elif kind == 'p1_noguns':
        og = R.FG.make_guns
        R.FG.make_guns = lambda f, k, w: (Image.new('RGBA', (1920, 1080), (0, 0, 0, 0)), None)
        try:
            im = R.render('p1')
        finally:
            R.FG.make_guns = og
    elif kind == 'p1_hold':
        f = copy.deepcopy(A.J['f1'])
        f['schedule'] = [0, 2, 0]
        im = R.render('p1', frame=f, tag='f1hold')
    else:
        raise SystemExit('unknown kind ' + kind)
    im.save(out)
    print('ok', skin, kind, round(time.time() - t, 1), flush=True)
