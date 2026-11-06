"""hv_ranges_r2.py : the round-2 numbers hover/NOTES.md quotes, over every plate (prints only; every value from chk/<name>.checks.json, which
hv_checks.py measured on the plate PNG)"""
import sys, json, glob, os
sys.dont_write_bytecode = True
HERE = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
names = sorted(os.path.basename(p)[:-12] for p in glob.glob(HERE + 'chk/h*.checks.json'))
C = {n: json.load(open(HERE + 'chk/%s.checks.json' % n)) for n in names}
R = {n: json.load(open(HERE + 'chk/%s.json' % n)) for n in names}


def rng(vals):
    v = [x for x in vals if x is not None]
    return (min(v), max(v)) if v else None


def gk(d, *ks):
    for k in ks:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


print('plates', len(names), 'pass', sum(1 for n in names if C[n]['plate_pass']))
print('fails', {n: [k for k, v in C[n]['pass'].items() if not v] for n in names if not C[n]['plate_pass']})
allk = sorted({k for c in C.values() for k in c['pass']})
print('per check passing plates', {k: sum(1 for c in C.values() if c['pass'].get(k)) for k in allk})
print()
# b2 (C3 / C4)
print('b2 unclassed px', rng([gk(c, 'b2_bright', 'unclassed_px') for c in C.values()]))
print('b2 hot ref', rng([gk(c, 'b2_bright', 'hot_p95_lit') for c in C.values()]), 'pooled', rng([gk(c, 'b2_bright', 'hot_p95_pooled_lit') for c in C.values()]))
print('b2 tower ref', rng([gk(c, 'b2_bright', 'tower_p95_lit') for c in C.values()]), 'tower lit share', rng([gk(c, 'b2_bright', 'tower_lit_share') for c in C.values()]),
      'plates with a tower ref', [n for n, c in C.items() if gk(c, 'b2_bright', 'tower_p95_lit') is not None])
print('b2 focus margin under SEND IT (C3a, gated)', rng([gk(c, 'b2_bright', 'focus_margin_under_send') for c in C.values()]),
      'send p95', rng([gk(c, 'b2_bright', 'send_p95') for c in C.values()]))
print('b2 focus vs hot (reported)', rng([gk(c, 'b2_bright', 'focus_vs_hot_reported') for c in C.values()]))
print('b2 pencil p99', rng([gk(c, 'b2_bright', 'hover_rows', 'N pencil (hover, wax + ink)', 'p99') for c in C.values()]))
HMK = 'N hover marks (bursts, brackets, tints; r < 480)'
print('b2 hover marks p99', {n: (gk(c, 'b2_bright', 'hover_rows', HMK, 'p99'), gk(c, 'b2_bright', 'hot_p95_lit'))
                             for n, c in C.items() if gk(c, 'b2_bright', 'hover_rows', HMK)})
for n, c in C.items():
    b = c.get('b2_bright') or {}
    if b.get('failures_gated'):
        print('  b2 gated fail', n, b['failures_gated'])
mx = {}
for c in C.values():
    for nm, r in (gk(c, 'b2_bright', 'structure_rows') or {}).items():
        if nm == 'N FOCUS':
            continue
        h = gk(c, 'b2_bright', 'hot_p95_lit')
        if h is not None:
            mx.setdefault(nm, []).append(round(h - r['p99'], 1))
print('b2 class p99 margin under the HOT ref (min over plates)', {k: min(v) for k, v in mx.items()})
dm = [round(gk(c, 'b2_bright', 'hot_p95_lit') - r['p95'], 1) for c in C.values() for r in (gk(c, 'b2_bright', 'token_discs') or {}).values()
      if gk(c, 'b2_bright', 'hot_p95_lit') is not None]
print('b2 token disc p95 margin under HOT', rng(dm))
print()
# d2 (C2)
cls = {}
for n, c in C.items():
    for r in gk(c, 'd2_drawn', 'drawn_vs_token') or []:
        cls.setdefault(r['cls'], []).append((r['dE'], r['drawn_hex'], n))
for k, v in cls.items():
    print('d2 %-18s dE %s  hexes %s' % (k, rng([x[0] for x in v]), sorted({x[1] for x in v})))
print('d2 min vs corp ink', {n: min([r['dE'] for r in gk(c, 'd2_drawn', 'drawn_vs_corp_ink') or []], default=None) for n, c in C.items()
                             if gk(c, 'd2_drawn', 'drawn_vs_corp_ink')})
for n, c in C.items():
    if gk(c, 'd2_drawn', 'failures'):
        print('  d2 fail', n, gk(c, 'd2_drawn', 'failures'))
print('d2 solace rim', {n: gk(c, 'd2_drawn', 'solace_rim') for n, c in C.items() if gk(c, 'd2_drawn', 'solace_rim')})
print()
# f (C1)
for part in ('L6', 'L6_hud'):
    rows = [(gk(c, 'f_pencil_r2', part, 'rows') or [None])[0] for c in C.values()]
    rows = [r for r in rows if r]
    print('f %-6s plates %d wax %s stroke %s ink/side %s grain %s' % (part, len(rows), rng([r['wax_w'] for r in rows]), rng([r['stroke_w'] for r in rows]),
                                                                   rng([r['ink_per_side'] for r in rows]), rng([r['grain_L_std'] for r in rows])))
    for n, c in C.items():
        r = (gk(c, 'f_pencil_r2', part, 'rows') or [None])[0]
        if r and not r['pass_']:
            print('  f fail', n, part, r)
