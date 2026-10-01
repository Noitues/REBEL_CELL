"""Round 13: the glyph catalogue (what each glyph means, its family, help/hurt) + a 16 px confusion metric.

Real game names come from scripts/data/rc.gd (SliceType, Status) and docs/art_asset.md (E2, E3, E5).
"""
import numpy as np
from PIL import Image, ImageFilter
import slicelib as SL
import glyphs13 as G

PINK, CYAN, GREEN, VIOLET, LAV, GREY = (255, 61, 168), (92, 225, 255), (123, 224, 123), (200, 90, 255), (176, 140, 255), (106, 106, 106)
HURT, HELP, MIXED, NEUTRAL = (255, 77, 77), (92, 225, 255), (255, 190, 60), (200, 200, 215)
CORP_COL = {"meridian": (255, 140, 26), "halcyon": (140, 123, 255), "orbital": (127, 168, 255), "solace": (61, 255, 139)}

# (glyph id, label, meaning, colour, kind) ; kind: slice | special | placeholder | status | state | picto
PROGRAMS = [
    ("EXPLOIT", "EXPLOIT", "ATTACK: damage (dagger)", PINK, "slice"),
    ("ZERO-DAY", "ZERO-DAY", "CRIT: big damage (burst)", (255, 120, 215), "slice"),
    ("FIREWALL", "FIREWALL", "DEFEND: block (wall on fire)", CYAN, "slice"),
    ("SANDBOX", "SANDBOX", "SHIELD: shield (window in window)", (70, 226, 205), "slice"),
    ("PROXY", "PROXY", "EVADE: dodge next hit (chevrons)", GREEN, "slice"),
    ("PATCH", "PATCH", "HEAL: restore HP (bandage)", (170, 240, 110), "slice"),
    ("BIOHAZ", "VIRUS", "AFFLICT: status on target (biohazard)", VIOLET, "slice"),
    ("TROJAN", "TROJAN", "DEPLOY: dock drones (horse)", LAV, "slice"),
    ("NULL", "NULL", "MISS: nothing (slashed zero)", GREY, "slice"),
]
SPECIALS = [
    ("TARIFF", "TARIFF", "Meridian: drains RAM (receipt)", CORP_COL["meridian"], "special"),
    ("CITATION", "CITATION", "Halcyon: plants PARASITE (gavel)", CORP_COL["halcyon"], "special"),
    ("FLARE", "SOLAR FLARE", "Orbital: overclock then corrupt", CORP_COL["orbital"], "special"),
    ("DOSE", "DOSE", "Solace: corrupts (capsule)", CORP_COL["solace"], "special"),
    ("INERTIA", "INERTIA", "+1 resistance (anvil)", (255, 210, 90), "special"),
    ("DRONE", "DRONE", "satellite docked on a slice", LAV, "special"),
]
PLACEHOLDERS = [
    ("PHISHING", "PHISHING", "hook + bait mail", PINK, "placeholder"),
    ("SHIELD", "SHIELD", "heater shield", CYAN, "placeholder"),
    ("ENCRYPT", "ENCRYPT", "*** password field", CYAN, "placeholder"),
    ("RECON", "RECON", "magnifier: reveal/scout", GREEN, "placeholder"),
    ("BURN", "BURN", "flame: damage over time", (255, 120, 40), "placeholder"),
    ("BOMB", "BOMB", "delayed big hit", PINK, "placeholder"),
    ("SAFE", "VAULT", "steel door: heavy block", CYAN, "placeholder"),
    ("KEY", "KEY", "unlock / bypass", (255, 210, 90), "placeholder"),
    ("FINGERPRINT", "SPOOF", "fingerprint: identity", GREEN, "placeholder"),
    ("STORM", "STORM", "storm cloud: hits all", VIOLET, "placeholder"),
]
# statuses (rc.gd Status) + the two status actions; badge: circle = helps, diamond = hurts, notched = mixed
STATUSES = [
    ("ST_CORRUPTED", "CORRUPTED", "slice output broken (hurts)", HURT, "hurt"),
    ("ST_PARASITE", "PARASITE", "half output (hurts)", HURT, "hurt"),
    ("ST_OVERCLOCKED", "OVERCLOCKED", "1.5x once, then CORRUPTED", MIXED, "mixed"),
    ("ST_ENCRYPTED", "ENCRYPTED", "absorbs the next status", HELP, "help"),
    ("ST_CLEANSE", "CLEANSE", "removes CORRUPTED", HELP, "help"),
    ("ST_CORRUPTED", "PREDICTED", "dashed badge = will happen", HURT, "predicted"),
]
STATES = [
    ("ST_FROZEN", "FROZEN", "slice skips / is held", (150, 220, 255), "hurt"),
    ("ST_LOCKED", "LOCKED", "slice can't be changed", NEUTRAL, "neutral"),
    ("ST_BURNING", "BURNING", "loses value each turn", (255, 120, 40), "hurt"),
    ("ST_EMPOWERED", "EMPOWERED", "boosted next trigger", (255, 214, 64), "help"),
]
# card pictograms (art_asset E5): (glyph, label, meaning, number-or-None)
PICTOS = [
    ("PI_SPIN_CW", "SPIN", "spin n ticks clockwise", "9"),
    ("PI_SPIN_CCW", "SPIN CCW", "spin n anticlockwise", "5"),
    ("PI_SPIN_CW", "SPIN n+", "spin 2, 5 if spun", "2+"),
    ("PI_RESPIN", "RESPIN", "respin to random tick", None),
    ("PI_NUDGE", "NUDGE", "+-1 tick, x n", "x2"),
    ("PI_NUDGE_INNER", "NUDGE INNER", "+-1 inner ring", "x2"),
    ("PI_FREE", "FREE NUDGE", "next n nudges free", "2"),
    ("PI_AGAIN", "AGAIN", "nudges trigger twice", None),
    ("PI_FLIP", "FLIP", "mirror the wheel", None),
    ("PI_SNAP", "SNAP", "snap to slice centre", None),
    ("PI_RING_LOCK", "RING LOCK", "inner ring holds", None),
    ("PI_PERFECT", "PERFECT", "perfect mark (RAM+)", None),
    ("PI_DRAW", "DRAW", "draw n cards", "3"),
    ("PI_RAM", "RAM", "gain / lose RAM", "+2"),
    ("ST_FROZEN", "FREEZE", "target skips respin", None),
    ("INERTIA", "RESIST", "resistance +- n", "-2"),
    ("PI_BREACH", "BREACH", "disable the hub", "1"),
    ("PI_UNDOCK", "UNDOCK", "move a satellite", None),
    ("EXPLOIT", "DAMAGE", "deal n (= ATTACK)", "4"),
    ("PI_BLOCK", "BLOCK", "gain n block", "6"),
    ("SHIELD", "SHIELD pts", "gain n shield", "4"),
    ("PROXY", "EVADE", "evade next attack", None),
    ("PATCH", "HEAL", "heal n (= HEAL)", "6"),
    ("PI_ALL", "ALL TARGETS", "every enemy", None),
    ("PI_SELF_DMG", "TAKE DMG", "you take n", "3"),
    ("PI_EXHAUST", "EXHAUST", "card is destroyed", None),
    ("PI_RETICLE", "TARGET", "aim reticle", None),
    ("PI_REFUSAL", "NO DAMAGE", "refused / blocked", None),
    ("PI_HP", "HP", "health", None),
]

