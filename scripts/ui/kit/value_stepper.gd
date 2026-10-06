class_name ValueStepper
extends HBoxContainer
## Parity NEWC-01 (designer 2026-10-05): a big `- n +` stepper (the art pass build's ICE
## `Stepper`, art-m13-final scripts/ui/kit/stepper.gd, reworked in the v2 kit): two terminal
## tile chips (MenuChip on the concept's tile plates) round the value in bare Anton (ART_BIBLE
## v2 §1.2: live big numbers are bare Anton with a dark rim). It fronts a SpinBox (`spin`,
## kept hidden in the row) the way CrtTiles fronts an OptionButton: the chips step the spin
## box and the number follows it, so the screen and its tests drive `spin` as before. A step
## past either end is refused (the chip flashes HARM); both chips always take pad focus. View
## only.

## The value's type step, its rim (px) and the rim's colour (§6.4 live numbers).
const VALUE_STEP := UiTheme.HEADING
const RIM_PX := 2
const RIM_COLOR := Color("#06060A")
## The chips' word step.
const CHIP_STEP := UiTheme.TITLE

var spin: SpinBox
var down: MenuChip
var up: MenuChip
var value_label: Label


## A stepper for `p_spin` (kept as the value's owner); its chips are named `<base>Down` /
## `<base>Up` and the number `<base>Value`.
func _init(p_spin: SpinBox, base: String) -> void:
	spin = p_spin
	name = base + "Stepper"
	add_theme_constant_override(&"separation", UiTheme.SP_S)
	spin.visible = false
	add_child(spin)
	down = _chip("-", base + "Down", -1)
	add_child(down)
	value_label = Label.new()
	value_label.name = base + "Value"
	value_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	value_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	value_label.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var ls := LabelSettings.new()
	ls.font = Palette.display()
	ls.font_color = Palette.TEXT_HI
	ls.outline_size = RIM_PX * 2
	ls.outline_color = RIM_COLOR
	value_label.label_settings = ls
	add_child(value_label)
	up = _chip("+", base + "Up", 1)
	add_child(up)
	spin.value_changed.connect(func(_v: float) -> void: sync())
	spin.changed.connect(sync)
	refit()
	sync()


func _ready() -> void:
	Settings.changed.connect(refit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(refit):
		Settings.changed.disconnect(refit)


func _chip(word: String, chip_name: String, dir: int) -> MenuChip:
	var c := MenuChip.new(word)
	c.name = chip_name
	c.plate = &"tile"
	c.pre_translated = true
	c.label_step = CHIP_STEP
	c.set_meta(UiFocus.META_NO_SCALE, true)
	c.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	c.pressed.connect(func() -> void: step_by(dir))
	return c


## Steps the value by `dir` steps; a step past either end is refused (the chip's HARM flash
## and no-entry mark, KitState) and changes nothing.
func step_by(dir: int) -> void:
	var to := spin.value + dir * spin.step
	if to < spin.min_value or to > spin.max_value:
		KitState.refuse(down if dir < 0 else up)
		return
	spin.value = to


## True when a step by `dir` would leave the range (the chip at that end).
func at_end(dir: int) -> bool:
	return spin.value <= spin.min_value if dir < 0 else spin.value >= spin.max_value


## The number and the sizes follow the spin box.
func sync() -> void:
	value_label.text = str(int(spin.value))
	refit()


## Sizes the number for the widest value and the chips square to the text.
func refit() -> void:
	var px := UiTheme.font_px(VALUE_STEP)
	value_label.label_settings.font_size = px
	var widest := str(int(spin.max_value)) if str(int(spin.max_value)).length() >= str(int(spin.min_value)).length() else str(int(spin.min_value))
	value_label.custom_minimum_size.x = ceilf(Palette.display().get_string_size(widest, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x) + RIM_PX * 2
	for c in [down, up]:
		var chip := c as MenuChip
		chip.min_width = 0.0
		chip.refit()
		chip.min_width = chip.custom_minimum_size.y
		chip.refit()
