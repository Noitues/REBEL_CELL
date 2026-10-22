"""REST / WORKSHOP page mocks, 1920 x 1080, three directions. Placeholder text only from the existing strings (node_page.gd,
netrun_scene.gd loot strings, the RUN window of the event page); sample numbers are placeholders."""
import math
import random
import sys
sys.path.insert(0, "D:/rc_scratch/solace_v1/nodes/scripts")
from kit import *
import icons

SLOTS = ["Shim 8", "Shield 8", "Hotfix 6", "Overflow 12", "Sandbox 8", "Trojan 1"]
FIRM = ["Overvolt", "-", "Skimmer", "Coolant Loop", "-", "Leech"]
OFFERS = ["Shield 5", "Block 12", "Overflow 14"]
PRICES = [80, 80, 100, 100, 80, 120]

# ---- the existing strings (node_page.gd / netrun_scene.gd) ------------------------------------------------------------
S_HP = "HP %d/%d"
S_PATCH = "PATCH  +%d HP -> %d/%d"
S_HINT_REST = "REWIRE: pick a wheel slot, then the slot to swap its Firmware with."
S_CONFIRM = "CONFIRM REWIRE"
S_UNDO = "UNDO"
S_LEAVE = "LEAVE"
S_CYC = "Cycles: %d"
S_HINT_SHOP = "Pick a slice, then the wheel slot it replaces."
S_BUY = "BUY  %d Cycles (%d left)"
S_STRIP = "NETRUN: %s // %s %d OF %d"   # LOOT_STRIP's pattern without the LOOT lead


def icon_img(direction, kind, px):
    return icons.make(direction, kind).render(scale=px / 130.0, ss=4)


def sticker_icon(img, direction, kind, c, px, tilt=0.0):
    im = icon_img(direction, kind, px)
    if tilt:
        im = im.rotate(tilt, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.split()[3].point(lambda v: int(v * 0.55)))
    sh = sh.filter(ImageFilter.GaussianBlur(8))
    img.alpha_composite(sh, (int(c[0] - im.width / 2 + 5), int(c[1] - im.height / 2 + 10)))
    paste_c(img, im, c[0], c[1])


def run_window(img, box, accent=NET_CYAN, hp=(41, 60), cyc=160):
    crt_window(img, box, accent, "RUN", "", seed=7)
    x0, y0, x1, y1 = box
    y = y0 + 84
    for icon, word, val, col in (("hp", "HP", "%d/%d" % hp, (255, 130, 200)), ("cyc", "CYCLES", str(cyc), CELL_ACID)):
        if icon == "hp":
            heart(img, (x0 + 40, y), 15, (255, 105, 190))
        else:
            cycles_icon(img, (x0 + 40, y), 16, accent)
        text(img, (x0 + 72, y), word, mono(26), TEXT_MID, "lm")
        text(img, (x1 - 24, y + 2), val, anton(44), col, "rm")
        y += 66


def hp_row(img, x, y, w, hp, heal, accent):
    heart(img, (x + 16, y + 4), 15, (255, 105, 190))
    text(img, (x + 44, y + 4), S_HP % hp, mono(28), TEXT_HI, "lm")
    bx0, bx1 = x + 250, x + w
    segs = 30
    seg_w = (bx1 - bx0) / segs
    d = ImageDraw.Draw(img)
    now = hp[0] / hp[1]
    after = min(hp[1], hp[0] + heal) / hp[1]
    for i in range(segs):
        f = (i + 1) / segs
        col = (255, 105, 190) if f <= now + 1e-6 else (accent + (110,) if f <= after + 1e-6 else (40, 48, 70))
        d.rectangle((bx0 + i * seg_w + 1, y - 6, bx0 + (i + 1) * seg_w - 3, y + 14), fill=col)


