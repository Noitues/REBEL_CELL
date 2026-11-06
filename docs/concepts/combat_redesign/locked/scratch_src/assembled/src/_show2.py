import json
R = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/assembled/checks.json'))
print('asserts', {k: (v['passed'], v['total']) for k, v in R['draw_asserts'].items()})
print('collision', R['collision_total_px'])
print(json.dumps(R['squint'], indent=0)[:200])
for p, d in R['squint'].items():
    for rn in ('plate', 'tower_r<=212', 'hand_zone', 'send_it', 'hud', 'rings_r214-430'):
        print(p, rn, {k: tuple(v.values()) for k, v in d[rn].items()})
g = R['game_info']
print('cards_table_all_ok', g['cards_table_all_ok'], 'cards_drawn_all_ok', g['cards_drawn_all_ok'])
for b, d in g['cards_drawn'].items():
    for c, v in d.items():
        print(b, c, v['ok'], v['missing'], v['extra'], v['cost_in_plate'], v['trace_in_plate'])
print(json.dumps(g['required_words_missing']))
for b, v in g['text_inventory_vs_e10'].items():
    print(b, v['chars_locked'], v['chars_e10'], 'miss', v['missing_vs_e10'], 'extra', v['extra_vs_e10'])
print(g.get('nowords_alnum_strings_drawn_by_text_calls'))
print(g.get('tower_numbers') and {k: {x: y for x, y in v.items() if x.endswith('match')} for k, v in g['tower_numbers'].items()})
