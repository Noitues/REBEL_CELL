"""Boss Wheel v2 round 3: Aurelian Concord, THE PANTHEON (fresco gods) + the combined mechanic ASCENDANT + OMENS.

Every slice is a tiled fresco of a god whose domain is a real boss action (GDD 2.6 slice types, 2.5 resistance, 2.9
statuses, corp specials ART_BIBLE 3.4):
  Mars SHIM 14 | Jupiter OVERFLOW 24 | Minerva DEFRAG 12 | Mercury RESIST 2 (corp special, WEIGHT/RESIST glyph: the
  boss gains spin resistance 2 until its next turn - the protector of thieves turned against them) | Vulcan INFECT 3
  (burn = CORRUPTED) | Pluto NULL (the underworld void). Neptune (SHIM 10, SWEEP) swaps in for Mercury in phase 3.
Hub: the emperor's apotheosis. Needle: the royal box with the VERDICT emoji hand.

MECHANIC: ASCENDANT + OMENS.
- ASCENDANT: one god is gilded; its slice resolves x2. The gilding moves one god clockwise at the start of every
  boss turn (fixed order, no RNG; it skips Pluto), telegraphed a turn ahead (dashed gold outline + NEXT tab).
- OMENS: every hit the player lands cracks the god under the boss's needle (1 crack per hit, pips under the plaque).
  At 3 cracks the god turns WRATHFUL for the rest of the fight: its effect flips hostile (table in WRATH).
- ASCENDANT + WRATHFUL is the most dangerous state: the wrathful effect x2, gold leaf over the cracks, the fresco
  bleeding light, the emperor's thumb trembling. Cracking a god weakens nothing by itself; it is a bet on where the
  gilding will be when the god breaks.
"""
import math

import numpy as np
from PIL import Image, ImageChops, ImageDraw

import bw_kit as K
import fig_roman as F
import fresco as FR
import render2d as RD
import roman as RM
import roman_bc as RB
import wheel_v2 as W

GOLD = (255, 210, 77)
SLOTS = [
    dict(type="SHIM", value=14, god="mars", label="MARS", wrath=dict(type="SHIM", value=14, tag="PIERCE", text="SHIM 14 PIERCE (ignores block + shield)")),
    dict(type="OVERFLOW", value=24, god="jupiter", label="JUPITER", wrath=dict(type="OVERFLOW", value=24, tag="+CORRUPT", text="OVERFLOW 24 + CORRUPTED on your landed slice")),
    dict(type="DEFRAG", value=12, god="minerva", label="MINERVA", wrath=dict(type="SHIM", value=12, tag="COUNTER", text="guard -> counterattack: SHIM 12")),
    dict(type="NULL", value=None, god="pluto", label="PLUTO", wrath=dict(type="SHIM", value=6, tag="THE VOID BITES", text="NULL -> SHIM 6 (the void bites)")),
    dict(type="SANDBOX", value=2, god="mercury", label="MERCURY", glyph="special_weight", resist=True,
         wrath=dict(type="INFECT", value=1, glyph="special_weight", tag="-1 RAM", text="resistance -> theft: steals 1 RAM per landing")),
    dict(type="INFECT", value=3, god="vulcan", label="VULCAN", wrath=dict(type="INFECT", value=3, tag="SPREAD", text="burn spreads: CORRUPTED on 2 of your slices")),
]
NEPTUNE = dict(type="SHIM", value=10, god="neptune", label="NEPTUNE (SWEEP)")


def next_ascendant(i, slots):
    j = (i + 1) % len(slots)
    while slots[j]["type"] == "NULL":
        j = (j + 1) % len(slots)
    return j


