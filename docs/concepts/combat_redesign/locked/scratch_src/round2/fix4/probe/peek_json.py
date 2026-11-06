"""peek_json.py <file.json> [path/with/slashes] [maxchars]: print a json subtree's keys or value (read only)"""
import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
if len(sys.argv) > 2 and sys.argv[2]:
    for k in sys.argv[2].split('/'):
        d = d[int(k)] if isinstance(d, list) else d[k]
mx = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
if isinstance(d, dict):
    for k, v in d.items():
        print(k, ':', json.dumps(v)[:mx // max(1, len(d)) + 80])
else:
    print(json.dumps(d, indent=1)[:mx])
