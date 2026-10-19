class_name ThemeChip
extends PanelContainer
## Plan 2 WH-02 (REPLAN 2026-10-19 A 2.4): the HUD's corporation-theme chip slot. One chip a
## theme rule fills (NetrunSession.theme_chip: its words and its RunThemeState.ChipKind):
## a dark terminal plate whose edge and words take the kind's colour (INFO terminal text,
## WARN amber, DANGER red), the words in mono caps. Hidden when empty. It shows; it never changes state.

## Lettering size and plate padding (px at text scale 1.0).
const FONT_PX := 15
const PAD_X := 10.0
const PAD_Y := 4.0
const EDGE_PX := 2
## Edge and word colour per RunThemeState.ChipKind (INFO is chrome: it follows the palette
## skin through PaletteSkins.chrome in _paint; WARN and DANGER are semantic).
const KIND_COLORS := {
	RunThemeState.ChipKind.INFO: Palette.TERMINAL_TEXT,
	RunThemeState.ChipKind.WARN: Palette.CRT_AMBER,
	RunThemeState.ChipKind.DANGER: Palette.HARM,
}

var label: Label
var kind: int = RunThemeState.ChipKind.INFO
var _box: StyleBoxFlat


func _init() -> void:
	name = "ThemeChip"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size_flags_vertical = Control.SIZE_SHRINK_CENTER
	_box = StyleBoxFlat.new()
	_box.bg_color = PaletteSkins.chrome(HudSkin.TERMINAL_BG)
	_box.set_border_width_all(EDGE_PX)
	_box.content_margin_left = PAD_X
	_box.content_margin_right = PAD_X
	_box.content_margin_top = PAD_Y
	_box.content_margin_bottom = PAD_Y
	add_theme_stylebox_override("panel", _box)
	label = Label.new()
	label.name = "Words"
	label.add_theme_font_override("font", HudSkin.mono())
	label.add_theme_font_size_override("font_size", roundi(FONT_PX * Settings.text_scale))
	add_child(label)
	visible = false
	_paint()


## Shows `text` (already translated) in `p_kind`'s colour; an empty `text` hides the chip.
func show_chip(text: String, p_kind: int) -> void:
	kind = p_kind if KIND_COLORS.has(p_kind) else RunThemeState.ChipKind.INFO
	label.text = text.to_upper()
	visible = text != ""
	_paint()


func _paint() -> void:
	var c: Color = PaletteSkins.chrome(KIND_COLORS[kind])  # a semantic colour comes back unchanged
	_box.bg_color = PaletteSkins.chrome(HudSkin.TERMINAL_BG)
	_box.border_color = c
	label.add_theme_color_override("font_color", c)
