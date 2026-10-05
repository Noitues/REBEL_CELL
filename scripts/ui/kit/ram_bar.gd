class_name RamBar
extends Control
## RAM on a terminal panel (ART-2 2D, ART_BIBLE v2 §3.1): the count and a row of cyan pips
## (lit = available), and the change the
## hovered card or the end of the turn brings: chips about to be spent blink out in pink,
## chips about to be gained are outlined in acid (H20). Hover for what RAM does.

## Chip size and spacing at text scale 1.0 (px).
const CHIP := 12.0
const STEP := 16.0
const FONT_SIZE := 12
## The "-N RAM" float: its lettering as a share of the count's, and the share of its time
## after which it fades (ANIM-R2 E9). ANIM-R4 C6h: it starts this far (px) above the
## count's words and rises from there (it never sits on them, at any text size).
const SPEND_FONT_SHARE := 1.4
const SPEND_FADE_FROM := 0.6
const SPEND_GAP := 2.0

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
	custom_minimum_size = Vector2(PANEL_W, PANEL_H)
	_glass = HudSkin.crt_backing(self, true)  # ART-1 1B: the CRT glass with its hex dump


func set_ram(value: int, maximum: int) -> void:
	_flash = false
	var from := shown_ram if max_ram > 0 else value
	if max_ram > 0 and value < ram:
		float_spend(ram - value)
	ram = value
	max_ram = maximum
	_tick_to(from, value)
	custom_minimum_size = panel_size()
	# ANIM-R5 combat 9: translated here, shown as given.
	tooltip_text = tr("RAM %d/%d: pays for cards, respins and extra nudges. Refills each turn.") % [value, maximum]
	tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	queue_redraw()


## ANIM-R2 E9: what a respin, a card or an extra nudge just spent rises off the count as
## "-N RAM" (`ram_spend_float`: its seconds, amplitude = px it rises), so RAM never drops
## with nothing said. Nothing under reduce effects and headless (the count shows it).
var spend_text: String = ""
var spend_p: float = 1.0
## ANIM-R4 C6h: the float's colour (pink for a spend, cyan for the turn start's refill) and
## the entry it runs on.
var spend_color: Color = Palette.CELL_PINK
var _spend_id: StringName = &"ram_spend_float"
var _spend_tween: Tween = null


func float_spend(amount: int) -> void:
	if amount <= 0:
		return
	_float(tr("-%d RAM") % amount, Palette.CELL_PINK, &"ram_spend_float")


## ANIM-R4 C6h: the turn start's RAM comes back as "+N RAM" rising off the chips as they
## tick back (`ram_refill_float`), so a refill is said where it happens.
func float_refill(amount: int) -> void:
	if amount <= 0:
		return
	_float(tr("+%d RAM") % amount, Palette.NET_CYAN, &"ram_refill_float")


func _float(text: String, col: Color, id: StringName) -> void:
	if not Motion.live(id) or not is_inside_tree():
		return
	if _spend_tween != null and _spend_tween.is_valid():
		_spend_tween.kill()
	spend_text = text
	spend_color = col
	_spend_id = id
	spend_p = 0.0
	var e := Motion.entry(id)
	_spend_tween = create_tween()
	_spend_tween.tween_method(_set_spend_p, 0.0, 1.0, Motion.seconds(id)).set_ease(e.ease).set_trans(e.trans)
	_spend_tween.tween_callback(_end_float)


func _set_spend_p(v: float) -> void:
	spend_p = v
	queue_redraw()


func _end_float() -> void:
	spend_text = ""
	spend_p = 1.0
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
	# ANIM-R4 C6h: a refusal spent nothing: no "-N RAM" float with it (it read as a loss);
	# the refusal says NEED / HAVE.
	if _spend_tween != null and _spend_tween.is_valid():
		_spend_tween.kill()
	_end_float()
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


## The refusal's words ("NEED 3 · HAVE 2": the cost against the RAM there is; ANIM-R3 A6j:
## "3 > 2" was a sum to decode), "" when none shows.
func refusal_text() -> String:
	return tr("NEED %d · HAVE %d") % [_need, ram] if _flash and _need > 0 else ""


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


## The held chips tick on to the real RAM (`ram_tick`); the RAM they gain floats "+N RAM"
## (ANIM-R4 C6h).
func play_refill() -> void:
	float_refill(ram - shown_ram)
	_tick_to(shown_ram, ram)


