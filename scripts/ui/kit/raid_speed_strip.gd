class_name RaidSpeedStrip
extends Control
## ART-6 3A: the raid's Speed / Skip controls as a CRT terminal strip (ART_BIBLE v2 §4.8:
## "the terminal strip below START DEFENSE; START peels away in playout and the strip stays";
## round 19 `ui19.speed_terminal`, round 21 `speed_position` picked "below"). In setup it is
## greyed out (nothing plays yet): this preview draws the same strip the playout's live
## buttons wear (`style_button`), so the controls never move. Takes no input.

const KEYS: Array[String] = ["1x", "2x", "4x", "SKIP"] # TR
const STEP_IDLE := "STEP -- / %d" # TR
## The strip's height and key widths (px at 1.0), the gap between keys.
const HEIGHT := 34.0
const KEY_W := 40.0
const SKIP_W := 56.0
const GAP := 6.0
const PAD := 6.0
## Greyed-out alpha in setup.
const IDLE_ALPHA := 0.45

var steps_max: int = 30


func _init(p_steps_max: int = 30) -> void:
	steps_max = p_steps_max
	name = "SpeedStrip"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var k := Settings.text_scale
	custom_minimum_size = Vector2((KEY_W * 3.0 + SKIP_W + GAP * 4.0 + PAD * 2.0) * k + _step_w(), HEIGHT * k)


func _step_w() -> float:
	return Palette.mono().get_string_size(tr(STEP_IDLE) % steps_max, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.BODY)).x + GAP * 2.0


func _draw() -> void:
	var k := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	var a := IDLE_ALPHA
	draw_rect(r, Color(Palette.TERMINAL_BG, Palette.TERMINAL_BG.a * a))
	draw_rect(r, Color(Palette.TERMINAL_EDGE, a), false, 1.0)
	var x := PAD * k
	var px := UiTheme.font_px(UiTheme.BODY)
	var f := Palette.mono()
	for key in KEYS:
		var w := (SKIP_W if key == "SKIP" else KEY_W) * k
		var box := Rect2(x, PAD * k * 0.6, w, size.y - PAD * k * 1.2)
		draw_rect(box, Color(Palette.NET_CYAN, 0.12 * a))
		draw_rect(box, Color(Palette.NET_CYAN, a), false, 1.0)
		var word := tr(key)
		var tw := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		draw_string(f, Vector2(box.get_center().x - tw * 0.5, box.get_center().y + f.get_ascent(px) * 0.4), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(Palette.NET_CYAN, a))
		x += w + GAP * k
	draw_string(f, Vector2(x + GAP * k, size.y * 0.5 + f.get_ascent(px) * 0.4), tr(STEP_IDLE) % steps_max, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(Palette.TERMINAL_TEXT, a))


## Dresses a live playout button `b` as a key of this strip: navy key with a cyan edge, lit
## (cyan fill, navy letters) while pressed / toggled on (§2.10: ON = cyan fill plus a word).
static func style_button(b: Button) -> void:
	var off := StyleBoxFlat.new()
	off.bg_color = Color(Palette.NET_CYAN, 0.1)
	off.border_color = Palette.NET_CYAN
	off.set_border_width_all(1)
	off.content_margin_left = PAD * Settings.text_scale
	off.content_margin_right = PAD * Settings.text_scale
	off.content_margin_top = 2.0
	off.content_margin_bottom = 2.0
	var on := off.duplicate() as StyleBoxFlat
	on.bg_color = Palette.NET_CYAN
	var hot := off.duplicate() as StyleBoxFlat
	hot.bg_color = Color(Palette.NET_CYAN, 0.25)
	for st in [&"normal", &"disabled"]:
		b.add_theme_stylebox_override(st, off)
	b.add_theme_stylebox_override(&"hover", hot)
	for st in [&"pressed", &"hover_pressed"]:
		b.add_theme_stylebox_override(st, on)
	b.add_theme_font_override(&"font", Palette.mono())
	b.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.BODY))
	b.add_theme_color_override(&"font_color", Palette.NET_CYAN)
	b.add_theme_color_override(&"font_hover_color", Palette.TEXT_HI)
	b.add_theme_color_override(&"font_pressed_color", Palette.NIGHT_SKY)
	b.add_theme_color_override(&"font_hover_pressed_color", Palette.NIGHT_SKY)
	b.add_theme_color_override(&"font_disabled_color", Color(Palette.NET_CYAN, IDLE_ALPHA))
