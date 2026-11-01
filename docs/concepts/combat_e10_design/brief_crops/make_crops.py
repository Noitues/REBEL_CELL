"""Crop every inventoried element of the E10 combat screen from the approved plates (read only) into this folder.
Run: python make_crops.py   (writes <cluster>__<id>.png, upscaled to at least 240 px on the long side, plus contact_<cluster>.jpg)
Source plates: D:/rc_tmp/combat_critic/plates/waves_e10/ (never written)."""
import os
from PIL import Image, ImageDraw, ImageFont

SRC = 'D:/rc_tmp/combat_critic/plates/waves_e10/'
OUT = os.path.dirname(os.path.abspath(__file__)) + '/'
P = {'p1': 'p1_decide.png', 'p2': 'p2_preview.png', 'p2b': 'p2b_hover.png', 'p3': 'p3_resolve.png', 'nw': 'p1_nowords.png'}

# (cluster, id, plate, box x0,y0,x1,y1 in 1920x1080 plate px)
E = [
    # ---------------- wheel_core
    ('wheel_core', 'hub_disc', 'p1', (482, 486, 590, 594)),
    ('wheel_core', 'hub_label', 'p1', (494, 528, 578, 562)),
    ('wheel_core', 'hub_emblem', 'p1', (514, 490, 560, 532)),
    ('wheel_core', 'slice_frame', 'p1', (398, 425, 525, 560)),
    ('wheel_core', 'slice_screen', 'p1', (398, 525, 520, 655)),
    ('wheel_core', 'icon_burst', 'p1', (492, 400, 580, 488)),
    ('wheel_core', 'icon_shield', 'p1', (492, 592, 580, 680)),
    ('wheel_core', 'icon_turret', 'p1', (572, 545, 662, 635)),
    ('wheel_core', 'icon_repair', 'p1', (410, 448, 500, 538)),
    ('wheel_core', 'slice_hp_bars', 'p1', (588, 408, 700, 540)),
    ('wheel_core', 'slice_break_x', 'p1', (590, 480, 660, 545)),
    ('wheel_core', 'threat_trim', 'p1', (520, 382, 692, 470)),
    ('wheel_core', 'hp_ring', 'p1', (430, 655, 645, 708)),
    ('wheel_core', 'codebase_frame', 'p1', (372, 380, 470, 520)),
    ('wheel_core', 'nudge_ghost', 'p1', (478, 352, 594, 396)),
    ('wheel_core', 'gun_tracers', 'p1', (630, 600, 760, 700)),
    ('wheel_core', 'gun_tracer_burst_pair', 'p1', (350, 580, 420, 630)),
    ('wheel_core', 'brace_plate', 'p2', (555, 535, 685, 665)),
    ('wheel_core', 'slice_soak_marks', 'p2', (585, 430, 690, 545)),
    # ---------------- wave_rings
    ('wave_rings', 'empty_cell', 'p1', (380, 185, 690, 255)),
    ('wave_rings', 'ring_separators', 'p1', (340, 240, 470, 420)),
    ('wave_rings', 'unit_cell_screen', 'p1', (405, 235, 665, 330)),
    ('wave_rings', 'unit_cell_outline', 'p1', (185, 540, 330, 880)),
    ('wave_rings', 'token_disc', 'p1', (446, 258, 512, 324)),
    ('wave_rings', 'glyph_packet', 'p1', (452, 264, 506, 318)),
    ('wave_rings', 'glyph_worm', 'p1', (634, 368, 698, 432)),
    ('wave_rings', 'glyph_payload', 'p1', (560, 758, 626, 820)),
    ('wave_rings', 'unit_hp_row', 'p1', (420, 238, 660, 300)),
    ('wave_rings', 'chev_solid_stack', 'p1', (500, 268, 572, 322)),
    ('wave_rings', 'chev_hollow', 'p1', (500, 800, 572, 875)),
    ('wave_rings', 'chev_sector_column', 'p1', (496, 680, 576, 880)),
    ('wave_rings', 'armor_cap', 'p1', (290, 590, 470, 790)),
    ('wave_rings', 'warded_mark', 'p1', (700, 476, 746, 522)),
    ('wave_rings', 'dead_x', 'p1', (458, 326, 504, 372)),
    ('wave_rings', 'adjuster_cell', 'p1', (650, 545, 830, 790)),
    ('wave_rings', 'adjuster_diamond', 'p1', (715, 625, 800, 710)),
    ('wave_rings', 'adjuster_hp_bar', 'p1', (735, 555, 830, 760)),
    ('wave_rings', 'ward_arc', 'p1', (612, 540, 708, 685)),
    ('wave_rings', 'consumed_unit', 'p2', (280, 640, 560, 880)),
    ('wave_rings', 'screen_motif_skull', 'p1', (375, 730, 440, 790)),
    # ---------------- outer_rings
    ('outer_rings', 'board_backplate', 'p1', (130, 420, 250, 660)),
    ('outer_rings', 'bezel_ring', 'p1', (138, 430, 200, 650)),
    ('outer_rings', 'bezel_ticks', 'p1', (142, 490, 202, 590)),
    ('outer_rings', 'sector_digits', 'p1', (512, 132, 560, 180)),
    ('outer_rings', 'needle', 'p1', (518, 158, 556, 196)),
    ('outer_rings', 'sched_this_turn', 'p1', (545, 140, 935, 420)),
    ('outer_rings', 'sched_hold_cells', 'p1', (400, 780, 800, 935)),
    ('outer_rings', 'ring_tags', 'p1', (588, 240, 735, 395)),
    ('outer_rings', 'landing_arc_frame', 'p1', (740, 140, 1010, 540)),
    ('outer_rings', 'arc_glyph_disc', 'p1', (750, 164, 800, 214)),
    ('outer_rings', 'arc_wear_mark', 'p1', (786, 195, 816, 224)),
    ('outer_rings', 'arc_now_dot', 'p1', (810, 214, 838, 242)),
    ('outer_rings', 'arc_turn_dots', 'p1', (808, 166, 844, 200)),
    ('outer_rings', 'arc_chevrons', 'p1', (868, 238, 962, 330)),
    ('outer_rings', 'arc_diamonds', 'p1', (900, 308, 978, 382)),
    ('outer_rings', 'arc_check', 'p2', (488, 946, 526, 984)),
    ('outer_rings', 'arc_twist_mark', 'p2', (668, 918, 706, 956)),
    ('outer_rings', 'future_wave_arcs', 'p1', (0, 60, 330, 560)),
    ('outer_rings', 'wave_arc_unit_pips', 'p1', (900, 215, 945, 260)),
    ('outer_rings', 'climax_hazard_ticks', 'p1', (720, 40, 900, 170)),
    ('outer_rings', 'wave_tags', 'p1', (618, 10, 718, 88)),
    ('outer_rings', 'sched_chevrons', 'p1', (800, 260, 920, 420)),
    ('outer_rings', 'board_scrim', 'p1', (0, 600, 240, 840)),
    ('wheel_core', 'slice_gutters', 'p1', (440, 470, 632, 612)),
    ('wave_rings', 'unit_screen_bezel', 'p1', (176, 530, 270, 590)),
    # ---------------- top_hud
    ('top_hud', 'header_plate', 'p1', (1060, 8, 1910, 62)),
    ('top_hud', 'header_title', 'p1', (1072, 14, 1392, 58)),
    ('top_hud', 'waves_left', 'p1', (1498, 14, 1842, 58)),
    ('top_hud', 'help_button', 'p1', (1856, 14, 1906, 58)),
    ('top_hud', 'bill_frame', 'p1', (1058, 62, 1910, 274)),
    ('top_hud', 'you_hp_tally', 'p1', (1066, 72, 1400, 132)),
    ('top_hud', 'hero_pair', 'p1', (1404, 70, 1585, 148)),
    ('top_hud', 'eq_row', 'p1', (1064, 136, 1906, 190)),
    ('top_hud', 'eq_labels', 'p1', (1070, 138, 1560, 160)),
    ('top_hud', 'tally_segments', 'p1', (1074, 152, 1300, 180)),
    ('top_hud', 'operators', 'p1', (1290, 150, 1540, 182)),
    ('top_hud', 'empty_socket', 'p1', (1392, 150, 1490, 182)),
    ('top_hud', 'split_row', 'p1', (1064, 186, 1906, 238)),
    ('top_hud', 'route_arrows', 'p1', (1260, 186, 1480, 210)),
    ('top_hud', 'next_row', 'p1', (1064, 238, 1906, 268)),
    ('top_hud', 'plan_pencil_underline', 'p2', (1064, 90, 1400, 142)),
    ('top_hud', 'best_line_tag', 'p2', (1800, 72, 1902, 96)),
    ('top_hud', 'without_twist_row', 'p2', (1420, 238, 1680, 268)),
    ('top_hud', 'option_chips', 'p2', (1058, 276, 1910, 410)),
    ('top_hud', 'chain_strip', 'p3', (1058, 276, 1910, 438)),
    # ---------------- objectives
    ('objectives', 'objectives_frame', 'p1', (1058, 276, 1910, 328)),
    ('objectives', 'star_glyph', 'p1', (1068, 284, 1104, 318)),
    ('objectives', 'win_label', 'p1', (1066, 282, 1150, 320)),
    ('objectives', 'challenge_labels', 'p1', (1166, 282, 1800, 320)),
    ('objectives', 'challenge_tallies', 'p1', (1560, 288, 1800, 312)),
    ('objectives', 'ram_trace_frame', 'p1', (1058, 324, 1910, 378)),
    ('objectives', 'ram_pips', 'p1', (1066, 330, 1262, 372)),
    ('objectives', 'trace_pips', 'p1', (1288, 330, 1556, 372)),
    ('objectives', 'trace_cap_hatch', 'p1', (1506, 332, 1552, 370)),
    ('objectives', 'ends_heat', 'p1', (1578, 330, 1740, 372)),
    ('objectives', 'ram_refund_pop', 'p2', (1120, 455, 1265, 515)),
    # ---------------- cards
    ('cards', 'hand_fan', 'p1', (980, 820, 1615, 1080)),
    ('cards', 'card_frame', 'p1', (988, 836, 1150, 1080)),
    ('cards', 'cost_badge', 'p1', (986, 840, 1038, 892)),
    ('cards', 'art_band', 'p1', (1000, 880, 1145, 975)),
    ('cards', 'card_icon', 'p1', (1046, 890, 1124, 960)),
    ('cards', 'card_multiplier', 'p1', (1238, 896, 1292, 954)),
    ('cards', 'card_title', 'p1', (1012, 974, 1104, 1018)),
    ('cards', 'type_band', 'p1', (1010, 1004, 1148, 1032)),
    ('cards', 'rules_text', 'p1', (1012, 1026, 1146, 1062)),
    ('cards', 'loud_tab', 'p2', (1388, 746, 1474, 792)),
    ('cards', 'loud_tab_resting', 'p1', (1384, 830, 1446, 870)),
    ('cards', 'card_hover_grow', 'p2', (1250, 738, 1482, 1080)),
    ('cards', 'played_liner', 'p3', (1178, 826, 1612, 1080)),
    # ---------------- actions
    ('actions', 'send_it', 'p1', (1650, 962, 1910, 1080)),
    ('actions', 'undo_chip', 'p1', (1736, 916, 1896, 966)),
    ('actions', 'nameplate', 'p1', (16, 962, 340, 1070)),
    ('actions', 'bottom_hint', 'p1', (1690, 1054, 1900, 1080)),
    ('actions', 'hover_tag', 'p2b', (16, 18, 538, 96)),
    ('actions', 'hover_path', 'p2b', (175, 530, 895, 860)),
    ('actions', 'hover_slice_highlight', 'p2b', (380, 380, 700, 700)),
    ('actions', 'hover_focus_dim', 'p2b', (180, 230, 900, 860)),
    ('actions', 'trigger_path', 'p2', (495, 690, 580, 810)),
    ('actions', 'hovered_cell_outline', 'p2b', (640, 530, 900, 800)),
    ('top_hud', 'trig_groups', 'p2', (1064, 138, 1470, 188)),
    ('actions', 'twist_badge', 'p2', (636, 292, 752, 344)),
    ('actions', 'refund_burst', 'p2', (318, 590, 440, 690)),
    ('actions', 'resolve_fire_lines', 'p3', (300, 560, 480, 700)),
    ('actions', 'nowords_variant', 'nw', (1058, 8, 1910, 380)),
    # ---------------- completeness review 2026-11-01 (new and split elements)
    ('wheel_core', 'hub_inner_rings', 'p1', (504, 508, 568, 572)),
    ('wheel_core', 'slice_screen_code_text', 'nw', (400, 430, 500, 540)),
    ('wheel_core', 'slice_pip_lost_harm', 'p1', (630, 420, 700, 510)),
    ('wheel_core', 'slice_pip_lost_soak', 'p2', (630, 440, 692, 520)),
    ('wheel_core', 'gun_result_hit', 'p1', (708, 656, 756, 704)),
    ('wheel_core', 'slice_soak_rim_arc', 'p2', (600, 410, 700, 510)),
    ('wheel_core', 'slice_soak_break_x', 'p2', (598, 486, 658, 546)),
    ('wave_rings', 'unit_screen_code_text', 'p1', (398, 266, 472, 330)),
    ('wave_rings', 'token_lane_base', 'p1', (203, 398, 267, 462)),
    ('wave_rings', 'token_halo', 'p1', (622, 356, 712, 444)),
    ('wave_rings', 'trigger_killed_unit', 'p2', (300, 560, 460, 700)),
    ('outer_rings', 'backdrop_grade', 'p1', (1150, 420, 1910, 820)),
    ('outer_rings', 'bezel_rim_lines', 'p1', (130, 380, 220, 700)),
    ('outer_rings', 'sector_digits_nowords', 'nw', (512, 132, 560, 180)),
    ('outer_rings', 'ring_tags_nowords', 'nw', (588, 240, 735, 395)),
    ('outer_rings', 'arc_soak_chevron', 'p2', (905, 342, 945, 382)),
    ('outer_rings', 'arc_brace_glyph', 'p2', (865, 765, 901, 801)),
    ('top_hud', 'hero_nowords_proxy', 'nw', (1400, 72, 1600, 150)),
    ('top_hud', 'option_plan_glyphs', 'p2', (1066, 280, 1240, 410)),
    ('top_hud', 'option_name_label', 'p2', (1248, 280, 1420, 410)),
    ('top_hud', 'option_outcome_bar', 'p2', (1458, 280, 1620, 410)),
    ('top_hud', 'option_pair', 'p2', (1820, 280, 1906, 410)),
    ('top_hud', 'chain_step_discs', 'p3', (1064, 280, 1110, 440)),
    ('top_hud', 'chain_step_glyphs', 'p3', (1100, 280, 1150, 440)),
    ('top_hud', 'chain_step_names', 'p3', (1140, 280, 1270, 440)),
    ('top_hud', 'chain_result_tallies', 'p3', (1310, 300, 1520, 400)),
    ('top_hud', 'chain_result_prose', 'p3', (1310, 280, 1620, 440)),
    ('top_hud', 'terminal_plate_kit', 'p1', (1064, 136, 1300, 190)),
    ('top_hud', 'hud_scrim', 'p1', (1040, 360, 1910, 840)),
    ('top_hud', 'layout_grid', 'p2', (1000, 0, 1920, 560)),
    ('objectives', 'ram_trace_labels', 'p1', (1066, 334, 1340, 368)),
    ('cards', 'card_header_strip', 'p1', (988, 836, 1440, 885)),
    ('cards', 'cards_nowords', 'nw', (980, 820, 1615, 1080)),
    ('actions', 'sticker_material', 'p1', (16, 962, 250, 1070)),
    ('actions', 'stickers_nowords', 'nw', (1640, 910, 1910, 1080)),
    ('actions', 'hover_dim_overlay', 'p2b', (700, 120, 1010, 540)),
    ('actions', 'refund_token', 'p2', (340, 590, 440, 660)),
]


