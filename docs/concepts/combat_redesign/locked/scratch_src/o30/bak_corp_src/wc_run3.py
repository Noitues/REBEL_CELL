import sys, json
sys.dont_write_bytecode=True
import wc_run2 as R
R.run3(set(sys.argv[1:]))
json.dump(R.RES, open('D:/rc_scratch/e10_design/wheel_core/res3.json','w'), indent=1)
