class_name TideRaidLayer
extends Control
## Phase 3: the Infected Tide raid drawn on the city map (a CityMapOverlay over the 3D city at the RAID band). The raid lines run as
## paths over the real network edges (RaidMapAnchor.street), typed by color and shape (D triangle, N square, E circle); sentries
## stand on Sites; the INFECTED Sites and their neighbours carry the Bloom front tint; the HOME and Genome Core ends are marked, with
## the worst tier of each route at HOME. A view: it draws the description the screen gives it and decides nothing.
##
## Phase 3c: the playout travels. A beam of the playout is a pulse that runs from its start along its path and stops where the raid says
## it stops (a guard, or HOME); a blocked beam ends at its guard with a shield burst, a beam that reaches HOME lands an impact, a lost
## Site blooms with the infection and a card flies from it to the deck strip. Labels sit off the map's Sites on a leader line, and the
## layer stamps DOWN and TAKEN on their own Sites (the city's own stamps are switched off while the raid is on).
##
## Look for the art-pass: the front tint is a flat translucent disk (the Bloom look API of CityView3D is the netrun street's, it does not
## apply to the City Grid map); the pulse, bursts and flying card are flat shapes.

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
## A beam that is not the focused one keeps this share of its alpha.
const FOCUS_DIM := 0.18
const IMPACT_R := 16.0
const IMPACT_SPOKES := 8
const IMPACT_PERIOD := 0.9
const CHIP_R := 8.0
## The pulse's head (px) and the share of the drawn beam its bright tail covers.
const PULSE_R := 9.0
const PULSE_TAIL := 0.22
## A label's candidate boxes: rings of distance from its anchor, and the directions tried on each.
const LABEL_RINGS: Array[float] = [30.0, 54.0, 80.0, 110.0]
const LABEL_DIRS := 12
const LABEL_PAD := 5.0
## The map's keep-out: a Site's disk and the HQ star / HOME's disk (px).
const KEEP_SITE_R := 24.0
const KEEP_END_R := 42.0
## Where the DOWN / TAKEN stamp sits under its Site (px) and its tilt.
const STAMP_DROP := 24.0
const STAMP_TILT := -0.1
const STAMP_PX := 12
## The flying INFECTED card (px) and how far it arcs up on the way.
const FLIGHT_W := 20.0
const FLIGHT_H := 28.0
const FLIGHT_ARC := 46.0
const BLOOM_R := 44.0
const BURST_SPOKES := 12

var overlay: CityMapOverlay = null
var core: StringName = &""
var home: StringName = &""
## Beams to draw: {cells (Site ids in scan order), type, role ("known" | "cand" | "hunter"), label, alpha, dashed, width, current, ghost,
## stop (the Site or "HOME" the beam ends at, "" = the end of its path), pulse (true while it travels), hit_sites (Sites it hits on the way)}.
var beams: Array[Dictionary] = []
## site -> [type, verb] for the sentries now standing.
var sentries: Dictionary = {}
## Sites that are INFECTED (a wound card names them), the neighbours of those (the front), the TAKEN Sites, the DOWN Sites.
var infected: Array[StringName] = []
var front: Array[StringName] = []
var taken: Array[StringName] = []
var downs: Array[StringName] = []
## Persistent hit marks: site -> "hit" | "block". The block markers show for the current beam only (see `blocks`).
var hits: Dictionary = {}
var blocks: Array = []
## The worst tier of each candidate route at HOME (empty: none), drawn at HOME.
var home_tiers: Array = []
## The type color of each of those routes (the chip colors that match the forecast columns).
var home_cols: Array[Color] = []
var ghost_home: bool = false
## The beam (its `name`) the player hovers or picked: every other beam dims. "" = none, all beams show alike.
var focus: String = ""
## What the current playout beat hits: [{site, col, label}], drawn as an impact burst on the Site.
var impacts: Array = []
## The effects of the current beat: [{kind ("shield" | "home" | "bloom"), site, col, t0 (ms), dur (s)}] and the INFECTED cards flying to the
## deck strip: [{site, to (this layer's px), t0, dur}].
var bursts: Array = []
var flights: Array = []
var hovered: StringName = &""
## The response being previewed (hovered or picked): [] or its response array, drawn as a ghost on the map.
var preview: Array = []
var preview_type: String = ""
const SENTRY_SCALE := 1.3
const GHOST_ALPHA := 0.7
var _font: Font = null
## The pulse: when the current beat started (ms) and how long its travel takes (s; 0 = it has arrived).
var pulse_t0: int = 0
var pulse_secs: float = 0.0
var _keep: Array = []
var _labels: Array = []
var _boxes: Array[Rect2] = []


