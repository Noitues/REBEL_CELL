class_name StreetRouteOverlay
extends Control
## NA-23b: the street netrun's overlay on `RouteRig`: the grease-pencil links (PIPELINE_SPEC 9.2: walked lime, option orange, ahead
## white dashes, past grey), the room frames, the vinyl stickers (9.3: type by shape; the three D4 kinds have provisional shapes),
## the option number chips, the operative token, the hover tag, the red-pencil TARGET circle and word, and the TARGET edge arrow
## (9.5b: arrow at or below half visible, with the visible part of the circle). Draws what the rules say; changes no game state.
## Wax stays clear of stickers, chips and the UI rects it is given (`avoid`): a link run that would touch them is not drawn.

const ART_DIR := "res://assets/netrun/route/"
const ART_OF := {"router": "router", "terminal": "terminal", "mainframe": "shop", "server_rack": "rack"}
const WORD_TARGET := "TARGET"
const TARGET_SHARE := 1.75
const TARGET_SQUASH := 0.86
const TARGET_FONT := 20
## Share of the TARGET word's width kept free round it by the safe-frame test (its -0.12 rad tilt, the pencil wobble).
const TARGET_WORD_PAD := 0.15
const HEAD_PX := 20.0
const SHAFT_PX := 64.0
const WORD_BACK := 30.0
const ARROW_SEED := 352
const LOOP_SEED := 211
const SAMPLE_PX := 4.0
const RING_W := 3.2
const KEYLINE_W := 3.0
const CHIP_FONT := 14
const TAG_FONT := 14
const GLOW_ALPHA := 0.18
const DIM_IDLE := 0.7

## The rig that gives the projections, the run data and the state (`current`, `visited`, `options`).
var rig: RouteRig = null
var data: StreetRouteData = null
var state: Dictionary = {"current": "", "visited": [], "options": []}
## The hovered node ("" = none), the selected one, and the tags to show (id -> text).
var focus: String = ""
var selected: String = ""
var tags: Dictionary = {}
## True while the legend is hovered: the whole graph lights (D7).
var lit_all := false
## The usable area (px in this control): the frame minus the HUD, legend and ROUTE window; the pencil clips to it and the arrow
## stands on its border. `avoid` are the UI rects the wax must keep clear of.
var usable: Rect2 = Rect2()
var avoid: Array[Rect2] = []
## The branch the hover lights (ids), set by the view.
var branch: Array = []
## HQ-LADDER-UI (the Solace ladder): id -> overlay kind for rooms with their own sticker (rest, mini-boss), id -> tower name
## (captioned over the rooms in play), and the "<from>><to>" keys of the ACROSS bridge links (drawn as pink dashes, never as UP).
var kind_overrides: Dictionary = {}
var tower_names: Dictionary = {}
var across_keys: Dictionary = {}
## The ACROSS bridge pencil, its dash (on, off in px at 1280) and the tower captions' font and colors.
const ACROSS_COLOR := Palette.CELL_PINK
const ACROSS_DASH: Array = [14.0, 7.0]
const TOWER_FONT := 15
const TOWER_COLORS := {"WARD": Palette.CORP_SOLACE, "BILLING": Palette.CRT_AMBER}

