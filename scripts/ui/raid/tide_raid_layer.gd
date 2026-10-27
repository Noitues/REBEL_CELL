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

const CAND_LETTERS: Array[String] = ["A", "B", "C"]
## A label's candidate boxes: rings of distance from its anchor, and the directions tried on each.
const LABEL_RINGS: Array[float] = [30.0, 54.0, 80.0, 110.0]
const LABEL_DIRS := 12
## The map's keep-out: a Site's disk and the HQ star / HOME's disk (px).
const KEEP_SITE_R := 24.0
const KEEP_END_R := 42.0
## Where the DOWN / TAKEN stamp sits under its Site (px).
const STAMP_DROP := 24.0

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
## H7c: the Sites a sentry's shield covers on the current beam, and the Sites whose shield just ended (the beat before was its last).
var shields: Array = []
var shields_gone: Array = []
## H7c: the Sites that fell at the raid's close (DOWN with no sentry -> TAKEN), stamped TAKEN with a "falls" note.
var falls: Array = []
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
## The map's room between the deck strip, the side panel, the HUD and the hand (this layer's px); empty = the whole layer.
var bounds: Rect2 = Rect2()
## The forecast outcome the player points at (a tile or a bar segment): {down, taken, home}; empty = none. The Sites that go DOWN or TAKEN and the HOME
## damage are drawn on the map as a prediction.
var fc_marks: Dictionary = {}
## Placed sentries that do nothing: site -> the reason. They turn red, and the reason shows beside them.
var bad_sentries: Dictionary = {}
## The picked card tried on each Site it could stand on: site -> {useless, reason}. A ring per Site: clear (it would work) or red (it would not).
var ghost_sites: Dictionary = {}
## The response being previewed (hovered or picked): [] or its response array, drawn as a ghost on the map.
var preview: Array = []
var preview_type: String = ""
var _font: Font = null
## The pulse: when the current beat started (ms) and how long its travel takes (s; 0 = it has arrived).
var pulse_t0: int = 0
var pulse_secs: float = 0.0
var _keep: Array = []
var _labels: Array = []
var _boxes: Array[Rect2] = []
## Every tag of the frame (DOWN / TAKEN stamps, HIT names, forecast and mismatch notes, beam labels), laid out together so none covers another.
var _tags: Array = []


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
	_tags = []
	_draw_tints()
	for b in beams:
		_draw_beam(b)
	_draw_hits()
	_draw_sentries()
	_draw_home()
	_draw_preview()
	_draw_impacts()
	_draw_bursts()
	_draw_flights()
	# The tags last, in the order of their weight: the stamps first (they say what happened), then the hits, the notes and the beam labels.
	_collect_stamps()
	_collect_marks()
	_collect_impact_tags()
	_collect_beam_tags()
	_draw_tags()


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
	# A standing sentry is drawn above its Site: tags keep off it too.
	for id in sentries:
		var p := at(id)
		if p.x != INF:
			_keep.append([p + Vector2(0.0, -24.0), 16.0])


func _clearance(p: Vector2) -> float:
	var best := INF
	for k in _keep:
		best = minf(best, p.distance_to(k[0]) - float(k[1]))
	return best


func _draw_tints() -> void:
	TideFx.tints(self, _points(front), _points(taken), _points(infected))


