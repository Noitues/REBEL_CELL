import json
from collections import Counter
E = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/text_e10.json', encoding='utf-8'))
for b, sfx in (('p1', 'p1'), ('p2', 'p2'), ('p2b', 'p2b'), ('p3', 'p3')):
    c = json.load(open('D:/rc_scratch/combat_redesign/locked/assembled/work/chk_%s.json' % sfx))
    mine = Counter(t for t in c['textlog'] if len(t) > 1)
    e10 = Counter(t for t in E[b] if len(t) > 1)
    print(b, 'NEW', dict(mine - e10))
    print(b, 'GONE', dict(e10 - mine))
    m1 = Counter(t for t in c['textlog'] if len(t) == 1); e1 = Counter(t for t in E[b] if len(t) == 1)
    print(b, 'single new', dict(m1 - e1), 'gone', dict(e1 - m1))
