"""crop8: crop a region of a set 8 plate at 1:1 for inspection.  python crop8.py name x0 y0 x1 y1"""
import sys
from PIL import Image
n, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
Image.open('D:/rc_art/art-pass/docs/concepts/raid_v3/set8/r8_%s.png' % n).crop((x0, y0, x1, y1)).save(
    'D:/rc_tmp/claude/claude/69b3558baa473bbc/4dfa2e73-e058-412d-b93c-b95aedb48b42/scratchpad/crop_%s.png' % n)
