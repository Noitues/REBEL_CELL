"""render_set.py [-j N] job ...   job = beat[:corp]  e.g. p1 p2 p2b p3 nowords p1:solace p2b:meridian
Runs corp/src/asm_render.py <beat> bio 1 with CORP=<corp> in parallel; logs to final_work/logs/."""
import sys, os, subprocess, time
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src'
LOG = 'D:/rc_scratch/combat_redesign/locked/final_work/logs/'
os.makedirs(LOG, exist_ok=True)
args = sys.argv[1:]
j = 4
if args and args[0] == '-j':
    j = int(args[1]); args = args[2:]
jobs = [a.split(':') + ['neutral'] for a in args]
run = []
t0 = time.time()
while jobs or run:
    while jobs and len(run) < j:
        beat, corp = jobs.pop(0)[:2]
        env = dict(os.environ, CORP=corp)
        lf = open(LOG + '%s_%s.log' % (beat, corp), 'w')
        p = subprocess.Popen([sys.executable, 'asm_render.py', beat, 'bio', '1'], cwd=SRC, env=env, stdout=lf, stderr=subprocess.STDOUT)
        run.append((p, beat, corp, lf))
    time.sleep(2)
    for r in run[:]:
        if r[0].poll() is not None:
            r[3].close()
            print(r[1], r[2], 'exit', r[0].returncode, round(time.time() - t0), open(LOG + '%s_%s.log' % (r[1], r[2])).read().strip().splitlines()[-1:], flush=True)
            run.remove(r)
