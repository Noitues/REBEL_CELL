class_name PortraitArt
extends RefCounted
## Drawn portraits until final art lands (design review options). One subject model, four
## looks. A subject is {kind, key, tint, name}: kind is one of KINDS (an operative, a
## corporate agent, a machine or program, a boss, a corporation's face); key picks the
## deterministic details (hair, visor, lens, emblem); tint is the owner's colour.
## Styles (`style`, `--demo-portrait=N`): 0 NEON BUST, 1 XEROX ZINE, 2 WIRE SCAN,
## 3 MUGSHOT. View only; decoration hashes, not game randomness.

enum Kind { OPERATIVE, AGENT, MACHINE, BOSS, CORP }
const STYLE_NAMES: Array[String] = ["NEON BUST", "XEROX ZINE", "WIRE SCAN", "MUGSHOT"]
## Name words that mark an enemy as a machine or program rather than a person.
const MACHINE_WORDS: Array[String] = ["drone", "daemon", "core", "array", "mast", "relay", "station", "pad", "unit", "script",
	"process", "engine", "meter", "satellite", "scanner", "dispenser", "debris", "template", "swarm", "hauler", "optimizer", "control", "drop", "proxy", "board", "office", "authority", "manifest", "routing", "powers", "test"]

static var style: int = 0


## A subject for an enemy from its content (boss / machine / agent by name).
static func enemy_subject(id: StringName, display_name: String, corporation_id: StringName, is_boss: bool) -> Dictionary:
	var kind := Kind.AGENT
	# Whole words only ("officer" is a person, "office" would not be).
	var words := (display_name.to_lower() + " " + String(id).replace("_", " ")).split(" ", false)
	for w in MACHINE_WORDS:
		if words.has(w):
			kind = Kind.MACHINE
			break
	if is_boss:
		kind = Kind.BOSS
	return {"kind": kind, "key": String(id), "tint": Palette.corp_color(corporation_id), "name": display_name}


