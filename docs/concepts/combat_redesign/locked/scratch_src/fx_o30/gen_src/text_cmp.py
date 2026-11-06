import json, re
from collections import Counter
E = json.load(open('../out/text_e10.json')); N = json.load(open('../out/text_new.json'))
def words(lst):
    c = Counter()
    for s in lst:
        for w in re.findall(r"[A-Za-z0-9\+\-\?]+", s):
            c[w.upper()] += 1
    return c
def chars(lst):
    return Counter(ch.upper() for s in lst for ch in s if ch.isalnum())
for b in ['p1', 'p2', 'p2b', 'p3']:
    ce, cn = chars(E[b]), chars(N[b])
    de = {k: v - cn.get(k, 0) for k, v in ce.items() if v > cn.get(k, 0)}
    dn = {k: v - ce.get(k, 0) for k, v in cn.items() if v > ce.get(k, 0)}
    print('CHARS', b, 'E10', sum(ce.values()), 'new', sum(cn.values()), 'E10 has more:', de, '| new has more:', dn)
for b in []:
    we, wn = words(E[b]), words(N[b])
    only_e = {k: v - wn.get(k, 0) for k, v in we.items() if v > wn.get(k, 0)}
    only_n = {k: v - we.get(k, 0) for k, v in wn.items() if v > we.get(k, 0)}
    print('==', b, 'E10 words', sum(we.values()), 'new', sum(wn.values()))
    print('  in E10, fewer/missing in new:', only_e)
    print('  in new, not in E10:', only_n)
