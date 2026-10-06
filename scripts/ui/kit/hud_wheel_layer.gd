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
	_place_glyphs()
	queue_redraw()


## The buttons' rotate glyphs (picto_spin_ccw / picto_spin), one node per button.
func _place_glyphs() -> void:
	var bs := buttons()
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
		g.glyph = HudSkin.glyph_name("ccw" if int(b["direction"]) < 0 else "cw")
		g.box_px = box
		var hot := Vector2(b["center"]).distance_to(mouse) <= float(b["radius"])
		g.fill = HudSkin.TERMINAL_HI if hot else HudSkin.TERMINAL_TEXT
		g.position = Vector2(b["center"]) - origin - cell * 0.5


## Puts each row beside its view's HP number (right of it; under it when the screen's edge
## is too close); a row whose view went is freed.
func place_rows() -> void:
	var s := Settings.text_scale
	var origin := get_global_rect().position
	var screen := get_global_rect()
	for v in rows.keys():
		var row: HudResultChips = rows[v]
		if not is_instance_valid(v) or not is_instance_valid(row):
			if is_instance_valid(row):
				row.queue_free()
			rows.erase(v)
			continue
		var wv := v as WheelView
		row.visible = wv.is_visible_in_tree() and wv.combatant != null and not wv.defeated()
		if not row.visible:
			continue
		row.set_standing(wv.standing_chips())  # B2 (D2): what the hub used to write
		var hp: Rect2 = wv.hp_layout()["hp"]
		var g := Rect2(wv.global_position + hp.position, hp.size)
		var at := Vector2(g.end.x + CHIP_GAP * s, g.get_center().y - row.size.y * 0.5)
		if at.x + row.size.x > screen.end.x - EDGE * s:
			at = Vector2(g.get_center().x - row.size.x * 0.5, g.end.y + CHIP_GAP * 0.5 * s)
		at.x = clampf(at.x, screen.position.x + EDGE * s, maxf(screen.position.x + EDGE * s, screen.end.x - EDGE * s - row.size.x))
		row.position = at - origin


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
		var rim := HudSkin.FOCUS if drop else wv.wheel_color
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
			draw_string(mono, at + Vector2(0.0, mono.get_ascent(kf)), key, HORIZONTAL_ALIGNMENT_LEFT, -1, kf, HudSkin.TERMINAL_HI)


## B2 (designer Q2; concept HUD v4): the key under a nudge button is its letter alone ("[Q]" -> "Q").
static func key_letter(hint: String) -> String:
	return hint.trim_prefix("[").trim_suffix("]")


## B2 (B1a Q2 ruling): the key letters' ink keyline, as Godot's outline size (it straddles the
## glyph's edge: KEYLINE_1080 board px outside it, so twice that), in canvas px.
static func keyline_px() -> int:
	return ceili(KEYLINE_1080 * 2.0 * GreasePencilMark.BOARD_TO_CANVAS * Settings.text_scale)
