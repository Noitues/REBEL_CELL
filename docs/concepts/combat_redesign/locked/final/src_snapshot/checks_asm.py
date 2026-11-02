"""the DECISIONS 5.6 checks + the squint vs approved E10 + e10_vs_e10d.jpg.  Reads the rendered final plates; re-renders only the hover unit's arcs."""
import sys, os, json, math, itertools, copy
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import asm_r2 as A
import asm_glyphs as AG
import kglyph2 as KG
import wr2_lib as W2L
from e10lib import *
OUT = 'D:/rc_art/art-pass/docs/concepts/combat_e10_design/final/'
E10D = 'D:/rc_tmp/combat_critic/plates/waves_e10/'
REP = {}
FD = 'D:/rc_art/art-pass/assets/fonts/'
mo = ImageFont.truetype(FD + 'ShareTechMono-Regular.ttf', 18)
an = ImageFont.truetype(FD + 'Anton-Regular.ttf', 28)


def load(n):
    return Image.open(OUT + n + '.png').convert('RGB')


# ---- 1. SOAK colour-vision table
import asm_tokens as TKN
SOAK = TKN.SOAK; OLD = (70, 78, 255); OLD0 = (106, 108, 255); VIO = (160, 60, 255); L1 = (120, 170, 255); CYN = (92, 225, 255)
tab = {}
for mode in ('normal', 'deutan', 'protan', 'tritan'):
    def sim(c):
        return c if mode == 'normal' else W2L.sim_rgb(c, mode)
    tab[mode] = {'SOAK vs TRACE_VIOLET': round(W2L.dE(sim(SOAK), sim(VIO)), 1), 'SOAK vs LANE_PLUS1': round(W2L.dE(sim(SOAK), sim(L1)), 1), 'SOAK vs CYAN': round(W2L.dE(sim(SOAK), sim(CYN)), 1),
                 'Y1 #464EFF vs TRACE_VIOLET': round(W2L.dE(sim(OLD), sim(VIO)), 1), 'old #6A6CFF vs TRACE_VIOLET': round(W2L.dE(sim(OLD0), sim(VIO)), 1)}
lumf = lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
tab['luma'] = {'SOAK': round(lumf(SOAK), 1), 'LANE_PLUS1': round(lumf(L1), 1), 'darker_than_LANE_PLUS1': lumf(SOAK) < lumf(L1)}
REP['soak_cvd'] = tab

# ---- no old soak pixels left in the plates
old_left = {}
for n in ('p1_decide', 'p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords'):
    a = np.asarray(load(n), np.int16)
    old_left[n] = int((np.abs(a - np.array(OLD)).sum(-1) < 14).sum())
    old_left[n + '_new'] = int((np.abs(a - np.array(SOAK)).sum(-1) < 14).sum())
REP['old_soak_pixels'] = old_left

# ---- 2. twin check
twin = {}
ids = list(KG.IDS)
for px in (16, 20, 28, 37, 44, 70):
    pairs = []
    for a_, b_ in itertools.combinations(ids, 2):
        pairs.append((round(KG.iou(AG.mask(a_), AG.mask(b_), px), 3), a_, b_))
    pairs.sort(reverse=True)
    twin[px] = pairs[:6]
REP['twin_top'] = {str(k): v for k, v in twin.items()}
nn = {}
for g in ids:
    best = max(((KG.iou(AG.mask(g), AG.mask(h), 28), h) for h in ids if h != g))
    nn[g] = (best[1], round(best[0], 3))
REP['twin_nearest_28'] = nn

# ---- 3. spoke continuity

# O2: label boxes of the hold cells (angle range of the HOLD text + glyph disc, radial band B0-1 .. B1+1); the spoke continuity metric is measured outside them
def _label_boxes():
    sch = A.J['f1']['schedule']
    cum = 0; out = []
    for v in sch:
        if v == 0:
            out.append((cum + 4.0, cum + 40.0)); cum += 40
        else:
            cum += 60 * v
    return out
LABELS = _label_boxes()
def in_label(k, r):
    a = (30 + 60 * k) % 360
    return r >= 357.4 and r <= 385.0 and any(lo <= a <= hi for lo, hi in LABELS)
im = np.asarray(load('p1_decide'), np.float32)
INKv = np.array([12, 10, 22], np.float32)


def dark_run(x, y, nx, ny, lim=12, tol=26):
    """width (px) of the contiguous INK-coloured run across the line at (x, y), normal (nx, ny)"""
    w = 0
    for sgn in (1, -1):
        d = 0.0 if sgn == 1 else 0.5
        while d < lim:
            xx, yy = x + sgn * nx * d, y + sgn * ny * d
            p = im[int(round(yy)), int(round(xx))]
            if np.abs(p - INKv).sum() > tol:
                break
            d += 0.5
        w += d - (0.0 if sgn == 1 else 0.5)
    return w


