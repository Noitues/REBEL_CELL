import sys
from PIL import Image, ImageChops, ImageFilter
a = Image.open(sys.argv[1]).convert("RGB"); b = Image.open(sys.argv[2]).convert("RGB"); c = Image.open(sys.argv[3]).convert("RGB")
dab = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 2 else 0)
dil = dab.filter(ImageFilter.MaxFilter(11))
dac = ImageChops.difference(a, c).convert("L").point(lambda v: 255 if v > 2 else 0)
outside = ImageChops.multiply(dac, ImageChops.invert(dil))
h = outside.histogram()
n_out = h[255]
print("pixels moving >2 levels between two OFF renders: %d (animation: traffic, lights, rain)" % dab.histogram()[255])
print("after a 5 px dilation of that animation mask, pixels differing >2 levels between OFF and ON: %d of %d" % (n_out, a.size[0] * a.size[1] - dil.histogram()[255]))
print("OFF vs ON pixels differing >2 inside the animated area: %d" % (dac.histogram()[255] - n_out))
