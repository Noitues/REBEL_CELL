p = 'D:/rc_scratch/combat_redesign/locked/fx_o30/src/o30_seq.py'
s = open(p, encoding='utf-8').read()
a = """        m = (d > 14) & ~E.pinkish(P3) & (RHO > R1[0]) & (RHO < R1[1])"""
b = """        m = (d > 14) & ~E.pinkish(P3) & (RHO > R1[0]) & (RHO < R1[1]) & ring1_span_mask()"""
assert a in s; s = s.replace(a, b)
a = """def ua_ring1():"""
b = """ANG = np.degrees(np.arctan2(XX - FL.C[0], -(YY - FL.C[1]))) % 360


def ring1_cells():
    \"\"\"ring +1 unit cells of the state (f2, dep 1): (a0, a1) degrees; cell = sector s .. s + w, centred on the sector axis\"\"\"
    J = json.load(open(O30 + 'state_e10.json'))
    return [(60 * u['s'] - 30, 60 * (u['s'] + u['w']) - 30) for u in J['f2']['units'] if u['dep'] == 1]


def ring1_span_mask(pad=2.0):
    m = np.zeros(ANG.shape, bool)
    for a0, a1 in ring1_cells():
        m |= ((ANG - (a0 - pad)) % 360) <= (a1 - a0 + 2 * pad)
    return m


def ua_ring1():"""
assert a in s; s = s.replace(a, b, 1)
a = """def ring1_units():
    \"\"\"angular centres of the ring +1 unit cells on p3 (from the unit layer)\"\"\""""
b = """def ring1_units():
    \"\"\"angular centres of the ring +1 unit cells (state f2, dep 1)\"\"\"
    return [((a0 + a1) / 2.0) % 360 for a0, a1 in ring1_cells()]


def ring1_units_px():
    \"\"\"angular centres of the ring +1 unit cells on p3 (from the unit layer)\"\"\""""
assert a in s; s = s.replace(a, b)
# arrow: cell leading edge = centre - 0 ... use the stand-alone rule: arrow from the cell centre's sector start, one sector long
s = s.replace("        c0 = cpost - 60.0 - 26.0          # arrow from the cell's leading edge, one sector long (as fx_twist)",
              "        c0 = cpost - 60.0                 # one sector long, from the old centre to the new one (fx_twist draws c0 + 4 .. c0 + 60)")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
