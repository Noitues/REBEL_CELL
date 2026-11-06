"""list_fx.py : every effect id with its family, kind, duration and skins (for splitting the build)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_cdhl as F
ids = [f['id'] for f in F.FX] + [k for k in F.BYID if k not in [f['id'] for f in F.FX]]
for k in ids:
    f = F.BYID[k]
    print(k, f['fam'], f['kind'], f['dur'], ','.join(f['skins']))
