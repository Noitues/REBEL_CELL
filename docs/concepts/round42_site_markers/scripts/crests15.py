"""Round 15 crest glyphs (512 box masks): Halcyon's EYE and REBEL_CELL's raised FIST."""
import math
from PIL import Image, ImageDraw

S = 512


def eye():
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    # almond: two circular arcs meeting at the corners
    pts = []
    for k in range(61):
        a = math.radians(180 + 180 * k / 60)
        pts.append((256 + 230 * math.cos(a), 256 + 150 * math.sin(a) * 0.95))
    for k in range(61):
        a = math.radians(180 * k / 60)
        pts.append((256 + 230 * math.cos(a), 256 + 150 * math.sin(a) * 0.95))
    d.polygon(pts, fill=255)
    inner = [(256 + (x - 256) * 0.80, 256 + (y - 256) * 0.68) for x, y in pts]
    d.polygon(inner, fill=0)
    d.ellipse([256 - 92, 256 - 92, 256 + 92, 256 + 92], fill=255)
    d.ellipse([256 - 40, 256 - 40, 256 + 40, 256 + 40], fill=0)
    d.ellipse([256 + 22, 256 - 62, 256 + 52, 256 - 32], fill=0)
    for k in (-2, -1, 0, 1, 2):  # lashes on the upper lid
        a = math.radians(-90 + k * 26)
        x0, y0 = 256 + 200 * math.cos(a) * 0.95, 256 + 150 * math.sin(a) * 0.95
        d.line([(x0, y0), (x0 + 50 * math.cos(a), y0 + 50 * math.sin(a))], fill=255, width=26)
    return m


def fist():
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([196, 330, 332, 500], radius=24, fill=255)  # forearm
    d.rounded_rectangle([132, 120, 380, 352], radius=56, fill=255)  # fist block
    for k in range(4):  # knuckles
        x = 168 + k * 60
        d.ellipse([x - 36, 92, x + 36, 164], fill=255)
    for k in range(3):  # finger splits
        x = 198 + k * 60
        d.line([(x, 108), (x, 238)], fill=0, width=18)
    d.rounded_rectangle([118, 236, 312, 300], radius=32, fill=255)  # thumb across the front
    d.line([(150, 236), (300, 236)], fill=0, width=16)
    d.line([(196, 338), (332, 338)], fill=0, width=14)  # cuff line at the wrist
    return m


CUSTOM = {"EYE": eye, "FIST": fist}
