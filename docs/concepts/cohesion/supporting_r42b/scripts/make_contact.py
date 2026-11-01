"""contact_old_vs_new.jpg (old left, new right) and squint_<plate>.png (plate left, 1/16 scale + blur back up, right)."""
import os
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
CONC = os.path.dirname(os.path.dirname(OUT))
PAIRS = [
    ("01 terminal event", "round31_reward_event/event_screen.png", "01_terminal_event.png"),
    ("02 dialogue A", "round31_reward_event/dialogue.png", "02_dialogue_A.png"),
    ("02 dialogue B", "round31_reward_event/dialogue_B.png", "02_dialogue_B.png"),
    ("03 reward", "round32_shop_reward/reward_screen_v2.png", "03_reward_fight_won.png"),
    ("04 shop", "round33_shop/shop_v3_layout.png", "04_shop_mainframe.png"),
    ("05 deck", "round44_undesigned/B_menus/deck_viewer.png", "05_deck_screen.png"),
    ("06 server rack", "round31_reward_event/server_rack.png", "06_server_rack.png"),
    ("07 heat strip", "round44_undesigned/A_map/topbar_by_page.png", "07_heat_strip_by_page.png"),
]
cw, ch = 480, 270
sheet = Image.new("RGB", (1920, 4 * (ch + 22)), (10, 10, 14))
d = ImageDraw.Draw(sheet)
for i, (name, old, new) in enumerate(PAIRS):
    x, y = (i % 2) * 960, (i // 2) * (ch + 22)
    a = Image.open(os.path.join(CONC, old)).convert("RGB").resize((cw, ch), Image.LANCZOS)
    b = Image.open(os.path.join(OUT, new)).convert("RGB").resize((cw, ch), Image.LANCZOS)
    sheet.paste(a, (x, y + 20)); sheet.paste(b, (x + cw, y + 20))
    d.text((x + 6, y + 4), name + "   OLD  |  NEW", fill=(220, 220, 230))
sheet.save(os.path.join(OUT, "contact_old_vs_new.jpg"), quality=90)
for name, old, new in PAIRS:
    im = Image.open(os.path.join(OUT, new)).convert("RGB")
    sq = im.resize((120, 67), Image.BOX).filter(ImageFilter.GaussianBlur(1.2)).resize((960, 540), Image.BICUBIC)
    c = Image.new("RGB", (1920, 540)); c.paste(im.resize((960, 540), Image.LANCZOS), (0, 0)); c.paste(sq, (960, 0))
    c.save(os.path.join(OUT, "squint_" + os.path.splitext(new)[0] + ".png"))
