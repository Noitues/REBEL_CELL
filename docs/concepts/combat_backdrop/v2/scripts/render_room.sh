#!/bin/bash
# usage: render_room.sh <room_type> <seed> <name> [samples]   -> D:/rc_scratch/cutaway_kit/<name>_{main,refl,mask}.png
BL="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
S=D:/rc_art/art-pass/docs/concepts/combat_backdrop/v2/scripts
O=D:/rc_scratch/cutaway_kit
SM=${4:-12}
for m in main refl mask; do
  "$BL" -b --factory-startup -P $S/bl_scene.py -- $1 $2 $m $O/$3_$m.png $SM > $O/log_$3_$m.txt 2>&1 &
done
wait
echo done $3