## The map points of Sites `ids` (the ones off the map left out).
func _points(ids: Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	for id in ids:
		var p := at(id)
		if p.x != INF:
			out.append(p)
	return out


func _draw_beam(b: Dictionary) -> void:
	var ids := _beam_ids(b)
	var m := path_marks(ids)
	var pts: PackedVector2Array = m["pts"]
	if pts.size() < 2:
		return
	var col := TideFx.type_color(String(b["type"]))
	var a := float(b.get("alpha", 1.0))
	if focus != "" and String(b.get("name", "")) != focus:
		a *= TideFx.look().focus_dim
	col.a = a
	var w := float(b.get("width", TideFx.LINE_W))
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
	var start := dp[0]
	TideFx.beam(self, dp, String(b["type"]), col, a, w, bool(b.get("dashed", false)), pulsing and drawn < end_len)
	# The sites the pulse has passed carry their hit mark at once.
	if pulsing:
		for hs in b.get("hit_sites", []):
			for i in ids.size():
				if String(ids[i]) == String(hs) and float((m["at"] as Array)[i]) <= drawn + 0.5:
					var hp := at(StringName(String(hs)))
					if hp.x != INF:
						TideFx.hit_cross(self, hp)
	var lab := String(b.get("label", ""))
	if lab != "" or String(b["role"]) == "hunter":
		_labels.append({"text": lab, "col": Color(col, a).lightened(0.3), "pts": dp, "a": a, "hound": String(b["role"]) == "hunter", "base": col})
	var chip := String(b.get("chip", ""))
	if chip != "" and a > TideFx.look().focus_dim:
		TideFx.beam_chip(self, start, chip, Color(TideFx.type_color(String(b["type"])), a))
	if bool(b.get("current", false)):
		TideFx.beam_current(self, start, a)

# ------------------------------------------------------------------------------------------------ labels on leader lines
## Every beam label, set where it covers no Site, the HQ star, HOME or another label, on a leader line to its beam. The HUNTER's hound
## stands on its street at the same clear point (never on a hex).
func _collect_beam_tags() -> void:
	for l in _labels:
		var pts: PackedVector2Array = l["pts"]
		if pts.size() < 2:
			continue
		var anchor := _clear_point(pts)
		if bool(l["hound"]):
			TideFx.hound(self, anchor + Vector2(0.0, -6.0), Color(l["base"], float(l["a"])))
		var text := String(l["text"])
		if text == "":
			continue
		_add_tag({"kind": "label", "anchor": anchor, "text": text, "col": l["col"], "a": float(l["a"]), "px": TideFx.LABEL_PX})


## Adds a tag to the frame: {kind, anchor (the map point it belongs to), text, col, px, prefer (where the box likes to sit, from the anchor), own
## (true: the anchor is a Site, which the box may touch)}.
func _add_tag(t: Dictionary) -> void:
	# One label per Site: a state tag (`state` rank: shield 1, HIT 2, DOWN 3, falls 4, TAKEN 5) on a Site that already has one replaces it when it is the same
	# or a later state, and is dropped when it is an earlier one.
	if t.has("state"):
		for i in _tags.size():
			var o: Dictionary = _tags[i]
			if o.has("state") and (o["anchor"] as Vector2).distance_to(t["anchor"]) < 1.0:
				if int(t["state"]) >= int(o["state"]):
					_tags[i] = t
				return
	_tags.append(t)


## Lays the frame's tags out in order, each on the clearest box near its anchor (the Sites, the HQ star, HOME and the tags before it kept clear), and draws them.
func _draw_tags() -> void:
	for t in _tags:
		var text := String(t["text"])
		var px := int(t.get("px", TideFx.LABEL_PX))
		var col: Color = t["col"]
		var a_t := float(t.get("a", 1.0))
		var anchor: Vector2 = t["anchor"]
		var lsize := _font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px) + Vector2(TideFx.look().label_pad * 2.0 + float(t.get("icon", 0.0)), 6.0)
		var own: Vector2 = anchor if bool(t.get("own", false)) else Vector2.INF
		var box := _label_box(anchor, lsize, t.get("prefer", Vector2.INF), own)
		# A tag never leaves the map's room (the deck strip, the panel and the hand stand outside it).
		var room := bounds if bounds.size.x > 0.0 else Rect2(Vector2.ZERO, size)
		box.position.x = clampf(box.position.x, room.position.x, maxf(room.position.x, room.end.x - box.size.x))
		box.position.y = clampf(box.position.y, room.position.y, maxf(room.position.y, room.end.y - box.size.y))
		_boxes.append(box)
		TideFx.tag(self, _font, box, anchor, text, col, a_t, px, String(t["kind"]))


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
func _label_box(anchor: Vector2, bsize: Vector2, prefer: Vector2 = Vector2.INF, own: Vector2 = Vector2.INF) -> Rect2:
	var best := Rect2(anchor + Vector2(12.0, -bsize.y - 12.0), bsize)
	var least := INF
	if prefer.x != INF:
		var pbox := Rect2(anchor + prefer - bsize * 0.5, bsize)
		var pc := _box_cost(pbox, own)
		if pc <= 0.0:
			return pbox
		best = pbox
		least = pc
	for ring in LABEL_RINGS:
		for k in LABEL_DIRS:
			var dir := Vector2.from_angle(TAU * float(k) / float(LABEL_DIRS) - PI * 0.5)
			var c := anchor + dir * ring
			var box := Rect2(c - bsize * 0.5, bsize)
			var cost := _box_cost(box, own)
			if cost < least:
				least = cost
				best = box
				if cost <= 0.0:
					return best
	return best


