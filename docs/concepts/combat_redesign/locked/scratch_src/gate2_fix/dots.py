"""dots.py: the plates with pixel dot runs in rebuild/board/checks.json, and where"""
import json, sys
sys.dont_write_bytecode = True
R = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))
for k, v in R.items():
    if isinstance(v, dict):
        for name, d in v.items():
            if isinstance(d, dict) and d.get('pixel_dot_runs'):
                print(k, name, d['pixel_dot_runs'], d.get('pixel_dot_run_list'))
