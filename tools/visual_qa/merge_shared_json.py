"""Three-way merge for the art pass's shared JSON files during a git merge conflict.

Run from the repo root while a merge is stopped on conflicts in either file:
    python tools/visual_qa/merge_shared_json.py

- tests/test_manifest.json: the union of both sides' test entries (ours wins on a duplicate).
- tools/visual_qa/lint_baseline.json: per file and rule, the lower count of the two sides.
  An entry one side removed was fixed there (counts as 0); an entry only one side added
  (not in the merge base) is kept as added.
Each resolved file is written and staged.
"""
import json
import subprocess
import sys


def stage(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    return json.loads(r.stdout.decode("utf-8")) if r.returncode == 0 else None


def conflicted():
    r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, check=True)
    return set(r.stdout.decode("utf-8").split())


def find_map(d):
    """The dict of path -> entry inside the file (the manifest and baseline nest one level)."""
    for k, v in d.items():
        if isinstance(v, dict) and all(isinstance(x, dict) for x in v.values()):
            return k
    return None


def merge_manifest(base, ours, theirs):
    key = find_map(ours)
    out = dict(ours)
    merged = dict(theirs[key])
    merged.update(ours[key])
    out[key] = dict(sorted(merged.items()))
    return out


def merge_lint(base, ours, theirs):
    key = find_map(ours)
    b, o, t = base.get(key, {}), ours[key], theirs[key]
    out_map = {}
    for f in sorted(set(o) | set(t)):
        if f in b:
            rules = set(o.get(f, {})) | set(t.get(f, {}))
            entry = {}
            for r in sorted(rules):
                v = min(o.get(f, {}).get(r, 0), t.get(f, {}).get(r, 0))
                if v > 0:
                    entry[r] = v
            if entry:
                out_map[f] = entry
        else:
            entry = dict(t.get(f, {}))
            entry.update(o.get(f, {}))
            out_map[f] = entry
    out = dict(ours)
    out[key] = out_map
    return out


def main():
    todo = {
        "tests/test_manifest.json": merge_manifest,
        "tools/visual_qa/lint_baseline.json": merge_lint,
    }
    hit = conflicted()
    for path, fn in todo.items():
        if path not in hit:
            continue
        base, ours, theirs = stage(path, 1) or {}, stage(path, 2), stage(path, 3)
        if ours is None or theirs is None:
            print(f"skip {path}: a side is missing")
            continue
        res = fn(base, ours, theirs)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(res, indent="\t", ensure_ascii=False) + "\n")
        subprocess.run(["git", "add", path], check=True)
        print(f"resolved {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
