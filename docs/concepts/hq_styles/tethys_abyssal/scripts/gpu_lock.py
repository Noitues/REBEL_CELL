"""The shared GPU queue (D:/rc_scratch/GPU_QUEUE.md): one Cycles job at a time on the RX 6700 XT.

Order: storyboard -> halcyon -> hq_others -> new_corps. acquire() waits (polling) until no GPU_LOCK exists and no
earlier-ordered agent has a GPU_WAITING_<name> file, keeping GPU_WAITING_hq_others while it waits; then creates the
lock atomically (O_EXCL) with the name + time, and deletes the waiting file. release() deletes the lock (ours only).
A batch holds the lock for at most ~45 min (the caller splits its renders). Never removes another agent's lock.
"""
import os
import time

Q = r"D:\rc_scratch"
LOCK = os.path.join(Q, "GPU_LOCK")
ME = "art_abyssal"
import glob


def _earlier_waiting():
    """other agents whose waiting file is older than ours (first come, first served; newer waiters go after us)."""
    wf = os.path.join(Q, "GPU_WAITING_" + ME)
    mine = os.path.getmtime(wf) if os.path.exists(wf) else time.time()
    return [os.path.basename(p)[12:] for p in glob.glob(os.path.join(Q, "GPU_WAITING_*"))
            if os.path.basename(p)[12:] != ME and os.path.getmtime(p) <= mine]


def acquire(what="", poll=150, log=print):
    wf = os.path.join(Q, "GPU_WAITING_" + ME)
    t0 = time.time()
    while True:
        if not os.path.exists(LOCK) and not _earlier_waiting():
            try:
                fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, ("%s %s %s\n" % (ME, time.strftime("%Y-%m-%d %H:%M:%S"), what)).encode())
                os.close(fd)
                if os.path.exists(wf):
                    os.remove(wf)
                log("GPU lock acquired after %.0f s (%s)" % (time.time() - t0, what))
                return True
            except FileExistsError:
                pass
        if not os.path.exists(wf):
            with open(wf, "w") as f:
                f.write("%s %s waiting for %s\n" % (ME, time.strftime("%Y-%m-%d %H:%M:%S"), what))
        time.sleep(poll)


def release(log=print):
    if os.path.exists(LOCK) and open(LOCK, errors="replace").read().startswith(ME):
        os.remove(LOCK)
        log("GPU lock released")


def holder():
    return open(LOCK, errors="replace").read().strip() if os.path.exists(LOCK) else None
