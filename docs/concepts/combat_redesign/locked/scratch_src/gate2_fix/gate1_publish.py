"""gate1_publish.py: copy the rebuilt set (locked/rebuild/board/) into locked/final/ and refresh final/src_snapshot (every non-underscore .py of
corp/src, and the backdrop scripts into src_snapshot/backdrop/).  Prints what it copied.  2026-11-04 (gate 1)."""
import os, shutil, glob, sys
sys.dont_write_bytecode = True
BOARD = 'D:/rc_scratch/combat_redesign/locked/rebuild/board/'
FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
SRC = 'D:/rc_scratch/combat_redesign/locked/corp/src/'
BSRC = 'D:/rc_scratch/combat_redesign/locked/backdrop/src/'
n = 0
for f in sorted(os.listdir(BOARD)):
    if f.endswith(('.png', '.jpg', '.json', '.txt')):
        shutil.copyfile(BOARD + f, FINAL + f)
        n += 1
print('plates and sheets copied:', n)
snap = FINAL + 'src_snapshot/'
k = 0
for f in sorted(glob.glob(SRC + '*.py')):
    b = os.path.basename(f)
    if b.startswith('_'):
        continue
    shutil.copyfile(f, snap + b)
    k += 1
print('src_snapshot .py copied:', k)
os.makedirs(snap + 'backdrop/', exist_ok=True)
j = 0
for f in sorted(glob.glob(BSRC + '*.py')):
    b = os.path.basename(f)
    if b.startswith(('bd2_', 'fg_extract', 'bd_measure')):
        shutil.copyfile(f, snap + 'backdrop/' + b)
        j += 1
print('src_snapshot/backdrop copied:', j)
