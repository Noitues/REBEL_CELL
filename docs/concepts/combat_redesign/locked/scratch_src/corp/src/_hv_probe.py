import sys; sys.dont_write_bytecode=True
import copy, math
import asm_r2 as A
import a2_hover as H2
A.setup()
f=copy.deepcopy(A.J['f1'])
u=H2.hv_unit(f)
print(u['id'],u['dep'],H2.span(u),H2.anchor_pt(f))
lay,info=A.AS.stack_layer(True,{})
print(info)
print({k:v for k,v in u.items() if k not in ('fate','path','items')})
import asm_units as AU
print([n for n in dir(AU) if 'tok' in n.lower() or 'pos' in n.lower() or 'centre' in n.lower() or 'center' in n.lower()])
print(AU.token_pos(u) if callable(AU.token_pos) else AU.token_pos)
