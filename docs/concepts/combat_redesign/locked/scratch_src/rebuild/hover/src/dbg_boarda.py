"""dbg_boarda.py <name> : board-only check a with R only vs R + Z board classes (no hover marks): rows of ring 0"""
import sys
sys.dont_write_bytecode = True
import hv_checks as HC
RC, T = HC.RC, HC.T
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
HOVER = ('hover', 'ghost', 'inset', 'plan', 'hand', 'send', 'undo')
for label, pres in (('R', ('R',)), ('R+Z', ('R', 'Z'))):
    Mb = {}
    for k, v in M.items():
        pre, _, nm = k.partition('__')
        if pre in pres and nm not in HOVER:
            Mb[nm] = (Mb[nm] | v) if nm in Mb else v
    rb = RC.check_cells(T.lum(bg), bg, dict(geometry=rep['geometry']), Mb, T.lum(probe) if probe is not None else None)
    print(label, 'pass', rb['pass_'], [(r['ring'], r['sector'], r['state'], r['ratio'], r['px']) for r in rb['rows'] if r['gated'] and r['ring'] == 0])
