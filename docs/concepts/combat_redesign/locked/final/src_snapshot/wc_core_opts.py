"""tower-material element options: hub (disc, rings, label, emblem), slice frame / screen / code text / gutters, icons, code-base frame."""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import wc_base as WB
import wc_tower as T
import wc_glyphs
import slicelib as SL
import roster_wheel as RW_
from cv_lib import RS, anton, mono, C
CYAN = (92, 225, 255); INK = (12, 10, 22); WHITE = (242, 246, 255)
KE = T.KE


def sc(x, ss):            # screen px -> canvas px
    return x / KE * ss


def _layer(over):
    return Image.new('RGBA', over.size, (0, 0, 0, 0))


def _comp(over, lay):
    over.alpha_composite(lay)


def ring(d, cx, cy, r, col, w, ss, a0=None, a1=None):
    box = [cx - sc(r, ss), cy - sc(r, ss), cx + sc(r, ss), cy + sc(r, ss)]
    if a0 is None:
        d.ellipse(box, outline=col, width=max(1, int(sc(w, ss))))
    else:
        d.arc(box, a0, a1, fill=col, width=max(1, int(sc(w, ss))))


def disc_fill(d, cx, cy, r, col, ss):
    d.ellipse([cx - sc(r, ss), cy - sc(r, ss), cx + sc(r, ss), cy + sc(r, ss)], fill=col)