## Draws `subj` into `rect` in the current style.
static func draw(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	match style:
		1:
			_xerox(ci, rect, subj)
		2:
			_wire(ci, rect, subj)
		3:
			_mugshot(ci, rect, subj)
		_:
			_neon(ci, rect, subj)


# --- The subject's shapes (shared by every style) -------------------------------------------

static func _h(key: String, salt: int) -> float:
	return float(absi(hash([key, salt])) % 1000) / 1000.0


## Silhouette parts in rect space: "body" (shoulders), "head" (polygon), "hair" (polygon or
## empty), "eyes" ([visor rect] or lens circle), "extras" (lines), "emblem" (corp).
static func _shapes(rect: Rect2, subj: Dictionary) -> Dictionary:
	var kind: int = subj["kind"]
	var key: String = subj["key"]
	var w := rect.size.x
	var c := rect.position + Vector2(w * 0.5, rect.size.y * (0.44 if kind != Kind.BOSS else 0.46))
	var r := w * (0.2 if kind != Kind.BOSS else 0.23)
	var out := {"c": c, "r": r, "hair": PackedVector2Array(), "extras": [], "visor": Rect2(), "lens": 0.0, "tie": PackedVector2Array()}
	var bl := Vector2(rect.position.x + w * (0.04 if kind == Kind.BOSS else 0.1), rect.end.y)
	var br := Vector2(rect.end.x - w * (0.04 if kind == Kind.BOSS else 0.1), rect.end.y)
	var sh := r * (1.9 if kind == Kind.BOSS else 1.6)
	out["body"] = PackedVector2Array([bl, Vector2(c.x - sh, c.y + r * 1.45), Vector2(c.x + sh, c.y + r * 1.45), br])
	if kind == Kind.MACHINE:
		# A drone or program: a rounded box head with one big lens and antennae.
		var box := PackedVector2Array()
		for k in 16:
			var a := TAU * k / 16.0
			var v := Vector2(cos(a), sin(a))
			box.append(c + Vector2(signf(v.x) * pow(absf(v.x), 0.45), signf(v.y) * pow(absf(v.y), 0.45)) * r * Vector2(1.15, 0.95))
		out["head"] = box
		out["lens"] = r * (0.42 + _h(key, 3) * 0.18)
		var n := 1 + int(_h(key, 4) * 3.0)
		for k in n:
			var x := c.x + (k - (n - 1) * 0.5) * r * 0.55
			out["extras"].append([Vector2(x, c.y - r * 0.9), Vector2(x + (k - 1) * r * 0.2, c.y - r * 1.6)])
		out["body"] = PackedVector2Array([Vector2(c.x - r * 0.9, rect.end.y), Vector2(c.x - r * 0.5, c.y + r * 1.0), Vector2(c.x + r * 0.5, c.y + r * 1.0), Vector2(c.x + r * 0.9, rect.end.y)])
		return out
	var head := PackedVector2Array()
	for k in 20:
		var a := TAU * k / 20.0
		var jaw := 1.0 + maxf(0.0, sin(a)) * 0.18
		head.append(c + Vector2(cos(a) * r * 0.86, sin(a) * r * jaw))
	out["head"] = head
	# Eyes: a visor band for operatives and bosses, glasses for agents and corp faces.
	out["visor"] = Rect2(c.x - r * 0.72, c.y - r * 0.18, r * 1.44, r * (0.3 if kind in [Kind.OPERATIVE, Kind.BOSS] else 0.2))
	var hair := PackedVector2Array()
	var hs := int(_h(key, 1) * 5.0)
	if kind in [Kind.AGENT, Kind.CORP]:
		hs = 5  # neat side part
	match hs:
		0:  # mohawk
			for k in 7:
				var t := float(k) / 6.0
				hair.append(c + Vector2(lerpf(-r * 0.22, r * 0.22, t), -r * (1.0 + (0.6 if k % 2 == 0 else 0.25))))
			hair.append(c + Vector2(r * 0.22, -r * 0.7))
			hair.append(c + Vector2(-r * 0.22, -r * 0.7))
		1:  # hood
			for k in 13:
				var a := PI + PI * k / 12.0
				hair.append(c + Vector2(cos(a) * r * 1.2, sin(a) * r * 1.3 + r * 0.1))
			hair.append(c + Vector2(r * 1.25, r * 1.2))
			hair.append(c + Vector2(r * 0.9, r * 0.2))
			hair.append(c + Vector2(-r * 0.9, r * 0.2))
			hair.append(c + Vector2(-r * 1.25, r * 1.2))
		2:  # spikes
			for k in 9:
				var a := PI + PI * k / 8.0
				var rr := r * (1.35 if k % 2 == 0 else 0.95)
				hair.append(c + Vector2(cos(a) * rr, sin(a) * rr - r * 0.05))
		3:  # bob
			for k in 13:
				var a := PI * 0.95 + PI * 1.1 * k / 12.0
				hair.append(c + Vector2(cos(a) * r * 1.05, sin(a) * r * 1.05 - r * 0.05))
			hair.append(c + Vector2(r * 1.0, r * 0.55))
			hair.append(c + Vector2(r * 0.75, r * 0.55))
			hair.append(c + Vector2(r * 0.75, -r * 0.4))
			hair.append(c + Vector2(-r * 0.75, -r * 0.4))
			hair.append(c + Vector2(-r * 0.75, r * 0.55))
			hair.append(c + Vector2(-r * 1.0, r * 0.55))
		4:  # shaved: a thin cap
			for k in 9:
				var a := PI * 1.1 + PI * 0.8 * k / 8.0
				hair.append(c + Vector2(cos(a) * r * 0.92, sin(a) * r * 1.02))
		_:  # side part
			for k in 11:
				var a := PI * 1.05 + PI * 0.9 * k / 10.0
				hair.append(c + Vector2(cos(a) * r * 0.95, sin(a) * r * 1.08))
			hair.append(c + Vector2(r * 0.8, -r * 0.35))
			hair.append(c + Vector2(-r * 0.3, -r * 0.55))
			hair.append(c + Vector2(-r * 0.85, -r * 0.2))
	out["hair"] = hair
	if kind in [Kind.AGENT, Kind.CORP]:
		# Suit collar and tie.
		out["tie"] = PackedVector2Array([Vector2(c.x - r * 0.12, c.y + r * 1.5), Vector2(c.x + r * 0.12, c.y + r * 1.5), Vector2(c.x + r * 0.2, rect.end.y), Vector2(c.x - r * 0.2, rect.end.y)])
		out["extras"].append([Vector2(c.x - r * 0.5, c.y + r * 1.45), Vector2(c.x, c.y + r * 2.1)])
		out["extras"].append([Vector2(c.x + r * 0.5, c.y + r * 1.45), Vector2(c.x, c.y + r * 2.1)])
	if kind == Kind.BOSS:
		# A crown of antennae spikes and a halo ring.
		for k in 5:
			var a := PI * 1.15 + PI * 0.7 * k / 4.0
			var p0 := c + Vector2(cos(a), sin(a)) * r * 1.05
			out["extras"].append([p0, c + Vector2(cos(a), sin(a)) * r * (1.55 + (0.25 if k == 2 else 0.0))])
	return out


static func _poly(ci: CanvasItem, pts: PackedVector2Array, col: Color) -> void:
	if pts.size() >= 3:
		ci.draw_colored_polygon(pts, col)


static func _outline(ci: CanvasItem, pts: PackedVector2Array, col: Color, w: float) -> void:
	if pts.size() >= 2:
		var closed := pts.duplicate()
		closed.append(pts[0])
		ci.draw_polyline(closed, col, w, true)


## A corporation's emblem in the backdrop (a ring and a letter-like mark).
static func _emblem(ci: CanvasItem, at: Vector2, s: float, key: String, col: Color) -> void:
	ci.draw_arc(at, s, 0, TAU, 32, col, maxf(1.0, s * 0.12), true)
	var n := 3 + int(_h(key, 7) * 4.0)
	var pts := PackedVector2Array()
	for k in n:
		var a := -PI * 0.5 + TAU * k / n
		pts.append(at + Vector2(cos(a), sin(a)) * s * 0.55)
	_outline(ci, pts, col, maxf(1.0, s * 0.1))


# --- Style 0: NEON BUST ---------------------------------------------------------------------

static func _neon(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint: Color = subj["tint"]
	var top := Palette.NIGHT_SKY
	var bottom := tint.darkened(0.5)
	ci.draw_polygon(PackedVector2Array([rect.position, Vector2(rect.end.x, rect.position.y), rect.end, Vector2(rect.position.x, rect.end.y)]),
		PackedColorArray([top, top, bottom, bottom]))
	for k in 6:
		var y := rect.position.y + rect.size.y * (0.1 + k * 0.16)
		ci.draw_line(Vector2(rect.position.x, y), Vector2(rect.end.x, y), Color(tint, 0.08), 1.0)
	var s := _shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.78, 0.22), rect.size.x * 0.14, subj["key"], Color(tint, 0.6))
	if kind == Kind.BOSS:
		ci.draw_arc(c, r * 1.9, 0, TAU, 48, Color(tint, 0.35), 3.0, true)
		ci.draw_arc(c, r * 1.9, 0, TAU, 48, Color(tint, 0.9), 1.2, true)
	var body := Color("#07080F")
	_poly(ci, s["body"], body)
	_poly(ci, s["head"], body)
	_poly(ci, s["hair"], body.lightened(0.04))
	_outline(ci, s["hair"], Color(tint, 0.55), maxf(1.0, r * 0.05))
	_poly(ci, s["tie"], Color(tint, 0.8))
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], Color(tint, 0.85), maxf(1.2, r * 0.07), true)
	# Rim light down the lit side.
	ci.draw_arc(c, r * 0.98, -PI * 0.45, PI * 0.35, 16, Color(tint, 0.9), maxf(1.2, r * 0.08), true)
	var b: PackedVector2Array = s["body"]
	ci.draw_line(b[2], b[3], Color(tint, 0.7), maxf(1.2, r * 0.07), true)
	if kind == Kind.MACHINE:
		var lens: float = s["lens"]
		ci.draw_circle(c, lens * 1.25, Color(tint, 0.25))
		ci.draw_circle(c, lens, Color(tint, 0.95))
		ci.draw_circle(c, lens * 0.45, Color("#07080F"))
		ci.draw_circle(c + Vector2(-lens * 0.3, -lens * 0.3), lens * 0.15, Color(1, 1, 1, 0.8))
		_outline(ci, s["head"], Color(tint, 0.6), maxf(1.0, r * 0.05))
	else:
		var v: Rect2 = s["visor"]
		ci.draw_rect(v.grow(r * 0.06), Color(tint, 0.25))
		ci.draw_rect(v, Color(tint, 0.95))


