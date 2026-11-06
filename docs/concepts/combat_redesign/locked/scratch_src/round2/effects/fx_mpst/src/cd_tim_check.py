"""cd_tim_check.py: the C/D/H/L totals the beat uses (the read-only snapshot's CD.FX) against their published timings_CDHL.json"""
import sys, json
sys.dont_write_bytecode = True
from mp_lib import ME, OUTD
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/src')
import fx_cdhl as CD
pub = json.load(open(OUTD + 'timings_CDHL.json'))
eff = pub.get('effects', pub)
bad = 0
for f in CD.FX:
    p = eff.get(f['id'])
    pt = None
    if isinstance(p, dict):
        pt = p.get('total_ms', p.get('total'))
    ok = pt == f['timing']['total']
    bad += not ok
    print('%-22s snapshot %4d  published %s  %s' % (f['id'], f['timing']['total'], pt, 'ok' if ok else 'DIFF'))
print('diffs', bad)
