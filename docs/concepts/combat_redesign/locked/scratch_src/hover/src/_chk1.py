import json
c = json.load(open('D:/rc_scratch/combat_redesign/locked/assembled/work/chk_p2b.json'))
print(c['overlap_px'], [a for a in c['asserts'] if not a['ok']])
