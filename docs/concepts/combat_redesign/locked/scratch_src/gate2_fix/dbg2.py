import sys, json
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_checks as RC
c = json.load(open(RC.WORK + 'chk_p1.json'))
for t in c['rb']['text']:
    if t['text'] in ('SEND IT', 'CELL-9', '// BREAKER', 'UNDO', 'YOU', 'Z', 'BREAKER'):
        print(t)
