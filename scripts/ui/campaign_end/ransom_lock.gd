class_name RansomLock
extends Control
## ART-11 4D: campaign lost, option A "ransomware lock" (ART_BIBLE v2 §4.8; ref
## `campaign_end/round20_raid_world/campaign_lost.jpg`, generator art-concepts-r43 round 20
## lost20.py `frame_A`). After BREACHED (ruling 6.2: the home server's fall is the cause), the
## winning corporation takes the Cell's station over in its house style and with its verb:
## 1. the home server falls: the screen tears (`ransom_glitch`);
## 2. the ransomware rolls down the screen in the house hue and motif (`ransom_wipe`) and a
##    padlock stamps on every node it passes (`ransom_padlock`);
## 3. the notice comes up (`ransom_notice_in`) and the verb is stamped on it
##    (`ransom_verb_stamp`); a countdown runs to the wipe (`ransom_countdown`);
## 4. the Cell's stickers, vinyl on the glass and never tinted, curl (`ransom_sticker_curl`)
##    and drop off (`ransom_sticker_drop`), one after another (`ransom_sticker_stagger`);
## 5. at zero the countdown holds (`ransom_wipe_hold`, a reading hold) and the CRT collapses
##    to a line (`ransom_cut`); then `finished` (the screen shows the audit dossier).
## MotionSkip: one press completes 1-4 (the end state: every node padlocked, the notice, the
## verb, 00:00.00, no sticker left); a press in the hold cuts at once. Reduce effects shows that
## end state at once and still holds to be read; headless never waits (no hold). View only: it
## reads the words and points it is given and emits `finished`.

signal finished

const SHADER := preload("res://shaders/ransom_lock.gdshader")
const GLITCH := &"ransom_glitch"
const WIPE := &"ransom_wipe"
const PADLOCK := &"ransom_padlock"
const NOTICE := &"ransom_notice_in"
const VERB := &"ransom_verb_stamp"
const CURL := &"ransom_sticker_curl"
const DROP := &"ransom_sticker_drop"
const STAGGER := &"ransom_sticker_stagger"
const COUNTDOWN := &"ransom_countdown"
const HOLD := &"ransom_wipe_hold"
const CUT := &"ransom_cut"
## Every motion of the lock (the hold and the cut come after them).
const MOTIONS: Array[StringName] = [GLITCH, WIPE, PADLOCK, NOTICE, VERB, CURL, DROP, STAGGER, COUNTDOWN]

## The notice's width at text scale 1.0 (round 20: 1040 px of 1920), the screen margin it
## keeps, the seal's side, the progress bar's height and the padlock's half size (px at 1.0;
## the home server's is HOME_LOCK_SCALE times bigger).
const NOTICE_W := 700.0
const SCREEN_MARGIN := 16.0
const SEAL_SIDE := 132.0
const BAR_H := 14.0
const LOCK_R := 14.0
const HOME_LOCK_SCALE := 1.35
## The notice's slide as it comes up (px) and where the verb stamp lands on it (share of the
## notice from its top-left), with its tilt (degrees).
const NOTICE_SLIDE := 14.0
const STAMP_AT := Vector2(0.72, 0.68)
const STAMP_TILT := -9.0
## The corner each sticker lifts in turn, and a defence card's die-cut border (px).
const STICKER_CORNERS: Array[VinylSticker.Lift] = [VinylSticker.Lift.TOP_RIGHT, VinylSticker.Lift.TOP_LEFT, VinylSticker.Lift.BOTTOM_RIGHT,
	VinylSticker.Lift.TOP_RIGHT, VinylSticker.Lift.BOTTOM_LEFT]
const CARD_BORDER := 7.0
## How far a dropping sticker drifts sideways (px at 1.0) and turns (degrees) as it falls.
const DROP_DRIFT := 60.0
const DROP_TURN := 40.0
## The countdown's format (minutes:seconds.hundredths).
const COUNTDOWN_FORMAT := "00:%05.2f"

var style: CorpHouseStyle = null
## The house name as printed (translated), the home server's integrity and the network's
## node count (the notice's fields).
var house_shown: String = ""
var home_now: int = 0
var home_max: int = 0
## () -> Array[Dictionary] {"at": Vector2 (global), "home": bool}: where every node of the
## Cell's network stands on the screen now (asked every frame: the city's camera may ease).
var nodes_provider: Callable = Callable()

