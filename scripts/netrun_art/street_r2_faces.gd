class_name StreetR2Faces
extends RefCounted
## A recorder with the accumulator interface the street r2 facade kits draw into (twin of `kits.Faces`): face records for the cells, and
## primitive records for the roof pieces. Nothing is meshed here; the renderer (step 2) turns the records into geometry.

## Polygons: `{pts, col, bid, fj}` (fj null = the renderer draws the tone jitter).
var faces: Array = []
## Roof primitives: `["cyl36", cx, cy, z0, z1, rad, col]`, `["box", x0, y0, z0, x1, y1, z1, col]`, `["beam", p0, p1, w, col]`.
var prims: Array = []


## One polygon: points, colour, part id (an int or [0, 0, 0] for the lit parts), tone jitter.
func face(pts: Array, col: Array, bid: Variant, fj: Variant = null) -> void:
	var p: Array = []
	for q: Array in pts:
		p.append(q.duplicate())
	faces.append({"pts": p, "col": col.duplicate(), "bid": (bid as Array).duplicate() if bid is Array else bid, "fj": fj})


## A roof primitive record.
func prim(kind: String, args: Array) -> void:
	var rec: Array = [kind]
	for a: Variant in args:
		rec.append((a as Array).duplicate() if a is Array else a)
	prims.append(rec)
