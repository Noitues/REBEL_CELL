"""r2_verify.py -- re-measure the PUBLISHED backdrop plates (docs/.../locked/backdrop/*.png) from the files themselves and compare with the
published checks.json; print the numbers the NOTES quote (room, as seen, box / street, reviewer box, p95 chain, cells, C3 unclassed px,
token discs, HOT core, HUD rows, C16 rim on Solace, squint).  Writes round2/backdrop/work/verify.json."""
import sys, json, os
sys.dont_write_bytecode = True
HERE = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/'
sys.path.insert(0, HERE)
import numpy as np
from PIL import Image
import r2_lib as L
import rb_checks as RC

DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
ck = json.load(open(DST + 'checks.json', encoding='utf-8'))
out = {}
for name, p in ck['plates'].items():
    sfx = p['capture']
    fp = DST + name + '.png'
    pl = np.asarray(Image.open(fp).convert('RGB'))
    s = L.stats(pl, sfx)
    rk = RC.run(name, fp, sfx)
    b = rk['b_value_order']
    tab = {r['family']: r for r in b['sorted']}
    same = s['room'] == p['after']['L']['room'] and s['room_as_seen'] == p['after']['L']['room_as_seen']
    rows = {k: tab[k]['p95'] for k in ('SEND IT', 'T HOT marks', 'P tower', 'P hand (rest)', 'E token discs', 'K clock (tape, sweep, plates)',
                                      'E cells occupied (glass)', 'room', 'E cells empty (glass)') if k in tab}
    a = rk['a_cell_contrast']
    gated = [r for r in a['rows'] if r['gated']]
    br = b['round2']
    discs = br.get('token_discs', {})
    d2 = rk['d_palette']['round2']
    o = dict(matches_checks_json=same, room=s['room'], room_as_seen=s['room_as_seen'], room_hull=s['room_hull']['mean'], room_city=s['room_city']['mean'],
             review_room_box=s['review_room_box'], detail=s['detail'], hull_median_rgb=s['hull_median_rgb'], hull_median_lab=s.get('hull_median_lab'),
             p95_chain=rows, room_ref=b['room_ref']['value'], clock_median=tab.get('K clock (tape, sweep, plates)', {}).get('median'),
             cells_lowest_ratio=min(r['ratio'] for r in gated), cells_occ_now_L=a['occ_now_L_range'],
             unclassed_bright_px=br['unclassed_px'],
             disc_p95=[min(v['p95'] for v in discs.values()), max(v['p95'] for v in discs.values())] if discs else None,
             disc_p99=[min(v['p99'] for v in discs.values()), max(v['p99'] for v in discs.values())] if discs else None,
             hot_core=dict((k, rk['i_hot_core'].get(k)) for k in ('core_w_px', 'core_vs_cell', 'fill_vs_cell', 'pass_') if k in rk['i_hot_core']),
             hud_rows_pass=rk['h_hud_rows']['pass_'], tickets_pass=rk['g_tickets']['pass_'], pencil_present=rk['f_pencil'].get('present'),
             palette_fail=len(rk['d_palette']['failures']), palette_pairs=rk['d_palette']['n_pairs'],
             solace_rim=d2.get('solace_rim'), caps_smallest=rk['c_cap_height']['smallest'][0]['cap_px'] if rk['c_cap_height']['smallest'] else None,
             hand=dict(send=rk['e_hand']['hand_x_send_px'], undo=rk['e_hand']['hand_x_undo_px']),
             squint=dict(room=p['after']['squint']['room'], board=p['after']['squint']['board'], plate=p['after']['squint']['plate']),
             plate_pass=rk['plate_pass'])
    out[name] = o
    print(name, 'same', same, 'room', s['room']['mean'], s['room']['p95'], 'seen', s['room_as_seen']['mean'], 'box/street', o['room_hull'], o['room_city'],
          'rbox', s['review_room_box']['mean'], 'det', s['detail']['detail_rel'], s['detail']['detail_rms'], 'sat', s['detail']['sat'],
          'pink', s['detail']['pink_share'], 'hue', o['hull_median_lab'], flush=True)
    print('   chain', rows, 'ref', o['room_ref'], 'clock med', o['clock_median'])
    print('   cells', o['cells_lowest_ratio'], o['cells_occ_now_L'], 'unclassed', o['unclassed_bright_px'], 'discs', o['disc_p95'], o['disc_p99'],
          'hot', o['hot_core'], 'hud', o['hud_rows_pass'], 'tickets', o['tickets_pass'], 'pal', o['palette_fail'], '/', o['palette_pairs'],
          'cap', o['caps_smallest'], 'hand', o['hand'], 'pass', o['plate_pass'])
    print('   squint room', o['squint']['room'], 'board', o['squint']['board'])
    if o['solace_rim']:
        print('   rim', o['solace_rim'] if not isinstance(o['solace_rim'], dict) else {k: v for k, v in o['solace_rim'].items() if not isinstance(v, (list, dict))})
json.dump(out, open(HERE + 'work/verify.json', 'w'), indent=1, default=str)