func _init() -> void:
	name = "TideRaidLayer"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_font = ThemeDB.fallback_font


func _process(_delta: float) -> void:
	# The city's own CLAIMED / TAKEN / DOWN stamps wander off to a free spot; the raid stamps its Sites itself (`_draw_stamps`).
	var city: Variant = overlay.city if overlay != null and is_instance_valid(overlay) else null
	if city != null and float(city.stamp_left) > 0.0:
		city.stamp_left = 0.0
	queue_redraw()


# ------------------------------------------------------------------------------------------------ the beat's clock
## A beam starts travelling now; it arrives after `secs` (0: it is there at once, as under reduced motion).
func start_pulse(secs: float) -> void:
	pulse_t0 = Time.get_ticks_msec()
	pulse_secs = maxf(0.0, secs)


## How far the current beam's pulse has run (0..1).
func pulse_progress() -> float:
	if pulse_secs <= 0.0:
		return 1.0
	return clampf(float(Time.get_ticks_msec() - pulse_t0) / 1000.0 / pulse_secs, 0.0, 1.0)


## Starts an effect on `site` ("HOME" for HOME) of `kind`: a shield burst, a HOME impact or an infection bloom, lasting `dur` seconds.
func add_burst(kind: String, site: StringName, col: Color, dur: float) -> void:
	bursts.append({"kind": kind, "site": site, "col": col, "t0": Time.get_ticks_msec(), "dur": dur})


## An INFECTED card leaves `site` for the point `to` of this layer.
func add_flight(site: StringName, to: Vector2, dur: float) -> void:
	flights.append({"site": site, "to": to, "t0": Time.get_ticks_msec(), "dur": dur})


## The effects are over (the next beat, the aftermath).
func clear_fx() -> void:
	bursts = []
	flights = []
	impacts = []
	pulse_secs = 0.0


func _age(e: Dictionary) -> float:
	var dur := float(e["dur"])
	if dur <= 0.0:
		return 1.0
	return clampf(float(Time.get_ticks_msec() - int(e["t0"])) / 1000.0 / dur, 0.0, 1.0)


# ------------------------------------------------------------------------------------------------ geometry
## Site `id`'s point in this layer's px (INF off the map).
func at(id: StringName) -> Vector2:
	var p := RaidMapAnchor.site(overlay, id)
	if p.x == INF:
		return Vector2.INF
	return get_global_transform().affine_inverse() * p


## The point of `id` on the map, HOME's word included.
func spot(id: StringName) -> Vector2:
	return at(home if String(id) == "HOME" else id)


## The path of `cells` (core first for a route, HOME last) over the map's streets, in this layer's px.
func path(ids: Array) -> PackedVector2Array:
	return path_marks(ids)["pts"]


## The path of `ids` and, per id, how far along the path (px) the path reaches it: {pts, at (Array[float], one per id), total}.
func path_marks(ids: Array) -> Dictionary:
	var pts := PackedVector2Array()
	var marks: Array[float] = []
	if overlay == null:
		return {"pts": pts, "at": marks, "total": 0.0}
	var inv := get_global_transform().affine_inverse()
	var run := 0.0
	marks.append(0.0)
	for i in ids.size() - 1:
		var seg := RaidMapAnchor.street(overlay, StringName(String(ids[i])), StringName(String(ids[i + 1])))
		for q in seg:
			var l: Vector2 = inv * q
			if pts.is_empty():
				pts.append(l)
			elif pts[pts.size() - 1].distance_to(l) > 0.5:
				run += pts[pts.size() - 1].distance_to(l)
				pts.append(l)
		marks.append(run)
	if pts.is_empty() and ids.size() == 1:
		var p := at(StringName(String(ids[0])))
		if p.x != INF:
			pts.append(p)
	return {"pts": pts, "at": marks, "total": run}


func _beam_ids(b: Dictionary) -> Array:
	var ids: Array = []
	if bool(b.get("route", false)):
		ids.append(core)
	ids.append_array(b["cells"])
	if bool(b.get("home", false)):
		ids.append(home)
	return ids