print()
# h (C8)
print('h bill measured', sorted({json.dumps(gk(c, 'h_hud_rows', 'measured')) for c in C.values()}))
print('h hud rows', sorted({json.dumps({k: v for k, v in (gk(c, 'h_hud_rows', 'row_record') or {}).items()}, sort_keys=True) for c in C.values()}))
print('h plate edges (board image) == board plate', {n: gk(c, 'h_hud_rows', 'hover_plate_edges_board_image') == gk(c, 'h_hud_rows', 'board_plate_edges') for n, c in C.items()})
print('h board refs', sorted({gk(c, 'h_hud_rows', 'board_reference') for c in C.values()}))
for n, c in C.items():
    if gk(c, 'h_hud_rows', 'failures'):
        print('  h fail', n, gk(c, 'h_hud_rows', 'failures'))
print()
# C17
for n, c in C.items():
    if 'h04' in n or 'h08' in n:
        print('c17', n, gk(c, 'c17_frame_band', 'gated'), gk(c, 'c17_frame_band', 'pencil_px_by_radius'), 'planlike frame band', gk(c, 'c17_frame_band', 'planlike_px_frame_band'))
print()
# e (C6)
for n, c in C.items():
    e = c['e_hand']
    print('e %-24s %s lift %s minr %s lift_r %s arcs %s low %s btn %s/%s/%s sib %s' % (
        n, 'PASS' if c['pass'].get('e_hand') else 'FAIL', (e.get('layout') or {}).get('lift_cy'), e.get('hand_min_r'), e.get('lift_min_r'),
        e.get('lift_px_within_3px_of_landing_marks'), e.get('hand_lowest_y'), e.get('hand_x_send_px'), e.get('hand_x_undo_px'), e.get('hand_px_within_2px_of_buttons'),
        [(s['sibling'], s.get('cost_px'), s.get('title_px'), s.get('rules_px'), s.get('mult_px')) for s in e.get('lifted_vs_sibling', [])]))
print()
# k refund tab
print('k refund tab', {n: (gk(c, 'k_refund_tab', 'tab_box'), gk(c, 'k_refund_tab', 'lift_px_in_tab'), gk(c, 'k_refund_tab', 'rest_px_in_tab'),
                           gk(c, 'k_refund_tab', 'gap_tab_right_to_lift_px'), gk(c, 'k_refund_tab', 'clearance', 'shift_px'))
                       for n, c in C.items() if gk(c, 'k_refund_tab', 'present')})
# a dying (C7)
for n, c in C.items():
    d = [(x['ring'], x['sector'], x['kind'], x['ratio'], x['occ_L'], x['empty_L'], x['gated'], x['pass_']) for x in c['a_cell_contrast'].get('rows', [])
         if x.get('state') == 'dying']
    if d:
        print('a dying', n, d)
print('a min gated ratio', rng([min([x['ratio'] for x in c['a_cell_contrast'].get('rows', []) if x['gated']] or [None]) for c in C.values()]))
print()
# i (C11, reported)
for n, c in C.items():
    i = c.get('i_hot_core_info') or {}
    print('i %-24s %s' % (n, {k: i.get(k) for k in ('present', 'core_w_px', 'core_vs_cell', 'fill_vs_cell_reported', 'pass_info', 'failures')}))
print()
print('dashes', {n: (gk(c, 'dashes', 'pixel_dot_runs'), gk(c, 'dashes', 'pixel_dot_runs_hover_made'), [r['bbox'] for r in gk(c, 'dashes', 'runs') or []])
                 for n, c in C.items() if gk(c, 'dashes', 'pixel_dot_runs')})
print('b dim', rng([c['b_value'].get('dim_luma_ratio') for c in C.values()]), 'lit', rng([c['b_value'].get('lit_luma_ratio') for c in C.values()]),
      'lifted', rng([c['b_value'].get('lifted card p95_L') for c in C.values()]), 'rest', rng([c['b_value'].get('resting hand p95_L') for c in C.values()]))
print('focus dE', rng([c['focus'].get('core_median_dE') for c in C.values()]), 'corners', sorted({x['corners'] for c in C.values() for x in c['focus'].get('calls', [])}),
      'bbox', rng([b for c in C.values() for x in c['focus'].get('calls', []) for b in (x.get('bbox_px') or [])]))
print('asserts', sorted({c['asserts']['board'] for c in C.values()}), [c['asserts']['insets'] for c in C.values() if c['asserts']['insets']])
print('insets', {n: [(i['name'], (i.get('source') or {}).get('placed_scale'), (i.get('source') or {}).get('placed_size'), i.get('box')) for i in R[n].get('insets', [])]
                 for n in names if R[n].get('insets')})
print('hand layouts', sorted({json.dumps(c['e_hand'].get('layout'), sort_keys=True) for c in C.values()}))
