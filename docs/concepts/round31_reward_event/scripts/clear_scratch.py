"""Round 31: remove this round's own scratch folder and bytecode caches (nothing outside round31_reward_event)."""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
assert os.path.basename(ROOT) == "round31_reward_event"
for p in (os.path.join(ROOT, "scratch"), os.path.join(ROOT, "scripts", "__pycache__"), os.path.join(ROOT, "scripts", "lib17", "__pycache__")):
    if os.path.isdir(p):
        shutil.rmtree(p)
        print("removed", p)