func _box_cost(box: Rect2, own: Vector2 = Vector2.INF) -> float:
	var cost := 0.0
	var inner := box.grow(3.0)
	for k in _keep:
		var c: Vector2 = k[0]
		if own.x != INF and c.distance_to(own) < 1.0:
			continue
		var near := Vector2(clampf(c.x, inner.position.x, inner.end.x), clampf(c.y, inner.position.y, inner.end.y))
		var gap := float(k[1]) - near.distance_to(c)
		if gap > 0.0:
			cost += gap * 4.0 + 20.0
	for o in _boxes:
		if o.grow(3.0).intersects(inner):
			cost += 60.0
	var r := bounds if bounds.size.x > 0.0 else Rect2(Vector2.ZERO, size)
	if not r.encloses(box):
		cost += 80.0
	return cost


# ------------------------------------------------------------------------------------------------ marks
func _draw_hits() -> void:
	for id in hits:
		var p := at(id)
		if p.x == INF:
			continue
		# A Site the raid hit turns the infection's magenta.
		TideFx.site_hit(self, p)
	for e in blocks:
		var p := at(StringName(String(e[0])))
		if p.x == INF:
			continue
		TideFx.guard_block(self, p, String(e[1]))
	for id in shields:
		var p := at(StringName(String(id)))
		if p.x == INF:
			continue
		TideFx.shield_ring(self, p)
	for id in shields_gone:
		var p := at(StringName(String(id)))
		if p.x == INF:
			continue
		TideFx.shield_gone_ring(self, p)


## DOWN and TAKEN, stamped on their own Sites: a tilted plate under the Site with a bolt (DOWN) or a crack (TAKEN).
func _collect_stamps() -> void:
	for id in downs:
		_stamp(id, "DOWN", Palette.TIDE_SITES_LOST, "stamp_down")
	for id in taken:
		_stamp(id, "TAKEN", TideFx.RED, "stamp_taken")
	for id in falls:
		var p := at(StringName(String(id)))
		if p.x != INF:
			_add_tag({"kind": "note", "anchor": p, "text": tr("falls: no sentry"), "col": TideFx.RED, "px": TideFx.SMALL_PX, "prefer": Vector2(0.0, STAMP_DROP + 22.0), "own": true, "state": 4})
	for id in shields:
		var p := at(StringName(String(id)))
		if p.x != INF:
			_add_tag({"kind": "note", "anchor": p, "text": tr("SHIELDED"), "col": TideFx.COBALT_HOT, "px": TideFx.SMALL_PX, "prefer": Vector2(0.0, -48.0), "own": true, "state": 1})
	for id in shields_gone:
		var p := at(StringName(String(id)))
		if p.x != INF:
			_add_tag({"kind": "note", "anchor": p, "text": tr("shield gone"), "col": TideFx.DIM, "px": TideFx.SMALL_PX, "prefer": Vector2(0.0, -48.0), "own": true, "state": 1})


