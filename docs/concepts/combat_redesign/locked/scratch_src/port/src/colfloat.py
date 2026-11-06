"""colfloat: print Godot Color(...) literals for the skin palettes (sRGB 0-255 -> 0-1, 4 decimals). usage: python colfloat.py"""
import sys
sys.dont_write_bytecode = True
C = {
    # neutral
    'n_bed': (9, 11, 15), 'n_panel': (40, 50, 64), 'n_panel_hi': (110, 124, 142), 'n_steel': (116, 128, 144), 'n_line': (188, 200, 214),
    'n_ink': (8, 9, 12), 'n_ticket': (26, 32, 41), 'n_bezel_base': (22, 27, 34), 'n_gloss': (235, 242, 250), 'n_annulus': (8, 11, 16), 'n_arcframe': (26, 33, 42),
    'n_frame': (91, 101, 115),
    # solace
    's_primary': (150, 255, 70), 's_glass': (20, 70, 46), 's_glass_hi': (96, 210, 110), 's_edge': (150, 236, 120), 's_porcelain': (226, 238, 216),
    's_porcelain_d': (150, 176, 150), 's_strand_a': (110, 214, 70), 's_strand_b': (24, 98, 78), 's_nucleus': (226, 120, 160), 's_pale': (236, 248, 226),
    's_groove': (8, 22, 16), 's_ticket': (14, 40, 30), 's_bezel_base': (16, 46, 34), 's_annulus': (8, 26, 20), 's_arcframe': (16, 48, 36), 's_sheen': (220, 255, 220),
    's_frame': (176, 194, 171),
    # meridian
    'm_primary': (255, 140, 26), 'm_steel': (70, 62, 56), 'm_oxide': (150, 76, 26), 'm_edge': (224, 128, 40), 'm_paint': (236, 214, 178),
    'm_hazard_paint': (230, 144, 59), 'm_hazard_b': (20, 15, 12), 'm_rivet': (40, 30, 24), 'm_groove': (10, 8, 7), 'm_ticket': (34, 26, 20),
    'm_trough': (20, 12, 8), 'm_ridge': (255, 206, 150), 'm_bezel_base': (34, 28, 24), 'm_annulus': (26, 20, 16), 'm_arcframe': (40, 24, 14),
    'm_frame': (173, 94, 19),
}
for k, (r, g, b) in C.items():
    print('%-16s #%02X%02X%02X  Color(%.4f, %.4f, %.4f, 1)' % (k, r, g, b, r / 255, g / 255, b / 255))
# token frame fills = mixc(a, b, t)
mix = lambda a, b, t: tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))
print('neutral frame', mix((116, 128, 144), (20, 24, 30), 0.35))
print('solace frame', mix((226, 238, 216), (60, 90, 66), 0.30))
print('meridian frame', mix((255, 140, 26), (60, 30, 10), 0.42))
print('neutral cell edge', mix((188, 200, 214), (12, 14, 18), 0.45))
print('solace cell edge', mix((150, 236, 120), (10, 30, 20), 0.35))
print('meridian cell edge', mix((224, 128, 40), (12, 8, 6), 0.35))
