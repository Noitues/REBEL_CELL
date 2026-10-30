"""Contact sheet: each plate as composed + squinted, with the current E10 as the baseline row."""
import sys, json
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/combat_backdrop/scripts')
from bd_common import *
from PIL import ImageDraw, ImageFont

F = ImageFont.truetype('D:/rc_art/art-pass/assets/fonts/ShareTechMono-Regular.ttf', 24)
rows = [('BASELINE  E10 as it is now (old violet city)', None),
        ('1  INTERIOR  Solace bio-lab hall, helix window', 'plate1_interior'),
        ('2  CUTAWAY  the building opened, the lab floor lit', 'plate2_cutaway'),
        ('3  X-RAY SCAN  the Cell\'s holo view of the building', 'plate3_xray')]
tw_, th_ = 944, 531
sheet = Image.new('RGB', (1920, 4 * (th_ + 46) + 60), (8, 10, 18))
d = ImageDraw.Draw(sheet)
d.text((24, 14), 'COMBAT BACKDROP   composed (left) / squint 1/16 blurred (right)   board unchanged', font=F, fill=(150, 255, 70))
y = 56
allstats = []
for title, name in rows:
    if name is None:
        plate = E10
        st = stats(plate, 'E10 baseline')
    else:
        plate = np.asarray(Image.open(OUT + name + '.png').convert('RGB')).astype(np.float32) / 255
        st = stats(plate, name)
    allstats.append(st)
    d.text((24, y), title + f"   [visible backdrop, squinted: mean {st['mean']:.2f}  p95 {st['p95']:.2f}  loud {st['loud']*100:.1f}%]", font=F, fill=(0, 229, 255))
    y += 36
    a = Image.fromarray((plate * 255).astype(np.uint8)).resize((tw_, th_), Image.LANCZOS)
    b = Image.fromarray((squint(plate) * 255).astype(np.uint8)).resize((tw_, th_), Image.LANCZOS)
    sheet.paste(a, (12, y))
    sheet.paste(b, (12 + tw_ + 8, y))
    y += th_ + 10
sheet.save(OUT + 'sheet.jpg', quality=90)
Image.fromarray((squint(E10) * 255).astype(np.uint8)).save(OUT + 'e10_baseline_squint.png')
json.dump(allstats, open(OUT + 'squint_stats.json', 'w'), indent=1)
print(json.dumps(allstats, indent=1))
