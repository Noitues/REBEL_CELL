"""Street round 2 (exec'd inside r2_scene.py after the city buildings): builds the facade props of the plan (props.facade).

Only builds what r2_facade.make_props placed: AC units, pipes, awnings, small lit signs, lit rooms, on the building's street
face (class 2 in the index pass). Solid parts go to the city / panel accumulators, lit parts to the neon / window ones.
"""
_PAX = PLAN["axis"]


def _pp(pr, u, d, z):
    return (u, pr["face"] + pr["out"] * d, z) if _PAX == 0 else (pr["face"] + pr["out"] * d, u, z)


def _quad(acc, pr, u0, u1, z0, z1, d, col, bid, fj=0.5):
    acc.face([_pp(pr, u0, d, z0), _pp(pr, u1, d, z0), _pp(pr, u1, d, z1), _pp(pr, u0, d, z1)], col, bid, fj=fj)


def _pbox(acc, pr, u0, u1, z0, z1, d0, d1, col, bid):
    _quad(acc, pr, u0, u1, z0, z1, d1, col, bid)
    acc.face([_pp(pr, u0, d0, z1), _pp(pr, u1, d0, z1), _pp(pr, u1, d1, z1), _pp(pr, u0, d1, z1)], tuple(min(1, v * 1.1) for v in col), bid)
    acc.face([_pp(pr, u0, d1, z0), _pp(pr, u1, d1, z0), _pp(pr, u1, d0, z0), _pp(pr, u0, d0, z0)], tuple(v * 0.6 for v in col), bid)
    for (ua, ub) in ((u0, u0), (u1, u1)):
        acc.face([_pp(pr, ua, d0, z0), _pp(pr, ua, d1, z0), _pp(pr, ua, d1, z1), _pp(pr, ua, d0, z1)], tuple(v * 0.8 for v in col), bid)


for _pr in PLAN.get("props", []):
    _bid = rid()
    _k = _pr["kind"]
    _c = tuple(_pr["col"])
    if _k == "ac":
        _pbox(CPANEL, _pr, _pr["u0"], _pr["u1"], _pr["z0"], _pr["z1"], 0.0, _pr["depth"], _c, _bid)
        _w = _pr["u1"] - _pr["u0"]
        for _i in range(3):                                   # grille slats on the front
            _zz = _pr["z0"] + (_pr["z1"] - _pr["z0"]) * (0.25 + 0.25 * _i)
            _quad(CPANEL, _pr, _pr["u0"] + 0.08, _pr["u1"] - 0.08, _zz, _zz + 0.04, _pr["depth"] + 0.015, (0.08, 0.08, 0.1), _bid)
        if _pr.get("led"):
            _quad(CNEON, _pr, _pr["u1"] - 0.2, _pr["u1"] - 0.1, _pr["z1"] - 0.14, _pr["z1"] - 0.06, _pr["depth"] + 0.02, tuple(_pr["ledcol"]), (0, 0, 0))
    elif _k == "pipe":
        _u = (_pr["u0"] + _pr["u1"]) / 2
        beam(_pp(_pr, _u, 0.12, _pr["z0"]), _pp(_pr, _u, 0.12, _pr["z1"]), 0.16, _c, acc=CPANEL)
        for _zz in (_pr["z0"] + 0.6, (_pr["z0"] + _pr["z1"]) / 2, _pr["z1"] - 0.6):
            beam(_pp(_pr, _u, 0.0, _zz), _pp(_pr, _u, 0.14, _zz), 0.22, (0.12, 0.12, 0.15), acc=CPANEL)
        if _pr.get("elbow"):
            _du = 0.9 if (_u - _pr["u0"]) < 0.5 * (_pr["u1"] - _pr["u0"]) + 0.5 else -0.9
            beam(_pp(_pr, _u, 0.12, _pr["z1"]), _pp(_pr, _u + _du, 0.12, _pr["z1"]), 0.16, _c, acc=CPANEL)
    elif _k == "awning":
        _dp = _pr["depth"]
        _col = tuple(_pr["col"])
        CITY.face([_pp(_pr, _pr["u0"], 0.0, _pr["z1"]), _pp(_pr, _pr["u1"], 0.0, _pr["z1"]), _pp(_pr, _pr["u1"], _dp, _pr["z0"]), _pp(_pr, _pr["u0"], _dp, _pr["z0"])],
                  _col, _bid)
        for _ua in (_pr["u0"], _pr["u1"]):                    # side flaps
            CITY.face([_pp(_pr, _ua, 0.0, _pr["z1"]), _pp(_pr, _ua, 0.0, _pr["z0"] - 0.1), _pp(_pr, _ua, _dp, _pr["z0"]), _pp(_pr, _ua, _dp, _pr["z0"])],
                      tuple(v * 0.7 for v in _col), _bid)
        if _pr.get("trim"):
            beam(_pp(_pr, _pr["u0"], _dp + 0.02, _pr["z0"] - 0.02), _pp(_pr, _pr["u1"], _dp + 0.02, _pr["z0"] - 0.02), 0.07, tuple(_pr["trimcol"]), acc=CNEON)
    elif _k == "small_sign":
        _dd = _pr["depth"]
        _pbox(CPANEL, _pr, _pr["u0"], _pr["u1"], _pr["z0"], _pr["z1"], 0.0, 0.07, (0.08, 0.08, 0.1), _bid)
        _fc = tuple(min(1.0, v * 1.3) for v in _c)
        _quad(CNEON, _pr, _pr["u0"] + 0.04, _pr["u1"] - 0.04, _pr["z0"] + 0.04, _pr["z1"] - 0.04, 0.085, _fc, (0, 0, 0))
        _h = _pr["z1"] - _pr["z0"]
        _w = _pr["u1"] - _pr["u0"]
        for _b in range(_pr["bars"]):                         # dark glyph bars, so the board reads as text
            if _pr.get("blade"):
                _zz = _pr["z1"] - 0.14 - _b * _h / (_pr["bars"] + 1) - 0.05
                _quad(CPANEL, _pr, _pr["u0"] + 0.07, _pr["u1"] - 0.07, _zz, _zz + 0.1, 0.095, (0.04, 0.04, 0.05), _bid)
            else:
                _uu = _pr["u0"] + 0.08 + _b * (_w - 0.16) / _pr["bars"]
                _quad(CPANEL, _pr, _uu, _uu + (_w - 0.16) / _pr["bars"] * 0.55, _pr["z0"] + _h * 0.28, _pr["z1"] - _h * 0.28, 0.095, (0.04, 0.04, 0.05), _bid)
    elif _k == "lit_room":
        _quad(CWIN, _pr, _pr["u0"], _pr["u1"], _pr["z0"], _pr["z1"], 0.04, _c, (0, 0, 0))
        if _pr.get("mull"):
            _um = (_pr["u0"] + _pr["u1"]) / 2
            _quad(CPANEL, _pr, _um - 0.03, _um + 0.03, _pr["z0"], _pr["z1"], 0.055, (0.06, 0.06, 0.08), _bid)
            _zm = (_pr["z0"] + _pr["z1"]) / 2
            _quad(CPANEL, _pr, _pr["u0"], _pr["u1"], _zm - 0.025, _zm + 0.025, 0.055, (0.06, 0.06, 0.08), _bid)
print("R2 props", len(PLAN.get("props", [])), flush=True)
