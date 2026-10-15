"""Debug: the emoji-style boss emblems at 256, 64 and 32 px on dark and light (scratch only)."""
import os
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nc_kit as K
from PIL import Image

sheet = Image.new("RGBA", (900, 620), (24, 20, 30, 255))
for i, kind in enumerate(("cartoon", "thumb")):
    e = K.emblem_thumb_cartoon() if kind == "cartoon" else K.emblem_emoji(kind)
    y = 20 + i * 300
    sheet.alpha_composite(e.resize((256, 256), Image.LANCZOS), (20, y))
    sheet.alpha_composite(e.resize((64, 64), Image.LANCZOS), (320, y + 96))
    sheet.alpha_composite(e.resize((32, 32), Image.LANCZOS), (420, y + 112))
    light = Image.new("RGBA", (300, 280), (236, 232, 222, 255))
    light.alpha_composite(e.resize((256, 256), Image.LANCZOS), (22, 12))
    sheet.alpha_composite(light, (580, y - 10))
out = os.path.join(K.SCR, "emoji_test.png")
sheet.save(out)
print(out)