# ---------------------------------------------------------------------------------------------------------------------
# DIRECTION A  "Kit window": the event page's layout (CRT window left, RUN right, kind title sticker + icon sticker right)
# ---------------------------------------------------------------------------------------------------------------------
def page_a(kind):
    acc = KCOL[kind]
    img = city_backdrop(acc)
    word = "REST" if kind == "rest" else "WORKSHOP"
    box = (90, 170, 1330, 170 + (700 if kind == "rest" else 760))
    crt_window(img, box, acc, S_STRIP % ("SOLACE", word, 4, 7), word, seed=3)
    x0, y0, x1, y1 = box
    if kind == "rest":
        hp_row(img, x0 + 34, y0 + 108, 560, (41, 60), 19, acc)
        sticker_chip(img, (x0 + 640, y0 + 74, x1 - 34, y0 + 146), S_PATCH % (19, 60, 60), 34, CELL_PINK, (255, 255, 255))
        text(img, (x0 + 34, y0 + 190), S_HINT_REST, mono(21), TEXT_MID, "lm")
        gy = y0 + 232
        for i, nm in enumerate(SLOTS):
            col, row = i % 2, i // 2
            bx = x0 + 34 + col * 600
            by = gy + row * 116
            st = "picked" if i == 0 else ("second" if i == 2 else ("off" if i == 4 else "normal"))
            fw = FIRM[i]
            if i == 0:
                fw = FIRM[2]
            elif i == 2:
                fw = FIRM[0]

            def right(im, p, a, fw=fw, i=i):
                col_ = CELL_ACID if i in (0, 2) else TEXT_MID
                text(im, (p[0], p[1]), "[%s]" % fw, mono(24), col_ + (a,), "rm")
            choice_row(img, (bx, by, bx + 570, by + 100), i + 1, nm, acc, st, right, SLICE_GLYPH[nm], plate=(34, 22, 58), label_px=36)
        fy = gy + 3 * 116 + 14
        sticker_chip(img, (x0 + 34, fy, x0 + 460, fy + 76), S_CONFIRM, 36, CELL_PINK, (255, 255, 255))
        sticker_chip(img, (x0 + 490, fy, x0 + 700, fy + 76), S_UNDO, 36, (60, 60, 74), (200, 204, 216))
        holo_chip(img, (x1 - 34 - 260, fy, x1 - 34, fy + 76), S_LEAVE, 40)
    else:
        row_y = y0 + 90
        cycles_icon(img, (x0 + 50, row_y + 4), 17, acc)
        text(img, (x0 + 84, row_y + 4), S_CYC % 160, mono(30), TEXT_HI, "lm")
        text(img, (x0 + 34, row_y + 62), S_HINT_SHOP, mono(21), TEXT_MID, "lm")
        oy = row_y + 100
        for i, nm in enumerate(OFFERS):
            bx = x0 + 34 + i * 400
            st = "picked" if i == 1 else "normal"
            choice_row(img, (bx, oy, bx + 384, oy + 92), i + 1, nm, acc, st, None, SLICE_GLYPH[nm], plate=(48, 36, 12), label_px=34)
        gy = oy + 124
        for i, nm in enumerate(SLOTS):
            col, row = i % 2, i // 2
            bx = x0 + 34 + col * 600
            by = gy + row * 104
            st = "second" if i == 2 else ("off" if i == 4 else "normal")

            def right(im, p, a, i=i):
                if a == 255:
                    price_tag(im, (p[0] - 130, p[1] - 28, p[0], p[1] + 28), str(PRICES[i]))
            choice_row(img, (bx, by, bx + 570, by + 88), i + 1, nm, acc, st, right, SLICE_GLYPH[nm], plate=(48, 36, 12), label_px=32)
        fy = gy + 3 * 104 + 12
        sticker_chip(img, (x0 + 34, fy, x0 + 600, fy + 76), S_BUY % (100, 60), 36, CELL_PINK, (255, 255, 255))
        holo_chip(img, (x1 - 34 - 260, fy, x1 - 34, fy + 76), S_LEAVE, 40)
    run_window(img, (1380, 170, 1880, 400))
    sticker_word(img, (1630, 560), word, 100 if kind == "rest" else 84, acc, -4, "mm")
    sticker_icon(img, "A", kind, (1630, 800), 330, 6)
    return img.convert("RGB")


