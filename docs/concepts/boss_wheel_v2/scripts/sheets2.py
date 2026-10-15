"""Boss Wheel v2: final, emblem, readability, compare and system sheets.

python sheets2.py final roman|atlantis      -> <corp>_wheel_final.png (full combat frame + combat size + 2x close-up + needle states)
python sheets2.py emblem roman|atlantis     -> <corp>_boss_emblem.png
python sheets2.py readability               -> readability_test.png
python sheets2.py compare                   -> compare_v1_v2.jpg
python sheets2.py system                    -> system.png
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
from PIL import Image, ImageChops, ImageDraw, ImageFilter  # noqa: E402

import bw_kit as K  # noqa: E402
import directions  # noqa: E402
import emoji_hand as EH  # noqa: E402
import sheets as SH  # noqa: E402
import wheel_v2 as W  # noqa: E402

OUT = K.OUTDIR
SW, SH_ = 1920, 1080
FINAL = {"roman": "D", "atlantis": "D"}
REST = {"roman": dict(rot=0.0, forecast=0), "atlantis": dict(rot=180.0, forecast=0)}     # slot 0 under each needle
HIT = {"roman": -1.0, "atlantis": 1.0}
CC = SH.CORP_COL


def needle_crop(w, corp, S):
    c = w.width / 2
    if corp == "atlantis":   # the needle is the beak: crop the head + the bottom slice
        return w.crop((int(c - 190 * S * 1.5), int(c - 200 * S * 1.5), int(c + 190 * S * 1.5), int(c + 260 * S * 1.5)))
    return w.crop((int(c - 260 * S * 1.4), int(c - 700 * S), int(c + 260 * S * 1.4), int(c - 300 * S)))


def final(corp):
    key = FINAL[corp]
    col = CC[corp]
    big = Image.new("RGBA", (SW, SH_ * 2), SH.BG + (255,))
    st = dict(REST[corp], gesture=0.0)
    frame = SH.combat_frame(corp, key, st, tip=False, label_txt="BOSS WHEEL v2 FINAL  |  %s  |  r = 236 px" % directions.CORPS[corp]["name"])
    big.alpha_composite(frame, (0, 0))
    lower = SH.sheet("%s  //  FINAL: %s" % (directions.CORPS[corp]["name"], directions.get(corp, key)[0].title.replace("FINAL  ", "")),
                     SH.CORP_NAME[corp] + "  |  combat size, 2x close-up, the needle reacting", col)
    d = ImageDraw.Draw(lower)
    w1, D, ctx, slots = SH.render(corp, key, SH.COMBAT_S, **st)
    cw = w1.width
    cr = w1.crop((int(cw * 0.12), int(cw * 0.04), int(cw * 0.88), int(cw * 0.86)))
    lower.alpha_composite(cr, (40, 120))
    SH.label(d, (48, 104), "COMBAT SIZE 1:1 (r = 236 px), rest", col, K.f_ui(18, b"Bold Condensed"))
    S2 = SH.COMBAT_S * 2
    w2, _, ctx2, _ = SH.render(corp, key, S2, **st)
    c2 = w2.width / 2
    if corp == "atlantis":
        cl = w2.crop((int(c2 - 470), int(c2 - 160), int(c2 + 470), int(c2 + 500)))
    else:
        cl = w2.crop((int(c2 - 470), int(c2 - 640 * S2), int(c2 + 470), int(c2 - 640 * S2 + 660)))
    lower.alpha_composite(cl, (900, 110))
    d.rectangle([900, 110, 900 + cl.width, 110 + cl.height], outline=col + (120,), width=2)
    SH.label(d, (908, 116), "2x CLOSE-UP", col, K.f_ui(18, b"Bold Condensed"))
    states = [("REST (deliberating)", dict(st)),
              ("HIT: lands PERFECT on SHIM 14" if corp == "roman" else "HIT: lands PERFECT on SHIM 12",
               dict(st, gesture=HIT[corp], landed=0, tier="PERFECT", latch=1.0, grab=1.0, finisher=0.6, beak=0.0, act_slot=0, act=0.6)),
              ("WHIFF: lands on the blank", dict(st, gesture=-HIT[corp], landed=3, tier="GOOD", rot=st["rot"] - 180, recoil=1.0, grab=0.0))]
    for j, (nm, s_) in enumerate(states):
        w3, _, _, _ = SH.render(corp, key, SH.COMBAT_S, **s_)
        c3 = w3.width / 2
        if corp == "atlantis":
            crp = w3.crop((int(c3 - 170), int(c3 - 60), int(c3 + 170), int(c3 + 190)))
        else:
            crp = w3.crop((int(c3 - 170), int(c3 - 700 * SH.COMBAT_S), int(c3 + 170), int(c3 - 700 * SH.COMBAT_S + 250)))
        xx = 900 + j * 340
        lower.alpha_composite(crp, (xx, 800))
        d.rectangle([xx, 800, xx + 340, 1050], outline=(70, 70, 86), width=1)
        SH.label(d, (xx + 6, 1054), nm, (220, 220, 230), K.f_ui(15, b"Bold Condensed"))
    for k_, ln in enumerate(D.blurb):
        SH.label(d, (48, 940 + k_ * 26), ln, (220, 222, 230), K.f_ui(18))
    big.alpha_composite(lower, (0, SH_))
    p = os.path.join(OUT, "%s_wheel_final.png" % corp)
    big.convert("RGB").save(p)
    print(p)


# ------------------------------------------------------------------ emblems
def octopus_emblem(px, ring=(47, 107, 255), bg=(6, 17, 42), border=True, phase=1):
    """The Black Smoker emblem, matched to the final: the head (mantle + glaring gold eyes + the beak pointing down)
    with six arms radiating and curling (the wheel), two blue rings. Flat, thick ink outline, one highlight."""
    ss = 2
    W_ = px * ss
    out = K.rgba((W_, W_))
    d = ImageDraw.Draw(out)
    c = W_ / 2
    r = W_ * (0.455 if border else 0.5)
    if border:
        d.ellipse([0, 0, W_ - 1, W_ - 1], fill=(250, 248, 244, 255))
    d.ellipse([c - r, c - r, c + r, c + r], fill=(14, 10, 22, 255))
    d.ellipse([c - r * 0.93, c - r * 0.93, c + r * 0.93, c + r * 0.93], fill=ring + (255,))
    d.ellipse([c - r * 0.84, c - r * 0.84, c + r * 0.84, c + r * 0.84], fill=bg + (255,))
    k = r / 100
    body = K.L((W_, W_))
    bd = ImageDraw.Draw(body)
    curls = []
    for j in range(8):
        a0 = j * 45 + 22.5
        pts = []
        sg = 1 if j % 2 else -1
        for q in range(16):
            u = q / 15
            aa = a0 + sg * 22 * math.sin(u * 3.0)
            rr = (20 + 60 * u) * k
            pts.append(K.pol(c, c + 6 * k, rr, aa))
        bd.polygon(K.stroke_poly(pts, 15 * k, 5 * k), fill=255)
        x, y = pts[-1]
        bd.ellipse([x - 2.5 * k, y - 2.5 * k, x + 2.5 * k, y + 2.5 * k], fill=255)
        tx, ty = K.pol(x, y, 6 * k, a0 + sg * 70)
        curls.append((tx, ty))
        bd.ellipse([tx - 6.5 * k, ty - 6.5 * k, tx + 6.5 * k, ty + 6.5 * k], fill=255)
    bd.polygon(K.catmull([(c, c - 58 * k), (c + 34 * k, c - 44 * k), (c + 40 * k, c), (c + 26 * k, c + 30 * k), (c, c + 38 * k),
                          (c - 26 * k, c + 30 * k), (c - 40 * k, c), (c - 34 * k, c - 44 * k)], 10), fill=255)
    skin = (190, 56, 64) if phase < 2 else (226, 70, 50)
    lay = K.solid(K.grow(body, 5 * k), (14, 10, 22))
    lay.alpha_composite(K.solid(body, skin))
    sh = ImageChops.subtract(body, K.shifted(body, -4 * k, -5 * k))
    lay.alpha_composite(K.solid(sh, K.mul(skin, 0.7)))
    ld = ImageDraw.Draw(lay)
    ld.arc([c - 26 * k, c - 50 * k, c + 6 * k, c - 18 * k], 200, 260, fill=(255, 230, 220, 220), width=max(1, int(3 * k)))   # one highlight
    for tx, ty in curls:      # the curled tips: an ink spiral hole
        ld.ellipse([tx - 2.6 * k, ty - 2.6 * k, tx + 2.6 * k, ty + 2.6 * k], fill=(14, 10, 22, 255))
    for sx in (-1, 1):                                                                         # blue rings
        ld.ellipse([c + sx * 22 * k - 6 * k, c - 30 * k - 6 * k, c + sx * 22 * k + 6 * k, c - 30 * k + 6 * k], outline=(70, 170, 255, 255), width=max(1, int(2.6 * k)))
    for sx in (-1, 1):                                                                         # glaring gold eyes
        ex, ey = c + sx * 19 * k, c + 6 * k
        ld.ellipse([ex - 11 * k, ey - 8 * k, ex + 11 * k, ey + 8 * k], fill=(14, 10, 22, 255))
        ld.ellipse([ex - 8.5 * k, ey - 5.5 * k, ex + 8.5 * k, ey + 5.5 * k], fill=(255, 196, 70, 255))
        ld.rectangle([ex - 6 * k, ey - 1.6 * k, ex + 6 * k, ey + 1.6 * k], fill=(14, 10, 22, 255))
        ld.polygon([(ex - 11 * k, ey - 9 * k), (ex + 11 * k, ey - 9 * k - sx * 0), (ex + sx * 11 * k, ey - 2 * k), (ex - sx * 11 * k, ey - 6 * k)], fill=skin + (255,))
    ld.polygon([(c - 8 * k, c + 22 * k), (c + 8 * k, c + 22 * k), (c, c + 40 * k)], fill=(30, 24, 26, 255), outline=(14, 10, 22, 255))   # beak down
    out.alpha_composite(lay)
    return out.resize((px, px), Image.LANCZOS)


def emblem(corp):
    col = CC[corp]
    im = SH.sheet("%s  //  BOSS EMBLEM" % directions.CORPS[corp]["name"],
                  "matched to the final wheel  |  sticker roundel, 512 / 64 / 32 / 16 px, greyscale", col)
    d = ImageDraw.Draw(im)
    if corp == "roman":
        mk = lambda px, **kw: EH.emblem(px, **kw)  # noqa: E731
        note = ["THE VERDICT HAND: an original emoji-style thumbs-down (chunky fist, flat shading, one highlight, thick",
                "outline, gold laurel cuff, imperial-purple sleeve). It is the SAME drawing as the needle: the emperor's",
                "hand on the royal box turns down on a hit and up on a whiff. The emblem shows the down pose."]
    else:
        mk = lambda px, **kw: octopus_emblem(px, **kw)  # noqa: E731
        note = ["THE BLACK SMOKER: the octopus that IS the wheel, flattened to a sticker: the head with glaring gold eyes,",
                "the beak pointing down (the needle), eight arms radiating and curling (six are the slice borders), two blue rings",
                "(they glow in phase 2). Approved octopus direction, pushed to the v2 final's drawing."]
    hero = mk(512)
    im.alpha_composite(hero, (60, 130))
    x = 640
    for px in (256, 128, 64, 32, 16):
        e = mk(px)
        im.alpha_composite(e, (x, 380 - px // 2))
        SH.label(d, (x, 520), "%d px" % px, (200, 200, 210), K.f_mono(16))
        x += px + 40
    # on light + greyscale
    lt = Image.new("RGBA", (420, 220), (236, 232, 222, 255))
    lt.alpha_composite(mk(180), (20, 20))
    lt.alpha_composite(K.greyscale(mk(180)), (220, 20))
    im.alpha_composite(lt, (640, 580))
    SH.label(d, (640, 808), "on paper  |  greyscale", (200, 200, 210), K.f_mono(16))
    if corp == "roman":   # the needle poses: the same drawing
        for j, (g, nm) in enumerate(((-1, "down: HIT"), (0, "sideways: REST"), (1, "up: WHIFF / BLOCKED"))):
            h = EH.hand_rgba(150, g, pivot_centre=True, pivot=(200, 10), swing=-1.0)
            im.alpha_composite(h, (1120 + j * 250, 560))
            SH.label(d, (1150 + j * 250, 870), nm, (220, 220, 230), K.f_ui(17, b"Bold Condensed"))
        SH.label(d, (1120, 540), "THE NEEDLE'S HAND (same drawing, wrist roll about the sleeve root)", col, K.f_ui(17, b"Bold Condensed"))
    else:
        for j, ph in enumerate((1, 2)):
            im.alpha_composite(octopus_emblem(200, phase=ph), (1140 + j * 260, 600))
            SH.label(d, (1160 + j * 260, 810), "phase %d" % ph, (220, 220, 230), K.f_ui(17, b"Bold Condensed"))
    for k_, ln in enumerate(note):
        SH.label(d, (60, 930 + k_ * 28), ln, (220, 222, 230), K.f_ui(19))
    p = os.path.join(OUT, "%s_boss_emblem.png" % corp)
    im.convert("RGB").save(p)
    print(p)


# ------------------------------------------------------------------ readability
def readability():
    im = SH.sheet("BOSS WHEEL v2  //  READABILITY TEST", "combat size (r = 236 px): full art | values only | 2 px blur + greyscale | reduce-effects end states",
                  (255, 214, 64))
    d = ImageDraw.Draw(im)
    S = SH.COMBAT_S
    y0 = 110
    for row, corp in enumerate(("roman", "atlantis")):
        key = FINAL[corp]
        st = dict(REST[corp], gesture=0.0)
        full, D, ctx, slots = SH.render(corp, key, S, **st)
        vals, _, _, _ = SH.render(corp, key, S, hide=("back_plate", "art_ring_under", "slice_scenes", "blank_window", "art_ring_over",
                                                       "hub_portrait", "inner_ring", "fx", "threat_ring"), **st)
        cw = full.width
        box = (int(cw * 0.14), int(cw * 0.08), int(cw * 0.86), int(cw * 0.84))
        sc = 0.47
        for col_, img in enumerate((full, vals, K.greyscale(full.filter(ImageFilter.GaussianBlur(2))))):
            c = img.crop(box)
            c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
            bgp = Image.new("RGBA", c.size, (14, 12, 18, 255))
            bgp.alpha_composite(c)
            im.alpha_composite(bgp, (20 + col_ * 330, y0 + 20 + row * 470))
        SH.label(d, (24, y0 + row * 470 - 2), "%s  (%s)  - left: full | middle: values only | right: blur + greyscale (shown at 0.47 of combat size)" %
                 (directions.CORPS[corp]["name"], corp), CC[corp], K.f_ui(16, b"Bold Condensed"))
        # reduce-effects end states (static, no flash, no particles)
        ends = [("LANDED (no latch anim, rail recolour only)", dict(st, landed=0, tier="PERFECT", latch=1.0, gesture=HIT[corp], grab=1.0, beak=0.0)),
                ("PHASE 2 (instant swap, no flash)", dict(st, phase=2, hp=0.6, dmg=0.3, gates=1.0, blink=0.0)),
                ("WHIFF (pose only)", dict(st, landed=3, tier="GOOD", rot=st["rot"] - 180, gesture=-HIT[corp], recoil=1.0))]
        for j, (nm, s_) in enumerate(ends):
            w_, _, _, _ = SH.render(corp, key, S * 0.62, **s_)
            cw_ = w_.width
            c = w_.crop((int(cw_ * 0.12), int(cw_ * 0.04), int(cw_ * 0.88), int(cw_ * 0.86)))
            bgp = Image.new("RGBA", c.size, (14, 12, 18, 255))
            bgp.alpha_composite(c)
            xx = 1010 + j * 300
            im.alpha_composite(bgp.resize((290, int(290 * c.height / c.width)), Image.LANCZOS), (xx, y0 + row * 470 + 30))
            SH.label(d, (xx, y0 + row * 470 + 360), nm, (210, 210, 220), K.f_ui(14, b"Bold Condensed"))
    # measured value size at combat scale
    f = K.f_num(int(W.NUM_PX * S))
    bb = f.getbbox("24")
    txt = ("Value numerals at combat size: Bahnschrift Bold Condensed %d px (cap height %d px), white on a 92 %% dark plaque with a "
           "type-colour cap; glyph %d px. The plaque radius is fixed (r 290) on every boss." % (int(W.NUM_PX * S), bb[3] - bb[1], int(W.GLYPH_PX * S)))
    SH.label(d, (24, 1050), txt, (230, 230, 236), K.f_ui(17))
    p = os.path.join(OUT, "readability_test.png")
    im.convert("RGB").save(p)
    print(p)


# ------------------------------------------------------------------ compare v1 / v2
def compare():
    W2 = r"D:\Godot\rebel_cell\docs\art_review\PLAN1\W2R2_GROUP.jpg"
    g = Image.open(W2).convert("RGB")
    # section 5 right panel: the 1080p build scaled to 960x540; the boss wheel sits on its right
    mainline = g.crop((1325, 2690, 1560, 2945)).resize((470, 510), Image.LANCZOS)   # 2x: back to 1080p scale
    r41 = Image.open(os.path.join(SH.R41C, "boss_manifest.png")).convert("RGBA")
    c41 = r41.width / 2
    r41c = r41.crop((int(c41 - 340), int(c41 - 360), int(c41 + 340), int(c41 + 330)))
    panels = [("v1 MAINLINE BUILD (W2R2, boss wheel)", mainline.convert("RGBA")), ("v1 CONCEPT (round 41, THE MANIFEST)", r41c)]
    for corp in ("roman", "atlantis"):
        w, _, _, _ = SH.render(corp, FINAL[corp], SH.COMBAT_S, **dict(REST[corp], gesture=0.0))
        cw = w.width
        panels.append(("v2 FINAL %s" % directions.CORPS[corp]["name"], w.crop((int(cw * 0.12), int(cw * 0.04), int(cw * 0.88), int(cw * 0.86)))))
    im = Image.new("RGBA", (1920, 820), SH.BG + (255,))
    d = ImageDraw.Draw(im)
    d.text((30, 20), "BOSS WHEEL  v1  vs  v2", font=K.f_anton(42), fill=(255, 255, 255))
    d.text((520, 38), "same combat size (r = 236 px); the mainline crop is from a 960 x 540 capture, upscaled", font=K.f_mono(18), fill=(200, 200, 210))
    x = 20
    for nm, p_ in panels:
        sc = 0.62     # one scale for every panel: all are at combat size (the mainline crop was upscaled 2x from 960 x 540)
        p2 = p_.resize((int(p_.width * sc), int(p_.height * sc)), Image.LANCZOS)
        bgp = Image.new("RGBA", p2.size, (14, 12, 18, 255))
        bgp.alpha_composite(p2)
        im.alpha_composite(bgp, (x + (460 - p2.width) // 2, 130 + (640 - p2.height) // 2))
        d.text((x, 96), nm, font=K.f_ui(19, b"Bold Condensed"), fill=(255, 214, 64) if nm.startswith("v2") else (200, 200, 210))
        x += 475
    p = os.path.join(OUT, "compare_v1_v2.jpg")
    im.convert("RGB").save(p, quality=92)
    print(p)


# ------------------------------------------------------------------ system: the exploded layer stack
SLOTS_DOC = [
    ("needle_rig", "the thematic pointer; carries pointer_angle (top by default, 180 for the octopus beak), the precision latch and the value window"),
    ("hub_portrait", "the boss portrait or emblem, animated; fixed (does not turn)"),
    ("plaques", "value + locked glyph on a dark plaque, upright, r 290: always on top of the art"),
    ("art_ring_over", "static (or self-rotating) art over the rim: arches, tentacles, gates; kept clear of r < 318 except the borders"),
    ("bezel + threat_ring + hp_arc", "the D4 lens & rail frame in the corp material; rail splits round the needle; HP arc + phase pips"),
    ("inner_ring (optional)", "boss inner ring: 3 x 10-tick segments (round 45: active segment raised, ghost wedge on the outer slice)"),
    ("rim_band + plaque_zone", "slice colour = type as a band at the rim; art under each plaque desaturated and darkened"),
    ("slice_scenes[] + blank_window", "one illustrated scene per slice, masked to its wedge; NULL = dark glass, art dimmed, thin empty outline"),
    ("art_ring_under", "ring art behind the slices, turns with the wheel (3 % lag in a spin = parallax)"),
    ("back_plate", "static stage behind everything (stands, vent field); seen through the blank window; parallax depth 1.0"),
]


def system():
    im = SH.sheet("BOSS WHEEL v2  //  THE TEMPLATE", "one compositor, named layer slots: every boss is built the same way", (255, 214, 64))
    d = ImageDraw.Draw(im)
    S = 0.5
    groups = [("back_plate",), ("art_ring_under",), ("slice_scenes", "blank_window"), ("rim_band",), ("bezel", "threat_ring"),
              ("inner_ring",), ("art_ring_over",), ("plaques",), ("hub_portrait",), ("needle_rig",)]
    for ci, corp in enumerate(("roman", "atlantis")):
        st = dict(REST[corp], gesture=0.0)
        D, slots = directions.get(corp, FINAL[corp])
        ctx = W.Ctx(S, t=0.0, phase=1, hp=0.86, still=True, **st)
        full, L_ = W.compose(D, ctx, slots, return_layers=True)
        cx0 = 300 + ci * 520
        for gi, grp in enumerate(groups):
            lay = K.rgba(full.size)
            for n in grp:
                if n in L_:
                    lay.alpha_composite(L_[n])
            if lay.getbbox() is None:
                continue
            wdt = 420
            flat = lay.resize((wdt, int(wdt * 0.36)), Image.LANCZOS)
            y = 1066 - gi * 82 - flat.height
            # plate outline (ellipse) so empty planes still read
            pl = K.rgba(flat.size)
            ImageDraw.Draw(pl).ellipse([2, 2, flat.width - 3, flat.height - 3], outline=(90, 90, 110, 160), width=2)
            im.alpha_composite(pl, (cx0 - wdt // 2, y))
            im.alpha_composite(K.drop_shadow(flat, 0, 6, 6, 0.5), (cx0 - wdt // 2 - 0, y - 0))
        SH.label(d, (cx0 - 200, 104), "%s (%s final)" % (directions.CORPS[corp]["name"], corp), CC[corp], K.f_ui(19, b"Bold Condensed"))
    xs = 1080
    SH.label(d, (xs, 110), "LAYER SLOTS (top of the stack first)", (255, 214, 64), K.f_ui(22, b"Bold Condensed"))
    for j, (nm, desc) in enumerate(SLOTS_DOC):
        y = 150 + j * 78
        SH.label(d, (xs, y), nm, (255, 255, 255), K.f_ui(20, b"Bold Condensed"))
        words, line, yy = desc.split(" "), "", y + 26
        for wd in words:
            if K.f_ui(16).getlength(line + " " + wd) > 800:
                SH.label(d, (xs, yy), line, (190, 194, 206), K.f_ui(16))
                yy += 20
                line = wd
            else:
                line = (line + " " + wd).strip()
        SH.label(d, (xs, yy), line, (190, 194, 206), K.f_ui(16))
    SH.label(d, (xs, 950), "+ fx_idle / fx_land / fx_phase: motion layers, each with a static reduce-effects end state", (255, 214, 64), K.f_ui(17))
    SH.label(d, (xs, 978), "Exploded views are the real layers of each final, squashed for perspective (bottom = back).", (170, 170, 186), K.f_ui(16))
    p = os.path.join(OUT, "system.png")
    im.convert("RGB").save(p)
    print(p)


if __name__ == "__main__":
    w = sys.argv[1]
    if w == "final":
        final(sys.argv[2])
    elif w == "emblem":
        emblem(sys.argv[2])
    elif w == "readability":
        readability()
    elif w == "compare":
        compare()
    elif w == "system":
        system()
