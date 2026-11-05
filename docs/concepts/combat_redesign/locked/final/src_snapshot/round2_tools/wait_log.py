"""wait_log (round 2): block until a log file has N lines containing a marker, or a time limit passes.
python wait_log.py <log> <marker> <n> <max_seconds>"""
import sys, time, os
sys.dont_write_bytecode = True
log, marker, n, lim = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
t0 = time.time()
seen = 0
while time.time() - t0 < lim:
    k = 0
    if os.path.exists(log):
        with open(log, errors='replace') as f:
            lines = [x.rstrip() for x in f if marker in x]
        k = len(lines)
        for x in lines[seen:]:
            print(x, flush=True)
        seen = k
    if k >= n:
        print('reached', k, round(time.time() - t0), flush=True)
        raise SystemExit(0)
    time.sleep(5)
print('timeout at', seen, flush=True)
raise SystemExit(1)
