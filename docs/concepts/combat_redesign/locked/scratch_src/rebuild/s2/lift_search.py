"""stage 2: p2 lifted-card layout on the new hand base (fan 4.0, left 1035, cy0 904): lifted Trigger clear of every sibling cost hex and rules block
(rules_box: one or two lines), hand off SEND IT / UNDO, outside r455 (+3 px), bottom <= 1068."""
import sys, itertools, json
sys.dont_write_bytecode = True
import hand_search as HS

LEFT, CY0, FAN = 1035, 904, 4.0
best = None
for dx, cy, push in itertools.product(range(-48, 1, 4), range(780, 872, 4), range(12, 41, 4)):
    r = HS.evaluate('p2', LEFT, 168, CY0, FAN, dict(dx=dx, cy=cy, push=push))
    bad = r['sib'] + r['send'] + r['undo'] + (0 if r['minr'] >= 458.0 else 1000) + (0 if r['bottom'] <= HS.BOTTOM_MAX else 1000)
    score = (bad, abs(dx) + abs(push - 16) + abs(cy - 832))
    if best is None or score < best[0]:
        best = (score, dx, cy, push, r)
        print(best, flush=True)
print('best', best)
json.dump(dict(dx=best[1], cy=best[2], push=best[3], res=best[4]), open('D:/rc_scratch/combat_redesign/locked/rebuild/s2/lift_search.json', 'w'))
