import json, sys
d = json.load(open(sys.argv[1]))
for p in sys.argv[2].split('.'):
    if p == '': continue
    d = d[int(p)] if isinstance(d, list) else d[p]
s = json.dumps(d, indent=1)
lim = int(sys.argv[3]) if len(sys.argv) > 3 else 6000
print(s[:lim])