## () -> bool: the screen behind is ready (the city baked); the lock's clock starts then. An
## invalid Callable starts it at once.
var ready_check: Callable = Callable()
## The screen as the lock found it (its first frame; null headless) and the nodes' points then:
## the dossier's prints are crops of it.
var snapshot: Image = null
var snapshot_points: Array = []
var started: bool = false
var _waited: int = 0
## Frames the screen behind draws before the lock starts (its last one is the picture), and
## the most the countdown's live number grows with the text size (it fills the notice at 2.0).
const START_FRAMES := 3
const COUNTDOWN_SCALE_CAP := 1.4

## Seconds since the lock began (game time at Motion's speed).
var elapsed: float = 0.0
var cut_elapsed: float = -1.0
var done: bool = false
var hold_left: float = -1.0

var glass: ColorRect = null
var padlocks: Control = null
var notice: PanelContainer = null
var countdown_label: Label = null
var fields_label: Label = null
var progress: Control = null
var verb_stamp: RubberStamp = null
var stickers: Array[VinylSticker] = []
var _sticker_rest: Array[Dictionary] = []
var _locks_landed: int = 0
var _marks: Array[Dictionary] = []
var _lock_count: int = 0


func _init() -> void:
	name = "RansomLock"
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	MotionSkip.register(self)


## Sets the lock up for the corporation `corporation_id` (its display name `display_name`,
## translated), the home server's integrity, and the Cell's stickers on the glass:
## [{"text": translated words, "fill": Array[Color]} or {"asset": id, "text": name}].
func setup(corporation_id: StringName, display_name: String, p_home_now: int, p_home_max: int, sticker_specs: Array[Dictionary]) -> void:
	style = CorpHouseStyle.of(corporation_id)
	house_shown = style.name_shown(display_name)
	home_now = p_home_now
	home_max = p_home_max
	glass = ColorRect.new()
	glass.name = "Takeover"
	glass.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	glass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var m := ShaderMaterial.new()
	m.shader = SHADER
	m.set_shader_parameter(&"house", style.color())
	m.set_shader_parameter(&"back", style.back())
	m.set_shader_parameter(&"motif_tex", load(MOTIF_ART % MOTIF_NAMES[clampi(style.motif, 0, MOTIF_NAMES.size() - 1)]))
	glass.material = m
	add_child(glass)
	padlocks = Control.new()
	padlocks.name = "Padlocks"
	padlocks.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	padlocks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	padlocks.draw.connect(_draw_padlocks)
	add_child(padlocks)
	_build_notice()
	verb_stamp = RubberStamp.new(tr(style.verb), style.accent(), UiTheme.DISPLAY, STAMP_TILT)
	verb_stamp.name = "VerbStamp"
	add_child(verb_stamp)
	for spec in sticker_specs:
		# 1B's vinyl: a word sticker, or a defence card (an object sticker framing its face).
		var v := VinylSticker.new()
		if spec.has("asset"):
			v.shape = VinylSticker.Shape.RECT
			v.border_px = CARD_BORDER
			v.body_size = DefenceCardFace.SIZE * Settings.text_scale
			var face := DefenceCardFace.new(StringName(String(spec["asset"])), String(spec["text"]))
			v.content_root.add_child(face)
			face.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		else:
			v.text = String(spec["text"])
			v.fill = int(spec.get("fill", VinylSticker.Fill.YELLOW))
			v.font_step = int(spec.get("size", UiTheme.HEADING))
		v.name = "Sticker%d" % stickers.size()
		v.seed = stickers.size() + 1
		v.lifted_corner = STICKER_CORNERS[stickers.size() % STICKER_CORNERS.size()]
		add_child(v)
		v.resized.connect(_layout_stickers)
		stickers.append(v)
	resized.connect(_layout_stickers)
	_layout_stickers.call_deferred()
	_apply()
	# Hidden until the screen behind is ready (`ready_check`): its first frame is the picture.
	visible = false


