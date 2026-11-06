"""show_vs_final.py : the base plates' difference against the published locked/final plates (from work/geo_*.json)"""
import json, glob, os
for p in sorted(glob.glob('D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/geo_*.json')):
    g = json.load(open(p))
    print(os.path.basename(p), g.get('vs_final'))
