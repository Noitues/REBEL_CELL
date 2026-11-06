import json
r = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
print(r['all_pass'])
print({k: (v['passed'], v['total']) if isinstance(v, dict) else v for k, v in r['draw_asserts'].items()})
for n, v in r['squint'].items():
    print(n, 'plate', v['plate'], '\n   tower', v['tower_r<=212'], '\n   rings', v['rings_r214-430'], '\n   hand', v['hand_zone'])
c = r['corp']
print({k: v for k, v in c.items() if not k.startswith('kind_dE2000_sw')})
print(r['cards']['type_colours'], r['cards']['icon_disc_min'])
print(r['game_info']['required_words_missing'], r['game_info']['cards_all_fields_drawn'])
print({k: v['ok'] for k, v in r['game_info']['state_cards_table'].items()})
print(r['game_info'].get('nowords_alnum_text_calls'))
