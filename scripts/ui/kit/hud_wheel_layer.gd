class_name HudWheelLayer
extends Control
## ART-2 2D (ART_BIBLE v2 §3.1): the HUD over the wheels.
## - The nudge buttons on one line above each wheel: counter-clockwise on the left,
##   clockwise on the right, the key under each ([Q] / [E] on the wheel the nudge keys
##   drive). Round glass buttons rimmed in the wheel's colour; the hovered one lights, a
##   drop target for an aimed card glows lime. The wheel views place and hit-test them
##   (WheelView.hud_results: `arrows`, `arrow_center`, `zone_at`), so clicks, drops and
##   their tooltips stay the views'; this layer only draws them.
## - The result chips (D15, HudResultChips) beside each wheel's HP number, placed every frame
##   where the view draws it (the wheels slide, grow and shrink).
## View only: it draws what the views and the scene give it.

## Button radius, rim and the glyph's share of the radius (px at text scale 1.0).
const BUTTON_R := 17.0
const RIM_PX := 2.5
const GLYPH_SHARE := 0.75
## The inner ring's mark: a dot in the glyph (share of the radius).
const INNER_DOT := 0.16
const KEY_FONT := 13
## plan1 W2-A5: the ring word under a key letter (INNER / OUTER).
const RING_WORD_FONT := 10
## B2: the key letters' keyline outside the glyph, in 1080p (board) px (B1a Q2: at least 3).
const KEYLINE_1080 := 3.0
## The chips' gap from the HP number and from the screen's edge (px at text scale 1.0).
const CHIP_GAP := 10.0
const EDGE := 4.0

## The views it draws for (the scene sets it): a Callable returning Array[WheelView].
var views_of: Callable
## The result chip row per view (created on demand).
var rows: Dictionary = {}
## 1C's atlas glyphs on the buttons (nodes: the SDF shader needs its own material).
var _glyphs: Array[GlyphIcon] = []


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _views() -> Array:
	if not views_of.is_valid():
		return []
	return views_of.call()


## The result chip row beside `view`'s HP (made the first time).
func row_for(view: WheelView) -> HudResultChips:
	var row: HudResultChips = rows.get(view)
	if row == null or not is_instance_valid(row):
		row = HudResultChips.new()
		row.name = "ResultChips"
		add_child(row)
		rows[view] = row
	return row


## W2-A2: a row of its own per satellite docked at `view`'s wheel (its HP, block, statuses), under
## the wheel's row, led by the satellite's name: {view: {satellite id: row}}.
var sat_rows: Dictionary = {}


## The satellite `sat_id`'s chip row under `view`'s row (made the first time), led by `name_text`.
func sat_row_for(view: WheelView, sat_id: StringName, name_text: String) -> HudResultChips:
	var per: Dictionary = sat_rows.get(view, {})
	var row: HudResultChips = per.get(sat_id)
	if row == null or not is_instance_valid(row):
		row = HudResultChips.new()
		row.name = "SatelliteChips"
		add_child(row)
		per[sat_id] = row
		sat_rows[view] = per
	row.set_standing([{"text": name_text, "color": HudSkin.CHIP_OTHER}])
	return row


## Empties `view`'s satellite rows (a new preview sets the ones it needs).
func clear_sat_rows(view: WheelView) -> void:
	for row in (sat_rows.get(view, {}) as Dictionary).values():
		if is_instance_valid(row):
			(row as HudResultChips).set_result([], "", "")


## Every row back to its live chips, motions at rest (a replay ended or was skipped).
func release_rows() -> void:
	for v in rows.keys():
		var row: HudResultChips = rows[v]
		if is_instance_valid(row):
			row.release()


## True while a row's tick, fade or flip plays.
func motion_running() -> bool:
	for v in rows.keys():
		var row: HudResultChips = rows[v]
		if is_instance_valid(row) and row.motion_running():
			return true
	return false


func _process(_delta: float) -> void:
	place_rows()
	# M14 perf slice: the buttons laid out once a frame (each costs the views' layout), and
	# redrawn only when what they draw changes (they redrew every frame of every fight).
	var bs := buttons()
	_place_glyphs(bs)
	var sig := draw_signature(bs)
	if sig != _drawn_sig:
		_drawn_sig = sig
		queue_redraw()


## M14 perf slice: the last drawn draw_signature().
var _drawn_sig: Array = []


