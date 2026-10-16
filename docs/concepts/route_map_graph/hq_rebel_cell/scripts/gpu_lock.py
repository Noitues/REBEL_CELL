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
ME = "hq_rev_rebel_cell"                                   # v3: the Rebel Cell netrun agent (hq_others in the queue)
EARLIER = ("storyboard", "halcyon", "hq_halcyon", "new_corps")   # queue order + the designer's new_corps override


LATER = ("city_all_corps",)


def _earlier_waiting():
    out = [n for n in EARLIER if os.path.exists(os.path.join(Q, "GPU_WAITING_" + n))]
    # v3: peers in the same queue slot (other HQ agents) that have been waiting longer than this agent go first
    mine = os.path.join(Q, "GPU_WAITING_" + ME)
    t_me = os.path.getmtime(mine) if os.path.exists(mine) else time.time()
    if time.time() - t_me > 600:
        return out              # after 10 min of waiting, an idle peer that never takes the free lock no longer blocks
    for f in os.listdir(Q):
        if f.startswith("GPU_WAITING_") and f != "GPU_WAITING_" + ME and f[12:] not in LATER + EARLIER:
            try:
                tf = os.path.getmtime(os.path.join(Q, f))
                if tf < t_me and time.time() - tf < 3 * 3600:          # (a 3 h old waiting file is stale)
                    out.append(f[12:])
            except OSError:
                pass
    return out


def acquire(what="", poll=30, log=print):
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
