"""Round 40: blended docking, the replace sequence, and the parasite ring v2 (player wheel, needle layouts).

- dock(): no added structure. The docked slice's own outline (its program-colour hairline) swells out of the
  host rim in one smooth curved lobe that wraps the satellite: one fill, one outline (metaball of an arc band,
  a neck and the satellite collar, thresholded so the curves blend).
- replace: the CURRENT satellite undocks and streams back to the host core as GREEN bits; the NEW one hovers,
  waiting, then installs.
- parasite2(): thinner partial ring, big glyph + value spread along each sub-slice (drone layout), glyph tinted
  like its number (faded red). Sub-slices reuse real slice effects, including ones that help the boss.
  Three layouts against the needle: A beyond the blade top, B in the blade band (needle over it), C inside the
  host slice at its root (anti-inner band).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import frames as F
from frames import INK, CREAM
import slicelib as SL
from slicelib import PROGRAMS, render_slice, f_num, f_ui, f_mono, glyph_rgba, number_rgba, shadowed
import sat2 as S2
from sat2 import Comp, dock_r, SAT_R, bit_burst, fade, greyed, host_image

GREEN = (123, 224, 123)
FADED_RED = (240, 110, 120)
PAR_COL = (214, 60, 255)


# ================================================================== blended dock
def dock(c, a, sat, host_spec, rot=0.0, glow=1.0):
    """Lobe that grows out of the docked slice's outline and wraps the satellite."""
    RA = c.RA
    i = int(round(((a - rot) % 360) / 60.0)) % 6
    prog = host_spec["slots"][i]["program"]
    pc = PROGRAMS[prog]["col"]
    W, H = c.W, c.H
    sc = 0.25  # build the field at quarter res for speed
    w, h = int(W * sc), int(H * sc)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    X, Y = xx / sc - c.C[0], yy / sc - c.C[1]
    rho = np.hypot(X, Y)
    th = np.degrees(np.arctan2(X, -Y))
    dth = ((th - a + 180) % 360) - 180
    # arc band along the host rim over the slice (taper toward the slice edges)
    band = np.clip(1 - np.abs(dth) / 26, 0, 1) ** 0.6 * np.exp(-((rho - (RA + 6)) / 22) ** 2)
    sx, sy = c.PP(dock_r(RA), a)
    dS = np.hypot(X + c.C[0] - sx, Y + c.C[1] - sy)
    coll = np.exp(-(np.maximum(0, dS - SAT_R - 4) / 18) ** 2) * (dS < SAT_R + 60)
    # neck: along the radial line
    rr0, rr1 = RA, dock_r(RA) - SAT_R
    q = np.clip((rho - rr0) / (rr1 - rr0), 0, 1)
    lat = np.abs(np.radians(dth)) * rho
    wneck = 46 - 26 * np.sin(np.pi * q)
    neck = np.exp(-(lat / wneck) ** 2) * ((rho > rr0 - 10) & (rho < rr1 + 30))
    f = np.maximum(np.maximum(band, coll), neck)
    m = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    m = m.filter(ImageFilter.GaussianBlur(6)).point(lambda v: 255 if v > 110 else 0)
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    fill = Image.new("RGBA", (W, H), (14, 13, 20, 235))
    c.under.paste(fill, (0, 0), m)
    glow_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_l.paste(Image.new("RGBA", (W, H), pc + (int(170 * glow),)), (0, 0), edge.filter(ImageFilter.MaxFilter(9)))
    c.under.alpha_composite(glow_l.filter(ImageFilter.GaussianBlur(8)))
    c.under.paste(Image.new("RGBA", (W, H), pc + (255,)), (0, 0), edge)


def compose(spec, sats, rot=0.0, states=None, host=None, lod=False, hp_number=True, size=None, ghosts=None, chase=None):
    host = host or host_image(spec, rot, hp_number=hp_number)
    c = Comp(host, size)
    states = states or {}
    for i, sat in sats:
        if not (states.get(i) or {}).get("nodock"):
            dock(c, 60 * i + rot, sat, spec, rot)
    if chase:
        c.chase(*chase)
    for i, N in ghosts or []:
        c.ghost(dict(sats)[i], 60 * i + rot + 12 * N)
    for i, sat in sats:
        st = states.get(i)
        if st and st.get("hidden"):
            continue
        c.put_sat(sat, 60 * i + rot, state={k: v for k, v in (st or {}).items() if k != "nodock"} or None, lod=lod)
    return c


