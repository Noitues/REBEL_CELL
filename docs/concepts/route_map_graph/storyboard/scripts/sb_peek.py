"""Storyboard: finish one rendered frame's passes into a plate (no UI) for a look check.
python sb_peek.py <bl_dir> <name> <out> [key=value post overrides]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import post_aaa as PA  # noqa: E402

if __name__ == "__main__":
    bl, name, out = sys.argv[1:4]
    over = {}
    for a in sys.argv[4:]:
        k, _, v = a.partition("=")
        over[k] = json.loads(v)
    PA.finish(bl, "real", shot=name, over=over).save(out)
    print("saved", out)
