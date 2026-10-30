"""Round 40 v2: re-run 02 dock preview, 13 threat moving, 14 defence fires with LIGHT40=1 as *_v2.gif (others untouched)."""
import os, sys, traceback
from PIL import Image
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
os.environ["NET36"] = "net_scope.json"
VSUF = os.environ.get("VSUF", "_v2")              # _v2: LIGHT40 (superseded); _v3: SOLID40 (translucent views only)
os.environ["LIGHT40" if VSUF == "_v2" else "SOLID40"] = "1"
import screens21 as S
WANT = set(os.environ.get("VWANT", "02_drag_dock_preview.gif,13_threat_moving.gif,14_defence_fires.gif").split(","))
TMP = os.path.join(H, "..", "..", "scratch", "idx")
os.makedirs(TMP, exist_ok=True)


def gif(name, n, fn, dur=90, size=None):
    if name in WANT:
        frames = [S.topil(fn(i / n, i)) for i in range(n)]
        S.save_gif(frames, name.replace(".gif", VSUF + ".gif"), dur, size=size)
    else:
        frames = [Image.new("RGB", size or (640, 360))]
    S.GIF_FRAMES[name] = frames
    return frames


S.gif = gif
which = sys.argv[1:]
if "21" in which:
    try:
        S.build_gifs()
    except Exception:
        traceback.print_exc()
if "23" in which:
    import screens23 as S23
    S23.gif, S23.GIFS, S23.OUT = gif, TMP, TMP
    try:
        S23.build()
    except Exception:
        traceback.print_exc()
print("V2 DONE", flush=True)