## M14 perf slice: everything _draw reads (the text scale and skin, the layer's place, and per
## button its place, ring, direction, rim colour, hover, drop and key hint), so the layer redraws
## only when one of them changes.
func draw_signature(bs: Array[Dictionary] = buttons()) -> Array:
	var origin := get_global_rect().position
	var mouse := get_global_mouse_position()
	var sig: Array = [Settings.text_scale, Settings.palette_skin, origin]
	for b in bs:
		var wv: WheelView = b["view"]
		var r: float = b["radius"]
		var zone := {"kind": "arrow", "ring": b["ring"], "direction": b["direction"]}
		var hot := WheelView._zone_is([wv.hover_zone], zone) or Vector2(b["center"]).distance_to(mouse) <= r
		sig.append_array([b["center"], r, b["ring"], b["direction"], wv.wheel_color, hot,
			WheelView._zone_is(wv.valid_zones, zone), wv.global_position,
			wv.arrow_hint_rect(int(b["ring"]), int(b["direction"])), wv.arrow_hints.get(int(b["direction"]), "")])
	return sig


## The buttons' rotate glyphs (picto_spin_ccw / picto_spin), one node per button.
func _place_glyphs(bs: Array[Dictionary] = buttons()) -> void:
	while _glyphs.size() > bs.size():
		var g: GlyphIcon = _glyphs.pop_back()
		g.queue_free()
	while _glyphs.size() < bs.size():
		var g := HudSkin.glyph_node(&"", HudSkin.GLYPH_MIN_PX, HudSkin.TERMINAL_TEXT)
		add_child(g)
		_glyphs.append(g)
	var origin := get_global_rect().position
	var mouse := get_global_mouse_position()
	for k in bs.size():
		var b: Dictionary = bs[k]
		var g: GlyphIcon = _glyphs[k]
		var box := maxf(HudSkin.GLYPH_MIN_PX, float(b["radius"]) * 2.0 * GLYPH_SHARE)
		var cell := GlyphIcon.cell_size_for(box)
		# M14 perf slice: each setter redraws (or swaps the material): set only what changed.
		var gn := HudSkin.glyph_name("ccw" if int(b["direction"]) < 0 else "cw")
		if g.glyph != gn:
			g.glyph = gn
		if g.box_px != box:
			g.box_px = box
		var hot := Vector2(b["center"]).distance_to(mouse) <= float(b["radius"])
		var fill := HudSkin.TERMINAL_HI if hot else HudSkin.TERMINAL_TEXT
		if g.fill != fill:
			g.fill = fill
		g.position = Vector2(b["center"]) - origin - cell * 0.5


## W2-A2: global rects the chip rows keep clear of when another place for them is free (the scene gives
## the stickers, SEND IT and the hand); empty = none.
var avoid: Callable


