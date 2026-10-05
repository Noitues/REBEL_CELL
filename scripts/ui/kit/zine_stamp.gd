class_name ZineStamp
extends Button
## Circular rubber stamp (STYLE_GUIDE 4): JACK IN at HQ, the result stamps (REPELLED,
## CLEAN EXIT...). `hint` is an optional key hint under the word (empty by default: H20,
## a stamp only names a key that really presses it). A result stamp is `display_only()`:
## no focus, no clicks.

var stamp_text: String = "SEND IT"
var stamp_color: Color = Palette.CELL_PINK
## Key hint under the word ("[Space]"); "" draws none.
var hint: String = "":
	set(value):
		hint = value
		queue_redraw()
var _hot: bool = false
## A StatIcon over the word (H22 #14: JACK IN carried its meaning in words only); &"" none.
var icon_kind: StringName = &"":
	set(value):
		icon_kind = value
		queue_redraw()

## Hint font size at text scale 1.0.
const HINT_SIZE := 11
const WORD_SIZE := 20
## The icon over the word: radius and lift as shares of the stamp's radius; the word moves
## down by WORD_DROP of the radius to make room.
const ICON_SHARE := 0.2
const ICON_LIFT := 0.36
const WORD_DROP := 0.12


func _init(p_text: String = "SEND IT", p_color: Color = Palette.CELL_PINK, p_hint: String = "") -> void:
	stamp_text = p_text
	stamp_color = p_color
	hint = p_hint
	custom_minimum_size = Vector2(112, 112)
	flat = true
	focus_mode = Control.FOCUS_ALL
	# Draws its own hover/focus glow; no theme box around the sticker.
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())
	KitState.track(self)  # ART-0 F (art pass W2, §6): the six states


## ART-0 F (§6): the state drawn now (KitState: idle, hover, focus, pressed, disabled, refused).
func state() -> StringName:
	return KitState.of(self)


## ART-0 F (§6 Error / refused): flashes the refused state (HARM outline, no-entry mark).
func refuse() -> void:
	KitState.refuse(self)


## Animation pass ANIM-6 (4.13): the rings' scale; JACK IN breathes (`jack_ring_breathe`,
## a slow loop between 1 and the entry's amplitude). 1 at rest.
var ring_scale: float = 1.0
var _breath: Tween = null


## Starts the slow breathing of the rings (the HQ's JACK IN). Nothing under reduce effects
## or headless: the rings rest at 1.
func breathe() -> void:
	if _breath != null and _breath.is_valid():
		_breath.kill()
	_breath = Motion.loop_pulse(self, ^"ring_scale", &"jack_ring_breathe")


## True while the rings breathe.
func breathing() -> bool:
	return _breath != null and _breath.is_valid()


## A stamp that only shows a result: it takes no focus and no clicks.
func display_only() -> ZineStamp:
	focus_mode = Control.FOCUS_NONE
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	return self


func _draw() -> void:
	var st := state()
	# ART-0 F (§6): hover lifts the stamp, a press drops it.
	var c := size / 2.0 + Vector2(0, KitState.lift(st))
	var r := minf(size.x, size.y) / 2.0 - 4
	var col := stamp_color if not disabled else Color(stamp_color, 0.35)
	draw_circle(c, r, Color(Palette.NIGHT_SKY, 0.85))
	if _hot and not disabled:
		draw_circle(c, r + 4, Color(Palette.CELL_ACID, 0.45))
		draw_circle(c, r, Color(Palette.NIGHT_SKY, 0.85))
	draw_arc(c, r * ring_scale, 0, TAU, 48, col, 4.0)
	draw_arc(c, (r - 9) * ring_scale, 0, TAU, 48, col, 1.5)
	var drop := 0.0
	if icon_kind != &"":
		StatIcon.draw(self, c + Vector2(0, -r * ICON_LIFT), r * ICON_SHARE, icon_kind, col)
		drop = r * WORD_DROP
	draw_string(Palette.display(), c + Vector2(-r + 12, 8 + drop), stamp_text, HORIZONTAL_ALIGNMENT_CENTER, r * 2 - 24, WORD_SIZE, col)
	if hint != "":
		draw_string(Palette.mono(), c + Vector2(-r + 12, 26), hint, HORIZONTAL_ALIGNMENT_CENTER, r * 2 - 24, roundi(HINT_SIZE * Settings.text_scale), col)
	# ART-0 F (§6): the disabled lock and the refused mark; focus is the stamp's own lime
	# halo (a sticker's focus, v2 §2.10), never brackets.
	KitState.draw_frame(self, Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0), st, false)
