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
## Motion (Animation pass ANIM-3): the chips shown lit (they drain or refill one chip per
## `ram_tick`, the chip changing now pops), and the pending cost's blink while a card is
## aimed (`ram_pending_blink`). `ram` is always the real value.
var shown_ram: int = 0
var tick_pop: float = 0.0
var pending_alpha: float = 1.0
var aiming: bool = false
var _tick_tween: Tween = null
var _blink_tween: Tween = null


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	custom_minimum_size = Vector2(200, 16)


func set_ram(value: int, maximum: int) -> void:
	_flash = false
	var from := shown_ram if max_ram > 0 else value
	ram = value
	max_ram = maximum
	_tick_to(from, value)
	custom_minimum_size.y = (CHIP + 4.0) * Settings.text_scale
	tooltip_text = "RAM %d/%d: pays for cards, respins and extra nudges. Refills each turn." % [value, maximum]
	queue_redraw()


## A refusal for want of RAM (ANIM-R1 C6): the chips flash red and "COST > RAM" shows
## beside the count with a chip for RAM, pulsing for `ram_refusal`'s duration (amplitude =
## pulses). The words need no reading: the numbers and the red say it.
var _flash: bool = false
const REFUSED_COLOR := Color("#FF4D4D")
## The missing chips (and the refusal at its faintest) keep this alpha.
const MISSING_ALPHA := 0.45
## The RAM the refused action needed (0 = unknown) and the pulse's strength (0..1).
var _need: int = 0
var flash_alpha: float = 1.0


## Flashes the bar (a refusal for want of RAM; `need` = what it cost); static (shown until
## the next RAM change) under reduce effects and headless.
func flash_short(need: int = 0) -> void:
	_flash = true
	_need = need
	flash_alpha = 1.0
	queue_redraw()
	if not Motion.live(&"ram_refusal") or not is_inside_tree():
		return
	var pulses := maxf(1.0, Motion.amplitude(&"ram_refusal"))
	var tw := create_tween()
	tw.tween_method(func(p: float) -> void:
		flash_alpha = absf(cos(p * PI * pulses))
		queue_redraw(), 0.0, 1.0, Motion.seconds(&"ram_refusal"))
	tw.tween_callback(func() -> void:
		_flash = false
		_need = 0
		flash_alpha = 1.0
		queue_redraw())


## True while the refusal shows (tests).
func flashing() -> bool:
	return _flash


## The refusal's words ("3 > 2": the cost against the RAM there is), "" when none shows.
func refusal_text() -> String:
	return "%d > %d" % [_need, ram] if _flash and _need > 0 else ""


## The lit chips step from `from` to `to`, one chip per `ram_tick`.
func _tick_to(from: int, to: int) -> void:
	if _tick_tween != null and _tick_tween.is_valid():
		_tick_tween.kill()
	_tick_tween = null
	if from == to or not Motion.live(&"ram_tick") or not is_inside_tree():
		shown_ram = to
		tick_pop = 0.0
		return
	shown_ram = from
	var tw := create_tween()
	var step := 1 if to > from else -1
	for v in range(from + step, to + step, step):
		tw.tween_callback(_tick.bind(v))
		tw.tween_method(func(p: float) -> void: tick_pop = 1.0 - p; queue_redraw(), 0.0, 1.0, Motion.seconds(&"ram_tick"))
	tw.tween_callback(func() -> void: tick_pop = 0.0; queue_redraw())
	_tick_tween = tw


func _tick(v: int) -> void:
	shown_ram = v
	tick_pop = 1.0
	queue_redraw()


## Shows `value` chips lit until the next tick or finish_motion (a SEND IT replay holds
## the RAM the turn ended with until its turn-start beat).
func hold(value: int) -> void:
	if _tick_tween != null and _tick_tween.is_valid():
		_tick_tween.kill()
	_tick_tween = null
	shown_ram = value if Motion.live(&"ram_tick") else ram
	tick_pop = 0.0
	queue_redraw()


## The held chips tick on to the real RAM (`ram_tick`).
func play_refill() -> void:
	_tick_to(shown_ram, ram)


## Ends the drain / refill at once (skip).
func finish_motion() -> void:
	_tick_to(ram, ram)
	queue_redraw()


## While a card is aimed its cost blinks (`ram_pending_blink`); off, it holds.
func set_aiming(on: bool) -> void:
	aiming = on
	if _blink_tween != null and _blink_tween.is_valid():
		_blink_tween.kill()
	_blink_tween = null
	pending_alpha = 1.0
	if on and Motion.live(&"ram_pending_blink") and is_inside_tree():
		_blink_tween = Motion.loop_pulse(self, ^"pending_alpha", &"ram_pending_blink")
	queue_redraw()


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
	var refusal := refusal_text()
	var rw := 0.0
	if refusal != "":
		rw = chip + 4.0 + Palette.mono().get_string_size(refusal, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + 8.0
	var x0 := (size.x - max_ram * step - lw - rw) * 0.5
	var lit := shown_ram
	var after := clampi(lit + pending, 0, max_ram)
	for k in max_ram:
		var rc := Rect2(x0 + k * step, 1, chip, chip)
		var col := Color(1, 1, 1, 0.1)
		if k < mini(lit, after):
			col = Palette.NET_CYAN
		elif k < lit:
			col = Color(Palette.CELL_PINK, pending_alpha)  # spent by the previewed action
		if _flash:
			# The RAM there is falls short: every chip flashes red, the missing ones faint.
			col = col.lerp(Color(REFUSED_COLOR, 1.0 if k < lit else MISSING_ALPHA), flash_alpha)
		if tick_pop > 0.0 and k == (lit - 1 if lit > 0 and ram >= lit else lit):
			# The chip ticking now pops (`ram_tick` amplitude).
			rc = rc.grow(chip * (Motion.amplitude(&"ram_tick") - 1.0) * 0.5 * tick_pop)
			col = col.lerp(Palette.PAPER, tick_pop * 0.6)
		draw_rect(rc, col)
		draw_rect(rc, Color(Palette.CELL_ACID, 0.9) if (k >= lit and k < after) else Color(Palette.NET_CYAN, 0.6), false, 2.0 if (k >= lit and k < after) else 1.0)
	draw_string(Palette.mono(), Vector2(x0 + max_ram * step + 6.0, chip), label, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.NET_CYAN)
	if refusal != "":
		# A RAM chip, then "COST > RAM" in red.
		var rx := x0 + max_ram * step + lw + 4.0
		var red := Color(REFUSED_COLOR, maxf(MISSING_ALPHA, flash_alpha))
		draw_rect(Rect2(rx, 1, chip, chip), red)
		draw_rect(Rect2(rx, 1, chip, chip), Palette.PAPER, false, 1.0)
		draw_string(Palette.mono(), Vector2(rx + chip + 4.0, chip), refusal, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, red)
