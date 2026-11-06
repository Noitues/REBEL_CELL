p = 'hv_checks.py'
s = open(p, encoding='utf-8').read()
old = "    ang = np.degrees(np.arctan2(yy - C[1], xx - C[0])) % 360\n"
assert old in s
s = s.replace(old, "    ang = np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) % 360          # the board's sector angle: 0 = up, clockwise (rb_checks)\n", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
