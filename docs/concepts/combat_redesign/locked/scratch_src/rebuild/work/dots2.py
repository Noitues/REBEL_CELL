"""dots2.py <png> ...: run corp/src dot_audit on plates and print the runs"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
from PIL import Image
import dot_audit as DA
for p in sys.argv[1:]:
    r = DA.audit(Image.open(p))
    print(p.split('/')[-1], 'runs', r['n_runs'], [(x['n'], x['spacing'], x['bbox']) for x in r['runs']])