# --- Style 1: XEROX ZINE --------------------------------------------------------------------

static func _xerox(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint: Color = subj["tint"]
	var paper := Palette.PAPER.darkened(0.05)
	ci.draw_rect(rect, paper)
	# Photocopier streaks and a halftone wash toward the bottom.
	for k in 5:
		var x := rect.position.x + rect.size.x * _h(subj["key"], 20 + k)
		ci.draw_line(Vector2(x, rect.position.y), Vector2(x + 2, rect.end.y), Color(0, 0, 0, 0.06), 1.0 + k % 2)
	var step := maxf(3.0, rect.size.x / 28.0)
	var y := rect.position.y + step * 0.5
	while y < rect.end.y:
		var x := rect.position.x + step * 0.5 + (step * 0.5 if int(y / step) % 2 == 1 else 0.0)
		var t := (y - rect.position.y) / rect.size.y
		while x < rect.end.x:
			ci.draw_circle(Vector2(x, y), step * 0.42 * t, Color(0, 0, 0, 0.35))
			x += step
		y += step
	var s := _shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	var ink := Palette.INK
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.78, 0.22), rect.size.x * 0.14, subj["key"], Color(ink, 0.7))
	_poly(ci, s["body"], ink)
	_poly(ci, s["head"], ink)
	_poly(ci, s["hair"], ink)
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], ink, maxf(1.5, r * 0.09), true)
	# Paper highlight on the face.
	ci.draw_arc(c + Vector2(-r * 0.1, 0), r * 0.7, PI * 0.6, PI * 1.3, 12, Color(paper, 0.7), maxf(1.0, r * 0.1), true)
	if kind == Kind.MACHINE:
		var lens: float = s["lens"]
		ci.draw_circle(c, lens, paper)
		ci.draw_circle(c, lens * 0.5, ink)
	else:
		# The Cell's marker censor bar over the eyes, in the owner's colour.
		var v: Rect2 = s["visor"]
		var bar := PackedVector2Array([v.position + Vector2(-r * 0.25, r * 0.08), Vector2(v.end.x + r * 0.3, v.position.y - r * 0.05), Vector2(v.end.x + r * 0.25, v.end.y + r * 0.05), Vector2(v.position.x - r * 0.3, v.end.y + r * 0.12)])
		_poly(ci, bar, tint)
	if kind == Kind.BOSS:
		# Marker crown scrawl.
		var cr := PackedVector2Array([c + Vector2(-r * 0.8, -r * 1.25), c + Vector2(-r * 0.5, -r * 1.7), c + Vector2(-r * 0.2, -r * 1.3), c + Vector2(0, -r * 1.8), c + Vector2(r * 0.2, -r * 1.3), c + Vector2(r * 0.5, -r * 1.7), c + Vector2(r * 0.8, -r * 1.25)])
		ci.draw_polyline(cr, tint, maxf(2.0, r * 0.12), true)
	# Tape strip.
	ci.draw_rect(Rect2(rect.position + Vector2(rect.size.x * 0.3, -rect.size.y * 0.02), Vector2(rect.size.x * 0.4, rect.size.y * 0.08)), Color(Palette.NOTE_TAPE, 0.85))


