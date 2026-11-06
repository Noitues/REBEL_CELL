s = open('m2.py').read()
s = s.replace("        near = np.exp(-np.clip(best, 0, None) / 38.0)           # 1 at the front, fades inward",
              "        near = np.exp(-np.clip(best, 0, None) / 38.0)           # 1 at the front, fades inward\n        if k >= 0.9:\n            near = np.maximum(near, 0.30 + 0.35 * n1)          # full Bloom: body stays plum-lit, not black")
s = s.replace("        a = m * k * .78", "        a = m * k * (.78 if k < .9 else .70)")
open('m2.py', 'w').write(s)
