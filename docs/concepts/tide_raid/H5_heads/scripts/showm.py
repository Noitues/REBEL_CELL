import json,sys
m=json.load(open(sys.argv[1]))
for k,v in m.items():
    if k.endswith('_24') or k.endswith('_32'):
        print(k,'DN',v['iouworst_DN'],'DE',v['iouworst_DE'],'NE',v['iouworst_NE'],'pc',v['pieces_D'],v['pieces_N'],v['pieces_E'],'area',v['area_D'],v['area_N'],v['area_E'],'mot',v['motion_D'],v['motion_N'],v['motion_E'])
