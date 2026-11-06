"""imsize.py <files...>: print image sizes"""
import sys
from PIL import Image
for f in sys.argv[1:]:
    print(Image.open(f).size, f)
