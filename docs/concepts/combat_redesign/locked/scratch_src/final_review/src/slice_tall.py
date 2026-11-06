"""Slice a tall sheet into horizontal bands of height H (no resampling).
Usage: python slice_tall.py <img> <tag> <H>"""
import sys, os
from PIL import Image

OUT = 'D:/rc_scratch/combat_redesign/locked/final_review/after_view'
im = Image.open(sys.argv[1]).convert('RGB')
tag, H = sys.argv[2], int(sys.argv[3])
i = 0
for y in range(0, im.height, H):
    p = os.path.join(OUT, f'{tag}_{i}.jpg')
    im.crop((0, y, im.width, min(im.height, y + H))).save(p, quality=90)
    print(p, im.width, min(im.height, y + H) - y)
    i += 1
