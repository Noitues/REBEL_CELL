#!/usr/bin/env python3
"""Path guard for the `balance` branch (docs/handoff/plan2/BALANCE_SIM.md S4).

Commits on branch `balance` may touch only data and the balance tooling:
    content/   docs/balance/   tools/balance/
Anything else fails. On any other branch the guard passes.

  python tools/balance/path_guard.py --branch balance path1 path2 ...
  git diff --name-only --cached | python tools/balance/path_guard.py --branch "$(git rev-parse --abbrev-ref HEAD)"

Exit 0 = allowed, 1 = a path outside the allowed folders (they are listed).
"""
import argparse
import sys

BRANCH = "balance"
ALLOWED = ("content/", "docs/balance/", "tools/balance/")


def violations(branch, paths):
    """Paths a commit on `branch` may not touch (empty for any branch but `balance`)."""
    if branch != BRANCH:
        return []
    bad = []
    for p in paths:
        p = p.strip().replace("\\", "/")
        if p and not p.startswith(ALLOWED):
            bad.append(p)
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--branch", required=True)
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args()
    paths = args.paths or sys.stdin.read().split("\n")
    bad = violations(args.branch, paths)
    if bad:
        print("balance path guard: branch '%s' may only change content/, docs/balance/ and tools/balance/; not allowed:" % args.branch, file=sys.stderr)
        for p in bad:
            print("  " + p, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
