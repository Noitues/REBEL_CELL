class_name PlayResultPlate
extends Control
## S-COMBAT-HUD (designer ruling 2026-10-05): while a card's aim is on its target wheel, the
## result of that play is shown ON the wheel it changes: a terminal plate on the wheel's hub
## (where the grease-pencil aim ends) saying the play ("IF YOU PLAY JOLT"), the wheel's HP
## from -> to and the result chips (D15's `ResultChipModel` row, the same chips as beside
## the HP: the play then SEND IT, held to the real resolve by the tests). The slices it
## changes are circled in grease pencil by the aim (AimLinePencil marks) and the landing is
## CardPreviewOverlay's ghost. No new rule: the scene gives the plate the preview's own
## numbers. Static (it shows with the aim), never covers the hand. View only.

## Padding, the gap between lines and the chamfer (px at text scale 1.0); the caption's and
## the HP line's lettering (px at 1.0); a plate grows with the text up to MAX_SCALE.
const PAD := Vector2(10.0, 6.0)
const LINE_GAP := 3.0
const CAPTION_FONT := 12
const HP_FONT := 26
const MAX_SCALE := 1.3
## The arrow between the HP before and after.
const ARROW := " → "

## {caption, hp_from, hp_to, chips} (see `show_result`); empty = hidden.
var result: Dictionary = {}
var chips_row: HudResultChips


func _init() -> void:
	name = "PlayResultPlate"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	chips_row = HudResultChips.new()
	chips_row.name = "Chips"
	chips_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(chips_row)


static func _s() -> float:
	return minf(Settings.text_scale, MAX_SCALE)


## Shows the play's result centred on `centre` (global): `caption` (translated), the HP
## before and after, and the result chips.
func show_result(p_caption: String, hp_from: int, hp_to: int, p_chips: Array, centre: Vector2) -> void:
	result = {"caption": p_caption, "hp_from": hp_from, "hp_to": hp_to, "chips": p_chips.duplicate(true)}
	chips_row.set_result(p_chips, "", "")
	chips_row.visible = not p_chips.is_empty()
	# The row at the plate's own size (the chips beside the HP grow with the text; the plate
	# stops at MAX_SCALE so it never hides the wheel it is on).
	chips_row.scale = Vector2.ONE * (_s() / maxf(Settings.text_scale, 0.01))
	size = plate_size()
	global_position = (centre - size * 0.5).round()
	var s := _s()
	var row := chips_row.size * chips_row.scale
	chips_row.position = Vector2((size.x - row.x) * 0.5, size.y - PAD.y * s - row.y).round()
	visible = true
	queue_redraw()


## Hides the plate.
func clear() -> void:
	result = {}
	visible = false


## The HP line's words ("40 → 29"; "40" when it stays).
func hp_text() -> String:
	if result.is_empty():
		return ""
	var a := int(result["hp_from"])
	var b := int(result["hp_to"])
	return str(a) if a == b else "%d%s%d" % [a, ARROW, b]


## The plate's size for what it shows.
func plate_size() -> Vector2:
	var s := _s()
	var cap := HudSkin.mono().get_string_size(String(result.get("caption", "")), HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(CAPTION_FONT * s))
	var hp := HudSkin.display().get_string_size(hp_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, roundi(HP_FONT * s))
	var w := maxf(cap.x, hp.x)
	var h := HudSkin.mono().get_height(roundi(CAPTION_FONT * s)) + LINE_GAP * s + HudSkin.display().get_height(roundi(HP_FONT * s))
	if chips_row.visible and not chips_row.chips.is_empty():
		w = maxf(w, chips_row.size.x * chips_row.scale.x)
		h += LINE_GAP * s + chips_row.size.y * chips_row.scale.y
	return Vector2(w + PAD.x * 2.0 * s, h + PAD.y * 2.0 * s).ceil()


func _draw() -> void:
	if result.is_empty():
		return
	var s := _s()
	var r := Rect2(Vector2.ZERO, size)
	HudSkin.draw_terminal_panel(self, r, Palette.PENCIL_PLAN)
	var y := PAD.y * s
	var mono := HudSkin.mono()
	var cfs := roundi(CAPTION_FONT * s)
	draw_string(mono, Vector2(0.0, y + mono.get_ascent(cfs)), String(result["caption"]), HORIZONTAL_ALIGNMENT_CENTER, size.x, cfs, Palette.PENCIL_PLAN)
	y += mono.get_height(cfs) + LINE_GAP * s
	var disp := HudSkin.display()
	var hfs := roundi(HP_FONT * s)
	var a := int(result["hp_from"])
	var b := int(result["hp_to"])
	var col := HudSkin.TERMINAL_HI if a == b else (HudSkin.CHIP_DAMAGE if b < a else HudSkin.CHIP_GAIN)
	draw_string_outline(disp, Vector2(0.0, y + disp.get_ascent(hfs)), hp_text(), HORIZONTAL_ALIGNMENT_CENTER, size.x, hfs, 4, HudSkin.CHIP_INK)
	draw_string(disp, Vector2(0.0, y + disp.get_ascent(hfs)), hp_text(), HORIZONTAL_ALIGNMENT_CENTER, size.x, hfs, col)