var _clip: Control = null
var _pencil: PencilSet = null
var _arrow_mark: GreasePencilMark = null
var _arrow_word: GreasePencilWord = null
var _arrow_on := false
var _arrow_k := 0.0
var _share := 1.0
var _stick_px: Dictionary = {}  # id -> Vector2
var _chip_rects: Dictionary = {}
var _art: Dictionary = {}
var _dirty := true
## NA-25: the entry sequence's staging. While `intro` is on, links write on by layer (`reveal_s` seconds into the REVEAL of
## `reveal_total` s; < 0 = none yet) and the stickers, rings, numbers and the TARGET circle come in over `mark_s` seconds into
## MARK (< 0 = none yet). Off, the overlay draws the whole route.
var intro := false
var reveal_s := -1.0
var reveal_total := 0.0
var mark_s := -1.0
var _intro_index: Dictionary = {}


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_clip = Control.new()
	_clip.name = "PencilClip"
	_clip.clip_contents = true
	_clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_clip)
	_pencil = PencilSet.under(_clip)
	_arrow_mark = GreasePencilMark.new()
	_arrow_mark.name = "Arrow"
	_arrow_mark.ink = GreasePencilMark.Ink.THREAT
	_arrow_mark.seed = ARROW_SEED
	_arrow_mark.auto_write = false
	add_child(_arrow_mark)
	_arrow_word = GreasePencilWord.new()
	_arrow_word.name = "ArrowWord"
	_arrow_word.ink = GreasePencilMark.Ink.THREAT
	_arrow_word.auto_write = false
	add_child(_arrow_word)
	_arrow_mark.visible = false
	_arrow_word.visible = false
	_arrow_word.text = CityMapOverlay.tr_word(WORD_TARGET)


## The overlay follows `p_rig`'s camera.
func bind(p_rig: RouteRig, p_data: StreetRouteData) -> void:
	rig = p_rig
	data = p_data
	rig.pose_changed.connect(mark_dirty)


## Redraw next frame.
func mark_dirty() -> void:
	_dirty = true


func _cfg() -> StreetRouteConfigData:
	return StreetRouteConfigData.shipped()


## Screen scale: px at the 1080 reference per px here.
func k() -> float:
	return size.y / float(_cfg().stickers["ref_h"])


func _process(delta: float) -> void:
	if rig == null or data == null:
		return
	var want := 1.0 if _arrow_on else 0.0
	var fade := float(_cfg().target["fade_s"])
	if _instant():
		_arrow_k = want
	elif not is_equal_approx(_arrow_k, want):
		_arrow_k = move_toward(_arrow_k, want, delta / maxf(fade, 0.001))
		_dirty = true
	if _dirty:
		_dirty = false
		queue_redraw()
		_lay_target()


func _instant() -> bool:
	return DisplayServer.get_name() == "headless" or Settings.reduce_effects


# --- Geometry ---------------------------------------------------------------------------------

## The sticker's centre of room `id`: on its left cut edge, `anchor.y` of the way down from the top (9.3 rule 2).
func sticker_pos(id: String) -> Vector2:
	var c := rig.room_corners_px(id)
	if c.size() < 4:
		return Vector2(INF, INF)
	var idx := [0, 1, 2, 3]
	idx.sort_custom(func(a: int, b: int) -> bool: return c[a].x < c[b].x)
	var left := [c[idx[0]], c[idx[1]]]
	left.sort_custom(func(a: Vector2, b: Vector2) -> bool: return a.y < b.y)
	var anchor: Array = _cfg().stickers["anchor"]
	return (left[0] as Vector2).lerp(left[1], float(anchor[1]))


## The sticker's outer reach in px.
func sticker_radius() -> float:
	return float(_cfg().stickers["radius_px"]) * k()


## The node under pixel `p` (a sticker first, then a room's front), "" when none. Ties go to the lowest id.
func node_at(p: Vector2) -> String:
	var ids: Array = data.rooms().keys()
	IdSort.sort_ids(ids)
	var r := sticker_radius()
	for id: String in ids:
		var s := sticker_pos(id)
		if s.is_finite() and s.distance_to(p) <= r:
			return id
	for id: String in ids:
		var c := rig.room_corners_px(id)
		if c.size() == 4 and Geometry2D.is_point_in_polygon(p, _ordered(c)):
			return id
	return ""


## The derive's front quad runs bottom, bottom, top, top around the room: already a ring.
static func _ordered(c: PackedVector2Array) -> PackedVector2Array:
	return PackedVector2Array([c[0], c[1], c[2], c[3]])


func _kind_of(id: String) -> String:
	return String(data.rooms()[id]["kind"])


func _elite(id: String) -> bool:
	for n: Dictionary in data.run_graph["nodes"]:
		if String(n["id"]) == id:
			return bool(n["elite"])
	return false


