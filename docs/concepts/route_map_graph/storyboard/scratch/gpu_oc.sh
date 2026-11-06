#!/bin/bash
# GPU queue protocol (D:\rc_scratch\GPU_QUEUE.md): one lock per job; designer override 16:40: never take the lock while
# GPU_WAITING_new_corps exists (new_corps' one block goes first).
LOCK="D:/rc_scratch/GPU_LOCK"
WAIT="D:/rc_scratch/GPU_WAITING_storyboard"
SB="C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass/docs/concepts/route_map_graph/storyboard/scripts"
touch "$WAIT"
while true; do
  if [ ! -e "D:/rc_scratch/GPU_WAITING_new_corps" ] && ( set -o noclobber; echo "storyboard $(date '+%Y-%m-%d %H:%M:%S') job $*" > "$LOCK" ) 2>/dev/null; then
    break
  fi
  sleep 60
done
rm -f "$WAIT"
echo "START $* $(date +%T)"
cd "$SB" && python sb_ocjobs.py "$@"
echo "END $* $(date +%T)"
rm -f "$LOCK"
