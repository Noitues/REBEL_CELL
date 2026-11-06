"""r2_sheet_crop.py <jpg> <x0,y0,x1,y1> <out.png> -- crop a region of a sheet at 1:1 for reading."""
import sys
sys.dont_write_bytecode = True
from PIL import Image
im = Image.open(sys.argv[1])
print(im.size)
im.crop(tuple(int(v) for v in sys.argv[2].split(','))).save(sys.argv[3])
