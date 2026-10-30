"""Draws the real prism roof centres (CityIsoCamera projection of the dumped data) over the frame-1 capture, to prove data and camera line up."""
import json, math, sys
from PIL import Image, ImageDraw
d = json.load(open('D:/rc_scratch/netrun_cel/city/lots_city.json')); cam = d['camera']
yaw = math.radians(cam['yaw']); pit = math.radians(cam['pitch'])
f = (math.cos(yaw) * math.cos(pit), -math.sin(pit), -math.sin(yaw) * math.cos(pit)); r = (math.sin(yaw), 0, math.cos(yaw))
u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
T = cam['target']; O = cam['ortho']; vp = cam['viewport']
def proj(w):
    dx = [w[k] - T[k] for k in range(3)]
    xc = sum(dx[k] * r[k] for k in range(3)); yc = sum(dx[k] * u[k] for k in range(3)); oh = O * vp[1] / vp[0]
    return ((xc / O + .5) * vp[0], (.5 - yc / oh) * vp[1])
im = Image.open(sys.argv[1]).convert('RGB'); dr = ImageDraw.Draw(im)
for p in d['prisms']:
    xs = [q[0] for q in p['poly']]; zs = [q[1] for q in p['poly']]
    cx = sum(xs) / len(xs); cz = sum(zs) / len(zs)
    top = proj((cx, p['y0'] + p['h'], cz)); bot = proj((cx, p['y0'], cz))
    if 1000 < top[0] < 1700 and 300 < top[1] < 800:
        dr.ellipse((top[0] - 3, top[1] - 3, top[0] + 3, top[1] + 3), outline=(255, 0, 0)); dr.line((top[0], top[1], bot[0], bot[1]), fill=(255, 255, 0))
im.crop((1010, 380, 1650, 740)).resize((1920, 1080), Image.LANCZOS).save(sys.argv[2])
