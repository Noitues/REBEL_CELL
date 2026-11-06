"""lift_pick.py: from logs/lift_scan3.log, the (fan mode, D, open, print) combinations where every slot 0-3 has a clear lift window at
BTN_DX 16, with the windows"""
import re
by = {}
for ln in open('D:/rc_scratch/combat_redesign/locked/round2/fix2/logs/lift_scan3.log'):
    m = re.match(r'(OK|no)\s+(shift|shrink) D\s+(\d+) open\s+(\d+) slot (\d) print (\w+)\s+btn (\d+) window (\[[^\]]*\]|None)', ln)
    if not m:
        continue
    ok, mode, D, op, slot, pr, b, win = m.groups()
    by.setdefault((mode, int(D), int(op), pr), {})[int(slot)] = win if ok == 'OK' else None
for k, sl in sorted(by.items()):
    if all(sl.get(s) for s in range(4)):
        print('ALL OK', k, sl)
print('---- slot 0 OK')
for k, sl in sorted(by.items()):
    if sl.get(0):
        print(k, sl)
