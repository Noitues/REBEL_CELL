"""python hv_set.py [-j N] [job ...]   render the hover set in N parallel worker processes (default 4).
A job is <pid>[:nw][@corp]; with no jobs, the whole set: h01-h11 and their nowords, h02 and h04 in Solace and Meridian (26 plates).
Each worker runs hv_run.py on its share with CORP set; logs go to round2/hover/logs/set_<k>.log.  Exits non-zero when a plate fails."""
import sys, os, subprocess, time
sys.dont_write_bytecode = True

SRC = os.path.dirname(os.path.abspath(__file__))
LOGS = os.path.join(SRC, '..', 'logs')
os.makedirs(LOGS, exist_ok=True)
EST = {'h01': 260, 'h02': 170, 'h03': 150, 'h04': 170, 'h05': 140, 'h06': 220, 'h07': 140, 'h08': 140, 'h09': 140, 'h10': 150, 'h11': 160}


def full_set():
    jobs = []
    for i in range(1, 12):
        pid = 'h%02d' % i
        jobs += [pid + '@neutral', pid + ':nw@neutral']
    for corp in ('solace', 'meridian'):
        jobs += ['h02@' + corp, 'h04@' + corp]
    return jobs


def main(argv):
    n = 4
    if argv[:1] == ['-j']:
        n = int(argv[1])
        argv = argv[2:]
    jobs = [j if '@' in j else j + '@neutral' for j in argv] or full_set()
    jobs.sort(key=lambda j: -EST.get(j[:3], 150))
    shards = [[] for _ in range(n)]
    load = [0] * n
    for j in jobs:
        k = load.index(min(load))
        shards[k].append(j)
        load[k] += EST.get(j[:3], 150)
    procs = []
    t0 = time.time()
    for k, sh in enumerate(shards):
        if not sh:
            continue
        # one hv_run.py call per skin in the shard (CORP is read at import)
        by = {}
        for j in sh:
            job, _, corp = j.partition('@')
            by.setdefault(corp, []).append(job)
        cmds = [(corp, ['python', os.path.join(SRC, 'hv_run.py')] + js) for corp, js in sorted(by.items())]
        log = open(os.path.join(LOGS, 'set_%d.log' % k), 'w')
        procs.append((k, cmds, log))
    running = []
    for k, cmds, log in procs:
        running.append([k, cmds, log, None])
    fails = 0
    while running:
        for r in list(running):
            k, cmds, log, p = r
            if p is None or p.poll() is not None:
                if p is not None and p.returncode != 0:
                    fails += 1
                if not cmds:
                    log.close()
                    running.remove(r)
                    continue
                corp, cmd = cmds.pop(0)
                env = dict(os.environ, CORP=corp)
                log.write('### CORP=%s %s\n' % (corp, ' '.join(cmd[2:])))
                log.flush()
                r[3] = subprocess.Popen(cmd, cwd=SRC, env=env, stdout=log, stderr=subprocess.STDOUT)
        time.sleep(2)
    ok = fail = 0
    for k in range(n):
        fp = os.path.join(LOGS, 'set_%d.log' % k)
        if not os.path.exists(fp):
            continue
        for line in open(fp, encoding='utf-8', errors='replace'):
            if line.startswith('ok '):
                ok += 1
                print(line.rstrip()[:220])
            elif line.startswith('FAIL'):
                fail += 1
                print(line.rstrip())
    print('set done in %.0f s: %d ok, %d failed' % (time.time() - t0, ok, fail))
    return 1 if (fail or fails) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
