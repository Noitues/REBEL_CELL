"""summ.py: print the gate-1 numbers from rebuild/board/checks.json and the per-plate rb checks (work/rb_<plate>.json or chk) for the NOTES"""
import json, sys, os, glob
sys.dont_write_bytecode = True
B = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
R = json.load(open(B + 'checks.json'))
print('all_pass', R['all_pass'])
print('cards_all_fields_drawn', R['game_info'].get('cards_all_fields_drawn'), 'words missing', {k: v for k, v in R['game_info']['required_words_missing'].items() if v})
print('squint_tower_zone', json.dumps(R.get('squint_tower_zone')))
gs = R.get('grammar_step3', {})
for k, v in gs.items():
    if 'chev' in k.lower():
        print('grammar', k, json.dumps(v)[:900])
rp = R.get('review_probes', {})
if isinstance(rp, dict):
    for sfx, d in rp.items():
        print('probes', sfx)
        for n, v in d.items():
            print('   %-48s L %-6s old_L %-6s box %s  (%s)' % (n, v['L'], v['old_L'], v['box'], v['lands_on']))
else:
    print('probes', rp)