def main():
    ims = {k: Image.open(SRC + v).convert('RGB') for k, v in P.items()}
    by = {}
    for cl, eid, pl, box in E:
        c = ims[pl].crop(box)
        k = 1
        while max(c.width, c.height) * k < 240:
            k += 1
        if k > 1:
            c = c.resize((c.width * k, c.height * k), Image.NEAREST)
        fn = '%s__%s.png' % (cl, eid)
        c.save(OUT + fn)
        by.setdefault(cl, []).append((eid, pl, c))
    try:
        font = ImageFont.truetype('arial.ttf', 16)
    except Exception:
        font = ImageFont.load_default()
    for cl, items in by.items():
        cell = 300
        cols = 5
        rows = (len(items) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * cell, rows * (cell + 24)), (24, 24, 30))
        d = ImageDraw.Draw(sheet)
        for i, (eid, pl, c) in enumerate(items):
            t = c.copy()
            t.thumbnail((cell - 8, cell - 8))
            x, y = (i % cols) * cell, (i // cols) * (cell + 24)
            sheet.paste(t, (x + 4, y + 4))
            d.text((x + 4, y + cell + 2), '%s (%s)' % (eid, pl), fill=(230, 230, 230), font=font)
        sheet.save(OUT + 'contact_%s.jpg' % cl, quality=88)
    print('crops', len(E))


if __name__ == '__main__':
    main()
