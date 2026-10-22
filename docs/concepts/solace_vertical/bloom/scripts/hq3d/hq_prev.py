"""v5 helper: finish one rendered stem (the npy passes) into a plate PNG + value numbers.

python hq_prev.py <stem> <zoom> <out.png> [thumb_max_px]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_post as PO  # noqa: E402
import hq_values as V  # noqa: E402

stem, zoom, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
plate = PO.finish(stem, zoom, t=2.0)
plate.save(out)
print(out, plate.size, V.check(out, stem))
