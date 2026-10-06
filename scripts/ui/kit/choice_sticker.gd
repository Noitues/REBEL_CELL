class_name ChoiceSticker
extends Control
## ART-9 4A (ART_BIBLE v2 §4.11 "choices as sticker buttons"; round 31 `event_screen`): an event
## choice as the concept's plate sticker (event.plate_button: the dark plate, the yellow number
## tab, the white die-cut border, gloss and shadow; MainframeArt "plate", "plate_hover" when the
## choice is hovered or focused) drawn behind the button's words, its middle stretched to the
## words, and the choice's number on the tab. `theme_for` gives the buttons' room and lettering
## (a theme type, so the outcome row's room keeps it). A focused choice also gets the acid edge.

const TYPE := &"ChoiceSticker"
## The tab's width (px at scale 1), the words' lettering and the room round them.
const TAB_W := 44.0
const WORDS_PX := 22
const PAD := Vector2(14, 8)
## The words grow with the text size this far (Anton at 22 px is already a headline).
const WORDS_MAX_SCALE := 1.5
## The plate art: its body's height and the shadow / border room round it (concept px), and the
## tab and right edge kept when its middle stretches.
const ART_BODY_H := 90.0
const ART_PAD := Vector4(18, 14, 30, 34)
const ART_LEFT := 100.0
const ART_RIGHT := 50.0

var number: int = 1
var text_scale: float = 1.0


func _init(p_number: int = 1, ts: float = 1.0) -> void:
	name = "ChoiceNumber"
	number = p_number
	text_scale = ts
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	show_behind_parent = true
	set_anchors_preset(Control.PRESET_FULL_RECT)


func _draw() -> void:
	var b := get_parent() as Button
	var off := b != null and b.disabled
	var hot := b != null and not off and (b.has_focus() or b.is_hovered())
	var r := Rect2(Vector2.ZERO, size)
	var k := r.size.y / ART_BODY_H
	var art := r.grow_individual(ART_PAD.x * k, ART_PAD.y * k, ART_PAD.z * k, ART_PAD.w * k)
	MainframeArt.draw_h3(self, "plate_hover" if hot else "plate", art, ART_LEFT, ART_RIGHT, Color(Palette.NO_TINT, 0.55) if off else Palette.NO_TINT)
	if hot and b.has_focus():
		draw_rect(r.grow(3), Palette.CELL_ACID, false, 2.0)
	var f := Palette.display()
	var fs := roundi(WORDS_PX * 1.4 * minf(text_scale, WORDS_MAX_SCALE))
	var tab := Rect2(Vector2.ZERO, Vector2(TAB_W * minf(text_scale, WORDS_MAX_SCALE), r.size.y))
	draw_string(f, Vector2(tab.position.x, tab.get_center().y + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5), str(number), HORIZONTAL_ALIGNMENT_CENTER, tab.size.x, fs, Palette.INK)


func _notification(what: int) -> void:
	if what == NOTIFICATION_PARENTED:
		var b := get_parent() as Button
		if b != null:
			for sig in [&"mouse_entered", &"mouse_exited", &"focus_entered", &"focus_exited"]:
				b.connect(sig, queue_redraw)


## The theme with the choices' room and lettering at text scale `ts` (the plate is the art).
static func theme_for(ts: float) -> Theme:
	var t := Theme.new()
	t.set_type_variation(TYPE, &"Button")
	var w := minf(ts, WORDS_MAX_SCALE)
	for st: StringName in [&"normal", &"hover", &"pressed", &"hover_pressed", &"focus", &"disabled"]:
		var sb := StyleBoxEmpty.new()
		sb.content_margin_left = (TAB_W + PAD.x) * w
		sb.content_margin_right = PAD.x * w
		sb.content_margin_top = PAD.y * w
		sb.content_margin_bottom = PAD.y * w
		t.set_stylebox(st, TYPE, sb)
	t.set_font(&"font", TYPE, Palette.display())
	t.set_font_size(&"font_size", TYPE, roundi(WORDS_PX * w))
	t.set_color(&"font_color", TYPE, Palette.TEXT_HI)
	t.set_color(&"font_hover_color", TYPE, Palette.TEXT_HI)
	t.set_color(&"font_focus_color", TYPE, Palette.TEXT_HI)
	t.set_color(&"font_pressed_color", TYPE, Palette.CELL_ACID)
	t.set_color(&"font_disabled_color", TYPE, Palette.TEXT_LO)
	t.set_color(&"font_outline_color", TYPE, Palette.INK)
	t.set_constant(&"outline_size", TYPE, 4)
	# the outcome row's lettering under the words (mono, like a terminal chip)
	t.set_font(&"font", &"Label", Palette.mono())
	t.set_font_size(&"font_size", &"Label", roundi(UiTheme.BASE_SIZE * ts))
	return t
