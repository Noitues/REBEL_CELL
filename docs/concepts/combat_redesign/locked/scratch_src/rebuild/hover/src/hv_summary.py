"""hv_summary.py : the numbers for hover/NOTES.md, from chk/<name>.checks.json and chk/<name>.json of every plate (prints, writes nothing)"""
import sys, json, glob, os
sys.dont_write_bytecode = True
HERE = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/'
names = sorted(os.path.basename(p)[:-12] for p in glob.glob(HERE + 'chk/h*.checks.json'))
for nm in names:
    c = json.load(open(HERE + 'chk/%s.checks.json' % nm))
    r = json.load(open(HERE + 'chk/%s.json' % nm))
    e = c['e_hand']
    b = c['b_value']
    p = c['pencil']
    gr = c['grain']
    fo = c['focus']
    rg = c['rings']
    fits = ['%s %s n%s' % (f['tag'], f.get('form'), f.get('n', '')) for f in rg.get('fits', [])]
    bad = [k for k, v in c['pass'].items() if not v]
    print('%-26s %s asserts %s | hand %s lift_r %s low %s send/undo %s/%s cost/rules %s | dim %s lit %s | pen %s/%s ink %s png %s | grain std %s p99 %s band %s/%s'
          ' | focus %s | rings %s | hud %s | fails %s' % (
              nm, 'PASS' if c['plate_pass'] else 'FAIL', c['asserts']['board'], e.get('layout'), e.get('lift_min_r'), e.get('hand_lowest_y'),
              e.get('hand_x_send_px'), e.get('hand_x_undo_px'),
              [(s['sibling'], s['cost_px'], s['rules_px']) for s in e.get('lifted_vs_sibling', [])],
              b.get('dim_luma_ratio'), b.get('lit_luma_ratio'), p['mask'].get('L6_wax'), p['mask'].get('L6_all'), p['mask'].get('L6_ink_each_side'),
              (p.get('png_L6') or {}).get('wax_px'), gr.get('L_std'), gr.get('L_p99'), gr.get('glow_band_yellow_px'), gr.get('board_band_yellow_px'),
              {k: v for k, v in fo.items() if k in ('core_median_dE', 'core_median_hex', 'old_lime_px', 'n_calls')},
              fits, c['hud_room_info'].get('hover_hud_bottom'), bad))
    if 'slices' in c and c['slices'].get('rows'):
        print('    slices', json.dumps(c['slices'].get('rows'))[:600])
    if c.get('options', {}).get('rows') or c.get('options', {}).get('n_rows'):
        print('    options', json.dumps({k: v for k, v in c['options'].items() if k != 'rule'})[:600])
    if c['ram']:
        print('    ram', json.dumps({k: v for k, v in c['ram'].items() if k != 'rule'})[:400])
    print('    a', 'gated', c['a_cell_contrast'].get('n_gated'), 'min gated ratio',
          min([x['ratio'] for x in c['a_cell_contrast'].get('rows', []) if x['gated']] or [None]) if c['a_cell_contrast'].get('rows') else None,
          'dash', json.dumps(c['dashes'])[:200])
