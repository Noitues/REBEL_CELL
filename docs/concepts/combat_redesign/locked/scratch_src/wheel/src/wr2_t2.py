import sys, time, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr2_sets as S
from wr2_lib import lab
t = time.time()
b, s = S.search(seed=5, n=1500)
print(round(s, 1), b, {k: round(float(lab(v)[0]), 1) for k, v in b.items()}, round(time.time() - t))
json.dump({k: list(v) for k, v in b.items()}, open('D:/rc_scratch/e10_design/wave_rings/out2/kind_table_R.json', 'w'))