## The overlay kind of node `id` (CityMapOverlay.KIND_* for the four types, the D4 names otherwise).
func kind_name(id: String) -> String:
	if kind_overrides.has(id):
		return String(kind_overrides[id])
	match _kind_of(id):
		"router":
			return CityMapOverlay.KIND_ELITE if _elite(id) else CityMapOverlay.KIND_FIGHT
		"terminal":
			return CityMapOverlay.KIND_EVENT
		"mainframe":
			return CityMapOverlay.KIND_SHOP
		"server_rack":
			return CityMapOverlay.KIND_RACK
	return _kind_of(id)


func _node_state(id: String) -> String:
	return StreetRouteRules.node_state(data.run_graph, id, String(state["current"]), state["visited"], state["options"])


# --- Draw -------------------------------------------------------------------------------------

func _draw() -> void:
	if rig == null or data == null or rig.pose == null:
		return
	_stick_px.clear()
	_chip_rects.clear()
	var ids: Array = data.rooms().keys()
	IdSort.sort_ids(ids)
	var r := sticker_radius()
	var kk := k()
	_layout_stickers()
	var options: Array = state["options"]
	if not intro or EntryBeats.rings_on(mark_s) and mark_s >= 0.0:
		_draw_frames(ids, kk)
	_draw_links(kk, r)
	for id: String in ids:
		if not _stick_px.has(id):
			continue
		if not intro:
			_draw_sticker(id, _stick_px[id], r, kk)
			continue
		var sc := EntryBeats.slap_scale(_intro_idx(id), mark_s) if mark_s >= 0.0 else 0.0
		if sc > 0.0:
			var at: Vector2 = _stick_px[id]
			draw_set_transform(at * (1.0 - sc), 0.0, Vector2(sc, sc))
			_draw_sticker(id, at, r, kk)
			draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if not intro or mark_s >= 0.0 and EntryBeats.numbers_on(mark_s):
		for i in options.size():
			var oid := String(options[i])
			if _chip_rects.has(oid):
				_draw_chip(_chip_rects[oid], i + 1, kk)
		_draw_token(r, kk)
	if not intro:
		_draw_tower_names(kk, r)
		_draw_tags(kk, r)


## The sticker's place in the MARK's slap order: layer, then id (ties by id, never by dictionary order).
func _intro_idx(id: String) -> int:
	if _intro_index.is_empty():
		var ids: Array = data.rooms().keys()
		ids.sort_custom(func(a: String, b: String) -> bool:
			var la := StreetRouteRules.layer_of(data.run_graph, a)
			var lb := StreetRouteRules.layer_of(data.run_graph, b)
			return la < lb if la != lb else IdSort.less(a, b))
		for i in ids.size():
			_intro_index[String(ids[i])] = i
	return int(_intro_index.get(id, 0))


## The sticker centres and the option chip rects for the displayed pose.
func _layout_stickers() -> void:
	var ids: Array = data.rooms().keys()
	IdSort.sort_ids(ids)
	var r := sticker_radius()
	var kk := k()
	for id: String in ids:
		var s := sticker_pos(id)
		if s.is_finite():
			_stick_px[id] = s
	var options: Array = state["options"]
	for i in options.size():
		var oid := String(options[i])
		if _stick_px.has(oid):
			var c: Vector2 = _stick_px[oid]
			var cs := float(_cfg().stickers["chip_px"]) * kk
			_chip_rects[oid] = Rect2(Vector2(c.x - r - cs * 1.05, c.y - cs * 0.5), Vector2(cs, cs))


func _dim_of(id: String) -> float:
	var st := _node_state(id)
	if lit_all or branch.has(id) or id == focus or st == StreetRouteRules.STATE_WALKED or st == StreetRouteRules.STATE_NEXT:
		return 1.0
	return DIM_IDLE


