import sys
from PIL import Image
# usage: squint.py in.png out.png  -> 320 px wide box-downsample, bicubic back up to 960 wide
im = Image.open(sys.argv[1]).convert("RGB")
w, h = im.size
s = im.resize((320, round(320 * h / w)), Image.BOX)
s.resize((960, round(960 * h / w)), Image.BICUBIC).save(sys.argv[2])
