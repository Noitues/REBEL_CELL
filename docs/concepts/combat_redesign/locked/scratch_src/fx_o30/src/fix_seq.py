p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/o30_seq.py'
s = open(p, encoding='utf-8').read()
i = s.index('def r_shield_s1(')
j = s.index('def mp_render(')
s = s[:i] + s[j:]
s = s.replace("            base = FL.over(base, FL.shadow(lp, (3, 5), 0.55), pa)", "            base = FL.over(base, FL.shadow(lp, (3, 5), 0.55 * (E.RED_SHIELD.get('shadow', 1.0) if reduce else 1.0)), pa)")
s = s.replace("    import types\n    src_fn = E.shield_render\n    g = dict(src_fn.__globals__)\n\n", "")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
