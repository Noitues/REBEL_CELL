class_name HudResultChips
extends Control
## ART-2 2D, D15 (ART_BIBLE v2 §3.1): the result chips beside a wheel's HP number, what SEND
## IT does to that wheel if pressed now (`ResultChipModel`): `[-14]` red boxed, `(4 shield)`
## blue, `+4 shield` green, `-1 RAM`, `☠×2`. They replace the forecast tag and the NEXT plate:
## hovering shows the breakdown (each wheel's slice and landing, guard, hub passive). A change
## flips the row (`intent_flip`); through a SEND IT replay the row holds the forecast it showed,
## ticks each chip as the replay does it (`forecast_tick`) and fades (`forecast_fade`), the
## tag's motion entries carried over. View only: it draws what the scene gives it.

## Chip height, lettering, gaps, padding and the icon's size (px at text scale 1.0).
const CHIP_H := 26.0
const NUMBER_FONT := 20
const GAP := 6.0
const PAD := 5.0
const ICON_BOX := 16.0
const ICON_GAP := 3.0
## The lethal skull's size as a share of the chip's height.
const SKULL_SHARE := 0.28
## Alpha of a ticked chip and its check's stroke (px).
const TICKED_ALPHA := 0.45
const CHECK_PX := 2.5

var chips: Array[Dictionary] = []
## The breakdown tooltip: its title and its lines.
var tip_title: String = ""
var tip_body: String = ""
## The replay's held row (empty = the live one), its ticks (chip index -> 0..1) and alpha.
var held: Array[Dictionary] = []
var holding: bool = false
var ticks: Dictionary = {}
var held_alpha: float = 1.0
## The flip as the row changes (1 = flat).
var flip: float = 1.0
var flips: int = 0
var _sig: String = ""
var _sets: int = 0
var _tweens: Dictionary = {}
## 1C's glyph nodes in the row (HudSkin.glyph_node).
var _glyphs: Array[GlyphIcon] = []


## Puts a line before the breakdown (a hovered card's name, what the row said before it).
func prepend_note(line: String) -> void:
	if line == "" or tooltip_text.begins_with(line):
		return
	tooltip_text = line + ("\n" + tooltip_text if tooltip_text != "" else "")


## MotionSkip: the ticks whole, the fade done, the flip flat (the hold itself stays until
## the replay ends: the scene releases it).
func complete_motion() -> void:
	if _tweens.has(&"fade"):
		held_alpha = 0.0
	for k in _tweens:
		var tw: Tween = _tweens[k]
		if tw != null and tw.is_valid():
			tw.kill()
	_tweens.clear()
	for i in ticks:
		ticks[i] = 1.0
	flip = 1.0
	queue_redraw()


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	MotionSkip.register_passive(self)  # a press that ends a motion ends the ticks and the flip


## Shows `p_chips` with the breakdown `title` / `body` (translated by the caller). New
## content flips in (also after the row was empty, e.g. once a replay's wheel settles); the
## row's first content (a fight's start) and the same content re-set (a hover) don't.
func set_result(p_chips: Array, title: String, body: String) -> void:
	tip_title = title
	tip_body = body
	tooltip_text = body if body != "" else ""
	var sig := signature(p_chips)
	chips.assign(p_chips)
	if sig != _sig and sig != "" and _sets > 0 and not holding:
		_flip()
	_sets += 1
	_sig = sig
	_fit()
	queue_redraw()


## The row's content as text (a change flips it; the same row re-set doesn't).
static func signature(p_chips: Array) -> String:
	var parts := PackedStringArray()
	for c in p_chips:
		parts.append("%s:%s" % [String(c["kind"]), ResultChipModel.label(c)])
	return "|".join(parts)


## The chips drawn now: the held forecast while a replay plays, else the live row.
func shown() -> Array[Dictionary]:
	return held if holding else chips


## A SEND IT replays: the row keeps what it showed (`p_chips`), ready to tick.
func hold(p_chips: Array) -> void:
	held.assign(p_chips.duplicate(true))
	holding = true
	ticks = {}
	held_alpha = 1.0
	_fit()
	queue_redraw()


