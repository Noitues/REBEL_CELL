class_name TideRaidLayer
extends Control
## Phase 3: the Infected Tide raid drawn on the city map (a CityMapOverlay over the 3D city at the RAID band). The raid lines run as
## paths over the real network edges (RaidMapAnchor.street), typed by color and shape (D triangle, N square, E circle); sentries
## stand on Sites; the INFECTED Sites and their neighbours carry the Bloom front tint; the HOME and Genome Core ends are marked, with
## the worst tier of each route at HOME. A view: it draws the description the screen gives it and decides nothing.
##
## Look for the art-pass: the front tint is a flat translucent disk (the Bloom look API of CityView3D is the netrun street's, it does not
## apply to the City Grid map).

const LINE_W := 3.0
const DONE_ALPHA := 0.25
const DASH_ON := 10.0
const DASH_OFF := 7.0
const FRONT_R := 30.0
const INFECT_R := 22.0
const HOME_GLYPH_R := 11.0
const CAND_LETTERS: Array[String] = ["A", "B", "C"]
const INFECT_COL := Palette.TIDE_INFECT_FILL
const FRONT_COL := Palette.TIDE_FRONT_FILL
const TAKEN_COL := Palette.TIDE_TAKEN_FILL
const INK_ALPHA := 0.7
const SMALL_PX := 12
const LABEL_PX := 13

var overlay: CityMapOverlay = null
var core: StringName = &""
var home: StringName = &""
## Beams to draw: {cells (Site ids in scan order), type, role ("known" | "cand" | "hunter"), label, alpha, dashed, width, current, ghost}.
var beams: Array[Dictionary] = []
## site -> [type, verb] for the sentries now standing.
var sentries: Dictionary = {}
## Sites that are INFECTED (a wound card names them), the neighbours of those (the front), the TAKEN Sites.
var infected: Array[StringName] = []
var front: Array[StringName] = []
var taken: Array[StringName] = []
## Persistent hit marks: site -> "hit" | "block". The block markers show for the current beam only (see `blocks`).
var hits: Dictionary = {}
var blocks: Array = []
## The worst tier of each candidate route at HOME (empty: none), drawn at HOME.
var home_tiers: Array = []
var ghost_home: bool = false
var hovered: StringName = &""
## The response being previewed (hovered or picked): [] or its response array, drawn as a ghost on the map.
var preview: Array = []
var preview_type: String = ""
const SENTRY_SCALE := 1.3
const GHOST_ALPHA := 0.7
var _font: Font = null


func _init() -> void:
	name = "TideRaidLayer"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_font = ThemeDB.fallback_font


func _process(_delta: float) -> void:
	queue_redraw()


## Site `id`'s point in this layer's px (INF off the map).
func at(id: StringName) -> Vector2:
	var p := RaidMapAnchor.site(overlay, id)
	if p.x == INF:
		return Vector2.INF
	return get_global_transform().affine_inverse() * p


## The path of `cells` (core first for a route, HOME last) over the map's streets, in this layer's px.
func path(ids: Array) -> PackedVector2Array:
	var pts := PackedVector2Array()
	if overlay == null:
		return pts
	var inv := get_global_transform().affine_inverse()
	for i in ids.size() - 1:
		var seg := RaidMapAnchor.street(overlay, StringName(String(ids[i])), StringName(String(ids[i + 1])))
		for q in seg:
			var l: Vector2 = inv * q
			if pts.is_empty() or pts[pts.size() - 1].distance_to(l) > 0.5:
				pts.append(l)
	if pts.is_empty() and ids.size() == 1:
		var p := at(StringName(String(ids[0])))
		if p.x != INF:
			pts.append(p)
	return pts


func _beam_ids(b: Dictionary) -> Array:
	var ids: Array = []
	if bool(b.get("route", false)):
		ids.append(core)
	ids.append_array(b["cells"])
	if bool(b.get("home", false)):
		ids.append(home)
	return ids


func _draw() -> void:
	if overlay == null or not is_instance_valid(overlay):
		return
	_draw_tints()
	for b in beams:
		_draw_beam(b)
	_draw_hits()
	_draw_sentries()
	_draw_home()
	_draw_preview()


func _draw_tints() -> void:
	for id in front:
		var p := at(id)
		if p.x != INF:
			draw_circle(p, FRONT_R, FRONT_COL)
	for id in taken:
		var p := at(id)
		if p.x != INF:
			draw_circle(p, FRONT_R * 0.8, TAKEN_COL)
	for id in infected:
		var p := at(id)
		if p.x != INF:
			draw_circle(p, INFECT_R, INFECT_COL)
			draw_arc(p, INFECT_R, 0.0, TAU, 24, Palette.TIDE_INFECT_EDGE, 1.5)
			TideGlyphs.crack(self, p, 9.0, Palette.TIDE_INFECT_CRACK, 1.5)


