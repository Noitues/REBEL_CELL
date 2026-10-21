#!/bin/bash
# usage: make_map.sh DIR   (raw cel render + id pass already rendered) -> out/DIR_map.png
cd D:/rc_scratch/solace_v1/district
d=$1
python scripts/ink.py out/${d}_map_raw.png out/${d}_ink.png out/${d}_map_inked.png 2.6 && python scripts/post.py map out/${d}_map_inked.png out/${d}_map.png
