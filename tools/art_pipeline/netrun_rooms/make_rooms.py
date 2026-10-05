"""ART-7 3B: builds rooms3b.py from round 36's r32_scene.py (the tower's dressed rooms as node
backdrops), one Blender run per corporation rendering one room per node kind.

    python make_rooms.py            -> writes rooms3b.py next to it
    blender -b --factory-startup --python rooms3b.py -- tower <outdir> room <corp>
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "r32_scene.py"), encoding="utf-8").read()

# The corporation tints the containers (its hue mixed into each family) and the trims.
src = src.replace('''CONT_COLS = [(0.72, 0.18, 0.12), (0.16, 0.36, 0.62), (0.15, 0.5, 0.48), (0.86, 0.42, 0.10), (0.8, 0.78, 0.72), (0.5, 0.52, 0.2)]''',
'''CONT_COLS = [(0.72, 0.18, 0.12), (0.16, 0.36, 0.62), (0.15, 0.5, 0.48), (0.86, 0.42, 0.10), (0.8, 0.78, 0.72), (0.5, 0.52, 0.2)]
CORP = _argv[3] if len(_argv) > 3 else "meridian"
CORP_HUE = {"meridian": (1.0, 0.55, 0.10), "solace": (0.59, 1.0, 0.27), "halcyon": (0.69, 0.43, 1.0),
            "orbital": (0.80, 0.94, 1.0), "rebel_cell": (0.91, 0.08, 0.12)}[CORP]
CORP_MIX = 0.0 if CORP == "meridian" else 0.55
CONT_COLS = [tuple(c * (1 - CORP_MIX) + h * 0.7 * CORP_MIX for c, h in zip(col, CORP_HUE)) for col in CONT_COLS]''')
src = src.replace('''WALLS = len(_argv) > 3 and _argv[3] == "walls"''', '''WALLS = False''')

# The room camera aims at the room picked for the kind being rendered.
src = src.replace('''    if VIEW == "room":  # round 36: the close-up of one dressed room (floor 2, slot 1: a Terminal), as a node backdrop
        return Vector((-7.9, -13.5, 8.9)), Vector((-7.9, 3.0, 8.4)), 24.0''',
'''    if VIEW == "room":  # ART-7 3B: the close-up of the room ROOM_AT = (tier, slot) as a node backdrop
        x0, y0, z0, x1, y1, z1 = room_box(*ROOM_AT)
        cx = (x0 + x1) / 2
        return Vector((cx, y0 - 14.4, z0 + 3.1)), Vector((cx, y0 + 2.1, z0 + 2.6)), 24.0''')

# One room per node kind, each rendered and its passes written as <corp>_<kind>.
a = src.index('base = SCENE_KIND + ("_walls" if WALLS else "")')
src = src[:a] + '''ROOMS_BY_KIND = {"fight": (1, 2), "event": (1, 1), "shop": (2, 0), "elite": (2, 1), "rack": (3, 1)}
for kind, at in ROOMS_BY_KIND.items():
    ROOM_AT = at
    set_cam(-1)
    passes("%s_%s" % (CORP, kind))
print("DONE", flush=True)
'''
open(os.path.join(HERE, "rooms3b.py"), "w", encoding="utf-8").write(src)
print("wrote rooms3b.py")
