s = open('asm_checks.py').read()
s = s.replace("extra = [s for s in strs if s not in exp]", "extra = [s for s in strs if s not in exp and s != 'PLAYED']      # PLAYED is the played-slot liner word (p3), not a card field")
open('asm_checks.py','w').write(s)
