"""W1 close: a short or sparse link street that fits no layer retries with its leg extension scaled (`extend_retry`)."""
from netrun_art.derive import street as S


def _row(i, x0):
    return dict(bid="b%02d" % i, x0=x0, x1=x0 + 5.0, y0=2.0, y1=9.0, h=40.0, ts=1.0, axis=0)


def _world(xs):
    B = [_row(i, x) for i, x in enumerate(xs)]
    layers = [(l, [{"id": "n%d" % l, "index": 0, "layer": l}]) for l in range(1, 8)]
    return B, layers


def test_a_street_that_fits_is_never_changed():
    B, layers = _world([0, 8, 16, 24, 32, 40, 48])
    best, step = S.choose_street_fitting(B, [[0.0, 0.0], [10.0, 0.0]], layers, S.RULES)
    assert step == 0 and best[7]


def test_sparse_frontage_retries_with_a_longer_extension():
    B, layers = _world([0, 8, 16, 90, 98, 106, 114])      # 3 buildings inside the 12 / 60 BU extension, 4 more past it
    legs = [[0.0, 0.0], [10.0, 0.0]]
    first = S.choose_street(B, legs, layers, S.RULES)
    assert not first[7]
    best, step = S.choose_street_fitting(B, legs, layers, S.RULES)
    assert step >= 2 and best[7] and len(best[6]) == 7
    assert S.choose_street_fitting(B, legs, layers, S.RULES)[1] == step      # deterministic


def test_nothing_fits_keeps_the_first_result():
    B, layers = _world([0, 8])
    best, step = S.choose_street_fitting(B, [[0.0, 0.0], [10.0, 0.0]], layers, S.RULES)
    assert step == 0 and not best[7]
