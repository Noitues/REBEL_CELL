"""mk_bdgrade: copy backdrop/src/bd_grade.py into corp/src with the published per-room parameters (backdrop/grade.json) embedded,
plus room_grade(): the default room grade of the generator (O-30 fix 2)."""
import json
SRC = 'D:/rc_scratch/combat_redesign/locked/backdrop/src/bd_grade.py'
DST = 'D:/rc_scratch/combat_redesign/locked/corp/src/bd_grade.py'
GJ = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/grade.json'
g = json.load(open(GJ))
body = open(SRC, encoding='utf-8').read()
rooms = json.dumps(g['rooms'], indent=1, sort_keys=True)
tail = '''

# ------------------------------------------------------------------------------------------------ O-30 fix 2: the default room grade of corp/src
# Per-room parameters as published in locked/backdrop/grade.json (version %s), solved by backdrop/src/bd_solve.py.
GRADE_VERSION = %r
ROOMS = %s


def room_key(path):
    """room_<n>_bare.png -> <n>"""
    import os
    b = os.path.basename(str(path))
    if b.startswith('room_') and b.endswith('_bare.png'):
        return b[5:-9]
    return 'bio'


def room_grade(opt='P'):
    """drop-in for r2_ground.grade(opt): the step-6 grade with the room's own parameters (room taken from the active bare path).
    The board scrim is unchanged (r2_ground.scrim).  Unknown rooms fall back to the bio parameters."""
    import r2_ground as G2
    import o_ground as OG
    path = getattr(OG, 'BARE_PATH', None) or getattr(G2, 'BARE_PATH', None)
    P = ROOMS.get(room_key(path), ROOMS['bio'])
    return grade(G2.bare().astype(np.float32), P)
''' % (g['version'], g['version'], rooms)
open(DST, 'w', encoding='utf-8').write(body.rstrip() + '\n' + tail)
print('ok', DST, list(g['rooms']))
