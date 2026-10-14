"""Copy the locked round 44 A_map kits into this folder and patch their relative paths for one level less depth.
python copy_kits.py   (idempotent; never edits the source round)"""
import os, re, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "round44_undesigned", "A_map", "scripts")
SKIP = {"hq44.py", "raid44.py", "topbar44.py", "contact44.py", "route44.py", "clear_scratch.py"}
for root, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d != "__pycache__"]
    rel = os.path.relpath(root, SRC)
    dst = os.path.join(HERE, rel) if rel != "." else HERE
    os.makedirs(dst, exist_ok=True)
    for f in files:
        if not f.endswith(".py") or (rel == "." and f in SKIP):
            continue
        s = open(os.path.join(root, f), encoding="utf-8").read()
        s = s.replace("CONC = os.path.dirname(os.path.dirname(ROOT))", "CONC = os.path.dirname(ROOT)")
        s = s.replace("CONCEPTS = os.path.dirname(os.path.dirname(OUT))", "CONCEPTS = os.path.dirname(OUT)")
        s = s.replace('"..", "..", "..", "..", "round', '"..", "..", "..", "round') if rel != "." else s.replace('"..", "..", "..", "round', '"..", "..", "round')
        s = s.replace('ROOT, "..", "..", "..", "..", "content"', 'ROOT, "..", "..", "..", "content"')
        s = s.replace('OUT, "..", "..", "round6', 'OUT, "..", "round6')
        open(os.path.join(dst, f), "w", encoding="utf-8").write(s)
print("copied")
