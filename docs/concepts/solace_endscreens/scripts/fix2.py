import re
p = 'D:/rc_art/art-pass/docs/concepts/solace_endscreens/scripts/d1_specimen.py'
s = open(p, encoding='utf-8').read()
BS = chr(92)


def rep(m):
    return "'" + m.group(1).replace('\n', BS + 'n') + "'"


s = re.sub(r"'([^'\n]*\n[^']*)'", rep, s)
open(p, 'w', encoding='utf-8').write(s)