func _draw_frames(ids: Array, kk: float) -> void:
	var cur := String(state["current"])
	var options: Array = state["options"]
	for id: String in ids:
		var c := rig.room_corners_px(id)
		if c.size() < 4:
			continue
		var col: Color
		var w := 3.0 * kk
		if id == cur:
			col = RouteInk.RING_WALKED
		elif options.has(id):
			col = RouteInk.RING_AVAILABLE
			w = 4.0 * kk
		elif lit_all or branch.has(id):
			col = Color(RouteInk.RING_UNAVAILABLE, 0.8)
			w = 2.0 * kk
		else:
			continue
		var ring := _ordered(c)
		ring.append(ring[0])
		draw_polyline(ring, Color(RouteInk.KEYLINE, 0.6), w + 2.0 * kk, true)
		draw_polyline(ring, col, w, true)


func _link_style(st: String) -> Dictionary:
	return _cfg().links[st]


func _draw_links(kk: float, r: float) -> void:
	for row: Dictionary in _collect_links(kk, r):
		var style: Dictionary = row["style"]
		var col: Color = row["color"]
		var width: float = float(style["width"]) * kk
		for run: PackedVector2Array in row["runs"]:
			if float(style["glow"]) > 0.0:
				draw_polyline(run, Color(col, GLOW_ALPHA * col.a), width * 3.0, true)
			var dash: Array = style["dash"]
			if dash.is_empty():
				draw_polyline(run, col, width, true)
			else:
				_dashes(run, col, width, float(dash[0]) * kk, float(dash[1]) * kk)


## Every link as the overlay draws it: `{key, state, style, color, runs}` in drawing order (past, ahead, walked, option), the
## runs being the pencil that stays clear of the stickers, the number chips and the avoided UI rects.
func _collect_links(kk: float, r: float) -> Array:
	var out: Array = []
	var cur := String(state["current"])
	var wob := float(_cfg().links["wobble_px"]) * kk
	var pad := float(_cfg().links["clear_pad_px"]) * kk
	var blocks: Array[Rect2] = []
	for id: String in _chip_rects:
		blocks.append((_chip_rects[id] as Rect2).grow(pad))
	var order := {StreetRouteRules.LINK_PAST: 0, StreetRouteRules.LINK_AHEAD: 1, StreetRouteRules.LINK_WALKED: 2, StreetRouteRules.LINK_OPTION: 3}
	var keyed: Array = []
	for e: Dictionary in (data.derive["edges"] as Array):
		var st := StreetRouteRules.link_state(data.run_graph, String(e["a"]), String(e["b"]), cur, state["visited"], state["options"])
		keyed.append([order[st], "%s>%s" % [e["a"], e["b"]], st, e])
	keyed.sort_custom(func(a: Array, b: Array) -> bool: return a[0] < b[0] if a[0] != b[0] else IdSort.less(a[1], b[1]))
	for row: Array in keyed:
		var e: Dictionary = row[3]
		var st: String = row[2]
		var style := _link_style(st)
		if across_keys.has(row[1]):
			style = style.duplicate()
			style["dash"] = ACROSS_DASH
			style["glow"] = maxf(float(style["glow"]), 0.5)
		var pts := PackedVector2Array()
		var ok := true
		for q: Array in e["path"]:
			var s := rig.to_screen(q)
			if not s.is_finite():
				ok = false
				break
			pts.append(s)
		if not ok or pts.size() < 2:
			continue
		var dim := 1.0
		if st == StreetRouteRules.LINK_AHEAD or st == StreetRouteRules.LINK_PAST:
			var lit := lit_all or (branch.has(String(e["a"])) and branch.has(String(e["b"])))
			dim = 1.0 if lit else DIM_IDLE
		var col := _color(style["color"], float(style["alpha"]) * dim)
		if across_keys.has(row[1]) and st != StreetRouteRules.LINK_WALKED:
			col = Color(ACROSS_COLOR, col.a)
		var rs := PencilShapes.resample(pts, SAMPLE_PX)
		if intro:
			var wk := EntryBeats.write_k(StreetRouteRules.layer_of(data.run_graph, String(e["b"])), int(data.run_graph["layers"]), reveal_total, reveal_s) 					if reveal_s >= 0.0 else 0.0
			if wk <= 0.0:
				continue
			rs = rs.slice(0, maxi(2, ceili(float(rs.size()) * wk)))
		var wobbled := PackedVector2Array()
		for i in rs.size():
			var j := _wobble(String(row[1]), i) * wob
			wobbled.append(rs[i] + Vector2(j, -j * 0.6))
		out.append({"key": row[1], "state": st, "style": style, "color": col, "runs": _runs_clear(wobbled, r + pad, blocks)})
	return out


