"""Remove this round's scratch/ folder and the script caches. python clear_scratch.py"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (os.path.join(ROOT, "scratch"), os.path.join(HERE, "__pycache__"), os.path.join(HERE, "lib17", "__pycache__")):
    if os.path.isdir(p) and os.path.abspath(p).startswith(ROOT):
        shutil.rmtree(p)
        print("removed", p)
