"""report.py: the gate-1 numbers for the NOTES, from locked/final/checks.json"""
import json, sys
sys.dont_write_bytecode = True
R = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
print('all_pass', all(R['all_pass'].values()), [k for k, v in R['all_pass'].items() if not v])
rb = R['rb_checks']
p1 = rb['p1_decide']['b_value_order']
print('p1 families:', ', '.join('%s %.1f' % (r['family'], r['p95']) for r in p1['sorted']))
print('p1 marks:')
for n, r in p1['marks'].items():
    print('   %-30s p95 %.1f p99 %.1f med %.1f' % (n, r['p95'], r['p99'], r['median']))
# mark maxima across plates
mx = {}
for name, r in rb.items():
    for n, m in r['b_value_order']['marks'].items():
        if n not in mx or m['p99'] > mx[n][0]:
            mx[n] = (m['p99'], name)
hot = {name: next((x['p95'] for x in r['b_value_order']['sorted'] if x['family'] == 'T HOT marks'), 0) for name, r in rb.items()}
tow = {name: next((x['p95'] for x in r['b_value_order']['sorted'] if x['family'] == 'P tower'), 0) for name, r in rb.items()}
print('HOT p95 range %.1f-%.1f, tower p95 %.1f-%.1f' % (min(hot.values()), max(hot.values()), min(tow.values()), max(tow.values())))
print('max p99 per mark row:', {k: v for k, v in mx.items()})
rooms = {}
for name, r in rb.items():
    s = {x['family']: x for x in r['b_value_order']['sorted']}
    rooms[name] = (s['room']['mean'], s['room as seen (scrim kept, info)']['mean'])
print('room mean (gate region) / as seen:', {k: v for k, v in rooms.items() if k.startswith(('p2_', 'p3_', 'p1_decide'))})
d = rb['p1_decide']['d_palette']
low = sorted(d['rows'], key=lambda r: r.get('dE', 99))[:4] if isinstance(d['rows'], list) else None
print('d pairs', d['n_pairs'], 'lowest', low)
c = rb['p1_decide']['c_cap_height']
print('c p1 n', c['n'], 'fail', c['n_fail'], 'smallest', c['smallest'], 'parked', {k: v for k, v in c['parked'].items() if k != 'rows'} if isinstance(c['parked'], dict) else c['parked'], 'uncaptured', len(c['uncaptured_text']))
c2 = rb['p2b_hover']['c_cap_height']
print('c p2b parked', json.dumps(c2['parked'])[:300])
a = rb['p1_decide']['a_cell_contrast']
print('a adjuster_hp', a.get('adjuster_hp'))
print('tower zone squint', {k: v['final'] for k, v in R['squint_tower_zone'].items() if k in ('p1_decide', 'p2_preview', 'p3_resolve', 'p2b_hover')})
g = R['grammar_step3']['chevrons_sector3']['neutral']
print('grammar s3 neutral', [(x['grammar'], x.get('luma_contrast'), x.get('core_luma_contrast')) for x in g])
print('cards_all_fields_drawn', R['game_info']['cards_all_fields_drawn'])
for sfx, dd in R['review_probes'].items():
    if sfx != 'p1':
        continue
    for n, v in dd.items():
        print('   probe %-46s L %s L_box %s box %s | old %s L %s' % (n, v['L'], v.get('L_box'), v['box'], v['old_box'], v['old_L']))
