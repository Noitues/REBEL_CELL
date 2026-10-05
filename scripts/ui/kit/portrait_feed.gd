class_name PortraitFeed
extends Control
## ART-9 4B (ART_BIBLE v2 §4.11 dialogue, §4.12 portraits; round 38 / 39 portraits): an
## operative's live CRT comm feed. The pre-rendered cel bust (PortraitBust) sits on the
## feed's backdrop under one shader (shaders/portrait_feed.gdshader: `mode`, `tint`,
## `split`, `tear`, `noise`, `fps_hold`); the chrome (bezel, "● CLASS // CALLSIGN" strip,
## LED, HP chip, voice bars, ON <SITE>, NO SIGNAL, the red pencil X, the stamps) is drawn on
## top. The same feed shows DISPATCH, who never gets a face (Mode.VOICE: a red voice trace,
## VOICE ONLY // NO FEED), and the corp's photo print of the bust (Mode.PRINT).
##
## Motion (content/config/ui_motion.tres): `portrait_feed` (the feed's live clock: rolling
## bar, static, torn bands; its amplitude is the stationed feed's frame rate),
## `portrait_blink` (eyes shut for its duration, every amplitude seconds), `portrait_talk`
## (mouth swap and voice bars at speech rate), `dispatch_trace` (the voice trace's drift).
## Under reduce effects, with an entry off or headless the feed is a still in its end state
## (talking: the mouth-open frame and still bars). Nothing waits. View only: callers set
## what to show; the feed emits nothing and changes no state.

enum Mode { IDLE, TALK, HURT, STATIONED, DEAD, RECRUIT, PRINT, VOICE }

const SHADER := preload("res://shaders/portrait_feed.gdshader")
const MOTION_FEED := &"portrait_feed"
const MOTION_BLINK := &"portrait_blink"
const MOTION_TALK := &"portrait_talk"
const MOTION_TRACE := &"dispatch_trace"
## HP share at or under which a live feed shows hurt (ART_BIBLE §4.12, art_asset B1: 25 %).
const HURT_SHARE := 0.25
## The feed's look per mode: RGB split (px at the bust's own size), torn-band share, static.
const LOOKS := {
	Mode.IDLE: [1.5, 0.0, 0.035], Mode.TALK: [1.5, 0.0, 0.035], Mode.HURT: [4.0, 0.12, 0.08],
	Mode.STATIONED: [1.0, 0.0, 0.05], Mode.DEAD: [2.0, 0.04, 0.45], Mode.RECRUIT: [1.0, 0.0, 0.05],
	Mode.PRINT: [0.0, 0.0, 0.0], Mode.VOICE: [0.0, 0.0, 0.0],
}
## Share of the feed's width the bust fills (bottom-aligned, centred).
const BUST_FILL := 0.96
## The feed's glass over the night sky (lightened share).
const BACKDROP_LIFT := 0.1
## DISPATCH's words (header, VOICE ONLY // NO FEED) as a share of its feed's height: its
## feed is wide and low, its words larger than a bust's label.
const VOICE_LABEL_SHARE := 0.085
## Chrome sizes as shares of the feed's height: label lettering, LED radius, bezel, inset.
const LABEL_SHARE := 0.05
const LED_SHARE := 0.022
const BEZEL_SHARE := 0.012
const INSET_SHARE := 0.03
## Big words (NO SIGNAL, stamps) as a share of the feed's height.
const WORD_SHARE := 0.11
## The chrome's words never go under the kit's floor (px at text scale 1.0); a feed too small
## for them (a roster chip) shows the LED and the marks only.
const WORD_FLOOR := 12
## Voice bars: bar width as a share of the feed's height and the strip's height share.
const BAR_SHARE := 0.022
const BARS_HEIGHT_SHARE := 0.09
## The listener's dim (dialogue: the speaker is live, the listener dimmed).
const DIM_SHARE := 0.7
## The stamps' tilt (degrees).
const STAMP_TILT := -8.0