spk = {}
bad = []
for k in range(6):
    a = math.radians(30 + 60 * k)
    t = (math.sin(a), -math.cos(a)); nrm = (math.cos(a), math.sin(a))
    for lo, hi, nm in ((158, 162, 'r158-162'), (160, 164, 'r160-164'), (163, 166, 'r163-166 (wide ring-0 cells cover it by design)'), (353, 357, 'r353-357'), (353, 360, 'r353-360'), (357, 359, 'r357-359')):
        for r in np.arange(lo, hi + 0.01, 0.5):
            if in_label(k, r):
                continue
            for off in (-3.0, 0.0, 3.0):
                x, y = C[0] + r * t[0] + off * nrm[0], C[1] + r * t[1] + off * nrm[1]
                p = im[int(round(y)), int(round(x))]
                if np.abs(p - INKv).sum() > 40:
                    bad.append((k, nm, float(r), off, [int(v) for v in p]))
        # edge test: the strip must be 8 px wide: +-5 px off the line is NOT ink at least once per band (lit cells beside the strip) - reported as a width profile
        ws = []
        for r in np.arange(lo, hi + 0.01, 1.0):
            x, y = C[0] + r * t[0], C[1] + r * t[1]
            w = 0.0
            for sgn in (1, -1):
                d = 0.0
                while d < 6.0:
                    p = im[int(round(y + sgn * nrm[1] * d)), int(round(x + sgn * nrm[0] * d))]
                    if np.abs(p - INKv).sum() > 40:
                        break
                    d += 0.5
                w += d
            ws.append(w)
        spk[(k, nm)] = ws
REP['spoke_ink_gaps'] = bad
REP['spoke_ink_samples_bad'] = len(bad)
REP['spoke_widths_cap6'] = {'%d_%s' % key: v for key, v in spk.items()}

# ---- 5. nameplate radius (alpha of the sticker layer inside the nameplate box)
lay, info = A.AS.stack_layer(True, {})
al = np.asarray(lay.split()[3])
x0, y0, nw, nh = [int(v) for v in info['name']]
ys, xs = np.nonzero(al[:, :700] > 8)
rr = np.hypot(xs - C[0], ys - C[1])
REP['nameplate'] = dict(box=info['name'], min_r_alpha8=round(float(rr.min()), 1), min_r_alpha64=round(float(np.hypot(*(np.nonzero(al[:, :700] > 64)[1] - C[0], np.nonzero(al[:, :700] > 64)[0] - C[1])).min()), 1))

# ---- 6. badges
meta = json.load(open(A.ROOT + 'out/meta.json'))
REP['badges'] = {b: meta[b]['badges'] for b in meta}
REP['hud_bottoms'] = {b: meta[b]['hud_bottom'] for b in meta}

# ---- 8. hover tag vs the hovered unit's landing arc
A.setup()
f = copy.deepcopy(A.J['f1'])
hid = A.J['hover']['id']
Lt = L2()
A.E.reg_reset()
A.A2.landing_arcs(Lt, f, {}, only={hid})
arc = Lt.done().split()[3]
arc = np.asarray(arc) > 8
box = meta['p2b']['hover_tag_box']
bx0, by0, bx1, by1 = [int(v) for v in box]
sub = arc[by0:by1, bx0:bx1]
ys, xs = np.nonzero(sub)
ay, ax = np.nonzero(arc)
REP['hover_tag'] = dict(tag_box=[bx0, by0, bx1, by1], arc_bbox=[int(ax.min()), int(ay.min()), int(ax.max()), int(ay.max())], arc_px=int(arc.sum()),
                        covered_px=int(sub.sum()), overlap_bbox=([int(xs.min() + bx0), int(ys.min() + by0), int(xs.max() + bx0), int(ys.max() + by0)] if len(xs) else None))

