p = 'hv_key.py'
s = open(p, encoding='utf-8').read()
old = "    Z.pink_burst(L, x + 240, y + 84, 22, 5)\n    bg.alpha_composite(L.done())"
assert old in s
s = s.replace(old, "    Z.pink_burst(L, x + 240, y + 84, 22, 5)\n    bg.alpha_composite(V.done_box(L))", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
