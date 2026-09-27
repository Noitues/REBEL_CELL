class_name RaidFxLayer
extends Control
## Raid execution drawn on the city map (Animation pass ANIM-5, handoff 4.15): threats
## travel their street routes between nodes, guns fire traces, ICE LOCK rings close on a
## threat and freeze it, a DECOY's lure pulls a threat aside, damage numbers pop off
## nodes, HOLDS / DISABLED / SEIZED / BREACHED stamps flip onto nodes, the home server's
## integrity drains with a lag bar, and a Seized node tints the streets round it in the
## corporation's colour until the city's real tint spreads (NeonCity).
##
## A child of a CityMapOverlay (it pans and zooms with the city; sizes are screen px x the
## overlay's `screen_k`). The RaidPlayoutPanel feeds it beats (RaidBeats, built from the
## resolver's events) on its own clock, which runs at Motion.speed (1x / 2x / 4x). The
## city backdrop keeps its own clock. View only: it reads events and the resolved raid,
## never game state, and uses no RNG.

## Node outcomes (RaidResolver) and their stamp words (the raid summary's words, in the
## same order), translated when drawn.
const STAMP_OUTCOMES: Array[String] = ["holds", "disabled", "seized", "passed", "breached"]
const STAMP_TEXT: Array[String] = ["HOLDS", "DISABLED", "SEIZED", "PASSED", "BREACHED"] # TR
## Screen px (x screen_k): stamp lettering, its padding, tilt (degrees) and lift over
## the icon; damage numbers; traces; hit rings; the home bar and its gap under CORE.
const STAMP_FONT := 14
const STAMP_PAD := 4.0
const STAMP_TILT := -6.0
const STAMP_LIFT := 30.0
const NUMBER_FONT := 22
const TRACE_WIDTH := 2.5
const HIT_RING := 10.0
const FROST_RING := 13.0
const HOME_BAR := Vector2(64, 7)
const HOME_BAR_GAP := 8.0
const PULL_DASH := 6.0
## A threat token is the map's marker this much bigger, with a glow this much wider.
const TOKEN_SCALE := 1.5
const TOKEN_GLOW := 1.8
## Alpha of a Seized node's corporate tint disc (its reach is CityInfluence.RADIUS lots).
const TINT_ALPHA := 0.24
const TINT_RINGS := 24

var overlay: CityMapOverlay
## The playout clock (seconds at 1x): advances by frame time x Motion.speed.
var clock: float = 0.0
var threat_color: Color = Palette.CORP_SOLACE
var home_id: StringName = &""
var home_max: int = 1
## Home integrity shown now (after the hits played so far) and where its lag bar starts.
var home_value: int = 0
var _home_from: int = 0
var _home_lag_t0: float = -INF
var _tokens: Dictionary = {}  # threat id (String) -> token
var _fx: Array[Dictionary] = []
var _stamps: Dictionary = {}  # site id (String) -> {"word", "color", "t0", "dur"}
var _tints: Array[Dictionary] = []
var _tint_fade_t0: float = INF
var _results: Dictionary = {}
var _owner_done: bool = false


func _init(p_overlay: CityMapOverlay = null) -> void:
	overlay = p_overlay
	name = "RaidFx"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Starts a playout: the resolved raid (`results`: RaidResult.to_dict / campaign.last_raid),
## the home Site, its full integrity and the threats' colour.
func setup(results: Dictionary, p_home: StringName, p_home_max: int, color: Color) -> void:
	_results = results
	home_id = p_home
	home_max = maxi(1, p_home_max)
	home_value = int(results.get("home_before", home_max))
	_home_from = home_value
	threat_color = color
	clock = 0.0
	_tokens.clear()
	_fx.clear()
	_stamps.clear()
	_tints.clear()
	_tint_fade_t0 = INF
	_owner_done = false
	queue_redraw()


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	# After the playout the layer keeps its own time (the tint fade, the last numbers).
	if _owner_done:
		clock += delta
	if _tint_fade_t0 == INF and not _tints.is_empty() and overlay != null and overlay.city != null and overlay.city.influence_pin == null \
			and overlay.city.showing_current_look():
		_tint_fade_t0 = clock
	queue_redraw()


