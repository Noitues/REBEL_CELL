"""gate1: summarise out/rb_checks_published.json (b round2, token discs, a rows, e, f, h, i)."""
import json
R = json.load(open('out/rb_checks_published.json'))
for nm, r in R.items():
    b = r['b_value_order']
    bb = b['round2']
    tab = {x['family']: x for x in b['sorted']}
    print('=' * 80)
    print(nm, 'HOT p95', tab.get('T HOT marks', {}).get('p95'), 'tower p95', tab.get('P tower', {}).get('p95'), 'SEND IT', tab.get('SEND IT', {}).get('p95'))
    print(' unclassed_px', bb['unclassed_px'], 'clusters', bb['unclassed_clusters'][:5] if isinstance(bb['unclassed_clusters'], list) else bb['unclassed_clusters'])
    sr = bb['structure_rows']
    rows = sr if isinstance(sr, list) else list(sr.values())
    top = sorted(rows, key=lambda q: -(q.get('p99') or 0))[:6]
    print(' top structure p99', [(q.get('cls') or q.get('class') or q.get('family'), q.get('p95'), q.get('p99')) for q in top])
    td = bb['token_discs']
    tdr = td if isinstance(td, list) else td.get('rows', td)
    if isinstance(tdr, dict):
        tdr = list(tdr.values())
    print(' token discs', [(q.get('cls') or q.get('unit'), q.get('p95'), q.get('p99'), q.get('pass_')) for q in tdr])
    # all other b classes: p99 vs HOT
    allrows = b.get('mark_rows') or b.get('rows') or []
    a = r['a_cell_contrast']
    g = [x for x in a['rows'] if x['gated']]
    w = min(g, key=lambda q: q['ratio'] or 99) if g else None
    print(' a worst gated', w and (w['ring'], w['sector'], w['kind'], w['state'], round(w['occ_L'], 1), w['empty_L'], w['ratio']))
    dy = [x for x in a['rows'] if x['state'] == 'dying']
    print(' a dying', [(x['ring'], x['sector'], x['kind'], round(x['occ_L'], 1), x['ratio'], x.get('px')) for x in dy])
    print(' f', {k: v for k, v in r['f_pencil'].items() if k not in ('rule',)})
    print(' i core', r['i_hot_core'].get('core_w_px'), r['i_hot_core'].get('core_vs_cell'), 'under', [(s['w'], s['box']) for s in r['i_hot_core'].get('strokes_under_min', [])])
    print(' e', r['e_hand'].get('hand_x_send_px'), r['e_hand'].get('hand_x_undo_px'), r['e_hand'].get('lifted_vs_sibling'))