## Chip `i` of the held row happened (a check pops on it).
func tick(i: int) -> void:
	if not holding or ticks.has(i):
		return
	if not Motion.live(&"forecast_tick"):
		ticks[i] = 1.0
		queue_redraw()
		return
	ticks[i] = 0.0
	var e := Motion.entry(&"forecast_tick")
	var tw := _tw(StringName("tick_%d" % i))
	tw.tween_method(_set_tick.bind(i), 0.0, 1.0, Motion.seconds(&"forecast_tick")).set_ease(e.ease).set_trans(e.trans)


func _set_tick(v: float, i: int) -> void:
	ticks[i] = v
	queue_redraw()


## The held row fades (the replay has read it out).
func fade() -> void:
	if not holding:
		return
	if not Motion.live(&"forecast_fade"):
		held_alpha = 0.0
		queue_redraw()
		return
	var e := Motion.entry(&"forecast_fade")
	var tw := _tw(&"fade")
	tw.tween_method(_set_alpha, held_alpha, 0.0, Motion.seconds(&"forecast_fade")).set_ease(e.ease).set_trans(e.trans)


func _set_alpha(v: float) -> void:
	held_alpha = v
	queue_redraw()


## The replay ended (or was skipped): the live row again, every motion at rest.
func release() -> void:
	for k in _tweens:
		var tw: Tween = _tweens[k]
		if tw != null and tw.is_valid():
			tw.kill()
	_tweens.clear()
	holding = false
	held = []
	ticks = {}
	held_alpha = 1.0
	flip = 1.0
	_fit()
	queue_redraw()


## True while a tick, fade or flip is playing.
func motion_running() -> bool:
	for k in _tweens:
		var tw: Tween = _tweens[k]
		if tw != null and tw.is_valid() and tw.is_running():
			return true
	return false


func _flip() -> void:
	flips += 1
	if not Motion.live(&"intent_flip"):
		flip = 1.0
		return
	var e := Motion.entry(&"intent_flip")
	var tw := _tw(&"flip")
	tw.tween_method(func(v: float) -> void: flip = v; queue_redraw(), 0.0, 1.0, Motion.seconds(&"intent_flip")).set_ease(e.ease).set_trans(e.trans)


func _tw(key: StringName) -> Tween:
	var old: Tween = _tweens.get(key)
	if old != null and old.is_valid():
		old.kill()
	var tw := create_tween()
	_tweens[key] = tw
	return tw


static func _ts() -> float:
	return Settings.text_scale


## The lettering size of the numbers.
static func font_px() -> int:
	return roundi(NUMBER_FONT * _ts())


## A chip's pieces, left to right: {lead (atlas glyph before the words), words, glyph (atlas
## glyph after them), mark (a drawn mark when there is no atlas glyph), close (")")}.
static func parts(c: Dictionary) -> Dictionary:
	var kind := StringName(c["kind"])
	var icon := String(c.get("icon", ""))
	var out := {"lead": &"", "words": ResultChipModel.label(c), "glyph": HudSkin.glyph_name(icon), "mark": "", "close": ""}
	if icon != "" and out["glyph"] == &"":
		out["mark"] = icon
	if kind == ResultChipModel.ABSORBED:
		out["close"] = ")"
	if kind == ResultChipModel.STATUS or kind == ResultChipModel.CLEARS:
		var g: StringName = HudSkin.STATUS_GLYPHS.get(int(c["status"]), &"")
		if g != &"":
			out["lead"] = g
			# The glyph stands for the status's character: the words keep the count (or "?").
			out["words"] = ("?" if bool(c.get("random", false)) else "×%d" % int(c["count"])) if kind == ResultChipModel.STATUS else "×"
			if kind == ResultChipModel.CLEARS:
				out["lead"] = &""
				out["glyph"] = g
	return out


## The glyph box in a chip (px; never under the 16 px glyph rule).
static func glyph_px() -> float:
	return maxf(HudSkin.GLYPH_MIN_PX, ICON_BOX * _ts())