## Every beat at its end at once (Skip, reduce effects, headless).
func finish_all() -> void:
	clock = maxf(clock, _last_end())
	queue_redraw()


## The playout has ended: from now on the layer runs its own clock (tint fade).
func release() -> void:
	_owner_done = true


func _last_end() -> float:
	var end := 0.0
	for id in _tokens:
		var t: Dictionary = _tokens[id]
		for k in ["enter_at", "dead_at"]:
			if t.has(k):
				end = maxf(end, float(t[k]) + float(t.get(k + "_dur", 0.0)))
		if t.has("move"):
			end = maxf(end, float(t["move"]["t0"]) + float(t["move"]["dur"]))
	for f in _fx:
		end = maxf(end, float(f["t0"]) + float(f["dur"]))
	for id in _stamps:
		end = maxf(end, float(_stamps[id]["t0"]) + float(_stamps[id]["dur"]))
	return maxf(end, _home_lag_t0 + RaidBeats.raw_seconds(&"home_lag"))


## Plays one beat (RaidBeats.timeline) starting at clock time `t0`.
func play_beat(b: Dictionary, t0: float) -> void:
	var e: Dictionary = b["event"]
	var dur := float(b["dur"])
	match String(b["type"]):
		"threat_enters":
			_tokens[String(e["threat"])] = {"site": StringName(e["site"]), "enter_at": t0, "enter_at_dur": dur}
		"move":
			var tok: Dictionary = _tokens.get_or_add(String(e["threat"]), {"site": StringName(e["from"])})
			tok["move"] = {"from": StringName(e["from"]), "to": StringName(e["to"]), "t0": t0, "dur": dur,
				"decoy": StringName(e.get("target", "")) if bool(e.get("decoy", false)) else &""}
			tok["site"] = StringName(e["to"])
			tok.erase("frozen")
		"held":
			_fx.append({"kind": "frost", "threat": String(e["threat"]), "t0": t0, "dur": dur})
			if _tokens.has(String(e["threat"])):
				_tokens[String(e["threat"])]["frozen"] = true
		"ice_lock", "station_hold":
			_fx.append({"kind": "lock", "threat": String(e["threat"]), "t0": t0, "dur": dur})
			if _tokens.has(String(e["threat"])):
				_tokens[String(e["threat"])]["frozen"] = true
		"shot":
			_fx.append({"kind": "trace", "site": StringName(e["site"]), "threat": String(e["threat"]), "t0": t0, "dur": dur})
			_fx.append({"kind": "hit", "threat": String(e["threat"]), "t0": t0 + dur * 0.5, "dur": RaidBeats.raw_seconds(&"raid_hit_effect")})
		"threat_destroyed":
			var tok: Dictionary = _tokens.get(String(e["threat"]), {})
			if not tok.is_empty():
				tok["dead_at"] = t0
				tok["dead_at_dur"] = dur
		"node_hit", "cascade":
			var site := StringName(e["site"])
			_number(site, "-%d" % int(e.get("damage", 0)), Palette.CELL_PINK, t0, dur)
			if site == home_id:
				_home_hit(int(e.get("damage", 0)), t0)
		"home_hit":
			_number(home_id, "-%d" % int(e.get("damage", 0)), Palette.CELL_PINK, t0, dur)
			_home_hit(int(e.get("damage", 0)), t0)
		"station_regen":
			_number(StringName(e["site"]), "+%d" % int(e.get("amount", 0)), Palette.CELL_ACID, t0, dur)
		"disabled":
			_stamp(StringName(e["site"]), "disabled", Palette.CELL_PINK, t0, dur)
		"seized":
			_stamp(StringName(e["site"]), "seized", Palette.RESIST_GOLD, t0, dur)
			_tints.append({"site": StringName(e["site"]), "t0": t0, "dur": RaidBeats.raw_seconds(&"influence_spread")})
		"home_lost":
			_stamp(home_id, "breached", Palette.CELL_PINK, t0, dur)
		"raid_end":
			var flip := RaidBeats.raw_seconds(&"raid_flip")
			var ids: Array = _results.get("nodes", {}).keys()
			ids.sort()
			for id in ids:
				var sid := StringName(String(id))
				if sid == home_id or _stamps.has(String(sid)):
					continue
				var outcome := String(_results["nodes"][id].get("outcome", "holds"))
				_stamp(sid, outcome, Palette.CELL_ACID if outcome == "holds" else Palette.CELL_PINK, t0, flip)
			if home_id != &"" and not _stamps.has(String(home_id)):
				var hit := int(_results.get("home_after", home_value)) < int(_results.get("home_before", home_value))
				_stamp(home_id, "breached" if hit else "holds", Palette.CELL_PINK if hit else Palette.CELL_ACID, t0, flip)
			# The end state is the resolved raid's (never a sum that could drift).
			if _results.has("home_after"):
				var after := int(_results["home_after"])
				if after != home_value:
					_home_hit(home_value - after, t0)
	queue_redraw()


