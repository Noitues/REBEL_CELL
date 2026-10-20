class_name CityA2Hqs
extends RefCounted
## LOOK L5 (designer 2026-10-20, whole-city plate parity): the two A2 HQs that are no game corporation's, built as
## landmark meshes for the whole-city pose: Aurelian's Circus Aurelius (an oval colosseum: three arcaded tiers and an
## attic round a stepped bowl and its sand) and Tethys's Floating Pier City (a white dome and its satellites on a round
## deck in the bay, radial piers, a mast). Surfaces carry 5b's landmark material names (lm_toon / lm_win / lm_neon), so
## LandmarkMaterials styles them like the glTF HQs (day / night). Sizes from CityConfig.a2_hq_look. View-side only.

## The material names LandmarkMaterials maps to its roles.
const TOON := "lm_toon"
const WIN := "lm_win"
const NEON := "lm_neon"


## The landmark node of A2 HQ style `style` ("colosseum_circus" or "pier_city"), `radius` BU, local y up at its base;
## null for another style.
static func make(cfg: CityConfig, style: String, radius: float) -> Node3D:
	var b := _Build.new()
	var look: Dictionary = cfg.a2_hq_look.get(style, {})
	match style:
		"colosseum_circus":
			_colosseum(b, look, radius)
		"pier_city":
			_pier_city(b, look, radius)
		_:
			return null
	var root := Node3D.new()
	var mi := MeshInstance3D.new()
	mi.name = "Body"
	mi.mesh = b.commit()
	root.add_child(mi)
	return root


static func _col(look: Dictionary, key: String, fallback: Color) -> Color:
	return look.get(key, fallback)


static func _colosseum(b: _Build, look: Dictionary, radius: float) -> void:
	var a := radius
	var e := float(look.get("aspect", 0.8))
	var tiers := int(look.get("tiers", 3))
	var th := float(look.get("tier_h", 3.0))
	var n := int(look.get("bays", 56))
	var stone := _col(look, "stone", Color(0.86, 0.80, 0.68))
	var shade := _col(look, "stone_dark", Color(0.62, 0.56, 0.48))
	var lamp := _col(look, "arch", Color(1.0, 0.78, 0.45))
	var gold := _col(look, "rim", Color(1.0, 0.82, 0.5))
	var sand := _col(look, "sand", Color(0.80, 0.70, 0.52))
	var wall := float(look.get("wall", 0.09)) * a
	var top := th * tiers
	var attic := th * 0.5
	# The outer wall: its face, the inner face and the top, in tiers; each tier's arches lit a hair outside the face.
	for t in tiers:
		var y0 := th * t
		b.band(a, e, y0, y0 + th, n, TOON, stone if t % 2 == 0 else stone * 0.96, 1.0)
		b.band(a - wall, e, y0, y0 + th, n, TOON, shade, -1.0)
		b.band(a * 1.004, e, y0 + th * 0.86, y0 + th, n, TOON, shade, 1.0)  # the cornice line
		for k in n:
			var u0 := (float(k) + 0.22) / n
			var u1 := (float(k) + 0.78) / n
			b.arch(a * 1.002, e, u0, u1, y0 + th * 0.12, y0 + th * 0.74, WIN, lamp)
	b.band(a, e, top, top + attic, n, TOON, stone, 1.0)
	b.band(a - wall, e, top, top + attic, n, TOON, shade, -1.0)
	b.ring_flat(a - wall, a, e, top + attic, n, TOON, shade)
	b.band(a * 1.006, e, top + attic * 0.75, top + attic, n, NEON, gold, 1.0)
	# The bowl: steps from the attic down to the arena, light and dark rows.
	var steps := int(look.get("steps", 7))
	var r_in := float(look.get("arena", 0.42)) * a
	for s in steps:
		var f0 := float(s) / steps
		var f1 := float(s + 1) / steps
		var ra := lerpf(a - wall, r_in, f0)
		var rb := lerpf(a - wall, r_in, f1)
		var ya := lerpf(top, th * 0.35, f0)
		var yb := lerpf(top, th * 0.35, f1)
		b.ring_flat(rb, ra, e, ya, n, TOON, stone * (1.0 if s % 2 == 0 else 0.82))
		b.band(rb, e, yb, ya, n, TOON, shade, 1.0)
	b.disc(r_in, e, th * 0.35, n, TOON, sand)
	# The night bowl's glow: a lamp ring round the arena.
	b.band(r_in * 1.01, e, th * 0.35, th * 0.5, n, NEON, lamp, 1.0)


