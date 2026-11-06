"""tune_red.py: reduce-motion flash count of shield_block / brace_block (neutral, MPST boxes) for candidate fade timings"""
import sys, math, json
sys.dont_write_bytecode = True
import fx_eff as E
from fxlib import flash_check
cands = {
 'lin300': (dict(fin=(0, 120), fout=(620, 920), ease='lin', shadow=1.0), dict(fin=(0, 120), fout=(760, 1060), ease='lin', shadow=1.0)),
 'lin260': (dict(fin=(0, 120), fout=(660, 920), ease='lin', shadow=1.0), dict(fin=(0, 120), fout=(800, 1060), ease='lin', shadow=1.0)),
 'sh30': (dict(fin=(0, 100), fout=(600, 760), ease='out3', shadow=0.3), dict(fin=(0, 120), fout=(760, 920), ease='out3', shadow=0.3)),
 'sh0': (dict(fin=(0, 100), fout=(600, 760), ease='out3', shadow=0.0), dict(fin=(0, 120), fout=(760, 920), ease='out3', shadow=0.0)),
 'late': (dict(fin=(0, 120), fout=(1000, 1300), ease='lin', shadow=1.0), dict(fin=(0, 120), fout=(1000, 1300), ease='lin', shadow=1.0)),
 'chev': (dict(fin=(0, 100), fout=(600, 760), ease='out3', chev_out=(260, 320)), dict(fin=(0, 120), fout=(760, 920), ease='out3', chev_out=(480, 560))),
 'chevio': (dict(fin=(0, 160), fout=(600, 900), ease='io3', chev_out=(260, 360)), dict(fin=(0, 160), fout=(760, 1060), ease='io3', chev_out=(480, 580))),
 'step4': (dict(fin=(0, 100), fout=(600, 760), ease='out3'), dict(fin=(0, 120), fout=(760, 920), ease='out3')),
 'io300': (dict(fin=(0, 300), fout=(620, 920), ease='io3'), dict(fin=(0, 300), fout=(760, 1060), ease='io3')),
 'io400': (dict(fin=(0, 400), fout=(520, 920), ease='io3'), dict(fin=(0, 400), fout=(660, 1060), ease='io3')),
}
names = sys.argv[1:] or list(cands)
for nm in names:
    rs, rb = cands[nm]
    E.RED_SHIELD.update(rs); E.RED_BRACE.update(rb)
    for fid in ('fx_shield_block', 'fx_brace_block'):
        s = E.FX[fid]
        tot = max(s['timing']['total'], rs['fout'][1], rb['fout'][1])
        n = int(math.ceil((tot + 100) * 60 / 1000.0)) + 1
        fr = [s['render'](i * 1000.0 / 60, 'neutral', True) for i in range(n)]
        f = flash_check(fr)
        print(nm, fid, 'reduce flashes', f['flashes'], 'max/s', f['max_flashes_per_s'], 'events', f['region_events'], 'frames', f['flash_frames'], 'up/down', f['max_area_swing_up'], f['max_area_swing_down'], flush=True)