func _number(site: StringName, text: String, col: Color, t0: float, dur: float) -> void:
	_fx.append({"kind": "number", "site": site, "text": text, "color": col, "t0": t0, "dur": dur})


func _stamp(site: StringName, outcome: String, col: Color, t0: float, dur: float) -> void:
	_stamps[String(site)] = {"word": stamp_text(outcome), "color": col, "t0": t0, "dur": dur}


## The stamp word for node outcome `outcome` (untranslated; drawn translated).
static func stamp_text(outcome: String) -> String:
	var i := STAMP_OUTCOMES.find(outcome)
	return STAMP_TEXT[i] if i >= 0 else outcome.to_upper()


func _home_hit(damage: int, t0: float) -> void:
	_home_from = _home_lag_value()
	home_value = maxi(0, home_value - damage)
	_home_lag_t0 = t0


## The home bar's white lag segment now (it trails home_value by `home_lag`).
func _home_lag_value() -> float:
	var e := Motion.entry(&"home_lag")
	if e == null or _home_lag_t0 == -INF:
		return home_value
	var u := clampf((clock - _home_lag_t0 - e.delay) / maxf(e.duration, 0.001), 0.0, 1.0)
	return float(Tween.interpolate_value(float(_home_from), float(home_value - _home_from), u, 1.0, e.trans, e.ease))


# --- Checks (tests) ---------------------------------------------------------------------------

## The stamp word on Site `site` ("" when none).
func stamp_word(site: StringName) -> String:
	return String(_stamps.get(String(site), {}).get("word", ""))


## Every stamp (site id -> word).
func stamps() -> Dictionary:
	var out := {}
	for id in _stamps:
		out[id] = _stamps[id]["word"]
	return out


## Where threat `id` stands (after its last move) and whether it is still in the raid.
func token_site(id: String) -> StringName:
	return StringName(_tokens.get(id, {}).get("site", &""))


func token_alive(id: String) -> bool:
	var t: Dictionary = _tokens.get(id, {})
	return not t.is_empty() and (not t.has("dead_at") or clock < float(t["dead_at"]))


## The threats standing on the map now, site id -> ids (sorted).
func standing() -> Dictionary:
	var out := {}
	var ids := _tokens.keys()
	ids.sort()
	for id in ids:
		if token_alive(String(id)):
			(out.get_or_add(_tokens[id]["site"], []) as Array).append(String(id))
	return out


# --- Drawing ----------------------------------------------------------------------------------

func _draw() -> void:
	if overlay == null or overlay.city == null:
		return
	var k := overlay.screen_k()
	_draw_tints(k)
	var at := _token_positions()
	for f in _fx:
		if f["kind"] == "trace":
			_draw_trace(f, at, k)
	for id in _tokens:
		_draw_token(String(id), at, k)
	for f in _fx:
		match String(f["kind"]):
			"lock", "frost":
				_draw_lock(f, at, k)
			"hit":
				_draw_hit(f, at, k)
			"number":
				_draw_number(f, k)
	for id in _stamps:
		_draw_stamp(StringName(id), _stamps[id], k)
	_draw_home(k)


