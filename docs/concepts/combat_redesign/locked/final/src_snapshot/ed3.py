s=open('sheets.py').read()
a=s.index("    crops = [('NOW ring unit")
b=s.index("    x0, y0 = 780, 118")
s=s[:a]+"""    crops = [('NOW ring (0): outline, chevrons, notch', (535, 738, 180, 140)), ('rings +1 / +2: outline, pips, chevrons', (535, 835, 180, 140)), ('landing arcs, right side', (905, 745, 180, 140)),
             ('tower trim + HP ring', (560, 415, 180, 140)), ('ring tags NOW / +1 / +2', (650, 300, 180, 140)), ('token + cell corner (+2)', (215, 505, 180, 140))]
"""+s[b:]
s=s.replace("cc = crop(pl, cx, cy, w, h, 1.7)","cc = crop(pl, cx, cy, w, h, 2.0)")
s=s.replace("    yy = 680\n    box(d, [780, yy, 1880, 1040], 'rules')","    yy = 700\n    box(d, [780, yy, 1880, 960], 'rules')")
s=s.replace("yy = y0 + (i // 3) * 262","yy = y0 + (i // 3) * 290")
# hp sheet tower position
s=s.replace("put(im, tw, 640, 150 + bgp.height + 30, d, 'tower in situ (1x)')","put(im, tw, 40, 150 + bgp.height + 30 + pbg.height + 34, d, 'tower in situ (1x)')")
s=s.replace("('unit HP tray, pink = our shots (3x)', (300, 545, 170, 100))","('unit HP tray, pink = our shots (3x)', (535, 748, 170, 100))")
open('sheets.py','w').write(s)