# ================================================================== replace
def green_stream(img, x0, y0, x1, y1, t, seed=3, n=90):
    """0/1 bits streaming from (x0, y0) to (x1, y1); t 0..1 (staggered, curving, fading in at the core)."""
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(img)
    for k in range(n):
        delay = rng.random() * 0.45
        q = (t - delay) / 0.55
        if q <= 0 or q >= 1.05:
            continue
        q = min(q, 1.0)
        e = q * q * (3 - 2 * q)
        bend = (rng.random() - 0.5) * 160
        nx, ny = -(y1 - y0), (x1 - x0)
        L = math.hypot(nx, ny) + 1e-6
        x = x0 + (x1 - x0) * e + nx / L * bend * math.sin(math.pi * e) + (rng.random() - 0.5) * 50 * (1 - e)
        y = y0 + (y1 - y0) * e + ny / L * bend * math.sin(math.pi * e) + (rng.random() - 0.5) * 50 * (1 - e)
        a = int(255 * (1 - max(0, e - 0.85) / 0.15))
        d.text((x, y), rng.choice(["0", "1"]), font=f_mono(int(18 + 16 * rng.random())), fill=GREEN + (a,), anchor="mm")


def dissolve(sim, k, seed=2):
    """Break the satellite image into pixel blocks that vanish (k 0..1)."""
    a = np.asarray(sim).copy()
    h, w = a.shape[:2]
    rng = np.random.default_rng(seed)
    bs = 10
    gy, gx = (h + bs - 1) // bs, (w + bs - 1) // bs
    keep = rng.random((gy, gx)) > k
    mask = np.kron(keep, np.ones((bs, bs)))[:h, :w]
    a[..., 3] = (a[..., 3] * mask).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


# ================================================================== parasite ring v2
PAR_SLICES = [  # reuse real slice effects; some benefit the boss
    dict(prog="EXPLOIT", val=4, desc="hits YOU 4"),
    dict(prog="PATCH", val=6, desc="heals the BOSS 6"),
    dict(prog="VIRUS", val=None, special="dose", desc="DOSE: corrupts your slice"),
]
LAYOUTS = {
    "A": "beyond the needle tip: the ring sits outside the blade; a beam links the blade to the sub-slice in line",
    "B": "in the blade band: the needle passes OVER it; the sub-slice under the blade window triggers",
    "C": "inside the host slice, at its root (anti-inner band); the needle's tick line runs down to it",
}


def ring_radii(c, layout, top):
    RA = c.RA
    if layout == "A":
        return top + 16, top + 106
    if layout == "B":
        return RA + 6, RA + 96
    return SL.R_IN + 4, SL.R_IN + 92


