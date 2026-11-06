"""Nearest-neighbour enlarge a crop for pixel inspection. Usage: python zoom.py <in> <out> <factor>"""
import sys
from PIL import Image

im = Image.open(sys.argv[1]).convert('RGB')
k = int(sys.argv[3])
im.resize((im.width * k, im.height * k), Image.NEAREST).save(sys.argv[2])
print(sys.argv[2], im.width * k, im.height * k)