## Ends the drain / refill at once (skip).
func finish_motion() -> void:
	_tick_to(ram, ram)
	if _spend_tween != null and _spend_tween.is_valid():
		_spend_tween.kill()
	spend_text = ""
	spend_p = 1.0
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


## ART-2 2D (ART_BIBLE v2 §3.1): the RAM readout is a terminal panel: a "RAM" header, the
## count in big numbers, then the pips (lit = available). Sizes at text scale 1.0 (px).
const PANEL_W := 240.0
const PANEL_H := 62.0
const PANEL_PAD := 9.0
const HEADER_FONT := 12
const COUNT_FONT := 28
const PIP_W := 9.0
const PIP_H := 18.0
const PIP_STEP := 13.0
const PIP_GAP := 12.0
## The hatch over the pips a previewed play spends: the gap between its strokes (px at 1.0).
const HATCH_STEP := 5.0
## The panel grows with the text by this share of the text scale's step (the pips shrink to
## fit; the count keeps the whole text scale).
const PANEL_GROWTH := 0.1
## ART-2 2D: words before "RAM" in the header (the operative's name and class, when the name
## sticker stands down at big text); "" = none.
var owner_words: String = ""


## The panel's size at the current text scale.
static func panel_size() -> Vector2:
	return Vector2(PANEL_W, PANEL_H) * (1.0 + (Settings.text_scale - 1.0) * PANEL_GROWTH) + Vector2(0.0, (COUNT_FONT + HEADER_FONT) * (Settings.text_scale - 1.0))