func _u(t0: float, dur: float) -> float:
	return clampf((clock - t0) / maxf(dur, 0.001), 0.0, 1.0)


func _eased(id: StringName, u: float) -> float:
	var e := Motion.entry(id)
	return float(Tween.interpolate_value(0.0, 1.0, u, 1.0, e.trans, e.ease)) if e != null else u


## Every token's position now (local px), INF for one not on the map or not shown.
func _token_positions() -> Dictionary:
	var out := {}
	var resting := {}
	var ids := _tokens.keys()
	ids.sort()
	for id in ids:
		var t: Dictionary = _tokens[id]
		var mv: Dictionary = t.get("move", {})
		var moving: bool = not mv.is_empty() and clock < float(mv["t0"]) + float(mv["dur"])
		var site: StringName = mv["from"] if moving and clock <= float(mv["t0"]) else t["site"]
		if not moving or clock <= float(mv["t0"]):
			(resting.get_or_add(site, []) as Array).append(id)
	for site in resting:
		var group: Array = resting[site]
		for i in group.size():
			out[group[i]] = overlay.marker_slot(site, i, group.size())
	for id in ids:
		var t: Dictionary = _tokens[id]
		var mv: Dictionary = t.get("move", {})
		if mv.is_empty() or clock <= float(mv["t0"]) or clock >= float(mv["t0"]) + float(mv["dur"]):
			continue
		out[id] = _along_move(mv, _eased(&"raid_move", _u(float(mv["t0"]), float(mv["dur"]))))
	return out


## A point `u` (0..1) along a move: from the threat's slot over its node, down the street
## route, up to the slot over the next node; a DECOY's pull veers it sideways mid-way.
func _along_move(mv: Dictionary, u: float) -> Vector2:
	var a := overlay.marker_slot(mv["from"], 0, 1)
	var b := overlay.marker_slot(mv["to"], 0, 1)
	if a.x == INF or b.x == INF:
		return b if u >= 1.0 else Vector2(INF, INF)
	var pts := PackedVector2Array([a])
	for p in overlay.route_between(mv["from"], mv["to"]):
		pts.append(overlay.grid_point_local(p))
	pts.append(b)
	var total := 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	var d := u * total
	var at := b
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if d <= seg:
			at = pts[i].lerp(pts[i + 1], d / maxf(seg, 0.001))
			break
		d -= seg
	if mv["decoy"] != &"":
		var side := (b - a).orthogonal().normalized()
		at += side * sin(u * PI) * Motion.amplitude(&"decoy_fire") * overlay.screen_k()
	return at


func _diamond(p: Vector2, s: float) -> PackedVector2Array:
	return PackedVector2Array([p + Vector2(0, -s), p + Vector2(s * 0.9, 0), p + Vector2(0, s), p + Vector2(-s * 0.9, 0)])


func _draw_token(id: String, at: Dictionary, k: float) -> void:
	var t: Dictionary = _tokens[id]
	var p: Vector2 = at.get(id, Vector2(INF, INF))
	if p.x == INF:
		return
	var enter := float(t.get("enter_at", -INF))
	if clock < enter:
		return
	var s := CityMapOverlay.MARKER_SIZE * k * TOKEN_SCALE
	var alpha := 1.0
	if enter > -INF:
		var pop := _u(enter, float(t.get("enter_at_dur", 0.0)))
		s *= lerpf(Motion.amplitude(&"node_pop"), 1.0, _eased(&"node_pop", pop)) if pop < 1.0 else 1.0
		alpha = pop if pop < 1.0 else 1.0
	if t.has("dead_at"):
		var du := _u(float(t["dead_at"]), float(t.get("dead_at_dur", 0.0)))
		if du >= 1.0:
			return
		s *= lerpf(1.0, Motion.amplitude(&"raid_hit_effect"), du)
		alpha *= 1.0 - du
	var mv: Dictionary = t.get("move", {})
	if not mv.is_empty() and mv["decoy"] != &"" and clock > float(mv["t0"]) and clock < float(mv["t0"]) + float(mv["dur"]):
		var lure := overlay.icon_at(mv["decoy"])
		if lure.x != INF:
			_dashed(lure, p, Color(Palette.RESIST_GOLD, 0.8), 1.5 * k, PULL_DASH * k)
	var dia := _diamond(p, s)
	draw_circle(p, s * TOKEN_GLOW, Color(threat_color, 0.25 * alpha))
	draw_colored_polygon(dia, Color(threat_color, alpha))
	draw_polyline(dia + PackedVector2Array([dia[0]]), Color(Palette.PAPER, alpha), 1.2 * k)
	if t.get("frozen", false):
		draw_arc(p, FROST_RING * k, 0, TAU, 20, Color(Palette.NET_CYAN, 0.8 * alpha), 2.0 * k)