func _build_notice() -> void:
	var s := Settings.text_scale
	notice = PanelContainer.new()
	notice.name = "Notice"
	notice.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var box := StyleBoxFlat.new()
	box.bg_color = Color(style.back(), 0.94)
	box.border_color = style.color()
	box.set_border_width_all(maxi(2, roundi(2.0 * s)))
	notice.add_theme_stylebox_override(&"panel", box)
	add_child(notice)
	var col := VBoxContainer.new()
	col.add_theme_constant_override(&"separation", 0)
	notice.add_child(col)
	# The header bar: the house and NOTICE, its reference on the right.
	var bar := PanelContainer.new()
	var bar_box := StyleBoxFlat.new()
	bar_box.bg_color = style.color()
	bar_box.content_margin_left = UiTheme.SP_M * s
	bar_box.content_margin_right = UiTheme.SP_M * s
	bar_box.content_margin_top = UiTheme.SP_S * s
	bar_box.content_margin_bottom = UiTheme.SP_S * s
	bar.add_theme_stylebox_override(&"panel", bar_box)
	col.add_child(bar)
	var head_row := HBoxContainer.new()
	bar.add_child(head_row)
	var who := _label(tr("%s  //  NOTICE") % house_shown.to_upper(), Palette.mono(), UiTheme.LABEL, style.back())
	who.name = "House"
	who.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_row.add_child(who)
	head_row.add_child(_label(tr(style.ref), Palette.mono(), UiTheme.BODY, style.back()))
	# The body: the seal beside the head line, the sub line, the fields and the progress.
	var body := MarginContainer.new()
	for side in ["left", "right", "top"]:
		body.add_theme_constant_override("margin_" + side, roundi(UiTheme.SP_L * s))
	body.add_theme_constant_override(&"margin_bottom", roundi(UiTheme.SP_S * s))
	col.add_child(body)
	var row := HBoxContainer.new()
	row.add_theme_constant_override(&"separation", roundi(UiTheme.SP_L * s))
	body.add_child(row)
	var seal := Control.new()
	seal.name = "Seal"
	seal.custom_minimum_size = Vector2(SEAL_SIDE, SEAL_SIDE) * minf(s, 1.3)
	seal.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	seal.draw.connect(func() -> void: CorpSeal.draw_seal(seal, seal.size * 0.5, seal.size.x * 0.5, style.corp_id, style.color(), house_shown))
	row.add_child(seal)
	var words := VBoxContainer.new()
	words.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	words.add_theme_constant_override(&"separation", roundi(UiTheme.SP_S * s))
	row.add_child(words)
	var head := _label(tr(style.head), style.head_font(), UiTheme.HEADING, Palette.END_HOUSE_TEXT)
	head.name = "Head"
	UiWrap.whole_words(head)  # whole words, never mid-word (ART-0 F)
	words.add_child(head)
	var sub := _label(tr(style.sub), Palette.body(), UiTheme.BODY, style.color())
	sub.name = "Sub"
	UiWrap.whole_words(sub)  # whole words, never mid-word (ART-0 F)
	words.add_child(sub)
	fields_label = _label("", Palette.mono(), UiTheme.BODY, Palette.END_HOUSE_TEXT)
	fields_label.name = "Fields"
	UiWrap.whole_words(fields_label)  # whole words, never mid-word (ART-0 F)
	words.add_child(fields_label)
	progress = Control.new()
	progress.name = "Progress"
	progress.custom_minimum_size = Vector2(0, BAR_H * s)
	progress.draw.connect(_draw_progress)
	words.add_child(progress)
	# The countdown to the wipe.
	var clock := MarginContainer.new()
	clock.add_theme_constant_override(&"margin_left", roundi(UiTheme.SP_L * s))
	clock.add_theme_constant_override(&"margin_right", roundi(UiTheme.SP_L * s))
	col.add_child(clock)
	var clock_col := VBoxContainer.new()
	clock_col.add_theme_constant_override(&"separation", 0)
	clock.add_child(clock_col)
	clock_col.add_child(_label(tr("WIPE IN"), Palette.mono(), UiTheme.TITLE, style.color()))
	countdown_label = _label(COUNTDOWN_FORMAT % 0.0, Palette.mono(), UiTheme.HERO, style.accent())
	countdown_label.add_theme_font_size_override(&"font_size", UiTheme.font_px_at(UiTheme.HERO, minf(s, COUNTDOWN_SCALE_CAP)))
	countdown_label.name = "Countdown"
	clock_col.add_child(countdown_label)
	var foot := MarginContainer.new()
	for side in ["left", "right", "bottom"]:
		foot.add_theme_constant_override("margin_" + side, roundi(UiTheme.SP_L * s))
	col.add_child(foot)
	var footer := _label(tr("decryption is not offered.  your station is no longer yours."), Palette.mono(), UiTheme.BODY, Palette.TEXT_MID)
	UiWrap.whole_words(footer)  # whole words, never mid-word (ART-0 F)
	foot.add_child(footer)


