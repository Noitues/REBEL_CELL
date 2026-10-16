#!/bin/sh
# CPU Cycles preview (no GPU, no lock): cpu_prev.sh <cam> <res_k> <spp>
P=D:/rc_scratch/city_all_corps/prev
CITY_CPU=1 "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -t 3 --factory-startup --python city_build.py -- aaa $1 $P $2 $3 > $P/cpu_$1.log 2>&1
grep -E "TIME|Error|Traceback" $P/cpu_$1.log
python post_city.py aaa $P/$1_aaa $P/$1_aaa_cpu.png