# ============================================================ hub
def hub_factory(disc='cur', rings='cur', label='cur', emblem='cur'):
    def fn(over, d, ss, cx, cy, nowords):
        HR = RS['hub']                                   # screen px
        # --- disc
        if disc == 'cur':
            disc_fill(d, cx, cy, HR, (14, 12, 20, 255), ss); ring(d, cx, cy, HR - 1.0, CYAN + (255,), 2.0, ss)
        else:
            lay = _layer(over); ld = ImageDraw.Draw(lay)
            if disc == 'A':        # quiet lens: near-black, one medium cyan rim, faint inner bevel
                disc_fill(ld, cx, cy, HR + 1.5, INK + (255,), ss)
                disc_fill(ld, cx, cy, HR, (6, 8, 14, 255), ss)
                ring(ld, cx, cy, HR - 1.6, (84, 206, 232, 255), 3.2, ss)
                ring(ld, cx, cy, HR - 4.6, (255, 255, 255, 46), 1.0, ss, 190, 300)
                ring(ld, cx, cy, HR - 4.6, (0, 0, 0, 90), 1.0, ss, 10, 120)
            elif disc == 'B':      # socket: heavy dim rim + dark halo ring around
                disc_fill(ld, cx, cy, HR + 3.5, (3, 4, 8, 255), ss)
                disc_fill(ld, cx, cy, HR, (9, 11, 19, 255), ss)
                ring(ld, cx, cy, HR - 2.0, (58, 160, 186, 255), 4.0, ss)
                ring(ld, cx, cy, HR - 4.6, INK + (255,), 1.2, ss)
            else:                  # CRT dome: scanlines + glint, thinner bright rim
                disc_fill(ld, cx, cy, HR + 1.2, INK + (255,), ss)
                disc_fill(ld, cx, cy, HR, (5, 7, 12, 255), ss)
                for y in range(int(-HR) + 3, int(HR) - 2, 4):
                    hw = math.sqrt(max(0, HR * HR - y * y)) - 3
                    ld.line([(cx - sc(hw, ss), cy + sc(y, ss)), (cx + sc(hw, ss), cy + sc(y, ss))], fill=(60, 120, 140, 26), width=max(1, int(sc(1, ss))))
                ring(ld, cx, cy, HR - 1.4, (92, 225, 255, 235), 2.6, ss)
                ring(ld, cx, cy, HR - 7, (255, 255, 255, 60), 2.0, ss, 205, 255)
            _comp(over, lay)
        # --- inner rings
        if rings == 'cur':
            for rr in range(16, int(HR / 1.0 * 1.0) - 6 + 0, 9):
                pass
            lay = _layer(over); ld = ImageDraw.Draw(lay)
            hr_m = HR / KE
            for rr in range(16, int(hr_m) - 6, 9):
                ld.ellipse([cx - rr * ss, cy - rr * ss, cx + rr * ss, cy + rr * ss], outline=(255, 255, 255, 10), width=ss)
            _comp(over, lay)
        elif rings == 'A':
            lay = _layer(over); ld = ImageDraw.Draw(lay)
            ring(ld, cx, cy, 33, (255, 255, 255, 50), 1.2, ss, 180, 300); ring(ld, cx, cy, 33, (0, 0, 0, 110), 1.2, ss, 0, 120)
            _comp(over, lay)
        elif rings == 'B':
            lay = _layer(over); ld = ImageDraw.Draw(lay)
            ld.pieslice([cx - sc(36, ss), cy - sc(36, ss), cx + sc(36, ss), cy + sc(36, ss)], 195, 285, fill=(255, 255, 255, 20))
            ld.pieslice([cx - sc(36, ss), cy - sc(36, ss), cx + sc(36, ss), cy + sc(36, ss)], 195, 285, fill=(0, 0, 0, 0))
            lay2 = _layer(over); l2 = ImageDraw.Draw(lay2)
            l2.ellipse([cx - sc(37, ss), cy - sc(37, ss), cx + sc(37, ss), cy + sc(37, ss)], fill=(255, 255, 255, 16))
            l2.ellipse([cx - sc(30, ss), cy - sc(27, ss) + sc(5, ss), cx + sc(34, ss), cy + sc(37, ss) + sc(5, ss)], fill=(0, 0, 0, 0))
            m = Image.new('L', over.size, 0); md = ImageDraw.Draw(m)
            md.ellipse([cx - sc(37, ss), cy - sc(37, ss), cx + sc(37, ss), cy + sc(37, ss)], fill=255)
            md.ellipse([cx - sc(31, ss) + sc(7, ss), cy - sc(31, ss) + sc(8, ss), cx + sc(37, ss) + sc(7, ss), cy + sc(37, ss) + sc(8, ss)], fill=0)
            sheen = Image.new('RGBA', over.size, (255, 255, 255, 30)); sheen.putalpha(m.point(lambda v: 30 if v else 0))
            _comp(over, sheen)
        else:
            lay = _layer(over); ld = ImageDraw.Draw(lay)
            ring(ld, cx, cy, 35, (255, 255, 255, 34), 1.3, ss)
            _comp(over, lay)
        # --- emblem
        def emb(name, px, dy, col, outline_k=0.08, alpha=255):
            g = SL.glyph_rgba(name, int(sc(px, ss)), max(2, int(sc(px, ss) * outline_k)), fill=col)
            if alpha < 255:
                g = g.copy(); g.putalpha(g.split()[3].point(lambda v: v * alpha // 255))
            over.alpha_composite(g, (int(cx - g.width / 2), int(cy + sc(dy, ss) - g.height / 2)))
        has_word = label in ('cur', 'A', 'C') and not nowords
        if emblem == 'cur':
            es = 40 / KE
            g = RW_.tinted_glyph(RW_.CLASS_STYLE['breaker']['emblem'], int(es * ss), CYAN)
            over.alpha_composite(g, (int(cx - g.width / 2), int(cy - (RS['hub'] / KE) * 0.62 * ss - g.height / 2)))
        else:
            nm = {'A': 'WC_EMB_A', 'B': 'WC_EMB_B', 'C': 'WC_EMB_C'}[emblem]
            col = {'A': (96, 214, 240), 'B': (214, 96, 168), 'C': (214, 226, 240)}[emblem]
            if has_word:
                emb(nm, 24, -17, col, alpha=235)
            else:
                emb(nm, 34, 0, col, alpha=235)
        # --- label
        if nowords:
            return
        if label == 'cur':
            fb = anton(int(27 * ss))
            w = fb.getlength('BREAKER'); d.text((cx - w / 2, cy - 8 * ss), 'BREAKER', font=fb, fill=(255, 255, 255, 255), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255)) if False else None
            fs = 27 - 4
            fb = anton(int(fs * ss)); w = fb.getlength('BREAKER')
            d.text((cx - w / 2, cy - 8 * ss), 'BREAKER', font=fb, fill=(255, 255, 255, 255), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))
        elif label == 'A':
            px = 17 / KE * ss
            fb = anton(int(px)); lay = _layer(over); ld = ImageDraw.Draw(lay)
            ld.text((cx, cy + sc(12, ss)), 'BREAKER', font=fb, fill=(246, 249, 255, 255), anchor='mm', stroke_width=max(2, int(sc(2.0, ss))), stroke_fill=INK + (255,))
            _comp(over, lay)
        elif label == 'C':
            fb = mono(int(16 / KE * ss)); lay = _layer(over); ld = ImageDraw.Draw(lay)
            wch = fb.getlength('BREAKER') / ss * KE + 12
            ld.rounded_rectangle([cx - sc(wch / 2, ss), cy + sc(5, ss), cx + sc(wch / 2, ss), cy + sc(25, ss)], radius=int(sc(5, ss)), fill=(4, 6, 12, 255), outline=(84, 206, 232, 230), width=max(1, int(sc(1.6, ss))))
            ld.text((cx, cy + sc(15.5, ss)), 'BREAKER', font=fb, fill=(226, 240, 250, 255), anchor='mm')
            _comp(over, lay)
        # label 'B' = no word
    return fn


