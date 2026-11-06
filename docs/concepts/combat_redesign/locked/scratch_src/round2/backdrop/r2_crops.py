"""r2_crops.py <folder> [names]  -- crops for looking at the backdrop plates: the room under the HUD at 1:1 (x 1060-1920, y 540-1080),
the seam / street at the box's left edge at 2x (x 1040-1340, y 560-860), and the left city at 1:1 (x 0-420, y 0-1080).  Writes
round2/backdrop/work/crops/<name>_{room,seam,city}.png."""
import sys, os
sys.dont_write_bytecode = True
from PIL import Image
D = sys.argv[1].rstrip('/') + '/'
OUT = 'D:/rc_scratch/combat_redesign/locked/round2/backdrop/work/crops/'
os.makedirs(OUT, exist_ok=True)
names = sys.argv[2].split(',') if len(sys.argv) > 2 else sorted(f[:-4] for f in os.listdir(D) if f.startswith('p1_') and f.endswith('.png'))
for n in names:
    im = Image.open(D + n + '.png').convert('RGB')
    im.crop((1060, 540, 1920, 1080)).save(OUT + n + '_room.png')
    s = im.crop((1040, 560, 1340, 860))
    s.resize((600, 600), Image.NEAREST).save(OUT + n + '_seam.png')
    im.crop((0, 0, 420, 1080)).save(OUT + n + '_city.png')
    print(n)