## The link pencil as it is drawn now: each link's runs of points (px in this control). The wax-clear test reads them.
func link_runs() -> Array:
	var out: Array = []
	if rig == null or rig.pose == null:
		return out
	_stick_px.clear()
	_chip_rects.clear()
	_layout_stickers()
	for row: Dictionary in _collect_links(k(), sticker_radius()):
		for run: PackedVector2Array in row["runs"]:
			out.append(run)
	return out


static func _wobble(key: String, i: int) -> float:
	return float(hash([key, i]) % 2001) / 1000.0 - 1.0


static func _color(rgb: Array, alpha: float) -> Color:
	return Color(float(rgb[0]), float(rgb[1]), float(rgb[2]), alpha)


## The runs of `pts` that stay `reach` px off every sticker centre and out of every `blocks` rect and every avoided UI rect.
func _runs_clear(pts: PackedVector2Array, reach: float, blocks: Array[Rect2]) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	var cur := PackedVector2Array()
	for p in pts:
		var bad := false
		for id: String in _stick_px:
			if (_stick_px[id] as Vector2).distance_to(p) < reach:
				bad = true
				break
		if not bad:
			for b in blocks:
				if b.has_point(p):
					bad = true
					break
		if not bad:
			for u in avoid:
				if u.has_point(p):
					bad = true
					break
		if bad:
			if cur.size() >= 2:
				out.append(cur)
			cur = PackedVector2Array()
		else:
			cur.append(p)
	if cur.size() >= 2:
		out.append(cur)
	return out


func _dashes(pts: PackedVector2Array, col: Color, width: float, on: float, off: float) -> void:
	var carry := 0.0
	for q in pts.size() - 1:
		var a := pts[q]
		var b := pts[q + 1]
		var length := a.distance_to(b)
		if length <= 0.0:
			continue
		var dir := (b - a) / length
		var t := carry
		while t < length:
			var t1 := minf(t + on, length)
			if t1 > maxf(t, 0.0):
				draw_line(a + dir * maxf(t, 0.0), a + dir * t1, col, width)
			t += on + off
		carry = t - length


func _art_of(kind_id: String, past: bool) -> Texture2D:
	var node := String(ART_OF.get(_kind_to_type(kind_id), ""))
	if kind_id == CityMapOverlay.KIND_ELITE:
		node = "elite"
	if node == "":
		return null
	var name := "node_%s%s" % [node, "_past" if past else ""]
	if not _art.has(name):
		_art[name] = load(ART_DIR + name + ".png") as Texture2D
	return _art[name]


static func _kind_to_type(kind_id: String) -> String:
	match kind_id:
		CityMapOverlay.KIND_FIGHT:
			return "router"
		CityMapOverlay.KIND_EVENT:
			return "terminal"
		CityMapOverlay.KIND_SHOP:
			return "mainframe"
		CityMapOverlay.KIND_RACK:
			return "server_rack"
	return kind_id


