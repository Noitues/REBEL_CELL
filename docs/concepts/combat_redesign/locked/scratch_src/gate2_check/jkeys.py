"""jkeys.py <json> [path.to.key ...] [--depth N] -- print key tree (types, lens) of a JSON file."""
import sys, json

args = [a for a in sys.argv[1:] if not a.startswith('--')]
depth = 3
for a in sys.argv[1:]:
    if a.startswith('--depth='):
        depth = int(a.split('=')[1])
d = json.load(open(args[0], encoding='utf-8'))
for k in args[1:]:
    for part in k.split('.'):
        if isinstance(d, list):
            d = d[int(part)]
        else:
            d = d[part]


def show(o, ind=0, lvl=0):
    pad = '  ' * ind
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (dict, list)) and lvl < depth:
                print(f"{pad}{k}: {type(v).__name__}[{len(v)}]")
                show(v, ind + 1, lvl + 1)
            else:
                s = json.dumps(v)
                print(f"{pad}{k}: {s[:160]}")
    elif isinstance(o, list):
        for i, v in enumerate(o[:6]):
            if isinstance(v, (dict, list)) and lvl < depth:
                print(f"{pad}[{i}]: {type(v).__name__}[{len(v)}]")
                show(v, ind + 1, lvl + 1)
            else:
                print(f"{pad}[{i}]: {json.dumps(v)[:160]}")
        if len(o) > 6:
            print(f"{pad}... ({len(o)} items)")


show(d)
