"""Round 14: the glyph catalogue (meanings, families, help/hurt), the old -> new change list, and the
16 px confusion metric.  Game names: scripts/data/rc.gd (SliceType, Status), docs/art_asset.md (E2/E3/E5).
"""
import numpy as np
from PIL import Image, ImageFilter
import slicelib as SL
import glyphs13 as G13
import glyphs14 as G

PINK, CYAN, GREEN, VIOLET, LAV, GREY = (255, 61, 168), (92, 225, 255), (123, 224, 123), (200, 90, 255), (176, 140, 255), (106, 106, 106)
HURT, HELP, MIXED, NEUTRAL = (255, 77, 77), (92, 225, 255), (255, 190, 60), (200, 200, 215)
CORP_COL = {"meridian": (255, 140, 26), "halcyon": (140, 123, 255), "orbital": (127, 168, 255), "solace": (61, 255, 139)}

# (glyph id, label, meaning, colour, kind) ; kind: slice | special | renamed | placeholder
PROGRAMS = [
    ("EXPLOIT", "EXPLOIT", "ATTACK: damage (dagger)", PINK, "slice"),
    ("ZERO-DAY", "ZERO-DAY", "CRIT: big damage (burst)", (255, 120, 215), "slice"),
    ("FIREWALL", "FIREWALL", "DEFEND: block (wall + flame)", CYAN, "slice"),
    ("SANDBOX", "SANDBOX", "SHIELD: persists, cap 15 (sandbox)", (70, 226, 205), "slice"),
    ("PROXY", "PROXY", "EVADE: dodge next hit (chevrons)", GREEN, "slice"),
    ("PATCH", "PATCH", "HEAL: restore HP (crossed band-aids)", (170, 240, 110), "slice"),
    ("BIOHAZ", "VIRUS", "AFFLICT: status on target", VIOLET, "slice"),
    ("TROJAN", "TROJAN", "DEPLOY: dock drones (horse)", LAV, "slice"),
    ("NULL", "NULL", "MISS: nothing (divide by zero)", GREY, "slice"),
]
SPECIALS = [
    ("JUDGEMENT", "JUDGEMENT", "Meridian: drains RAM (gavel); was TARIFF", CORP_COL["meridian"], "renamed"),
    ("CITATION", "CITATION", "Halcyon: plants PARASITE (receipt)", CORP_COL["halcyon"], "special"),
    ("FLARE", "SOLAR FLARE", "Orbital: overclock then corrupt", CORP_COL["orbital"], "special"),
    ("DOSE", "DOSE", "Solace: corrupts (capsule)", CORP_COL["solace"], "special"),
    ("WEIGHT", "WEIGHT", "+1 resistance; was INERTIA", (255, 210, 90), "renamed"),
    ("DRONE", "DRONE", "satellite docked on a slice", LAV, "special"),
]
PLACEHOLDERS = [
    ("PHISHING", "PHISHING", "hook + bait mail", PINK, "placeholder"),
    ("SHIELD", "SHIELD", "heraldic shield", CYAN, "placeholder"),
    ("ENCRYPT", "ENCRYPT", "*** password field", CYAN, "placeholder"),
    ("RECON", "RECON", "binoculars: scout", GREEN, "placeholder"),
    ("BURN", "BURN", "the shared 2-peak flame", (255, 120, 40), "placeholder"),
    ("BOMB", "BOMB", "delayed big hit", PINK, "placeholder"),
    ("SAFE", "VAULT", "steel door: heavy block", CYAN, "placeholder"),
    ("KEY", "KEY", "unlock / bypass", (255, 210, 90), "placeholder"),
    ("FINGERPRINT", "SPOOF", "whole fingerprint: identity", GREEN, "placeholder"),
    ("STORM", "STORM", "storm cloud: hits all", VIOLET, "placeholder"),
    ("ALT_F4", "KILL PROCESS", "ALT-F4 keycap", (255, 90, 90), "placeholder"),
]
STATUSES = [
    ("ST_CORRUPTED", "CORRUPTED", "slice output broken (hurts)", HURT, "hurt"),
    ("ST_PARASITE", "PARASITE", "half output (hurts)", HURT, "hurt"),
    ("ST_OVERCLOCKED", "OVERCLOCKED", "1.5x once, then CORRUPTED", MIXED, "mixed"),
    ("ST_ENCRYPTED", "ENCRYPTED", "absorbs the next status", HELP, "help"),
    ("ST_CLEANSE", "CLEANSE", "CTRL-ALT-DEL; one DEL key <= 48 px", HELP, "help"),
    ("ST_CORRUPTED", "PREDICTED", "dashed badge = will happen", HURT, "predicted"),
]
STATES = [
    ("ST_FROZEN", "FROZEN", "slice skips / is held", (150, 220, 255), "hurt"),
    ("ST_LOCKED", "LOCKED", "slice can't be changed", NEUTRAL, "neutral"),
    ("ST_BURNING", "BURNING", "loses value each turn", (255, 120, 40), "hurt"),
    ("ST_EMPOWERED", "EMPOWERED", "boosted next trigger", (255, 214, 64), "help"),
]
PICTOS = [
    ("PI_SPIN_CW", "SPIN", "spin n ticks clockwise", "9"),
    ("PI_SPIN_CCW", "SPIN CCW", "spin n anticlockwise", "5"),
    ("PI_MOMENTUM", "MOMENTUM", "spin 2; 5 if already spun", "2>5"),
    ("PI_RESPIN", "RESPIN", "respin to random tick", None),
    ("PI_NUDGE", "NUDGE", "free +-1 tick, either way", "x2"),
    ("PI_NUDGE_INNER", "NUDGE INNER", "+-1 on the inner ring", "x2"),
    ("PI_FREE", "FREE NUDGE", "next n nudges free", "2"),
    ("PI_AGAIN", "AGAIN", "nudges trigger twice", None),
    ("PI_FLIP", "FLIP", "mirror the wheel", None),
    ("PI_SNAP", "SNAP", "snap to slice centre", None),
    ("PI_RING_LOCK", "RING LOCK", "inner ring holds", None),
    ("PI_PERFECT", "PERFECT", "perfect mark (RAM+)", None),
    ("PI_DRAW", "DRAW", "draw n cards", "3"),
    ("PI_RAM", "RAM", "gain / lose RAM", "+2"),
    ("ST_FROZEN", "FREEZE", "target skips respin", None),
    ("WEIGHT", "RESIST", "resistance +- n", "-2"),
    ("PI_BREACH", "BREACH", "disable the hub", "1"),
    ("PI_UNDOCK", "UNDOCK", "move a satellite", None),
    ("EXPLOIT", "DAMAGE", "deal n (= ATTACK)", "4"),
    ("PI_BLOCK", "BLOCK", "gain n block", "6"),
    ("SHIELD", "SHIELD pts", "gain n shield", "4"),
    ("PROXY", "EVADE", "evade next attack", None),
    ("PATCH", "HEAL", "heal n (= PATCH)", "6"),
    ("PI_ALL", "ALL TARGETS", "every enemy", None),
    ("PI_SELF_DMG", "TAKE DMG", "you take n", "3"),
    ("PI_EXHAUST", "EXHAUST", "card torn in two", None),
    ("PI_RETICLE", "TARGET", "aim reticle", None),
    ("PI_REFUSAL", "NO DAMAGE", "refused / blocked", None),
    ("PI_HP", "HP", "health", None),
]