def parasite2(c, slot, layout="A", rot=0.0, top=None, lit=None, prog=1.0, lod=False, turns=3, t=0.4, radii=None):
    top = top or (c.RA + 96)
    r_in, r_out = radii if radii else ring_radii(c, layout, top)
    a_mid = 60 * slot + rot
    span = 58.0 if layout != "C" else 56.0
    a0 = a_mid - span / 2
    n = len(PAR_SLICES)
    sp = span / n
    canvas = np.zeros((c.H, c.W, 4), np.float32)
    old = (SL.R_OUT, SL.R_IN)
    SL.R_OUT, SL.R_IN = r_out, r_in
    try:
        for j, ps in enumerate(PAR_SLICES):
            render_slice(canvas, c.C[0], c.C[1], ps["prog"], a0 + j * sp, sp, None, (t + 0.3 * j) % 1, "solace", 1,
                         dict(upright=True, icons=False, tex_gain=0.85), seed=41 + j, special=ps.get("special"))
    finally:
        SL.R_OUT, SL.R_IN = old
    rgb, al = canvas[..., :3], canvas[..., 3:]
    if prog < 1:
        yy, xx = np.mgrid[0:c.H, 0:c.W].astype(np.float32)
        rho = np.hypot(xx - c.C[0], yy - c.C[1])
        rr = r_in + (r_out - r_in) * max(0.02, prog)
        al = al * np.clip((rr - rho) / 4 + 0.5, 0, 1)[..., None]
    st = np.where(al > 1e-4, rgb / np.maximum(al, 1e-4), 0)
    ring = Image.fromarray((np.clip(np.concatenate([st, al], 2), 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    if layout == "C":  # the root band sits on top of the host slice
        c.top.alpha_composite(ring)
        tgt = c.top
    else:
        c.under.alpha_composite(ring) if layout == "B" else c.top.alpha_composite(ring)
        tgt = c.under if layout == "B" else c.top
    d = ImageDraw.Draw(tgt)
    gl = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    for r in (r_in - 4, r_out + 4):
        arc = [c.PP(r, a0 - 1 + (span + 2) * j / 60) for j in range(61)]
        gd.line(arc, fill=PAR_COL + (190,), width=14)
        d.line(arc, fill=(40, 6, 48, 255), width=10)
        d.line(arc, fill=PAR_COL + (255,), width=4)
    for side in (0, 1):
        a = a0 + side * span
        d.line([c.PP(r_in - 4, a), c.PP(r_out + 4, a)], fill=PAR_COL + (255,), width=5)
    if layout != "C":
        for k in range(7):  # barbs on the outer arc
            a = a0 + span * (k + 0.5) / 7
            d.polygon([c.PP(r_out + 4, a - 2), c.PP(r_out + 22, a), c.PP(r_out + 4, a + 2)], fill=PAR_COL + (255,), outline=INK + (255,))
    if prog >= 0.98:
        rc = (r_in + r_out) / 2
        for j, ps in enumerate(PAR_SLICES):
            mid = a0 + sp * (j + 0.5)
            if lit == j:
                poly = [c.PP(r_out - 2, mid - sp / 2 + 0.6 + (sp - 1.2) * q / 20) for q in range(21)] + \
                       [c.PP(r_in + 2, mid + sp / 2 - 0.6 - (sp - 1.2) * q / 20) for q in range(21)]
                gd.polygon(poly, outline=(255, 255, 255, 255), width=20)
                d.polygon(poly, outline=(255, 240, 250, 255), width=6)
            gname = {"dose": "DOSE"}.get(ps.get("special"), ps["prog"])
            arc_len = math.radians(sp) * rc
            gpx = int(min(58, (r_out - r_in) * 0.62)) if not lod else int((r_out - r_in) * 0.8)
            off = math.degrees(min(arc_len * 0.22, 34) / rc)
            items = [("g", gname, mid - off)] + ([("v", str(ps["val"]), mid + off)] if ps["val"] is not None and not lod else [])
            if ps["val"] is None or lod:
                items = [("g", gname, mid)]
            for kind, x, a in items:
                px, py = c.PP(rc, a)
                pl = Image.new("RGBA", (c.W, c.H), (0, 0, 0, 0))
                ImageDraw.Draw(pl).ellipse([px - 40, py - 36, px + 40, py + 36], fill=(0, 0, 0, 160))
                tgt.alpha_composite(pl.filter(ImageFilter.GaussianBlur(10)))
                if kind == "g":
                    g = shadowed(glyph_rgba(x, gpx, 4, fill=FADED_RED), 1)
                else:
                    g = shadowed(number_rgba(x, gpx * 1.25, 4, fill=FADED_RED), 1)
                tgt.alpha_composite(g, (int(px - g.width / 2), int(py - g.height / 2)))
        d = ImageDraw.Draw(tgt)
        for k in range(3):  # turns-left pips at the ring's trailing end
            x, y = c.PP(r_out + (28 if layout != "C" else -((r_out - r_in) / 2)), a0 + span + 4 + k * 4 if layout != "C" else a0 + 5 + k * 4)
            if layout == "C":
                x, y = c.PP(r_in - 14, a0 + span / 2 + (k - 1) * 5)
            d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(PAR_COL if k < turns else (60, 40, 70)) + (255,), outline=INK + (255,), width=2)
    tgt.alpha_composite(gl.filter(ImageFilter.GaussianBlur(7)))
    return r_in, r_out, a0, sp


def link(c, layout, r_in, r_out, top, a=0.0, k=1.0):
    """Trigger link from the needle to the in-line sub-slice."""
    d = ImageDraw.Draw(c.top)
    col = (255, 240, 250, int(255 * k))
    if layout == "A":
        p0, p1 = c.PP(top - 6, a), c.PP(r_in, a)
        d.line([p0, p1], fill=PAR_COL + (int(200 * k),), width=16)
        d.line([p0, p1], fill=col, width=6)
    elif layout == "C":
        for r in range(int(r_out), int(SL.R_OUT - 20), 14):
            d.line([c.PP(r, a), c.PP(r + 8, a)], fill=col, width=5)
