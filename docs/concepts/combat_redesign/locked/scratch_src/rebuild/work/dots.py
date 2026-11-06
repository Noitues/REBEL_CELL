"""dots.py: print the pixel dot runs per plate from rebuild/board/checks.json"""
import json
J = json.load(open('D:/rc_scratch/combat_redesign/locked/rebuild/board/checks.json'))
for k, v in J['dash_audit'].items():
    if v.get('pixel_dot_runs'):
        print(k, v['pixel_dot_runs'], v.get('pixel_dot_runs_first_pass'))
        for r in v['pixel_dot_run_list']:
            print('   ', r)