func _draw_sticker(id: String, p: Vector2, r: float, kk: float) -> void:
	var st := _node_state(id)
	var dim := _dim_of(id)
	var ring_r := r - RING_W * 0.5 * kk
	var disc_r := r - (RING_W + 2.0 + 2.4) * kk
	var cut := disc_r + 2.4 * kk
	var ring_col := RouteInk.ring_of(st)
	var kind_id := kind_name(id)
	if st == StreetRouteRules.STATE_NEXT:
		draw_arc(p, ring_r, 0.0, TAU, 40, Color(ring_col, 0.28 * dim), 9.0 * kk)
	var tex := _art_of(kind_id, st == StreetRouteRules.STATE_CUT)
	if tex != null:
		var sz := Vector2(tex.get_width(), tex.get_height()) * (cut * 2.0 / maxf(1.0, float(tex.get_width())))
		draw_texture_rect(tex, Rect2(p - sz * 0.5, sz), false, Color(Palette.NO_TINT, dim * (0.75 if st == StreetRouteRules.STATE_CUT else 1.0)))
	else:
		_draw_d4(kind_id, p, cut, dim, kk)
	_ring(p, ring_r, st, kk, dim, ring_col)


## Provisional D4 stickers (9.3 rule 1): REST a crescent, WORKSHOP a hexagon, CACHE a notched crate square.
func _draw_d4(kind_id: String, p: Vector2, rr: float, dim: float, kk: float) -> void:
	draw_circle(p, rr, Color(RouteInk.KEYLINE, 0.9 * dim))
	draw_circle(p, rr - 2.4 * kk, Color(RouteInk.DIE_CUT, dim))
	var fill := _color(StreetRouteConfigData.shipped().rooms["colors"].get(kind_id, [0.7, 0.7, 0.7]), dim)
	var inner := rr - 5.0 * kk
	match kind_id:
		"rest":
			# A crescent: the disc with a die-cut disc bitten out of its right side (the polygon form did not triangulate).
			draw_circle(p, inner, fill)
			draw_circle(p + Vector2(inner * 0.42, -inner * 0.1), inner * 0.8, Color(RouteInk.DIE_CUT, dim))
		"workshop":
			var pts2 := PackedVector2Array()
			for i in 6:
				pts2.append(p + Vector2.from_angle(TAU * float(i) / 6.0) * inner)
			draw_colored_polygon(pts2, fill)
		_:
			var q := inner * 0.85
			var n := q * 0.4
			draw_colored_polygon(PackedVector2Array([p + Vector2(-q, -q), p + Vector2(-n, -q), p + Vector2(0, -q + n), p + Vector2(n, -q), p + Vector2(q, -q),
				p + Vector2(q, q), p + Vector2(-q, q)]), fill)


func _ring(p: Vector2, ring_r: float, st: String, kk: float, dim: float, col: Color) -> void:
	var w := RING_W * kk
	var ink := Color(RouteInk.KEYLINE, 0.9 * dim)
	var c := Color(col, dim)
	match st:
		StreetRouteRules.STATE_WALKED:
			for rr in [ring_r - w * 0.55, ring_r + w * 0.55]:
				draw_arc(p, rr, 0.0, TAU, 40, ink, w * 0.6 + KEYLINE_W * kk * 0.6)
			for rr in [ring_r - w * 0.55, ring_r + w * 0.55]:
				draw_arc(p, rr, 0.0, TAU, 40, c, w * 0.55)
		StreetRouteRules.STATE_LATER:
			for q in 12:
				var a0 := TAU * float(q) / 12.0
				var a1 := a0 + TAU / 12.0 * 0.55
				draw_arc(p, ring_r, a0, a1, 6, ink, w + KEYLINE_W * kk)
				draw_arc(p, ring_r, a0, a1, 6, c, w)
		StreetRouteRules.STATE_CUT:
			for q in 16:
				var d := p + Vector2.from_angle(TAU * float(q) / 16.0) * ring_r
				draw_circle(d, w * 0.75 + kk, ink)
				draw_circle(d, w * 0.6, c)
			var s := Vector2(ring_r, -ring_r) * 0.72
			draw_line(p - s, p + s, ink, w + KEYLINE_W * kk)
			draw_line(p - s, p + s, c, w)
		_:
			draw_arc(p, ring_r, 0.0, TAU, 40, ink, w * 1.4 + KEYLINE_W * kk)
			draw_arc(p, ring_r, 0.0, TAU, 40, c, w * 1.4)


