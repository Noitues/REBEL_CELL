"""wheel_core design harness, part 1: the tower core painter.
A parametrised copy of slicelib.render_slice (same bezel / screen shader as E10) so that each tower-material element
(frame, screen, gutters, hub, icons) can be swapped alone.  All-defaults == E10.  Master px -> screen px is KE (set below).
Hub, emblem and icons are drawn here too (they are part of the same opaque disc).  Everything outside r 160 stays the E10 board."""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import build10 as B
from cv_lib import K, C, RS, W, H
import slicelib as SL
from slicelib import bilinear, smooth, round_min, c01, PROGRAMS, shadowed, glyph_rgba, Ctx
import programs
import roster_wheel as RW_
import cv_board as CB

TS = 524                                   # tower canvas, master px
NSC = int(round(TS * K))                   # screen px of the canvas
KE = NSC / TS                              # master -> screen
R_IN_M, R_OUT_M = RS['s0'] / KE, RS['s1'] / KE
SLC = CB.SLC
INK = (12, 10, 22)
BACKPLATE = np.array([0.020, 0.022, 0.034], np.float32)

TILE_DEFAULT = dict(gap_side=1.6, gap_rad=1.6, bw=8.5, r_t_out=4.0, r_t_in=4.0, r_s_out=11.0, r_s_in=9.0,
                    hair_gain=1.1, hair_w=0.9, led=True, tex=None, post=None, tex_gain=0.9, plate=0.62,
                    plate_ax=None, plate_ay=None, edge_w=0.0, edge_col=None, edge_gain=1.0, ink_w=0.0, bez_base=None,
                    r_s_gain=1.0, glass=0.0, vig=1.0, bevel=0.6, inset_line=0.0)


