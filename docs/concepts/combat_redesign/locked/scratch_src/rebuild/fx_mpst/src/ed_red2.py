"""ed_red2.py: one-off edit of mp_eff.py: per-block reduce-motion windows (tune_red3.py: the smaller plate and the clamp brackets of the
review 2.10 pass count 2 flashes per s in reduce motion with the shared 0-200 / 300-600 window; these windows count 1, as full motion)"""
P = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_eff.py'
s = open(P, encoding='utf-8').read()
pairs = [
    ("def _red_k(t):\n    return seg(t, *RED_FIN) * (1 - seg(t, *RED_FOUT))\n",
     "# per block (tune_red3.py, 2026-11-04): appear window, dissolve window; each counts 1 flash per s in reduce motion, as its full motion does\n"
     "RED_WIN = dict(shield=((0, 150), (250, 600)), brace=((0, 300), (300, 600)), soak=((0, 200), (300, 600)))\n\n\n"
     "def _red_k(t, w=None):\n    fin, fout = RED_WIN[w] if w is not None else (RED_FIN, RED_FOUT)\n    return seg(t, *fin) * (1 - seg(t, *fout))\n", 1),
    ("        pa = _red_k(t)\n", "        pa = _red_k(t, 'shield')\n", 1),
    ("        clamp_al = _red_k(t)\n", "        clamp_al = _red_k(t, 'brace')\n", 1),
    ("        k = _red_k(t)\n        fk, wash,", "        k = _red_k(t, 'soak')\n        fk, wash,", 1),
    ("reduce_phases=[('plate, ticks and stopped chevrons appear', 0, 200, 'linear'), ('hold', 200, 300, '-'), ('dissolve', 300, 600, 'linear')]",
     "reduce_phases=[('plate, ticks and stopped chevrons appear', 0, 150, 'linear'), ('hold', 150, 250, '-'), ('dissolve', 250, 600, 'linear')]", 1),
    ("appear over 200 ms (linear), hold, and dissolve over 300 ms (linear); no hard shadow in reduce motion (with it the reduce form counted 2 flashes per s, the full form 1).",
     "appear over 150 ms (linear), hold 100 ms, and dissolve over 350 ms (linear); no hard shadow in reduce motion. Measured: this form counts 1 flash per s, as full motion (the 0-200 / 300-600 form counted 2).", 1),
    ("reduce_phases=[('lane, clamp, bar, crumpled chevrons and stamp appear', 0, 200, 'linear'), ('hold', 200, 300, '-'), ('dissolve', 300, 600, 'linear')]",
     "reduce_phases=[('lane, clamp brackets, bar, crumpled chevrons and stamp appear', 0, 300, 'linear'), ('dissolve', 300, 600, 'linear')]", 1),
    ("stamp appear over 200 ms with no hard shadow, hold, and dissolve over 300 ms;",
     "stamp appear over 300 ms with no hard shadow and dissolve over 300 ms (measured 1 flash per s, as full motion; with a 200 ms appear it counted 2);", 1),
]
for a, b, n in pairs:
    c = s.count(a)
    assert c == n, (c, a[:60])
    s = s.replace(a, b)
open(P, 'w', encoding='utf-8').write(s)
print('ok')
