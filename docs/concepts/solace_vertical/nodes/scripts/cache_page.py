"""CACHE: the loot page with the header art of a stash. Built on the real reward screen (round 32 reward_screen_v2): only the
title sticker, the strip's node word, the loot sheet's header words and the kind stamp change. Strings are the existing ones
(LOOT, LOOT_STRIP, the sheet header's pattern) with the node word CACHE."""
import sys
sys.path.insert(0, "D:/rc_scratch/solace_v1/nodes/scripts")
from pages import *

SRC = "D:/rc_art/art-pass/docs/concepts/round32_shop_reward/reward_screen_v2.png"


def patch(img, box, src_xy, feather=14):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sx, sy = src_xy
    piece = img.crop((sx, sy, sx + w, sy + h))
    mask = Image.new("L", (w, h), 255)
    ImageDraw.Draw(mask).rectangle((0, 0, w - 1, h - 1), outline=0, width=1)
    mask = mask.filter(ImageFilter.GaussianBlur(feather / 2))
    m2 = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m2).rectangle((feather, feather, w - feather, h - feather), fill=255)
    m2 = m2.filter(ImageFilter.GaussianBlur(feather / 2))
    img.paste(piece, (x0, y0), m2)


def cache_page(direction):
    img = Image.open(SRC).convert("RGBA")
    acc = KCOL["cache"]
    # clear the old title and strip (the backdrop is a soft city: borrow nearby backdrop)
    patch(img, (100, 30, 560, 195), (900, 20))
    patch(img, (66, 188, 850, 248), (640, 66))
    # the strip: the existing CrtWindow strip, the node word now CACHE (cyan stays: the strip is the loot window, not the node)
    d = ImageDraw.Draw(img)
    box = (78, 197, 835, 237)
    crt_window(img, box, NET_CYAN, "", "", alpha=200, head=False, seed=2)
    text(img, (93, 217), "LOOT  //  NETRUN: SOLACE  //  CACHE 4 OF 7", mono(20), (92, 225, 255, 255), "lm")
    # the title sticker: the existing LOOT word (LOOT_PLAIN), yellow, and the kind stamp tucked over its corner
    sticker_word(img, (130, 112), "LOOT", 112, YELLOW, -3, "lm")
    sticker_icon(img, direction, "cache", (430, 118), 150, 8)
    # the loot sheet header words: LOOT SHEET // LOOT // PICK 1 OF 3 ... CACHE 4/7
    band = (300, 312, 1290, 346)
    d.rectangle(band, fill=(27, 25, 33, 255))
    text(img, (322, 324), "LOOT SHEET  //  LOOT  //  PICK 1 OF 3", mono(21), (242, 238, 228, 255), "lm")
    text(img, (1267, 324), "CACHE 4/7", mono(21), (255, 176, 0, 255), "rm")
    return img.convert("RGB")


if __name__ == "__main__":
    for dr in "ABC":
        cache_page(dr).save(OUT + "work/cache_%s.png" % dr)
    print("ok")
