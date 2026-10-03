"""Round 31 -> contact_sheet.jpg (every screen, recommended option marked).

python contact.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw

import r31lib as L

ITEMS = [
    ("reward_screen.png", "1 REWARD  A: peel from a loot sheet", True),
    ("reward_screen_B.png", "1 REWARD  B: decompiled from the beaten wheel", False),
    ("server_rack.png", "2 SERVER RACK: banked + upgrade bay + swap drawer", True),
    ("event_screen.png", "3 TERMINAL EVENT: CRT story + sticker choices", True),
    ("event_screen_memo.png", "3 EVENT VARIANT: corp memo drives it (after the pick)", True),
    ("dialogue.png", "4 DIALOGUE  A: cel bust on a CRT comm feed", True),
    ("dialogue_B.png", "4 DIALOGUE  B: sticker portrait", False),
    ("netrun_map.png", "5 NETRUN ROUTE: grease pencil on the corp site plan", True),
    ("shop_interior.png", "6 MODEM SHOP: pegboard over MARKET NEON", True),
]


def main():
    tw, th = 620, 349
    pad, top = 16, 92
    W = 3 * tw + 4 * pad
    H = top + 3 * (th + 40) + pad
    sheet = Image.new("RGBA", (W, H), (11, 10, 16, 255))
    sd = L.sticker_word(["ROUND 31  REWARD / EVENT / ROUTE / SHOP"], 46, fills=["yellow"], seed=5)
    sheet = L.place_sticker(sheet, sd, 560, 48, angle=-1)
    d = ImageDraw.Draw(sheet)
    d.text((W - pad, 50), "* = recommended", font=L.f_mono(18), fill=(255, 214, 64, 255), anchor="rm")
    for k, (fn, cap, rec) in enumerate(ITEMS):
        r, c = divmod(k, 3)
        x = pad + c * (tw + pad)
        y = top + r * (th + 40)
        im = Image.open(os.path.join(L.OUT, fn)).convert("RGB").resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (x, y))
        d.text((x, y + th + 8), ("* " if rec else "  ") + fn + "  " + cap, font=L.f_mono(14), fill=(220, 220, 230, 255) if rec else (150, 150, 165, 255))
    L.save(sheet, "contact_sheet.jpg", q=88)


if __name__ == "__main__":
    main()
