class_name PortraitArt
extends RefCounted
## Drawn portraits until final art lands (ART_BIBLE 7.1, 7.2; STYLE_GUIDE 7). One subject
## model, four looks. A subject is {kind, key, tint, name, ...}: kind is one of Kind (an
## operative, a corporate agent, a machine or program, a boss, a corporation's face); key
## picks the deterministic details; tint is the owner's colour.
##
## Operatives (art pass W5): each of the eight §7.1 classes has its own head-and-shoulders
## silhouette and prop (CLASS_IDS; `silhouette_polygons`), painted in its class accent
## (`Palette.class_accent`). The operative id's hash varies hair, visor and a shade of that
## accent (never another hue), so two Breakers look apart and still read as Breakers.
## Four expressions (Expr): neutral, hurt, triumphant, flatlined (grey, a flat line).
## Enemies carry their corporation's hue and pattern (`CorpPattern`) on the body.
##
## Styles (`style`, `--demo-portrait=N`): 0 NEON BUST, 1 XEROX ZINE, 2 WIRE SCAN,
## 3 MUGSHOT. View only; decoration hashes, not game randomness. Final painted art drops in
## behind the views (`Polaroid.portrait`, `ClassData.portrait`) without code changes.

enum Kind { OPERATIVE, AGENT, MACHINE, BOSS, CORP }
## ART_BIBLE 7.1: the four expressions every operative portrait has.
enum Expr { NEUTRAL, HURT, TRIUMPHANT, FLATLINED }
const EXPRESSION_NAMES: Array[String] = ["NEUTRAL", "HURT", "TRIUMPHANT", "FLATLINED"]
const STYLE_NAMES: Array[String] = ["NEON BUST", "XEROX ZINE", "WIRE SCAN", "MUGSHOT"]
## Name words that mark an enemy as a machine or program rather than a person.
const MACHINE_WORDS: Array[String] = ["drone", "daemon", "core", "array", "mast", "relay", "station", "pad", "unit", "script",
	"process", "engine", "meter", "satellite", "scanner", "dispenser", "debris", "template", "swarm", "hauler", "optimizer", "control", "drop", "proxy", "board", "office", "authority", "manifest", "routing", "powers", "test"]
## The eight §7.1 classes (content ids, content/classes/*.tres) in the bible's order. Each
## has its own silhouette and prop; any other id draws the generic operative.
const CLASS_IDS: Array[StringName] = [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]
## Per-operative variation (id hash): hair styles and visor variants per class, and three
## shades of the class accent (lighter, as is, darker by SHADE_STEP; always nearest its
## own class accent, tested).
const HAIR_STYLES := 4
const VISOR_STYLES := 3
const SHADE_STEP := 0.07
## The silhouette mask's grid (cells per side) for `silhouette_mask`.
const MASK_CELLS := 48

## Base tones (all Palette tokens; no literal colours): the figure's dark mass, the wire
## scan's and the mugshot's backdrops, and the light that picks out highlights.
const FIGURE := Palette.NIGHT_SKY
const WIRE_BACK := Palette.NET_BG_OUTER
const MUG_BACK := Palette.DESK_DARK
const LIGHT := Palette.TEXT_HI
## How much lighter the figure's hair and a masked face read than the dark mass.
const FIGURE_LIFT := 0.05
## Corp pattern on enemy bodies: the pattern's scale is the portrait width over this
## (px), clamped to PATTERN_SCALE_MIN..1; its alpha on the body in NEON and WIRE.
const PATTERN_REF := 140.0
const PATTERN_SCALE_MIN := 0.45
const PATTERN_ALPHA := 0.5
## Expression poses: head turn (degrees) and shift (head radii), eye squint (y scale).
const POSE := {
	Expr.NEUTRAL: [0.0, Vector2.ZERO, 1.0],
	Expr.HURT: [8.0, Vector2(0.06, 0.07), 0.45],
	Expr.TRIUMPHANT: [-6.0, Vector2(0.0, -0.09), 1.0],
	Expr.FLATLINED: [14.0, Vector2(0.1, 0.16), 1.0],
}
## Flatlined: the whole portrait greys (luma weights) and dims by this much.
const FLAT_DIM := 0.3
## The flat line's height (share of the rect) and its one last blip.
const FLAT_LINE_Y := 0.82
const FLAT_BLIP := 0.07

static var style: int = 0
## The rect being drawn (polygons clip to it); empty between draws.
static var _clip: Rect2 = Rect2()


## A subject for an enemy from its content (boss / machine / agent by name), in its
## corporation's hue and pattern (ART_BIBLE 7.2, 3.6).
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
	return {"kind": kind, "key": String(id), "tint": Palette.corp_color(corporation_id), "name": display_name,
		"corp": corporation_id, "pattern": Palette.corp_pattern_id(corporation_id), "expression": Expr.NEUTRAL}


## A subject for an enemy's content resource (EnemyData).
static func enemy_data_subject(data: EnemyData) -> Dictionary:
	return enemy_subject(data.id, data.display_name, data.corporation_id, data.is_boss)


## A subject for one operative (H20: every operative of a class had the same face): the
## class sets the silhouette and accent, and the operative id varies hair, visor and a
## shade of the accent through a hash of both (deterministic, no RNG), so two Breakers
## look different and one operative looks the same on every screen. An empty
## `operative_id` gives the class's own face.
static func operative_subject(class_id: StringName, operative_id: StringName = &"", display_name: String = "",
		expression: int = Expr.NEUTRAL) -> Dictionary:
	var key := String(class_id) if operative_id == &"" else "%s/%s" % [class_id, operative_id]
	var accent := Palette.class_accent(class_id)
	var shade := _hi(key, 11, 3)
	var tint := accent
	if shade == 0:
		tint = accent.lightened(SHADE_STEP)
	elif shade == 2:
		tint = accent.darkened(SHADE_STEP)
	return {"kind": Kind.OPERATIVE, "key": key, "class": class_id, "tint": tint, "accent": accent, "name": display_name,
		"hair": _hi(key, 1, HAIR_STYLES), "visor": _hi(key, 2, VISOR_STYLES), "expression": expression}


## A copy of `subj` with `expression` (Expr).
static func with_expression(subj: Dictionary, expression: int) -> Dictionary:
	var out := subj.duplicate()
	out["expression"] = expression
	return out


## Draws one operative's portrait into `rect` in the current style (the combat caption
## and the dossiers use the same call, so an operative keeps one face everywhere).
## `expression` defaults to neutral.
static func draw_operative(ci: CanvasItem, rect: Rect2, class_id: StringName, operative_id: StringName = &"",
		display_name: String = "", expression: int = Expr.NEUTRAL) -> void:
	draw(ci, rect, operative_subject(class_id, operative_id, display_name, expression))


