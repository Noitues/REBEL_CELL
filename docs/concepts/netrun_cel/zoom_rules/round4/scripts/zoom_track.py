"""Usage: python zoom_track.py <dolly log> <dolly frames dir> <out jpg> : parses TRACK lines, prints the stats, draws the target markers on every 6th frame (centre green, end lots magenta)."""
import re
import sys
from PIL import Image, ImageDraw
sys.dont_write_bytecode = True
rows = []
for line in open(sys.argv[1], errors="replace"):
    m = re.match(r"TRACK (\d+) yaw=([-\d.]+) ppb=([-\d.]+) c=\(([-\d.]+), ([-\d.]+)\) e0=\(([-\d.]+), ([-\d.]+)\) e1=\(([-\d.]+), ([-\d.]+)\) ang=([-\d.]+)", line)
    if m:
        rows.append([float(x) for x in m.groups()])
fps = 12.0
yaw = [r[1] for r in rows]
steps = [((yaw[i] - yaw[i - 1] + 180.0) % 360.0) - 180.0 for i in range(1, len(yaw))]
print("frames", len(rows), "max heading change %.2f deg/frame = %.1f deg/s at %d fps" % (max(abs(s) for s in steps), max(abs(s) for s in steps) * fps, fps))
print("centre x drift: max |x-960| = %.1f px; centre y range %.0f..%.0f px; max angle to target %.2f deg" % (max(abs(r[3] - 960.0) for r in rows), min(r[4] for r in rows), max(r[4] for r in rows), max(r[9] for r in rows)))
print("total yaw turn %.1f deg (shortest arc)" % sum(steps))
sel = list(range(0, len(rows), 6)) + ([len(rows) - 1] if (len(rows) - 1) % 6 else [])
w, h = 320, 180
cols = 5
rws = (len(sel) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rws))
for k, i in enumerate(sel):
    im = Image.open("%s/dolly_%03d.jpg" % (sys.argv[2], i)).convert("RGB")
    d = ImageDraw.Draw(im)
    r = rows[i]
    for (x, y, col, rad) in [(r[3], r[4], (0, 255, 80), 18), (r[5], r[6], (255, 0, 220), 12), (r[7], r[8], (255, 0, 220), 12)]:
        d.ellipse((x - rad, y - rad, x + rad, y + rad), outline=col, width=5)
    d.line((960 - 30, 540, 960 + 30, 540), fill=(255, 255, 255), width=2)
    d.line((960, 540 - 30, 960, 540 + 30), fill=(255, 255, 255), width=2)
    im = im.resize((w, h), Image.LANCZOS)
    ImageDraw.Draw(im).text((4, 4), "f%d yaw %.0f" % (i, r[1]), fill=(255, 255, 255))
    sheet.paste(im, ((k % cols) * w, (k // cols) * h))
sheet.save(sys.argv[3], quality=90)
