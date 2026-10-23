#!/bin/bash
# the cel maps (Eevee) + ratio passes, run under gpu_run.py (the lock helper). usage: maps.sh [TARGET] [SCALE]
cd /d/rc_scratch/solace_v1/garden
TG=${1:-20,-44,36}; SC=${2:-270}
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
S=D:/rc_art/art-pass/docs/concepts/solace_vertical/garden/scripts
CAM=$(python -c "import math;t=[float(v) for v in '$TG'.split(',')];e=math.radians(38);a=math.radians(-135);print('%.2f,%.2f,%.2f,%.1f,%.1f,%.1f'%(t[0]+math.cos(e)*math.cos(a)*900,t[1]+math.cos(e)*math.sin(a)*900,t[2]+math.sin(e)*900,*t))")
declare -A CK=([A]=0.45 [B]=0.5 [C]=0.62)
for k in A B C; do
  COMMON="--dir D --park 1 --plinth 1 --garden $k --size 1920x1080 --scale $SC --cam $CAM --gdetail 1 --celk ${CK[$k]} --gstr ${CK[$k]}"
  "$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map --out out/M_${k}_raw.png > scratch/M_${k}_raw.log 2>&1
  "$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode ink --out out/M_${k}_ink.png > scratch/M_${k}_ink.log 2>&1
  grep -h "RENDER_SECONDS" scratch/M_${k}_raw.log scratch/M_${k}_ink.log
  python $S/ink.py out/M_${k}_raw.png out/M_${k}_ink.png out/M_${k}_inked.png 2.6 && python $S/post.py map out/M_${k}_inked.png out/M_${k}_map.png
  "$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map --out out/r${k}_full_raw.png > scratch/r_full.log 2>&1
  "$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map --gvis 0 --out out/r${k}_nog_raw.png > scratch/r_nog.log 2>&1
  "$BL" --factory-startup -b --python $S/sd_main.py -- $COMMON --mode map --nohelix 1 --out out/r${k}_noh_raw.png > scratch/r_noh.log 2>&1
done
echo MAPS_DONE
