s = open('lw_ui.py').read()
a = "    xtext(cv, 'Z', 1855, 879, 19, ANTON, fill=WH, rot=-0.6, wob=0.05, seed=9, grain=0.0)\n"
b = "    if nw:\n        cv.paint(poly(cv, [(1862, 872), (1847, 879), (1862, 886), (1862, 882.5), (1854.5, 879), (1862, 875.5)]), WH)      # nowords: an undo chevron on the keycap, no letter\n    else:\n        xtext(cv, 'Z', 1855, 879, 19, ANTON, fill=WH, rot=-0.6, wob=0.05, seed=9, grain=0.0)\n"
assert a in s
open('lw_ui.py','w').write(s.replace(a, b))
