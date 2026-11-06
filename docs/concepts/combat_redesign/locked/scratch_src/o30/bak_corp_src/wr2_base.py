import sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/e10_design/wave_rings/src')
import wr_build as W
FAV = dict(empty_cell='A', ring_separators='B', unit_cell_screen='C', unit_screen_bezel='A', unit_screen_code_text='A', unit_cell_outline='A', token_disc='A', token_lane_base='A',
           token_halo='A', glyph_packet='A', glyph_worm='B', glyph_payload='A', glyph_jammer='B', glyph_ring='C', unit_hp_row='A', chev_solid_stack='A', chev_hollow='B',
           chev_sector_column='A', armor_cap='B', warded_mark='A', dead_x='A', adjuster_cell='A', adjuster_diamond='A', adjuster_hp_bar='A', ward_arc='A', consumed_unit='A',
           trigger_killed_unit='A', screen_motif_skull='A', shield_bracket='A', adjuster_armor_strike='A', ring_unit_wide6='A')
t = time.time()
for b in sys.argv[1:]:
    W.render(b, FAV, hud=False).save('D:/rc_scratch/e10_design/wave_rings/out2/base_r1_%s.png' % b)
    print(b, time.time() - t)
