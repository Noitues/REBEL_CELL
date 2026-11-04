"""rb_tokens (2026-11-03 rebuild): the one table of colours and value targets the rebuild draws with and the checks test against.
No drawing code here (rb_patch draws, rb_checks measures).  Every number the AD review / REVIEW_RESPONSE / VISUAL_PLAN A.1 amendment set is here."""
import numpy as np


def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


_M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
_WP = np.array([0.95047, 1.0, 1.08883])


def lin(rgb):
    c = np.asarray(rgb, np.float64) / 255.0
    return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)


def lum(rgb):
    """relative luminance Y of sRGB (0-255), any shape [..., 3]"""
    c = lin(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def lstar(Y):
    Y = np.asarray(Y, np.float64)
    return np.where(Y > 216 / 24389, 116 * np.cbrt(Y) - 16, Y * 24389 / 27)


def y_of_lstar(L):
    L = np.asarray(L, np.float64)
    return np.where(L > 8, ((L + 16) / 116) ** 3, L * 27 / 24389)


def lab(rgb):
    c = lin(rgb)
    xyz = (c @ _M.T) / _WP
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def lab2rgb(L, a, b):
    fy = (L + 16) / 116
    f = np.array([fy + a / 500, fy, fy - b / 200])
    xyz = np.where(f ** 3 > 216 / 24389, f ** 3, (116 * f - 16) / (24389 / 27)) * _WP
    c = np.linalg.solve(_M, xyz)
    c = np.clip(c, 0, 1)
    c = np.where(c > 0.0031308, 1.055 * c ** (1 / 2.4) - 0.055, 12.92 * c)
    return tuple(int(round(v * 255)) for v in c)


def de76(a, b):
    return float(np.linalg.norm(lab(np.array(a, np.float64)) - lab(np.array(b, np.float64))))


# ------------------------------------------------------------------ meaning tokens (VISUAL_PLAN E)
# BOSS_GOLD re-picked 2026-11-03 (palette-collision check): #FFC428 sat at dE76 11.4 from CRT_AMBER (Heat) and 11.3 from RESIST_GOLD (stars),
# both on the same plate.  The boss keeps gold, one step deeper (brass): >= 15 from every token, SCHEDULE, PLAN and the card type plates.
BOSS_GOLD_OLD = hx('FFC428')
TOKENS = {
    'CELL_PINK': hx('FF3DA8'), 'HARM': hx('FF4433'), 'GAIN': hx('7BE07B'), 'SOAK': hx('3A7EF3'), 'PLAN': hx('FFE200'),
    'SCHEDULE': hx('FF8C1A'), 'BOSS_GOLD': hx('D69A1A'), 'NET_CYAN': hx('5CE1FF'), 'TRACE_VIOLET': hx('A03CFF'),
    'CRT_AMBER': hx('FFB000'), 'RESIST_GOLD': hx('FFD24D'), 'FOCUS': hx('D4FF00'),
}
BOSS_GOLD = TOKENS['BOSS_GOLD']
BOSS_GOLD_HI = (240, 190, 70)          # the gold edge highlight line (inside the edge, never a second hue)

# ------------------------------------------------------------------ the time grammar marks (T family)
HARM_UP = hx('FF6452')                 # HOT chevron fill (one value step over HARM, fix 2 of R51)
HOT_CORE = (255, 234, 224)             # HOT: the white-hot core stroke inside every HOT chevron / diamond (L9: live at this END TURN)
COLD_CHEV = hx('D9877C')
FAR_CHEV = hx('96767A')

# ------------------------------------------------------------------ the value targets (VISUAL_PLAN A.1, amended 2026-11-03)
CELL_OCC_L = (40.0, 45.0)              # occupied cell glass, ring NOW, mean L*
CELL_EMPTY_L = 28.0                    # empty cell (review figure); the gate is the luminance ratio below
CELL_RATIO_MIN = 3.0                   # occupied / empty mean luminance, per ring and per covered sector
RING_VAL = (1.0, 0.80, 0.62)           # time grammar: ring +1 / +2 glass value (R51)
CLOCK_L = (45.0, 55.0)                 # K clock material (tape, sweep, plates): median L*
SLICE_INK_L = (60.0, 72.0)             # tower slice inks, mean L* of the wedge ink
CAP_MIN_PX = 16.0                      # every text draw: cap height at 1080p
DE_MIN = 15.0                          # palette collision floor (CIE76)
ORDER_MARGIN = 1.0                     # L* by which each family must beat the next in the A.1 order
ROOM_MEAN_L = (28.0, 34.0)             # stage 2 (review 2.8 IMPL): the room behind the board, L* of its mean luminance (room region of rb_checks)
REVIEW_ROOM_BOX = (1200, 450, 1800, 800)   # the reviewer's measure.py probe 'room backdrop (right)' (reported)
REVIEW_CITY_BOX = (0, 200, 60, 900)        # ... and 'left city backdrop' (reported)

# ------------------------------------------------------------------ tower slice inks (DR-4 / DR-7: own colour + texture per slice type), value-capped to L* 60-72
# picked by rb_palette.py: >= 15 from the tokens that touch the tower (CELL_PINK halo, HARM / SOAK hatch, GAIN HP ring and pips, PLAN pencil, FOCUS brackets)
# 2026-11-04 (gate 1, check d): TURRET #D6A33A sat at dE76 9.6 from BOSS_GOLD, in the same sector as the Adjuster it shoots (the pair review 2.2
# named).  Check d now tests every slice ink against EVERY meaning token, the light neutrals and the other slice inks; TURRET moves off gold to
# an olive-chartreuse (gun-metal olive drab, L* 70.4), >= 30 from every token (gate2_fix/turret_pick2.py).  Its texture follows the hue.
SLICE_INK = {'BURST': hx('F06EAE'), 'SHIELD': hx('5E9BE0'), 'TURRET': hx('AEB24E'), 'REPAIR': hx('3FB59A')}
SLICE_TEX = {'BURST': hx('9E2A66'), 'SHIELD': hx('234E8C'), 'TURRET': hx('5A5E1A'), 'REPAIR': hx('1D6656')}
SLICE_INK_OLD = {'TURRET': hx('D6A33A')}
SLICE_NEIGHBOURS = ('CELL_PINK', 'HARM', 'SOAK', 'GAIN', 'PLAN', 'FOCUS')       # kept for reference; check d tests every token (TOKENS)
# the light neutrals that carry a family read (PAPER = the player's paper, ENAMEL = the enemy outline, TEXT_HI / TEXT_MID = HUD type):
# slice and skin inks must keep >= DE_MIN from them too (gate 1: Solace porcelain #E6EFE4 sat at dE 4.7 from PAPER)
NEUTRALS = {'PAPER': hx('F2EEE4'), 'ENAMEL': hx('D9E1EA'), 'TEXT_HI': hx('F2F6FF'), 'TEXT_MID': hx('AFC0D6')}

# ------------------------------------------------------------------ 2026-11-04 (gate 1, review 1.2 "HOT second under SEND IT"): every mark that is
# not a HOT T mark sits below the HOT marks, and every E and K mark sits below the tower.  Enemy HP ticks were CREAM #FFF4D6 (L* 96, above HOT);
# the sector digits and the ring tags were white / ENAMEL type (L* 96-100).  They keep their hue and drop to one type value, L* 84.
E_MARK_L = 84.0                        # E marks (HP ticks): L* of the fill
K_TYPE_L = 84.0                        # K type (sector digits, ring tags, ticket glyphs, W tags, tallies): L* of the ink
CREAM_HP = hx('DBD1B7')                # enemy HP tick: CREAM at L* 84
ENAMEL_E = hx('C4CBD3')                # 2026-11-04 (gate 1): tried for the bright 1 px ring lines and NOT installed (it did not reach them); kept for reference
                                       # (the lines read L* 95-100 at their 1 px peak after the LANCZOS downsample)
STEEL_HI_E = hx('C4CBD8')              # 2026-11-04 (gate 1): the armour rail's top edge (was #E2E9F6; it read L* 100 on the ring +1 tray)
CREAM_FADED = hx('FFF4D6')            # the ticks of hover-faded units (p2b, faded to DIM_K alpha): full CREAM, so the faded tick stays one segment
K_TYPE = hx('CBD2DB')                  # K type: ENAMEL at L* 84 (stamped digits, tag type, ticket glyphs)
HIT_PAPER = hx('DED8CA')               # 2026-11-04 (gate 1): the gun hit star fill (was WHITE, L* 100); L* 86, a P mark under the HOT marks
PLAN_BADGE_V = 0.86                    # 2026-11-04 (gate 1): the twist badge's PLAN yellow value (its outline edge read L* 97 at full PLAN)
MARK_MARGIN = 1.0                      # L* by which a mark's p95 sits under the tower, and its p99 under the HOT marks' p95

# ------------------------------------------------------------------ corp skin hue inks (DR-6 + ART_BIBLE 2.4 note): hue on rim, lip, crest, cell edges only
SKIN_INKS = {
    'neutral': {},
    # 2026-11-04 (gate 1): porcelain #E6EFE4 was dE 4.7 from PAPER (the player's paper) and 11.2 from ENAMEL; it is now a celadon glaze,
    # >= 17 from every token and light neutral (gate2_fix/pick.py)
    'solace': {'leaf': hx('96FF46'), 'leaf_deep': hx('4FA83A'), 'porcelain': hx('B8DCCC')},
    'meridian': {'rust': hx('B0602C'), 'rust_hi': hx('D88A4E'), 'barcode': hx('2A2A2E')},
}
SKIN_NEIGHBOURS = ('HARM', 'GAIN', 'FOCUS', 'SCHEDULE', 'BOSS_GOLD', 'PLAN', 'CELL_PINK', 'SOAK')
CELL_LIME = hx('D4FF00')               # Cell lime (= FOCUS hex); listed for the 2.4 note
# the neutral slate cell fill every skin uses (a low-chroma tint is allowed on top, max chroma below)
CELL_TINT_MAX_CHROMA = 8.0             # Lab chroma of the skin tint over the slate fill

# ------------------------------------------------------------------ card type plates sit next to these (REVIEW_RESPONSE 2.2)
CARD_NEIGHBOURS = ('SOAK', 'SCHEDULE', 'BOSS_GOLD', 'TRACE_VIOLET', 'NET_CYAN', 'CELL_PINK', 'PLAN', 'HARM')