## The part of `pts` that is `dist` px long from its start.
static func trim(pts: PackedVector2Array, dist: float) -> PackedVector2Array:
	var out := PackedVector2Array()
	if pts.is_empty():
		return out
	out.append(pts[0])
	var run := 0.0
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if run + seg >= dist:
			var k := 0.0 if seg <= 0.0 else (dist - run) / seg
			out.append(pts[i].lerp(pts[i + 1], clampf(k, 0.0, 1.0)))
			return out
		run += seg
		out.append(pts[i + 1])
	return out


## The point `dist` px along `pts`.
static func point_at(pts: PackedVector2Array, dist: float) -> Vector2:
	var t := trim(pts, dist)
	return t[t.size() - 1]


static func length_of(pts: PackedVector2Array) -> float:
	var run := 0.0
	for i in pts.size() - 1:
		run += pts[i].distance_to(pts[i + 1])
	return run


# ------------------------------------------------------------------------------------------------ draw
func _draw() -> void:
	if overlay == null or not is_instance_valid(overlay):
		return
	_build_keepout()
	_labels = []
	_boxes = []
	_draw_tints()
	for b in beams:
		_draw_beam(b)
	_draw_hits()
	_draw_stamps()
	_draw_sentries()
	_draw_home()
	_draw_labels()
	_draw_preview()
	_draw_impacts()
	_draw_bursts()
	_draw_flights()


## The points a label keeps off: every Site of the map, the HQ star and HOME.
func _build_keepout() -> void:
	_keep = []
	for n in overlay.nodes:
		var p := at(StringName(String(n["id"])))
		if p.x != INF:
			_keep.append([p, KEEP_SITE_R])
	for id in [core, home]:
		var p := at(id)
		if p.x != INF:
			_keep.append([p, KEEP_END_R])


func _clearance(p: Vector2) -> float:
	var best := INF
	for k in _keep:
		best = minf(best, p.distance_to(k[0]) - float(k[1]))
	return best


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
	var ids := _beam_ids(b)
	var m := path_marks(ids)
	var pts: PackedVector2Array = m["pts"]
	if pts.size() < 2:
		return
	var col := TideGlyphs.type_color(String(b["type"]))
	var a := float(b.get("alpha", 1.0))
	if focus != "" and String(b.get("name", "")) != focus:
		a *= FOCUS_DIM
	col.a = a
	var w := float(b.get("width", LINE_W))
	var ink := Color(TideGlyphs.BLACK, INK_ALPHA * a)
	# A playout beam ends where the raid stops it (a guard, or HOME); while it travels only the part the pulse has run is drawn.
	var end_len := float(m["total"])
	var stop := String(b.get("stop", ""))
	if stop != "":
		for i in ids.size():
			if String(ids[i]) == stop or (stop == "HOME" and bool(b.get("home", false)) and i == ids.size() - 1):
				end_len = float((m["at"] as Array)[i])
				break
	var pulsing := bool(b.get("pulse", false))
	var drawn := end_len * (pulse_progress() if pulsing else 1.0)
	var dp := trim(pts, drawn) if drawn < float(m["total"]) else pts
	if dp.size() < 2:
		dp = PackedVector2Array([pts[0], pts[0] + Vector2(0.1, 0.0)])
	if bool(b.get("dashed", false)):
		_dashed(dp, ink, w + 2.0)
		_dashed(dp, col, w)
	else:
		draw_polyline(dp, ink, w + 2.0)
		draw_polyline(dp, col, w)
	# The head: the type shape at the start, an arrowhead at the end of what is drawn.
	var start := dp[0]
	TideGlyphs.type_shape(self, start, String(b["type"]), 7.0, col)
	var d := (dp[dp.size() - 1] - dp[dp.size() - 2]).normalized()
	if pulsing and drawn < end_len:
		_draw_pulse(dp, col, a)
	else:
		var tip := dp[dp.size() - 1] - d * 14.0
		var n := Vector2(-d.y, d.x)
		draw_colored_polygon(PackedVector2Array([tip + d * 9.0, tip - n * 5.0, tip + n * 5.0]), col)
	# The sites the pulse has passed carry their hit mark at once.
	if pulsing:
		for hs in b.get("hit_sites", []):
			for i in ids.size():
				if String(ids[i]) == String(hs) and float((m["at"] as Array)[i]) <= drawn + 0.5:
					var hp := at(StringName(String(hs)))
					if hp.x != INF:
						TideGlyphs.xmark(self, hp, 7.0, TideGlyphs.RED, 2.5)
	var lab := String(b.get("label", ""))
	if lab != "" or String(b["role"]) == "hunter":
		_labels.append({"text": lab, "col": Color(col, a).lightened(0.3), "pts": dp, "a": a, "hound": String(b["role"]) == "hunter", "base": col})
	var chip := String(b.get("chip", ""))
	if chip != "" and a > FOCUS_DIM:
		TideGlyphs.route_chip(self, start + Vector2(14.0, -14.0), chip, CHIP_R, Color(TideGlyphs.type_color(String(b["type"])), a))
	if bool(b.get("current", false)):
		draw_arc(start, 12.0, 0.0, TAU, 20, Color(TideGlyphs.INK, a), 2.0)


