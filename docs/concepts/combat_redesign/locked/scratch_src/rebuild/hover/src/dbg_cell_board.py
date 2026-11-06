"""dbg_cell_board.py <name> : the board's own check_cells (rb_checks, read only) on the board image under a hover plate, with the board's masks only
(R__ capture classes), next to the hover plate's rows"""
import sys, json
sys.dont_write_bytecode = True
import numpy as np
import hv_checks as HC
RC, T = HC.RC, HC.T

name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
Mb = {}
for k, v in M.items():
    pre, _, nm = k.partition('__')
    if pre == 'R':
        Mb[nm] = (Mb[nm] | v) if nm in Mb else v
probeY = T.lum(probe) if probe is not None else None
rb = RC.check_cells(T.lum(bg), bg, dict(geometry=rep['geometry']), Mb, probeY)
hv = json.load(open(HC.HERE + 'chk/%s.checks.json' % name))['a_cell_contrast']
hrows = {(r['ring'], r['sector']): r for r in hv['rows']}
print('board pass', rb.get('pass_'))
for r in rb['rows']:
    h = hrows.get((r['ring'], r['sector']), {})
    print('r%d s%d %-8s %-7s board occ %5.1f ref %5.1f ratio %5.2f px %5d | hover %-7s occ %5s ratio %5s px %s' % (
        r['ring'], r['sector'], r['kind'], r['state'], r['occ_L'], r['empty_L'], r['ratio'], r['px'],
        h.get('state'), h.get('occ_L'), h.get('ratio'), h.get('px')))
