"""hv_publish: copy the rebuilt hover plates and the key to art-pass locked/hover/, build contact_sheet.jpg (the 11 neutral plates + the key)
and checks.json (all_pass per check over every plate, a per-plate summary with the numbers, the key's text caps, and every plate's full
checks).  Run after hv_set.py, hv_key.py and hv_checks.py.
python hv_publish.py"""
import sys, os, json, shutil, glob
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFont

SRC = 'D:/rc_scratch/combat_redesign/locked/rebuild/hover/'
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
    d.text((pad, 18), 'HOVER PLATES  |  rebuilt board 2026-11-03 (neutral), one per card effect type', font=an, fill=(242, 246, 255))
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
            dashes=dict(dash_calls=ck['dashes']['dash_calls'], dot_calls=ck['dashes']['dot_calls'], pixel_dot_runs=ck['dashes']['pixel_dot_runs']),
            nowords_text=ck['nowords'].get('alnum_text_calls'), hud_room=ck['hud_room_info'], hand_layout=ck['e_hand'].get('layout'))
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
        e='rb_checks.check_hand + the board hand rules (r455, lifted r459 and 3 px off landings, lowest y 1067, 2 px off SEND IT / UNDO, resting cost hexes clear)',
        hover='pencil widths, grain and glow, rings, HP strip, RAM, insets, option rows, 3.13 slices, FOCUS colour and corners, collisions, dashes, nowords, asserts: see hv_checks.py',
        hud_room='cross-set: the hover HUD carries the ring room (and on h04 the option rows), so it is taller than the board HUD; reported per plate, not gated',
        e_rest_faces='new gate in e: no resting card face more covered by the resting cards after it than on the board\'s own resting fan of the same hand '
                     '(rest_faces). h02 x4 fail it: Brace is lifted from slot 0 (the E10 hand order) and no layout in the 4-card fan keeps the board rules '
                     'and every resting face; the least-move layout is drawn. h05-h09 hold their showcase card in slot 1 (plan records unchanged)',
        a_board_image='a_cell_contrast.board_image_same_state: the board check a on the board image under the plate (same plan state, no hover). '
                      'h03 x2 fail a on r0 s3 (dying Packet) where the board image fails the board check on the same cell: a board renderer item',
        pencil_widths='widths integrated on the saved pencil coverage (Pv__), not the run of a 50 % mask (which jumps a pixel with the sub-pixel position)')
    json.dump(dict(all_pass=allp, summary=summ, key=key, notes=notes, full=full), open(DST + 'checks.json', 'w'), indent=1, default=str)
    print('published %d plates + key; all_pass %s' % (len(exp) - 1, allp))
    return 0


if __name__ == '__main__':
    sys.exit(main())