func _stamp(id: StringName, word: String, col: Color, kind: String) -> void:
	var p := at(id)
	if p.x == INF:
		return
	_add_tag({"kind": kind, "anchor": p, "text": word, "col": col, "px": TideFx.STAMP_PX, "icon": 12.0, "prefer": Vector2(0.0, STAMP_DROP), "own": true,
		"state": 5 if kind == "stamp_taken" else 3})


## The words of the HOME tag for the forecast marks `m` ({down, taken, falls, home}): the Sites that would be hit, then HOME: "2 Sites DOWN, HOME safe".
func forecast_summary(m: Dictionary) -> String:
	var parts := PackedStringArray()
	var nd := (m.get("down", []) as Array).size()
	var nt := (m.get("taken", []) as Array).size()
	var nf := (m.get("falls", []) as Array).size()
	if nd > 0:
		parts.append(tr("%d Sites DOWN") % nd if nd > 1 else tr("1 Site DOWN"))
	if nt > 0:
		parts.append(tr("%d Sites TAKEN") % nt if nt > 1 else tr("1 Site TAKEN"))
	if nf > 0:
		parts.append(tr("%d Sites fall (no sentry)") % nf if nf > 1 else tr("1 Site falls (no sentry)"))
	var dmg := int(m.get("home", 0))
	parts.append(tr("HOME -%d") % dmg if dmg > 0 else tr("HOME safe"))
	return ", ".join(parts)


## The forecast prediction the player points at, the mismatched sentries and the picked card's fit: rings on the Sites and a tag each where a word is needed.
func _collect_marks() -> void:
	# One summary tag at HOME says what the rings mean ("2 Sites DOWN, HOME safe"); a single marked Site also gets its own word.
	var lone := (fc_marks.get("down", []) as Array).size() + (fc_marks.get("taken", []) as Array).size() + (fc_marks.get("falls", []) as Array).size() == 1
	for id in fc_marks.get("down", []):
		var p := at(StringName(String(id)))
		if p.x == INF:
			continue
		TideFx.forecast_ring(self, p)
		if lone:
			_add_tag({"kind": "note", "anchor": p, "text": tr("would go DOWN"), "col": Palette.TIDE_SITES_LOST, "px": TideFx.SMALL_PX, "prefer": Vector2(0.0, STAMP_DROP + 20.0), "own": true})
	for id in fc_marks.get("taken", []):
		var p := at(StringName(String(id)))
		if p.x == INF:
			continue
		TideFx.forecast_ring(self, p)
		if lone:
			_add_tag({"kind": "note", "anchor": p, "text": tr("would fall"), "col": TideFx.RED, "px": TideFx.SMALL_PX, "prefer": Vector2(0.0, STAMP_DROP + 20.0), "own": true})
	# H7c: a Site hit and left DOWN with no sentry on it falls when the raid closes: every such Site says so (the rule is new to the player).
	for id in fc_marks.get("falls", []):
		var p := at(StringName(String(id)))
		if p.x == INF:
			continue
		TideFx.forecast_falls_ring(self, p)
		_add_tag({"kind": "note", "anchor": p, "text": tr("falls"), "col": TideFx.RED, "px": TideFx.SMALL_PX, "prefer": Vector2(0.0, STAMP_DROP + 20.0), "own": true})
	if not fc_marks.is_empty():
		var hp := at(home)
		if hp.x != INF:
			var dmg := int(fc_marks.get("home", 0))
			var hit_sites := not (fc_marks.get("down", []) as Array).is_empty() or not (fc_marks.get("taken", []) as Array).is_empty() \
				or not (fc_marks.get("falls", []) as Array).is_empty()
			var hc: Color = TideFx.forecast_home_color(dmg, hit_sites)
			TideFx.forecast_home_ring(self, hp, hc)
			_add_tag({"kind": "note", "anchor": hp, "text": forecast_summary(fc_marks), "col": hc, "px": TideFx.LABEL_PX, "prefer": Vector2(0.0, -46.0), "own": true})
	var hov: StringName = overlay.hover_id if overlay != null and is_instance_valid(overlay) else &""
	for id in bad_sentries:
		var p := at(id)
		if p.x == INF:
			continue
		TideFx.bad_sentry(self, p)
		_add_tag({"kind": "bad", "anchor": p, "text": String(bad_sentries[id]) if hov == id or bad_sentries.size() == 1 else tr("does nothing"),
			"col": TideFx.RED, "px": TideFx.SMALL_PX, "icon": 12.0, "prefer": Vector2(0.0, -62.0), "own": true})
	for id in ghost_sites:
		var p := at(id)
		if p.x == INF:
			continue
		var g: Dictionary = ghost_sites[id]
		TideFx.ghost_site(self, p, bool(g["useless"]))
		if bool(g["useless"]):
			if hov == id:
				_add_tag({"kind": "bad", "anchor": p, "text": String(g["reason"]), "col": TideFx.RED, "px": TideFx.SMALL_PX, "icon": 12.0, "prefer": Vector2(0.0, -48.0), "own": true})


