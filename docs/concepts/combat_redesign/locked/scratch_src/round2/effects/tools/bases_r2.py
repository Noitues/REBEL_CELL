"""bases_r2.py [-j N] [job ...]: every effects base plate on the round-2 board (corp/src read-only, rb4_patch installed by lw_render),
one process per job.  Jobs: C:<skin>:<var,...> (fx_cdhl base_render.py) and M:<skin>:<kind,...> (fx_mpst mp_bases.py)."""
import sys, os, subprocess, time
sys.dont_write_bytecode = True
R2 = 'D:/rc_scratch/combat_redesign/locked/round2/effects/'
# one beat (p1 / p2 / p3 family) per process (the asm hooks are installed once per process).  The stock p1 / p3 plates are rendered once
# (C:neutral:p1, C:neutral:p3 and M:<corp>:p3) and copied to the other set's names by share_bases.py.
JOBS = [
    'C:neutral:p1', 'C:neutral:p3', 'M:neutral:p2', 'M:solace:p3', 'M:meridian:p3', 'M:solace:p2',
    'M:meridian:p2', 'C:neutral:p3alt,p3grow', 'C:neutral:p3kill',
    'M:neutral:p3_pre,p3_mid', 'M:neutral:p3_kill,p3_after', 'M:neutral:p3_clean',
    'M:neutral:p1_noguns,p1_empty', 'M:neutral:p1_hold,p1_after', 'M:neutral:p1_clean',
    'C:solace:p3alt,p3grow', 'C:solace:p3kill', 'C:meridian:p3alt,p3grow', 'C:meridian:p3kill',
    'M:solace:p1,p1_empty', 'M:solace:p1_hold,p1_after', 'M:solace:p1_clean',
    'M:meridian:p1,p1_empty', 'M:meridian:p1_hold,p1_after', 'M:meridian:p1_clean',
]
a = sys.argv[1:]
j = 6
if a and a[0] == '-j':
    j = int(a[1]); a = a[2:]
todo = a or list(JOBS)
os.makedirs(R2 + 'logs', exist_ok=True)
run, t0 = [], time.time()
while todo or run:
    while todo and len(run) < j:
        job = todo.pop(0)
        kind, skin, vs = job.split(':')
        if kind == 'C':
            cmd = [sys.executable, R2 + 'fx_cdhl/src/base_render.py', skin] + vs.split(',')
        else:
            cmd = [sys.executable, R2 + 'fx_mpst/src/mp_bases.py', skin] + vs.split(',')
        lf = open(R2 + 'logs/base_%s.log' % job.replace(':', '_').replace(',', '-'), 'w')
        p = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT)
        run.append((p, job, lf))
        print('start', job, 'pid', p.pid, flush=True)
    time.sleep(3)
    for r in run[:]:
        if r[0].poll() is not None:
            r[2].close()
            print('done', r[1], 'exit', r[0].returncode, round(time.time() - t0), flush=True)
            run.remove(r)
print('all done', round(time.time() - t0), flush=True)