# old -> new for glyph_changes.png: (label, old ref, [options], note).  old ref: ("r13", id) or ("base", id)
CHANGES = [
    ("1 WEIGHT (was INERTIA)", ("r13", "INERTIA"), ["WEIGHT@A", "WEIGHT@B", "WEIGHT@C"], "renamed (game name change pending)"),
    ("2 SANDBOX", ("base", "SANDBOX"), ["SANDBOX@A", "SANDBOX@B", "SANDBOX@C"], "a kid's sandbox + shovel"),
    ("3 PATCH (= HEAL picto)", ("base", "PATCH"), ["PATCH"], "two crossed band-aids, one width"),
    ("4 SHIELD (placeholder)", ("r13", "SHIELD"), ["SHIELD@A", "SHIELD@B", "SHIELD@C"], "per pale / riot / double wall"),
    ("5 RECON", ("r13", "RECON"), ["RECON"], "binoculars"),
    ("6 NULL", ("r13", "NULL"), ["NULL@A", "NULL@B", "NULL@C", "NULL@D"], "slashed 0 vs divide by zero"),
    ("7 JUDGEMENT (was TARIFF)", ("base", "TARIFF"), ["JUDGEMENT"], "takes the gavel; renamed"),
    ("8 CITATION", ("r13", "CITATION"), ["CITATION"], "takes the old receipt"),
    ("9 SPOOF", ("r13", "FINGERPRINT"), ["FINGERPRINT"], "whole print"),
    ("10 CLEANSE", ("r13", "ST_CLEANSE"), ["ST_CLEANSE@A", "ST_CLEANSE@S", "ST_CLEANSE@B"], "row (DEL key small) / stack"),
    ("10b KILL PROCESS (new)", None, ["ALT_F4"], "placeholder ability"),
    ("11 EMPOWERED", ("r13", "ST_EMPOWERED"), ["ST_EMPOWERED@A", "ST_EMPOWERED@B", "ST_EMPOWERED@C"], "chevrons / bar break / star"),
    ("12 MOMENTUM (was SPIN n+)", ("r13", "PI_SPIN_CW"), ["PI_MOMENTUM@A", "PI_MOMENTUM@B", "PI_MOMENTUM@C"], "chain / double loop / steps"),
    ("13 NUDGE INNER", ("r13", "PI_NUDGE_INNER"), ["PI_NUDGE_INNER"], "bullseye, middle ring = +-1"),
    ("14 NUDGE", ("r13", "PI_NUDGE"), ["PI_NUDGE@A", "PI_NUDGE@B", "PI_NUDGE@C"], "short 2-headed arc, +-1"),
    ("15 UNDOCK", ("r13", "PI_UNDOCK"), ["PI_UNDOCK@A", "PI_UNDOCK@B"], "drone out / ball + socket"),
    ("16 BREACH", ("r13", "PI_BREACH"), ["PI_BREACH"], "bolt over a bullseye"),
    ("17 EXHAUST", ("r13", "PI_EXHAUST"), ["PI_EXHAUST"], "card torn in two, no fire"),
    ("18 BURN / BURNING", ("r13", "BURN"), ["BURN"], "the ONE 2-peak flame"),
    ("18 FIREWALL", ("r13", "FIREWALL"), ["FIREWALL"], "wall + the same flame"),
]


