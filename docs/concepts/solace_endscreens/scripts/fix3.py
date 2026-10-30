p = 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/scripts/d1_specimen.py'
s = open(p, encoding='utf-8').read()
BS = chr(92)
s = s.replace(BS + 'n', '\n')
lines = s.split('\n')
out = []
i = 0
while i < len(lines):
    ln = lines[i]
    # a postit string opened but not closed on this line
    while ln.lstrip().startswith('postit(') and ln.count("'") % 2 == 1 and i + 1 < len(lines):
        i += 1
        ln = ln + BS + 'n' + lines[i]
    out.append(ln)
    i += 1
open(p, 'w', encoding='utf-8').write('\n'.join(out))
