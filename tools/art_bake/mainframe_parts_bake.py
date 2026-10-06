"""ART-9 4A: exports the MAINFRAME shop's, the loot sheet's and the event's art from the concept's own
scripts on tag `art-concepts-r43` (their drawing code unchanged: this wrapper only calls it, crops
and saves). Extract the rounds first (see mainframe_facade_bake.py), plus
docs/concepts/round17_slice_system/glyphs, then run, as a file:

    python tools/art_bake/mainframe_parts_bake.py --gen <...>/docs/concepts --part shop
    python tools/art_bake/mainframe_parts_bake.py --gen <...>/docs/concepts --part reward

Everything is written at the concepts' own scale (their 1920x1080 canvas: 1.5x the game's 1280x720)
to assets/ui/mainframe/, with parts.json (each part's size and its anchor, in concept px).

--part shop (round 34 firmware_daemons/scripts: shop_v5.py, shop.py, shop_layout.py, fwlib.py,
recycle.py, lib17/slicekit.py):
  chip_<id>.png / chip_<id>_lit.png   fwlib.chip(id, 84[, lit=0.25])            every Firmware
  daemon_<id>.png                     shop_v5.daemon_row (housing + fwlib.daemon_tile), cropped
  foam.png, foam_lip.png              shop_v5.foam
  tag.png, tag_short.png, tag_sold.png  r31lib.price_tag("", afford, sold): the kraft tag, no price
                                      (the game writes the price in Bahnschrift's place: Anton)
  pegboard.png                        shop.pegboard
  dymo_<word>.png                     shop.dymo (CARDS, FIRMWARE, DAEMONS, RECYCLE BIN)
  lock.png                            shop_layout.lock_icon
  wedge_<slice id>_<m1|0|p1>.png      slicekit.wheel(12 x the slice, r_px=470) (as assets.shop_wheel12), the
                                      wedge at -30 / 0 / +30 degrees cut out with its rim; anchor = the hub
  wheel_stock.png                     assets.shop_wheel12 (the concept's stock wheel), whole
  bin_shut.png, bin_open.png          recycle.scene (the lid at 0 and 96 degrees)
--part leave (parity SHOP-05; round 34 scripts: shop2.py):
  leave_arrow.png                     shop2.leave_sticker()'s pink chevron sticker, as drawn
--part reward (round 31 reward_event/scripts: reward.py, event.py):
  liner.png                           reward.liner, the print band only (no header or footer words)
  slot.png, slot_empty.png            reward.kiss_cut on a clear canvas (a card's slot, before and after)
  plate.png, plate_hover.png          event.plate_button("", "") (the choice sticker, no words)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'assets', 'ui', 'mainframe')
# the shop's slice stock (content/config/campaign_config.tres shop_slices) as round 17 programs
SHOP_SLICES = [("shim_6", "EXPLOIT", 6), ("shim_8", "EXPLOIT", 8), ("overflow_12", "ZERO-DAY", 12),
               ("defrag_5", "FIREWALL", 5), ("defrag_8", "FIREWALL", 8), ("sandbox_5", "SANDBOX", 5),
               ("detour_1", "PROXY", 1), ("shim_10", "EXPLOIT", 10), ("overflow_16", "ZERO-DAY", 16),
               ("hotfix_6", "PATCH", 6), ("sandbox_8", "SANDBOX", 8), ("detour_2", "PROXY", 2)]
WORDS = ["CARDS", "FIRMWARE", "DAEMONS", "RECYCLE BIN"]
meta: dict = {}


def save(im, name, anchor=None):
    im.save(os.path.join(OUT, name + '.png'), optimize=True)
    meta[name] = {"size": [im.width, im.height]}
    if anchor is not None:
        meta[name]["anchor"] = [round(float(anchor[0]), 2), round(float(anchor[1]), 2)]


def bbox_crop(im, pad=2):
    box = im.getbbox()
    if box is None:
        return im, (0, 0)
    box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad))
    return im.crop(box), box[:2]


def shop(gen: str) -> None:
    d = os.path.join(gen, 'round34_firmware_daemons', 'scripts')
    sys.path.insert(0, d)
    sys.path.insert(0, os.path.join(d, 'lib17'))
    os.chdir(d)
    from PIL import Image, ImageDraw
    import fwlib as F
    import shop as S1
    import shop_v5 as V5
    import shop_layout as SL3
    import recycle as RB
    import slicekit as K
    K.TIER_STYLE = "a"
    K.TIER_STRENGTH = 2
    for f in F.FIRMWARE:
        save(F.chip(f[0], 84), 'chip_' + f[0])
        save(F.chip(f[0], 84, lit=0.25), 'chip_%s_lit' % f[0])
    for dm in F.DAEMONS:
        V5.DAEMONS = [(dm[0], 0)]
        canvas = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
        canvas = V5.daemon_row(canvas)
        # the housing at (x0 + 6, y0) 92 x 100 and its drop shadow (daemon_row's own geometry)
        crop = canvas.crop((1180 + 6 - 4, 548 - 4, 1180 + 6 + 98, 548 + 104))
        save(crop, 'daemon_' + dm[0], anchor=(4, 4))
    save(V5.foam(352, 34), 'foam')
    save(V5.foam(72, 12, seed=10), 'foam_lip')
    import r31lib as L
    save(L.price_tag("", afford=True, seed=140), 'tag')
    save(L.price_tag("", afford=False, seed=141), 'tag_short')
    save(L.price_tag("", sold=True, seed=142), 'tag_sold')
    save(S1.pegboard(1600, 1000), 'pegboard')
    # the clerk's pixel face from shop.clerk_panel (its 8 x 7 grid of 22 px cells at (40, 64))
    save(S1.clerk_panel().crop((36, 60, 40 + 8 * 22 + 4, 64 + 7 * 22 + 4)), 'clerk_face')
    for w in WORDS:
        save(S1.dymo(w, 26), 'dymo_' + w.lower().replace(' ', '_'))
    save(SL3.lock_icon(46), 'lock')
    for sid, prog, val in SHOP_SLICES:
        wheel = K.wheel([(prog, val, 1, None)] * 12, t=0.45, r_px=470)
        c = wheel.width / 2
        r_out = 470 + 14
        # the wedges for sale stand at -30, 0 and +30 degrees; each is cut from its own place on
        # the wheel so its read block stays upright as slicekit draws it
        for pos, tag in ((-1, 'm1'), (0, '0'), (1, 'p1')):
            m = Image.new('L', wheel.size, 0)
            pts = [(c, c)]
            for k in range(17):
                a = math.radians(pos * 30 - 15 + 30 * k / 16)
                pts.append((c + math.sin(a) * r_out, c - math.cos(a) * r_out))
            ImageDraw.Draw(m).polygon(pts, fill=255)
            cut = Image.new('RGBA', wheel.size, (0, 0, 0, 0))
            cut.paste(wheel, (0, 0), m)
            part, at = bbox_crop(cut)
            save(part, 'wedge_%s_%s' % (sid, tag), anchor=(c - at[0], c - at[1]))
    # the stock wheel itself (assets.shop_wheel12: the concept's 12 slices), under the ones for sale
    import assets as A
    A.shop_wheel12()
    wheel = Image.open(os.path.join(A.CACHE, 'shop_wheel12.png')).convert('RGBA')
    save(wheel, 'wheel_stock', anchor=(wheel.width / 2, wheel.height / 2))
    meta['wedge_radius'] = 470
    for name, theta in (('bin_shut', 0), ('bin_open', 96)):
        RB.set_scale(1.0)
        o = (200, 380)
        im = RB.scene((400, 420), o, theta, badge=0)
        part, at = bbox_crop(im)
        save(part, name, anchor=(o[0] - at[0], o[1] - at[1]))


def leave(gen: str) -> None:
    """Parity SHOP-05: the pink chevron sticker beside LEAVE, round 34 shop2.leave_sticker()'s own
    arrow (its drawing code unchanged: the sticker it caches is saved as drawn)."""
    d = os.path.join(gen, 'round34_firmware_daemons', 'scripts')
    sys.path.insert(0, d)
    sys.path.insert(0, os.path.join(d, 'lib17'))
    os.chdir(d)
    from PIL import Image
    import shop2 as S2
    import r31lib as L
    _leave, arrow, _tag = S2.leave_sticker()
    # placed as shop2.place_leave places it (angle -4, scale 0.7), on a clear canvas
    canvas = Image.new('RGBA', (400, 300), (0, 0, 0, 0))
    canvas = L.place_sticker(canvas, arrow, 200, 150, angle=-4, scale=0.7)
    part, _at = bbox_crop(canvas)
    save(part, 'leave_arrow')


def reward(gen: str) -> None:
    d = os.path.join(gen, 'round31_reward_event', 'scripts')
    sys.path.insert(0, d)
    os.chdir(d)
    from PIL import Image
    import reward as R
    import event as E
    lin = R.liner(900, 560, seed=3)
    save(lin.crop((0, 60, 900, 500)), 'liner')
    for name, empty in (('slot', False), ('slot_empty', True)):
        im = Image.new('RGBA', (240, 320), (0, 0, 0, 0))
        R.kiss_cut(im, 120, 160, 220, 300, empty=empty)
        save(im, name)
    import r31lib as L
    for name, hov in (('plate', False), ('plate_hover', True)):
        sd = E.plate_button("", "", w=430, h=78, seed=1, hover=hov)
        canvas = Image.new('RGBA', (600, 240), (0, 0, 0, 0))
        canvas = L.place_sticker(canvas, sd, 300, 120)
        part, at = bbox_crop(canvas)
        save(part, name, anchor=(300 - at[0], 120 - at[1]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--gen', required=True, help='the extracted docs/concepts folder')
    ap.add_argument('--part', choices=['shop', 'reward', 'leave'], required=True)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'parts.json')
    if os.path.exists(path):
        meta.update(json.load(open(path, encoding='utf-8')))
    gen = os.path.abspath(a.gen)
    {'shop': shop, 'reward': reward, 'leave': leave}[a.part](gen)
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=1, sort_keys=True)
    print('parts', len(meta))


if __name__ == '__main__':
    main()
