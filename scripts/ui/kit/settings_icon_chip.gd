class_name SettingsIconChip
extends Button
## B2 (integration review section c, "TURN strip key hints, Settings corner chip"): the fight's
## Settings corner control is a small terminal icon chip, 32 px square at 1080p (scaled with the
## text up to VerbSticker.SCALE_MAX): navy glass, the terminal edge (bright while hot), a gear in
## the terminal's text colour, the kit's lime focus brackets. No words on it: its name and key
## ([Esc]) are its tooltip (designer Q2: key hints in the tooltip). The gear is drawn: no concept
## made a settings icon (the glyph atlas has none; `seg_accelerator`'s gear is a segment's mark,
## and bible 5.2 keeps silhouettes unique). View only: a press is the scene's.

## The chip's side at 1080p (board px) and the gear's shares of it: its outer and inner radius,
## its hub hole, its tooth count and each tooth's share of the pitch.
const SIDE_1080 := 32.0
const GEAR_OUTER := 0.34
const GEAR_INNER := 0.26
const GEAR_HOLE := 0.1
const GEAR_TEETH := 8
const TOOTH_SHARE := 0.45


func _init() -> void:
	name = "SettingsChip"
	flat = true
	focus_mode = Control.FOCUS_ALL
	for st in ["normal", "hover", "pressed", "focus", "disabled", "hover_pressed"]:
		add_theme_stylebox_override(st, StyleBoxEmpty.new())
	mouse_entered.connect(queue_redraw)
	mouse_exited.connect(queue_redraw)
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)
	_refit()


func _ready() -> void:
	Settings.changed.connect(_refit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_refit):
		Settings.changed.disconnect(_refit)


## The chip's side now (canvas px).
static func side_px() -> float:
	return SIDE_1080 * GreasePencilMark.BOARD_TO_CANVAS * clampf(Settings.text_scale, 1.0, VerbSticker.SCALE_MAX)


func _refit() -> void:
	custom_minimum_size = Vector2.ONE * side_px()
	queue_redraw()


## The gear's outline (local px) round `c`, radius `r`.
static func gear_points(c: Vector2, r: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	var pitch := TAU / GEAR_TEETH
	for i in GEAR_TEETH:
		var a := i * pitch
		var half := pitch * TOOTH_SHARE * 0.5
		for p in [[a - half, GEAR_INNER], [a - half, GEAR_OUTER], [a + half, GEAR_OUTER], [a + half, GEAR_INNER]]:
			var ang: float = p[0]
			pts.append(c + Vector2(cos(ang), sin(ang)) * r * float(p[1]) / GEAR_OUTER)
	return pts


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var hot := is_hovered() or button_pressed
	HudSkin.draw_terminal_panel(self, r, HudSkin.TERMINAL_HI if hot else PaletteSkins.chrome(HudSkin.TERMINAL_EDGE), PaletteSkins.chrome(Palette.TERMINAL_BG_HOT) if hot else PaletteSkins.chrome(HudSkin.TERMINAL_BG))
	var c := r.get_center()
	var side := minf(size.x, size.y)
	var col := HudSkin.TERMINAL_HI if hot else HudSkin.TERMINAL_TEXT
	draw_colored_polygon(gear_points(c, side * GEAR_OUTER), col)
	draw_circle(c, side * GEAR_HOLE, PaletteSkins.chrome(HudSkin.TERMINAL_BG))
	if has_focus():
		KitState.draw_frame(self, r, KitState.FOCUS)
