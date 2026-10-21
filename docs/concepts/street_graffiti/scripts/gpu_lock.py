"""The shared GPU queue (D:/rc_scratch/GPU_QUEUE.md): one Cycles job at a time on the RX 6700 XT.

street_graffiti queues LAST and never blocks anyone: it writes no GPU_WAITING file, and takes the lock (atomically, O_EXCL)
only when no lock exists and no other agent is waiting. (Writing a waiting file while every agent defers to every waiting
file could deadlock the queue.) release() deletes the lock only if it is ours. Never removes another agent's lock.
"""
import glob
import os
import time

Q = r"D:\rc_scratch"
LOCK = os.path.join(Q, "GPU_LOCK")
ME = "street_graffiti"


def _waiting():
    return [os.path.basename(p)[12:] for p in glob.glob(os.path.join(Q, "GPU_WAITING_*")) if os.path.basename(p)[12:] != ME]


def acquire(what="", poll=150, log=print):
    t0 = time.time()
    while True:
        if not os.path.exists(LOCK) and not _waiting():
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, ("%s %s %s\n" % (ME, time.strftime("%Y-%m-%d %H:%M:%S"), what)).encode())
                os.close(fd)
                log("GPU lock acquired after %.0f s (%s)" % (time.time() - t0, what))
                return True
            except FileExistsError:
                pass
        time.sleep(poll)


def release(log=print):
    if os.path.exists(LOCK) and open(LOCK, errors="replace").read().startswith(ME):
        os.remove(LOCK)
        log("GPU lock released")


def holder():
    return open(LOCK, errors="replace").read().strip() if os.path.exists(LOCK) else None
