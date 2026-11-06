"""Runs a command while holding the shared GPU lock (D:/rc_scratch/GPU_LOCK) as agent 'tide_g1'. Usage: python gpu_lock_run.py "<what>" -- <cmd...>
Written as a file (never python from stdin). Releases the lock when the command ends, also on error."""
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, r"D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts")
import gpu_lock  # noqa: E402

gpu_lock.ME = "tide_g1"


def main() -> int:
    i = sys.argv.index("--")
    what = sys.argv[1]
    cmd = sys.argv[i + 1:]
    gpu_lock.acquire(what, poll=20)
    try:
        return subprocess.call(cmd)
    finally:
        gpu_lock.release()


if __name__ == "__main__":
    sys.exit(main())
