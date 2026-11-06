import json, glob, os
for p in sorted(glob.glob('D:/rc_scratch/combat_redesign/locked/hover/chk/*.json')):
    try:
        j = json.load(open(p))
    except Exception:
        continue
    b = j.get('bill')
    if b:
        print(os.path.basename(p), b.get('live'), b.get('plan'), b.get('hp_after'))