def _slice_tile(canvas, cx, cy, prog, a0, span, t, ss, P, seed, icon_dims=None, rc_f=0.55):
    """one wedge, master px.  ss = canvas supersample."""
    col = PROGRAMS[prog]['col']
    Ro, Ri = R_OUT_M * ss, R_IN_M * ss
    gs_, gr_ = P['gap_side'] * ss, P['gap_rad'] * ss
    bw = P['bw'] * ss
    mid = a0 + span / 2
    half = span / 2
    ext = (P['ink_w'] + 2) * ss
    angs = np.radians(np.linspace(a0, a0 + span, 32))
    pts = [(cx + r * np.sin(a), cy - r * np.cos(a)) for r in (Ri, Ro) for a in angs]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0, x1 = int(max(0, min(xs) - ext)), int(min(canvas.shape[1], max(xs) + ext + 1))
    y0, y1 = int(max(0, min(ys) - ext)), int(min(canvas.shape[0], max(ys) + ext + 1))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx + 0.5 - cx, yy + 0.5 - cy
    rho = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(dx, -dy)) % 360
    d = ((th - mid + 180) % 360) - 180
    e_side = rho * np.sin(np.radians(np.clip(half - np.abs(d), -90, 90))) - gs_
    e_out = Ro - gr_ - rho
    e_in = rho - Ri - (P['gap_in'] * ss if P.get('gap_in') is not None else gr_)
    e_tile = round_min(round_min(e_side, e_out, P['r_t_out'] * ss), e_in, P['r_t_in'] * ss)
    a_tile = np.clip(e_tile, 0, 1)
    s_side = e_side - bw
    s_out = e_out - bw
    s_in = e_in - bw * 0.85
    e_scr = round_min(round_min(s_side, s_out, P['r_s_out'] * ss), s_in, P['r_s_in'] * ss)
    a_scr = np.clip(e_scr + 0.5, 0, 1)
    # ---- texture (ctx uses the E10 constants so every texture function sees what it saw in E10)
    r_out_s = Ro - 1.6 * ss - 8.5 * ss
    r_in_s = Ri + 1.6 * ss + 8.5 * ss * 0.85
    Wt = int(r_out_s * math.radians(span) + 8 * ss)
    Ht = int(r_out_s - r_in_s + 4 * ss)
    ctx = Ctx(Wt, Ht, t, ss, span, r_out_s, col, 'player', prog, seed)
    ctx.opts = dict(upright=True)
    ctx.special = None
    tex_img = P['tex'](ctx) if P['tex'] else programs.texture(ctx)
    tex = np.asarray(tex_img, dtype=np.float32) / 255.0
    glow = np.asarray(tex_img.filter(ImageFilter.GaussianBlur(5 * ss)), dtype=np.float32) / 255.0
    glow2 = np.asarray(tex_img.filter(ImageFilter.GaussianBlur(14 * ss)), dtype=np.float32) / 255.0
    gk = P.get('glow_k', (0.55, 0.35))
    tex = tex * P['tex_gain'] + glow * gk[0] + glow2 * gk[1]
    if P['post']:
        tex = P['post'](tex, ctx)
    tx = Wt / 2 + rho * np.radians(d)
    ty = r_out_s - rho
    nx = (tx - Wt / 2) / (Wt / 2)
    ny = (ty - Ht / 2) / (Ht / 2)
    f = 1 - 0.055 * (nx * nx + ny * ny)
    sx = Wt / 2 + (tx - Wt / 2) * f
    sy = Ht / 2 + (ty - Ht / 2) * f
    scr = bilinear(tex, sx, sy)
    sl = 0.70 + 0.30 * (0.5 + 0.5 * np.cos(2 * np.pi * ty / (3.0 * ss)))
    scr *= sl[..., None]
    vig = 0.35 + 0.65 * smooth(0, 26 * ss, e_scr)
    scr *= (1 - P['vig'] * (1 - vig))[..., None]
    if icon_dims is not None and P['plate'] > 0:
        rc = (R_IN_M + rc_f * (R_OUT_M - R_IN_M)) * ss
        bcx = cx + rc * math.sin(math.radians(mid))
        bcy = cy - rc * math.cos(math.radians(mid))
        ax, ay = icon_dims[0] * ss, icon_dims[1] * ss
        q = ((xx + 0.5 - bcx) / ax) ** 2 + ((yy + 0.5 - bcy) / ay) ** 2
        scr *= (1 - P['plate'] * np.exp(-q * 1.4))[..., None]
    gl = np.exp(-((ny + 0.75) * 2.6) ** 2) * np.clip(0.6 - nx * 0.5, 0, 1) * 0.07
    scr += gl[..., None]
    # ---- bezel
    base = np.array(P['bez_base'] or [0.085, 0.08, 0.11], np.float32)
    hair = c01(col)
    light = 0.85 + 0.3 * np.cos(np.radians(th - 315))
    bez = base[None, None, :] * light[..., None]
    lip = np.exp(-(e_tile / (1.2 * ss)) ** 2) * 0.22
    bez = bez + lip[..., None]
    shadow = smooth(-5 * ss, 0, e_scr)
    bez *= (1 - P['bevel'] * shadow)[..., None]
    hl = np.exp(-((e_scr + 1.3 * ss) / (P['hair_w'] * ss)) ** 2)
    bez = bez + hl[..., None] * hair[None, None, :] * P['hair_gain']
    if P['led']:
        led_r = Ro - gr_ - bw * 0.5
        led_lat = (half - min(4.0, half * 0.35)) * math.pi / 180 * led_r * 0.86
        ldx = rho * np.radians(d) - led_lat
        ldy = rho - led_r
        ld = np.hypot(ldx, ldy)
        led = np.clip(1.6 * ss - ld, 0, 1) + np.exp(-(ld / (3.5 * ss)) ** 2) * 0.5
        bez = bez + led[..., None] * hair[None, None, :] * 1.3
    rgb = scr * a_scr[..., None] + bez * (1 - a_scr[..., None])
    # inner glass catch-light (top-left) for 'glass' frames
    if P['glass'] > 0:
        gl2 = np.exp(-(((e_scr) - 1.5 * ss) / (1.4 * ss)) ** 2) * np.clip(np.cos(np.radians(th - 315)), 0, 1) * P['glass']
        rgb = rgb + gl2[..., None] * a_scr[..., None]
    # type-colour edge on the tile outline + ink outside
    if P['edge_w'] > 0:
        ec = c01(P['edge_col'] or col)
        ew = P['edge_w'] * ss
        eb = np.clip(e_tile + 0.5, 0, 1) * np.clip(ew - e_tile + 0.5, 0, 1)
        rgb = rgb * (1 - eb[..., None]) + (ec * P['edge_gain'])[None, None, :] * eb[..., None]
    if P['inset_line'] > 0:
        ic = c01(col)
        pos = P['bw'] * ss * 0.5
        ib = np.clip(1 - np.abs(e_tile - pos) / (0.8 * ss), 0, 1) * P['inset_line']
        rgb = rgb * (1 - ib[..., None]) + ic[None, None, :] * ib[..., None]
    region = canvas[y0:y1, x0:x1]
    if P['ink_w'] > 0:
        ia = np.clip(e_tile + P['ink_w'] * ss + 0.5, 0, 1)
        ink = np.array(INK, np.float32) / 255.0
        region[..., :3] = region[..., :3] * (1 - ia[..., None]) + ink[None, None, :] * ia[..., None]
    a = a_tile[..., None]
    region[..., :3] = region[..., :3] * (1 - a) + rgb * a