var class_id: StringName = &""
var operative_id: StringName = &""
## The callsign in the label strip (as given, never translated).
var callsign: String = ""
## Overrides the label strip ("COMMS // STREET MERC"); empty = "CLASS // CALLSIGN".
var label_text: String = ""
var mode: int = Mode.IDLE
## The site a stationed operative is on ("LANE 15 RELAY"), as given.
var site: String = ""
## HP shown on the hurt chip (-1: none).
var hp: int = -1
var max_hp: int = -1
## Schematics a recruit costs (-1: the stamp says HIRE alone).
var hire_cost: int = -1
## The listener in a dialogue: dimmed.
var dimmed: bool = false
## The chrome (label strip, LED, bezel, stamps); off for a bare picture.
var chrome: bool = true
## The rookie variant (PortraitBust.variant_for unless set).
var variant: int = 0

var _screen: ColorRect
var _overlay: Control
var _mat: ShaderMaterial
var _t: float = 0.0
var _frame: int = -1
## A per-operative phase so a roster of feeds never blinks in step (a hash, not RNG).
var _phase: float = 0.0


func _init(p_class: StringName = &"", p_operative: StringName = &"", p_callsign: String = "", p_mode: int = Mode.IDLE) -> void:
	name = "PortraitFeed"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	clip_contents = true
	auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_screen = ColorRect.new()
	_screen.name = "Screen"
	_screen.material = _mat
	_screen.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_screen.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_screen)
	_overlay = Control.new()
	_overlay.name = "Chrome"
	_overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	_overlay.draw.connect(_draw_chrome)
	add_child(_overlay)
	resized.connect(_layout)
	set_operative(p_class, p_operative, p_callsign)
	set_mode(p_mode)


## A DISPATCH feed: no face, a red voice trace (ART_BIBLE §4.11, DECISIONS "DISPATCH text").
static func dispatch() -> PortraitFeed:
	var f := PortraitFeed.new(&"", &"", "", Mode.VOICE)
	f.name = "DispatchFeed"
	return f


## Shows `p_class`'s rookie for `p_operative` (its variant by PortraitBust.variant_for).
func set_operative(p_class: StringName, p_operative: StringName = &"", p_callsign: String = "") -> void:
	class_id = p_class
	operative_id = p_operative
	callsign = p_callsign
	variant = PortraitBust.variant_for(p_class, p_operative)
	_phase = float(posmod(hash("%s/%s/blink" % [p_class, p_operative]), 1000)) / 1000.0
	_frame = -1
	_apply()


## Switches the feed to `p_mode` (Mode).
func set_mode(p_mode: int) -> void:
	mode = p_mode
	_frame = -1
	_apply()


## HP for the hurt chip; a live feed (idle or talking) turns hurt at HURT_SHARE or less and
## back when healed.
func set_hp(p_hp: int, p_max: int) -> void:
	hp = p_hp
	max_hp = p_max
	var low := p_max > 0 and float(p_hp) <= float(p_max) * HURT_SHARE
	if low and mode in [Mode.IDLE, Mode.TALK]:
		set_mode(Mode.HURT)
	elif not low and mode == Mode.HURT:
		set_mode(Mode.IDLE)
	else:
		_overlay.queue_redraw()


## The listener's dim on or off.
func set_dimmed(on: bool) -> void:
	dimmed = on
	_apply()


## The class colour the feed wears (rim haze, stationed monochrome, label, bars).
func accent() -> Color:
	if mode == Mode.VOICE:
		return dispatch_red()
	return Palette.class_accent(class_id)


## DISPATCH's red (REBEL_CELL red, ART_BIBLE §1.2 "red DISPATCH").
static func dispatch_red() -> Color:
	return Palette.CORP_REBEL_CELL


## The grease pencil's red for the flatlined X (ART_BIBLE §1.2: threat / loss).
static func pencil_red() -> Color:
	return Palette.PENCIL_THREAT


