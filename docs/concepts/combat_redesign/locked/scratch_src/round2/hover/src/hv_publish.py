"""hv_publish: copy the rebuilt hover plates and the key to art-pass locked/hover/, build contact_sheet.jpg (the 11 neutral plates + the key)
and checks.json (all_pass per check over every plate, a per-plate summary with the numbers, the key's text caps, and every plate's full
checks).  Run after hv_set.py, hv_key.py and hv_checks.py.
python hv_publish.py"""
import sys, os, json, shutil, glob
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

SRC = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
DST = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/hover/'
FD = 'D:/rc_art/art-pass/assets/fonts/'
NAMES = ['h01_tower_turn', 'h02_brace', 'h03_trigger', 'h04_twist', 'h05_strike', 'h06_shove', 'h07_pull', 'h08_hold', 'h09_firewall', 'h10_soak', 'h11_unit']
TITLE = {'h01_tower_turn': 'SPIN 3 | SPIN 2 | NUDGE', 'h02_brace': 'BRACE', 'h03_trigger': 'TRIGGER', 'h04_twist': 'TWIST', 'h05_strike': 'STRIKE',
         'h06_shove': 'SHOVE', 'h07_pull': 'PULL', 'h08_hold': 'HOLD', 'h09_firewall': 'FIREWALL', 'h10_soak': 'SOAK (no card)', 'h11_unit': 'UNIT HOVER'}


def font(name, px):
    for f in glob.glob(FD + '*'):
        if f.lower().endswith('.ttf') and name.lower() in os.path.basename(f).lower():
            return ImageFont.truetype(f, px)
    return ImageFont.load_default()


def expected():
    out = []
    for n in NAMES:
        out += [n, n + '_nowords']
    for n in ('h02_brace', 'h04_twist'):
        out += [n + '_solace', n + '_meridian']
    return out + ['h00_key']