## ANIM-R4 C6h: the count's words ("5/12") as drawn (local rect).
func label_rect() -> Rect2:
	var s := Settings.text_scale
	var fs := roundi(COUNT_FONT * s)
	var f := HudSkin.display()
	var pad := PANEL_PAD * s
	var base := size.y - pad
	return Rect2(Vector2(pad, base - f.get_ascent(fs)), Vector2(f.get_string_size(_count(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, f.get_ascent(fs)))


## ANIM-R4 C6h: where the RAM float is now (local rect; empty when none shows): it starts
## SPEND_GAP above the count's words and rises its entry's amplitude px.
func spend_rect() -> Rect2:
	if spend_text == "":
		return Rect2()
	var fs := roundi(FONT_SIZE * Settings.text_scale)
	var sfs := roundi(fs * SPEND_FONT_SHARE)
	var f := Palette.display()
	var sz := Vector2(f.get_string_size(spend_text, HORIZONTAL_ALIGNMENT_LEFT, -1, sfs).x, f.get_height(sfs))
	var lr := label_rect()
	var bottom := lr.position.y - SPEND_GAP - Motion.amplitude(_spend_id) * spend_p
	return Rect2(Vector2(lr.position.x, bottom - sz.y), sz)


var _glass: CrtTerminalPanel = null


## The words a reader gets ("RAM 6/12 (-2)"; the tooltip and tests).
func _label() -> String:
	var label := tr("RAM %d/%d") % [ram, max_ram]
	if pending != 0:
		label += " (%+d)" % pending
	return label


## The big count ("6/12").
func _count() -> String:
	return "%d/%d" % [ram, max_ram]


## The pips' rects (local), one per RAM.
func pip_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var s := Settings.text_scale
	var lr := label_rect()
	var x0 := lr.end.x + PIP_GAP * s
	var room := size.x - PANEL_PAD * s - x0
	var step := minf(PIP_STEP * s, room / maxf(1.0, max_ram))
	var w := minf(PIP_W * s, step * 0.75)
	var h := PIP_H * s
	var y := lr.position.y + (lr.size.y - h) * 0.5
	for k in max_ram:
		out.append(Rect2(Vector2(x0 + k * step, y), Vector2(w, h)))
	return out


## The centre of pip `k` on screen (global; FX fly to and from it). Past the last pip, the
## spot one step on.
func pip_spot(k: int) -> Vector2:
	var pips := pip_rects()
	if pips.is_empty():
		return get_global_rect().get_center()
	if k < pips.size():
		return global_position + pips[maxi(0, k)].get_center()
	var last := pips[pips.size() - 1]
	var step := last.position.x - pips[pips.size() - 2].position.x if pips.size() > 1 else last.size.x
	return global_position + last.get_center() + Vector2(step * (k - pips.size() + 1), 0.0)


func _draw() -> void:
	var s := Settings.text_scale
	var pad := PANEL_PAD * s
	HudSkin.draw_terminal_edge(self, Rect2(Vector2.ZERO, size), HudSkin.TERMINAL_EDGE)
	var hf := roundi(HEADER_FONT * s)
	var mono := HudSkin.mono()
	var head := tr("RAM")  # drawn words translate (H24)
	if owner_words != "":
		head = owner_words  # ART-2 2D: the name sticker's words at big text (the count says RAM)
	if pending != 0:
		head += "  (%+d)" % pending
	draw_string(mono, Vector2(pad, pad + mono.get_ascent(hf)), head, HORIZONTAL_ALIGNMENT_LEFT, -1, hf, HudSkin.TERMINAL_TEXT)
	var refusal := refusal_text()
	if refusal != "":
		var red := Color(REFUSED_COLOR, maxf(MISSING_ALPHA, flash_alpha))
		var rw := mono.get_string_size(refusal, HORIZONTAL_ALIGNMENT_LEFT, -1, hf).x
		draw_string(mono, Vector2(size.x - pad - rw, pad + mono.get_ascent(hf)), refusal, HORIZONTAL_ALIGNMENT_LEFT, -1, hf, red)
	var cf := roundi(COUNT_FONT * s)
	var lr := label_rect()
	draw_string_outline(HudSkin.display(), Vector2(lr.position.x, size.y - pad), _count(), HORIZONTAL_ALIGNMENT_LEFT, -1, cf, 2, Palette.LIVE_NUMBER_RIM)
	draw_string(HudSkin.display(), Vector2(lr.position.x, size.y - pad), _count(), HORIZONTAL_ALIGNMENT_LEFT, -1, cf, HudSkin.PIP_ON)
	var lit := shown_ram
	var after := clampi(lit + pending, 0, max_ram)
	var pips := pip_rects()
	for k in pips.size():
		var rc := pips[k]
		var col := HudSkin.PIP_OFF
		if k < mini(lit, after):
			col = HudSkin.PIP_ON
		elif k < lit:
			col = Color(Palette.CELL_PINK, pending_alpha)  # spent by the previewed action
		if _flash:
			# The RAM there is falls short: every pip flashes red, the missing ones faint.
			col = col.lerp(Color(REFUSED_COLOR, 1.0 if k < lit else MISSING_ALPHA), flash_alpha)
		if tick_pop > 0.0 and k == (lit - 1 if lit > 0 and ram >= lit else lit):
			# The pip ticking now pops (`ram_tick` amplitude).
			rc = rc.grow(rc.size.x * (Motion.amplitude(&"ram_tick") - 1.0) * 0.5 * tick_pop)
			col = col.lerp(Palette.PAPER, tick_pop * 0.6)
		draw_rect(rc, col)
		if k >= after and k < lit:
			# ART-2 2D: the previewed cost is hatched across the pips it will spend.
			var hy := rc.size.x
			var y := rc.position.y - hy
			while y < rc.end.y:
				var a0 := Vector2(rc.position.x, clampf(y + hy, rc.position.y, rc.end.y))
				var a1 := Vector2(rc.end.x, clampf(y, rc.position.y, rc.end.y))
				draw_line(a0, a1, Color(Palette.LIVE_NUMBER_RIM, 0.7 * pending_alpha), 1.5)
				y += HATCH_STEP * Settings.text_scale
		if k >= lit and k < after:
			draw_rect(rc, Color(Palette.CELL_ACID, 0.9), false, 2.0)  # gained by the previewed action
	if spend_text != "":
		# "-N RAM" (or "+N RAM") rising off the count and fading, from above its words.
		var r := spend_rect()
		var a := 1.0 - clampf((spend_p - SPEND_FADE_FROM) / (1.0 - SPEND_FADE_FROM), 0.0, 1.0)
		var sfs := roundi(roundi(FONT_SIZE * s) * SPEND_FONT_SHARE)
		var at := Vector2(r.position.x, r.position.y + Palette.display().get_ascent(sfs))
		draw_string_outline(Palette.display(), at, spend_text, HORIZONTAL_ALIGNMENT_LEFT, -1, sfs, 4, Color(Palette.NIGHT_SKY, a))
		draw_string(Palette.display(), at, spend_text, HORIZONTAL_ALIGNMENT_LEFT, -1, sfs, Color(spend_color, a))
