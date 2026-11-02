"""hz_set.py [-j N] job ...   job = hNN[:nw][@corp]   e.g. h01 h02:nw h02@solace     (or 'all' = the published set of 26)
Runs hz_run.py (from corp/src, the one generator) in parallel, one process per job; logs to locked/hover/logs/."""
import sys, os, subprocess, time
SRC = os.path.dirname(os.path.abspath(__file__))
LOG = 'D:/rc_scratch/combat_redesign/locked/hover/logs/'
os.makedirs(LOG, exist_ok=True)
args = sys.argv[1:]
j = 4
if args and args[0] == '-j':
    j = int(args[1]); args = args[2:]
if args == ['all']:
    ids = ['h%02d' % i for i in range(1, 12)]
    args = ids + [i + ':nw' for i in ids] + ['h02@solace', 'h02@meridian', 'h04@solace', 'h04@meridian']
jobs = []
for a in args:
    job, _, corp = a.partition('@')
    jobs.append((job, corp or 'neutral'))
run = []
t0 = time.time()
while jobs or run:
    while jobs and len(run) < j:
        job, corp = jobs.pop(0)
        env = dict(os.environ, CORP=corp)
        lfn = LOG + '%s_%s.log' % (job.replace(':', '_'), corp)
        lf = open(lfn, 'w')
        p = subprocess.Popen([sys.executable, 'hz_run.py', job], cwd=SRC, env=env, stdout=lf, stderr=subprocess.STDOUT)
        run.append((p, job, corp, lf, lfn))
    time.sleep(2)
    for r in run[:]:
        if r[0].poll() is not None:
            r[3].close()
            tail = open(r[4]).read().strip().splitlines()[-1:]
            print(r[1], r[2], 'exit', r[0].returncode, round(time.time() - t0), tail, flush=True)
            run.remove(r)
