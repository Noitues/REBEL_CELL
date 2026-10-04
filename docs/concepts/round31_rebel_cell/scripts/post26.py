"""Round 26: finish the Blender close-ups (round 11/25 backdrop pass: ink, grime, bloom + light spill, haze, rain)
-> ../scratch/backdrops/rc26_<idea>[_dispatch]_night.png (1920 x 1080). python post26.py [tag ...]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backdrop25 as B

if __name__ == "__main__":
    tags = sys.argv[1:]
    for tag in tags:
        if not os.path.exists(os.path.join(B.SRC, "%s_beauty_night.png" % tag)):
            print("missing", tag)
            continue
        B.finish(tag, "night")
