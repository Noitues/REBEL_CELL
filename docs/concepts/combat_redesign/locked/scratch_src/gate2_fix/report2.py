"""report2.py: c counts, ticket glyph p90, hand margin, draw asserts, occupied NOW range, uncaptured text, per plate (final/checks.json)"""
import json, sys
sys.dont_write_bytecode = True
R = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/checks.json'))
rb = R['rb_checks']
cn = {k: (v['c_cap_height']['n'], v['c_cap_height']['n_fail'], len(v['c_cap_height']['uncaptured_text']),
          v['c_cap_height']['parked'].get('n') if isinstance(v['c_cap_height']['parked'], dict) else None) for k, v in rb.items()}
print('c (n, fail, uncaptured, parked):', cn)
s2 = R.get('stage2_measures', {})
p90 = [g['p90_L'] for v in s2.values() for t in v.get('ticket_glyphs', []) for g in t]
print('ticket glyph p90 L* %.1f-%.1f' % (min(p90), max(p90)) if p90 else 'no ticket data')
print('hand margin', sorted(set(v.get('hand_margin_px') for v in s2.values())))
print('occ NOW', {k: v['a_cell_contrast']['occ_now_L_range'] for k, v in rb.items() if k in ('p1_decide', 'p2_preview', 'p3_resolve', 'p1_decide_meridian')})
dn = {k: (v['d_palette']['n_pairs'], len(v['d_palette']['failures'])) for k, v in rb.items()}
print('d pairs/fails range', min(x[0] for x in dn.values()), max(x[0] for x in dn.values()), sum(x[1] for x in dn.values()))
print('dash', {k: v for k, v in R['all_pass'].items()})
