import re
s = open('card_render.py', encoding='utf-8').read()
old = s[s.index("        pts = [(112, 12), (84, 62)"):s.index("    else:\n        # motion bar")]
new = '''        base = [(0, -10), (5, -10), (1, -1), (7, -1), (-4, 12), (-1, 2), (-7, 2)]
        for (bx, by, sc, rt) in ((142, 40, 2.3, 0.3), (28, 96, 2.1, -0.3)):
            c, sn = math.cos(rt), math.sin(rt)
            m = poly(cv, [(bx + sc * (px * c - py * sn), by + sc * (px * sn + py * c)) for px, py in base])
            cv.paint(extrude(cv, grow(cv, m, 1.6), 2.4, 3.0) * ab, INK)
            cv.paint(grow(cv, m, 1.6) * ab, INK)
            cv.paint(m * ab, hx('F6F3EA'))
'''
s = s.replace(old, new)
s = s.replace("[(8, 104), (CW - 8, 94), (CW - 8, 126), (8, 126)], 1.3", "[(8, 114), (CW - 8, 108), (CW - 8, 126), (8, 126)], 1.3")
s = s.replace("return np.clip(r * cv.R - d + 0.5, 0, 1).astype(np.float32) if False else (d <= r * cv.R).astype(np.float32)", "return (d <= r * cv.R).astype(np.float32)")
open('card_render.py', 'w', encoding='utf-8').write(s)
