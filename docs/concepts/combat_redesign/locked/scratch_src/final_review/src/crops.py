"""Cut 1x crops (no resampling) from a plate. Usage:
python crops.py <image> <tag> x0,y0,x1,y1 [x0,y0,x1,y1 ...]
Writes final_review/crops/<tag>_<i>.png. Optional 'grey' as tag suffix writes luma too."""
import sys, os
from PIL import Image

OUT = 'D:/rc_scratch/combat_redesign/locked/final_review/crops'

def main():
    src, tag = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert('RGB')
    os.makedirs(OUT, exist_ok=True)
    for i, box in enumerate(sys.argv[3:]):
        b = tuple(int(v) for v in box.split(','))
        c = im.crop(b)
        p = os.path.join(OUT, f'{tag}_{i}.png')
        c.save(p)
        print(p, c.size)

if __name__ == '__main__':
    main()
