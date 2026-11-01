import sys
from PIL import Image, ImageDraw
Z = "D:/rc_art/art-pass/docs/concepts/netrun_cel/zoom_rules/"
items = [("r6", Z + "round7/highlight_before.png"), ("r7", Z + "round7/highlight_after.png")]
for n in "ABC":
    items.append(("cand" + n, Z + "round7b/cand%s/stage_1_layers.png" % n))
items.append(("PICK = candB", Z + "round7b/candB/stage_1_layers.png"))
box = (700, 380, 1240, 720)
w, h = 540, 340
out = Image.new("RGB", (w * 3 + 20, h * 2 + 10), (20, 20, 20))
d = ImageDraw.Draw(out)
for i, (n, p) in enumerate(items):
    c = Image.open(p).convert("RGB").crop(box)
    x, y = (i % 3) * (w + 10), (i // 3) * (h + 10)
    out.paste(c, (x, y)); d.text((x + 6, y + 6), n, fill=(255, 255, 255))
out.save(Z + "round7b/crop_sheet.png")