static func _pier_city(b: _Build, look: Dictionary, radius: float) -> void:
	var white := _col(look, "white", Color(0.92, 0.94, 0.96))
	var deck := _col(look, "deck", Color(0.70, 0.72, 0.74))
	var cyan := _col(look, "neon", Color(0.35, 0.9, 1.0))
	var lamp := _col(look, "win", Color(0.75, 0.95, 1.0))
	var r0 := float(look.get("deck_k", 0.26)) * radius
	var dh := float(look.get("deck_h", 1.2))
	var n := 64
	b.disc(r0, 1.0, dh, n, TOON, deck)
	b.band(r0, 1.0, -1.0, dh, n, TOON, deck * 0.7, 1.0)
	b.band(r0 * 1.005, 1.0, dh * 0.6, dh, n, NEON, cyan, 1.0)
	# The main dome (ribbed: lit meridians by night) and a ring of windows at its foot.
	var rd := float(look.get("dome_k", 0.14)) * radius
	var hd := rd * float(look.get("dome_h", 0.85))
	b.dome(Vector3(0.0, dh, 0.0), rd, hd, 40, 10, TOON, white)
	b.band(rd * 1.01, 1.0, dh, dh + hd * 0.12, 40, WIN, lamp, 1.0)
	for k in 12:
		b.rib(Vector3(0.0, dh, 0.0), rd * 1.008, hd * 1.008, TAU * k / 12.0, 10, 0.012 * TAU, NEON, cyan)
	# Satellites round it.
	var sat := int(look.get("satellites", 6))
	var rs := rd * 0.38
	for k in sat:
		var an := TAU * (k + 0.5) / sat
		var c := Vector3(cos(an), 0.0, sin(an)) * (rd + rs * 1.6)
		b.dome(c + Vector3(0.0, dh, 0.0), rs, rs * 0.9, 20, 6, TOON, white * 0.97)
		b.band_at(c, rs * 1.02, dh, dh + rs * 0.15, 20, WIN, lamp)
	# Radial piers to moorings, each with a lamp line.
	var piers := int(look.get("piers", 8))
	var pl := float(look.get("pier_k", 0.42)) * radius
	var pw := float(look.get("pier_w", 2.0))
	for k in piers:
		var an := TAU * k / piers + 0.2
		var d := Vector3(cos(an), 0.0, sin(an))
		var s := Vector3(-d.z, 0.0, d.x)
		var p0 := d * r0 * 0.98
		var p1 := d * (r0 + pl)
		b.box_between(p0, p1, s, pw, 0.0, dh * 0.7, TOON, deck)
		b.box_between(p0 + Vector3(0.0, dh * 0.7, 0.0), p1 + Vector3(0.0, dh * 0.7, 0.0), s, pw * 0.25, 0.0, 0.25, NEON, cyan)
		b.box_between(p1 - d * 2.5 + s * 2.5, p1 + s * 2.5, d, 3.0, 0.0, 2.5, TOON, white * 0.9)  # a pier-head hall
	# The mast with its lamp.
	var mh := float(look.get("mast_h", 2.6)) * hd
	b.box_between(Vector3(0.0, dh + hd * 0.9, 0.0), Vector3(0.0, dh + mh, 0.0), Vector3.RIGHT, 0.7, 0.0, 0.0, TOON, white, true)
	b.box_between(Vector3(0.0, dh + mh, 0.0), Vector3(0.0, dh + mh + 1.6, 0.0), Vector3.RIGHT, 1.1, 0.0, 0.0, NEON, cyan, true)


