p = "versions.py"
s = open(p, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)
rep("""    a = -30.0
    slot_angles = []
""", """    if boss and version == 2:  # back plate of the outer program ring first (it repaints the centre)
        RW.ring_base(canvas, ss, 412 - 6, 476 + 4, (0.03, 0.03, 0.04), acc, rim=1.2)
        RW.ring_base(canvas, ss, R_OUT + 1, R1, (0.025, 0.03, 0.04), acc, rim=1.4)
    a = -30.0
    slot_angles = []
""")
rep("""        RW.ring_base(canvas, ss, r_in2 - 6, r_out2 + 4, (0.03, 0.03, 0.04), acc, rim=1.2)
""", "")
rep('fs = f_ui(int(11 * ss), b"Bold Condensed")\n            lines = txt.split', 'fs = f_ui(int(15 * ss), b"Bold Condensed")\n            lines = txt.split')
rep("h = len(lines) * 12 * ss + 8 * ss", "h = len(lines) * 16 * ss + 8 * ss")
rep("ds.text((8 * ss, 5 * ss + i * 12 * ss), l", "ds.text((8 * ss, 4 * ss + i * 16 * ss), l")
rep('st = glyph_rgba("ZERO-DAY", int(30 * ss)', 'st = glyph_rgba("ZERO-DAY", int(38 * ss)')
open(p, "w", encoding="utf-8").write(s)
print("ok")
