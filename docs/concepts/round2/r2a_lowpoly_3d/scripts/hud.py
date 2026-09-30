"""R2A LOW-POLY 3D: faceted UI pieces (plates, pips, buttons) built as chunky meshes."""
import math
import lp_lib as L


def plate(name, w, h, mat_face, mat_edge, depth=0.06, bevel=0.12, jit=0.0, seed=0, dome=0.02, coll=None,
          notch=True):
    """A chunky chamfered slab facing +Z (local XY), its face a low fan so it catches facets of light."""
    pb = L.PB()
    c = bevel
    if notch:
        pts = [(-w / 2 + c, -h / 2), (w / 2 - c * 2.2, -h / 2), (w / 2, -h / 2 + c * 2.2), (w / 2, h / 2 - c),
               (w / 2 - c, h / 2), (-w / 2 + c * 2.2, h / 2), (-w / 2, h / 2 - c * 2.2), (-w / 2, -h / 2 + c)]
    else:
        pts = [(-w / 2 + c, -h / 2), (w / 2 - c, -h / 2), (w / 2, -h / 2 + c), (w / 2, h / 2 - c),
               (w / 2 - c, h / 2), (-w / 2 + c, h / 2), (-w / 2, h / 2 - c), (-w / 2, -h / 2 + c)]
    # face: inset ring + raised centre -> chamfer facets like a cut gem
    ins = [(x * (1 - c / w * 1.6), y * (1 - c / h * 1.6)) for x, y in pts]
    bot = [pb.vert((x, y, -depth)) for x, y in pts]
    rim = [pb.vert((x, y, 0.0), jit) for x, y in pts]
    top = [pb.vert((x, y, depth * 0.6), jit) for x, y in ins]
    cen = pb.vert((0, 0, depth * 0.6 + dome), 0.0)
    n = len(pts)
    for i in range(n):
        a, b = i, (i + 1) % n
        pb.face([bot[a], bot[b], rim[b], rim[a]], 1)
        pb.face([rim[a], rim[b], top[b], top[a]], 1)
        pb.face([top[a], top[b], cen], 0)
    return pb.build(name, [mat_face, mat_edge], seed=seed, coll=coll, shadow=False)


def hexpip(name, r, mat_top, mat_side, depth=0.05, coll=None):
    pb = L.PB()
    pb.prism(L.ngon(6, r, rot=math.pi / 6), -depth, 0.0, 1, 1)
    pb.prism(L.ngon(6, r * 0.7, rot=math.pi / 6), 0.0, depth * 0.5, 0, 0, top_center_dz=depth * 0.4)
    # the skirt between the two
    return pb.build(name, [mat_top, mat_side], coll=coll, shadow=False)


def gem(name, r, mat_a, mat_b, n=6, h=None, coll=None, seed=0):
    """A faceted cut gem facing +Z: crown fan (two tones alternate) over a short girdle."""
    pb = L.PB()
    h = h if h is not None else r * 0.5
    outer = L.ngon(n, r, rot=math.pi / 2)
    inner = L.ngon(n, r * 0.55, rot=math.pi / 2 + math.pi / n)
    ob_ = [pb.vert((x, y, -h * 0.3)) for x, y in outer]
    ot = [pb.vert((x, y, 0.0)) for x, y in outer]
    it = [pb.vert((x, y, h * 0.6)) for x, y in inner]
    c = pb.vert((0, 0, h * 0.75))
    for i in range(n):
        a, b = i, (i + 1) % n
        pb.face([ob_[a], ob_[b], ot[b], ot[a]], 1)
        pb.face([ot[a], ot[b], it[a]], (i % 2))
        pb.face([ot[b], it[b], it[a]], 1 - (i % 2))
        pb.face([it[a], it[b], c], i % 2)
    return pb.build(name, [mat_a, mat_b], coll=coll, shadow=False, seed=seed)
