class_name IconMark
extends Control
## A StatIcon on a Button, or on its own beside a drawn control (H21 #13: menus and
## Skip / Leave buttons that carried their meaning in words only). `attach` gives the
## button an empty icon slot (a transparent 1x1 ImageTexture with a size override) so its
## text moves over, and the mark draws the icon in that slot at the button's font size (it
## follows the text scale); in a terminal menu the icon takes the chevron's place. The
## button keeps its text, key hint and tooltip; the icon kind is in the button's
## "icon_kind" meta (tests). Draw-only.

## Icon side relative to the button's font size.
const SIZE_FACTOR := 1.15
## A standalone mark's radius relative to its size.
const FILL := 0.45

var kind: StringName = &""
## Transparent = the button's font colour.
var color: Color = Color(0, 0, 0, 0)
## The button's empty icon slot: a transparent texture sized to the icon (a
## PlaceholderTexture2D would draw Godot's checkerboard).
var _slot: ImageTexture = null


func _init(p_kind: StringName = &"", p_color: Color = Color(0, 0, 0, 0)) -> void:
	name = "IconMark"
	kind = p_kind
	color = p_color
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


## Puts icon `p_kind` on button `b` (replacing an earlier mark's kind); returns the mark.
static func attach(b: Button, p_kind: StringName, p_color: Color = Color(0, 0, 0, 0)) -> IconMark:
	b.set_meta(&"icon_kind", p_kind)
	var old := b.get_node_or_null(^"IconMark") as IconMark
	if old != null:
		old.kind = p_kind
		old.color = p_color
		old.queue_redraw()
		return old
	var m := IconMark.new(p_kind, p_color)
	var clear := Image.create_empty(1, 1, false, Image.FORMAT_RGBA8)
	clear.fill(Color(0, 0, 0, 0))
	m._slot = ImageTexture.create_from_image(clear)
	b.icon = m._slot
	b.add_child(m)
	m.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	m._fit()
	return m


## A mark of its own, `side` px square (beside a control that draws its own label).
static func standalone(p_kind: StringName, side: float, p_color: Color = Color(0, 0, 0, 0)) -> IconMark:
	var m := IconMark.new(p_kind, p_color)
	m.custom_minimum_size = Vector2(side, side)
	m.size = m.custom_minimum_size
	return m


## The icon kind on button `b` (&"" when it has none).
static func kind_of(b: Control) -> StringName:
	return StringName(b.get_meta(&"icon_kind", &"")) if b != null else &""


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		_fit()
		queue_redraw()
	elif what == NOTIFICATION_RESIZED:
		queue_redraw()


func _px() -> float:
	var b := get_parent() as Button
	if b == null:
		return minf(size.x, size.y)
	return roundf(b.get_theme_font_size(&"font_size") * SIZE_FACTOR)


func _fit() -> void:
	if _slot == null:
		return
	var px := _px()
	if Vector2(_slot.get_size()) != Vector2(px, px):
		_slot.set_size_override(Vector2i(roundi(px), roundi(px)))
		var b := get_parent() as Button
		if b != null:
			b.update_minimum_size()


func _draw() -> void:
	var b := get_parent() as Button
	if b == null or _slot == null:
		var own := color if color.a > 0.0 else Palette.TERMINAL_TEXT
		StatIcon.draw(self, size * 0.5, minf(size.x, size.y) * FILL, kind, own)
		return
	var sb := b.get_theme_stylebox(&"normal")
	var left := sb.get_margin(SIDE_LEFT) if sb != null else 0.0
	var px := float(_slot.get_width())
	var col := color
	if col.a <= 0.0:
		col = b.get_theme_color(&"font_disabled_color" if b.disabled else &"font_color")
	StatIcon.draw(self, Vector2(left + px * 0.5, size.y * 0.5), px * FILL, kind, col)
