p='mk_nr_city.py'
s=open(p,encoding='utf-8').read()
s=s.replace('''rep("def ink_t(cx, cy, cz, k=1.0):\n", "def ink_t(cx, cy, cz, k=1.0):\n    if INK_FIXED[0] is not None:\n        return max(0.03, INK_FIXED[0] * INK_PX * k)\n")''',
'''rep("def ink_t(cx, cy, cz, k=1.0):\n", "def ink_t(cx, cy, cz, k=1.0):\n    if XF[0]:\n        c_, s_, tx_, ty_, tz_ = XF[0]\n        cx, cy, cz = cx * c_ - cy * s_ + tx_, cx * s_ + cy * c_ + ty_, cz + tz_\n    if INK_FIXED[0] is not None:\n        return max(0.03, INK_FIXED[0] * INK_PX * k)\n")
rep("u = mn('DIVIDE', u, 0.95); v = mn('DIVIDE', sep.outputs['Z'], 1.25)", "u = mn('DIVIDE', u, 0.95 * WS); v = mn('DIVIDE', sep.outputs['Z'], 1.25 * WS)")
s_ = None''')
s=s.replace("s += '\n' + open(base","s = s.replace('INK_JIT = random.Random(99)', \"INK_JIT = random.Random(99)\nWS = float(os.environ.get('NR_WINSCALE', '1.0'))\", 1)\ns += '\n' + open(base")
open(p,'w',encoding='utf-8').write(s)