# ---------------------------------------------------------------------------------------------------------------------
# DIRECTION B  "Room": the page is the room (the street kit's interior as the backdrop), rows are the objects
# ---------------------------------------------------------------------------------------------------------------------
PROPS = {
    "rest": [[-0.44, 0.22, 0.0, 0.20, 0], [-0.44, -0.30, 0.20, 0.32, 0], [0.30, 0.34, 0.0, 0.62, 0], [0.24, 0.40, 0.62, 0.72, 1]],
    "workshop": [[-0.42, -0.36, 0.0, 0.34, 0], [0.36, 0.42, 0.0, 0.34, 0], [-0.44, 0.44, 0.34, 0.41, 0], [0.18, 0.30, 0.41, 0.56, 0],
                 [-0.42, -0.04, 0.58, 0.90, 0], [-0.30, -0.22, 0.62, 0.86, 1]],
    "cache": [[-0.36, 0.08, 0.0, 0.46, 0], [0.10, 0.40, 0.0, 0.30, 0], [-0.26, 0.02, 0.46, 0.66, 0], [-0.30, -0.22, 0.20, 0.30, 1]],
}


def room_backdrop(kind, acc):
    base = city_backdrop(acc, dark=0.78, blur=18, seed_flip=True)
    x0, y0, x1, y1 = 70, 70, 1850, 1010
    W, H = x1 - x0, y1 - y0
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    wall = tuple(int(c * 0.8) for c in acc)
    # back wall with the glow fading toward the top, floor, ceiling
    for yy in range(y0, y1):
        v = (y1 - yy) / H
        g = 0.55 - 0.40 * v if v > 0 else 0.55
        col = tuple(int(c * (0.62 - 0.35 * v)) for c in wall)
        d.line((x0, yy, x1, yy), fill=col + (255,))
    fl = int(H * 0.10)
    for yy in range(y1 - fl, y1):
        t = (yy - (y1 - fl)) / fl
        col = tuple(int(c * (0.34 + 0.22 * t)) for c in acc)
        d.line((x0, yy, x1, yy), fill=col + (255,))
    # side walls (trapezoids in dark)
    d.polygon([(x0, y0), (x0 + 150, y0 + 70), (x0 + 150, y1 - fl - 20), (x0, y1)], fill=tuple(int(c * 0.20) for c in acc) + (255,))
    d.polygon([(x1, y0), (x1 - 150, y0 + 70), (x1 - 150, y1 - fl - 20), (x1, y1)], fill=tuple(int(c * 0.14) for c in acc) + (255,))
    d.polygon([(x0, y0), (x1, y0), (x1 - 150, y0 + 70), (x0 + 150, y0 + 70)], fill=tuple(int(c * 0.06) for c in acc) + (255,))
    # props: near-black boxes, lit ones glow in the kind colour
    lit = []
    for (s0, s1, v0, v1, l) in PROPS[kind]:
        px0 = x0 + (s0 + 0.5) * W
        px1 = x0 + (s1 + 0.5) * W
        py0 = (y1 - fl) - v1 * (H - fl) * 0.92
        py1 = (y1 - fl) - v0 * (H - fl) * 0.92
        if l:
            lit.append((px0, py0, px1, py1))
            d.rectangle((px0, py0, px1, py1), fill=tuple(min(255, int(c * 1.1)) for c in acc) + (255,))
        else:
            d.rectangle((px0, py0, px1, py1), fill=(6, 6, 10, 255))
            d.polygon([(px0, py0), (px1, py0), (px1 - 16, py0 - 14), (px0 + 16, py0 - 14)], fill=tuple(int(c * 0.30) for c in acc) + (255,))
            d.line((px0, py0, px1, py0), fill=tuple(int(c * 0.65) for c in acc) + (255,), width=3)
            d.line((px0, py0, px0, py1), fill=tuple(int(c * 0.25) for c in acc) + (255,), width=2)
    base.alpha_composite(lay)
    if lit:
        glow(base, lambda dd: [dd.rectangle(b, fill=255) for b in lit], acc, 40, 0.8)
    # window frame: four thin white bars
    d = ImageDraw.Draw(base)
    d.rectangle((x0 - 6, y0 - 6, x1 + 6, y1 + 6), outline=(230, 238, 255, 255), width=8)
    return base


