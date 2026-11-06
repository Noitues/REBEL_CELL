"""ed_red.py: one-off text edit of mp_eff.py (reduce motion of the P blocks: no hard shadow, 200 ms appear; stock hex in the stills)"""
import sys
sys.dont_write_bytecode = True
p = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_eff.py'
s = open(p, encoding='utf-8').read()
rep = [
    ("RED_FIN, RED_FOUT = (0, 200), (300, 600)        # reduce motion: appear 0-200 linear, hold, dissolve 300-600 linear (tune_red.py: 0-120 counted 2 flashes per s with the hard shadow; 0-200 counts 1)",
     "RED_FIN, RED_FOUT = (0, 200), (300, 600)        # reduce motion: appear 0-200 linear, hold, dissolve 300-600 linear, and no hard offset shadow\n"
     "# (tune_red.py / tune_red2.py: with the shadow the plate's light fill and its dark shadow swing opposite ways at once, 2 flashes per s on\n"
     "#  shield and brace in reduce motion against 1 in full motion; without it both count 1)\n"
     "RED_SHADOW = 0.0"),
    ("        base = over(base, shadow(lp, (3, 5), 0.55), pa)", "        base = over(base, shadow(lp, (3, 5), 0.55 * (RED_SHADOW if reduce else 1.0)), pa)"),
    ("        base = over(base, shadow(lc, (3, 5), 0.55), clamp_al)", "        base = over(base, shadow(lc, (3, 5), 0.55 * (RED_SHADOW if reduce else 1.0)), clamp_al)"),
    ("fill=INK + (int(140 * stamp_al),))", "fill=INK + (int(140 * stamp_al * (RED_SHADOW if reduce else 1.0)),))"),
    ("pink-tinted paper #F7B3D6)", "pink-tinted paper #F6C8DE)"),
    ("appear over 120 ms (linear), hold, and dissolve over 300 ms (linear; a 260 ms dissolve counts 2 flashes, O-30).",
     "appear over 200 ms (linear), hold, and dissolve over 300 ms (linear); no hard shadow in reduce motion (with it the reduce form counted 2 flashes per s, the full form 1)."),
    ("stamp appear over 120 ms, hold, and dissolve over 300 ms;", "stamp appear over 200 ms with no hard shadow, hold, and dissolve over 300 ms;"),
    ("appear over 120 ms with the flow chevrons still, hold, and dissolve over 300 ms.", "appear over 200 ms with the flow chevrons still, hold, and dissolve over 300 ms."),
]
for a, b in rep:
    n = s.count(a)
    assert n == 1, (n, a[:60])
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok', len(rep))