# --- Style 2: WIRE SCAN ---------------------------------------------------------------------

static func _wire(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint: Color = subj["tint"]
	ci.draw_rect(rect, Color("#02040C"))
	var step := rect.size.x / 10.0
	for k in 11:
		ci.draw_line(Vector2(rect.position.x + k * step, rect.position.y), Vector2(rect.position.x + k * step, rect.end.y), Color(Palette.NET_CYAN, 0.07), 1.0)
		ci.draw_line(Vector2(rect.position.x, rect.position.y + k * step), Vector2(rect.end.x, rect.position.y + k * step), Color(Palette.NET_CYAN, 0.07), 1.0)
	var s := _shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	var w := maxf(1.0, r * 0.05)
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.78, 0.22), rect.size.x * 0.14, subj["key"], Color(tint, 0.7))
	_poly(ci, s["head"], Color(tint, 0.08))
	_poly(ci, s["body"], Color(tint, 0.06))
	# Contour rings round the head and a meridian mesh.
	for k in 5:
		var t := -0.7 + k * 0.35
		var hw := r * 0.86 * sqrt(maxf(0.0, 1.0 - t * t))
		ci.draw_line(Vector2(c.x - hw, c.y + t * r), Vector2(c.x + hw, c.y + t * r), Color(tint, 0.5), w, true)
	for k in 5:
		var t := -0.8 + k * 0.4
		var pts := PackedVector2Array()
		for q in 11:
			var a := -PI * 0.5 + PI * q / 10.0
			pts.append(c + Vector2(sin(a + PI * 0.5) * 0.0 + t * r * 0.86 * cos(a), sin(a) * r))
		ci.draw_polyline(pts, Color(tint, 0.35), w, true)
	_outline(ci, s["head"], tint, w * 1.6)
	_outline(ci, s["hair"], Color(tint, 0.8), w * 1.2)
	var b: PackedVector2Array = s["body"]
	ci.draw_polyline(b, tint, w * 1.6, true)
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], tint, w * 1.4, true)
	if kind == Kind.MACHINE:
		ci.draw_arc(c, s["lens"], 0, TAU, 24, Palette.CELL_ACID, w * 2.0, true)
		ci.draw_circle(c, float(s["lens"]) * 0.3, Palette.CELL_ACID)
	else:
		var v: Rect2 = s["visor"]
		ci.draw_rect(v, Color(Palette.CELL_ACID, 0.85))
	# Scan line and corner brackets.
	var sy := rect.position.y + rect.size.y * (0.3 + _h(subj["key"], 9) * 0.4)
	ci.draw_line(Vector2(rect.position.x, sy), Vector2(rect.end.x, sy), Color(Palette.CELL_ACID, 0.5), 1.0)
	var bk := rect.size.x * 0.12
	for corner in [rect.position, Vector2(rect.end.x, rect.position.y), rect.end, Vector2(rect.position.x, rect.end.y)]:
		var dx := bk if corner.x == rect.position.x else -bk
		var dy := bk if corner.y == rect.position.y else -bk
		var p: Vector2 = corner + Vector2(signf(dx), signf(dy)) * 3.0
		ci.draw_line(p, p + Vector2(dx, 0), Palette.NET_CYAN, 1.5)
		ci.draw_line(p, p + Vector2(0, dy), Palette.NET_CYAN, 1.5)
	if kind == Kind.BOSS:
		ci.draw_arc(c, r * 1.8, -PI * 0.9, -PI * 0.1, 24, Palette.CELL_PINK, 2.0, true)
		ci.draw_string(Palette.mono(), rect.position + Vector2(6, 12), "THREAT: MAX", HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(7, int(rect.size.x / 14.0)), Palette.CELL_PINK)


