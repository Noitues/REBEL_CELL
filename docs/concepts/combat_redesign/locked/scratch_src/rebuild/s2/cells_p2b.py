"""cells_p2b.py <beat> <corp> : print the cell-contrast rows and the value-order table of one published rebuild plate"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_checks as RC
import rb_set as RS

beat, corp = sys.argv[1], sys.argv[2]
nm = RS.plate_name(beat, corp)
r = RC.run(nm, RS.BOARD + nm + '.png', RS.sfx(beat, corp))
for row in r['a_cell_contrast']['rows']:
    print(row['ring'], row['sector'], row['kind'], row['state'], 'occL', row['occ_L'], 'ratio', row['ratio'], 'px', row['px'])
print(RC.table_order(r))
print(r['b_value_order']['failures'])
print(r['b_value_order'].get('probes'))
