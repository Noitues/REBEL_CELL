"""crops.py: cut 1x crops (and whole-sheet thumbnails) from published files into round2/docs/work/crops/ for viewing.
usage: python crops.py"""
import os
from PIL import Image

LOCK = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/'
OUT = 'D:/rc_scratch/combat_redesign/locked/round2/docs/work/crops/'
os.makedirs(OUT, exist_ok=True)
JOBS = [
    ('final/grey_proof.jpg', None, 'grey_proof_thumb.jpg', 1400),
    ('final/p2_preview.png', (1060, 560, 1920, 1080), 'p2_hand_1x.png', None),
    ('final/p2_preview.png', (0, 0, 1072, 1080), 'p2_board_half.jpg', 900),
    ('final/p2b_hover_solace.png', (0, 0, 1072, 1080), 'p2b_solace_board.jpg', 900),
    ('hover/h02_brace.png', (1060, 640, 1920, 1080), 'h02_hand_1x.png', None),
    ('hover/h04_twist.png', (0, 0, 1080, 1080), 'h04_board.jpg', 900),
    ('effects/fx_M_motion.png', None, 'fx_M_thumb.jpg', 1600),
    ('effects/fx_P_protect.png', None, 'fx_P_thumb.jpg', 1600),
    ('effects/resolve_beat_strip.jpg', None, 'beat_thumb.jpg', 1600),
]
for src, box, name, w in JOBS:
    im = Image.open(LOCK + src).convert('RGB')
    print(src, im.size)
    if box:
        im = im.crop(box)
    if w and im.size[0] > w:
        im = im.resize((w, round(im.size[1] * w / im.size[0])), Image.LANCZOS)
    im.save(OUT + name, quality=90)
    print('  ->', name, im.size)
