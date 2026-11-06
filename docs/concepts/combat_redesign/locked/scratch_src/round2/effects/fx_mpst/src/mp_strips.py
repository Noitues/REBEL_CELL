"""mp_strips.py [-j N] [skin ...]: run mp_run.py for every effect x skin of the spec (parallel, one process per job) -> logs/run_<id>_<skin>.log"""
import sys, os, subprocess, time
sys.dont_write_bytecode = True
ME = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/'
sys.path.insert(0, ME + 'src')
import mp_eff as E
a = sys.argv[1:]
j = 4
if a and a[0] == '-j':
    j = int(a[1]); a = a[2:]
skins = a or ['neutral', 'solace', 'meridian']
todo = [(fid, sk) for sk in skins for fid, s in E.FX.items() if sk in s['skins']]
run, t0 = [], time.time()
print('jobs', len(todo), flush=True)
while todo or run:
    while todo and len(run) < j:
        fid, sk = todo.pop(0)
        lf = open(ME + 'logs/run_%s_%s.log' % (fid, sk), 'w')
        p = subprocess.Popen([sys.executable, ME + 'src/mp_run.py', fid, sk], stdout=lf, stderr=subprocess.STDOUT, cwd=ME + 'src')
        run.append((p, fid, sk, lf))
        print('start', fid, sk, 'pid', p.pid, flush=True)
    time.sleep(2)
    for r in run[:]:
        if r[0].poll() is not None:
            r[3].close()
            print('done', r[1], r[2], 'exit', r[0].returncode, round(time.time() - t0), flush=True)
            run.remove(r)
print('all done', round(time.time() - t0), flush=True)
