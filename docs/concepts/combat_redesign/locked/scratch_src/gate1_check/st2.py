import json
st = json.load(open('D:/rc_scratch/combat_polish/E7_waves/E10/state_e10.json'))
for k in ['twist_payoff', 'trigs', 'hover', 'meta']:
    print(k, json.dumps(st[k])[:1500])
print('f2 log', st['f2']['log'])
print('f2 tlog', st['f2']['tlog'])
