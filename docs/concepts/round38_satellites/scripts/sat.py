"""Round 38: satellites (drones docked on wheels) as mini-wheels in the locked D4 + C-slice language.

GDD 2.1 / 2.7 / Botnet: a satellite is a 2-3 slice mini-wheel (15 or 10 ticks per slice) with its own pointer,
intent and HP. It docks on ONE slice of its host and rides it (spins/flips carry it along); it can be nudged
on its own; an attack aimed at a pointer whose slice has a satellite hits the satellite first (bodyguard).

Satellite frame: the whole mini-wheel is oriented RADIALLY: its pointer blade always faces OUT from the host,
so it never points into the host's slices; values stay upright (render_slice upright mode).

render_sat(sat, ang, ss, lod, srot, state) -> RGBA (master units, R_OUT = 360) + centre px
compose(host_spec, sats, r_px, rot, states, preview) -> RGBA composite at host radius r_px, host centre px
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
from frames import P, Q, layer, add_glow, over_pil, INK, CREAM
import d4corp as D
import roster_wheel as RW
from slicelib import R_OUT, R_IN, PROGRAMS, render_slice, f_num, f_ui, f_mono, glyph_rgba, c01
from preview15 import dashed_poly

SAT_K = 0.30          # satellite size relative to the host (master units)
DOCK_OFF = 22.0       # docked 22 deg clockwise of the slice centre: never under the host blade or value
HP_COL = (123, 224, 123)
HURT = (255, 70, 90)

BOTNET_DRONE = dict(name="DRONE", theme="player", cls="botnet", slots=[("EXPLOIT", 3), ("FIREWALL", 3)], hp=5, hpmax=5)
SEED_DRONE = dict(name="SEED", theme="player", cls="botnet", slots=[("EXPLOIT", 3), ("FIREWALL", 3)], hp=1, hpmax=1)
CARE_DRONE = dict(name="CARE DRONE", theme="solace", slots=[("EXPLOIT", 3), ("EXPLOIT", 3), ("FIREWALL", 2)], hp=4, hpmax=4)


def sat_acc(sat):
    if sat["theme"] == "player":
        return RW.CLASS_STYLE[sat["cls"]]["acc"]
    return D.MO.ACCENT[sat["theme"]]["a"]


def active_slot(sat, srot):
    n = len(sat["slots"])
    span = 360.0 / n
    return int(((-srot + span / 2) % 360) // span)


def render_sat(sat, ang, ss=1, lod=False, srot=0.0, state=None, t=0.4):
    """ang: pointer direction (deg, 0 = up) = the outward dock direction. srot: own-wheel rotation (deg)."""
    F.set_centre()
    state = state or {}
    canvas = F.new_canvas(ss)
    n = len(sat["slots"])
    span = 360.0 / n
    acc = sat_acc(sat)
    theme = sat["theme"]
    # back plate
    dx, dy = F.grids(ss)
    rho = np.hypot(dx, dy)
    bp = np.clip(R_OUT + 4 - rho, 0, 1)
    canvas[..., :3] = canvas[..., :3] * (1 - bp[..., None]) + np.array([0.02, 0.018, 0.03]) * bp[..., None]
    canvas[..., 3] = np.maximum(canvas[..., 3], bp)
    del dx, dy, rho, bp
    act = active_slot(sat, srot)
    opts = dict(RW.LOD) if lod else {}
    opts.update(upright=True, glyph_scale=opts.get("glyph_scale", 1.0) * 1.25, number_scale=opts.get("number_scale", 1.0) * 1.2)
    for j, (prog, val) in enumerate(sat["slots"]):
        a0 = ang - span / 2 + j * span + srot
        o = dict(opts)
        render_slice(canvas, F.CX * ss, F.CY * ss, prog, a0, span, val, (t + j * 0.21) % 1.0, theme, ss, o, seed=j + 11)
        if j != act:  # dim the inactive slices (D4 rule)
            pass
    # dim inactive slices by overpainting a dark wedge
    im, d = layer(ss)
    for j in range(n):
        if j == act:
            continue
        a0 = ang - span / 2 + j * span + srot
        d.polygon(F.wedge_pts(a0 + 0.5, a0 + span - 0.5, R_IN - 2, R_OUT + 1, ss, 60), fill=(0, 0, 0, 92))
    over_pil(canvas, im)
    # bezel: narrow machined ring + 30 ticks
    is_player = theme == "player"
    base = (0.16, 0.15, 0.19) if is_player else D.CORP_STYLE[theme]["base"]
    R1 = R_OUT + 44
    F.machined(canvas, ss, [(R_OUT - 4, 0.0), (R_OUT - 1, 6.0), (R1 - 4, 8.0), (R1, 0.0)], base, acc, seed=5,
               accent_r=((R_OUT + 2, 0.9, 0.9), (R1 - 1.0, 1.2, 1.2)), brushed=0.04)
    im, d = layer(ss)
    gl, gd = layer(ss)
    for k in range(30):
        a = ang + k * 12
        major = k % (30 // n) == 0
        d.line([P(R_OUT + 8, a, ss), P(R_OUT + (26 if major else 16), a, ss)], fill=(235, 235, 245, 255) if major else acc + (200,),
               width=int((5 if major else 3) * ss))
    # active slice outline
    a0 = ang - span / 2 + act * span + srot
    pc = PROGRAMS[sat["slots"][act][0]]["col"]
    pts = F.wedge_pts(a0 + 1.2, a0 + span - 1.2, R_IN + 2, R_OUT - 2, ss, 60)
    gd.polygon(pts, outline=pc + (255,), width=int(18 * ss))
    d.polygon(pts, outline=INK + (255,), width=int(12 * ss))
    d.polygon(pts, outline=CREAM + (255,), width=int(7 * ss))
    # hub: HP (big number + pip ring)
    hr = R_IN - 6
    cx, cy = F.CX * ss, F.CY * ss
    d.ellipse([cx - hr * ss, cy - hr * ss, cx + hr * ss, cy + hr * ss], fill=(12, 11, 18, 255), outline=acc + (255,), width=int(5 * ss))
    hp, hpmax = sat["hp"], sat["hpmax"]
    hpv = state.get("hp", hp)
    for k in range(hpmax):
        a_ = -150 + 300 * (k + 0.5) / hpmax
        on = k < hpv
        lost = k >= hpv and k < hp
        col = HP_COL if on else (HURT if lost else (50, 60, 52))
        pa = RW.arc_poly(hr - 26, hr - 8, a_ - 120 / hpmax + 3, a_ + 120 / hpmax - 3, ss, 6)
        pa = [(x - RW.CX * ss + cx, y - RW.CY * ss + cy) for x, y in pa]
        d.polygon(pa, fill=col + (255,))
    f = f_num(int(110 * ss))
    s = str(hpv)
    tw = f.getlength(s)
    d.text((cx - tw / 2, cy - 72 * ss), s, font=f, fill=(HP_COL if hpv > 0 else HURT) + (255,), stroke_width=int(4 * ss), stroke_fill=INK + (255,))
    add_glow(canvas, gl, ss, 0.8)
    over_pil(canvas, im)
    # own pointer: D4 blade facing outward, value window = the active slice value
    val = sat["slots"][act][1]
    top = R1 + 170
    bl, bg = F.blade(ss, ang, acc, CREAM if is_player else D.mix(acc, (255, 255, 255), 0.35), (230, 220, 200), val,
                     sat["slots"][act][0], tip=R_OUT - 40, sh=R1 + 34, top=top, wsh=70, wtop=96, win=(R1 + 52, top - 26, 74))
    F.shadow_of(canvas, bl, ss, 10, 16, 6, 0.6)
    add_glow(canvas, bg, ss, 0.9)
    over_pil(canvas, bl)
    # states
    if state.get("guard"):
        im, d = layer(ss)
        gl, gd = layer(ss)
        r = R1 + 30
        bb = [cx - r * ss, cy - r * ss, cx + r * ss, cy + r * ss]
        ga = state["guard"]  # angle the hit comes from (host side)
        gd.arc(bb, ga - 90 - 60, ga - 90 + 60, fill=(120, 220, 255, 255), width=int(40 * ss))
        d.arc(bb, ga - 90 - 60, ga - 90 + 60, fill=(200, 240, 255, 255), width=int(14 * ss))
        x, y = P(r, ga, ss)
        star = [(x + (80 if k % 2 == 0 else 34) * ss * math.cos(math.radians(k * 22.5)), y + (80 if k % 2 == 0 else 34) * ss * math.sin(math.radians(k * 22.5))) for k in range(16)]
        gd.polygon(star, fill=(255, 230, 160, 255))
        d.polygon(star, fill=(255, 240, 200, 255), outline=INK + (255,))
        add_glow(canvas, gl, ss, 1.0, blur=10)
        over_pil(canvas, im)
    if state.get("dead"):
        a = canvas[..., :3]
        lum = a.mean(axis=2, keepdims=True)
        canvas[..., :3] = lum * 0.35 + a * 0.08
        im, d = layer(ss)
        rng = np.random.default_rng(4)
        for k in range(7):  # cracks from the centre
            pts = [(cx, cy)]
            a_ = rng.random() * 360
            r = 0
            for s_ in range(5):
                r += 60 + rng.random() * 50
                a_ += (rng.random() - 0.5) * 30
                pts.append((cx + r * ss * math.sin(math.radians(a_)), cy - r * ss * math.cos(math.radians(a_))))
            d.line(pts, fill=(255, 90, 100, 255), width=int(7 * ss))
            d.line(pts, fill=(20, 10, 14, 255), width=int(3 * ss))
        over_pil(canvas, im)
    F.set_centre()
    rgb = np.clip(canvas[..., :3], 0, 1)
    al = np.clip(canvas[..., 3:], 0, 1)
    st = np.where(al > 1e-4, rgb / np.maximum(al, 1e-4), 0)
    out = Image.fromarray((np.clip(np.concatenate([st, al], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    return out, (F.CX * ss, F.CY * ss)


# ================================================================== composite on a host wheel
def host_image(spec, rot=0.0, ss=1, hp_number=False):
    s = dict(spec)
    s["drones"] = []
    im, c, meta = D.render(s, ss=ss, rot=rot, hp_number=hp_number)
    return im, c, meta


def dock_r(meta):
    RA = meta["hp_r"] - 36
    return RA + 50 + (R_OUT + 44) * SAT_K


def compose(host_spec, sats, r_px, rot=0.0, states=None, ghosts=None, host=None, lod=False, chase=None,
            labels=None, hp_number=False):
    """sats: [(slot_index, sat)]; states: {slot_index: state}; ghosts: [(slot_index, N)] = card preview: dashed
    ghost satellite where it ENDS UP after spinning N ticks (locked preview behaviour)."""
    states = states or {}
    if host is None:
        host = host_image(host_spec, rot, hp_number=hp_number)
    him, hc, meta = host
    margin = 560
    W, H = him.width + 2 * margin, him.height + 2 * margin
    cv = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    C = (hc[0] + margin, hc[1] + margin)
    RA = meta["hp_r"] - 36
    Rd = dock_r(meta)
    acc_h = D.acc_of(host_spec)
    under = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ud = ImageDraw.Draw(under)

    def PP(r, a):
        return (C[0] + r * math.sin(math.radians(a)), C[1] - r * math.cos(math.radians(a)))
    # dock clamps (under the host so the host bezel overlaps them)
    for i, sat in sats:
        a = 60 * i + DOCK_OFF + rot
        st = states.get(i, {})
        acc = sat_acc(sat)
        for side in (-1, 1):
            p0 = PP(RA - 30, a + side * 6)
            p1 = PP(Rd - (R_OUT + 44) * SAT_K * 0.7, a + side * 4)
            ud.line([p0, p1], fill=INK + (255,), width=26)
            ud.line([p0, p1], fill=(110, 108, 118, 255), width=16)
            ud.line([p0, p1], fill=acc + (255,), width=4)
    cv.alpha_composite(under)
    cv.alpha_composite(him, (margin, margin))
    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for i, sat in sats:
        a = 60 * i + DOCK_OFF + rot
        acc = sat_acc(sat)
        # clamp plate on the host rim (marks the docked slice)
        x, y = PP(RA + 4, a)
        r = 22
        od.rounded_rectangle([x - r, y - r, x + r, y + r], radius=6, fill=(30, 28, 36, 255), outline=acc + (255,), width=4)
        od.ellipse([x - 7, y - 7, x + 7, y + 7], fill=acc + (255,))
    cv.alpha_composite(over)
    # ghosts (preview of where satellites END UP)
    for gi, (i, N) in enumerate(ghosts or []):
        sat = dict(sats)[i]
        a = 60 * i + DOCK_OFF + rot + 12 * N
        gx, gy = PP(Rd, a)
        rr = (R_OUT + 44) * SAT_K
        gimg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gimg)
        gd.ellipse([gx - rr, gy - rr, gx + rr, gy + rr], fill=sat_acc(sat) + (60,))
        circ = [(gx + rr * math.cos(math.radians(k * 6)), gy + rr * math.sin(math.radians(k * 6))) for k in range(60)]
        dashed_poly(gd, circ, sat_acc(sat) + (255,), 6, dash=18, gap=10)
        g = glyph_rgba("DRONE", int(rr * 1.0), 3)
        g.putalpha(g.split()[3].point(lambda v: int(v * 0.75)))
        gimg.alpha_composite(g, (int(gx - g.width / 2), int(gy - g.height / 2)))
        cv.alpha_composite(gimg)
    if chase is not None:  # the locked chevron chase for the top needle only
        im, d = Image.new("RGBA", (W, H), (0, 0, 0, 0)), None
        d = ImageDraw.Draw(im)
        N, ph = chase
        R_ch = RA + 62
        head = ph * (N + 1.5)
        for j in range(N):
            aa = rot * 0 - 12 * (j + 0.6)
            dist = head - (j + 1)
            al = 0.35 if ph >= 1 else (0.18 + 0.82 * math.exp(-(dist / 1.1) ** 2) if dist > -1.5 else 0.10)
            if 1.5 < dist and ph < 1:
                al = max(al, 0.35)
            w = 64
            da = math.degrees(w / R_ch)
            tip = PP(R_ch, aa - da * 0.55)
            l0, l1 = PP(R_ch + w * 0.62, aa + da * 0.45), PP(R_ch - w * 0.62, aa + da * 0.45)
            m0, m1 = PP(R_ch + w * 0.62, aa + da * 1.0), PP(R_ch - w * 0.62, aa + da * 1.0)
            nt = PP(R_ch, aa)
            col = tuple(int(255 * (1 - al) + (255, 214, 64)[k] * al) for k in range(3))
            d.polygon([l0, tip, l1, m1, nt, m0], fill=col + (int(50 + 205 * al),), outline=INK + (int(90 + 165 * al),))
        cv.alpha_composite(im)
    # satellites
    for i, sat in sats:
        a = 60 * i + DOCK_OFF + rot
        st = states.get(i, {})
        sim, sc = render_sat(sat, a, lod=lod, srot=st.get("srot", 0.0), state=st)
        k = SAT_K
        sim = sim.resize((int(sim.width * k), int(sim.height * k)), Image.LANCZOS)
        sx, sy = PP(Rd, a)
        cv.alpha_composite(sim, (int(sx - sc[0] * k), int(sy - sc[1] * k)))
    # scale to the requested host radius
    s = r_px / R_OUT
    out = cv.resize((int(W * s), int(H * s)), Image.LANCZOS)
    bb = out.split()[3].point(lambda v: 255 if v > 4 else 0).getbbox()
    out = out.crop(bb)
    return out, (C[0] * s - bb[0], C[1] * s - bb[1]), dict(RA=RA * s, Rd=Rd * s, scale=s, C=C, bb=bb)