def old_mask(ref):
    src, name = ref
    if src == "r13":
        m = G13.mask(name)
        if m is not None:
            return m
    G.BYPASS.add(name)
    G13.BYPASS.add(name)
    try:
        return SL.glyph_mask(name)
    finally:
        G.BYPASS.discard(name)
        G13.BYPASS.discard(name)


def cov(mask, px=16):
    m = mask.resize((px, px), Image.BOX).filter(ImageFilter.GaussianBlur(0.6))
    return np.asarray(m, np.float32) / 255.0


def m16(name, px=16):
    """Coverage at px of the glyph actually shown at that size (small forms included)."""
    return cov(SL.glyph_mask(G.resolve(name, px)), px)


def similarity(a, b):
    """Soft IoU of two 16 px coverage maps (1 = identical blobs)."""
    return float(np.minimum(a, b).sum() / max(1e-6, np.maximum(a, b).sum()))


def all_ids():
    ids = []
    for lst in (PROGRAMS, SPECIALS, PLACEHOLDERS, STATUSES, STATES, PICTOS):
        for g in lst:
            if g[0] not in ids:
                ids.append(g[0])
    return ids


SHARED = {("ST_BURNING", "BURN"), ("ST_ENCRYPTED", "ENCRYPT"), ("PI_HP", "PI_SELF_DMG"), ("PI_SPIN_CW", "PI_SPIN_CCW")}


def top_pairs(ids, n=10, shared=SHARED):
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


def nearest(cov_map, ids, exclude=()):
    best = (0.0, "")
    for i in ids:
        if i in exclude:
            continue
        s = similarity(cov_map, m16(i))
        if s > best[0]:
            best = (s, i)
    return best
