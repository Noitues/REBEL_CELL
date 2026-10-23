#!/bin/bash
# usage: rs.sh KIND VIEW NAME SIZE SPP [extra gs_scene args]  -- Cycles frame via the GPU lock helper, then post
cd /d/rc_scratch/solace_v1/garden
K=$1; V=$2; N=$3; SZ=$4; SPP=$5; shift 5
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"
S=D:/rc_art/art-pass/docs/concepts/solace_vertical/garden/scripts
cd $S
python gpu_run.py "$N" "$BL" --factory-startup -b --python $S/gs_scene.py -- --dir $K --view $V --size $SZ --spp $SPP --out D:/rc_scratch/solace_v1/garden/out/$N "$@" > /d/rc_scratch/solace_v1/garden/scratch/$N.log 2>&1
grep -n "Traceback\|Error\|RENDER_SECONDS\|GPU lock\|GPU_RUN\|BUILD" /d/rc_scratch/solace_v1/garden/scratch/$N.log | tail -8
python $S/gs_post.py /d/rc_scratch/solace_v1/garden/out/$N /d/rc_scratch/solace_v1/garden/out/$N.png 2>&1 | tail -2