func _label(t: String, f: Font, step: int, c: Color) -> Label:
	var l := Label.new()
	l.text = t
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # translated where built
	l.add_theme_font_override(&"font", f)
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(step))
	l.add_theme_color_override(&"font_color", c)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


# --- Timeline ---------------------------------------------------------------------------------

## Where motion `id` stands now, 0..1 (1 at once when it does not play: its end state).
func phase(id: StringName, extra_delay: float = 0.0) -> float:
	if not Motion.live(id):
		return 1.0
	var d := Motion.seconds(id)
	var t := elapsed - Motion.delay_of(id) - extra_delay
	if d <= 0.0:
		return 1.0 if t >= 0.0 else 0.0
	return clampf(t / d, 0.0, 1.0)


## Seconds from the start until the last motion of the lock ends (0 when none plays).
func motion_end() -> float:
	var end := 0.0
	for id in MOTIONS:
		if Motion.live(id):
			var extra := Motion.seconds(STAGGER) * maxf(0.0, stickers.size() - 1.0) if id in [CURL, DROP] else 0.0
			end = maxf(end, Motion.delay_of(id) + Motion.seconds(id) + extra)
	return end


## MotionSkip: the lock's motion plays.
func motion_running() -> bool:
	return not done and cut_elapsed < 0.0 and elapsed < motion_end()


## MotionSkip: shows the end state of every motion (the hold then runs as normal).
func complete_motion() -> void:
	elapsed = maxf(elapsed, motion_end())
	_apply()


## The reading hold after the countdown (s): `ransom_wipe_hold` when switched on, none headless.
func hold_seconds() -> float:
	if DisplayServer.get_name() == "headless" and not Motion.force_live:
		return 0.0
	return Motion.seconds(HOLD) if Motion.switched_on(HOLD) else 0.0


## Cuts to the end now (a press in the hold, or the hold's end): the CRT collapse when it
## plays, then `finished`.
func cut() -> void:
	if done or cut_elapsed >= 0.0:
		return
	elapsed = maxf(elapsed, motion_end())
	cut_elapsed = 0.0
	if not Motion.live(CUT):
		_finish()
	else:
		_apply()


func _finish() -> void:
	if done:
		return
	done = true
	_apply()
	finished.emit()


## True when the lock shows at all: a real display (or Motion.force_live). Headless never
## waits on it (the screen goes straight to the dossier); reduce effects shows its end state.
static func plays_now() -> bool:
	return Motion.force_live or DisplayServer.get_name() != "headless"


func _process(delta: float) -> void:
	if done:
		return
	if not started:
		# The page under the lock draws for a few frames first (its picture is the prints').
		_waited += 1
		if _waited < START_FRAMES or (ready_check.is_valid() and not bool(ready_check.call())):
			return
		started = true
		_take_snapshot()
		visible = true
		return
	if cut_elapsed >= 0.0:
		cut_elapsed += delta
		_apply()
		if cut_elapsed >= Motion.seconds(CUT):
			_finish()
		return
	elapsed += delta
	_apply()
	if elapsed >= motion_end():
		# The countdown is at zero: the reading hold, then the cut.
		if hold_left < 0.0:
			hold_left = hold_seconds()
		else:
			hold_left -= delta
		if hold_left <= 0.0:
			cut()


## The screen as it stands (the last drawn frame, before the takeover shows) for the prints.
func _take_snapshot() -> void:
	snapshot_points = nodes_provider.call() if nodes_provider.is_valid() else []
	if DisplayServer.get_name() == "headless":
		return
	var tex := get_viewport().get_texture()
	snapshot = tex.get_image() if tex != null else null


