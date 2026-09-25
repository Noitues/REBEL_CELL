class_name CrewCard
extends PanelContainer
## An operative's dossier card (reference: the crew Polaroids laid on the deck): taped
## paper with the Polaroid, the name in marker, "// CLASS // RANK" tags, an HP strip,
## the kit in numbers and the operative's orders underneath. `orders` holds the buttons
## the scene adds. A downed operative's card is greyed and stamped.

var polaroid: Polaroid
var orders: VBoxContainer
var dead: bool = false
var tilt: float = 0.0
var hp_frac: float = 1.0
var stamp_text: String = ""


func _init(p_name: String, p_class: String, rank: int, hp: int, max_hp: int, detail: String, p_tilt: float = 0.0) -> void:
	tilt = p_tilt
	hp_frac = clampf(float(hp) / maxf(1.0, max_hp), 0.0, 1.0)
	custom_minimum_size = Vector2(196, 0)
	var style := UiTheme.box(Palette.NOTE_PAPER, Color(Palette.INK, 0.45), 1, 10, 12)
	style.shadow_color = Palette.SHADOW
	style.shadow_size = 7
	style.shadow_offset = Vector2(4, 5)
	add_theme_stylebox_override("panel", style)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 4)
	add_child(box)
	polaroid = Polaroid.new("%s R%d" % [p_name, rank], "[%s PORTRAIT]" % p_class.to_upper(), -2.0 + tilt)
	polaroid.custom_minimum_size = Vector2(120, 144)
	polaroid.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(polaroid)
	var name_label := Label.new()
	name_label.text = p_name.to_upper()
	name_label.add_theme_font_override("font", Palette.marker())
	name_label.add_theme_font_size_override("font_size", 20)
	name_label.add_theme_color_override("font_color", Palette.INK)
	name_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	box.add_child(name_label)
	var tags := Label.new()
	tags.text = "// %s // RANK %d" % [p_class.to_upper(), rank]
	tags.add_theme_color_override("font_color", Color(Palette.INK, 0.75))
	tags.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	tags.add_theme_font_size_override("font_size", 12)
	box.add_child(tags)
	var hp_strip := Control.new()
	hp_strip.custom_minimum_size = Vector2(0, 16)
	hp_strip.draw.connect(func() -> void:
		var r := Rect2(Vector2(0, 4), Vector2(hp_strip.size.x, 8))
		hp_strip.draw_rect(r, Color(Palette.INK, 0.15))
		hp_strip.draw_rect(Rect2(r.position, Vector2(r.size.x * hp_frac, r.size.y)), Palette.CELL_PINK if hp_frac < 0.35 else Color("#2a8f3c"))
		hp_strip.draw_rect(r, Color(Palette.INK, 0.6), false, 1.0))
	box.add_child(hp_strip)
	var info := Label.new()
	info.text = detail
	info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	info.custom_minimum_size.x = 176
	info.add_theme_color_override("font_color", Palette.INK)
	info.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0))
	info.add_theme_font_size_override("font_size", 12)
	box.add_child(info)
	orders = VBoxContainer.new()
	orders.add_theme_constant_override("separation", 4)
	box.add_child(orders)


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = tilt


func _draw() -> void:
	draw_rect(Rect2(size.x * 0.5 - 24, -7, 48, 14), Palette.NOTE_TAPE)
	if dead or stamp_text != "":
		var t := stamp_text if stamp_text != "" else "FLATLINED"
		draw_set_transform(Vector2(size.x * 0.5, 90), -0.3, Vector2.ONE)
		draw_rect(Rect2(-80, -20, 160, 40), Color(Palette.CELL_PINK, 0.85), false, 3.0)
		draw_string(Palette.display(), Vector2(-80, 10), t, HORIZONTAL_ALIGNMENT_CENTER, 160, 26, Color(Palette.CELL_PINK, 0.9))
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