def main():
    exp = expected()
    missing = [n for n in exp if not os.path.exists(SRC + 'out/' + n + '.png')]
    if missing:
        print('missing plates, not publishing:', missing)
        return 1
    for n in exp:
        shutil.copy(SRC + 'out/' + n + '.png', DST + n + '.png')
    tw, th, pad, top = 640, 360, 16, 46
    cols, rows = 4, 3
    sheet = Image.new('RGB', (cols * (tw + pad) + pad, 110 + rows * (th + top + pad)), (8, 10, 22))
    d = ImageDraw.Draw(sheet)
    an, mo, an2 = font('anton', 44), font('mono', 23), font('anton', 28)
    d.text((pad, 18), 'HOVER PLATES  |  round-2 board 2026-11-04 (neutral), one per card effect type', font=an, fill=(242, 246, 255))
    d.text((pad + 2, 76), 'dim value x0.40 chroma x0.45  |  FOCUS = four corners  |  PLAN arrow = movement  |  pencil ring = this number changes  |  hatch = lost at END TURN',
           font=mo, fill=(175, 192, 214))
    for i, nm in enumerate(NAMES + ['h00_key']):
        c, r = i % cols, i // cols
        x, y = pad + c * (tw + pad), 110 + r * (th + top + pad)
        d.text((x, y + 4), TITLE.get(nm, 'GRAMMAR KEY'), font=an2, fill=(242, 246, 255))
        d.text((x + tw - 4, y + 12), nm[:3], font=mo, fill=(175, 192, 214), anchor='ra')
        sheet.paste(Image.open(SRC + 'out/' + nm + '.png').convert('RGB').resize((tw, th), Image.LANCZOS), (x, y + top))
    sheet.save(DST + 'contact_sheet.jpg', quality=90)
    full, summ = {}, {}
    for n in exp[:-1]:
        cp = SRC + 'chk/' + n + '.checks.json'
        if not os.path.exists(cp):
            print('no checks for', n)
            return 1
        ck = json.load(open(cp))
        rep = json.load(open(SRC + 'chk/' + n + '.json'))
        full[n] = dict(checks=ck, report={k: v for k, v in rep.items() if k not in ('geometry', 'rbc', 'snap')})
        b = ck['b_value']
        summ[n] = dict(
            plate_pass=ck['plate_pass'], failing=[k for k, v in ck['pass'].items() if not v], asserts=ck['asserts']['board'], inset_asserts=ck['asserts']['insets'],
            cells_gated=ck['a_cell_contrast'].get('n_gated'),
            a_failing_cells=['r%d s%d %s %s ratio %.2f' % (x['ring'], x['sector'], x['kind'], x['state'], x['ratio']) for x in ck['a_cell_contrast'].get('rows', [])
                             if x['gated'] and not x['pass_']],
            a_board_image_same_state=dict((k, (ck['a_cell_contrast'].get('board_image_same_state') or {}).get(k)) for k in
                                          ('pass_', 'failing_cells', 'hover_fails_also_failing_on_board', 'hover_fails_board_passes')),
            resting_rules_covered_px_info=[(x['card'], x['rules_covered_px']) for x in ck['e_hand'].get('rest_cards_covered_info', [])],
            dim_luma_ratio=b.get('dim_luma_ratio'), lit_luma_ratio=b.get('lit_luma_ratio'),
            dim_board_p95_L=b.get('dim_board_p95_L'), pencil_p95_L=(b.get('pencil wax (L6 + L5)') or {}).get('p95_L'), focus_p95_L=(b.get('FOCUS corners') or {}).get('p95_L'),
            lifted_p95_L=b.get('lifted card p95_L'), resting_p95_L=b.get('resting hand p95_L'), cap_min_px=(ck['c_cap_height'].get('smallest') or [{}])[0].get('cap_px'),
            palette_fails=len(ck['d_palette']['failures']),
            hand=dict((k, ck['e_hand'].get(k)) for k in ('hand_x_send_px', 'hand_x_undo_px', 'hand_min_r', 'lift_min_r', 'lift_px_within_3px_of_landing_marks', 'hand_lowest_y',
                                                         'hand_px_within_2px_of_buttons', 'rest_cost_hex_covered_px')),
            lifted_vs_sibling=ck['e_hand'].get('lifted_vs_sibling'),
            pencil=dict([(k, ck['pencil']['mask'].get(k)) for k in ('L6_wax', 'L6_all', 'L6_ink_each_side', 'L5_wax', 'L5_all')]
                        + [('png_L6_wax', (ck['pencil'].get('png_L6') or {}).get('wax_px')), ('png_L6_ink', (ck['pencil'].get('png_L6') or {}).get('ink_px'))]),
            rest_faces=ck['e_hand'].get('rest_faces'),
            grain=dict((k, ck['grain'].get(k)) for k in ('L_mean', 'L_std', 'L_p99', 'glow_band_yellow_px', 'board_band_yellow_px')),
            rings=[dict((kk, f.get(kk)) for kk in ('tag', 'form', 'n', 'ok', 'ring_box')) for f in ck['rings']['fits']],
            hp_strip_px=ck['hp_strip']['px'], ram=ck['ram']['px'], insets=ck['insets']['rows'],
            options=dict((k, ck['options'].get(k)) for k in ('n_rows', 'plan_px_in_rows', 'stars')) if ck['options'].get('applies') else None,
            slices=ck['slices'].get('rows') if ck['slices'].get('applies') else None,
            focus=dict((k, ck['focus'].get(k)) for k in ('core_median_hex', 'core_median_dE', 'old_lime_px', 'n_calls')) if ck['focus'].get('applies', True) else None,
            focus_corners=sorted(set(c['corners'] for c in ck['focus'].get('calls', []))),
            collide=dict(hover_vs_marks_px=ck['collide'].get('hover_vs_marks_px'), occlusion_px=ck['collide'].get('occlusion_px'), mark_pairs_px=ck['collide'].get('mark_pairs_px')),
            dashes=dict(dash_calls=ck['dashes']['dash_calls'], dot_calls=ck['dashes']['dot_calls'], pixel_dot_runs=ck['dashes']['pixel_dot_runs'],
                        hover_made=ck['dashes'].get('pixel_dot_runs_hover_made'), board_made=ck['dashes'].get('pixel_dot_runs_board_made'),
                        runs=[dict(n=x['n'], spacing=x['spacing'], bbox=x['bbox'], board_made=x.get('board_made')) for x in ck['dashes'].get('runs', [])]),
            nowords_text=ck['nowords'].get('alnum_text_calls'), hand_layout=ck['e_hand'].get('layout'),
            # round 2
            b2_bright=dict((k, (ck.get('b2_bright') or {}).get(k)) for k in ('unclassed_px', 'unclassed_clusters', 'hot_p95_lit', 'hot_p95_by_class_lit',
                                                                          'hot_p95_pooled_lit', 'tower_p95_lit', 'tower_lit_share', 'tower_p95_lit_any_share',
                                                                          'failures_gated', 'send_p95', 'focus_margin_under_send', 'focus_vs_hot_reported',
                                                                          'hover_rows')),
            b2_token_discs=(ck.get('b2_bright') or {}).get('token_discs'),
            d2_drawn=dict(vs_token=[(r['cls'], r['drawn_hex'], r['dE']) for r in (ck.get('d2_drawn') or {}).get('drawn_vs_token', [])],
                          min_vs_corp_ink=min([r['dE'] for r in (ck.get('d2_drawn') or {}).get('drawn_vs_corp_ink', [])], default=None),
                          failures=(ck.get('d2_drawn') or {}).get('failures'), solace_rim=(ck.get('d2_drawn') or {}).get('solace_rim')),
            f_pencil_L6=dict((k, ((ck.get('f_pencil_r2') or {}).get('L6') or {}).get('rows', [{}])[0].get(k) if ((ck.get('f_pencil_r2') or {}).get('L6') or {}).get('rows') else None)
                             for k in ('wax_w', 'stroke_w', 'ink_per_side', 'grain_L_std', 'wax_L_median', 'px')),
            f_pencil_L6_hud=dict((k, ((ck.get('f_pencil_r2') or {}).get('L6_hud') or {}).get('rows', [{}])[0].get(k) if ((ck.get('f_pencil_r2') or {}).get('L6_hud') or {}).get('rows') else None)
                                 for k in ('wax_w', 'stroke_w', 'ink_per_side', 'grain_L_std', 'wax_L_median', 'px')),
            k_refund_tab=dict((k, (ck.get('k_refund_tab') or {}).get(k)) for k in ('present', 'tab_box', 'lift_px_in_tab', 'rest_px_in_tab', 'gap_tab_right_to_lift_px', 'clearance')),
            a_dying=[dict(ring=x['ring'], sector=x['sector'], kind=x['kind'], ratio=x['ratio'], occ_L=x['occ_L'], empty_L=x['empty_L'], gated=x['gated'], pass_=x['pass_'])
                     for x in ck['a_cell_contrast'].get('rows', []) if x.get('state') == 'dying'],
            h_hud_rows=dict((k, (ck.get('h_hud_rows') or {}).get(k)) for k in ('measured', 'row_record', 'failures', 'board_reference', 'hover_plate_edges_board_image',
                                                                              'board_plate_edges')),
            c17=dict((k, (ck.get('c17_frame_band') or {}).get(k)) for k in ('gated', 'pencil_px_by_radius', 'planlike_px_frame_band')),
            i_hot_core_info=dict((k, (ck.get('i_hot_core_info') or {}).get(k)) for k in ('core_w_px', 'core_vs_cell', 'fill_vs_cell_reported', 'core_L', 'cell_L')))
    keys = sorted({k for v in full.values() for k in v['checks']['pass']})
    allp = {k: all(v['checks']['pass'].get(k, False) for v in full.values()) for k in keys}
    allp['every_plate'] = all(v['checks']['plate_pass'] for v in full.values())
    key = json.load(open(SRC + 'chk/h00_key.json'))
    allp['key_text_cap_16'] = key['smallest_cap_px'] is not None and key['smallest_cap_px'] >= 15.95
    notes = dict(
        L_star='every value number is CIE L* of sRGB luminance (rb_tokens.lstar = the reviewer\'s measure.py), measured on the published PNG',
        a='rb_checks.check_cells on the lit cells (60 % of the glass lit); hover-dimmed cells and ghosts reported',
        b='hover rules gated (dim x0.40 +- 0.03 in sRGB luma, lit 0.97-1.03, pencil and FOCUS above the dimmed board, lifted card above the rest); the board A.1 chain reported only',
        c='rb_checks.check_caps: every text draw >= 16 px cap (inset tabs, ring tags, option tags included)',
        d='rb_checks.check_palette (tokens incl. PLAN and FOCUS, slice inks, card types, skin inks, HOT / COLD vs the lit cells); FOCUS / PLAN vs cells reported',
        e='rb_checks.check_hand (round 2: rb_lift.protected = cost hex, title band, rules line, xN plate) + the board hand rules (r455, lifted r459 and 3 px off landings, lowest y 1067, 2 px off SEND IT / UNDO, resting cost hexes clear)',
        round2='b2_bright: rb_checks_r2.check_bright (C3 unclassed bright px inside r480 = 0, class rows, C4 per disc).  HOT reference = the loudest LIT HOT class '
               '(chevrons or T arc) p95 on the plate (the pooled lit p95 reported); tower reference only when 50 % of the tower is lit (else no tower rule); '
               'hover ghosts cut by FOCUS / pencil on top; FOCUS vs HOT reported, open designer call. '
               'd2_drawn: rb_checks_r2.check_drawn (C2 drawn colours: hover marks whole, board marks where lit and not under a hover mark). '
               'f_pencil_r2: rb_checks_r2.check_pencil on L6 on the board and in the HUD (rings, YOU underline; HUD panel not cut) (C1). '
               'h_hud_rows: rb_checks_r2.check_hud_rows + the HUD plate edges vs the published board plate (C8). c17_frame_band: 0 PLAN px at r 480-500 on the Twist plates (C17). '
               'k_refund_tab: 0 hand px inside the REFUND tab. i_hot_core_info: rb_checks_r2.check_hot_core, reported. '
               'dashes: runs made only of the same-state board image\'s own dot-audit spots (a 1 px keyline\'s AA steps, chained on the plate because the hover dims the dark spots beside them) are reported, hover-made runs gated',
        lift='round 2 (C6): the hand is rb_lift.layout: fan slots kept, cards right of the lifted card open 36 px, straight-up lift at y 718 (slots 1-3), the UNDO / SEND IT column 16 px right; '
             'slot 0 (h02) has no straight-up lift outside r459: it rises 8 px (y 906) and its neighbour\'s cost hex and title are covered (check e fails, NOT DONE)',
        hover='pencil widths, grain and glow, rings, HP strip, RAM, insets, option rows, 3.13 slices, FOCUS colour and corners, collisions, dashes, nowords, asserts: see hv_checks.py',
        hud_rows='C8: the hover HUD is hud_rows, the board grid (option rows reserved on the board too): see h_hud_rows per plate.  The YOU strip is lit whole '
                 'with the bill (its die-cut edge pokes 6 px left of the bill frame).  The REFUND tab slides left of a lifted card that rises into its rows '
                 '(hv_core.TAB; h03: 33 px, coin 4 refunded); on board p2 the rule moves nothing',
        e_rest_faces='e also keeps: no resting card face more covered by the resting cards after it than on the board\'s own resting fan of the same hand '
                     '(rest_faces); with rb_lift the fan only opens. h05-h09 hold their showcase card in slot 1 (plan records unchanged)',
        a_board_image='a_cell_contrast.board_image_same_state: the board check a on the board image under the plate (same plan state, no hover), '
                      'with the round-2 dying-glass rule (the dying cell measured whole, hatch included, guns cut)',
        pencil_widths='widths integrated on the saved pencil coverage (Pv__), not the run of a 50 % mask (which jumps a pixel with the sub-pixel position)')
    json.dump(dict(all_pass=allp, summary=summ, key=key, notes=notes, full=full), open(DST + 'checks.json', 'w'), indent=1, default=str)
    print('published %d plates + key; all_pass %s' % (len(exp) - 1, allp))
    return 0


if __name__ == '__main__':
    sys.exit(main())
