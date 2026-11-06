import json
R = json.load(open('D:/rc_scratch/combat_redesign/locked/assembled/out/checks_partial.json'))
print(json.dumps(R['draw_asserts'], indent=1)[:3500])
print(json.dumps(R['collision'], indent=1)[:3000])
print(R['collision_total_px'])
print(json.dumps(R['dash_audit'], indent=1))
