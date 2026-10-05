import json, subprocess, sys, io
# three-way union of tests/test_manifest.json: start from ours, add theirs' new scripts
p = "tests/test_manifest.json"
def show(ref):
    return json.loads(subprocess.check_output(["git", "show", "%s:%s" % (ref, p)]).decode("utf-8"))
ours, theirs = show("HEAD"), show("MERGE_HEAD")
def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = merge(a[k], v) if k in a else v
        return out
    return a
m = merge(ours, theirs)
raw = io.open(p, encoding="utf-8").read()
indent = "\t" if "\n\t" in subprocess.check_output(["git", "show", "HEAD:" + p]).decode("utf-8") else 2
io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=indent) + "\n")
print("scripts", len(m.get("scripts", m)))
