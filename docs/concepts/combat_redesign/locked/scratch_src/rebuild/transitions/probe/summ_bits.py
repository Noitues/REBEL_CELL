"""summ_bits.py: one line per bit stream per skin (C* median, share C* >= 20, L* range, keyline colour), from the published metrics.json."""
import json
m = json.load(open('D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/transitions/metrics.json'))
for s in ('neutral', 'solace'):
    for k, v in m[s]['bits'].items():
        print(s, '%-14s n %3d  srcL %5.1f  bitL %5.1f-%5.1f  C* %5.1f  C20 %4.2f  hue dE %4.2f  key %s' % (
            k, v['n'], v['src_L_median'], v['bit_L_min'], v['bit_L_max'], v['bit_C_median'], v['share_C20'], v['hue_dE_src_vs_bit_max'],
            v.get('keyline_rgb', '')))
