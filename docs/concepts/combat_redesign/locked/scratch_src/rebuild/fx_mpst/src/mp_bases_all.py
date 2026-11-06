"""mp_bases_all.py [-j N] [group ...]: run mp_bases.py groups in parallel (one process per group, one skin per process)."""
import sys, os, subprocess, time
sys.dont_write_bytecode = True
ME = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/'
GROUPS = {
    'N1': ['neutral', 'p1_noguns', 'p1_empty', 'p1_hold', 'p1_after', 'p1_clean'],
    'N2': ['neutral', 'p2', 'p3', 'p3_pre', 'p3_mid'],
    'N3': ['neutral', 'p3_kill', 'p3_after', 'p3_clean'],
    'S1': ['solace', 'p1', 'p1_empty', 'p1_hold', 'p1_after'],
    'S2': ['solace', 'p1_clean', 'p2', 'p3'],
    'M1': ['meridian', 'p1', 'p1_empty', 'p1_hold', 'p1_after'],
    'M2': ['meridian', 'p1_clean', 'p2', 'p3'],
}
a = sys.argv[1:]
j = 3
if a and a[0] == '-j':
    j = int(a[1]); a = a[2:]
todo = a or list(GROUPS)
run, t0 = [], time.time()
while todo or run:
    while todo and len(run) < j:
        g = todo.pop(0)
        lf = open(ME + 'logs/bases_%s.log' % g, 'w')
        p = subprocess.Popen([sys.executable, ME + 'src/mp_bases.py'] + GROUPS[g], stdout=lf, stderr=subprocess.STDOUT)
        run.append((p, g, lf))
        print('start', g, 'pid', p.pid, flush=True)
    time.sleep(3)
    for r in run[:]:
        if r[0].poll() is not None:
            r[2].close()
            print('done', r[1], 'exit', r[0].returncode, round(time.time() - t0), flush=True)
            run.remove(r)
print('all done', round(time.time() - t0))