## Puts each row beside its view's HP number: right of it, else left of it, else under it (the first
## place that is on screen and clear of the rows already placed and of `avoid`; under it when none
## is); a row whose view went is freed. A wheel's satellite rows stack under its row.
func place_rows() -> void:
	var s := Settings.text_scale
	var origin := get_global_rect().position
	var screen := get_global_rect()
	var blockers: Array = avoid.call() if avoid.is_valid() else []
	blockers.append_array(_drone_boxes())
	var placed: Array[Rect2] = []
	for v in rows.keys():
		var row: HudResultChips = rows[v]
		if not is_instance_valid(v) or not is_instance_valid(row):
			if is_instance_valid(row):
				row.queue_free()
			rows.erase(v)
			for srow in (sat_rows.get(v, {}) as Dictionary).values():
				if is_instance_valid(srow):
					(srow as Node).queue_free()
			sat_rows.erase(v)
			continue
		var wv := v as WheelView
		row.visible = wv.is_visible_in_tree() and wv.combatant != null and not wv.defeated()
		if not row.visible:
			continue
		row.set_standing(wv.standing_chips())  # B2 (D2): what the hub used to write
		var hp: Rect2 = wv.hp_layout()["hp"]
		var g := Rect2(wv.global_position + hp.position, hp.size)
		var gap := CHIP_GAP * s
		var cands: Array[Vector2] = [
			Vector2(g.end.x + gap, g.get_center().y - row.size.y * 0.5),
			Vector2(g.position.x - gap - row.size.x, g.get_center().y - row.size.y * 0.5),
		]
		var under := Vector2(g.get_center().x - row.size.x * 0.5, g.end.y + CHIP_GAP * 0.5 * s)
		var at := under
		var found := false
		for c in cands:
			if _free(Rect2(c, row.size), screen, s, placed, blockers):
				at = c
				found = true
				break
		if not found and cands[0].x + row.size.x <= screen.end.x - EDGE * s:
			at = cands[0]  # nothing is free: the place that was always allowed
		at.x = clampf(at.x, screen.position.x + EDGE * s, maxf(screen.position.x + EDGE * s, screen.end.x - EDGE * s - row.size.x))
		row.position = at - origin
		var mine := Rect2(at, row.size)
		if not row.chips.is_empty() or not row.standing.is_empty():
			placed.append(mine)
		# W2-A2: the wheel's satellites, one row each: under the row (left edges together, else right edges
		# together), else beside it on the left. A row with no free place stays folded into the tooltip
		# (the scene writes the satellite's changes there too) rather than cover a button or a wheel.
		var below := mine.end.y + CHIP_GAP * 0.4 * s
		var keep_clear: Array = blockers.duplicate()
		for other in _views():
			var ow := other as WheelView
			if ow != null and is_instance_valid(ow) and ow.is_visible_in_tree() and ow.combatant != null:
				keep_clear.append(ow.wheel_rect())
				var ohp: Rect2 = ow.hp_layout()["hp"]
				keep_clear.append(Rect2(ow.global_position + ohp.position, ohp.size))
		var ids: Array = (sat_rows.get(v, {}) as Dictionary).keys()
		ids.sort()
		for sid in ids:
			var srow: HudResultChips = sat_rows[v][sid]
			if not is_instance_valid(srow):
				continue
			srow.visible = false
			if srow.chips.is_empty():
				continue
			var spots: Array[Vector2] = [
				Vector2(at.x, below),
				Vector2(mine.end.x - srow.size.x, below),
				Vector2(mine.position.x - gap - srow.size.x, mine.position.y),
			]
			for spot in spots:
				var sr := Rect2(spot, srow.size)
				if _free(sr, screen, s, placed, keep_clear):
					srow.position = spot - origin
					srow.visible = true
					placed.append(sr)
					below += srow.size.y + CHIP_GAP * 0.4 * s
					break


## The boxes of every bloomed drone or satellite token as drawn (a row never sits on one).
func _drone_boxes() -> Array:
	var out: Array = []
	for v in _views():
		var wv := v as WheelView
		if wv == null or not is_instance_valid(wv) or wv.combatant == null or wv.attachments == null or wv.attachments.dock == null:
			continue
		var dock: DroneDock = wv.attachments.dock
		for e in dock.entries():
			var b := float(dock.bloom.get(int(e["slot"]), 0.0))
			var at: Vector2 = (e["tile"] as Vector2).lerp(e["mini"], b)
			var r := float(e["mini_r"]) * lerpf(DroneDock.BLOOM_FROM, 1.0, b)
			out.append(Rect2(dock.global_position + at - Vector2(r, r), Vector2(r, r) * 2.0))
	return out


## Whether a row at `r` is on screen (with the edge margin) and clear of `placed` and `blockers`.
func _free(r: Rect2, screen: Rect2, s: float, placed: Array[Rect2], blockers: Array) -> bool:
	if not screen.grow(-EDGE * s).encloses(r):
		return false
	for p in placed:
		if p.intersects(r):
			return false
	for b in blockers:
		if (b as Rect2).intersects(r):
			return false
	return true


## Every button on screen: {view, ring, direction, center (global), radius}.
func buttons() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var r := BUTTON_R * minf(Settings.text_scale, WheelView.NUDGE_SCALE_MAX)
	for v in _views():
		var wv := v as WheelView
		if wv == null or not is_instance_valid(wv) or not wv.is_visible_in_tree() or not wv.hud_results:
			continue
		for ar in wv.arrows():
			out.append({"view": wv, "ring": int(ar["ring"]), "direction": int(ar["direction"]),
				"center": wv.arrow_center(int(ar["ring"]), int(ar["direction"])), "radius": r})
	return out


