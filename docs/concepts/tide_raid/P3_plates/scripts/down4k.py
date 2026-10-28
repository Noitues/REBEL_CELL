"""plates/ = Lanczos downsample of the native 3840x2160 plates4k/ (supersampled 1080p)."""
import os
from PIL import Image
O = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/'
for f in sorted(os.listdir(O + 'plates4k')):
    Image.open(O + 'plates4k/' + f).convert('RGB').resize((1920, 1080), Image.LANCZOS).save(O + 'plates/' + f)
    print(f)