## "HIT: name" beside each Site the beat hits.
func _collect_impact_tags() -> void:
	for im in impacts:
		var p := at(StringName(String(im["site"])))
		var lab := String(im.get("label", ""))
		if p.x == INF or lab == "":
			continue
		_add_tag({"kind": "note", "anchor": p, "text": lab, "col": im["col"], "px": TideFx.LABEL_PX, "prefer": Vector2(70.0, -30.0), "own": true,
			"state": 4 if lab.begins_with("FALLS") else 2})


func _draw_sentries() -> void:
	for id in sentries:
		var p := at(id)
		if p.x == INF:
			continue
		var c: Array = sentries[id]
		TideFx.sentry_post(self, p, String(c[0]), String(c[1]))


func _draw_home() -> void:
	var hp := at(home)
	var cp := at(core)
	TideFx.home_marks(self, hp, hp.x != INF, ghost_home, home_tiers, home_cols, CAND_LETTERS, cp, cp.x != INF)


func _draw_impacts() -> void:
	if impacts.is_empty():
		return
	var animated := Motion.seconds_live(&"raid_step_beat") > 0.0
	var k := fmod(float(Time.get_ticks_msec()) / 1000.0 / TideFx.look().impact_period, 1.0) if animated else 0.5
	for im in impacts:
		var p := at(StringName(String(im["site"])))
		if p.x == INF:
			continue
		TideFx.impact(self, p, im["col"], k)


func _draw_bursts() -> void:
	for e in bursts:
		var p := spot(StringName(String(e["site"])))
		if p.x == INF:
			continue
		TideFx.burst(self, String(e["kind"]), p, e["col"], _age(e), size)


func _draw_flights() -> void:
	for f in flights:
		var from := spot(StringName(String(f["site"])))
		if from.x == INF:
			continue
		var k := _age(f)
		var e := k * k * (3.0 - 2.0 * k)
		var to: Vector2 = f["to"]
		var pos := from.lerp(to, e) + Vector2(0.0, -TideFx.look().flight_arc * sin(PI * e))
		TideFx.flight_card(self, pos, lerpf(1.4, 0.8, e))


func _draw_preview() -> void:
	if preview.is_empty():
		return
	var head := String(preview[0])
	var p := Vector2.INF
	var q := Vector2.INF
	var hunters := PackedVector2Array()
	match head:
		"DEPLOY":
			p = at(StringName(preview[2]))
		"REDEPLOY":
			p = at(StringName(preview[1]))
			q = at(StringName(preview[2]))
		"SACRIFICE":
			p = at(StringName(preview[1]))
		"JAM", "JAM_B":
			for b in beams:
				if String(b["role"]) == "hunter":
					var pts := path(_beam_ids(b))
					if pts.size() > 1:
						hunters.append(pts[0])
	TideFx.preview_ghost(self, head, String(preview[1]) if head == "DEPLOY" else "", preview_type, p, q, at(home), hunters)