## Draws `subj` into `rect` in the current style.
static func draw(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	_clip = rect
	match style:
		1:
			_xerox(ci, rect, subj)
		2:
			_wire(ci, rect, subj)
		3:
			_mugshot(ci, rect, subj)
		_:
			_neon(ci, rect, subj)
	if _flat(subj):
		_flatline(ci, rect)
	_clip = Rect2()


## Draws a class's neutral silhouette (body, head and prop) flat in `col`: the class
## glyph beside a dossier's class tag.
static func draw_silhouette(ci: CanvasItem, rect: Rect2, class_id: StringName, col: Color) -> void:
	for p in silhouette_polygons(rect, operative_subject(class_id)):
		_poly(ci, p, col)


## The filled polygons that make `subj`'s silhouette in `rect` (body, head, hair, props).
static func silhouette_polygons(rect: Rect2, subj: Dictionary) -> Array[PackedVector2Array]:
	var s := shapes(rect, subj)
	var out: Array[PackedVector2Array] = []
	for part in ["body", "head", "hair"]:
		var p: PackedVector2Array = s[part]
		if p.size() >= 3:
			out.append(p)
	for pr in s["props"]:
		out.append(pr["p"])
	return out


## `subj`'s silhouette as a MASK_CELLS x MASK_CELLS grid (1 = inside), sampled at cell
## centres of a unit square portrait. Tests compare classes with it.
static func silhouette_mask(subj: Dictionary, cells: int = MASK_CELLS) -> PackedByteArray:
	var polys := silhouette_polygons(Rect2(0, 0, cells, cells), subj)
	var out := PackedByteArray()
	out.resize(cells * cells)
	for y in cells:
		for x in cells:
			var p := Vector2(x + 0.5, y + 0.5)
			for poly in polys:
				if Geometry2D.is_point_in_polygon(p, poly):
					out[y * cells + x] = 1
					break
	return out


## How far apart two masks are: cells in one but not the other over cells in either (0 =
## the same silhouette, 1 = no overlap).
static func mask_difference(a: PackedByteArray, b: PackedByteArray) -> float:
	var either := 0
	var one := 0
	for i in mini(a.size(), b.size()):
		if a[i] == 1 or b[i] == 1:
			either += 1
			if a[i] != b[i]:
				one += 1
	return float(one) / maxf(1.0, either)


# --- The subject's shapes (shared by every style) -------------------------------------------

static func _h(key: String, salt: int) -> float:
	return float(absi(hash([key, salt])) % 1000) / 1000.0


static func _hi(key: String, salt: int, n: int) -> int:
	return absi(hash([key, salt])) % n


static func _flat(subj: Dictionary) -> bool:
	return int(subj.get("expression", Expr.NEUTRAL)) == Expr.FLATLINED


## `col` as the subject shows it: greyed when flatlined (luma), else as is.
static func _k(subj: Dictionary, col: Color) -> Color:
	if not _flat(subj):
		return col
	var g := (col.r * 0.299 + col.g * 0.587 + col.b * 0.114) * (1.0 - FLAT_DIM)
	return Color(g, g, g, col.a)


## Points from head-radius units round `c` (flat x, y list).
static func _u(c: Vector2, r: float, xy: Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	for i in range(0, xy.size() - 1, 2):
		out.append(c + Vector2(xy[i], xy[i + 1]) * r)
	return out


static func _ellipse(c: Vector2, rx: float, ry: float, n: int = 20) -> PackedVector2Array:
	var out := PackedVector2Array()
	for k in n:
		var a := TAU * k / n
		out.append(c + Vector2(cos(a) * rx, sin(a) * ry))
	return out


## A polyline thickened into a filled polygon (a prop's bar or cable).
static func _stroke(pts: PackedVector2Array, width: float) -> PackedVector2Array:
	var polys := Geometry2D.offset_polyline(pts, width * 0.5, Geometry2D.JOIN_ROUND, Geometry2D.END_ROUND)
	return polys[0] if polys.size() > 0 else PackedVector2Array()


## A rounded box (rect centred on `c`).
static func _box(c: Vector2, half: Vector2, roundness: float = 0.45) -> PackedVector2Array:
	var out := PackedVector2Array()
	for k in 20:
		var a := TAU * k / 20.0
		var v := Vector2(cos(a), sin(a))
		out.append(c + Vector2(signf(v.x) * pow(absf(v.x), roundness), signf(v.y) * pow(absf(v.y), roundness)) * half)
	return out


## Silhouette parts in rect space (see `_class_parts` for the operative entries):
## "body", "head", "hair" (polygons), "props" [{p, h}] (filled, part of the silhouette),
## "eyes" [polygon] (the glowing eye feature), "visor" (Rect2 round the eyes), "details"
## [{p, w, a, h}] (lines in the tint), "dots" [{at, r, h}] (lights), "scars" [[a, b]],
## "mouth" (polyline), "mask"/"face" (polygons), "extras" (lines), "lens", "tie". Entries
## flagged h move with the head's expression pose.
static func shapes(rect: Rect2, subj: Dictionary) -> Dictionary:
	var kind: int = subj["kind"]
	var key: String = subj["key"]
	var w := rect.size.x
	var c := rect.position + Vector2(w * 0.5, rect.size.y * (0.44 if kind != Kind.BOSS else 0.46))
	var r := w * (0.2 if kind != Kind.BOSS else 0.23)
	var out := {"c": c, "r": r, "hair": PackedVector2Array(), "extras": [], "visor": Rect2(), "lens": 0.0, "tie": PackedVector2Array(),
		"props": [], "eyes": [], "details": [], "dots": [], "scars": [], "mouth": PackedVector2Array(), "mask": PackedVector2Array(),
		"face": PackedVector2Array()}
	var bl := Vector2(rect.position.x + w * (0.04 if kind == Kind.BOSS else 0.1), rect.end.y)
	var br := Vector2(rect.end.x - w * (0.04 if kind == Kind.BOSS else 0.1), rect.end.y)
	var sh := r * (1.9 if kind == Kind.BOSS else 1.6)
	out["body"] = PackedVector2Array([bl, Vector2(c.x - sh, c.y + r * 1.45), Vector2(c.x + sh, c.y + r * 1.45), br])
	if kind == Kind.MACHINE:
		# A drone or program: a rounded box head with one big lens and antennae.
		out["head"] = _box(c, Vector2(r * 1.15, r * 0.95))
		out["lens"] = r * (0.42 + _h(key, 3) * 0.18)
		var n := 1 + int(_h(key, 4) * 3.0)
		for k in n:
			var x := c.x + (k - (n - 1) * 0.5) * r * 0.55
			out["extras"].append([Vector2(x, c.y - r * 0.9), Vector2(x + (k - 1) * r * 0.2, c.y - r * 1.6)])
		out["body"] = PackedVector2Array([Vector2(c.x - r * 0.9, rect.end.y), Vector2(c.x - r * 0.5, c.y + r * 1.0), Vector2(c.x + r * 0.5, c.y + r * 1.0), Vector2(c.x + r * 0.9, rect.end.y)])
		return out
	out["head"] = _head(c, r)
	# Eyes: a visor band for operatives and bosses, glasses for agents and corp faces.
	var visor := Rect2(c.x - r * 0.72, c.y - r * 0.18, r * 1.44, r * (0.3 if kind in [Kind.OPERATIVE, Kind.BOSS] else 0.2))
	out["visor"] = visor
	out["eyes"] = [_rect_poly(visor)]
	var cls: StringName = subj.get("class", &"")
	if kind == Kind.OPERATIVE and CLASS_IDS.has(cls):
		_class_parts(out, rect, subj, cls)
	else:
		out["hair"] = _generic_hair(c, r, 5 if kind in [Kind.AGENT, Kind.CORP] else int(_h(key, 1) * 5.0))
	if kind in [Kind.AGENT, Kind.CORP]:
		# Suit collar and tie.
		out["tie"] = PackedVector2Array([Vector2(c.x - r * 0.12, c.y + r * 1.5), Vector2(c.x + r * 0.12, c.y + r * 1.5), Vector2(c.x + r * 0.2, rect.end.y), Vector2(c.x - r * 0.2, rect.end.y)])
		out["extras"].append([Vector2(c.x - r * 0.5, c.y + r * 1.45), Vector2(c.x, c.y + r * 2.1)])
		out["extras"].append([Vector2(c.x + r * 0.5, c.y + r * 1.45), Vector2(c.x, c.y + r * 2.1)])
	if kind == Kind.BOSS:
		# Sloped shoulders rising to a neck (a boss is a figure, not a plinth), then a crown
		# of antennae spikes and a halo ring.
		out["body"] = PackedVector2Array([bl, Vector2(c.x - sh * 1.1, c.y + r * 2.1), Vector2(c.x - sh * 0.7, c.y + r * 1.45),
			Vector2(c.x - r * 0.45, c.y + r * 1.08), Vector2(c.x + r * 0.45, c.y + r * 1.08), Vector2(c.x + sh * 0.7, c.y + r * 1.45),
			Vector2(c.x + sh * 1.1, c.y + r * 2.1), br])
		for k in 5:
			var a := PI * 1.15 + PI * 0.7 * k / 4.0
			var p0 := c + Vector2(cos(a), sin(a)) * r * 1.05
			out["extras"].append([p0, c + Vector2(cos(a), sin(a)) * r * (1.55 + (0.25 if k == 2 else 0.0))])
	if kind == Kind.OPERATIVE:
		_expression(out, rect, subj)
	return out


static func _head(c: Vector2, r: float) -> PackedVector2Array:
	var head := PackedVector2Array()
	for k in 20:
		var a := TAU * k / 20.0
		var jaw := 1.0 + maxf(0.0, sin(a)) * 0.18
		head.append(c + Vector2(cos(a) * r * 0.86, sin(a) * r * jaw))
	return head


static func _rect_poly(v: Rect2) -> PackedVector2Array:
	return PackedVector2Array([v.position, Vector2(v.end.x, v.position.y), v.end, Vector2(v.position.x, v.end.y)])


## The pre-class hair set (generic operatives, agents and bosses): mohawk, hood, spikes,
## bob, shaved, side part.
static func _generic_hair(c: Vector2, r: float, hs: int) -> PackedVector2Array:
	var hair := PackedVector2Array()
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
	return hair


## Close-cropped hair on top of the head (the variation under a prop): 0 short spikes,
## 1 swept fringe, 2 cap, 3 top knot. Small, so the class's prop carries the silhouette.
static func _crop_hair(c: Vector2, r: float, hs: int) -> PackedVector2Array:
	match hs:
		0:
			var out := PackedVector2Array()
			for k in 9:
				var a := PI * 1.08 + PI * 0.84 * k / 8.0
				var rr := r * (1.12 if k % 2 == 0 else 0.92)
				out.append(c + Vector2(cos(a) * rr * 0.95, sin(a) * rr))
			return out
		1:
			return _u(c, r, [-0.86, -0.1, -0.8, -0.7, -0.3, -1.05, 0.4, -1.02, 0.9, -0.55, 0.3, -0.62, -0.5, -0.45])
		2:
			var cap := PackedVector2Array()
			for k in 9:
				var a := PI * 1.1 + PI * 0.8 * k / 8.0
				cap.append(c + Vector2(cos(a) * r * 0.9, sin(a) * r * 1.02))
			return cap
		_:
			var knot := _u(c, r, [-0.7, -0.62, -0.25, -0.98, -0.18, -1.2, 0.18, -1.2, 0.25, -0.98, 0.7, -0.62])
			return knot


## The eye feature for a visor variant: 0 band, 1 twin lenses, 2 thin slit.
static func _visor_eyes(c: Vector2, r: float, variant: int, y: float = -0.18) -> Array:
	match variant:
		1:
			return [_box(c + Vector2(-0.36, y + 0.12) * r, Vector2(0.28, 0.16) * r, 0.6), _box(c + Vector2(0.36, y + 0.12) * r, Vector2(0.28, 0.16) * r, 0.6)]
		2:
			return [_rect_poly(Rect2(c.x - r * 0.74, c.y + (y + 0.06) * r, r * 1.48, r * 0.14))]
		_:
			return [_rect_poly(Rect2(c.x - r * 0.72, c.y + y * r, r * 1.44, r * 0.3))]


static func _prop(out: Dictionary, p: PackedVector2Array, head: bool) -> void:
	if p.size() >= 3:
		out["props"].append({"p": p, "h": head})


static func _detail(out: Dictionary, p: PackedVector2Array, width: float, alpha: float, head: bool) -> void:
	out["details"].append({"p": p, "w": width, "a": alpha, "h": head})


static func _dot(out: Dictionary, at: Vector2, radius: float, head: bool) -> void:
	out["dots"].append({"at": at, "r": radius, "h": head})


## ART_BIBLE 7.1: the eight classes' silhouettes and props (head radius units round the
## head centre; B = the rect's bottom).
static func _class_parts(out: Dictionary, rect: Rect2, subj: Dictionary, cls: StringName) -> void:
	var c: Vector2 = out["c"]
	var r: float = out["r"]
	var B := (rect.end.y - c.y) / r
	var hs: int = subj.get("hair", 0)
	var vs: int = subj.get("visor", 0)
	out["eyes"] = _visor_eyes(c, r, vs)
	out["hair"] = _crop_hair(c, r, hs)
	match cls:
		&"breaker":
			# Heavy padded jacket (square shoulders to the frame, popped collar) and a
			# crowbar-antenna hooked over the right shoulder.
			out["body"] = _u(c, r, [-2.5, B, -2.45, 1.9, -2.2, 1.3, -1.0, 0.95, -0.55, 1.35, 0.55, 1.35, 1.0, 0.95, 2.2, 1.3, 2.45, 1.9, 2.5, B])
			_prop(out, _stroke(_u(c, r, [1.65, 1.4, 1.4, -1.35, 1.25, -1.85, 0.9, -1.98, 0.68, -1.72]), r * 0.24), false)
			_dot(out, c + Vector2(0.68, -1.72) * r, r * 0.12, false)
			_detail(out, _u(c, r, [0.0, 1.35, 0.0, B]), 0.07, 0.6, false)
			_detail(out, _u(c, r, [-2.35, 1.95, -1.1, 1.75]), 0.06, 0.45, false)
			_detail(out, _u(c, r, [2.35, 1.95, 1.1, 1.75]), 0.06, 0.45, false)
			_detail(out, _u(c, r, [-1.0, 0.95, -0.55, 1.35]), 0.06, 0.6, false)
			_detail(out, _u(c, r, [1.0, 0.95, 0.55, 1.35]), 0.06, 0.6, false)
		&"wrecker":
			# A welding visor plate wider than the face, hinge nubs, a padded left shoulder;
			# scars across the plate and the neck.
			out["head"] = _box(c + Vector2(0, -0.05) * r, Vector2(0.9, 1.02) * r, 0.5)
			_prop(out, _u(c, r, [-1.08, -0.6, 1.08, -0.6, 0.96, 0.62, -0.96, 0.62]), true)
			_prop(out, _ellipse(c + Vector2(-1.14, -0.05) * r, r * 0.22, r * 0.22, 12), true)
			_prop(out, _ellipse(c + Vector2(1.14, -0.05) * r, r * 0.22, r * 0.22, 12), true)
			out["body"] = _u(c, r, [-2.35, B, -2.4, 1.55, -2.1, 0.95, -1.15, 0.95, -0.6, 1.3, 0.6, 1.3, 1.5, 1.55, 1.9, 1.95, 2.0, B])
			var slit: float = [0.16, 0.08, 0.26][vs]
			out["eyes"] = [_rect_poly(Rect2(c.x - r * 0.72, c.y - r * 0.12, r * 1.44, r * slit))]
			out["scars"] = [[c + Vector2(-0.62, -0.46) * r, c + Vector2(-0.18, 0.4) * r], [c + Vector2(-0.52, -0.2) * r, c + Vector2(-0.3, -0.28) * r],
				[c + Vector2(0.35, 1.2) * r, c + Vector2(0.75, 1.5) * r]]
			_detail(out, _u(c, r, [-1.08, -0.6, 1.08, -0.6]), 0.08, 0.7, true)
			_detail(out, _u(c, r, [-2.2, 1.35, -1.25, 1.2]), 0.06, 0.5, false)
			if hs == 1 or hs == 3:
				out["hair"] = _u(c, r, [-0.25, -1.0, -0.12, -1.35, 0.12, -1.35, 0.25, -1.0])
			else:
				out["hair"] = PackedVector2Array()
		&"ghost":
			# A peaked hood that is the head's outline, a dark face opening crossed by a
			# face-mesh, narrow sloped shoulders.
			out["hair"] = _u(c, r, [0.18, -1.9, 0.82, -1.42, 1.22, -0.5, 1.32, 0.5, 1.5, 1.35, -1.5, 1.35, -1.32, 0.5, -1.22, -0.5, -0.78, -1.46])
			out["face"] = _ellipse(c + Vector2(0, 0.12) * r, r * 0.74, r * 0.95, 20)
			out["body"] = _u(c, r, [-2.05, B, -1.95, 2.05, -1.5, 1.3, 1.5, 1.3, 1.95, 2.05, 2.05, B])
			for k in 5:
				var x := -0.56 + k * 0.28
				var hy := 0.95 * sqrt(maxf(0.0, 1.0 - pow(x / 0.74, 2.0)))
				_detail(out, _u(c, r, [x, 0.12 - hy, x, 0.12 + hy]), 0.04, 0.4, true)
			for k in 6:
				var y := -0.62 + k * 0.28
				var hx := 0.74 * sqrt(maxf(0.0, 1.0 - pow(y / 0.95, 2.0)))
				_detail(out, _u(c, r, [-hx, 0.12 + y, hx, 0.12 + y]), 0.04, 0.4, true)
			var eye: float = [0.1, 0.07, 0.13][vs]
			out["eyes"] = [_ellipse(c + Vector2(-0.3, -0.05) * r, r * 0.16, r * eye, 10), _ellipse(c + Vector2(0.3, -0.05) * r, r * 0.16, r * eye, 10)]
			if hs == 1 or hs == 2:
				out["details"].append({"p": _u(c, r, [-0.6, -0.55, -0.2, -0.78, 0.3, -0.7]), "w": 0.07, "a": 0.55, "h": true})
			out["hair_under"] = true
		&"phantom":
			# A smooth mask with angled slits, and a long coat whose collar stands up past
			# the ears on both sides.
			out["mask"] = _u(c, r, [-0.72, -0.72, 0.72, -0.72, 0.8, 0.1, 0.45, 0.78, 0.0, 0.95, -0.45, 0.78, -0.8, 0.1])
			_prop(out, _u(c, r, [-0.7, 1.25, -1.2, -0.5, -1.62, -1.0, -1.8, 0.25, -1.65, 1.45]), false)
			_prop(out, _u(c, r, [0.7, 1.25, 1.2, -0.5, 1.62, -1.0, 1.8, 0.25, 1.65, 1.45]), false)
			out["body"] = _u(c, r, [-2.1, B, -2.05, 1.95, -1.65, 1.35, -0.6, 1.25, 0.6, 1.25, 1.65, 1.35, 2.05, 1.95, 2.1, B])
			_detail(out, _u(c, r, [-0.7, 1.25, 0.0, 2.45, 0.7, 1.25]), 0.07, 0.6, false)
			_detail(out, _u(c, r, [-1.2, -0.5, -1.25, 1.2]), 0.05, 0.45, false)
			_detail(out, _u(c, r, [1.2, -0.5, 1.25, 1.2]), 0.05, 0.45, false)
			var tilt: float = [0.12, 0.2, 0.05][vs]
			out["eyes"] = [_u(c, r, [-0.62, -0.25 - tilt, -0.14, -0.12, -0.18, 0.0, -0.64, -0.12 - tilt]),
				_u(c, r, [0.62, -0.25 - tilt, 0.14, -0.12, 0.18, 0.0, 0.64, -0.12 - tilt])]
			out["hair"] = [_u(c, r, [-0.84, -0.3, -0.7, -0.85, 0.0, -1.1, 0.7, -0.85, 0.84, -0.3, 0.75, -0.72, 0.0, -0.9, -0.75, -0.72]),
				_u(c, r, [-0.8, -0.4, -0.5, -1.0, 0.1, -1.18, 0.75, -0.9, 0.86, -0.35, 0.4, -0.85]),
				_u(c, r, [-0.78, -0.5, -0.2, -1.08, 0.2, -1.1, 0.3, -1.45, 0.5, -1.05, 0.8, -0.5]),
				_u(c, r, [-0.85, -0.2, -0.75, -0.8, -0.1, -1.08, 0.0, -0.8, 0.1, -1.08, 0.75, -0.8, 0.85, -0.2])][hs]
		&"rigger":
			# Round goggles pushed up on the brow (they stick out past the head), a strap,
			# a cable harness over the chest and a cable loop off the left shoulder.
			var gr: float = [0.4, 0.36, 0.42][vs]
			_prop(out, _ellipse(c + Vector2(-0.52, -0.52) * r, r * gr, r * gr, 16), true)
			_prop(out, _ellipse(c + Vector2(0.52, -0.52) * r, r * gr, r * gr, 16), true)
			_detail(out, _u(c, r, [-0.9, -0.45, -0.95, -0.2]), 0.12, 0.8, true)
			_detail(out, _u(c, r, [0.9, -0.45, 0.95, -0.2]), 0.12, 0.8, true)
			var lens: float = gr * 0.62
			out["eyes"] = [_ellipse(c + Vector2(-0.52, -0.52) * r, r * lens, r * lens, 14), _ellipse(c + Vector2(0.52, -0.52) * r, r * lens, r * lens, 14)]
			out["body"] = _u(c, r, [-2.1, B, -2.0, 1.8, -1.6, 1.4, 1.6, 1.4, 2.0, 1.8, 2.1, B])
			_prop(out, _stroke(_u(c, r, [-1.45, 1.5, -2.1, 0.95, -2.36, 1.55, -2.15, 2.3, -1.55, 2.45]), r * 0.2), false)
			_prop(out, _box(c + Vector2(-1.45, 2.45) * r, Vector2(0.2, 0.14) * r), false)
			_detail(out, _u(c, r, [-1.4, 1.45, 1.1, B]), 0.1, 0.75, false)
			_detail(out, _u(c, r, [1.4, 1.45, -1.1, B]), 0.1, 0.75, false)
			_dot(out, c + Vector2(0.0, 2.0) * r, r * 0.12, false)
			out["hair"] = [_generic_hair(c, r, 2), _crop_hair(c, r, 1), _crop_hair(c, r, 2), _generic_hair(c, r, 3)][hs]
		&"overclocker":
			# A crown of heat-sink fins (tallest in the middle) with LEDs on the tips, an LED
			# strip for eyes and a square vented collar.
			_prop(out, _rect_poly(Rect2(c.x - r * 0.88, c.y - r * 1.0, r * 1.76, r * 0.3)), true)
			for k in 7:
				var x := -0.75 + k * 0.25
				var hgt := 0.4 + (1.0 - absf(k - 3) / 3.0) * 0.6
				_prop(out, _rect_poly(Rect2(c.x + (x - 0.065) * r, c.y - (0.95 + hgt) * r, r * 0.13, r * hgt)), true)
				_dot(out, c + Vector2(x, -0.95 - hgt) * r, r * 0.07, true)
			out["body"] = _u(c, r, [-2.1, B, -2.05, 1.75, -1.55, 1.4, -0.78, 1.35, -0.78, 1.02, 0.78, 1.02, 0.78, 1.35, 1.55, 1.4, 2.05, 1.75, 2.1, B])
			for k in 4:
				var y := 1.1 + k * 0.07
				_detail(out, _u(c, r, [-0.6, y, 0.6, y]), 0.03, 0.55, false)
			var n: int = [5, 3, 7][vs]
			var eyes := []
			for k in n:
				var x: float = -0.7 + (1.4 / n) * (k + 0.5)
				eyes.append(_rect_poly(Rect2(c.x + (x - 0.7 / n) * r + r * 0.02, c.y - r * 0.16, r * (1.4 / n - 0.04), r * 0.24)))
			out["eyes"] = eyes
			out["hair"] = PackedVector2Array() if hs % 2 == 0 else _u(c, r, [-0.86, -0.05, -0.92, -0.65, -0.78, -0.72, -0.72, -0.1])
		&"botnet":
			# A halo of small drones circling above the head on a tilted ring.
			var hc := c + Vector2(0, -1.4) * r
			var ring := _ellipse(hc, r * 1.55, r * 0.36, 28)
			ring.append(ring[0])
			_detail(out, ring, 0.05, 0.55, true)
			for k in 5:
				var a := TAU * k / 5.0 + 0.3
				var p := hc + Vector2(cos(a) * 1.55, sin(a) * 0.36) * r
				_prop(out, _u(p, r, [-0.26, 0.0, 0.0, -0.14, 0.26, 0.0, 0.0, 0.14]), true)
				_detail(out, _u(p, r, [-0.34, -0.18, -0.12, -0.18]), 0.05, 0.8, true)
				_detail(out, _u(p, r, [0.12, -0.18, 0.34, -0.18]), 0.05, 0.8, true)
				_dot(out, p, r * 0.06, true)
			out["body"] = _u(c, r, [-2.0, B, -1.9, 1.85, -1.5, 1.45, 1.5, 1.45, 1.9, 1.85, 2.0, B])
			_prop(out, _stroke(_u(c, r, [1.2, 1.5, 1.35, 0.95]), r * 0.1), false)
			out["hair"] = [PackedVector2Array(), _crop_hair(c, r, 2), _crop_hair(c, r, 3), _crop_hair(c, r, 0)][hs]
		&"hivemind":
			# A linked-node headset: a band over the head, three stalks ending in nodes
			# linked into one web, and discs at the temples; a hex-plate collar.
			var nodes := [c + Vector2(-1.15, -1.45) * r, c + Vector2(0, -1.92) * r, c + Vector2(1.15, -1.45) * r]
			var band := PackedVector2Array()
			for k in 13:
				var a := PI + PI * k / 12.0
				band.append(c + Vector2(cos(a) * 0.98, sin(a) * 1.08) * r)
			_detail(out, band, 0.12, 0.8, true)
			var roots := [c + Vector2(-0.7, -0.75) * r, c + Vector2(0, -1.08) * r, c + Vector2(0.7, -0.75) * r]
			for k in 3:
				_prop(out, _stroke(PackedVector2Array([roots[k], nodes[k]]), r * 0.12), true)
				_prop(out, _ellipse(nodes[k], r * 0.24, r * 0.24, 12), true)
				_dot(out, nodes[k], r * 0.1, true)
			for pair in [[0, 1], [1, 2], [0, 2]]:
				_detail(out, PackedVector2Array([nodes[pair[0]], nodes[pair[1]]]), 0.04, 0.6, true)
			_prop(out, _ellipse(c + Vector2(-0.98, 0.0) * r, r * 0.26, r * 0.26, 12), true)
			_prop(out, _ellipse(c + Vector2(0.98, 0.0) * r, r * 0.26, r * 0.26, 12), true)
			out["body"] = _u(c, r, [-2.0, B, -1.95, 1.8, -1.55, 1.4, -0.7, 1.4, -0.45, 1.1, 0.45, 1.1, 0.7, 1.4, 1.55, 1.4, 1.95, 1.8, 2.0, B])
			for k in 3:
				var hx := -0.5 + k * 0.5
				var hex := PackedVector2Array()
				for q in 7:
					var a := TAU * q / 6.0
					hex.append(c + (Vector2(hx, 1.95) + Vector2(cos(a), sin(a)) * 0.22) * r)
				_detail(out, hex, 0.04, 0.55, false)
	var eb := Rect2()
	for i in (out["eyes"] as Array).size():
		var bb := _bounds(out["eyes"][i])
		eb = bb if i == 0 else eb.merge(bb)
	out["visor"] = eb


static func _bounds(pts: PackedVector2Array) -> Rect2:
	var b := Rect2(pts[0], Vector2.ZERO)
	for p in pts:
		b = b.expand(p)
	return b


## The expression (ART_BIBLE 7.1): poses the head (turn and shift round the neck), squints
## or crosses out the eyes, sets the mouth, and adds the hurt crack and scratches or the
## triumphant fist.
static func _expression(out: Dictionary, rect: Rect2, subj: Dictionary) -> void:
	var e: int = subj.get("expression", Expr.NEUTRAL)
	var c: Vector2 = out["c"]
	var r: float = out["r"]
	var pose: Array = POSE.get(e, POSE[Expr.NEUTRAL])
	# The mouth, in the head's frame.
	match e:
		Expr.HURT:
			out["mouth"] = _u(c, r, [-0.3, 0.55, -0.15, 0.48, 0.0, 0.58, 0.15, 0.47, 0.3, 0.56])
			out["scars"].append([c + Vector2(-0.8, -0.3) * r, c + Vector2(0.25, 0.1) * r])
			out["scars"].append([c + Vector2(0.25, 0.1) * r, c + Vector2(0.05, 0.28) * r])
			out["hurt"] = [[c + Vector2(0.45, 0.25) * r, c + Vector2(0.7, 0.55) * r], [c + Vector2(0.58, 0.2) * r, c + Vector2(0.8, 0.46) * r]]
		Expr.TRIUMPHANT:
			var grin := PackedVector2Array()
			for k in 7:
				var a := PI * 0.15 + PI * 0.7 * k / 6.0
				grin.append(c + Vector2(cos(a) * 0.34, 0.38 + sin(a) * 0.2) * r)
			out["mouth"] = grin
			out["glow"] = true
			# A fist raised at the lower right, beside the shoulder.
			var fc := c + Vector2(1.75, 1.35) * r
			_prop(out, PackedVector2Array([fc + Vector2(-0.12, 0.25) * r, fc + Vector2(0.3, 0.25) * r,
				Vector2(fc.x + r * 0.5, rect.end.y), Vector2(fc.x + r * 0.05, rect.end.y)]), false)
			_prop(out, _box(fc, Vector2(0.36, 0.32) * r, 0.6), false)
			for k in 3:
				_detail(out, _u(fc, r, [-0.3 + k * 0.2, -0.3, -0.3 + k * 0.2, -0.05]), 0.05, 0.7, false)
		Expr.FLATLINED:
			out["mouth"] = _u(c, r, [-0.26, 0.55, 0.26, 0.55])
			var cross := []
			for sx in [-0.36, 0.36]:
				var ec := c + Vector2(sx, -0.05) * r
				cross.append([ec + Vector2(-0.14, -0.12) * r, ec + Vector2(0.14, 0.12) * r])
				cross.append([ec + Vector2(-0.14, 0.12) * r, ec + Vector2(0.14, -0.12) * r])
			out["cross"] = cross
			out["eyes"] = []
		_:
			out["mouth"] = _u(c, r, [-0.18, 0.55, 0.18, 0.55])
	# Squint: the eyes flatten about their own centres.
	var squint: float = pose[2]
	if squint != 1.0:
		var squashed := []
		for p in out["eyes"]:
			var b := _bounds(p)
			var m := Transform2D().translated(-b.get_center()).scaled(Vector2(1.0, squint)).translated(b.get_center())
			squashed.append(m * (p as PackedVector2Array))
		out["eyes"] = squashed
	var turn: float = pose[0]
	var shift: Vector2 = pose[1]
	if turn == 0.0 and shift == Vector2.ZERO:
		return
	var neck := c + Vector2(0, 1.1) * r
	var t := Transform2D().translated(-neck).rotated(deg_to_rad(turn)).translated(neck + shift * r)
	for part in ["head", "hair", "mouth", "mask", "face"]:
		out[part] = t * (out[part] as PackedVector2Array)
	var eyes := []
	for p in out["eyes"]:
		eyes.append(t * (p as PackedVector2Array))
	out["eyes"] = eyes
	out["visor"] = t * (out["visor"] as Rect2)
	for pr in out["props"]:
		if pr["h"]:
			pr["p"] = t * (pr["p"] as PackedVector2Array)
	for d in out["details"]:
		if d["h"]:
			d["p"] = t * (d["p"] as PackedVector2Array)
	for d in out["dots"]:
		if d["h"]:
			d["at"] = t * (d["at"] as Vector2)
	for key in ["scars", "hurt", "cross"]:
		var moved := []
		for seg in out.get(key, []):
			moved.append([t * (seg[0] as Vector2), t * (seg[1] as Vector2)])
		out[key] = moved


## Fills `pts`, clipped to the portrait's rect while one is drawn (a pose or a prop never
## paints onto the Polaroid's frame).
static func _poly(ci: CanvasItem, pts: PackedVector2Array, col: Color) -> void:
	if pts.size() < 3:
		return
	if _clip.has_area() and not _clip.encloses(_bounds(pts)):
		for q in Geometry2D.intersect_polygons(pts, _rect_poly(_clip)):
			if q.size() >= 3:
				ci.draw_colored_polygon(q, col)
		return
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


## The corp pattern over an enemy's body (ART_BIBLE 7.2, 3.6): none for operatives.
static func _pattern_body(ci: CanvasItem, rect: Rect2, subj: Dictionary, s: Dictionary, col: Color) -> void:
	var kind: int = subj.get("pattern", CorpPattern.Kind.NONE)
	if kind == CorpPattern.Kind.NONE:
		return
	var ps := clampf(rect.size.x / PATTERN_REF, PATTERN_SCALE_MIN, 1.0)
	var body: PackedVector2Array = s["body"]
	if body.size() >= 3:
		CorpPattern.fill_polygon(ci, body, kind, col, ps)


## A boss's halo: a ring behind the head filled with its corp pattern (the boss reads by
## pattern as well as hue, §3.6).
static func boss_halo(ci: CanvasItem, rect: Rect2, subj: Dictionary, s: Dictionary, col: Color) -> void:
	var kind: int = subj.get("pattern", CorpPattern.Kind.NONE)
	if kind == CorpPattern.Kind.NONE:
		return
	var r: float = s["r"]
	CorpPattern.fill_ring(ci, s["c"], r * 1.6, r * 1.9, kind, col, clampf(rect.size.x / PATTERN_REF, PATTERN_SCALE_MIN, 1.0))


## The pattern kind a subject's portrait carries (the corp's; NONE for operatives).
static func pattern_of(subj: Dictionary) -> int:
	return subj.get("pattern", CorpPattern.Kind.NONE)


## Draws the figure's parts that every style shares: props rimmed, details, dots, scars,
## mouth and the expression marks, in `tint` (already greyed when flatlined).
static func _figure_marks(ci: CanvasItem, subj: Dictionary, s: Dictionary, tint: Color, ink: Color) -> void:
	var r: float = s["r"]
	for d in s["details"]:
		var p: PackedVector2Array = d["p"]
		if p.size() >= 2:
			ci.draw_polyline(p, Color(tint, float(d["a"])), maxf(1.0, r * float(d["w"])), true)
	for d in s["dots"]:
		ci.draw_circle(d["at"], maxf(1.0, float(d["r"])), tint)
	for seg in s["scars"]:
		ci.draw_line(seg[0], seg[1], ink, maxf(1.0, r * 0.07), true)
	for seg in s.get("hurt", []):
		ci.draw_line(seg[0], seg[1], _k(subj, Palette.HARM), maxf(1.0, r * 0.07), true)
	var mouth: PackedVector2Array = s["mouth"]
	if mouth.size() >= 2:
		ci.draw_polyline(mouth, Color(tint, 0.8), maxf(1.0, r * 0.06), true)
	for seg in s.get("cross", []):
		ci.draw_line(seg[0], seg[1], tint, maxf(1.2, r * 0.08), true)


## Flatlined (ART_BIBLE 7.1, 11 FLATLINED): a dim wash and a heart-monitor line that
## blips once and goes flat.
static func _flatline(ci: CanvasItem, rect: Rect2) -> void:
	ci.draw_rect(rect, Color(Palette.INK, FLAT_DIM))
	var y := rect.position.y + rect.size.y * FLAT_LINE_Y
	var x0 := rect.position.x
	var w := rect.size.x
	var h := rect.size.y
	var line := PackedVector2Array([Vector2(x0, y), Vector2(x0 + w * 0.16, y), Vector2(x0 + w * 0.2, y - h * FLAT_BLIP),
		Vector2(x0 + w * 0.24, y + h * FLAT_BLIP * 0.6), Vector2(x0 + w * 0.28, y), Vector2(rect.end.x, y)])
	ci.draw_polyline(line, Palette.TEXT_MID, maxf(1.5, w * 0.022), true)


# --- Style 0: NEON BUST ---------------------------------------------------------------------

static func _neon(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint := _k(subj, subj["tint"])
	var top := _k(subj, Palette.NIGHT_SKY)
	var bottom := tint.darkened(0.5)
	ci.draw_polygon(_rect_poly(rect), PackedColorArray([top, top, bottom, bottom]))
	for k in 6:
		var y := rect.position.y + rect.size.y * (0.1 + k * 0.16)
		ci.draw_line(Vector2(rect.position.x, y), Vector2(rect.end.x, y), Color(tint, 0.08), 1.0)
	var s := shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.78, 0.22), rect.size.x * 0.14, subj["key"], Color(tint, 0.6))
	if kind == Kind.BOSS:
		boss_halo(ci, rect, subj, s, Color(tint, PATTERN_ALPHA))
		ci.draw_arc(c, r * 1.9, 0, TAU, 48, Color(tint, 0.35), 3.0, true)
		ci.draw_arc(c, r * 1.9, 0, TAU, 48, Color(tint, 0.9), 1.2, true)
	var body := _k(subj, FIGURE)
	var rim_w := maxf(1.0, r * 0.05)
	_poly(ci, s["body"], body)
	_pattern_body(ci, rect, subj, s, Color(tint, PATTERN_ALPHA))
	for pr in s["props"]:
		if not pr["h"]:
			_poly(ci, pr["p"], body)
			_outline(ci, pr["p"], Color(tint, 0.7), rim_w)
	if s.get("hair_under", false):
		_poly(ci, s["hair"], body.lightened(FIGURE_LIFT))
		_outline(ci, s["hair"], Color(tint, 0.6), rim_w)
	_poly(ci, s["head"], body)
	_poly(ci, s["face"], body.lightened(FIGURE_LIFT))
	if not s.get("hair_under", false):
		_poly(ci, s["hair"], body.lightened(FIGURE_LIFT))
		_outline(ci, s["hair"], Color(tint, 0.55), rim_w)
	for pr in s["props"]:
		if pr["h"]:
			_poly(ci, pr["p"], body)
			_outline(ci, pr["p"], Color(tint, 0.75), rim_w)
	_poly(ci, s["mask"], Color(tint, 0.3))
	_outline(ci, s["mask"], Color(tint, 0.7), rim_w)
	_poly(ci, s["tie"], Color(tint, 0.8))
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], Color(tint, 0.85), maxf(1.2, r * 0.07), true)
	# Rim light down the lit side.
	ci.draw_arc(c, r * 0.98, -PI * 0.45, PI * 0.35, 16, Color(tint, 0.9), maxf(1.2, r * 0.08), true)
	var b: PackedVector2Array = s["body"]
	ci.draw_line(b[b.size() - 2], b[b.size() - 1], Color(tint, 0.7), maxf(1.2, r * 0.07), true)
	if kind == Kind.MACHINE:
		var lens: float = s["lens"]
		ci.draw_circle(c, lens * 1.25, Color(tint, 0.25))
		ci.draw_circle(c, lens, Color(tint, 0.95))
		ci.draw_circle(c, lens * 0.45, body)
		ci.draw_circle(c + Vector2(-lens * 0.3, -lens * 0.3), lens * 0.15, Color(_k(subj, LIGHT), 0.8))
		_outline(ci, s["head"], Color(tint, 0.6), maxf(1.0, r * 0.05))
	else:
		var glow := 0.25 if not s.get("glow", false) else 0.45
		for p in s["eyes"]:
			var grown := Geometry2D.offset_polygon(p, r * (0.06 if not s.get("glow", false) else 0.14))
			if grown.size() > 0:
				_poly(ci, grown[0], Color(tint, glow))
			_poly(ci, p, Color(tint, 0.95))
	_figure_marks(ci, subj, s, tint, body.lightened(0.02))


