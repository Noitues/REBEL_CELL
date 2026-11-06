"""ed_loud3.py: third loudness pass on mp_eff.py (hold arrow stub, brace bar, soak funnel width), review 2.10"""
P = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_eff.py'
s = open(P, encoding='utf-8').read()
pairs = [
    ("        head = 12 + 38 * e_out3(seg(t, 100, 240))\n        clock_arrow(L, arc_pts(426.5, 12, head), AW, AH, int(255 * (1 - seg(t, 420, 560))))",
     "        head = 12 + 38 * e_out3(seg(t, 100, 240))\n        clock_arrow(L, arc_pts(426.5, max(12.0, head - ARROW_STUB['hold']), head), AW, AH, int(255 * (1 - seg(t, 420, 560))))"),
    ("rings=32.0)", "rings=32.0, hold=22.0)"),
    ("        bar = sc(band_pts(bar_r - 3.0, bar_r + 4.0, A - 7.0, A + 7.0, 0.5))", "        bar = sc(band_pts(bar_r - 2.0, bar_r + 3.0, A - 7.0, A + 7.0, 0.5))"),
    ("    mouth_r, apex_r, mouth_h = 204.0, 158.0, 26.0", "    mouth_r, apex_r, mouth_h = 204.0, 158.0, 32.0"),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
