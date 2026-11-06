import json
J = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/state_e10.json'))
f = J['f1']
print(list(f.keys()))
for w in f['wheel']: print(w)
for u in f['units']: print({k: u[k] for k in u if k in ('id','kind','dep','s','w','hp','mx','fate','consumed','trigdead','warded','lose','hp_after')})