## The pulse: a bright tail along the end of the drawn beam and a glowing head.
func _draw_pulse(dp: PackedVector2Array, col: Color, a: float) -> void:
	var total := length_of(dp)
	var head := dp[dp.size() - 1]
	var from := maxf(0.0, total * (1.0 - PULSE_TAIL))
	var tp := PackedVector2Array()
	var run := 0.0
	for i in dp.size() - 1:
		var seg := dp[i].distance_to(dp[i + 1])
		if run + seg >= from:
			tp.append(dp[i] if run >= from else dp[i].lerp(dp[i + 1], (from - run) / maxf(seg, 0.001)))
			tp.append(dp[i + 1])
		run += seg
	if tp.size() >= 2:
		draw_polyline(tp, Color(TideGlyphs.INK, a), 3.0)
	draw_circle(head, PULSE_R + 5.0, Color(col, 0.28 * a))
	draw_circle(head, PULSE_R, Color(col, 0.75 * a))
	draw_circle(head, PULSE_R * 0.5, Color(TideGlyphs.INK, a))


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


# ------------------------------------------------------------------------------------------------ labels on leader lines
## Every beam label, set where it covers no Site, the HQ star, HOME or another label, on a leader line to its beam. The HUNTER's hound
## stands on its street at the same clear point (never on a hex).
func _draw_labels() -> void:
	for l in _labels:
		var pts: PackedVector2Array = l["pts"]
		if pts.size() < 2:
			continue
		var anchor := _clear_point(pts)
		if bool(l["hound"]):
			TideGlyphs.hound(self, anchor + Vector2(0.0, -6.0), Color(l["base"], float(l["a"])))
		var text := String(l["text"])
		if text == "":
			continue
		var col: Color = l["col"]
		var lsize := _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, LABEL_PX) + Vector2(LABEL_PAD * 2.0, 6.0)
		var box := _label_box(anchor, lsize)
		_boxes.append(box)
		var edge := Vector2(clampf(anchor.x, box.position.x, box.end.x), clampf(anchor.y, box.position.y, box.end.y))
		draw_line(anchor, edge, Color(col, 0.9), 1.5)
		draw_circle(anchor, 2.5, col)
		draw_rect(box, Color(TideGlyphs.BLACK, 0.82))
		draw_rect(box, Color(col, 0.9), false, 1.5)
		draw_string(_font, box.position + Vector2(LABEL_PAD, lsize.y - 5.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, LABEL_PX, Color(TideGlyphs.INK, float(l["a"])))


## The point of `pts` farthest from the map's Sites and ends, within the middle half of the path.
func _clear_point(pts: PackedVector2Array) -> Vector2:
	var total := length_of(pts)
	var best := point_at(pts, total * 0.5)
	var best_c := -INF
	for i in 11:
		var p := point_at(pts, total * (0.25 + 0.05 * float(i)))
		var c := _clearance(p)
		if c > best_c + 0.01:
			best_c = c
			best = p
	return best


## The first box of size `size` near `anchor` that covers the least of the keep-out and the labels placed so far.
func _label_box(anchor: Vector2, bsize: Vector2) -> Rect2:
	var best := Rect2(anchor + Vector2(12.0, -bsize.y - 12.0), bsize)
	var least := INF
	for ring in LABEL_RINGS:
		for k in LABEL_DIRS:
			var dir := Vector2.from_angle(TAU * float(k) / float(LABEL_DIRS) - PI * 0.5)
			var c := anchor + dir * ring
			var box := Rect2(c - bsize * 0.5, bsize)
			var cost := _box_cost(box)
			if cost < least:
				least = cost
				best = box
				if cost <= 0.0:
					return best
	return best


func _box_cost(box: Rect2) -> float:
	var cost := 0.0
	var inner := box.grow(3.0)
	for k in _keep:
		var c: Vector2 = k[0]
		var near := Vector2(clampf(c.x, inner.position.x, inner.end.x), clampf(c.y, inner.position.y, inner.end.y))
		var gap := float(k[1]) - near.distance_to(c)
		if gap > 0.0:
			cost += gap * 4.0 + 20.0
	for o in _boxes:
		if o.grow(3.0).intersects(inner):
			cost += 60.0
	var r := Rect2(Vector2.ZERO, size)
	if not r.encloses(box):
		cost += 80.0
	return cost


# ------------------------------------------------------------------------------------------------ marks
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


## DOWN and TAKEN, stamped on their own Sites: a tilted plate under the Site with a bolt (DOWN) or a crack (TAKEN).
func _draw_stamps() -> void:
	for id in downs:
		_stamp(id, "DOWN", Palette.TIDE_BATTERED, false)
	for id in taken:
		_stamp(id, "TAKEN", TideGlyphs.RED, true)


func _stamp(id: StringName, word: String, col: Color, cracked: bool) -> void:
	var p := at(id)
	if p.x == INF:
		return
	var tw := _font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, STAMP_PX).x
	var box := Rect2(Vector2(-(tw + 22.0) * 0.5, -9.0), Vector2(tw + 22.0, 18.0))
	draw_set_transform(p + Vector2(0.0, STAMP_DROP), STAMP_TILT, Vector2.ONE)
	draw_rect(box, Color(TideGlyphs.BLACK, 0.88))
	draw_rect(box, col, false, 2.0)
	var gc := box.position + Vector2(9.0, 9.0)
	if cracked:
		TideGlyphs.crack(self, gc, 5.0, col, 1.5)
	else:
		draw_colored_polygon(PackedVector2Array([gc + Vector2(1.0, -6.0), gc + Vector2(-4.0, 1.0), gc + Vector2(-0.5, 1.0), gc + Vector2(-1.5, 6.0), gc + Vector2(4.0, -1.5), gc + Vector2(0.5, -1.5)]), TideGlyphs.INK)
	draw_string(_font, box.position + Vector2(17.0, 13.0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, STAMP_PX, col)
	draw_set_transform(Vector2.ZERO)


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
			var chip_col: Color = home_cols[i] if i < home_cols.size() else TideGlyphs.DIM
			TideGlyphs.route_chip(self, c + Vector2(0.0, HOME_GLYPH_R + 13.0), CAND_LETTERS[i], CHIP_R, chip_col)
	var cp := at(core)
	if cp.x != INF:
		draw_arc(cp, 26.0, 0.0, TAU, 28, TideGlyphs.COBALT_HOT, 2.0)


## The beat's impact on each Site it hits: a solid ring, a pulse ring swelling out of it (still under reduce motion), spokes and a
## named chip, so a beam that lands is a visible event and not only a log line.
func _draw_impacts() -> void:
	if impacts.is_empty():
		return
	var animated := Motion.seconds_live(&"raid_step_beat") > 0.0
	var k := fmod(float(Time.get_ticks_msec()) / 1000.0 / IMPACT_PERIOD, 1.0) if animated else 0.5
	for im in impacts:
		var p := at(StringName(String(im["site"])))
		if p.x == INF:
			continue
		var col: Color = im["col"]
		draw_circle(p, IMPACT_R + 4.0, Color(TideGlyphs.BLACK, 0.45))
		draw_arc(p, IMPACT_R, 0.0, TAU, 28, col, 3.5)
		draw_arc(p, IMPACT_R + 22.0 * k, 0.0, TAU, 28, Color(col, 1.0 - k), 2.5)
		for s in IMPACT_SPOKES:
			var d := Vector2.from_angle(TAU * float(s) / float(IMPACT_SPOKES) + 0.2)
			draw_line(p + d * (IMPACT_R + 5.0), p + d * (IMPACT_R + 13.0 + 6.0 * k), col, 2.0)
		TideGlyphs.xmark(self, p, 7.0, TideGlyphs.RED, 3.0)
		var lab := String(im.get("label", ""))
		if lab != "":
			var w := _font.get_string_size(lab, HORIZONTAL_ALIGNMENT_LEFT, -1, LABEL_PX).x
			var box := Rect2(p + Vector2(18.0, -34.0), Vector2(w + 12.0, 20.0))
			draw_rect(box, Color(TideGlyphs.BLACK, 0.85))
			draw_rect(box, col, false, 2.0)
			draw_string(_font, box.position + Vector2(6.0, 15.0), lab, HORIZONTAL_ALIGNMENT_LEFT, -1, LABEL_PX, TideGlyphs.INK)


## The shield bursts, HOME impacts and infection blooms of the beat.
func _draw_bursts() -> void:
	for e in bursts:
		var p := spot(StringName(String(e["site"])))
		if p.x == INF:
			continue
		var k := _age(e)
		var col: Color = e["col"]
		match String(e["kind"]):
			"shield":
				# The guard holds: a shield swells over the Site and a ring runs out of it.
				var r := 16.0 + 8.0 * k
				draw_circle(p, 26.0, Color(TideGlyphs.INK, 0.45 * (1.0 - k)))
				draw_colored_polygon(TideGlyphs.shield_pts(p, r), Color(col, 0.55))
				draw_polyline(_closed(TideGlyphs.shield_pts(p, r)), TideGlyphs.INK, 2.5)
				draw_arc(p, 20.0 + 38.0 * k, 0.0, TAU, 32, Color(col, 1.0 - k), 3.0)
				draw_arc(p, 20.0 + 22.0 * k, 0.0, TAU, 32, Color(TideGlyphs.INK, 0.8 * (1.0 - k)), 2.0)
			"home":
				# The beam lands on HOME: a hot flash, a ring and spokes.
				draw_circle(p, 22.0 + 30.0 * k, Color(TideGlyphs.RED, 0.5 * (1.0 - k)))
				draw_arc(p, 26.0 + 46.0 * k, 0.0, TAU, 36, Color(TideGlyphs.INK, 1.0 - k), 4.0)
				for s in BURST_SPOKES:
					var d := Vector2.from_angle(TAU * float(s) / float(BURST_SPOKES))
					draw_line(p + d * (26.0 + 8.0 * k), p + d * (34.0 + 40.0 * k), Color(TideGlyphs.RED, 1.0 - 0.5 * k), 3.0)
				TideGlyphs.xmark(self, p, 12.0, TideGlyphs.RED, 4.0)
			"bloom":
				# The infection takes the Site: a dark bloom swells over the district and cracks.
				var r := lerpf(6.0, BLOOM_R, 1.0 - pow(1.0 - k, 2.0))
				draw_circle(p, r, Color(INFECT_COL, 0.8))
				draw_arc(p, r, 0.0, TAU, 32, Palette.TIDE_INFECT_EDGE, 2.5)
				draw_arc(p, r * 0.6, 0.0, TAU, 28, Color(Palette.TIDE_INFECT_EDGE, 0.7), 1.5)
				TideGlyphs.crack(self, p, 12.0 + 6.0 * k, Palette.TIDE_INFECT_CRACK, 2.5)


func _closed(pts: PackedVector2Array) -> PackedVector2Array:
	var out := pts.duplicate()
	if not out.is_empty():
		out.append(out[0])
	return out


## The INFECTED cards flying from their Sites to the deck strip, arcing up on the way and shrinking as they land.
func _draw_flights() -> void:
	for f in flights:
		var from := spot(StringName(String(f["site"])))
		if from.x == INF:
			continue
		var k := _age(f)
		var e := k * k * (3.0 - 2.0 * k)
		var to: Vector2 = f["to"]
		var pos := from.lerp(to, e) + Vector2(0.0, -FLIGHT_ARC * sin(PI * e))
		var s := lerpf(1.4, 0.8, e)
		var r := Rect2(pos - Vector2(FLIGHT_W, FLIGHT_H) * 0.5 * s, Vector2(FLIGHT_W, FLIGHT_H) * s)
		draw_rect(r.grow(3.0), Color(TideGlyphs.RED, 0.35))
		draw_rect(r, TideGlyphs.WOUND_FILL)
		draw_rect(r, TideGlyphs.RED, false, 2.0)
		TideGlyphs.crack(self, r.get_center(), 6.0 * s, TideGlyphs.RED, 2.0)


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
