"""Round 10 wheel: round 6 Screens & Data slices + the round 7 V2 telemetry border ring.

render(spec) draws a combat wheel:
- C screen slices (per-slice bezel, CRT content, white glyph + value on a dark read plate),
  with the glyph/value block kept upright (counter-rotating) so 6 never reads as 9;
- the V2 "living programs" border: a thin readout strip scrolling class/corp telemetry,
  emblem badges at the quarters (skipped under a pointer);
- bosses: an extra heavy outer band (corp hazard stripes + crown studs), nameplate banner,
  phase pips on the HP arc;
- HP arc with a predicted-loss segment (E1 "predicted loss").
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import slicelib as SL
from slicelib import R_OUT, PROGRAMS, CORPS, render_slice, f_num, f_ui, f_mono
import roster_wheel as RW
from roster_wheel import CLASS_STYLE, CORP_EMBLEM, SPECIAL_GLYPH, LOD, P, HP_GREEN

READOUT = {
    "breaker": "CELL-9 // BREAKER // RIG OK // SPIN +1 // PERFECT = RESOLVE x2 // RING x2 . PIERCE . - // RAM 5/12 // HP 41/60 // ",
    "route_optimizer": "MERIDIAN FREIGHT // ROUTE OPTIMIZER // LANE 00 OK // LANE 15 OK // ETA 00:14 // PKG 4471 ROUTED // ",
    "the_manifest": "THE MANIFEST // PRIORITY ROUTING +4 SHIELD // PHASE 1 OF 3 // MULTIPLY @66% // ORBIT @33% // ",
}
HP_LOSS = (255, 70, 90)


def text_ring(img, text, r, a_start, a_end, ss, font, col, head=None):
    cx, cy = RW.CX * ss, RW.CY * ss
    a = a_start
    i = 0
    while a < a_end:
        ch = text[i % len(text)]
        adv = font.getlength(ch)
        if ch != " ":
            c = col
            if head is not None and abs(((a - head + 180) % 360) - 180) < 14:
                c = (255, 255, 255)
            im = Image.new("RGBA", (int(adv + 4), int(font.size * 1.3)), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((2, 0), ch, font=font, fill=c + (255,))
            am = a + math.degrees(adv / 2 / (r * ss))
            x, y = P(r, am, ss)
            im = im.rotate(-am, resample=Image.BICUBIC, expand=True)
            img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))
        a += math.degrees(adv / (r * ss))
        i += 1


def emblem_badge(img, d, gd, x, y, r, acc, emblem):
    gd.ellipse([x - r * 1.5, y - r * 1.5, x + r * 1.5, y + r * 1.5], fill=acc + (150,))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(10, 10, 14, 255), outline=acc + (255,), width=int(r * 0.12))
    g = RW.tinted_glyph(emblem, int(r * 1.3), acc)
    img.alpha_composite(g, (int(x - g.width / 2), int(y - g.height / 2)))


def telemetry_ring(img, d, gd, spec, R0, R1, ss, acc, key, emblem, lod=False):
    for rr in (R0 + 4, R1 - 4):
        bb = [RW.CX * ss - rr * ss, RW.CY * ss - rr * ss, RW.CX * ss + rr * ss, RW.CY * ss + rr * ss]
        d.ellipse(bb, outline=tuple(int(v * 0.5) for v in acc) + (255,), width=max(1, ss))
    if not lod:
        f = f_mono(int(13 * ss))
        text_ring(img, READOUT.get(key, key.upper() + " // "), (R0 + R1) / 2 - 5, 0, 360, ss, f,
                  tuple(int(v * 0.95) for v in acc), head=320)
    else:  # small size: the readout becomes a dotted data strip
        for i in range(120):
            a = i * 3
            if i % 7 in (0, 1):
                continue
            d.line([P((R0 + R1) / 2 - 3, a, ss), P((R0 + R1) / 2 - 3, a + 1.6, ss)], fill=acc + (200,), width=int(4 * ss))
    ptr = [p * 12 for p in spec.get("pointers", [0])]
    for a in (0, 90, 180, 270):
        if any(abs(((a - p + 180) % 360) - 180) < 10 for p in ptr):
            continue
        if spec.get("hp") and 135 < a < 225:
            pass
        x, y = P((R0 + R1) / 2, a, ss)
        emblem_badge(img, d, gd, x, y, 19 * ss, acc, emblem)


def boss_band(d, gd, R0, R1, ss, acc):
    band0, band1 = R0 + 3, R1 - 4
    for i in range(120):
        a = i * 3
        poly = [P(band0, a, ss), P(band1, a + 1.5, ss), P(band1, a + 3.0, ss), P(band0, a + 1.5, ss)]
        d.polygon(poly, fill=(20, 16, 12, 255) if i % 2 else acc + (255,))
    for i in range(36):
        x, y = P(R1 - 1, i * 10 + 5, ss)
        r = 3.6 * ss
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 230, 220, 255), outline=(10, 8, 16, 255))
    bb = [RW.CX * ss - (R1 + 2) * ss, RW.CY * ss - (R1 + 2) * ss, RW.CX * ss + (R1 + 2) * ss, RW.CY * ss + (R1 + 2) * ss]
    gd.ellipse(bb, outline=acc + (200,), width=int(6 * ss))
    d.ellipse(bb, outline=acc + (255,), width=int(2 * ss))


def draw_hp(d, gd, ss, R, hp, hpmax, pred=0, phases=None, active_phase=1, number=True):
    n = 30
    a0, a1 = 130, 230
    r0, r1 = R + 14, R + 36
    on_n = round(n * hp / hpmax)
    loss_n = round(n * max(0, hp - pred) / hpmax)
    for i in range(n):
        # fill from the right-hand end (a1) toward a0 so the arc drains clockwise
        aa = a1 - (a1 - a0) * (i + 0.88) / n
        ab = a1 - (a1 - a0) * (i + 0.12) / n
        on = i < on_n
        lost = loss_n <= i < on_n
        col = HP_LOSS if lost else (HP_GREEN if on else (38, 58, 42))
        d.polygon(RW.arc_poly(r0, r1, aa, ab, ss, 3), fill=col + (255,))
        if on:
            gd.polygon(RW.arc_poly(r0, r1, aa, ab, ss, 3), fill=col + (110,))
        if lost:  # hatch = "will be lost"
            x, y = P((r0 + r1) / 2, (aa + ab) / 2, ss)
            d.line([(x - 5 * ss, y + 5 * ss), (x + 5 * ss, y - 5 * ss)], fill=(255, 235, 240, 255), width=max(1, int(1.6 * ss)))
    if phases:
        for k, frac in enumerate(phases):
            a = a1 - (a1 - a0) * frac
            x, y = P(r1 + 13, a, ss)
            r = 9 * ss
            on = (k + 2) <= active_phase
            col = (255, 210, 90) if on else (150, 135, 100)
            d.line([P(r0 - 4, a, ss), P(r1 + 4, a, ss)], fill=(255, 220, 120, 255), width=int(3 * ss))
            d.polygon([(x, y - r), (x + r, y), (x, y + r), (x - r, y)], fill=col + (255,), outline=(10, 8, 16, 255))
            f = f_num(int(15 * ss))
            s = "P%d" % (k + 2)
            xx, yy = P(r1 + 32, a, ss)
            tw = f.getlength(s)
            d.text((xx - tw / 2, yy - 9 * ss), s, font=f, fill=col + (255,), stroke_width=int(1.5 * ss), stroke_fill=(10, 8, 16, 255))
    if number:
        txt = "%d/%d" % (hp, hpmax)
        f = f_num(int(56 * ss))
        w = f.getlength(txt)
        d.text((RW.CX * ss - w / 2, (RW.CY + R + 38) * ss), txt, font=f, fill=HP_GREEN + (255,), stroke_width=int(3 * ss), stroke_fill=(6, 16, 8, 255))


def render(spec, ss=2, lod=False, upright=True):
    theme = spec["theme"]
    boss = spec.get("boss")
    if boss:
        RW.CW, RW.CH, RW.CX, RW.CY = 1160, 1300, 580, 700
    else:
        RW.CW, RW.CH, RW.CX, RW.CY = 1100, 1200, 550, 610
    CW, CH = RW.CW, RW.CH
    canvas = np.zeros((CH * ss, CW * ss, 4), np.float32)
    if theme == "player":
        st = CLASS_STYLE[spec["cls"]]
        acc, emblem = st["acc"], st["emblem"]
    else:
        st = None
        acc, emblem = CORPS[theme]["col"], CORP_EMBLEM[theme]
    Rt = R_OUT + 40
    R1 = Rt + (24 if boss else 0)
    RW.ring_base(canvas, ss, R_OUT + 1, Rt, (0.025, 0.03, 0.04), acc, rim=1.4)
    if boss:
        RW.ring_base(canvas, ss, Rt, R1, tuple(min(1, v * 1.4) for v in CORPS[theme]["bezel"]), acc, rim=1.6)
    opts = dict(LOD) if lod else {}
    opts["upright"] = upright
    if boss:
        opts.update(boss=True, phase=boss.get("phase", 1))
    a = -30.0
    for i, sl in enumerate(spec["slots"]):
        val = sl["value"]
        if sl["program"] == "NULL" or (sl.get("special") and sl["special"] != "tariff"):
            val = None
        render_slice(canvas, RW.CX * ss, RW.CY * ss, sl["program"], a, 60, val, (0.3 + i * 0.137) % 1.0, theme, ss,
                     opts, seed=i + spec.get("seed", 1) * 7, glyph=SPECIAL_GLYPH.get(sl.get("special")),
                     badge=sl.get("badge"), special=sl.get("special"))
        a += 60
    over = Image.new("RGBA", (CW * ss, CH * ss), (0, 0, 0, 0))
    glow = Image.new("RGBA", (CW * ss, CH * ss), (0, 0, 0, 0))
    d, gd = ImageDraw.Draw(over), ImageDraw.Draw(glow)
    telemetry_ring(over, d, gd, spec, R_OUT + 1, Rt, ss, acc, spec.get("key", ""), emblem, lod)
    if boss:
        boss_band(d, gd, Rt, R1, ss, acc)
    if spec.get("ring"):
        RW.draw_inner_ring(over, d, gd, spec["ring"], ss, acc, st)
        hub_r = 96
    else:
        hub_r = 126
    hub = spec["hub"]
    RW.draw_hub(over, d, gd, ss, hub_r, acc, hub.get("emblem"), hub["name"], hub.get("sub", ""))
    if spec.get("resistance"):
        RW.draw_res_badge(over, d, gd, ss, spec["resistance"], hub_r, lock=spec.get("lock", False))
    R_piv = R_OUT + (44 if boss else 30)
    ptrs = spec.get("pointers", [0])
    for k, tk in enumerate(ptrs):
        ang = tk * 12
        if spec.get("orbit"):
            RW.draw_orbit(d, gd, ang, spec["orbit"], R_OUT + 18, ss, acc)
            RW.draw_pointer(d, gd, ang + spec["orbit"] * 12, R_piv, ss, acc, ghost=True)
        RW.draw_pointer(d, gd, ang, R_piv, ss, acc, label=str(k + 1) if len(ptrs) > 1 else None)
    hp = spec.get("hp")
    if hp:
        draw_hp(d, gd, ss, R1, hp[0], hp[1], pred=spec.get("pred", 0), phases=boss.get("pips") if boss else None,
                active_phase=boss.get("phase", 1) if boss else 1, number=spec.get("hp_number", True))
    if boss:
        RW.draw_banner(over, d, gd, ss, R1, boss["title"], boss["sub"], acc)
    glow = glow.filter(ImageFilter.GaussianBlur(7 * ss))
    g = np.asarray(glow, np.float32) / 255
    o = np.asarray(over, np.float32) / 255
    canvas[..., :3] = canvas[..., :3] + g[..., :3] * g[..., 3:] * 0.9
    canvas[..., 3:] = np.maximum(canvas[..., 3:], g[..., 3:] * 0.9)
    oa = o[..., 3:]
    canvas[..., :3] = canvas[..., :3] * (1 - oa) + o[..., :3] * oa
    canvas[..., 3:] = canvas[..., 3:] * (1 - oa) + oa
    im = Image.fromarray((np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")
    out = im.resize((CW, CH), Image.LANCZOS)
    centre = (RW.CX, RW.CY)
    RW.CW, RW.CH, RW.CX, RW.CY = 1100, 1200, 550, 610
    return out, centre
