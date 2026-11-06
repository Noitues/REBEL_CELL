import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_build as W
FAV = dict(empty_cell='A', ring_separators='B', unit_cell_screen='C', unit_screen_bezel='A', unit_screen_code_text='A', unit_cell_outline='A', token_disc='A', token_lane_base='A',
           token_halo='A', glyph_packet='A', glyph_worm='B', glyph_payload='A', glyph_jammer='A', glyph_ring='B', unit_hp_row='A', chev_solid_stack='A', chev_hollow='B',
           chev_sector_column='A', armor_cap='B', warded_mark='A', dead_x='A', adjuster_cell='A', adjuster_diamond='A', adjuster_hp_bar='A', ward_arc='A', consumed_unit='A',
           trigger_killed_unit='A', screen_motif_skull='A', shield_bracket='A', adjuster_armor_strike='A', ring_unit_wide6='A')
D = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/r1/wave_rings/'
for b, n in (('p1', 'full_plate_p1_favourites'), ('p2', 'full_plate_p2_favourites')):
    W.render(b, FAV, hud=True).save(D + n + '.png')
    print(n)