# --- Style 1: XEROX ZINE --------------------------------------------------------------------

static func _xerox(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint := _k(subj, subj["tint"])
	var paper := _k(subj, Palette.PAPER.darkened(0.05))
	var ink := _k(subj, Palette.INK)
	ci.draw_rect(rect, paper)
	# Photocopier streaks and a halftone wash toward the bottom.
	for k in 5:
		var x := rect.position.x + rect.size.x * _h(subj["key"], 20 + k)
		ci.draw_line(Vector2(x, rect.position.y), Vector2(x + 2, rect.end.y), Color(ink, 0.06), 1.0 + k % 2)
	var step := maxf(3.0, rect.size.x / 28.0)
	var y := rect.position.y + step * 0.5
	while y < rect.end.y:
		var x := rect.position.x + step * 0.5 + (step * 0.5 if int(y / step) % 2 == 1 else 0.0)
		var t := (y - rect.position.y) / rect.size.y
		while x < rect.end.x:
			ci.draw_circle(Vector2(x, y), step * 0.42 * t, Color(ink, 0.35))
			x += step
		y += step
	var s := shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.78, 0.22), rect.size.x * 0.14, subj["key"], Color(ink, 0.7))
	for p in silhouette_polygons(rect, subj):
		_poly(ci, p, ink)
	_poly(ci, s["face"], ink.lightened(0.12))
	# The corp's pattern printed over an enemy's body in its hue.
	_pattern_body(ci, rect, subj, s, Color(tint, 0.85))
	_poly(ci, s["mask"], Color(paper, 0.85))
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], ink, maxf(1.5, r * 0.09), true)
	# Paper highlight on the face.
	ci.draw_arc(c + Vector2(-r * 0.1, 0), r * 0.7, PI * 0.6, PI * 1.3, 12, Color(paper, 0.7), maxf(1.0, r * 0.1), true)
	if kind == Kind.MACHINE:
		var lens: float = s["lens"]
		ci.draw_circle(c, lens, paper)
		ci.draw_circle(c, lens * 0.5, ink)
	elif not (s["eyes"] as Array).is_empty():
		# The Cell's marker censor bar over the eyes, in the owner's colour.
		var v: Rect2 = s["visor"]
		var bar := PackedVector2Array([v.position + Vector2(-r * 0.25, r * 0.08), Vector2(v.end.x + r * 0.3, v.position.y - r * 0.05), Vector2(v.end.x + r * 0.25, v.end.y + r * 0.05), Vector2(v.position.x - r * 0.3, v.end.y + r * 0.12)])
		_poly(ci, bar, tint)
	_figure_marks(ci, subj, s, paper, tint)
	if kind == Kind.BOSS:
		# Marker crown scrawl.
		var cr := PackedVector2Array([c + Vector2(-r * 0.8, -r * 1.25), c + Vector2(-r * 0.5, -r * 1.7), c + Vector2(-r * 0.2, -r * 1.3), c + Vector2(0, -r * 1.8), c + Vector2(r * 0.2, -r * 1.3), c + Vector2(r * 0.5, -r * 1.7), c + Vector2(r * 0.8, -r * 1.25)])
		ci.draw_polyline(cr, tint, maxf(2.0, r * 0.12), true)
	# Tape strip.
	ci.draw_rect(Rect2(rect.position + Vector2(rect.size.x * 0.3, -rect.size.y * 0.02), Vector2(rect.size.x * 0.4, rect.size.y * 0.08)), Color(Palette.NOTE_TAPE, 0.85))