func _draw_trace(f: Dictionary, at: Dictionary, k: float) -> void:
	var u := _u(float(f["t0"]), float(f["dur"]))
	if clock < float(f["t0"]) or u >= 1.0:
		return
	var from := overlay.icon_at(f["site"])
	var to: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if from.x == INF or to.x == INF:
		return
	var a := 1.0 - u
	draw_line(from, to, Color(Palette.CELL_ACID, 0.35 * a), TRACE_WIDTH * 3.0 * k)
	draw_line(from, to, Color(Palette.PAPER, a), TRACE_WIDTH * k)
	draw_circle(from, 3.0 * k, Color(Palette.CELL_ACID, a))


func _draw_lock(f: Dictionary, at: Dictionary, k: float) -> void:
	if clock < float(f["t0"]):
		return
	var u := _u(float(f["t0"]), float(f["dur"]))
	if f["kind"] == "frost" and u >= 1.0:
		return
	var p: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if p.x == INF:
		return
	var rest := FROST_RING * k
	if f["kind"] == "lock":
		if u >= 1.0:
			return
		var r := lerpf(rest * Motion.amplitude(&"ice_lock_ring"), rest, _eased(&"ice_lock_ring", u))
		draw_arc(p, r, 0, TAU, 28, Color(Palette.NET_CYAN, 0.35 + 0.65 * u), 3.0 * k)
		for q in 6:
			var d := Vector2.from_angle(TAU * q / 6.0)
			draw_line(p + d * r, p + d * (r + 4.0 * k), Palette.NET_CYAN, 1.5 * k)
	else:
		draw_arc(p, rest * (1.0 + 0.3 * (1.0 - u)), 0, TAU, 20, Color(Palette.NET_CYAN, 1.0 - u), 2.0 * k)


func _draw_hit(f: Dictionary, at: Dictionary, k: float) -> void:
	var u := _u(float(f["t0"]), float(f["dur"]))
	if clock < float(f["t0"]) or u >= 1.0:
		return
	var p: Vector2 = at.get(String(f["threat"]), Vector2(INF, INF))
	if p.x == INF:
		return
	var r := HIT_RING * k * lerpf(1.0, Motion.amplitude(&"raid_hit_effect"), _eased(&"raid_hit_effect", u))
	draw_arc(p, r, 0, TAU, 20, Color(Palette.PAPER, 1.0 - u), 2.5 * k)
	for q in 4:
		var d := Vector2.from_angle(PI * 0.25 + q * PI * 0.5)
		draw_line(p + d * r * 0.6, p + d * r * 1.2, Color(Palette.CELL_ACID, 1.0 - u), 2.0 * k)


func _draw_number(f: Dictionary, k: float) -> void:
	var u := _u(float(f["t0"]), float(f["dur"]))
	if clock < float(f["t0"]) or u >= 1.0:
		return
	var p := overlay.icon_at(f["site"])
	if p.x == INF:
		return
	var rise := Motion.amplitude(&"node_damage_number") * k * _eased(&"node_damage_number", u)
	var fs := maxi(1, roundi(NUMBER_FONT * Settings.text_scale * k))
	var font := Palette.display()
	var text := String(f["text"])
	var w := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var at := p + Vector2(-w * 0.5, -CityMapOverlay.ICON_RADIUS * k - rise)
	var a := 1.0 if u < 0.66 else (1.0 - u) / 0.34
	draw_string_outline(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(4.0 * k)), Color(0, 0, 0, 0.9 * a))
	draw_string(font, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(f["color"], a))