def paste_block(canvas, im, px, py):
    SL.paste_rgba(canvas, im, px, py)


def icon_on_canvas(canvas, ss, cx, cy, mid_deg, glyph_name, px_screen, rc_f=0.55, dx=0.0, dy=0.0, keyline=0.075, shadow=True, fill=(255, 255, 255), edge=INK):
    """upright glyph block at the wedge visual centre (master px canvas).  px_screen = glyph box in screen px."""
    gpx = px_screen / KE
    g = glyph_rgba(glyph_name, gpx * ss, max(2.0, gpx * keyline * ss), fill=fill, edge=edge)
    blk = shadowed(g, ss) if shadow else g
    rc = (R_IN_M + rc_f * (R_OUT_M - R_IN_M)) * ss
    bx = cx + rc * math.sin(math.radians(mid_deg)) + dx * ss / KE
    by = cy - rc * math.cos(math.radians(mid_deg)) + dy * ss / KE
    paste_block(canvas, blk, bx - blk.width / 2, by - blk.height / 2)


def render_core(wheel, cfg, ss=3, nowords=False, icons_skip=False):
    """returns RGBA (NSC x NSC) at screen scale.  wheel = f['wheel'].  cfg keys: tile (dict), tile_by_type (dict type->dict), icons (fn), hub (fn), gutter (dict)"""
    S = TS * ss
    canvas = np.zeros((S, S, 4), np.float32)
    cx = cy = S / 2
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float32)
    rho = np.hypot(xx + 0.5 - cx, yy + 0.5 - cy) / ss
    bp = np.clip(161 / KE - rho, 0, 1)[..., None]
    canvas[..., :3] = BACKPLATE * bp
    canvas[..., 3:] = bp
    del yy, xx, rho
    icon_dims = cfg.get('icon_dims', None)
    for s in range(6):
        w = wheel[s]
        prog, _ = SLC[w['t']]
        P = dict(TILE_DEFAULT)
        P.update(cfg.get('tile', {}))
        P.update(cfg.get('tile_by_type', {}).get(w['t'], {}))
        _slice_tile(canvas, cx, cy, prog, 60 * s - 30, 60, (0.3 + 0.137 * s) % 1, ss, P, s + 3, icon_dims=icon_dims)
    # hub + frame rings in the same pass as E10 (PIL overlay at canvas scale)
    over = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(over)
    cfg['frame'](over, d, ss, cx, cy)
    cfg['hub'](over, d, ss, cx, cy, nowords)
    o = np.asarray(over, np.float32) / 255
    oa = o[..., 3:]
    canvas[..., :3] = canvas[..., :3] * (1 - oa) + o[..., :3] * oa
    canvas[..., 3:] = canvas[..., 3:] * (1 - oa) + oa
    # icons
    if cfg.get('icons') and not icons_skip:
        for s in range(6):
            cfg['icons'](canvas, ss, cx, cy, s, wheel[s]['t'])
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')
    im = im.resize((NSC, NSC), Image.LANCZOS)
    # keep only the disc r <= 160 (outside is the E10 board)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(im, (int(C[0] - NSC / 2), int(C[1] - NSC / 2)))
    return out
