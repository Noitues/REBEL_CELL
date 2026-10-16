#!/bin/sh
# A2 CPU preview (no GPU, no lock): cpu_a2.sh <cam> <res_k> <spp> [aaa|day]
M=${4:-aaa}
P=D:/rc_scratch/city_all_corps/prev_a2
mkdir -p $P
CITY_CPU=1 "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -t 6 --factory-startup --python city_build.py -- $M $1 $P $2 $3 > $P/cpu_$1_$M.log 2>&1
grep -E "TIME|Error|Traceback|line [0-9]+, in" $P/cpu_$1_$M.log | grep -v CUEW
python post_city.py $M $P/$1_$M $P/$1_${M}_cpu.png
