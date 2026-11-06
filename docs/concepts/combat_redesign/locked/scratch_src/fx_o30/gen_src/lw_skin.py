"""lw_skin: the NEUTRAL corp-side base (clean enamel graphite, no corp hue) as one Skin token set, plus the corp-independent THIS TURN tape.
Every layer is a function of (X, Y, RHO, TH) -> (rgb, alpha) and reads only self.pal, so a corp skin = a subclass or a new pal + overrides.
Layers: cell, bezel, annulus, arcframe, rim (materials); rim_vector, crest, cell_detail, token_frame, disc_frame, ticket (vector pieces).
The tape is NOT a skin layer: NeutralTape below is applied for every corp (ART CALL 53 default: one neutral THIS TURN tape)."""
import math, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from cs_skin import Skin, Acc, sstep, mixc
from cv_lib import C, ppx


class NeutralSkin(Skin):
    name = 'neutral'
    pal = dict(bed=(9, 11, 15), panel=(40, 50, 64), panel_hi=(110, 124, 142), steel=(116, 128, 144), steel_d=(70, 80, 94),
               line=(188, 200, 214), ink=(8, 9, 12), accent=(150, 162, 178))
    hue_shift = 0.0

    # ---------------------------------------------------------------- materials
    def cell(self, X, Y, RHO, TH, empty=False):
        P = self.pal
        acc = Acc(X.shape)
        acc.add(P['panel'], 0.30)                                           # clean enamel tint over the slate cell (kind wash survives)
        sector = np.abs(((TH + 30) % 60) - 30)
        acc.add(P['panel_hi'], (1 - sstep(0.0, 0.45, np.abs(((TH + 5) % 10) - 5) * RHO * 0.01745)) * 0.07)      # fine polar index lines every 10 degrees
        acc.add(P['panel_hi'], (1 - sstep(0.0, 0.5, np.abs(((RHO - 214) % 9.5) - 4.75) - 4.25)) * 0.05)           # and rings every 9.5 px
        acc.add((235, 242, 250), np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 2 * 0.05)                        # a soft gloss
        return acc.rgb, acc.a

    def bezel(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        u = np.clip((RHO - 388) / 34.0, 0, 1)
        acc.add((22, 27, 34), 1.0)
        acc.add(P['panel'], 0.45 + 0.25 * np.sin(np.pi * u))
        acc.add((220, 230, 242), (0.5 + 0.5 * np.cos(2 * np.pi * RHO / 2.4)) * 0.035)                         # brushed rings
        acc.add((255, 255, 255), np.clip(np.cos(np.radians(TH - 315)), 0, 1) ** 3 * np.exp(-((u - 0.2) / 0.12) ** 2) * 0.10)
        lip = (1 - sstep(0.0, 1.0, np.abs(RHO - 389.4))) + (1 - sstep(0.0, 1.0, np.abs(RHO - 420.6)))
        acc.add(P['line'], np.clip(lip, 0, 1) * 0.55)
        return acc.rgb, acc.a

    def annulus(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        acc.add((8, 11, 16), 0.55)
        acc.add(P['panel_hi'], (1 - sstep(0.0, 0.6, np.abs(((RHO - 424) % 8.0) - 4.0) - 3.6)) * 0.06)
        return acc.rgb, acc.a

    def rim(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        u = np.clip((RHO - 489.0) / 11.0, 0, 1)
        k = 0.80 + 0.20 * np.sin(np.pi * u) + 0.10 * np.cos(np.radians(TH - 315))
        acc.add(np.array(P['steel'], np.float32)[None, None] * k[..., None], 1.0)
        ph = (TH / 360.0 * 360.0) % 1.0                                                                          # a degree scale: one tick per degree, a long tick every 10
        tick = (ph < 0.12) * ((u > 0.45) | (np.round(TH) % 10 == 0))
        acc.add(P['ink'], tick.astype(np.float32) * 0.55)
        return acc.rgb, acc.a

    def arcframe(self, X, Y, RHO, TH):
        P = self.pal
        acc = Acc(X.shape)
        acc.add((26, 33, 42), 0.55)
        acc.add(P['panel_hi'], (1 - sstep(0.0, 0.5, np.abs(((RHO - 200) % 5.0) - 2.5) - 2.2)) * 0.05)
        return acc.rgb, acc.a

    # ---------------------------------------------------------------- vectors
    def rim_vector(self, L):
        for r in (488.6, 500.2):
            L.line(L.arc_pts(C, r, 0, 360, 360), (10, 12, 16), 1.6)
        for k in range(6):
            x, y = ppx(C, 494.5, 30 + 60 * k)
            self.crest(L, x, y, 1.2)

    def crest(self, L, x, y, s=1.0):
        """the neutral corp plate: a dark roundel with a pale ring and a bar.  A corp skin replaces this with its own crest."""
        P = self.pal
        h = 9.0 * s
        L.ellipse([x - h - 1.6, y - h - 1.6, x + h + 1.6, y + h + 1.6], fill=(8, 9, 12))
        L.ellipse([x - h, y - h, x + h, y + h], fill=(30, 36, 46))
        L.ellipse([x - h * 0.62, y - h * 0.62, x + h * 0.62, y + h * 0.62], outline=P['line'], w=1.3 * s)
        L.rect([x - h * 0.3, y - 0.8 * s, x + h * 0.3, y + 0.8 * s], fill=P['line'])

    def cell_detail(self, L, poly, dep, empty, seed):
        pp = poly + [poly[0]]
        L.line(pp, mixc(self.pal['line'], (12, 14, 18), 0.45) + (120,), 1.0)

    def token_frame(self, L, x, y, R, kind, dep):
        P = self.pal
        L.ellipse([x - R - 6.6, y - R - 6.6, x + R + 6.6, y + R + 6.6], fill=(8, 9, 12))
        L.ellipse([x - R - 5.0, y - R - 5.0, x + R + 5.0, y + R + 5.0], fill=mixc(P['steel'], (20, 24, 30), 0.35))
        L.ellipse([x - R - 5.0, y - R - 5.0, x + R + 5.0, y + R + 5.0], outline=mixc(P['line'], (20, 24, 30), 0.2), w=1.0)
        L.ellipse([x - R - 1.8, y - R - 1.8, x + R + 1.8, y + R + 1.8], fill=(8, 9, 12))

    def disc_frame(self, L, x, y, R):
        P = self.pal
        L.ellipse([x - R - 4.4, y - R - 4.4, x + R + 4.4, y + R + 4.4], fill=(8, 9, 12))
        L.ellipse([x - R - 3.2, y - R - 3.2, x + R + 3.2, y + R + 3.2], fill=mixc(P['steel'], (20, 24, 30), 0.35))
        L.ellipse([x - R - 1.4, y - R - 1.4, x + R + 1.4, y + R + 1.4], fill=(8, 9, 12))

    def ticket(self, L, box, nearest, climax):
        P = self.pal
        x0, y0, x1, y1 = box
        pts = [(x0 + 3, y0), (x1 - 3, y0), (x1, y0 + 3), (x1, y1 - 3), (x1 - 3, y1), (x0 + 3, y1), (x0, y1 - 3), (x0, y0 + 3)]
        L.poly(pts, fill=(26, 32, 41, 255))
        L.line(pts + [pts[0]], (8, 9, 12), 4.2)
        L.line(pts + [pts[0]], P['line'] if nearest else mixc(P['line'], (26, 32, 41), 0.45), 1.6)


class NeutralTape:
    """THIS TURN / +N tape: one treatment for every corp.  The orange SCHEDULE fill is remapped to cool silver; the generator's chevrons and text ride on top as tone.
    Corp independent on purpose (O-27 follow-up): time grammar must not take the corp hue."""
    lo = (118, 128, 142)
    hi = (232, 238, 244)
    hue_lo, hue_hi = 8.0, 36.0          # degrees: the SCHEDULE orange band (the HOLD amber and the plan yellow sit above it and are left alone)

    @classmethod
    def remap(cls, im):
        rgba = np.asarray(im.convert('RGBA')).astype(np.float32)
        hsv = np.asarray(im.convert('RGB').convert('HSV')).astype(np.float32)
        h = hsv[..., 0] * 360.0 / 255.0
        s = hsv[..., 1] / 255.0
        v = hsv[..., 2] / 255.0
        sel = ((h >= cls.hue_lo) & (h <= cls.hue_hi) & (s > 0.40) & (v > 0.30)).astype(np.float32)
        t = np.clip((v - 0.30) / 0.70, 0, 1)[..., None]
        lo, hi = np.array(cls.lo, np.float32), np.array(cls.hi, np.float32)
        col = lo * (1 - t) + hi * t
        rgba[..., :3] = rgba[..., :3] * (1 - sel[..., None]) + col * sel[..., None]
        return Image.fromarray(np.clip(rgba, 0, 255).astype(np.uint8), 'RGBA')