func _draw() -> void:
	var s := Settings.text_scale
	var origin := get_global_rect().position
	var mouse := get_global_mouse_position()
	var kf := roundi(KEY_FONT * s)
	var mono := HudSkin.mono()
	for b in buttons():
		var wv: WheelView = b["view"]
		var c: Vector2 = Vector2(b["center"]) - origin
		var r: float = b["radius"]
		var zone := {"kind": "arrow", "ring": b["ring"], "direction": b["direction"]}
		var hot := WheelView._zone_is([wv.hover_zone], zone) or Vector2(b["center"]).distance_to(mouse) <= r
		var drop := WheelView._zone_is(wv.valid_zones, zone)
		# plan1 W2-A5: the pair Q / E drive wears a lit acid rim (its key letters show under it).
		var keyed := wv.arrow_hint_rect(int(b["ring"]), int(b["direction"])).has_area()
		var rim := HudSkin.FOCUS if drop else (Palette.CELL_ACID if keyed else wv.wheel_color)
		draw_circle(c + Vector2(2.0, 3.0) * s, r, Color(Palette.NIGHT_SKY, 0.5))
		draw_circle(c, r, PaletteSkins.chrome(Palette.TERMINAL_BG_HOT) if hot else PaletteSkins.chrome(HudSkin.TERMINAL_BG))
		draw_arc(c, r, 0.0, TAU, 32, rim.lightened(0.25) if hot else rim, RIM_PX * s * (1.4 if hot or drop else 1.0), true)
		var gc := HudSkin.TERMINAL_HI if hot or drop else HudSkin.TERMINAL_TEXT
		if HudSkin.glyph_name("ccw" if int(b["direction"]) < 0 else "cw") == &"":
			HudSkin.draw_glyph(self, "ccw" if int(b["direction"]) < 0 else "cw", c, r * GLYPH_SHARE, gc)
		if int(b["ring"]) == RC.RingScope.INNER:
			# The inner ring's pair: a dot under the glyph.
			draw_circle(c + Vector2(0.0, r * 0.72), r * INNER_DOT, gc)
		var hr := wv.arrow_hint_rect(int(b["ring"]), int(b["direction"]))
		if hr.has_area():
			var key := key_letter(String(wv.arrow_hints.get(int(b["direction"]), "")))
			var kw := mono.get_string_size(key, HORIZONTAL_ALIGNMENT_LEFT, -1, kf).x
			var at := wv.global_position + Vector2(hr.get_center().x - kw * 0.5, hr.position.y) - origin
			# B2 (B1a Q2 ruling): a word over the world wears its ink keyline (>= 3 px at 1080p).
			draw_string_outline(mono, at + Vector2(0.0, mono.get_ascent(kf)), key, HORIZONTAL_ALIGNMENT_LEFT, -1, kf, keyline_px(), Palette.INK)
			HighContrast.draw_text(self, mono, at + Vector2(0.0, mono.get_ascent(kf)), key, HORIZONTAL_ALIGNMENT_LEFT, -1, kf, HudSkin.TERMINAL_HI)
			# plan1 W2-A5: on a wheel with an inner ring, the word under the key says which ring it nudges.
			if wv.combatant != null and wv.combatant.wheel != null and wv.combatant.wheel.has_inner_ring():
				var word := tr("INNER") if int(b["ring"]) == RC.RingScope.INNER else tr("OUTER")
				var wf := roundi(RING_WORD_FONT * s)
				var ww := mono.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, wf).x
				var wat := Vector2(at.x + kw * 0.5 - ww * 0.5, at.y + mono.get_height(kf) - 1.0) + Vector2(0.0, mono.get_ascent(wf))
				draw_string_outline(mono, wat, word, HORIZONTAL_ALIGNMENT_LEFT, -1, wf, keyline_px(), Palette.INK)
				HighContrast.draw_text(self, mono, wat, word, HORIZONTAL_ALIGNMENT_LEFT, -1, wf, Palette.CELL_ACID)


## B2 (designer Q2; concept HUD v4): the key under a nudge button is its letter alone ("[Q]" -> "Q").
static func key_letter(hint: String) -> String:
	return hint.trim_prefix("[").trim_suffix("]")


## B2 (B1a Q2 ruling): the key letters' ink keyline, as Godot's outline size (it straddles the
## glyph's edge: KEYLINE_1080 board px outside it, so twice that), in canvas px.
static func keyline_px() -> int:
	return ceili(KEYLINE_1080 * 2.0 * GreasePencilMark.BOARD_TO_CANVAS * Settings.text_scale)
