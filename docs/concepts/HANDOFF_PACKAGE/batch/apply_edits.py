"""Apply a batch edit list ([{"old", "new"}] JSON, optionally wrapped in a ```json fence) to one file.

    python apply_edits.py <target file> <edits.md> [--dry]
Every `old` must occur exactly once; otherwise nothing is written and the bad edits are listed.
"""
import json
import re
import sys
from pathlib import Path

target, edits_path = Path(sys.argv[1]), Path(sys.argv[2])
raw = edits_path.read_text(encoding="utf-8")
m = re.search(r"\[.*\]", raw, re.S)
edits = json.loads(m.group(0))
s = target.read_text(encoding="utf-8")
bad = [i for i, e in enumerate(edits) if s.count(e["old"]) != 1]
if bad:
    for i in bad:
        print("BAD", i, s.count(edits[i]["old"]), repr(edits[i]["old"][:80]))
    sys.exit(1)
for e in edits:
    s = s.replace(e["old"], e["new"])
if "--dry" not in sys.argv:
    target.write_text(s, encoding="utf-8", newline="\n")
print("applied", len(edits))
