"""ed_gantt2.py: the header half of ed_gantt.py by line (the string match failed on quoting): the 'Board:' line wraps"""
P = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/src/mp_sheets.py'
L = open(P, encoding='utf-8').read().split('\n')
i = [k for k, l in enumerate(L) if "d.text((40, y + 6), 'Board:" in l]
assert len(i) == 1
i = i[0]
assert L[i + 1].strip().startswith("font=font('mono', 14)") and L[i + 2].strip() == 'hdr = hdr.crop((0, 0, SW, y + 36))', (L[i + 1], L[i + 2])
L[i] = L[i].replace("d.text((40, y + 6), 'Board:", "y = wrap(d, (40, y + 6), 'Board:")
L[i + 1] = "                 font('mono', 14), (150, 150, 170), SW - 80)"
L[i + 2] = '        hdr = hdr.crop((0, 0, SW, y + 16))'
open(P, 'w', encoding='utf-8').write('\n'.join(L))
print('ok')