## True when the feed shows a bust (a class with a bust set, not DISPATCH).
func has_bust() -> bool:
	return mode != Mode.VOICE and PortraitBust.has_class(class_id)


## The bust frame on screen now (PortraitBust.Frame).
func frame() -> int:
	return _frame if _frame >= 0 else rest_frame()


## The frame a still feed shows in its mode (the end state: talking keeps the mouth open,
## flatlined the dead eyes, hurt the grimace).
func rest_frame() -> int:
	match mode:
		Mode.TALK:
			return PortraitBust.Frame.TALK
		Mode.HURT:
			return PortraitBust.Frame.HURT
		Mode.DEAD:
			return PortraitBust.Frame.BLINK
		_:
			return PortraitBust.Frame.IDLE


## True while any of the feed's motions plays (tests; the lab).
func animating() -> bool:
	if mode == Mode.VOICE:
		return Motion.live(MOTION_TRACE)
	return Motion.live(MOTION_FEED) or Motion.live(MOTION_BLINK) or (mode == Mode.TALK and Motion.live(MOTION_TALK))


## The frame the motions want at clock `t` (s): a blink every `portrait_blink` amplitude
## seconds for its duration (live feeds), the mouth swapped every `portrait_talk` duration
## while talking. Without the motions: rest_frame().
func frame_at(t: float) -> int:
	var f := rest_frame()
	if mode in [Mode.DEAD, Mode.PRINT, Mode.VOICE, Mode.HURT]:
		return f
	if mode == Mode.TALK and Motion.live(MOTION_TALK):
		var step := maxf(0.01, Motion.seconds(MOTION_TALK))
		f = PortraitBust.Frame.TALK if posmod(int(floor(t / step)), 2) == 0 else PortraitBust.Frame.IDLE
	if Motion.live(MOTION_BLINK):
		var period := maxf(0.1, Motion.amplitude(MOTION_BLINK))
		if fmod(t + _phase * period, period) < Motion.seconds(MOTION_BLINK):
			f = PortraitBust.Frame.BLINK
	return f


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	if not animating():
		if _frame != rest_frame():
			_frame = -1
			_apply()
		return
	_t += delta
	if mode == Mode.VOICE:
		# The trace's clock counts sweeps (`dispatch_trace` duration each).
		_mat.set_shader_parameter(&"feed_time", _t / maxf(0.01, Motion.seconds(MOTION_TRACE)) if Motion.live(MOTION_TRACE) else 0.0)
	else:
		_mat.set_shader_parameter(&"feed_time", _t if Motion.live(MOTION_FEED) else 0.0)
		_mat.set_shader_parameter(&"roll_period", Motion.seconds(MOTION_FEED))
	var f := frame_at(_t)
	if f != _frame and has_bust():
		_frame = f
		_mat.set_shader_parameter(&"bust_uv", _uv_vec(PortraitBust.uv_rect(class_id, variant, f)))
	if mode in [Mode.TALK, Mode.VOICE]:
		_overlay.queue_redraw()


static func _uv_vec(r: Rect2) -> Vector4:
	return Vector4(r.position.x, r.position.y, r.size.x, r.size.y)


