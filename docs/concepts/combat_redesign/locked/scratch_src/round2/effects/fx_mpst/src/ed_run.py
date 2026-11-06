"""ed_run.py: one-off edit of mp_run.py: add the shared gated loudness meter (fxk_lib.loud_frame) next to the brighter-only measure"""
p = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/src/mp_run.py'
s = open(p, encoding='utf-8').read()
pairs = [
    ("import mp_eff as E\nfrom mp_lib import *\n",
     "import mp_eff as E\nfrom mp_lib import *\nsys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/src')\nimport fxk_lib as K      # the C/D/H/L designer's loudness meter (read-only snapshot): one scale for all eight families\n"),
    ("    best['curve'] = curve\n",
     "    best['curve'] = curve\n"
     "    # shared gated meter (review 2.10): px with dE76 > 5 against the marks-off frame AND against the settled frame, weighted by L* / 100\n"
     "    endf = np.clip(post, 0, 255)\n"
     "    g = [K.loud_frame(np.clip(f, 0, 255), np.clip(r, 0, 255), endf) for f, r in zip(frames, refs)]\n"
     "    gi = int(np.argmax([x[0] for x in g]))\n"
     "    best['gated'] = dict(peak=round(g[gi][0], 1), area_px=g[gi][1], t_ms=round(ts[gi], 1), curve=[round(x[0], 1) for x in g])\n"),
    ("loudness peak area x value: full %.0f (%d px at mean L* %.0f), reduce %.0f  |",
     "loudness (shared gated meter) %.0f (%d px), brighter-only %.0f; reduce %.0f  |"),
    ("% (fc['max_flashes_per_s'], fcr['max_flashes_per_s'], ld['av'], ld['area_px'], ld['mean_L'], ldr['av'],",
     "% (fc['max_flashes_per_s'], fcr['max_flashes_per_s'], ld['gated']['peak'], ld['gated']['area_px'], ld['av'], ldr['gated']['peak'],"),
    ("'| loud', ld['av'], ld['area_px'], ld['mean_L'], 'reduce', ldr['av'],",
     "'| loud gated', ld['gated']['peak'], ld['gated']['area_px'], '@', ld['gated']['t_ms'], 'bright', ld['av'], 'reduce gated', ldr['gated']['peak'],"),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
