"""contact_old_vs_new.jpg: old page (left) next to new page (right), 4 rows, each 960x540."""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)
OLD = os.path.join(os.path.dirname(OUT), "..", "round44_undesigned", "A_map")
pages = ["hq_idle", "hq_node_selected", "route_page", "raid_setup"]
f = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 22)
sh = Image.new("RGB", (1920, 4 * 564), (10, 10, 14)); d = ImageDraw.Draw(sh)
for i, p in enumerate(pages):
    y = i * 564
    d.text((10, y + 4), "OLD  " + p, font=f, fill=(230, 235, 240)); d.text((970, y + 4), "NEW (r42, strong grade)  " + p, font=f, fill=(230, 235, 240))
    sh.paste(Image.open(os.path.join(OLD, p + ".png")).convert("RGB").resize((950, 534), Image.LANCZOS), (5, y + 28))
    sh.paste(Image.open(os.path.join(OUT, p + ".png")).convert("RGB").resize((950, 534), Image.LANCZOS), (965, y + 28))
sh.save(os.path.join(OUT, "contact_old_vs_new.jpg"), quality=88)
