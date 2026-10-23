#!/bin/bash
# usage: rm2.sh KIND NAME SIZE SCALE TX,TY,TZ [extra]  -- cel map with the camera aimed at a target (raw + ink pass + inked + post -> out/NAME_map.png)
cd /d/rc_scratch/solace_v1/garden
K=$1; N=$2; SZ=$3; SC=$4; TG=$5; shift 5
CAM=$(python -c "import math;t=[float(v) for v in '$TG'.split(',')];e=math.radians(38);a=math.radians(-135);print('%.2f,%.2f,%.2f,%.1f,%.1f,%.1f'%(t[0]+math.cos(e)*math.cos(a)*900,t[1]+math.cos(e)*math.sin(a)*900,t[2]+math.sin(e)*900,*t))")
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
S=D:/rc_art/art-pass/docs/concepts/solace_vertical/garden/scripts
COMMON="--dir D --park 1 --plinth 1 --garden $K --size $SZ --scale $SC --cam $CAM"
"$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map "$@" --out out/${N}_raw.png > scratch/${N}_raw.log 2>&1
"$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode ink "$@" --out out/${N}_ink.png > scratch/${N}_ink.log 2>&1
grep -h "RENDER_SECONDS\|Traceback" scratch/${N}_raw.log scratch/${N}_ink.log
python $S/ink.py out/${N}_raw.png out/${N}_ink.png out/${N}_inked.png 2.6 && python $S/post.py map out/${N}_inked.png out/${N}_map.png
