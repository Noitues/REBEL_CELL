"""Regenerate content into a temp copy of the repo and diff it against content/.
Exit 1 on any difference (content/ itself is never touched).
Usage: python tools/content_gen/check_regen.py [gen_name ...] [--keep] [--lines N]
Default generators: every gen_*.py that writes content (not the shared lib)."""
import difflib
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
# Order matters: classes and pools first (config patches), then corporations.
ORDER = ["gen_classes", "gen_pools", "gen_meridian", "gen_halcyon", "gen_orbital",
         "gen_rebel_cell", "gen_home", "gen_h1"]


def read(path):
    with open(path, "rb") as f:
        return f.read()


def main(argv):
    keep = "--keep" in argv
    lines = 12
    if "--lines" in argv:
        i = argv.index("--lines")
        lines = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    names = [a for a in argv if not a.startswith("--")] or ORDER
    tmp = tempfile.mkdtemp(prefix="regen_check_")
    try:
        shutil.copytree(os.path.join(ROOT, "content"), os.path.join(tmp, "content"))
        shutil.copytree(os.path.join(ROOT, "docs", "handoff"), os.path.join(tmp, "docs", "handoff"))
        shutil.copytree(HERE, os.path.join(tmp, "tools", "content_gen"),
                        ignore=shutil.ignore_patterns("__pycache__"))
        for n in names:
            script = os.path.join(tmp, "tools", "content_gen", n + ".py")
            r = subprocess.run([sys.executable, script], cwd=tmp, capture_output=True, text=True)
            if r.returncode != 0:
                print("FAIL running %s:\n%s" % (n, r.stderr))
                return 1
        bad = 0
        for base, _dirs, files in os.walk(os.path.join(tmp, "content")):
            for fn in sorted(files):
                new = os.path.join(base, fn)
                rel = os.path.relpath(new, tmp)
                old = os.path.join(ROOT, rel)
                if not os.path.exists(old) or read(old) != read(new):
                    bad += 1
                    print("DIFF", rel.replace("\\", "/"))
                    if os.path.exists(old):
                        a = read(old).decode("utf-8").splitlines()
                        b = read(new).decode("utf-8").splitlines()
                        for line in list(difflib.unified_diff(a, b, "content", "regen", lineterm="", n=0))[:lines]:
                            print("   ", line)
        print("check_regen: %d differing file(s)" % bad)
        return 1 if bad else 0
    finally:
        if keep:
            print("kept", tmp)
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
