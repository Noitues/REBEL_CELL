class_name RamBar
extends Control
## RAM as a bare row of cyan chips (lit = available) with the count, and the change the
## hovered card or the end of the turn brings: chips about to be spent blink out in pink,
## chips about to be gained are outlined in acid (H20). Hover for what RAM does.

## Chip size and spacing at text scale 1.0 (px).
const CHIP := 12.0
const STEP := 16.0
const FONT_SIZE := 12

var ram: int = 0
var max_ram: int = 0
## Predicted change (the preview), 0 = none.
var pending: int = 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	custom_minimum_size = Vector2(200, 16)


func set_ram(value: int, maximum: int) -> void:
	_flash = false
	ram = value
	max_ram = maximum
	custom_minimum_size.y = (CHIP + 4.0) * Settings.text_scale
	tooltip_text = "RAM %d/%d: pays for cards, respins and extra nudges. Refills each turn." % [value, maximum]
	queue_redraw()


## Seconds the bar flashes when RAM was short (refused action).
const FLASH_SECONDS := 0.6
var _flash: bool = false


## Flashes the bar (a refusal for want of RAM); static under reduce effects.
func flash_short() -> void:
	_flash = true
	queue_redraw()
	if DisplayServer.get_name() == "headless" or not Fx.effects_enabled():
		return
	get_tree().create_timer(FLASH_SECONDS).timeout.connect(func() -> void:
		if is_instance_valid(self):
			_flash = false
			queue_redraw())


func set_pending(delta: int) -> void:
	if delta != pending:
		pending = delta
		queue_redraw()


func _draw() -> void:
	var s := Settings.text_scale
	var step := STEP * s
	var chip := CHIP * s
	var fs := roundi(FONT_SIZE * s)
	var label := tr("RAM %d/%d") % [ram, max_ram]  # drawn words translate (H24)
	if pending != 0:
		label += " (%+d)" % pending
	var lw := Palette.mono().get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 8.0
	var x0 := (size.x - max_ram * step - lw) * 0.5
	var after := clampi(ram + pending, 0, max_ram)
	for k in max_ram:
		var rc := Rect2(x0 + k * step, 1, chip, chip)
		var col := Color(1, 1, 1, 0.1)
		if k < mini(ram, after):
			col = Palette.NET_CYAN
		elif k < ram:
			col = Palette.CELL_PINK  # spent by the previewed action
		if _flash and k >= ram:
			col = Color(Palette.CELL_PINK, 0.45)  # the RAM that was missing
		draw_rect(rc, col)
		draw_rect(rc, Color(Palette.CELL_ACID, 0.9) if (k >= ram and k < after) else Color(Palette.NET_CYAN, 0.6), false, 2.0 if (k >= ram and k < after) else 1.0)
	draw_string(Palette.mono(), Vector2(x0 + max_ram * step + 6.0, chip), label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.NET_CYAN)