## Pushes the feed's look into the shader (mode, tint, bust, strengths).
func _apply() -> void:
	if _mat == null:
		return
	var bust := has_bust()
	var look: Array = LOOKS.get(mode, LOOKS[Mode.IDLE])
	_mat.set_shader_parameter(&"mode", mode)
	_mat.set_shader_parameter(&"has_bust", bust)
	_mat.set_shader_parameter(&"tint", accent())
	_mat.set_shader_parameter(&"backdrop", Palette.NIGHT_SKY.lightened(BACKDROP_LIFT))
	_mat.set_shader_parameter(&"paper", Palette.PAPER_ALT.darkened(0.12))
	_mat.set_shader_parameter(&"alarm", dispatch_red())
	_mat.set_shader_parameter(&"split", float(look[0]))
	_mat.set_shader_parameter(&"tear", float(look[1]))
	_mat.set_shader_parameter(&"noise", float(look[2]))
	_mat.set_shader_parameter(&"fps_hold", Motion.amplitude(MOTION_FEED) if mode == Mode.STATIONED else 0.0)
	_mat.set_shader_parameter(&"dim", DIM_SHARE if dimmed else 0.0)
	if not animating():
		_mat.set_shader_parameter(&"feed_time", 0.0)
	if bust:
		var tex := PortraitBust.sheet(class_id)
		_mat.set_shader_parameter(&"bust", tex)
		_mat.set_shader_parameter(&"bust_uv", _uv_vec(PortraitBust.uv_rect(class_id, variant, frame())))
	_layout()


## Where the bust sits (bottom-aligned, centred, BUST_FILL of the width; never taller than
## the feed) and the shader's pixel size.
func _layout() -> void:
	if _mat == null:
		return
	var s := size if size.x > 0.0 and size.y > 0.0 else Vector2(PortraitBust.CELL)
	_mat.set_shader_parameter(&"rect_size", s)
	var cell := Vector2(PortraitBust.CELL)
	var w := BUST_FILL
	var h := w * (cell.y / cell.x) * (s.x / s.y)
	if h > 1.0:
		w /= h
		h = 1.0
	_mat.set_shader_parameter(&"bust_box", Vector4((1.0 - w) * 0.5, 1.0 - h, w, h))
	_overlay.queue_redraw()


# --- Chrome -----------------------------------------------------------------------------------

## The label strip's words ("RIGGER // SPROCKET", "> DISPATCH").
func label_words() -> String:
	if label_text != "":
		return label_text
	if mode == Mode.VOICE:
		return "> " + tr("DISPATCH")
	var cls := class_word().to_upper()
	return cls if callsign == "" else "%s // %s" % [cls, callsign.to_upper()]


## The class's name in the player's language (its content's display name; the id when the
## content is not loaded).
func class_word() -> String:
	var registry: Node = get_tree().root.get_node_or_null(^"ContentRegistry") if is_inside_tree() else null
	var cls := registry.get_content(class_id) as ClassData if registry != null and class_id != &"" else null
	return TextDb.t(cls, "display_name") if cls != null else String(class_id)


## The lettering of the chrome's small words (px), or 0 when the feed is too small to carry
## them at the floor.
func word_size() -> int:
	var fs := roundi(size.y * (VOICE_LABEL_SHARE if mode == Mode.VOICE else LABEL_SHARE))
	return fs if fs >= roundi(WORD_FLOOR * Settings.text_scale) else 0


## The LED's colour (green live, red hurt, class colour stationed, amber recruit, off dead).
func led_color() -> Color:
	match mode:
		Mode.HURT:
			return Palette.HARM
		Mode.STATIONED:
			return accent()
		Mode.DEAD:
			return Palette.DISABLED
		Mode.RECRUIT:
			return Palette.CRT_AMBER
		_:
			return Palette.GAIN


