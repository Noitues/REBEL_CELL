"""keys.py: the key structure of one rb_checks entry in rebuild/board/checks.json"""
import json, sys
R = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))['rb_checks']
r = R[sorted(R)[0]]
print(sorted(R)[0], list(r.keys()))
for k, v in r.items():
    if isinstance(v, dict):
        print(' ', k, list(v.keys())[:12])