# ---- 9. squint
def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def squint(img):
    s = img.resize((img.width // 16, img.height // 16), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
    a = np.asarray(s, np.float32) / 255.0
    l = lum(a)
    return dict(mean=round(float(l.mean()), 4), p95=round(float(np.percentile(l, 95)), 4), loud_gt_0_38=round(float((l > 0.38).mean()), 4)), s


e10 = Image.open(E10D + 'p1_decide.png').convert('RGB')
new = load('p1_decide')
sq_new, s_new = squint(new)
sq_old, s_old = squint(e10)
REP['squint'] = dict(new=sq_new, e10=sq_old)
for nm in ('p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords'):
    REP['squint_' + nm] = dict(new=squint(load(nm))[0], e10=squint(Image.open(E10D + nm + '.png').convert('RGB'))[0])

# ---- e10 vs e10d
cmp_ = Image.new('RGB', (1920, 560), (10, 12, 20))
cmp_.paste(e10.resize((960, 540), Image.LANCZOS), (0, 20))
cmp_.paste(new.resize((960, 540), Image.LANCZOS), (960, 20))
d = ImageDraw.Draw(cmp_)
d.text((8, 0), 'E10 approved p1_decide', font=mo, fill=(255, 226, 0))
d.text((968, 0), 'E10 redesign (assembled) p1_decide', font=mo, fill=(255, 226, 0))
cmp_.save(OUT + 'e10_vs_e10d.jpg', quality=90)

# ---- squint + deutan + tritan sheets (p1 and p2b)
def sheet(names, fn):
    sh = Image.new('RGB', (1920, 60 + len(names) * 3 * 300), (10, 12, 20))
    d = ImageDraw.Draw(sh)
    d.text((16, 14), 'assembled E10: 320 px squint (3x nearest) | deutan | tritan (Machado 1.0)', font=an, fill=(255, 255, 255))
    y = 60
    for n in names:
        im = load(n)
        sq = im.resize((320, 180), Image.LANCZOS)
        row = [sq.resize((640, 360), Image.NEAREST), W2L.sim_cb(im, 'deutan').resize((640, 360), Image.LANCZOS), W2L.sim_cb(im, 'tritan').resize((640, 360), Image.LANCZOS)]
        for i, r in enumerate(row):
            sh.paste(r, (i * 640, y))
        d.text((8, y + 4), n + ' squint', font=mo, fill=(255, 226, 0)); d.text((648, y + 4), n + ' deutan', font=mo, fill=(255, 226, 0)); d.text((1288, y + 4), n + ' tritan', font=mo, fill=(255, 226, 0))
        y += 370
    sh.crop((0, 0, 1920, y)).save(fn, quality=88)


sheet(['p1_decide', 'p2b_hover'], OUT + 'checks_squint_deutan_tritan.jpg')

# ---- soak notch at 320 px: crops of p1 (SPLIT row and the slice soak mark) at full size and at the 320 px scale shown 4x
def crop4(img, box, k):
    c = img.crop(box)
    return c.resize((c.width * k, c.height * k), Image.NEAREST)


p1 = load('p2_preview')       # p2 has soak on the SHIELD slice (mark, break X, pip) and the SOAK chips
s320 = p1.resize((320, 180), Image.LANCZOS)
sh = Image.new('RGB', (1920, 700), (10, 12, 20))
sh.paste(crop4(s320, (92, 66, 126, 96), 10), (0, 30))                                     # shield slice at 320 px, 10x nearest
sh.paste(p1.crop((552, 410, 712, 560)).resize((480, 450), Image.LANCZOS), (360, 30))     # the same at 1920, 3x
sh.paste(p1.crop((1085, 322, 1495, 362)).resize((1230, 120), Image.LANCZOS), (700, 30))  # BRACE + SOAK ONLY row at 1920, 3x
sh.paste(crop4(s320, (180, 52, 250, 66), 10), (700, 170))                                 # that row at 320 px, 10x nearest
d = ImageDraw.Draw(sh)
d.text((4, 4), 'SOAK #3A7EF3 (notch 5 px, 1 px INK keyline) on p2: shield slice at 320 px (10x) | at 1920 (3x) | chip row at 1920 and 320 px', font=mo, fill=(255, 226, 0))
sh.save(OUT + 'checks_soak_notch.jpg', quality=90)
# ---- R3 spoke continuity (run-width metric: contiguous INK run through the spoke axis, tol 60 (max channel step 20: a faint 1 px teal hairline of the board texture at 330 deg is r354 is under it); a break = run < 6 px)
def run_w(x, y, nx, ny, lim=10.0, tol=60):
    w = 0.0
    for sgn in (1, -1):
        d = 0.0
        while d < lim:
            p = im[int(round(y + sgn * ny * d)), int(round(x + sgn * nx * d))]
            if np.abs(p - INKv).sum() > tol:
                break
            d += 0.5
        w += d
    return w
spk2 = {}
for k in range(6):
    a = math.radians(30 + 60 * k)
    t = (math.sin(a), -math.cos(a)); nrm = (math.cos(a), math.sin(a))
    for lo, hi, nm in ((158, 162, 'r158-162'), (160, 164, 'r160-164'), (163, 166, 'r163-166'), (353, 357, 'r353-357'), (353, 360, 'r353-360')):
        ws = [run_w(C[0] + r * t[0], C[1] + r * t[1], nrm[0], nrm[1]) for r in np.arange(lo, hi + 0.01, 0.5) if not in_label(k, r)]
        spk2['%d_%s' % (k, nm)] = dict(min_run=round(min(ws), 1) if ws else None, breaks=int(sum(1 for w in ws if w < 6.0)))
REP['spoke_runs'] = spk2
# ---- R3 fix-pass extra checks
import measure_regions as MR
bx0, by0, bx1, by1 = [int(v) for v in box]
cornr = [math.hypot(x - C[0], y - C[1]) for x, y in ((bx0, by0), (bx1, by0), (bx0, by1), (bx1, by1))]
# nearest point of the box to the board centre
nx_, ny_ = min(max(C[0], bx0), bx1), min(max(C[1], by0), by1)
Lt2 = L2(); A.E.reg_reset(); A.A2.landing_arcs(Lt2, copy.deepcopy(A.J['f1']), {}, only={hid})
arc_h = np.asarray(Lt2.done().split()[3]) > 8
Lt3 = L2(); A.E.reg_reset(); A.A2.landing_arcs(Lt3, copy.deepcopy(A.J['f1']), {})
arc_all = np.asarray(Lt3.done().split()[3]) > 8
ov_h = int(arc_h[by0:by1, bx0:bx1].sum()); ov_all = int(arc_all[by0:by1, bx0:bx1].sum())
REP['hover_tag_r3'] = dict(box=[bx0, by0, bx1, by1], min_r_from_board_centre=round(math.hypot(nx_ - C[0], ny_ - C[1]), 1), hud_bottom_p2b=meta['p2b']['hud_bottom'], overlap_px_hovered_arc=ov_h, overlap_px_any_landing_arc=ov_all, overlap_px_board_disc_r516=int(((np.hypot(np.arange(bx0, bx1)[None, :] - C[0], np.arange(by0, by1)[:, None] - C[1])) <= 516).sum()))
# ---- board identical in all five states (shadow / ground): pixels with r in 516..700 from C, x < 1000, outside the nameplate box, the p2b tag box and the p2b leader
yy_, xx_ = np.mgrid[0:1080, 0:1920]; rho_ = np.hypot(xx_ - C[0], yy_ - C[1])
names5 = ('p1_decide', 'p2_preview', 'p2b_hover', 'p3_resolve', 'p1_nowords')
ims5 = {n: np.asarray(load(n), np.float32) for n in names5}
nx0, ny0, nw_, nh_ = [int(v) for v in info['name']]
msk = (rho_ >= 516) & (rho_ < 700) & (xx_ < 1000)
msk &= ~((xx_ >= nx0 - 30) & (xx_ <= nx0 + nw_ + 30) & (yy_ >= ny0 - 30) & (yy_ <= ny0 + nh_ + 30))
msk &= ~((xx_ >= 840) & (yy_ >= 470) & (yy_ <= 620))      # the p2b leader's exit corridor toward the tag
sd = {}
for n in names5[1:]:
    dd_ = np.abs(ims5[n] - ims5['p1_decide']).sum(-1)
    sd[n] = dict(px_diff_gt6=int(((dd_ > 6) & msk).sum()), mean_signed_lum_diff=round(float((ims5[n] - ims5['p1_decide']).mean(-1)[msk].mean()), 3))
REP['board_outer_ground_vs_p1'] = sd
# ---- region squint on every plate (room hull vs board disc)
REP['region_squint'] = {n: MR.measure(load(n)) for n in names5}
for nm in ('srv', 'gh'):
    REP['region_squint']['p1_decide_' + nm] = MR.measure(load('p1_decide_' + nm))
REP['region_squint']['e10_approved_p1'] = MR.measure(Image.open(E10D + 'p1_decide.png').convert('RGB'))
# nameplate squint spot
sq_ = MR.squint(load('p1_decide'))
REP['nameplate_squint'] = dict(box=info['name'], centre=round(float(sq_[int((ny0 + nh_ / 2) // 16), int((nx0 + nw_ / 2) // 16)]), 3), peak=round(float(sq_[ny0 // 16:(ny0 + nh_) // 16 + 1, nx0 // 16:(nx0 + nw_) // 16 + 1].max()), 3),
                               send_it_peak=round(float(sq_[870 // 16:(870 + 178) // 16, 1625 // 16:(1625 + 297) // 16].max()), 3), hand_peak=round(float(sq_[832 // 16:1080 // 16, 1010 // 16:1625 // 16].max()), 3))
# ---- jammer glyph arc stroke at 20 px
gm = AG.mask('jammer')
import PIL.Image as _I
REP['jammer_stroke'] = 'arc stroke 52 mask units = %.2f px at 20 px (was 40 units = %.2f px)' % (52 / 512 * 20, 40 / 512 * 20)
json.dump(REP, open(A.ROOT + 'out/checks.json', 'w'), indent=1, default=str)
print(json.dumps(REP, indent=1, default=str)[:6000])