func _draw_chip(box: Rect2, n: int, kk: float) -> void:
	draw_rect(box.grow(kk), Color(RouteInk.KEYLINE, 0.9))
	draw_rect(box, RouteInk.RING_AVAILABLE)
	var f := Palette.mono()
	var fs := maxi(1, roundi(float(CHIP_FONT) * kk * 1.4))
	var y := box.get_center().y + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	draw_string(f, Vector2(box.position.x, y), str(n), HORIZONTAL_ALIGNMENT_CENTER, box.size.x, fs, RouteInk.KEYLINE)


func _draw_token(r: float, kk: float) -> void:
	var cur := String(state["current"])
	if cur == "" or not _stick_px.has(cur):
		return
	var tex := load(ART_DIR + "token_operative.png") as Texture2D
	if tex == null:
		return
	var p: Vector2 = _stick_px[cur]
	var side := r * 1.05 * 2.0
	var sz := Vector2(tex.get_width(), tex.get_height()) * (side / maxf(1.0, float(tex.get_width())))
	draw_texture_rect(tex, Rect2(p + Vector2(r * 0.75, -r * 1.45) - sz * 0.5, sz), false)


## HQ-LADDER-UI: the tower's name over each room in play (the one stood in and the choices), so the two towers read apart.
func _draw_tower_names(kk: float, r: float) -> void:
	if tower_names.is_empty():
		return
	var f := Palette.mono()
	var fs := maxi(1, roundi(float(TOWER_FONT) * kk))
	var ids: Array = (state["options"] as Array).duplicate()
	ids.append(String(state["current"]))
	for id in ids:
		var key := String(id)
		if not tower_names.has(key) or not _stick_px.has(key):
			continue
		var text := String(tower_names[key])
		var sz := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
		var p: Vector2 = _stick_px[key]
		var at := Vector2(p.x - sz.x * 0.5, p.y - r * 1.25)
		var col: Color = TOWER_COLORS.get(text, Palette.TEXT_HI)
		draw_rect(Rect2(at - Vector2(4.0, sz.y - 2.0) * kk, sz + Vector2(8.0, 4.0) * kk), Color(Palette.NIGHT_SKY, 0.85))
		draw_string(f, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)


## The hover tag (9.3 rule 3: tags show only on hover; the legend lights them all).
func _draw_tags(kk: float, r: float) -> void:
	var f := Palette.mono()
	var fs := maxi(1, roundi(float(TAG_FONT) * kk * 1.4))
	var ids: Array = tags.keys()
	IdSort.sort_ids(ids)
	for id: String in ids:
		if not (id == focus or lit_all) or not _stick_px.has(id):
			continue
		var text := String(tags[id])
		if text == "":
			continue
		var sz := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
		var p: Vector2 = _stick_px[id]
		var box := Rect2(Vector2(p.x + r * 1.1, p.y - sz.y - r * 0.8), sz + Vector2(10.0, 6.0) * kk)
		draw_rect(box, Color(Palette.NIGHT_SKY, 0.92))
		draw_rect(box, Color(RouteInk.RING_AVAILABLE, 0.9), false, kk)
		draw_string(f, box.position + Vector2(5.0 * kk, sz.y + 1.0 * kk), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.TEXT_HI)


# --- TARGET pencil and arrow ------------------------------------------------------------------

## The TARGET's screen box (its room front plus the circle's reach), px in this control.
func target_box() -> Rect2:
	var tid := StreetRouteRules.target_of(data.run_graph)
	var box := rig.room_box_px(tid)
	if box.size == Vector2.ZERO:
		return Rect2()
	var pad := float(_cfg().target["circle_pad_px"]) * k()
	return box.grow(pad)


## The visible share of the TARGET inside `usable` (0..1) under the displayed pose.
func target_share() -> float:
	return StreetRouteRules.visible_share(target_box(), usable)