# before -> after fixes (old shape rendered with glyphs13.BYPASS)
FIXES = [
    ("FLARE", "ZERO-DAY", "Old SOLAR FLARE (rayed disc) = ZERO-DAY burst by eye (both radial; IoU is blind to it)", "horizon sun: flat base, rays on top only"),
    ("FIREWALL", "SHIELD", "Old FIREWALL (shield + bricks) = SHIELD outline", "FIREWALL is a wall with flames; shields are shields"),
    ("NULL", "PI_REFUSAL", "Old NULL (round slashed 0) = no-entry REFUSAL", "NULL is a tall narrow 0; refusal stays round"),
    ("CITATION", "TARIFF", "Old CITATION (ticket) = TARIFF receipt: two tall paper slips", "CITATION is a gavel on its block"),
]


def m16(name, px=16):
    """The glyph's coverage at px (box filter), lightly blurred: what the eye gets at that size."""
    m = SL.glyph_mask(name).resize((px, px), Image.BOX)
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    return np.asarray(m, np.float32) / 255.0


def similarity(a, b):
    """Soft IoU of two 16 px coverage maps (1 = identical blobs)."""
    return float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum()))


def all_ids():
    ids = []
    for lst in (PROGRAMS, SPECIALS, PLACEHOLDERS, STATUSES, STATES):
        for g in lst:
            if g[0] not in ids:
                ids.append(g[0])
    for g in PICTOS:
        if g[0] not in ids:
            ids.append(g[0])
    return ids


def top_pairs(ids, n=10, shared=()):
    """Most alike pairs at 16 px (pairs that are the same concept on purpose are skipped)."""
    maps = {i: m16(i) for i in ids}
    out = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            if (a, b) in shared or (b, a) in shared:
                continue
            out.append((similarity(maps[a], maps[b]), a, b))
    out.sort(reverse=True)
    return out[:n]


SHARED = {("ST_BURNING", "BURN"), ("ST_ENCRYPTED", "ENCRYPT"), ("PI_HP", "PI_SELF_DMG")}
