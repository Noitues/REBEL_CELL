#!/bin/bash
# usage: rt.sh KIND CELK GSTR : re-render full + nog raw maps for the ratio test (HQ pass kept)
cd /d/rc_scratch/solace_v1/garden
k=$1; CK=$2; GS=$3; TG=${4:-20,-44,36}; SC=${5:-270}
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
S=D:/rc_art/art-pass/docs/concepts/solace_vertical/garden/scripts
CAM=$(python -c "import math;t=[float(v) for v in '$TG'.split(',')];e=math.radians(38);a=math.radians(-135);print('%.2f,%.2f,%.2f,%.1f,%.1f,%.1f'%(t[0]+math.cos(e)*math.cos(a)*900,t[1]+math.cos(e)*math.sin(a)*900,t[2]+math.sin(e)*900,*t))")
COMMON="--dir D --park 1 --plinth 1 --garden $k --size 1920x1080 --scale $SC --cam $CAM --gdetail 1 --celk $CK --gstr $GS"
"$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map --out out/r${k}_full_raw.png > scratch/r_full.log 2>&1
"$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map --nohelix 1 --out out/r${k}_noh_raw.png > scratch/r_noh.log 2>&1
"$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map --gvis 0 --out out/r${k}_nog_raw.png > scratch/r_nog.log 2>&1