def cfg_with(**kw):
    c = WB.cur_cfg(); c['tile'] = dict(c['tile'])
    for k, v in kw.items():
        if k == 'tile':
            c['tile'].update(v)
        else:
            c[k] = v
    return c


# ============================================================ slice frame / gutters
G8 = 4.0 / KE        # master half-gap for an 8 px gutter
FRAME = {
    'A': dict(gap_side=G8, gap_in=G8, bw=6.0, r_t_out=9.0, r_t_in=9.0, r_s_out=9, r_s_in=8, edge_w=3.0, edge_gain=0.95, ink_w=2.4, hair_gain=0.5, led=False),
    'B': dict(gap_side=G8, gap_in=G8, bw=8.5, r_t_out=12.0, r_t_in=12.0, r_s_out=12, r_s_in=10, hair_w=1.8, hair_gain=1.9, ink_w=3.0, led=False, bevel=0.8),
    'C': dict(gap_side=G8, gap_in=G8, bw=5.0, r_t_out=10.0, r_t_in=10.0, r_s_out=10, r_s_in=9, edge_w=4.2, edge_gain=1.0, ink_w=2.0, led=False, glass=0.5, hair_gain=0.0),
}
# ============================================================ gutters (tile params)
def gutter_cfg(kind):
    base = dict(gap_side=G8, gap_in=G8)
    if kind == 'A':
        return cfg_with(tile=base)
    if kind == 'B':
        def post(L):             # one radial ink strip hub -> frame, through the HP ring
            for s in range(6):
                a = 60 * s + 30
                L.line([WB.ppx(C, 44, a), WB.ppx(C, 159, a)], (3, 4, 8), 8)
        c = cfg_with(tile=base); c['post_frame'] = post
        return c
    def postc(L):
        for s in range(6):
            a = 60 * s + 30
            L.line([WB.ppx(C, 44, a), WB.ppx(C, 159, a)], (3, 4, 8), 8)
            L.line([WB.ppx(C, 46, a), WB.ppx(C, 157, a)], (40, 46, 62), 1.2)
    c = cfg_with(tile=dict(gap_side=G8, gap_in=G8)); c['post_frame'] = postc
    return c


# ============================================================ code-base frame
def frame_factory(kind):
    def fn(over, d, ss, cx, cy):
        lay = _layer(over); ld = ImageDraw.Draw(lay)
        R = 158.4
        if kind == 'A':       # one fine cyan ring + ink line outside
            ring(ld, cx, cy, R + 1.5, INK + (255,), 2.2, ss)
            ring(ld, cx, cy, R, CYAN + (255,), 1.6, ss)
        elif kind == 'B':     # ring with a bracket tick at each sector boundary
            ring(ld, cx, cy, R + 1.5, INK + (255,), 2.2, ss)
            ring(ld, cx, cy, R, CYAN + (235,), 1.4, ss)
            for s in range(6):
                a = math.radians(60 * s + 30)
                p0 = (cx + sc(R - 4, ss) * math.sin(a), cy - sc(R - 4, ss) * math.cos(a)); p1 = (cx + sc(R + 1.6, ss) * math.sin(a), cy - sc(R + 1.6, ss) * math.cos(a))
                ld.line([p0, p1], fill=CYAN + (255,), width=max(1, int(sc(3, ss))))
        else:                 # six arcs, one per sector, split at the gutters
            for s in range(6):
                a0, a1 = 60 * s - 90 - 26.5, 60 * s - 90 + 26.5
                ring(ld, cx, cy, R + 1.5, INK + (255,), 2.2, ss, a0, a1)
                ring(ld, cx, cy, R, CYAN + (255,), 2.0, ss, a0, a1)
        _comp(over, lay)
    return fn