func _draw_chrome() -> void:
	var c := _overlay
	var s := size
	if s.x <= 0.0 or s.y <= 0.0 or mode == Mode.PRINT:
		return
	var h := s.y
	var inset := maxf(2.0, h * INSET_SHARE)
	var a := 1.0 - (DIM_SHARE * 0.6 if dimmed else 0.0)
	var mono := Palette.mono()
	var fs := word_size()
	match mode:
		Mode.TALK:
			_draw_bars(c, s, Color(accent(), a))
		Mode.HURT:
			_draw_cracks(c, s, a)
		Mode.STATIONED:
			if fs > 0:
				var strip := Rect2(0, h - fs * 2.0, s.x, fs * 2.0)
				c.draw_rect(strip, Color(Palette.NIGHT_SKY, 0.8 * a))
				var words := tr("ON %s") % site.to_upper() if site != "" else tr("STATIONED")
				words += " // " + tr("%d fps") % roundi(Motion.amplitude(MOTION_FEED))
				c.draw_string(mono, Vector2(inset * 1.5, h - fs * 0.6), words, HORIZONTAL_ALIGNMENT_LEFT, s.x - inset * 3.0, fs, Color(accent(), a))
		Mode.DEAD:
			_draw_dead(c, s, a)
		Mode.RECRUIT:
			var words := tr("HIRE: %d SCHEMATICS") % hire_cost if hire_cost >= 0 else tr("HIRE")
			_draw_stamp(c, Vector2(s.x * 0.62, h * 0.8), words, Palette.RESIST_GOLD, a)
		Mode.VOICE:
			if fs > 0:
				var foot := tr("VOICE ONLY // NO FEED")
				c.draw_string(mono, Vector2(0, h - inset - fs * 0.4), foot, HORIZONTAL_ALIGNMENT_CENTER, s.x, fs, Color(dispatch_red(), 0.6 * a))
	# The label strip.
	if fs > 0:
		var words := label_words()
		var tw := mono.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var dot := mode in [Mode.IDLE, Mode.TALK, Mode.HURT]
		var dot_r := fs * 0.3
		var pad := fs * 0.45
		var chip_room := 0.0
		if mode == Mode.HURT and max_hp > 0:
			chip_room = mono.get_string_size(tr("HP %d/%d") % [maxi(0, hp), max_hp], HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + pad * 3.0
		var strip := Rect2(inset, inset, minf(s.x - inset * 2.0 - chip_room, tw + pad * 2.0 + (dot_r * 2.0 + pad if dot else 0.0)), fs * 1.5)
		c.draw_rect(strip, Color(Palette.NIGHT_SKY, 0.72 * a))
		var x := strip.position.x + pad
		if dot:
			c.draw_circle(Vector2(x + dot_r, strip.get_center().y), dot_r, Color(dispatch_red(), a))
			x += dot_r * 2.0 + pad
		var ink := Palette.TEXT_MID if mode in [Mode.DEAD, Mode.RECRUIT] else accent()
		c.draw_string(mono, Vector2(x, strip.position.y + fs * 1.1), words, HORIZONTAL_ALIGNMENT_LEFT, strip.end.x - x, fs, Color(ink, a))
		if mode == Mode.HURT and max_hp > 0:
			var chip := tr("HP %d/%d") % [maxi(0, hp), max_hp]
			var cw := mono.get_string_size(chip, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + pad * 2.0
			var cr := Rect2(s.x - inset - cw, inset, cw, fs * 1.5)
			c.draw_rect(cr, Color(Palette.HARM.darkened(0.45), a))
			c.draw_rect(cr, Color(Palette.HARM, a), false, 1.0)
			c.draw_string(mono, Vector2(cr.position.x + pad, cr.position.y + fs * 1.1), chip, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.TEXT_HI, a))
	# The LED and the bezel.
	if mode != Mode.VOICE:
		var led_r := maxf(2.0, h * LED_SHARE)
		var at := s - Vector2(inset, inset) - Vector2(led_r, led_r)
		if mode != Mode.DEAD:
			c.draw_circle(at, led_r * 1.9, Color(led_color(), 0.22 * a))
		c.draw_circle(at, led_r, Color(led_color(), a))
	var bezel := maxf(1.0, h * BEZEL_SHARE)
	var edge := Color(dispatch_red(), 0.9) if mode == Mode.VOICE else Color(Palette.TEXT_HI, 0.12)
	c.draw_rect(Rect2(Vector2.ZERO, s), Palette.DESK_DARK, false, bezel * 2.0)
	c.draw_rect(Rect2(Vector2.ONE * bezel, s - Vector2.ONE * bezel * 2.0), edge, false, maxf(1.0, bezel * 0.6))


## Voice-level bars along the foot (talking): heights step with `portrait_talk`.
func _draw_bars(c: Control, s: Vector2, col: Color) -> void:
	var bw := maxf(2.0, s.y * BAR_SHARE)
	var n := int(s.x * 0.9 / (bw * 1.35))
	var top := s.y * BARS_HEIGHT_SHARE
	var step := 0
	if Motion.live(MOTION_TALK):
		step = int(floor(_t / maxf(0.01, Motion.seconds(MOTION_TALK))))
	var x0 := s.x * 0.05
	for i in n:
		var k := float(posmod(hash([i, step, variant]), 1000)) / 1000.0
		var bh := top * (0.25 + 0.75 * k)
		c.draw_rect(Rect2(x0 + i * bw * 1.35, s.y * 0.97 - bh, bw, bh), col)


## Cracked glass (hurt): white cracks from one point, fixed per operative (a hash).
func _draw_cracks(c: Control, s: Vector2, a: float) -> void:
	var seed_i := posmod(hash("%s/%s/crack" % [class_id, operative_id]), 1000)
	var o := Vector2(s.x * (0.68 + seed_i % 7 * 0.02), s.y * (0.3 + seed_i % 5 * 0.03))
	var w := maxf(1.0, s.y * 0.004)
	for k in 6:
		var ang := TAU * (k + float(seed_i % 13) / 13.0) / 6.0
		var p := o
		var pts := PackedVector2Array([p])
		for j in 3:
			ang += (float(posmod(hash([seed_i, k, j]), 100)) / 100.0 - 0.5) * 0.7
			p += Vector2(cos(ang), sin(ang)) * s.y * (0.07 + 0.05 * j)
			pts.append(p)
		c.draw_polyline(pts, Color(Palette.TEXT_HI, 0.85 * a), w, true)


## Flatlined: NO SIGNAL, the red pencil X, FLATLINED.
func _draw_dead(c: Control, s: Vector2, a: float) -> void:
	var big := roundi(s.y * WORD_SHARE)
	if big >= roundi(WORD_FLOOR * Settings.text_scale):
		var band := Rect2(0, s.y * 0.43, s.x, big * 1.5)
		c.draw_rect(band, Color(Palette.INK, 0.85 * a))
		c.draw_string(Palette.display(), Vector2(0, band.position.y + big * 1.15), tr("NO SIGNAL"), HORIZONTAL_ALIGNMENT_CENTER, s.x, big, Color(Palette.TEXT_HI, a))
	var w := maxf(2.0, s.y * 0.022)
	var m := s.y * 0.05
	var red := Color(pencil_red(), 0.96 * a)
	c.draw_line(Vector2(m, m), s - Vector2(m, m), red, w, true)
	c.draw_line(Vector2(s.x - m, m), Vector2(m, s.y - m), red, w, true)
	if big >= roundi(WORD_FLOOR * Settings.text_scale):
		_draw_stamp(c, Vector2(s.x * 0.48, s.y * 0.84), tr("FLATLINED"), Palette.HARM, a * 0.8)


## A rubber stamp: a tilted outlined box with Anton words, centred on `at`.
func _draw_stamp(c: Control, at: Vector2, words: String, col: Color, a: float) -> void:
	var fs := roundi(size.y * WORD_SHARE * 0.7)
	if fs < roundi(WORD_FLOOR * Settings.text_scale):
		return
	var f := Palette.display()
	var tw := minf(f.get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, size.x * 0.8)
	var box := Rect2(-tw * 0.5 - fs * 0.3, -fs * 0.75, tw + fs * 0.6, fs * 1.4)
	c.draw_set_transform(at, deg_to_rad(STAMP_TILT))
	c.draw_rect(box, Color(col, a), false, maxf(1.5, fs * 0.08))
	c.draw_string(f, Vector2(-tw * 0.5, fs * 0.38), words, HORIZONTAL_ALIGNMENT_LEFT, tw, fs, Color(col, a))
	c.draw_set_transform(Vector2.ZERO)