## True while the edge arrow is shown (or fading in).
func arrow_showing() -> bool:
	return _arrow_on


## The visible-share the last layout used.
func last_share() -> float:
	return _share


func _lay_target() -> void:
	if _pencil == null:
		return
	var cfgt: Dictionary = _cfg().target
	var tid := StreetRouteRules.target_of(data.run_graph)
	_share = target_share()
	_arrow_on = StreetRouteRules.arrow_on(_share, _arrow_on, float(cfgt["switch_share"]), float(cfgt["hysteresis"]))
	var origin := usable.position
	_clip.position = usable.position
	_clip.size = usable.size
	var kk := k()
	_clip.visible = not intro or (mark_s >= 0.0 and EntryBeats.target_on(mark_s))
	_pencil.begin()
	var tword := CityMapOverlay.tr_word(WORD_TARGET)
	if _share > 0.0 and _stick_px.has(tid):
		var c: Vector2 = _stick_px[tid] - origin
		var rr := sticker_radius() * TARGET_SHARE
		_pencil.circle("target_loop", c, Vector2(rr, rr * TARGET_SQUASH), GreasePencilMark.Ink.THREAT, LOOP_SEED)
		var wk := maxf(kk, 0.5)
		var wsz := PencilSet.word_size(tword, TARGET_FONT) * wk
		var place := StreetRouteRules.target_word_place(c, rr, wsz, wsz.x * TARGET_WORD_PAD, Rect2(Vector2.ZERO, usable.size))
		var base: Vector2 = place["baseline"]
		var wc := PencilSet.centre_of(base, tword, TARGET_FONT, wk, -0.12)
		_pencil.word("target_word", tword, wc, TARGET_FONT, GreasePencilMark.Ink.THREAT, wk, PencilSet.AUTO, 0.0, -0.12)
	_pencil.end()
	_lay_arrow(tid, kk)


func _lay_arrow(tid: String, kk: float) -> void:
	var show_it := _arrow_k > 0.001 and usable.size.x > 0.0 and not intro
	var box := rig.room_box_px(tid)
	if not show_it or box.size == Vector2.ZERO:
		_arrow_mark.visible = false
		_arrow_word.visible = false
		return
	var margin := float(_cfg().target["margin_px"]) * kk
	var e := TargetEdgeMarker.edge_point(usable, box.get_center(), margin)
	if bool(e["inside"]):
		var cc := usable.get_center()
		var d := (box.get_center() - cc).normalized() if box.get_center() != cc else Vector2.UP
		e = TargetEdgeMarker.edge_point(usable, cc + d * usable.size.length(), margin)
	var at: Vector2 = e["at"]
	var dir: Vector2 = e["dir"]
	var tail := at - dir * SHAFT_PX * kk
	_arrow_mark.clear()
	for s in PencilShapes.arrow(PackedVector2Array([tail, tail.lerp(at, 0.5), at]), HEAD_PX * kk, ARROW_SEED):
		_arrow_mark.add_stroke(s)
	var wsize := _arrow_word.global_rect().size
	_arrow_word.position = tail - dir * WORD_BACK * kk - wsize * 0.5
	_arrow_mark.visible = true
	_arrow_word.visible = true
	_arrow_mark.modulate.a = _arrow_k
	_arrow_word.modulate.a = _arrow_k


## The pencil rects (px in this control) the wax occupies: the arrow's box and its word (the "wax clear of UI" test reads them).
func arrow_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if _arrow_mark != null and _arrow_mark.visible:
		out.append(_arrow_mark.global_rect())
		out.append(_arrow_word.global_rect())
	return out


## Every sticker ring rect (centre +- reach) and chip rect, px: what the wax must keep clear of.
func sticker_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var r := sticker_radius()
	for id: String in _stick_px:
		out.append(Rect2((_stick_px[id] as Vector2) - Vector2(r, r), Vector2(r, r) * 2.0))
	for id: String in _chip_rects:
		out.append(_chip_rects[id])
	return out
