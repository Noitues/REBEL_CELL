s = open('render_all.py', encoding='utf-8').read()
s = s.replace("X0, Y0, X1, Y1 = 800, 730, 1700, 1080", "X0, Y0, X1, Y1 = 800, 690, 1700, 1080")
a = s.index("    h1 = hand(1)\n    h2 = hand(2)")
b = s.index("    im.save(OUT + 'hand_p1.jpg'")
new = '''    h1 = hand(1)
    h2 = hand(2)
    hl = hand(1, lift='Trigger')
    W = h2.width
    H = 100 + h1.height + 40 + h2.height + 20
    im = Image.new('RGB', (W, H), (30, 26, 40))
    d = ImageDraw.Draw(im)
    lab(d, (20, 12), 'P1 HAND on the bio cutaway: Brace / Spin 3 / Trigger / Twist (decide beat). 1x = real 1920x1080 pixels; 2x below.', 24)
    lab(d, (20, 62), '1x   decide beat (all four at 88 percent value)', 20)
    lab(d, (940, 62), '1x   Trigger lifted (1.10 x, full value, pink print, the rest pushed 30 px)', 20)
    y = 96
    im.paste(h1.convert('RGB'), (0, y)); im.paste(hl.convert('RGB'), (900, y)); y += h1.height + 10
    lab(d, (20, y), '2x', 22); y += 30
    im.paste(h2.convert('RGB'), (0, y))
'''
s = s[:a] + new + s[b:]
s = s.replace("H = 100 + h1.height + 40 + h2.height + 20", "H = 100 + h1.height + 40 + h2.height + 20")
open('render_all.py', 'w', encoding='utf-8').write(s)
