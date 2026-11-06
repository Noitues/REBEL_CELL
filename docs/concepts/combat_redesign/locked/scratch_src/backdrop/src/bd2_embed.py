"""bd2_embed.py : write the solved rb2-1 room table (work/bd2_params.json) into corp/src/bd_grade.py between the ROOMS_RB2 markers,
and copy the resulting bd_grade.py over backdrop/src/bd_grade.py so both pipelines grade with one file."""
import sys, json, shutil
sys.dont_write_bytecode = True
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src/bd_grade.py'
J = json.load(open('D:/rc_scratch/combat_redesign/locked/backdrop/work/bd2_params.json'))
order = ['bio', 'srv', 'gh', 'rec', 'lobby', 'event', 'shop', 'shop_meridian']
missing = [k for k in order if k not in J]
if missing:
    sys.exit('missing keys %s' % missing)
body = json.dumps({k: J[k] for k in order}, indent=1)
s = open(SRC).read()
a = s.index('# >>> ROOMS_RB2')
a = s.index('\n', a) + 1
b = s.index('# <<< ROOMS_RB2')
s = s[:a] + 'ROOMS = ' + body + '\n' + s[b:]
open(SRC, 'w').write(s)
shutil.copyfile(SRC, 'D:/rc_scratch/combat_redesign/locked/backdrop/src/bd_grade.py')
print('embedded', list(J))
