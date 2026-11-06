import re
p = 'hv_comp.py'
s = open(p, encoding='utf-8').read()
a = s.index('# ================================================================================================ the hand (2.6), searched per plate')
b = s.index('def hand_draw(')
new = open('hl_new.txt', encoding='utf-8').read()
s = s[:a] + new + '\n\n' + s[b:]
open(p, 'w', encoding='utf-8').write(s)
print('patched')
