"""V2 'Living programs': a signature mascot per program, drawn as a faint watermark
inside the slice's screen, behind the glyph (512 masks, tinted and scanlined)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from slicelib import PROGRAMS

MASCOT_OF = {"FIREWALL": "golem", "ZERO-DAY": "skull", "VIRUS": "worm", "TROJAN": "horse", "PROXY": "mask",
             "PATCH": "bandage", "EXPLOIT": "padlock", "SANDBOX": "cube", "NULL": "plug"}
MASCOT_NOTE = {
    "golem": "brick golem (stomps: bricks shake on each packet hit)",
    "skull": "skull (resolves from noise, jaw chatters)",
    "worm": "segmented worm (crawls across the screen, eats pixels)",
    "horse": "trojan horse head (smiles, then its eyes go red)",
    "mask": "masquerade mask (slides sideways, leaves an after-image)",
    "bandage": "bandage with a heart (heart beats as the bar fills)",
    "padlock": "cracked padlock (shackle springs open on the injected line)",
    "cube": "sandbox cube with a face (blinks inside its walls)",
    "plug": "unplugged plug (sparks once, then nothing)",
}


def mask(name):
    S = 512
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    if name == "golem":
        d.rectangle([186, 40, 326, 150], fill=255)                 # head
        d.rectangle([216, 80, 240, 104], fill=0)
        d.rectangle([272, 80, 296, 104], fill=0)
        d.rectangle([136, 160, 376, 340], fill=255)                # body
        d.rectangle([60, 170, 126, 320], fill=255)                 # arms
        d.rectangle([386, 170, 452, 320], fill=255)
        d.rectangle([160, 350, 240, 480], fill=255)                # legs
        d.rectangle([272, 350, 352, 480], fill=255)
        for y in (205, 250, 295, 400, 440):                         # mortar
            d.line([(40, y), (472, y)], fill=0, width=8)
        for y0, y1, xs in ((160, 205, (256,)), (205, 250, (196, 316)), (250, 295, (256,)), (295, 340, (196, 316))):
            for x in xs:
                d.line([(x, y0), (x, y1)], fill=0, width=8)
    elif name == "skull":
        d.ellipse([96, 40, 416, 360], fill=255)
        d.rounded_rectangle([156, 290, 356, 460], radius=24, fill=255)
        d.ellipse([150, 170, 240, 270], fill=0)
        d.ellipse([272, 170, 362, 270], fill=0)
        d.polygon([(256, 280), (230, 330), (282, 330)], fill=0)
        for x in (196, 236, 276, 316):
            d.line([(x, 380), (x, 460)], fill=0, width=12)
    elif name == "worm":
        pts = []
        for i in range(9):
            x = 60 + i * 50
            y = 280 + 90 * math.sin(i * 0.8)
            r = 58 - i * 3
            pts.append((x, y, r))
        for (x, y, r) in pts[::-1]:
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
            d.arc([x - r + 10, y - r + 10, x + r - 10, y + r - 10], 200, 340, fill=0, width=6)
        hx, hy, hr = pts[-1]
        d.ellipse([hx + 4, hy - 30, hx + 30, hy - 4], fill=0)
        d.ellipse([hx + 10, hy - 24, hx + 22, hy - 12], fill=255)
        d.line([(hx + 20, hy + 20), (hx + 40, hy + 12)], fill=0, width=8)
    elif name == "horse":  # chess-knight style head
        d.polygon([(140, 480), (150, 360), (110, 300), (130, 210), (200, 120), (250, 40), (290, 110), (360, 140),
                   (420, 230), (400, 270), (330, 260), (300, 300), (360, 380), (380, 480)], fill=255)
        d.ellipse([290, 160, 322, 192], fill=0)
        for k in range(5):
            d.line([(220 + k * 18, 120 + k * 22), (180 + k * 18, 150 + k * 22)], fill=0, width=8)
        d.rectangle([120, 440, 400, 490], fill=255)
    elif name == "mask":
        d.ellipse([40, 170, 260, 340], fill=255)
        d.ellipse([252, 170, 472, 340], fill=255)
        d.rectangle([200, 200, 312, 290], fill=255)
        d.ellipse([90, 215, 200, 285], fill=0)
        d.ellipse([312, 215, 422, 285], fill=0)
        d.polygon([(256, 300), (226, 350), (286, 350)], fill=0)
        d.line([(40, 250), (0, 330)], fill=255, width=16)
        d.line([(472, 250), (512, 330)], fill=255, width=16)
        d.polygon([(380, 170), (440, 60), (470, 90), (420, 190)], fill=255)  # feather
    elif name == "bandage":
        L = Image.new("L", (S, S), 0)
        dl = ImageDraw.Draw(L)
        dl.rounded_rectangle([10, 186, 502, 326], radius=70, fill=255)
        dl.rectangle([176, 186, 336, 326], fill=0)
        dl.rectangle([190, 200, 322, 312], fill=255)
        # heart on the pad
        dl.ellipse([210, 225, 258, 273], fill=0)
        dl.ellipse([254, 225, 302, 273], fill=0)
        dl.polygon([(212, 258), (300, 258), (256, 300)], fill=0)
        for x in (60, 100, 412, 452):
            for y in (236, 276):
                dl.ellipse([x - 8, y - 8, x + 8, y + 8], fill=0)
        m = L.rotate(-25, resample=Image.BICUBIC)
    elif name == "padlock":
        d.rounded_rectangle([110, 230, 402, 480], radius=30, fill=255)
        d.arc([150, 40, 362, 300], 180, 300, fill=255, width=46)    # shackle sprung open
        d.line([(320, 80), (360, 30)], fill=255, width=46)
        d.ellipse([226, 300, 286, 360], fill=0)
        d.rectangle([246, 340, 266, 420], fill=0)
        d.line([(130, 290), (200, 340), (170, 390), (240, 440)], fill=0, width=10)  # crack
    elif name == "cube":
        top = [(256, 60), (450, 160), (256, 260), (62, 160)]
        d.polygon(top, fill=255)
        d.polygon([(62, 170), (250, 270), (250, 480), (62, 380)], fill=200)
        d.polygon([(262, 270), (450, 170), (450, 380), (262, 480)], fill=255)
        d.ellipse([110, 280, 150, 320], fill=0)
        d.ellipse([170, 310, 210, 350], fill=0)
        d.arc([110, 330, 210, 400], 20, 120, fill=0, width=10)
    elif name == "plug":
        d.rounded_rectangle([150, 160, 362, 330], radius=30, fill=255)
        d.rectangle([196, 60, 226, 170], fill=255)
        d.rectangle([286, 60, 316, 170], fill=255)
        d.line([(256, 330), (256, 380), (180, 430), (120, 500)], fill=255, width=30)
        for (x, y) in ((380, 90), (420, 140), (400, 60)):
            d.line([(x, y), (x + 30, y - 20)], fill=255, width=10)
    return m


_cache = {}


def apply(ctx, im, strength=0.55):
    prog = ctx.prog
    name = MASCOT_OF.get(prog)
    if not name:
        return im
    W, H = im.size
    size = int(H * 0.98)
    key = (name, size)
    if key not in _cache:
        _cache[key] = mask(name).resize((size, size), Image.LANCZOS)
    mk = _cache[key]
    m = Image.new("L", (W, H), 0)
    m.paste(mk, (int(W / 2 - size / 2), int(H * 0.47 - size / 2)))
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    arr = np.asarray(im, np.float32) / 255
    mm = np.asarray(m, np.float32)[..., None] / 255
    ee = np.asarray(edge, np.float32)[..., None] / 255
    col = np.array(PROGRAMS[prog]["col"], np.float32) / 255
    # dark silhouette fill + bright outline: reads as a watermark under any skin
    arr = arr * (1 - 0.45 * mm) + mm * col * strength * 0.55 + ee * (col * 0.6 + 0.4) * strength
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
