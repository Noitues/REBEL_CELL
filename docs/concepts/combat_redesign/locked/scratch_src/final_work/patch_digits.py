"""O-29 fix 2: sector digits drawn above the cells, tape and label plates; digit 0 moved 4.5 deg off the tape start; holes punched in the schedule layer"""
import re
P = 'D:/rc_scratch/combat_redesign/locked/corp/src/'
def sub(fn, a, b):
    s = open(P + fn, newline='').read()
    nl = '\r\n' if '\r\n' in s else '\n'
    a2, b2 = a.replace('\n', nl), b.replace('\n', nl)
    assert s.count(a2) == 1, (fn, a[:50], s.count(a2))
    open(P + fn, 'w', newline='').write(s.replace(a2, b2))
sub('r2_sched.py', "WELL_R = 12.0\n",
    "WELL_R = 12.0\n"
    "DIGIT_ANG = [-4.5, 60.0, 120.0, 180.0, 240.0, 300.0]     # O-29 fix 2: digit 0 sits 4.5 deg before the THIS TURN tape start (sector 0 spans -30..30)\n"
    "DIGIT_GAP = 2.6                                           # px of bezel left clear round each digit boss (holes punched in the schedule layer)\n\n\n"
    "def digit_xy(s):\n"
    "    return ppx(C, DIGIT_R, DIGIT_ANG[s])\n\n\n"
    "def punch_digits(L):\n"
    "    \"\"\"cut a round hole (boss radius + DIGIT_GAP) at every digit in an L2 layer: tape, hold plates and labels never run under a digit\"\"\"\n"
    "    from PIL import ImageDraw as _ID\n"
    "    d = _ID.Draw(L.im)\n"
    "    k = L.k\n"
    "    for s in range(6):\n"
    "        x, y = digit_xy(s)\n"
    "        r = (BOSS_R + DIGIT_GAP) * k\n"
    "        d.ellipse([x * k - r, y * k - r, x * k + r, y * k + r], fill=(0, 0, 0, 0))\n")
sub('r2_sched.py', "        x, y = ppx(C, DIGIT_R, 60 * s)\n        R = BOSS_R if opt",
    "        x, y = digit_xy(s)\n        R = BOSS_R if opt")
# f1_render: digits move to their own layer above the board marks
sub('f1_render.py', "    A.S2.SKIP_LABELS[0] = False\n    A.S2.digits(L, 'P')\n",
    "    A.S2.SKIP_LABELS[0] = False\n")
sub('f1_render.py', "    bg.alpha_composite(Ltag.done())\n    if hover:\n        d = Ld.done()",
    "    bg.alpha_composite(Ltag.done())\n"
    "    Ldg = L2()                       # O-29 fix 2: the sector digits ride above cells, tape, label plates and tags\n"
    "    A.S2.digits(Ldg, 'P')\n"
    "    bg.alpha_composite(Ldg.done())\n"
    "    if hover:\n        d = Ld.done()")
# lw_install: punch the holes in the tape layer and the label layer
sub('lw_install.py', "    _orig_sched(T, sched, sel)\n    _remap(T, True)\n",
    "    _orig_sched(T, sched, sel)\n    _remap(T, True)\n    A.S2.punch_digits(T)\n")
sub('lw_install.py', "    _orig_labels(T, sched, sel)\n    _remap(T, False)\n",
    "    _orig_labels(T, sched, sel)\n    _remap(T, False)\n    A.S2.punch_digits(T)\n")
print('ok')