func _input(event: InputEvent) -> void:
	if done or not is_visible_in_tree():
		return
	if motion_running():
		MotionSkip.handle(event, self)
	elif cut_elapsed < 0.0 and MotionSkip.is_press(event) and not MotionSkip.pause_open(self):
		MotionSkip.consume(self, event)
		cut()


# --- Drawing ----------------------------------------------------------------------------------

## Applies the timeline to the pieces.
func _apply() -> void:
	if glass == null:
		return
	var s := Settings.text_scale
	var m := glass.material as ShaderMaterial
	var g := phase(GLITCH)
	m.set_shader_parameter(&"glitch", Motion.amplitude(GLITCH) * (1.0 - g) if g < 1.0 else 0.0)
	m.set_shader_parameter(&"wipe", phase(WIPE))
	m.set_shader_parameter(&"collapse", clampf(cut_elapsed / maxf(0.001, Motion.seconds(CUT)), 0.0, 1.0) if cut_elapsed >= 0.0 else (1.0 if done else 0.0))
	m.set_shader_parameter(&"screen", size)
	_update_padlocks()
	padlocks.queue_redraw()
	# The notice comes up, then the verb lands on it.
	var n := phase(NOTICE)
	notice.modulate.a = n
	var w := minf(NOTICE_W * s, size.x - SCREEN_MARGIN * 2.0)
	notice.custom_minimum_size.x = w
	notice.size = Vector2(w, notice.get_combined_minimum_size().y)
	notice.position = ((size - notice.size) * 0.5).floor() + Vector2(0, -NOTICE_SLIDE * (1.0 - n))
	var v := phase(VERB)
	verb_stamp.visible = v > 0.0 and n > 0.0
	verb_stamp.position = notice.position + notice.size * STAMP_AT - verb_stamp.size * 0.5
	var amp := Motion.amplitude(VERB)
	verb_stamp.scale = Vector2.ONE * lerpf(amp, 1.0, ease(v, 0.4)) if amp > 0.0 else Vector2.ONE
	# The fields and the countdown.
	countdown_label.text = COUNTDOWN_FORMAT % (Motion.amplitude(COUNTDOWN) * (1.0 - phase(COUNTDOWN)))
	fields_label.text = tr("HOME SERVER  %02d/%d   //   NODES ENCRYPTED  %d/%d") % [home_now, home_max, _locks_landed, _lock_count]
	progress.queue_redraw()
	_apply_stickers()


func _layout_stickers() -> void:
	_sticker_rest.clear()
	var s := Settings.text_scale
	var margin := SCREEN_MARGIN * s
	# The title sticker top-left, the cards in a row along the foot, the Cell's name bottom-right.
	var cards: Array[VinylSticker] = []
	# Each sticker is placed by its body (its art's shadow pad lies round it).
	for i in stickers.size():
		var v := stickers[i]
		var body := v.body_rect.size
		var at := Vector2.ZERO
		if v.shape == VinylSticker.Shape.RECT:
			cards.append(v)
			continue
		if i == 0:
			at = Vector2(margin * 2.0, margin)
		else:
			at = Vector2(size.x - body.x - margin * 2.0, size.y - body.y - margin * 1.5)
		_sticker_rest.append({"v": v, "at": at - v.body_rect.position, "tilt": [-1.5, -3.0, 2.0][i % 3]})
	var gap := margin * 0.6
	var row_w := 0.0
	for c in cards:
		row_w += c.body_rect.size.x + gap
	var x := (size.x - row_w) * 0.5
	for i in cards.size():
		var c := cards[i]
		var at := Vector2(x, size.y - c.body_rect.size.y - margin * 1.2)
		_sticker_rest.append({"v": c, "at": at - c.body_rect.position, "tilt": [-2.0, 1.5, -1.0, 2.0, -1.5][i % 5]})
		x += c.body_rect.size.x + gap
	_apply_stickers()


