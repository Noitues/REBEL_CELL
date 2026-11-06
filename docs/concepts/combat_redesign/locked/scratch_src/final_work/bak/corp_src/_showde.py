import json
r=json.load(open('../work/de_kinds.json'))
for n,v in r.items():
    if isinstance(v,list): print(n,v); continue
    print(n,' '.join('r%d min %.1f mean %.1f'%(d,v['ring%d'%d]['min'],v['ring%d'%d]['mean']) for d in range(3)))
