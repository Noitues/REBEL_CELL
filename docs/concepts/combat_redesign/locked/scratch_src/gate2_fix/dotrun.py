"""dotrun.py <png> ...: dot_audit runs per plate (the unchanged O-30 detector)"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
from PIL import Image
import dot_audit as DA
for f in sys.argv[1:]:
    r = DA.audit(Image.open(f))
    print(f.split('/')[-1], r['n_runs'], [(x['n'], x['spacing'], x['colour'], x['bbox']) for x in r['runs']])
