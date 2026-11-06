"""splice_grade.py : replace bd_grade.grade() (from 'def grade(bare, P):' to its 'return np.clip(a * 255.0, 0, 255)') with grade_body.py"""
import sys
sys.dont_write_bytecode = True
F = 'D:/rc_scratch/combat_redesign/locked/corp/src/bd_grade.py'
s = open(F).read()
a = s.index('def grade(bare, P):')
end_tok = '    return np.clip(a * 255.0, 0, 255)\n'
b = s.index(end_tok, a) + len(end_tok)
body = open('D:/rc_scratch/combat_redesign/locked/rebuild/s2/grade_body.py').read()
s = s[:a] + body + s[b:]
open(F, 'w').write(s)
print('spliced', a, b)
