"""line samples for the style board: chalk strokes, misregistered plates, doodles, spray mist, tally"""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
import js_tower as JT
import js_doodle as D
from f1_lib import Canvas, pol
from scipy import ndimage as ndi
ROOT = 'D:/rc_scratch/combat_redesign/punk/jinx_scribble/'
W, H = 560, 170
cv = Canvas(W, H, 3, seed=5)
base = np.zeros((cv.H, cv.W, 3), np.float32) + np.array((20, 11, 44), np.float32)
n = ndi.gaussian_filter(np.random.default_rng(2).standard_normal((cv.H, cv.W)).astype(np.float32), 9) * 90
cv.over_rgb(np.ones((cv.H, cv.W), np.float32), base + n[..., None] * np.array((0.6, 0.3, 1.0)))
NP, NC, CH = JT.NP, JT.NC, JT.CHALKC
# misregistered plate stroke
JT.neon(cv, [(20, 30), (90, 22), (160, 34), (220, 26)], NC, 4.2, 0.95, 0.4, shift=(3, -2.4))
JT.neon(cv, [(20, 30), (90, 22), (160, 34), (220, 26)], NP, 5.0, 0.98, 0.7)
# thin chalk line
JT.neon(cv, [(20, 58), (110, 52), (200, 62), (250, 56)], CH, 2.2, 0.9, 0.2)
# zigzag scribble fill
pts = []
for i in range(40):
    pts.append((20 + i * 6.2, 90 + (14 if i % 2 else -14) + math.sin(i) * 3))
JT.neon(cv, pts, NP, 2.2, 0.8, 0.3, wob=0.4)
# doodles
x = 275
for k, c in (('star', NC), ('x', NP), ('tally', NC), ('bolt', NP), ('spiral', NC), ('face', CH), ('crown', NP), ('arrow', NC)):
    JT.doodle_on(cv, JT._g(k, (x, 40 + (i := 0)), 6.5), c, 2.2, 0.5)
    x += 34 if k != 'face' else 38
# second row
x = 285
for k, c in (('star4', NP), ('x', NC), ('tally', CH), ('bolt', NC), ('spiral', NP)):
    JT.doodle_on(cv, JT._g(k, (x, 95), 6.5), c, 2.2, 0.5)
    x += 40
# spray mist + splat
mist = ndi.gaussian_filter(cv.circle_mask((470, 130), 22), 12 * 3)
cv.over(np.clip(mist * 3.4, 0, 1), NP, 0.6)
JT.splat(cv, (470, 130), 14, NP, 0.9, n=90)
mist = ndi.gaussian_filter(cv.circle_mask((380, 140), 18), 10 * 3)
cv.over(np.clip(mist * 3.4, 0, 1), NC, 0.6)
JT.splat(cv, (380, 140), 11, NC, 0.9, n=70)
# glitch sample: a white bar, cyan plate and pink plate shifted
ic = np.zeros((cv.H, cv.W), np.float32)
ic[int(128 * 3):int(150 * 3), int(40 * 3):int(210 * 3)] = 1
ic = ndi.gaussian_filter(ic, 1.2)
cv.over(np.roll(ic, (4 * 3, 5 * 3), (0, 1)), NP, 0.95)
cv.over(np.roll(ic, (-2 * 3, -4 * 3), (0, 1)), NC, 0.95)
cv.over(ic, CH, 1.0)
cv.rgba().save(ROOT + 'work/lines_strip.png')
print('ok')
