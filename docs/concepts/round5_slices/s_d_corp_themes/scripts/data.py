"""Slice lists (type, ticks, value) for every wheel and sheet row.  Each wheel sums to 30 ticks."""

WHEELS = {
    "meridian": dict(name="COLLECTIONS\nAGENT", corp="Meridian Freight", hp=(40, 40), slices=[
        ("ATTACK", 3, 6), ("EVADE", 3, 3), ("DEFEND", 3, 6), ("ATTACK", 2, 8), ("DEPLOY", 5, 2),
        ("MISS", 3, None), ("ATTACK", 3, 6), ("SHIELD", 3, 4), ("CRITICAL", 2, 14), ("DEFEND", 3, 5)]),
    "solace": dict(name="TRIAGE\nUNIT", corp="Solace Biosystems", hp=(34, 36), slices=[
        ("ATTACK", 3, 5), ("HEAL", 3, 6), ("AFFLICT", 3, 3), ("SHIELD", 2, 4), ("ATTACK", 3, 5),
        ("MISS", 3, None), ("HEAL", 5, 4), ("AFFLICT", 2, 2), ("DEFEND", 3, 5), ("CRITICAL", 3, 11)]),
    "orbital": dict(name="UPLINK\nWARDEN", corp="Orbital Commons", hp=(45, 45), slices=[
        ("ATTACK", 3, 6), ("DEFEND", 3, 5), ("EVADE", 2, 4), ("CRITICAL", 3, 14), ("MISS", 3, None),
        ("ATTACK", 3, 7), ("EVADE", 5, 3), ("SHIELD", 3, 5), ("ATTACK", 2, 9), ("DEFEND", 3, 6)]),
    "rebel": dict(name="DISPATCH\nECHO", corp="REBEL_CELL", hp=(52, 60), slices=[
        ("ATTACK", 3, 9), ("AFFLICT", 3, 5), ("CRITICAL", 2, 16), ("DEPLOY", 3, 3), ("MISS", 2, None),
        ("ATTACK", 5, 7), ("EVADE", 3, 4), ("AFFLICT", 2, 6), ("ATTACK", 3, 9), ("DEFEND", 4, 6)]),
    "halcyon_boss": dict(name="CIVIC\nOVERSEER", corp="Halcyon Civic  //  BOSS", hp=(81, 120), slices=[
        ("ATTACK", 3, 8), ("DEFEND", 3, 8), ("DEPLOY", 2, 3), ("ATTACK", 3, 8), ("SHIELD", 3, 6),
        ("CRITICAL", 2, 18), ("MISS", 2, None), ("ATTACK", 5, 10), ("DEFEND", 2, 5), ("AFFLICT", 3, 4),
        ("ATTACK", 2, 12)]),
    "halcyon": dict(name="PATROL\nCONTRACTOR", corp="Halcyon Civic", hp=(38, 38), slices=[
        ("ATTACK", 3, 7), ("DEFEND", 3, 8), ("SHIELD", 3, 5), ("ATTACK", 2, 7), ("DEPLOY", 5, 2),
        ("MISS", 3, None), ("ATTACK", 3, 7), ("DEFEND", 3, 6), ("CRITICAL", 2, 13), ("SHIELD", 3, 4)]),
    "player": dict(name="BREAKER", corp="Breaker Core", hp=(60, 60), slices=[
        ("CRITICAL", 2, 12), ("EVADE", 3, 4), ("ATTACK", 3, 9), ("AFFLICT", 3, 3), ("DEFEND", 3, 6),
        ("MISS", 3, None), ("ATTACK", 3, 8), ("SHIELD", 3, 5), ("ATTACK", 3, 9), ("HEAL", 4, 4)]),
}

# corp sheet rows: 5 programs (3-tick) + a 2-tick and a 5-tick variant
SHEET = [
    ("meridian", [("ATTACK", 6), ("DEFEND", 6), ("EVADE", 3), ("DEPLOY", 2), ("MISS", None)],
     ("ATTACK", 8), ("DEPLOY", 3)),
    ("solace", [("ATTACK", 5), ("HEAL", 6), ("SHIELD", 4), ("AFFLICT", 3), ("MISS", None)],
     ("HEAL", 3), ("AFFLICT", 4)),
    ("halcyon", [("ATTACK", 7), ("DEFEND", 8), ("SHIELD", 5), ("DEPLOY", 2), ("MISS", None)],
     ("DEFEND", 4), ("ATTACK", 10)),
    ("orbital", [("ATTACK", 6), ("CRITICAL", 14), ("EVADE", 4), ("DEFEND", 5), ("MISS", None)],
     ("CRITICAL", 18), ("EVADE", 3)),
    ("rebel", [("ATTACK", 9), ("CRITICAL", 16), ("AFFLICT", 5), ("DEPLOY", 3), ("MISS", None)],
     ("EVADE", 4), ("AFFLICT", 6)),
]

STILL_T = {"meridian": 0.30, "solace": 0.12, "halcyon": 0.35, "orbital": 0.45, "rebel": 0.0, "player": 0.3}