## A chip's width: its words, its glyphs and its padding.
static func chip_width(c: Dictionary) -> float:
	var s := _ts()
	var p := parts(c)
	var f := HudSkin.display()
	var w := f.get_string_size(String(p["words"]), HORIZONTAL_ALIGNMENT_LEFT, -1, font_px()).x + PAD * 2.0 * s
	for key in ["lead", "glyph"]:
		if p[key] != &"":
			w += glyph_px() + ICON_GAP * s
	if String(p["mark"]) != "":
		w += glyph_px() + ICON_GAP * s
	if String(p["close"]) != "":
		w += f.get_string_size(String(p["close"]), HORIZONTAL_ALIGNMENT_LEFT, -1, font_px()).x
	if bool(c.get("lethal", false)):
		w += CHIP_H * SKULL_SHARE * 2.4 * s
	return w


## Each chip's rect in the row (local), in order.
func chip_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var x := 0.0
	var h := CHIP_H * _ts()
	for c in shown():
		var w := chip_width(c)
		out.append(Rect2(Vector2(x, 0.0), Vector2(w, h)))
		x += w + GAP * _ts()
	return out


func _fit() -> void:
	var rs := chip_rects()
	var w := 0.0 if rs.is_empty() else rs[rs.size() - 1].end.x
	custom_minimum_size = Vector2(w, CHIP_H * _ts())
	size = custom_minimum_size
	_layout_glyphs()


## The colour a chip is drawn in.
static func chip_color(c: Dictionary) -> Color:
	match StringName(c["kind"]):
		ResultChipModel.DAMAGE:
			return HudSkin.CHIP_DAMAGE
		ResultChipModel.ABSORBED:
			return HudSkin.CHIP_ABSORBED
		ResultChipModel.GAINED, ResultChipModel.HEALED, ResultChipModel.EVADE:
			return HudSkin.CHIP_GAIN
		ResultChipModel.ODDS:
			return HudSkin.CHIP_OTHER
		ResultChipModel.RAM, ResultChipModel.HEAT, ResultChipModel.HP_OTHER:
			return HudSkin.CHIP_GAIN if bool(c.get("good", false)) else HudSkin.CHIP_OTHER
	return HudSkin.CHIP_GAIN if bool(c.get("good", false)) else HudSkin.CHIP_DAMAGE


## The ink of chip `i` now (its colour; the damage chip's words are white on its red box).
func _ink(i: int, c: Dictionary) -> Color:
	var a := held_alpha if holding else 1.0
	var t := float(ticks.get(i, 0.0)) if holding else 0.0
	var ca := a * (1.0 - (1.0 - TICKED_ALPHA) * t)
	var col := HudSkin.TERMINAL_HI if StringName(c["kind"]) == ResultChipModel.DAMAGE else chip_color(c)
	return Color(col, ca)


## Each chip's pieces placed (local x of each), shared by the drawing and the glyph nodes.
func _piece_xs(r: Rect2, c: Dictionary) -> Dictionary:
	var s := _ts()
	var p := parts(c)
	var f := HudSkin.display()
	var x := r.position.x + PAD * s
	var out := {}
	if p["lead"] != &"":
		out["lead"] = x
		x += glyph_px() + ICON_GAP * s
	out["words"] = x
	x += f.get_string_size(String(p["words"]), HORIZONTAL_ALIGNMENT_LEFT, -1, font_px()).x + ICON_GAP * s * 0.5
	if p["glyph"] != &"" or String(p["mark"]) != "":
		out["glyph"] = x
		x += glyph_px() + ICON_GAP * s * 0.5
	out["close"] = x
	return out


