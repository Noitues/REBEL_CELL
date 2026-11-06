"""run corp/src dot_audit.audit on PNGs and print the runs.  python dot_probe.py <png> [<png> ...]"""
import sys
from PIL import Image
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import dot_audit as DA

for p in sys.argv[1:]:
    r = DA.audit(Image.open(p))
    print(p, 'runs', r['n_runs'])
    for x in r['runs']:
        print('   n %d spacing %.2f bbox %s' % (x['n'], x['spacing'], x['bbox']))
