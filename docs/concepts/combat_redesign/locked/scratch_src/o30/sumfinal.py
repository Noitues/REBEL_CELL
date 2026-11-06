import json
d = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
print('all_pass', d['all_pass'])
for k, v in d['draw_asserts'].items():
    print(k, v['passed'], v['total'], 'hand', d['hand_vs_board'][k].get('hand_min_r_px'), 'dots', d['dash_audit'][k].get('pixel_dot_runs'), 'first', d['dash_audit'][k].get('pixel_dot_runs_first_pass'))
for k, v in d['squint'].items():
    print(k, {r: v[r].get('final') for r in ('plate', 'tower_r<=212', 'room_x>=1100_y>=420_no_hand')})
print('p1 first pass room', d['squint']['p1_decide']['room_x>=1100_y>=420_no_hand'])
print('corp', {k: v for k, v in d['corp'].items() if k.startswith('tape') or k.startswith('pink')})
print('words missing', d['game_info']['required_words_missing'])
print('cards ok', d['game_info']['cards_all_fields_drawn'], 'nowords text', d['game_info'].get('nowords_alnum_text_calls'))
print('numbers', d['game_info'].get('tower_numbers'))