func _draw_stamp(site: StringName, s: Dictionary, k: float) -> void:
	if clock < float(s["t0"]):
		return
	var p := overlay.icon_at(site)
	if p.x == INF:
		return
	var u := _u(float(s["t0"]), float(s["dur"]))
	var angle := lerpf(Motion.amplitude(&"raid_flip"), 0.0, _eased(&"raid_flip", u))
	var sx := maxf(0.05, cos(deg_to_rad(angle)))
	var word := CityMapOverlay.tr_word(String(s["word"]))
	var fs := maxi(1, roundi(STAMP_FONT * Settings.text_scale * k))
	var font := Palette.display()
	var size := font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs) + Vector2(STAMP_PAD, STAMP_PAD) * 2.0 * k
	var col: Color = s["color"]
	draw_set_transform(p + Vector2(0, -STAMP_LIFT * k - CityMapOverlay.ICON_RADIUS * k), deg_to_rad(STAMP_TILT), Vector2(sx, 1.0))
	var box := Rect2(-size * 0.5, size)
	draw_rect(box, Color(Palette.NIGHT_SKY, 0.85))
	draw_rect(box, col, false, 2.0 * k)
	draw_string(font, box.position + Vector2(STAMP_PAD * k, STAMP_PAD * k + font.get_ascent(fs)), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
	draw_set_transform(Vector2.ZERO)


func _draw_home(k: float) -> void:
	if home_id == &"":
		return
	var p := overlay.icon_at(home_id)
	if p.x == INF:
		return
	var w := HOME_BAR.x * k
	var h := HOME_BAR.y * k
	var r := Rect2(p + Vector2(-w * 0.5, CityMapOverlay.ICON_RADIUS_BIG * k + HOME_BAR_GAP * k), Vector2(w, h))
	draw_rect(r.grow(1.5 * k), Color(0, 0, 0, 0.85))
	var lag := clampf(_home_lag_value() / home_max, 0.0, 1.0)
	var now := clampf(float(home_value) / home_max, 0.0, 1.0)
	draw_rect(Rect2(r.position, Vector2(w * lag, h)), Palette.PAPER)
	draw_rect(Rect2(r.position, Vector2(w * now, h)), Palette.CELL_ACID if now > 0.5 else Palette.CELL_PINK)


## Seized nodes' corporate tint: a soft disc grows over the streets round the node and
## holds (the city's own tint is baked at the raid's end) until the city's spread starts.
func _draw_tints(_k: float) -> void:
	var fade := 1.0
	if _tint_fade_t0 != INF:
		fade = 1.0 - _u(_tint_fade_t0, RaidBeats.raw_seconds(&"influence_crossfade"))
		if fade <= 0.0:
			return
	var reach := CityInfluence.RADIUS * NeonCity.TILE_A
	for t in _tints:
		if clock < float(t["t0"]):
			continue
		var c := overlay.icon_at(t["site"])
		if c.x == INF:
			continue
		var r := reach * _eased(&"influence_spread", _u(float(t["t0"]), float(t["dur"])))
		var mid := Color(threat_color, TINT_ALPHA * fade)
		var edge := Color(threat_color, 0.0)
		for q in TINT_RINGS:
			var a0 := TAU * q / TINT_RINGS
			var a1 := TAU * (q + 1) / TINT_RINGS
			var p0 := c + Vector2(cos(a0), sin(a0) * 0.5) * r
			var p1 := c + Vector2(cos(a1), sin(a1) * 0.5) * r
			draw_polygon(PackedVector2Array([c, p0, p1]), PackedColorArray([mid, edge, edge]))


func _dashed(a: Vector2, b: Vector2, col: Color, width: float, dash: float) -> void:
	var length := a.distance_to(b)
	var dir := (b - a) / maxf(length, 0.001)
	var t := 0.0
	while t < length:
		draw_line(a + dir * t, a + dir * minf(t + dash, length), col, width)
		t += dash * 2.0
