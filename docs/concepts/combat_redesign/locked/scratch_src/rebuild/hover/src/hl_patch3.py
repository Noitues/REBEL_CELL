p = 'hv_comp.py'
s = open(p, encoding='utf-8').read()
a = s.index("    feasible_rest = []\n    for cost, fan, pre, push, rest in rest_opts:")
b = s.index("def hand_draw(")
new = open('hl_new3.txt', encoding='utf-8').read()
s = s[:a] + new + '\n\n' + s[b:]
# helpers before hand_layout
h = open('hl_new3h.txt', encoding='utf-8').read()
i = s.index("def _shifts(")
s = s[:i] + h + '\n\n' + s[i:]
open(p, 'w', encoding='utf-8').write(s)
print('ok')
