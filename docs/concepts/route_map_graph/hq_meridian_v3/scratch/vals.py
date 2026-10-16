import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)).replace('scratch','scripts'))
import hq_values as V
for n in ('H_overview','H_decision','H_hover'):
    print(n, V.check(os.path.join('..','plates',n+'_v3_plate.png'), os.path.join(r'D:\rc_scratch\meridian_v3','bl_stills_final',n), os.path.join('..','scratch',n+'_thumb.png')))