class PantheonV3(RB.MosaicB):
    key = "V3"
    title = "V3  THE PANTHEON  (ascendant god)"
    blurb = ["Every slice is a tiled fresco of a god whose domain is a real boss action: Mars attacks, Jupiter crits,",
             "Minerva guards, Mercury grants RESISTANCE, Vulcan burns, Pluto is the void. ASCENDANT: one god is gilded x2,",
             "moving one god clockwise per turn. OMENS: your hits crack the god under the needle; 3 cracks = WRATHFUL (flipped)."]
    needle = RM.ArenaA.needle

    # ---------------- the panels
    def scene(self, slot, ctx, act, i):
        tq = round(ctx.t * 6) / 6.0 if not ctx.get("still") else 0.0
        asc = ctx.get("asc")
        ak = 1.0 if asc == i else 0.0
        if ctx.get("asc_from") == i:          # the gilding leaving this panel (animation)
            ak = 1 - ctx.get("asc_mix", 1.0)
        if ctx.get("asc_to") == i:
            ak = ctx.get("asc_mix", 0.0)
        wr = 1.0 if i in ctx.get("wrath_slots", ()) else 0.0
        key = ("scV3", ctx.S, slot["god"], tq, round(act, 2), i, round(ak, 2), wr, round(ctx.rot, 1))
        return self.cached(key, lambda: self._god(slot, ctx, tq, act, i, ak, wr))

    def _god(self, slot, ctx, t, act, i, ak, wr):
        S = ctx.S
        w = W.scene_box(ctx)
        ox, oy = RB.scene_offset(ctx, i, off=52)
        return FR.paint(slot["god"], w, K.TYPE_COL[slot["type"]], t, act, S, ox, oy, ascendant=ak, wrath=wr, seed=i, fig_k=0.74, tile=max(3.0, 4.4 * S))

    def blank_window(self, ctx, i, rot, wm, back, under):
        """Pluto = the NULL slice: the underworld void. A dark fresco barely there, art dimmed, the thin empty outline."""
        S = ctx.S
        w = W.scene_box(ctx)
        ox, oy = RB.scene_offset(ctx, i, off=52)
        sp = self.cached(("pluto", S, round(ctx.rot, 1)), lambda: FR.paint("pluto", w, (80, 80, 90), 0.0, 0.0, S, ox, oy, dark=True, seed=i, fig_k=0.74))
        cxs, cys = W.slice_centre(ctx, i, rot)
        lay = K.rgba(ctx.size)
        lay.alpha_composite(sp, (int(cxs - w / 2), int(cys - w / 2)))
        lay = K.masked(lay, wm)
        lay.alpha_composite(K.solid(K.blur(ImageChops.subtract(wm, K.shrink(wm, 16 * S)), 10 * S), (0, 0, 0), 0.8))
        em = W.wedge_mask(ctx, i, rot, inset=12)
        lay.alpha_composite(K.solid(ImageChops.subtract(em, K.shrink(em, max(1, 2.2 * S))), (110, 112, 124), 0.95))
        if i in ctx.get("wrath_slots", ()):
            lay = K.add(lay, K.solid(K.blur(K.shrink(wm, 30 * S), 30 * S), (255, 50, 30)), 0.5)
        return lay

    def slice_glass(self, ctx, i, rot, wm, slot):
        S = ctx.S
        lay = K.rgba(ctx.size)
        inner = ImageChops.subtract(wm, K.shrink(wm, 10 * S))
        lay.alpha_composite(K.solid(K.blur(inner, 6 * S), (40, 20, 10), 0.55))
        asc = ctx.get("asc") == i
        frame = ImageChops.subtract(K.shrink(wm, 4 * S), K.shrink(wm, (13 if asc else 9) * S))
        lay.alpha_composite(RB.gilt(frame, ctx.size, S, depth=2))
        if asc:
            lay = K.add(lay, K.solid(K.blur(frame, 8 * S), GOLD), 0.7)
        nc = ctx.get("cracks", {}).get(i, 0)
        wr = i in ctx.get("wrath_slots", ())
        if wr:
            nc = 3
        if nc > 0:
            both = wr and asc
            glow = (255, 200, 90) if both else ((255, 90, 50) if wr else (230, 190, 120))
            cr = K.rot_c(W.crack_layer(ctx, min(1.0, 0.18 + 0.3 * nc), 150, 330, 300 + i * 13, col=(40, 20, 16) if wr else (60, 44, 36),
                                       glow=glow, n_max=8), rot)
            cr = K.masked(cr, K.shrink(wm, 10 * S))
            lay.alpha_composite(cr)
            if both:      # the fresco bleeds light through the gold leaf
                lay = K.add(lay, K.solid(K.blur(cr.split()[3], 6 * S), (255, 190, 80)), 1.6 + 0.4 * math.sin(ctx.t * 9))
            elif wr:
                lay = K.add(lay, K.solid(K.blur(cr.split()[3], 4 * S), (255, 70, 40)), 0.8)
        return lay

    # ---------------- plaques: the ascendant god's value doubles, with a gold x2 tag
    def plaque(self, ctx, slot, i):
        asc = ctx.get("asc") == i
        wr = i in ctx.get("wrath_slots", ())

        def build():
            S = ctx.S
            s2 = dict(slot["wrath"]) if wr else dict(slot)
            if asc and s2.get("value") is not None:
                s2["value"] = s2["value"] * 2
            p = W.plaque(ctx, s2, RM.special_mask(slot))
            if not (asc or wr):
                return p
            pad = int(18 * S)
            out = K.rgba((p.width + pad * 2, p.height + pad * 2))
            out.alpha_composite(p, (pad, pad))
            d = ImageDraw.Draw(out)
            ring = GOLD if asc else (255, 70, 40)
            d.rounded_rectangle([pad + 6 * S, pad + 8 * S, pad + p.width - 6 * S, pad + p.height - 8 * S], radius=12 * S, outline=ring + (255,), width=max(1, int(2.5 * S)))
            if asc:
                tag = K.text_img("x2", K.f_num(int(24 * S)), fill=(40, 24, 0))
                tw, th = tag.width + 8 * S, tag.height + 2 * S
                d.rounded_rectangle([out.width - tw - 2 * S, 0, out.width - 2 * S, th], radius=6 * S, fill=GOLD + (255,), outline=(60, 36, 0, 255), width=max(1, int(1.5 * S)))
                out.alpha_composite(tag, (int(out.width - tw - 2 * S + 4 * S), int(1 * S)))
            if wr:
                tg = K.text_img(slot["wrath"]["tag"], K.f_ui(int(14 * S), b"Bold Condensed"), fill=(255, 255, 255))
                tw, th = tg.width + 10 * S, tg.height + 2 * S
                y0 = out.height - th - 1 * S
                d.rounded_rectangle([pad, y0, pad + tw, y0 + th], radius=5 * S, fill=(200, 40, 30, 255), outline=(60, 0, 0, 255), width=max(1, int(1.5 * S)))
                out.alpha_composite(tg, (int(pad + 5 * S), int(y0 + 1 * S)))
            return out
        return self.cached(("plqV3", ctx.S, i, slot.get("value"), asc, wr), build)

    # ---------------- the telegraph: a dashed gold outline on the next god + a gold arrow along the rim
    def fx(self, ctx, slots):
        asc = ctx.get("asc")
        if ctx.get("blur", 0) > 1:
            return None
        S = ctx.S
        lay = K.rgba(ctx.size)
        d = ImageDraw.Draw(lay)
        # omen pips: 3 small diamonds on the inner side of every plaque (filled = cracks; all red = wrathful)
        for i in range(len(slots)):
            nc = 3 if i in ctx.get("wrath_slots", ()) else ctx.get("cracks", {}).get(i, 0)
            a = W.slot_angle(i, ctx.rot)
            for q in range(3):
                x, y = ctx.P(343, a + (q - 1) * 4.0)
                sz = 5.5 * S
                on = q < nc
                c = (255, 70, 40) if nc >= 3 else ((255, 190, 90) if on else (60, 50, 44))
                d.polygon([(x, y - sz), (x + sz, y), (x, y + sz), (x - sz, y)], fill=c + (255,), outline=(20, 10, 10, 255))
        if asc is None:
            return lay
        nxt = ctx.get("asc_next", next_ascendant(asc, slots))
        a0 = W.slot_angle(nxt, ctx.rot)
        for r in (W.R["sl_in"] + 8, W.R["band_in"] - 6):
            for k in range(0, 52, 6):
                aa = a0 - 26 + k
                d.arc([ctx.cx - r * S, ctx.cy - r * S, ctx.cx + r * S, ctx.cy + r * S], aa - 90, aa - 90 + 3.5, fill=GOLD + (230,), width=max(1, int(3 * S)))
        for sg in (-1, 1):
            aa = a0 + sg * 27
            for k in range(0, 10):
                r0 = W.R["sl_in"] + 10 + k * 21
                d.line([ctx.P(r0, aa), ctx.P(r0 + 10, aa)], fill=GOLD + (230,), width=max(1, int(3 * S)))
        # small "NEXT" gold laurel tab on the rim of the next god
        x, y = ctx.P(W.R["bezel_out"] + 2, a0)
        t = K.text_img("NEXT", K.f_ui(int(13 * S), b"Bold Condensed"), fill=(40, 24, 0))
        d.rounded_rectangle([x - t.width / 2 - 4 * S, y - t.height / 2 - 1 * S, x + t.width / 2 + 4 * S, y + t.height / 2 + 1 * S], radius=4 * S,
                            fill=GOLD + (255,), outline=(60, 36, 0, 255))
        K.paste_c(lay, t, x, y)
        # the ascendant god's laurel crown tab
        xa, ya = ctx.P(W.R["bezel_out"] + 2, W.slot_angle(asc, ctx.rot) + 22)
        t2 = K.text_img("ASCENDANT", K.f_ui(int(13 * S), b"Bold Condensed"), fill=(40, 24, 0))
        d.rounded_rectangle([xa - t2.width / 2 - 5 * S, ya - t2.height / 2 - 2 * S, xa + t2.width / 2 + 5 * S, ya + t2.height / 2 + 2 * S], radius=4 * S,
                            fill=GOLD + (255,), outline=(60, 36, 0, 255), width=max(1, int(1.5 * S)))
        K.paste_c(lay, t2, xa, ya)
        return lay

    # ---------------- hub: the apotheosis
    def hub(self, ctx):
        tq = round(ctx.t * 6) / 6.0 if not ctx.get("still") else 0.0
        return self.cached(("hubV3", ctx.S, ctx.phase, tq), lambda: self._apotheosis(ctx, tq))

    def _apotheosis(self, ctx, t):
        S = ctx.S
        cx, cy = ctx.cx, ctx.cy
        R0 = W.R["hub"] * S
        w = int(R0 * 2 + 8)
        sky = K.rad_grad((w, w), w / 2, w * 0.42, w * 0.6, (40, 70, 140) if ctx.phase < 2 else (150, 50, 30), (8, 16, 44) if ctx.phase < 2 else (50, 10, 10))
        d = ImageDraw.Draw(sky)
        rot = t * 6
        for j in range(18):
            a = math.radians(j * 20 + rot)
            d.polygon([(w / 2, w * 0.42), (w / 2 + w * math.cos(a - 0.06), w * 0.42 + w * math.sin(a - 0.06)),
                       (w / 2 + w * math.cos(a + 0.06), w * 0.42 + w * math.sin(a + 0.06))], fill=(255, 200, 90, 120))
        px = int(w * 0.86)
        m = F.emperor(px * 2, 0, 0)
        sz = (px * 2, px * 2)
        bust = RD.relief(m["main"], sz, stone=(236, 230, 220), shadow=(110, 96, 100), hi=(255, 255, 250), s=2 * S, depth=6)
        bust.alpha_composite(K.solid(K.mask_mul(m["detail"], m["main"]), (150, 136, 130), 0.55))
        bust.alpha_composite(RD.relief(m["glint"], sz, stone=(232, 186, 80), shadow=(110, 70, 20), hi=(255, 240, 180), s=2 * S, depth=3))
        bust.alpha_composite(K.solid(m["eye"], (255, 220, 120)))
        bust = K.keyline(bust, 6 * S, col=(30, 20, 20))
        bust = bust.resize((px, px), Image.LANCZOS)
        mos = RD.mosaic(sky, max(3.0, 4.2 * S), seed=5, grout=(30, 30, 50), gap=0.12)
        mos.alpha_composite(K.drop_shadow(bust, 0, int(4 * S), 4 * S, 0.6), (int(w / 2 - px / 2 + 4 * S), int(w / 2 - px / 2 + 10 * S)))
        disc = K.ring_mask((w, w), w / 2, w / 2, 0, R0)
        im = K.rgba(ctx.size)
        im.alpha_composite(K.masked(mos, disc), (int(cx - w / 2), int(cy - w / 2)))
        f = K.f_ui(int(12 * S), b"Bold Condensed")
        t1 = K.text_img("DIVUS IMPERATOR", f, fill=(250, 244, 230), stroke=max(1, int(1.5 * S)))
        dd = ImageDraw.Draw(im)
        pw, ph = t1.width + 12 * S, t1.height + 4 * S
        dd.rounded_rectangle([cx - pw / 2, cy + 82 * S - ph / 2, cx + pw / 2, cy + 82 * S + ph / 2], radius=4 * S, fill=(14, 8, 12, 220), outline=GOLD + (255,))
        K.paste_c(im, t1, cx, cy + 82 * S)
        ring = K.ring_mask(ctx.size, cx, cy, R0, R0 + 14 * S)
        im.alpha_composite(RB.gilt(ring, ctx.size, S, depth=3))
        return im


def wrath_demo():
    """Mechanic B (proposal, drawn for comparison): a cracked god turns wrathful and flips its meaning."""
    return None
