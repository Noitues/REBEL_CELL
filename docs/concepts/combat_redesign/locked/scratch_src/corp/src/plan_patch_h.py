"""plan_patch: brings the E10 generator's board onto the VISUAL_PLAN grammar for the hover plates (monkey patches in the working COPY only).
 - no dashed line anywhere: lane +2 = L8 dotted, growth chevrons = hollow outline, tracers = solid pink painted stroke (L2)
 - lane outlines are neutral ENAMEL and carry the time grammar (NOW hot solid / +1 cold thinner / +2 far dotted), no red / blue / white lane colours
 - HP lost at END TURN = L7 cross-hatch (red = enemy hit, pink = we take it), the white slash is retired
 - enemy units use the cool slate set; tokens carry an ENAMEL rim
 - hub rim / tracers in the player's pink
"""
import sys, math
sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

PINK = (255, 61, 168)
ENAMEL = (217, 225, 234)
HARM = (255, 68, 51)
INKC = (12, 10, 22)
SLATE = {'Packet': (61, 84, 102), 'Worm': (75, 74, 110), 'Jammer': (45, 93, 105), 'Payload': (91, 85, 96), 'Ring': (85, 97, 122)}




def hatch_poly(L, pts, col, pitch=4.0, lw=1.5, base=None, alpha=255, edge=0.0, both=True):
    """L7 cross-hatch clipped to the polygon pts (1080p px); base = optional solid fill under the hatch; edge = solid outline width"""
    k = L.k
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, y0 = int(min(xs)) - 3, int(min(ys)) - 3
    x1, y1 = int(max(xs)) + 4, int(max(ys)) + 4
    w, h = (x1 - x0) * k, (y1 - y0) * k
    if w <= 0 or h <= 0:
        return
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).polygon([((x - x0) * k, (y - y0) * k) for x, y in pts], fill=255)
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if base is not None:
        d.rectangle([0, 0, w, h], fill=tuple(base) + (255,))
    c = tuple(col) + (255,)
    step = pitch * k
    n = int((w + h) / step) + 2
    for i in range(n):
        o = i * step
        d.line([(o - h, h), (o, 0)], fill=c, width=max(1, int(lw * k)))                 # 45 deg
        if both:
            d.line([(o - h, 0), (o, h)], fill=c, width=max(1, int(lw * k)))             # 135 deg
    if edge:
        pp = [((x - x0) * k, (y - y0) * k) for x, y in pts]
        d.line(pp + [pp[0]], fill=c, width=max(1, int(edge * k)), joint='curve')
        m2 = Image.new('L', (w, h), 0)
        ImageDraw.Draw(m2).polygon(pp, fill=255)
        mask = m2
    if alpha != 255:
        mask = mask.point(lambda v: int(v * alpha / 255))
    lay.putalpha(Image.fromarray((np.array(lay.split()[3]).astype(np.uint16) * np.array(mask).astype(np.uint16) // 255).astype(np.uint8)))
    L.im.alpha_composite(lay, (x0 * k, y0 * k))


