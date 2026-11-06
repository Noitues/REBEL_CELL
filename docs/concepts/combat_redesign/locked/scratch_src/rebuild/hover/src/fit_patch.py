p = 'hv_core.py'
s = open(p, encoding='utf-8').read()
rep = [("RING_N = (3.0, 3.5, 4.0, 5.0)     #", "RING_N = (3.0, 3.5, 4.0, 5.0, 6.0)     #"),
       ("        for ex in (9, 7, 11, 5, 13, 15, 4, 17):", "        for ex in (9, 7, 11, 5, 6, 13, 15, 4, 17):"),
       ("            for dy in (0, 1, -1, 2, -2):\n                for dx in (0, 1, -1, 2, -2):", "            for dy in (0, 1, -1, 2, -2, 3, 4, -3, 5):\n                for dx in (0, 1, -1, 2, -2, 3, -3):"),
       ("        if Z._quick_hit(pts, RING_HALF + 0.5, forb):", "        if Z._quick_hit(pts, RING_HALF, forb):            # coarse pre-filter; the drawn ring below is the test"),
       ("        if tested > 80:\n            break", "        if tested > 240:\n            break")]
for a, b in rep:
    assert a in s, a
    s = s.replace(a, b, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
