import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_run as R, wr_extra as X
R.run(None, force=True)
X.run(None)
open(R.OUT + 'ALL_DONE.txt', 'w').write('done')
