"""bd2_show.py : print the solved per-room numbers of work/bd2_params.json"""
import sys, json
sys.dont_write_bytecode = True
J = json.load(open('D:/rc_scratch/combat_redesign/locked/backdrop/work/bd2_params.json'))
for k, P in J.items():
    print('%-14s tone_lo %.4f tone_hi %.3f ceil %.3f chroma %.3f contrast %.2f pink %.2f spill %s %s' % (
        k, P['tone_lo'], P['tone_hi'], P['ceil'], P['chroma'], P['contrast'], P['pink_chroma'], P['spill_rgb'],
        'corp light %s->%s x%s' % (P['hue_lo'], P['hue_to'], P['hue_amt']) if P.get('hue_amt') else ''))
