p = 'hv_checks.py'
s = open(p, encoding='utf-8').read()
s = s.replace("over = dil(pen_all | focus | hover | ghost | inset | hand | stick | g(M, 'Y__you') & False, 2)", "over = dil(pen_all | focus | hover | ghost | inset | hand | stick, 2)", 1)
s = s.replace("        return dict(pass_=False, why='no geometry captured')\n", "        return dict(pass_=False, why='no geometry captured'), None\n", 1)
s = s.replace("you_needed=you_needed if False else you_need,", "you_needed=you_need,", 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
