import sys, json
sys.dont_write_bytecode = True
J = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/state_e10.json'))
print('keys', list(J.keys()))
for k in ('f1', 'f2'):
    f = J[k]
    print(k, 'hp', f['hp'], 'maxhp', f['maxhp'], 'pv', {kk: vv for kk, vv in f['pv'].items() if kk != 'eq'})
    print('  eq', f['pv']['eq'])
    print('  next', f['next'])
    print('  waves_left', f['waves_left'], 'trace', f['trace'], 'tcap', f['tcap'], 'ram', f['ram'], f['ram_max'], 'refunds', f.get('refunds'))
    print('  chain', f.get('chain'))
    print('  hand', f['hand'], 'played', f['played'])
print('twist_payoff', J.get('twist_payoff'))
