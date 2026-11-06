"""print the pixel size of each image given"""
import sys
sys.dont_write_bytecode = True
from PIL import Image
for p in sys.argv[1:]:
    print(p, Image.open(p).size)
