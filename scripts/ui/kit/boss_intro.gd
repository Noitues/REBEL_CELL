class_name BossIntro
extends Control
## Art pass W3 (ART_BIBLE §7.2, §8 T4): a boss fight's intro sting. The boss's name slams
## in, Anton `display`, on a taped PAPER banner over a scrim, holds, then lifts away
## (`boss_intro`: its duration is the whole sting, its amplitude the slam's start scale).
## T4: skippable (`skip`, the scene's press rule), and a plain cross-fade under reduce
## effects; nothing in a headless run. It never blocks input and never changes game state.

## The slam's share of the sting, the fade-out's share at its end.
const SLAM_SHARE := 0.12
const FADE_SHARE := 0.2
## The banner: its tilt (rad), padding (px at 1.0), the widest it gets (share of the screen),
## the scrim's alpha at the sting's peak, and its hue stripe (px).
const TILT := -0.06
const PAD := 16.0
const MAX_SHARE := 0.7
const SCRIM_ALPHA := 0.45
const STRIPE := 6.0
## The tape strips' size (shares of the banner's height).
const TAPE := Vector2(1.2, 0.35)

var text: String = ""
var hue: Color = Palette.NET_CYAN
## The sting's progress 0..1 (1 = done) and its current scale and alpha.
var progress: float = 1.0
var slam: float = 1.0
var alpha: float = 0.0
var _tween: Tween = null
var _fade_only: bool = false


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Plays the sting for boss `p_text` in its corporation's `p_hue`. Returns whether it plays.
func play(p_text: String, p_hue: Color) -> bool:
	text = p_text
	hue = p_hue
	skip()
	var live := Motion.live(&"boss_intro")
	# Reduce effects: the T4 sting becomes a cross-fade (§8); headless: nothing at all.
	_fade_only = not live and not Fx.effects_enabled() and (Motion.force_live or DisplayServer.get_name() != "headless")
	if not live and not _fade_only:
		return false
	var secs := Motion.entry(&"boss_intro").duration
	visible = true
	progress = 0.0
	_tween = create_tween()
	_tween.tween_method(_step, 0.0, 1.0, secs)
	_tween.tween_callback(skip)
	return true


## True while the sting shows.
func playing() -> bool:
	return visible and progress < 1.0


## Ends the sting at once (a press, a new fight): the end state is nothing on screen.
func skip() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null
	progress = 1.0
	alpha = 0.0
	slam = 1.0
	visible = false
	queue_redraw()


func _step(p: float) -> void:
	progress = p
	var amp := Motion.amplitude(&"boss_intro")
	if _fade_only:
		slam = 1.0
		alpha = clampf(minf(p / FADE_SHARE, (1.0 - p) / FADE_SHARE), 0.0, 1.0)
	else:
		var s := clampf(p / SLAM_SHARE, 0.0, 1.0)
		slam = lerpf(amp, 1.0, Tween.interpolate_value(0.0, 1.0, s, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT) as float)
		alpha = minf(clampf(s * 2.0, 0.0, 1.0), clampf((1.0 - p) / FADE_SHARE, 0.0, 1.0))
	queue_redraw()


## The banner's lettering (px): `display` at the text scale, smaller until it fits.
func font_size() -> int:
	var fs := UiTheme.font_px(UiTheme.DISPLAY)
	var room := (size.x if size.x > 0.0 else get_viewport_rect().size.x) * MAX_SHARE - PAD * 2.0
	while fs > UiTheme.CAPTION and Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	return fs


## The banner's rect (unrotated, local): centred across the screen at its upper third.
func banner_rect() -> Rect2:
	var fs := font_size()
	var ts := Settings.text_scale
	var w := Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + PAD * 2.0 * ts
	var h := fs * UiTheme.line_height(UiTheme.DISPLAY) + PAD * ts + STRIPE
	return Rect2(Vector2((size.x - w) * 0.5, size.y * 0.38 - h * 0.5), Vector2(w, h))


func _draw() -> void:
	if alpha <= 0.0 or text == "":
		return
	draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.SCRIM, SCRIM_ALPHA * alpha))
	var r := banner_rect()
	var c := r.get_center()
	draw_set_transform(c, TILT, Vector2.ONE * slam)
	var local := Rect2(-r.size * 0.5, r.size)
	draw_rect(Rect2(local.position + Vector2(5, 6), local.size), Color(Palette.SHADOW, Palette.SHADOW.a * alpha))
	draw_rect(local, Color(Palette.PAPER, alpha))
	draw_rect(Rect2(Vector2(local.position.x, local.end.y - STRIPE), Vector2(local.size.x, STRIPE)), Color(hue, alpha))
	var fs := font_size()
	var f := Palette.display()
	draw_string(f, Vector2(local.position.x + PAD * Settings.text_scale, local.position.y + (local.size.y - STRIPE) * 0.5 + f.get_ascent(fs) * 0.5 - f.get_descent(fs) * 0.2),
		text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.INK, alpha))
	var tape := Vector2(local.size.y * TAPE.x, local.size.y * TAPE.y)
	for sx: float in [-1.0, 1.0]:
		draw_set_transform(c + Vector2(sx * local.size.x * 0.5, -local.size.y * 0.5).rotated(TILT) * slam, TILT + sx * 0.6, Vector2.ONE * slam)
		draw_rect(Rect2(-tape * 0.5, tape), Color(Palette.NOTE_TAPE, Palette.NOTE_TAPE.a * alpha))
	draw_set_transform(Vector2.ZERO)