## One SurfaceTool per material name.
class _Build:
	var tools: Dictionary = {}

	func _st(mat: String) -> SurfaceTool:
		if not tools.has(mat):
			var st := SurfaceTool.new()
			st.begin(Mesh.PRIMITIVE_TRIANGLES)
			tools[mat] = st
		return tools[mat]

	func tri(mat: String, a: Vector3, b: Vector3, c: Vector3, col: Color) -> void:
		var st := _st(mat)
		for p: Vector3 in [a, b, c]:
			st.set_color(Color(col.r, col.g, col.b, 0.8))
			st.add_vertex(p)

	func quad(mat: String, a: Vector3, b: Vector3, c: Vector3, d: Vector3, col: Color) -> void:
		tri(mat, a, b, c, col)
		tri(mat, a, c, d, col)

	static func _ell(r: float, e: float, u: float) -> Vector3:
		return Vector3(cos(u * TAU) * r, 0.0, sin(u * TAU) * r * e)

	## A vertical band round an ellipse (radius `r`, aspect `e`) from y0 to y1 (`face` 1 outward, -1 inward: the shader
	## turns its normals to the camera, so the sign only sets the winding).
	func band(r: float, e: float, y0: float, y1: float, n: int, mat: String, col: Color, face: float) -> void:
		for k in n:
			var a := _ell(r, e, float(k) / n)
			var c := _ell(r, e, float(k + 1) / n)
			if face < 0.0:
				var t := a
				a = c
				c = t
			quad(mat, a + Vector3(0, y0, 0), c + Vector3(0, y0, 0), c + Vector3(0, y1, 0), a + Vector3(0, y1, 0), col)

	## A band round a circle of radius `r` about `c`.
	func band_at(c: Vector3, r: float, y0: float, y1: float, n: int, mat: String, col: Color) -> void:
		for k in n:
			var a := c + _ell(r, 1.0, float(k) / n)
			var d := c + _ell(r, 1.0, float(k + 1) / n)
			quad(mat, a + Vector3(0, y0, 0), d + Vector3(0, y0, 0), d + Vector3(0, y1, 0), a + Vector3(0, y1, 0), col)

	## A flat ring between radii r0 < r1 at height y.
	func ring_flat(r0: float, r1: float, e: float, y: float, n: int, mat: String, col: Color) -> void:
		for k in n:
			var u0 := float(k) / n
			var u1 := float(k + 1) / n
			var up := Vector3(0, y, 0)
			quad(mat, _ell(r0, e, u0) + up, _ell(r1, e, u0) + up, _ell(r1, e, u1) + up, _ell(r0, e, u1) + up, col)

	func disc(r: float, e: float, y: float, n: int, mat: String, col: Color) -> void:
		var c := Vector3(0, y, 0)
		for k in n:
			tri(mat, c, _ell(r, e, float(k) / n) + c, _ell(r, e, float(k + 1) / n) + c, col)

	## An arch opening on the ellipse wall: a quad u0..u1 from y0 to y1 with a round head (a fan of 6).
	func arch(r: float, e: float, u0: float, u1: float, y0: float, y1: float, mat: String, col: Color) -> void:
		var a := _ell(r, e, u0)
		var d := _ell(r, e, u1)
		var w := (d - a).length() * 0.5
		var spring := y1 - w
		quad(mat, a + Vector3(0, y0, 0), d + Vector3(0, y0, 0), d + Vector3(0, spring, 0), a + Vector3(0, spring, 0), col)
		var mid := (a + d) * 0.5 + Vector3(0, spring, 0)
		for k in 6:
			var t0 := PI * k / 6.0
			var t1 := PI * (k + 1) / 6.0
			var p0 := mid + (a - d).normalized() * w * cos(t0) + Vector3(0, w * sin(t0), 0)
			var p1 := mid + (a - d).normalized() * w * cos(t1) + Vector3(0, w * sin(t1), 0)
			tri(mat, mid, p0, p1, col)

	## A dome (ellipsoid cap) at `c`, radius `r`, height `h`.
	func dome(c: Vector3, r: float, h: float, n: int, rings: int, mat: String, col: Color) -> void:
		for j in rings:
			var t0 := PI * 0.5 * j / rings
			var t1 := PI * 0.5 * (j + 1) / rings
			for k in n:
				var u0 := TAU * k / n
				var u1 := TAU * (k + 1) / n
				var p00 := c + Vector3(cos(u0) * cos(t0) * r, sin(t0) * h, sin(u0) * cos(t0) * r)
				var p10 := c + Vector3(cos(u1) * cos(t0) * r, sin(t0) * h, sin(u1) * cos(t0) * r)
				var p01 := c + Vector3(cos(u0) * cos(t1) * r, sin(t1) * h, sin(u0) * cos(t1) * r)
				var p11 := c + Vector3(cos(u1) * cos(t1) * r, sin(t1) * h, sin(u1) * cos(t1) * r)
				quad(mat, p00, p10, p11, p01, col.lerp(Color.WHITE, 0.08 * j / rings))

	## A lit meridian on a dome: a thin strip at azimuth `an`, `half` radians wide.
	func rib(c: Vector3, r: float, h: float, an: float, rings: int, half: float, mat: String, col: Color) -> void:
		for j in rings:
			var t0 := PI * 0.5 * j / rings
			var t1 := PI * 0.5 * (j + 1) / rings
			var pts: Array[Vector3] = []
			for t: float in [t0, t1]:
				for u: float in [an - half, an + half]:
					pts.append(c + Vector3(cos(u) * cos(t) * r, sin(t) * h, sin(u) * cos(t) * r))
			quad(mat, pts[0], pts[1], pts[3], pts[2], col)

	## A box from p0 to p1 (its axis), `w` wide along `side`, from y0 to y1 over them (`vertical`: p0..p1 is the height
	## and the box is w x w).
	func box_between(p0: Vector3, p1: Vector3, side: Vector3, w: float, y0: float, y1: float, mat: String, col: Color,
			vertical: bool = false) -> void:
		var s := side.normalized() * w * 0.5
		var lo0: Vector3
		var lo1: Vector3
		var hi_y: Vector3
		var t := Vector3(-s.z, 0.0, s.x) if vertical else Vector3.ZERO
		if vertical:
			lo0 = p0
			lo1 = p0
			hi_y = p1 - p0
		else:
			lo0 = p0 + Vector3(0, y0, 0)
			lo1 = p1 + Vector3(0, y0, 0)
			hi_y = Vector3(0, y1 - y0, 0)
		var c: Array[Vector3]
		if vertical:
			c = [lo0 - s - t, lo0 + s - t, lo0 + s + t, lo0 - s + t]
		else:
			c = [lo0 - s, lo1 - s, lo1 + s, lo0 + s]
		for k in 4:
			var a := c[k]
			var d := c[(k + 1) % 4]
			quad(mat, a, d, d + hi_y, a + hi_y, col)
		quad(mat, c[0] + hi_y, c[1] + hi_y, c[2] + hi_y, c[3] + hi_y, col)

	func commit() -> ArrayMesh:
		var mesh := ArrayMesh.new()
		var names: Array = tools.keys()
		names.sort()
		for nm: String in names:
			var st: SurfaceTool = tools[nm]
			st.generate_normals()
			st.commit(mesh)
			var m := StandardMaterial3D.new()
			m.resource_name = nm
			mesh.surface_set_material(mesh.get_surface_count() - 1, m)
		return mesh
