import re
p='hq_preset.py'; s=open(p,encoding='utf8').read()
s=s.replace('"leg": (7.0, 12.0), "leg_top": 108.0, "span_z": (84.0, 100.0), "span_half": 7.0','"leg": (7.0, 20.0), "leg_top": 142.0, "span_z": (104.0, 122.0), "span_half": 9.0')
s=s.replace('"keep_top": 128.0','"keep_top": 148.0')
s=s.replace('"steel": (0.105, 0.052, 0.034)','"steel": (0.075, 0.037, 0.024)')
s=s.replace('''[(0.11, 0.045, 0.03), (0.05, 0.065, 0.08), (0.10, 0.07, 0.035), (0.075, 0.03, 0.03),
                      (0.035, 0.05, 0.045)]''','''[(0.078, 0.032, 0.021), (0.035, 0.046, 0.056), (0.07, 0.049, 0.025), (0.052, 0.021, 0.021),
                      (0.025, 0.035, 0.032)]''')
s=s.replace('"streak_k": 6.0','"streak_k": 3.0').replace('"span_down_w": 4.0e4','"span_down_w": 2.8e4')
open(p,'w',encoding='utf8').write(s)
p='meridian_landmark.py'; s=open(p,encoding='utf8').read()
a='        beacon(cx, GY, LTOP + 9.6)\n'
b=a+'''        for (px, py) in ((cx - LHX, y0), (cx + LHX, y0), (cx - LHX, y1), (cx + LHX, y1)):     # rim: sodium-white vertical edges
            box(SEAM, px - 0.3, py - 0.3, WTOP + 6.0, px + 0.3, py + 0.3, LTOP, EDGE, LH["seam_k"] * 1.3)
'''
assert a in s; s=s.replace(a,b,1)
a='    box(SEAM, sx0, sy0 - 0.25, SZ1 - 1.0'
b='''    box(SEAM, sx0, sy0 - 0.3, SZ1 - 0.2, sx1, sy0 + 0.3, SZ1 + 0.4, EDGE, LH["seam_k"] * 1.4)         # rim: the span's top edges
    box(SEAM, sx0, sy1 - 0.3, SZ1 - 0.2, sx1, sy1 + 0.3, SZ1 + 0.4, EDGE, LH["seam_k"] * 1.4)
'''+a
assert a in s; s=s.replace(a,b,1)
open(p,'w',encoding='utf8').write(s)