# --- Style 2: WIRE SCAN ---------------------------------------------------------------------

static func _wire(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint := _k(subj, subj["tint"])
	var grid := _k(subj, Palette.NET_CYAN)
	var hot := _k(subj, Palette.CELL_ACID)
	ci.draw_rect(rect, _k(subj, WIRE_BACK))
	var step := rect.size.x / 10.0
	for k in 11:
		ci.draw_line(Vector2(rect.position.x + k * step, rect.position.y), Vector2(rect.position.x + k * step, rect.end.y), Color(grid, 0.07), 1.0)
		ci.draw_line(Vector2(rect.position.x, rect.position.y + k * step), Vector2(rect.end.x, rect.position.y + k * step), Color(grid, 0.07), 1.0)
	var s := shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	var w := maxf(1.0, r * 0.05)
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.78, 0.22), rect.size.x * 0.14, subj["key"], Color(tint, 0.7))
	_poly(ci, s["head"], Color(tint, 0.08))
	_poly(ci, s["body"], Color(tint, 0.06))
	_pattern_body(ci, rect, subj, s, Color(tint, PATTERN_ALPHA * 0.6))
	# Contour rings round the head and a meridian mesh.
	for k in 5:
		var t := -0.7 + k * 0.35
		var hw := r * 0.86 * sqrt(maxf(0.0, 1.0 - t * t))
		ci.draw_line(Vector2(c.x - hw, c.y + t * r), Vector2(c.x + hw, c.y + t * r), Color(tint, 0.5), w, true)
	_outline(ci, s["head"], tint, w * 1.6)
	_outline(ci, s["hair"], Color(tint, 0.8), w * 1.2)
	for pr in s["props"]:
		_poly(ci, pr["p"], Color(tint, 0.1))
		_outline(ci, pr["p"], tint, w * 1.3)
	_outline(ci, s["mask"], tint, w * 1.2)
	var b: PackedVector2Array = s["body"]
	ci.draw_polyline(b, tint, w * 1.6, true)
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], tint, w * 1.4, true)
	if kind == Kind.MACHINE:
		ci.draw_arc(c, s["lens"], 0, TAU, 24, hot, w * 2.0, true)
		ci.draw_circle(c, float(s["lens"]) * 0.3, hot)
	else:
		for p in s["eyes"]:
			_poly(ci, p, Color(hot, 0.85))
	_figure_marks(ci, subj, s, tint, Color(tint, 0.5))
	# Scan line and corner brackets.
	var sy := rect.position.y + rect.size.y * (0.3 + _h(subj["key"], 9) * 0.4)
	ci.draw_line(Vector2(rect.position.x, sy), Vector2(rect.end.x, sy), Color(hot, 0.5), 1.0)
	var bk := rect.size.x * 0.12
	for corner in [rect.position, Vector2(rect.end.x, rect.position.y), rect.end, Vector2(rect.position.x, rect.end.y)]:
		var dx := bk if corner.x == rect.position.x else -bk
		var dy := bk if corner.y == rect.position.y else -bk
		var p: Vector2 = corner + Vector2(signf(dx), signf(dy)) * 3.0
		ci.draw_line(p, p + Vector2(dx, 0), grid, 1.5)
		ci.draw_line(p, p + Vector2(0, dy), grid, 1.5)
	if kind == Kind.BOSS:
		ci.draw_arc(c, r * 1.8, -PI * 0.9, -PI * 0.1, 24, _k(subj, Palette.HARM), 2.0, true)


