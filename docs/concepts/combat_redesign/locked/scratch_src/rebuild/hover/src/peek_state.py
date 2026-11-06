"""print the top-level structure of state_e10.json (read only)"""
import json, sys
sys.dont_write_bytecode = True
J = json.load(open('D:/rc_scratch/combat_redesign/locked/corp/state_e10.json'))
for k, v in J.items():
    if isinstance(v, dict):
        print(k, 'dict', list(v.keys())[:40])
    elif isinstance(v, list):
        print(k, 'list', len(v), str(v)[:300])
    else:
        print(k, repr(v)[:200])
print('meta', json.dumps(J.get('meta'), default=str)[:1500])
print('twist_payoff', json.dumps(J.get('twist_payoff'), default=str)[:800])
print('f1 next', J['f1'].get('next'))
print('f1 pv', json.dumps(J['f1']['pv'])[:600])
print('f1 hand', J['f1']['hand'], 'ram', J['f1']['ram'], 'trace', J['f1']['trace'])