func _apply_stickers() -> void:
	var curl_amp := Motion.amplitude(CURL)
	var fall := Motion.amplitude(DROP) * Settings.text_scale
	var stagger := Motion.seconds(STAGGER) if Motion.live(STAGGER) else 0.0
	for i in _sticker_rest.size():
		var r: Dictionary = _sticker_rest[i]
		var v: VinylSticker = r["v"]
		var lag := stagger * i
		var c := phase(CURL, lag)
		var d := phase(DROP, lag)
		v.fold = curl_amp * c
		v.lift = d
		var side := -1.0 if i % 2 == 0 else 1.0
		v.position = (r["at"] as Vector2) + Vector2(side * DROP_DRIFT * Settings.text_scale * d, fall * d * d)
		v.rotation_degrees = float(r["tilt"]) + side * DROP_TURN * d
		v.modulate.a = 1.0 - d * 0.3
		v.visible = d < 1.0


## Where each padlock stands and how big it is now (`_marks`), and how many have landed: a
## lock lands as the wipe's edge passes its node (its pop runs from that moment).
func _update_padlocks() -> void:
	_marks.clear()
	var pts: Array = nodes_provider.call() if nodes_provider.is_valid() else []
	_lock_count = pts.size()
	var s := Settings.text_scale
	var w := phase(WIPE)
	var edge_y := (w * 1.12 - 0.06) * size.y
	var inv := padlocks.get_global_transform().affine_inverse() if padlocks.is_inside_tree() else Transform2D.IDENTITY
	var pop := Motion.amplitude(PADLOCK)
	var pop_live := Motion.live(PADLOCK) and Motion.seconds(PADLOCK) > 0.0
	for p: Dictionary in pts:
		var at: Vector2 = inv * (p["at"] as Vector2)
		if at.y > edge_y and w < 1.0:
			continue
		var t := 1.0
		if pop_live:
			var passed := Motion.delay_of(WIPE) + Motion.seconds(WIPE) * clampf((at.y / maxf(1.0, size.y) + 0.06) / 1.12, 0.0, 1.0)
			t = clampf((elapsed - passed) / Motion.seconds(PADLOCK), 0.0, 1.0)
		var r := LOCK_R * s * (HOME_LOCK_SCALE if p.get("home", false) else 1.0) * lerpf(pop, 1.0, t)
		_marks.append({"at": at, "r": r})
	_locks_landed = _marks.size()


func _draw_padlocks() -> void:
	for m in _marks:
		draw_padlock(padlocks, m["at"], m["r"], style.accent())


## Draws a padlock centred on `c` with half size `r`: round 20's own `padlock` (M14 asset
## parity, `assets/campaign_end/padlock.png`), tinted `col` (its keyhole keeps its ink) over
## the shadow pool that lifts it off the city.
static func draw_padlock(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	ci.draw_circle(c + Vector2(0, r * 0.2), r * 1.15, Palette.SHADOW)
	var side := r * PADLOCK_SIDE
	var at := c + Vector2(0, r * PADLOCK_DROP)
	ci.draw_texture_rect(_padlock(), Rect2(at - Vector2(side, side) * 0.5, Vector2(side, side)), false, col)


## The house motifs (round 20 `motif(style, 1)`, M14 asset parity), by CorpHouseStyle.Motif.
const MOTIF_ART := "res://assets/campaign_end/motif_%s.png"
const MOTIF_NAMES: Array[String] = ["blueprint", "hazard", "cells", "stars", "glitch"]
## The lock's texture side and its centre's drop, as shares of the half size (the concept's
## lock fills 0.88 of its box, shackle to foot).
const PADLOCK_SIDE := 1.95
const PADLOCK_DROP := 0.2
const PADLOCK_ART := "res://assets/campaign_end/padlock.png"


static func _padlock() -> Texture2D:
	if _padlock_tex == null:
		_padlock_tex = load(PADLOCK_ART) as Texture2D
	return _padlock_tex


static var _padlock_tex: Texture2D = null


func _draw_progress() -> void:
	var r := Rect2(Vector2.ZERO, progress.size)
	progress.draw_rect(r, style.color(), false, 2.0)
	var share := float(_locks_landed) / maxf(1.0, _lock_count) if _lock_count > 0 else phase(WIPE)
	var inner := r.grow(-4.0)
	inner.size.x *= share
	progress.draw_rect(inner, style.accent())