# --- Style 3: MUGSHOT -----------------------------------------------------------------------

static func _mugshot(ci: CanvasItem, rect: Rect2, subj: Dictionary) -> void:
	var tint := _k(subj, subj["tint"])
	var light := _k(subj, LIGHT)
	var dark := _k(subj, FIGURE)
	ci.draw_rect(rect, _k(subj, MUG_BACK))
	# Height chart.
	var rows := 8
	for k in rows:
		var y := rect.position.y + rect.size.y * (k + 0.5) / rows
		ci.draw_line(Vector2(rect.position.x, y), Vector2(rect.end.x, y), Color(light, 0.14 if k % 2 == 0 else 0.07), 1.0)
	# Harsh flash: a pale disc behind the head.
	var s := shapes(rect, subj)
	var kind: int = subj["kind"]
	var c: Vector2 = s["c"]
	var r: float = s["r"]
	ci.draw_circle(c + Vector2(r * 0.3, -r * 0.2), r * 1.6, Color(light, 0.06))
	if kind == Kind.CORP:
		_emblem(ci, rect.position + rect.size * Vector2(0.8, 0.2), rect.size.x * 0.12, subj["key"], Color(tint, 0.5))
	# Glitch split: the silhouette offset in pink and cyan, then the dark figure.
	var sil := silhouette_polygons(rect, subj)
	for pass_n in 3:
		var off: Vector2 = [Vector2(-r * 0.07, 0), Vector2(r * 0.07, 0), Vector2.ZERO][pass_n]
		var col: Color = [Color(_k(subj, Palette.CELL_PINK), 0.55), Color(_k(subj, Palette.NET_CYAN), 0.55), dark][pass_n]
		for pts in sil:
			_poly(ci, Transform2D().translated(off) * pts, col)
	_pattern_body(ci, rect, subj, s, Color(tint, PATTERN_ALPHA))
	_poly(ci, s["mask"], Color(tint, 0.35))
	for e in s["extras"]:
		ci.draw_line(e[0], e[1], dark, maxf(1.5, r * 0.09), true)
	_poly(ci, s["tie"], Color(tint, 0.7))
	if kind == Kind.MACHINE:
		ci.draw_circle(c, s["lens"], Color(tint, 0.9))
		ci.draw_circle(c, float(s["lens"]) * 0.4, dark)
	else:
		for p in s["eyes"]:
			_poly(ci, p, Color(tint, 0.9))
	_figure_marks(ci, subj, s, tint, Color(light, 0.35))
	# Placard (the name is on the placard only when the portrait is large enough to read).
	var pl := Rect2(rect.position.x + rect.size.x * 0.14, rect.end.y - rect.size.y * 0.2, rect.size.x * 0.72, rect.size.y * 0.15)
	ci.draw_rect(pl, _k(subj, Palette.INK))
	ci.draw_rect(pl, Color(light, 0.6), false, 1.0)
	var fs := UiTheme.font_px(UiTheme.CAPTION)
	if pl.size.y >= fs:
		ci.draw_string(Palette.mono(), pl.position + Vector2(3, pl.size.y * 0.5 + fs * 0.35), String(subj.get("name", "")).to_upper(), HORIZONTAL_ALIGNMENT_CENTER, pl.size.x - 6, fs, Color(light, 0.9))
	if kind == Kind.BOSS:
		ci.draw_rect(Rect2(rect.position + Vector2(4, 4), Vector2(rect.size.x * 0.4, rect.size.y * 0.1)), _k(subj, Palette.HARM))