## 1C's atlas glyphs as nodes (the SDF shader needs its own material): one per glyph in the
## row, placed in their chips, tinted with them.
func _layout_glyphs() -> void:
	var want: Array = []
	var row := shown()
	var rs := chip_rects()
	var gp := glyph_px()
	var h := CHIP_H * _ts()
	for i in row.size():
		var p := parts(row[i])
		var xs := _piece_xs(rs[i], row[i])
		for key in ["lead", "glyph"]:
			if p[key] != &"":
				want.append([p[key], Vector2(float(xs[key]), (h - gp) * 0.5), _ink(i, row[i])])
	while _glyphs.size() > want.size():
		var g: GlyphIcon = _glyphs.pop_back()
		g.queue_free()
	while _glyphs.size() < want.size():
		var g := HudSkin.glyph_node(&"", gp, HudSkin.TERMINAL_HI)
		add_child(g)
		_glyphs.append(g)
	for k in want.size():
		var g: GlyphIcon = _glyphs[k]
		var cell := GlyphIcon.cell_size_for(gp)
		g.glyph = want[k][0]
		g.box_px = gp
		g.fill = want[k][2]
		g.position = Vector2(want[k][1]) - (cell - Vector2(gp, gp)) * 0.5
		g.scale = Vector2(1.0, maxf(0.05, flip))
		g.visible = (held_alpha if holding else 1.0) > 0.0


func _draw() -> void:
	var row := shown()
	if row.is_empty():
		return
	var a := held_alpha if holding else 1.0
	if a <= 0.0:
		return
	var s := _ts()
	var fs := font_px()
	var font := HudSkin.display()
	var h := CHIP_H * s
	if flip < 1.0:
		draw_set_transform(Vector2(0.0, h * 0.5 * (1.0 - flip)), 0.0, Vector2(1.0, maxf(0.05, flip)))
	var rs := chip_rects()
	for i in row.size():
		var c := row[i]
		var r := rs[i]
		var col := chip_color(c)
		var t := float(ticks.get(i, 0.0)) if holding else 0.0
		var ca := a * (1.0 - (1.0 - TICKED_ALPHA) * t)
		var kind := StringName(c["kind"])
		var ink := _ink(i, c)
		match kind:
			ResultChipModel.DAMAGE:
				draw_rect(r, Color(HudSkin.CHIP_DAMAGE, ca))
				draw_rect(r, Color(HudSkin.CHIP_INK, ca), false, 1.5)
			ResultChipModel.GAINED:
				draw_rect(r, Color(HudSkin.CHIP_INK, 0.7 * ca))
				draw_rect(r, Color(col, ca), false, 1.5)
			_:
				draw_rect(r, Color(HudSkin.CHIP_INK, 0.55 * ca))
		var p := parts(c)
		var xs := _piece_xs(r, c)
		var base := r.position.y + (h + font.get_ascent(fs) - font.get_descent(fs)) * 0.5
		var words := String(p["words"])
		draw_string_outline(font, Vector2(float(xs["words"]), base), words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, 2, Color(HudSkin.CHIP_INK, ca))
		draw_string(font, Vector2(float(xs["words"]), base), words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, ink)
		if String(p["mark"]) != "":
			var gp := glyph_px()
			HudSkin.draw_glyph(self, String(p["mark"]), Vector2(float(xs["glyph"]) + gp * 0.5, r.position.y + h * 0.5), gp * 0.5, ink)
		if String(p["close"]) != "":
			draw_string(font, Vector2(float(xs["close"]), base), String(p["close"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, ink)
		if bool(c.get("lethal", false)):
			WheelView.draw_skull(self, Vector2(r.end.x - CHIP_H * SKULL_SHARE * 1.4 * s, r.position.y + h * 0.5), CHIP_H * SKULL_SHARE * s, ink)
		if t > 0.0:
			# The replay did it: a check pops over the chip.
			var cc := r.get_center()
			var k := h * 0.3 * t
			draw_polyline(PackedVector2Array([cc + Vector2(-k, 0), cc + Vector2(-k * 0.3, k * 0.7), cc + Vector2(k, -k * 0.8)]), Color(HudSkin.TERMINAL_HI, a), CHECK_PX * s, true)
	draw_set_transform(Vector2.ZERO)
	_layout_glyphs.call_deferred()


func _make_custom_tooltip(for_text: String) -> Object:
	if for_text == "":
		return null
	return UiTip.make(for_text, tip_title)
