"""ed_loud2.py: second loudness pass on mp_eff.py (brace stamp, hold stamp, soak funnel, rings stub), review 2.10"""
P = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_eff.py'
s = open(P, encoding='utf-8').read()
pairs = [
    ("        stamp_s = 1.5 - 0.5 * e_back(seg(t, 330, 400), 2.2)", "        stamp_s = 1.2 - 0.2 * e_back(seg(t, 330, 400), 2.2)"),
    ("        q = 9.0 * stamp_s", "        q = 8.0 * stamp_s"),
    ("BR_ARM = 24.0 ", "BR_ARM = 20.0 "),
    ("        R0 = 14.5 * s", "        R0 = 12.5 * s"),
    ("    al = clamp01(seg(t, 0, 40)) * (1 - seg(t, 200, 320))\n", "    al = clamp01(seg(t, 0, 40)) * (1 - seg(t, 120, 220))\n"),
    ("    mouth_r, apex_r, mouth_h = 204.0, 158.0, 17.0", "    mouth_r, apex_r, mouth_h = 204.0, 158.0, 26.0"),
    ("ppx(rr + 3.0, A + w_)], P_STOCK, 1.6)", "ppx(rr + 3.0, A + w_)], P_STOCK, 2.2)"),
    ("rings=40.0)", "rings=32.0)"),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
