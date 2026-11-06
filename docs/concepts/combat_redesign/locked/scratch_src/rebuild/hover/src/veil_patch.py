p = 'hv_plates.py'
s = open(p, encoding='utf-8').read()
s = s.replace("    veil = Z.veil_cells(f_live, {uid}, 0.6)\n", "    veil = veil_cells(f_live, {uid}, 0.6)\n")
anchor = "def pencil_cell(L, u, seed=1):"
s = s.replace(anchor, '''VEIL_INSET = 2.0          # px the origin veil keeps inside the cell edge: on the edge line its AA stair-steps read as a dot run


def veil_cells(f, ids, k=0.6):
    """hz_core.veil_cells, inset VEIL_INSET px from the cell outline (the board's own cell edge stays as drawn)"""
    L = L2()
    for u in f['units']:
        if u['id'] in ids and u['w'] < 6:
            HL.tint_poly(L, grow_poly(HL.cell_poly_unit(u), -VEIL_INSET), (8, 10, 20), 255 * k)
    return L.done()


''' + anchor, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok', s.count('veil_cells(f_live'))