def pod_row(img, box, num, name, acc, state, right, gl, plate=(34, 22, 58), px=34):
    x0, y0, x1, y1 = box
    h = y1 - y0
    a = 255 if state != "off" else 110
    if state in ("picked", "second"):
        glow(img, lambda dd: dd.rounded_rectangle((x0, y0, x1, y1), radius=h // 2, fill=255), acc, 14, 0.75)
    rr(img, (x0, y0, x1, y1), h / 2, fill=(252, 251, 249, a), outline=(109, 105, 110, a), ow=1, pad=3)
    rr(img, (x0 + 5, y0 + 5, x1 - 5, y1 - 5), h / 2 - 5, fill=INKC + (a,))
    pl = mix(plate, acc, 0.34) if state == "picked" else plate
    rr(img, (x0 + 8, y0 + 8, x1 - 8, y1 - 8), h / 2 - 8, fill=pl + (a,))
    cx, cy = x0 + h / 2 + 4, (y0 + y1) / 2
    r = h / 2 - 12
    d = ImageDraw.Draw(img)
    d.ellipse((cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3), fill=INKC + (a,))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(YELLOW if state in ("normal", "picked") else (acc if state == "second" else (150, 150, 150))) + (a,))
    text(img, (cx, cy + 1), str(num), anton(h * 0.5), INKC + (a,), "mm")
    tx = cx + r + 18
    if gl:
        glyph(img, gl, (tx + h * 0.28, cy), int(h * 0.58))
        tx += h * 0.64
    text(img, (tx, cy + 2), name.upper(), anton(px), (246, 243, 232, a), "lm")
    if right:
        right(img, (x1 - h / 2 - 6, cy), a)


def pocket(img, box, num, name, acc, state, gl):
    """a tool-roll pocket: a canvas panel with a stitched edge and a strap; the slice sticks out of it."""
    x0, y0, x1, y1 = box
    a = 255 if state != "off" else 110
    if state in ("picked", "second"):
        glow(img, lambda dd: dd.rounded_rectangle((x0, y0, x1, y1), radius=12, fill=255), acc, 14, 0.75)
    rr(img, (x0, y0, x1, y1), 12, fill=mix((58, 42, 20), acc, 0.12 if state != "picked" else 0.35) + (a,), outline=INKC + (255,), ow=3)
    d = ImageDraw.Draw(img)
    # stitches
    for sx in range(int(x0 + 14), int(x1 - 14), 14):
        d.line((sx, y0 + 12, sx + 7, y0 + 12), fill=(255, 226, 170, a), width=2)
        d.line((sx, y1 - 12, sx + 7, y1 - 12), fill=(255, 226, 170, a), width=2)
    # the strap with the number
    rr(img, (x0 + 18, y0 - 10, x0 + 18 + 52, y0 + 28), 6, fill=YELLOW + (a,), outline=INKC + (255,), ow=3)
    text(img, (x0 + 18 + 26, y0 + 9), str(num), anton(30), INKC + (a,), "mm")
    cy = (y0 + y1) / 2 + 8
    glyph(img, gl, (x0 + 52, cy), 66)
    text(img, (x0 + 100, cy + 2), name.upper(), anton(32), (246, 243, 232, a), "lm")


def page_b(kind):
    acc = KCOL[kind]
    img = room_backdrop(kind, acc)
    word = "REST" if kind == "rest" else "WORKSHOP"
    box = (760, 120, 1810, 960)
    crt_window(img, box, acc, S_STRIP % ("SOLACE", word, 4, 7), word, alpha=238, seed=5)
    x0, y0, x1, y1 = box
    if kind == "rest":
        hp_row(img, x0 + 30, y0 + 108, 440, (41, 60), 19, acc)
        sticker_chip(img, (x0 + 30, y0 + 150, x1 - 30, y0 + 222), S_PATCH % (19, 60, 60), 34, CELL_PINK, (255, 255, 255))
        text(img, (x0 + 30, y0 + 262), S_HINT_REST, mono(20), TEXT_MID, "lm")
        gy = y0 + 300
        for i, nm in enumerate(SLOTS):
            by = gy + i * 78
            st = "picked" if i == 0 else ("second" if i == 2 else ("off" if i == 4 else "normal"))
            fw = FIRM[2] if i == 0 else (FIRM[0] if i == 2 else FIRM[i])

            def right(im, p, a, fw=fw, i=i):
                text(im, (p[0], p[1]), "[%s]" % fw, mono(24), (CELL_ACID if i in (0, 2) else TEXT_MID) + (a,), "rm")
            pod_row(img, (x0 + 30, by, x1 - 30, by + 68), i + 1, nm, acc, st, right, SLICE_GLYPH[nm], px=32)
        fy = gy + 6 * 78 + 4
        sticker_chip(img, (x0 + 30, fy, x0 + 440, fy + 70), S_CONFIRM, 34, CELL_PINK, (255, 255, 255))
        sticker_chip(img, (x0 + 462, fy, x0 + 640, fy + 70), S_UNDO, 34, (60, 60, 74), (200, 204, 216))
        holo_chip(img, (x1 - 30 - 230, fy, x1 - 30, fy + 70), S_LEAVE, 36)
    else:
        cycles_icon(img, (x0 + 46, y0 + 100), 16, acc)
        text(img, (x0 + 78, y0 + 100), S_CYC % 160, mono(28), TEXT_HI, "lm")
        text(img, (x0 + 30, y0 + 148), S_HINT_SHOP, mono(20), TEXT_MID, "lm")
        oy = y0 + 196
        for i, nm in enumerate(OFFERS):
            bx = x0 + 30 + i * 336
            pocket(img, (bx, oy + 14, bx + 318, oy + 130), i + 1, nm, acc, "picked" if i == 1 else "normal", SLICE_GLYPH[nm])
        gy = oy + 172
        for i, nm in enumerate(SLOTS):
            by = gy + i * 66
            st = "second" if i == 2 else ("off" if i == 4 else "normal")

            def right(im, p, a, i=i):
                if a == 255:
                    price_tag(im, (p[0] - 130, p[1] - 24, p[0], p[1] + 24), str(PRICES[i]))
            pod_row(img, (x0 + 30, by, x1 - 30, by + 58), i + 1, nm, acc, st, right, SLICE_GLYPH[nm], px=28)
        fy = gy + 6 * 66 + 6
        sticker_chip(img, (x0 + 30, fy, x0 + 560, fy + 70), S_BUY % (100, 60), 34, CELL_PINK, (255, 255, 255))
        holo_chip(img, (x1 - 30 - 230, fy, x1 - 30, fy + 70), S_LEAVE, 36)
    # the sticker as the room's sign: large, on the lit wall at the left, with the title sticker under it
    run_window(img, (130, 110, 610, 340))
    sticker_icon(img, "B", kind, (370, 540), 340, -5)
    sticker_word(img, (370, 735), word, 92 if kind == "rest" else 78, acc, 3, "mm")
    return img.convert("RGB")


# ---------------------------------------------------------------------------------------------------------------------
# DIRECTION C  "Slap-tag": a compact terminal, the contour sticker as the hero, a pencil plan (orange = the netrun plan)
# ---------------------------------------------------------------------------------------------------------------------
def pencil_circle(img, box, col=(255, 140, 26), w=7):
    rnd = random.Random(4)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
    pts = []
    for i in range(0, 392, 6):
        a = math.radians(i - 20)
        k = 1 + 0.03 * math.sin(a * 3 + 1) + (i - 20) / 392 * 0.05
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    d = Doc(img.width, img.height)
    d.line([(x + 2, y + 3) for x, y in pts], (17, 12, 26, 150), w + 4)
    d.line(pts, col + (245,), w)
    img.alpha_composite(d.render(1.0, ss=2))


def pencil_arrow(img, a, b, col=(255, 140, 26), w=7):
    mx, my = (a[0] + b[0]) / 2 + 60, (a[1] + b[1]) / 2
    pts = []
    for i in range(0, 21):
        t = i / 20
        u = 1 - t
        pts.append((u * u * a[0] + 2 * u * t * mx + t * t * b[0], u * u * a[1] + 2 * u * t * my + t * t * b[1]))
    ang = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
    h1 = (b[0] - 30 * math.cos(ang - 0.5), b[1] - 30 * math.sin(ang - 0.5))
    h2 = (b[0] - 30 * math.cos(ang + 0.5), b[1] - 30 * math.sin(ang + 0.5))
    d = Doc(img.width, img.height)
    for L in (pts, [h1, b, h2]):
        d.line([(x + 2, y + 3) for x, y in L], (17, 12, 26, 150), w + 4)
    for L in (pts, [h1, b, h2]):
        d.line(L, col + (245,), w)
    img.alpha_composite(d.render(1.0, ss=2))


def tag_row(img, box, num, name, acc, state, right, gl, px=32):
    x0, y0, x1, y1 = box
    a = 255 if state != "off" else 110
    cy = (y0 + y1) / 2
    d = ImageDraw.Draw(img)
    if state == "picked":
        d.rectangle(box, fill=mix(NAVY, acc, 0.22) + (255,))
    elif state == "second":
        d.rectangle(box, fill=mix(NAVY, acc, 0.12) + (255,))
    d.line((x0, y1, x1, y1), fill=acc + (70,), width=2)
    rr(img, (x0 + 8, cy - 22, x0 + 52, cy + 22), 6, fill=(YELLOW if state in ("normal", "picked") else (acc if state == "second" else (150, 150, 150))) + (a,), outline=INKC + (255,), ow=3)
    text(img, (x0 + 30, cy + 1), str(num), anton(30), INKC + (a,), "mm")
    tx = x0 + 72
    if gl:
        glyph(img, gl, (tx + 22, cy), 44)
        tx += 56
    text(img, (tx, cy + 2), name.upper(), anton(px), (246, 243, 232, a), "lm")
    if right:
        right(img, (x1 - 14, cy), a)


def page_c(kind):
    acc = KCOL[kind]
    img = city_backdrop(acc, dark=0.70, blur=20)
    word = "REST" if kind == "rest" else "WORKSHOP"
    box = (640, 120, 1840, 980) if kind == 'rest' else (640, 70, 1840, 1010)
    crt_window(img, box, acc, S_STRIP % ("SOLACE", word, 4, 7), word, alpha=236, seed=9)
    x0, y0, x1, y1 = box
    rows_y = {}
    if kind == "rest":
        hp_row(img, x0 + 30, y0 + 106, 520, (41, 60), 19, acc)
        sticker_chip(img, (x0 + 610, y0 + 70, x1 - 30, y0 + 144), S_PATCH % (19, 60, 60), 34, CELL_PINK, (255, 255, 255))
        text(img, (x0 + 30, y0 + 186), S_HINT_REST, mono(21), TEXT_MID, "lm")
        gy = y0 + 214
        for i, nm in enumerate(SLOTS):
            by = gy + i * 84
            st = "picked" if i == 0 else ("second" if i == 2 else ("off" if i == 4 else "normal"))
            fw = FIRM[2] if i == 0 else (FIRM[0] if i == 2 else FIRM[i])

            def right(im, p, a, fw=fw, i=i):
                text(im, (p[0], p[1]), "[%s]" % fw, mono(26), (CELL_ACID if i in (0, 2) else TEXT_MID) + (a,), "rm")
            tag_row(img, (x0 + 30, by, x1 - 30, by + 78), i + 1, nm, acc, st, right, SLICE_GLYPH[nm])
            rows_y[i] = by + 39
        fy = gy + 6 * 84 + 14
        sticker_chip(img, (x0 + 30, fy, x0 + 470, fy + 76), S_CONFIRM, 36, CELL_PINK, (255, 255, 255))
        sticker_chip(img, (x0 + 500, fy, x0 + 700, fy + 76), S_UNDO, 36, (60, 60, 74), (200, 204, 216))
        holo_chip(img, (x1 - 30 - 260, fy, x1 - 30, fy + 76), S_LEAVE, 40)
        # the netrun plan in orange pencil: the swap, row 1 <-> row 3 (a plan true to the rules: it is what CONFIRM would do)
        pencil_arrow(img, (x0 + 30 + 880, rows_y[0] + 12), (x0 + 30 + 880, rows_y[2] - 14), w=6)
        pencil_circle(img, (x0 + 18, gy - 4, x1 - 18, gy + 84 + 0), w=6) if False else None
    else:
        cycles_icon(img, (x0 + 50, y0 + 100), 17, acc)
        text(img, (x0 + 84, y0 + 100), S_CYC % 160, mono(30), TEXT_HI, "lm")
        text(img, (x0 + 30, y0 + 148), S_HINT_SHOP, mono(21), TEXT_MID, "lm")
        oy = y0 + 180
        for i, nm in enumerate(OFFERS):
            tag_row(img, (x0 + 30, oy + i * 84, x1 - 30, oy + i * 84 + 78), i + 1, nm, acc, "picked" if i == 1 else "normal", None, SLICE_GLYPH[nm])
            rows_y[("o", i)] = oy + i * 84 + 39
        gy = oy + 3 * 84 + 24
        for i, nm in enumerate(SLOTS):
            by = gy + i * 66
            st = "second" if i == 2 else ("off" if i == 4 else "normal")

            def right(im, p, a, i=i):
                if a == 255:
                    price_tag(im, (p[0] - 120, p[1] - 24, p[0], p[1] + 24), str(PRICES[i]))
            tag_row(img, (x0 + 30, by, x1 - 30, by + 60), i + 1, nm, acc, st, right, SLICE_GLYPH[nm], px=28)
            rows_y[i] = by + 30
        fy = gy + 6 * 66 + 10
        sticker_chip(img, (x0 + 30, fy, x0 + 560, fy + 72), S_BUY % (100, 60), 34, CELL_PINK, (255, 255, 255))
        holo_chip(img, (x1 - 30 - 250, fy, x1 - 30, fy + 72), S_LEAVE, 38)
        pencil_arrow(img, (x0 + 30 + 800, rows_y[("o", 1)] + 4), (x0 + 30 + 800, rows_y[2] - 14), w=6)
    # the hero: the contour sticker, big, with the title sticker under it (a tag on the wall)
    sticker_icon(img, "C", kind, (330, 400), 520, -7)
    sticker_word(img, (330, 720), word, 92 if kind == "rest" else 78, acc, 3, "mm")
    run_window(img, (120, 800, 560, 980))
    return img.convert("RGB")


def page(direction, kind):
    return {"A": page_a, "B": page_b, "C": page_c}[direction](kind)