# --- Style 3: MUGSHOT -----------------------------------------------------------------------

static func _mugshot(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint: Color = subj["tint"]
	ci.draw_rect(rect, Color("#1A1F2B"))
	# Height chart.
	var rows := 8
	for k in rows:
		var y := rect.position.y + rect.size.y * (k + 0.5) / rows
		ci.draw_line(Vector2(rect.position.x, y), Vector2(rect.end.x, y), Color(1, 1, 1, 0.14 if k % 2 == 0 else 0.07), 1.0)
		if k % 2 == 0:
			ci.draw_string(Palette.mono(), Vector2(rect.position.x + 2, y - 2), str(7 - k / 2) + "'", HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(6, int(rect.size.x / 16.0)), Color(1, 1, 1, 0.3))
	# Harsh flash: a pale disc behind the head.
	var s := _shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	ci.draw_circle(c + Vector2(r * 0.3, -r * 0.2), r * 1.6, Color(1, 1, 1, 0.06))
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.8, 0.2), rect.size.x * 0.12, subj["key"], Color(tint, 0.5))
	# Glitch split: the silhouette offset in pink and cyan, then the dark figure.
	for pass_n in 3:
		var off: Vector2 = [Vector2(-r * 0.07, 0), Vector2(r * 0.07, 0), Vector2.ZERO][pass_n]
		var col: Color = [Color(Palette.CELL_PINK, 0.55), Color(Palette.NET_CYAN, 0.55), Color("#0B0D14")][pass_n]
		for part in ["body", "head", "hair"]:
			var pts: PackedVector2Array = s[part]
			if pts.size() < 3:
				continue
			var moved := PackedVector2Array()
			for p in pts:
				moved.append(p + off)
			ci.draw_colored_polygon(moved, col)
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], Color("#0B0D14"), maxf(1.5, r * 0.09), true)
	_poly(ci, s["tie"], Color(tint, 0.7))
	if kind == Kind.MACHINE:
		ci.draw_circle(c, s["lens"], Color(tint, 0.9))
		ci.draw_circle(c, float(s["lens"]) * 0.4, Color("#0B0D14"))
	else:
		var v: Rect2 = s["visor"]
		ci.draw_rect(v, Color(tint, 0.9))
	# Placard with the name.
	var pl := Rect2(rect.position.x + rect.size.x * 0.14, rect.end.y - rect.size.y * 0.2, rect.size.x * 0.72, rect.size.y * 0.15)
	ci.draw_rect(pl, Color(0.05, 0.05, 0.06))
	ci.draw_rect(pl, Color(1, 1, 1, 0.6), false, 1.0)
	var fs := maxi(6, int(pl.size.y * 0.42))
	ci.draw_string(Palette.mono(), pl.position + Vector2(3, pl.size.y * 0.5 + fs * 0.35), String(subj.get("name", "")).to_upper(), HORIZONTAL_ALIGNMENT_CENTER, pl.size.x - 6, fs, Color(1, 1, 1, 0.9))
	if kind == Kind.BOSS:
		ci.draw_rect(Rect2(rect.position + Vector2(4, 4), Vector2(rect.size.x * 0.4, rect.size.y * 0.1)), Palette.CELL_PINK)
		ci.draw_string(Palette.mono(), rect.position + Vector2(8, 4 + rect.size.y * 0.075), "MOST WANTED", HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(6, int(rect.size.y * 0.06)), Palette.INK)