func _draw_beam(b: Dictionary) -> void:
	var pts := path(_beam_ids(b))
	if pts.size() < 2:
		return
	var col := TideGlyphs.type_color(String(b["type"]))
	var a := float(b.get("alpha", 1.0))
	col.a = a
	var w := float(b.get("width", LINE_W))
	var ink := Color(TideGlyphs.BLACK, INK_ALPHA * a)
	if bool(b.get("dashed", false)):
		_dashed(pts, ink, w + 2.0)
		_dashed(pts, col, w)
	else:
		draw_polyline(pts, ink, w + 2.0)
		draw_polyline(pts, col, w)
	# The head: the type shape at the start, an arrowhead at the end, the label beside the head.
	var start := pts[0]
	TideGlyphs.type_shape(self, start, String(b["type"]), 7.0, col)
	var d := (pts[pts.size() - 1] - pts[pts.size() - 2]).normalized()
	var tip := pts[pts.size() - 1] - d * 14.0
	var n := Vector2(-d.y, d.x)
	draw_colored_polygon(PackedVector2Array([tip + d * 9.0, tip - n * 5.0, tip + n * 5.0]), col)
	var lab := String(b.get("label", ""))
	if lab != "":
		var mid := pts[mini(pts.size() - 1, 1)] + Vector2(8.0, -8.0)
		draw_string(_font, mid + Vector2(1, 1), lab, HORIZONTAL_ALIGNMENT_LEFT, -1, LABEL_PX, Color(TideGlyphs.BLACK, a))
		draw_string(_font, mid, lab, HORIZONTAL_ALIGNMENT_LEFT, -1, LABEL_PX, Color(col, a).lightened(0.3))
	if String(b["role"]) == "hunter":
		TideGlyphs.hound(self, start + Vector2(0.0, -14.0), col)
	if bool(b.get("current", false)):
		draw_arc(start, 12.0, 0.0, TAU, 20, Color(TideGlyphs.INK, a), 2.0)


func _dashed(pts: PackedVector2Array, col: Color, w: float) -> void:
	var on := true
	var left := DASH_ON
	for i in pts.size() - 1:
		var a := pts[i]
		var b := pts[i + 1]
		var seg := a.distance_to(b)
		var dir := (b - a) / maxf(seg, 0.001)
		var t := 0.0
		while t < seg:
			var step := minf(left, seg - t)
			if on:
				draw_line(a + dir * t, a + dir * (t + step), col, w)
			t += step
			left -= step
			if left <= 0.001:
				on = not on
				left = DASH_ON if on else DASH_OFF


func _draw_hits() -> void:
	for id in hits:
		var p := at(id)
		if p.x == INF:
			continue
		TideGlyphs.xmark(self, p, 7.0, TideGlyphs.RED, 2.5)
	for e in blocks:
		var p := at(StringName(String(e[0])))
		if p.x == INF:
			continue
		draw_arc(p, 17.0, 0.0, TAU, 20, TideGlyphs.type_color(String(e[1])), 3.0)
		TideGlyphs.verb(self, p + Vector2(0, -24.0), "GUARD", 8.0, TideGlyphs.INK)


func _draw_sentries() -> void:
	for id in sentries:
		var p := at(id)
		if p.x == INF:
			continue
		var c: Array = sentries[id]
		TideGlyphs.sentry(self, p + Vector2(0.0, -24.0), String(c[0]), String(c[1]), SENTRY_SCALE)
		draw_line(p + Vector2(0.0, -9.0), p + Vector2(0.0, -9.0), TideGlyphs.INK, 1.0)


func _draw_home() -> void:
	var hp := at(home)
	if hp.x != INF:
		if ghost_home:
			TideGlyphs.ghost(self, hp, 24.0, TideGlyphs.COBALT_HOT)
		for i in home_tiers.size():
			var off := Vector2(-30.0 + 30.0 * i, 30.0)
			var tw := String(home_tiers[i])
			var c := hp + off
			draw_circle(c, HOME_GLYPH_R + 4.0, Color(TideGlyphs.BLACK, INK_ALPHA))
			TideGlyphs.tier(self, c, tw, HOME_GLYPH_R)
			draw_string(_font, c + Vector2(-4, HOME_GLYPH_R + 15.0), CAND_LETTERS[i], HORIZONTAL_ALIGNMENT_LEFT, -1, SMALL_PX, TideGlyphs.DIM)
	var cp := at(core)
	if cp.x != INF:
		draw_arc(cp, 26.0, 0.0, TAU, 28, TideGlyphs.COBALT_HOT, 2.0)


## A response's effect on the board as a ghost: DEPLOY a sentry dropping in, REDEPLOY an arrow from the source to the target, SACRIFICE a
## dome on HOME and a cobalt crumble on the district, JAM a struck-out hound on the hunter lanes.
func _draw_preview() -> void:
	if preview.is_empty():
		return
	var head := String(preview[0])
	var ghost_col := Color(TideGlyphs.GOLD, GHOST_ALPHA)
	match head:
		"DEPLOY":
			var p := at(StringName(preview[2]))
			if p.x != INF:
				TideGlyphs.sentry(self, p + Vector2(0.0, -24.0), String(preview[1]), "GUARD", SENTRY_SCALE)
				draw_arc(p, 20.0, 0.0, TAU, 20, ghost_col, 2.0)
		"REDEPLOY":
			var a := at(StringName(preview[1]))
			var b := at(StringName(preview[2]))
			if a.x != INF and b.x != INF:
				draw_line(a + Vector2(0.0, -24.0), b + Vector2(0.0, -24.0), ghost_col, 3.0)
				TideGlyphs.sentry(self, b + Vector2(0.0, -24.0), preview_type, "SHIFT", SENTRY_SCALE)
				draw_arc(b, 20.0, 0.0, TAU, 20, ghost_col, 2.0)
		"SACRIFICE":
			var s := at(StringName(preview[1]))
			if s.x != INF:
				draw_circle(s, FRONT_R, TAKEN_COL)
				draw_arc(s, 20.0, 0.0, TAU, 20, TideGlyphs.COBALT_HOT, 3.0)
			var h := at(home)
			if h.x != INF:
				draw_arc(h + Vector2(0.0, 6.0), 30.0, PI, TAU, 20, TideGlyphs.COBALT_HOT, 3.0)
		"JAM", "JAM_B":
			for b in beams:
				if String(b["role"]) == "hunter":
					var pts := path(_beam_ids(b))
					if pts.size() > 1:
						draw_line(pts[0] + Vector2(-12, -12), pts[0] + Vector2(12, 12), TideGlyphs.RED, 4.0)
