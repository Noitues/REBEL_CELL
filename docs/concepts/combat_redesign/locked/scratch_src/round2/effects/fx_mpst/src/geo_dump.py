"""geo_dump.py <chk json> : print the structure of a corp/work chk_*.json rb section (keys, geometry, text draws with boxes)."""
import sys, json
d = json.load(open(sys.argv[1]))
print('top', list(d.keys()))
rb = d.get('rb', {})
print('rb keys', list(rb.keys()))
for k, v in rb.items():
    s = json.dumps(v)
    print('--', k, len(s), s[:1500])