# ============================================================ screen textures
def _u8(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def tex_factory(material='A', code='A'):
    def fn(ctx):
        ss, Wt, Ht = ctx.ss, ctx.W, ctx.H
        col = np.array(ctx.col, np.float32) / 255.0
        rng = np.random.default_rng(100 + ctx.seed)
        yy, xx = np.mgrid[0:Ht, 0:Wt].astype(np.float32)
        base = np.full((Ht, Wt), 0.10, np.float32)
        lum = base.copy()
        pitch = 3.4 * ss
        if material == 'A':        # phosphor mesh
            gx = np.cos(2 * np.pi * xx / pitch) * 0.5 + 0.5; gy = np.cos(2 * np.pi * yy / pitch) * 0.5 + 0.5
            lum += 0.10 * (gx * gy) ** 2
            lum += 0.04 * (np.cos(2 * np.pi * yy / (pitch * 3)) * 0.5 + 0.5)
        elif material == 'B':      # column rain
            colw = 7.0 * ss
            ci = np.floor(xx / colw)
            ph = rng.random(int(Wt / colw) + 2)[ci.astype(int)]
            ln = 0.4 + 0.5 * rng.random(int(Wt / colw) + 2)[ci.astype(int)]
            v = ((yy / Ht + ph) % 1.0)
            streak = np.clip(1 - v / ln, 0, 1) ** 1.6
            inside = (np.cos(2 * np.pi * xx / colw) * 0.5 + 0.5) ** 0.6
            lum += 0.18 * streak * inside
        else:                      # tinted glass with one soft diagonal glint
            lum += 0.04 * (rng.random((Ht, Wt)).astype(np.float32) - 0.5)
            g = (xx * 0.6 + yy) / (Ht + Wt * 0.6)
            lum += 0.10 * np.exp(-((g - 0.35) / 0.07) ** 2)
        # code layer (sub-legible, <= 10 % contrast)
        cl = np.zeros((Ht, Wt), np.float32)
        if code == 'A':            # pseudo-glyph rows: 5x7 master-px random cells, 9 px rows
            cw, rh = 5, 9
            for r in range(0, int(Ht // rh) + 1):
                n = int(rng.integers(8, 16)); x0 = int(rng.integers(0, max(1, Wt // 4)))
                bits = rng.random((n, 3, 2)) > 0.45
                for i in range(n):
                    for a in range(3):
                        for b in range(2):
                            if bits[i, a, b]:
                                x = x0 + i * (cw + 2) * 1 + a * 2; y = r * rh + b * 3
                                if x + 2 < Wt and y + 3 < Ht:
                                    cl[y:y + 2, x:x + 2] = 1
            cl *= 0.09
        elif code == 'B':          # blurred columns
            n = Wt // int(5 * ss) + 1
            for i in range(n):
                x = int(i * 5 * ss + rng.integers(0, 3))
                y0 = int(rng.integers(0, Ht)); ln = int(rng.integers(Ht // 5, Ht // 2))
                cl[y0:y0 + ln, x:x + 2] = 1
            cl = np.asarray(_u8(cl).filter(ImageFilter.GaussianBlur(1.6 * ss)), np.float32) / 255.0
            cl = cl / max(cl.max(), 1e-3) * 0.09
        elif code == 'C':          # dot-matrix tally rows: dashes of varying length
            rh = int(8 * ss)
            for r in range(0, Ht // rh + 1):
                x = int(rng.integers(2, 20)) * ss
                while x < Wt - 8 * ss:
                    ln = int(rng.integers(2, 7) * ss)
                    cl[r * rh + 2:r * rh + 2 + max(1, int(ss)), x:x + ln] = 1
                    x += ln + int(rng.integers(2, 6) * ss)
            cl *= 0.09
        lum = np.clip(lum + cl, 0, 0.30)
        rgb = lum[..., None] * col[None, None, :] * 2.6 / 1.0
        return _u8(np.clip(rgb * 0.9, 0, 1))
    return fn


def screen_cfg(material='A', code='A', frame=None):
    tp = dict(tex=tex_factory(material, code), tex_gain=1.0, glow_k=(0.0, 0.0))
    if frame:
        tp.update(FRAME[frame])
    return cfg_with(tile=tp)


# ============================================================ icons
def icons_factory(kind, size=44, rc_f=0.52, per=None):
    def fn(canvas, ss, cx, cy, s, t):
        nm = 'WC_%s_%s' % (t, kind)
        if t == 'SHIELD' and kind == 'cur':
            pass
        T.icon_on_canvas(canvas, ss, cx, cy, 60 * s, nm, size, rc_f=rc_f)
    return fn


def icons_cfg(kind_by_type, size=44):
    def fn(canvas, ss, cx, cy, s, t):
        k = kind_by_type.get(t, 'cur')
        if k == 'cur':
            WB.icons_cur(canvas, ss, cx, cy, s, t)
        else:
            T.icon_on_canvas(canvas, ss, cx, cy, 60 * s, 'WC_%s_%s' % (t, k), size, rc_f=0.52)
    return fn
