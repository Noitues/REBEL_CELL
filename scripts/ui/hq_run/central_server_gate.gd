class_name CentralServerGate
extends Control
## ART-8 8w: the Central Server's gate (bible 4.9, LOCKED look, round 38
## `central_server_gate.png`), shown before the HQ breach on the current rules: the boss
## wheel in front of its dimmed compound; the CENTRAL SERVER panel with three keycard
## sockets (+ two dashed extras for the expanded set) and `EXPLOITS n/min`; each Exploit
## held slaps into its socket and the socket rings in the corp colour; once every card is in,
## the grey BREACH vinyl turns pink. The keycards and the BREACH vinyl are the concept
## generator's own art (assets/hq_run, exploits.py on art-concepts-r43). The boss wheel shows
## NetrunSession.breach_preview(): the gate preview equals the fight start.
## Reduce effects / reduce motion show the end state at once; one press completes the motion
## (MotionSkip). A view: it emits `breach_pressed` / `back_pressed` and never changes state.

signal breach_pressed
signal back_pressed

const KEYCARD_DIR := "res://assets/hq_run/keycards/"
const BREACH_OFF := preload("res://assets/hq_run/breach_off.png")
const BREACH_ON := preload("res://assets/hq_run/breach_on.png")
## The kinds a socket takes, in socket order (today's three Exploit categories).
const KINDS: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
## The expanded set's extra sockets (LOCKED as options, bible 4.9): drawn dashed and empty.
const EXTRA_SOCKETS := 2
## Motion: a card's slap (VinylSticker's), the stagger between cards, the socket's ring in
## the corp colour, the BREACH vinyl turning pink.
const SLAP := &"sticker_slap"
const STAGGER := &"gate_keycard_stagger"
const RING := &"gate_socket_ring"
const READY := &"gate_breach_ready"
## A slapped card starts this much bigger and turned by the slap's amplitude (degrees).
const SLAP_FROM_SCALE := 1.35

const TITLE := "CENTRAL SERVER // %s" # TR
const SUBTITLE := "%s  //  TIER %d" # TR
const EXPLOITS_WORD := "EXPLOITS" # TR
const MIN_WORDS := "minimum to breach" # TR
const EXTRA_WORDS := "EXTRA  (each one weakens the boss further)" # TR
const READY_WORDS := "%d/%d  -  BREACH READY" # TR
const LOCKED_WORDS := "%d/%d  -  LOCKED" # TR
const BACK_WORDS := "Back to the compound" # TR
const BREACH_TIP := "BREACH: start the fight at the Central Server." # TR
const KIND_WORDS := {RC.ExploitType.INTEL: "INTEL", RC.ExploitType.BREACH: "BREACH", RC.ExploitType.VIRUS: "VIRUS"} # TR

## Design sizes (px at 1280 x 720, times the text scale where they hold words).
const PANEL_WIDTH := 600.0
const SOCKET_SIZE := Vector2(170, 224)
const EXTRA_SIZE := Vector2(110, 72)
const SOCKET_GAP := 14.0
const RING_WIDTH := 4.0
const DASH := 9.0
const DASH_GAP := 6.0
const BREACH_SIZE := Vector2(232, 106)
const WHEEL_SIZE := Vector2(420, 420)
const SCRIM_ALPHA := 0.55
const ROW_GAP := 40
const COUNT_FONT := 26
const FOOTER_FONT := 22
const KIND_FONT := 16
const COUNT_GAP := 18
const BUTTON_GAP := 24
## Dashed outlines: line width, the extra socket's plus sign (share of its short side).
const DASH_WIDTH := 2.0
const PLUS_SHARE := 0.08
## The focus frame round BREACH (px out, width).
const FOCUS_GROW := 3.0
const FOCUS_WIDTH := 3.0

var corp: StringName = &""
var held: Array[int] = []
var needed: int = 3
## 0..1 per socket: the card's slap and the ring.
var _card_t: Array[float] = []
var _ring_t: Array[float] = []
## 0 grey .. 1 pink.
var breach_t: float = 0.0:
	set(v):
		breach_t = v
		if _breach_on != null:
			_breach_on.modulate.a = v

var wheel: WheelView = null
var breach_button: TextureButton = null
var back_button: Button = null
var _cards: Array[TextureRect] = []
var _sockets: Array[Control] = []
var _breach_on: TextureRect = null
var _count_label: Label = null
var _footer: Label = null
var _tween: Tween = null


func _init() -> void:
	name = "CentralServerGate"
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## Builds the gate for `corp` (`corp_name`, the Central Server `server_name` at `tier`) with
## the Exploit kinds `p_held` of the `p_needed` the breach takes, and the boss of `preview`
## (NetrunSession.breach_preview(); null: no wheel).
func setup(p_corp: StringName, corp_name: String, server_name: String, tier: int, p_held: Array[int], p_needed: int,
		preview: CombatSession, lookup: ContentLookup) -> void:
	corp = p_corp
	held = p_held.duplicate()
	needed = p_needed
	var scrim := ColorRect.new()
	scrim.name = "Scrim"
	scrim.color = Color(Palette.NIGHT_SKY, SCRIM_ALPHA)
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(scrim)
	var row := HBoxContainer.new()
	row.name = "Row"
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", ROW_GAP)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(row)
	var col := VBoxContainer.new()
	col.name = "PanelColumn"
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(col)
	var win := TerminalWindow.new(tr(TITLE) % server_name, Palette.corp_color(corp))
	win.name = "ServerPanel"
	win.custom_minimum_size.x = PANEL_WIDTH * Settings.text_scale
	col.add_child(win)
	var sub := Label.new()
	sub.text = tr(SUBTITLE) % [corp_name.to_upper(), tier]
	sub.add_theme_color_override("font_color", Palette.TEXT_MID)
	win.body.add_child(sub)
	var count_row := HBoxContainer.new()
	count_row.add_theme_constant_override("separation", COUNT_GAP)
	win.body.add_child(count_row)
	var ex := Label.new()
	ex.text = tr(EXPLOITS_WORD)
	ex.add_theme_font_size_override("font_size", roundi(COUNT_FONT * Settings.text_scale))
	count_row.add_child(ex)
	_count_label = Label.new()
	_count_label.name = "ExploitCount"
	_count_label.text = "%d/%d" % [held.size(), needed]
	_count_label.add_theme_font_size_override("font_size", roundi(COUNT_FONT * Settings.text_scale))
	_count_label.add_theme_color_override("font_color", Palette.corp_color(corp))
	count_row.add_child(_count_label)
	var mn := Label.new()
	mn.text = tr(MIN_WORDS)
	mn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	mn.add_theme_color_override("font_color", Palette.TEXT_MID)
	count_row.add_child(mn)
	var sockets := HBoxContainer.new()
	sockets.name = "Sockets"
	sockets.add_theme_constant_override("separation", roundi(SOCKET_GAP))
	win.body.add_child(sockets)
	for i in KINDS.size():
		sockets.add_child(_socket(i))
	var extra := Label.new()
	extra.text = tr(EXTRA_WORDS)
	extra.add_theme_color_override("font_color", Palette.TEXT_MID)
	win.body.add_child(extra)
	var extras := HBoxContainer.new()
	extras.name = "Extras"
	extras.alignment = BoxContainer.ALIGNMENT_CENTER
	extras.add_theme_constant_override("separation", roundi(SOCKET_GAP * 4.0))
	win.body.add_child(extras)
	for i in EXTRA_SOCKETS:
		var e := Control.new()
		e.name = "Extra%d" % (i + 1)
		e.custom_minimum_size = EXTRA_SIZE
		e.mouse_filter = Control.MOUSE_FILTER_IGNORE
		e.draw.connect(_draw_extra.bind(e))
		extras.add_child(e)
	_footer = Label.new()
	_footer.name = "Footer"
	_footer.text = (tr(READY_WORDS) if held.size() >= needed else tr(LOCKED_WORDS)) % [held.size(), needed]
	_footer.add_theme_font_size_override("font_size", roundi(FOOTER_FONT * Settings.text_scale))
	_footer.add_theme_color_override("font_color", Palette.corp_color(corp) if held.size() >= needed else Palette.TEXT_LO)
	win.body.add_child(_footer)
	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_CENTER
	buttons.add_theme_constant_override("separation", BUTTON_GAP)
	col.add_child(buttons)
	breach_button = TextureButton.new()
	breach_button.name = "Breach"
	breach_button.texture_normal = BREACH_OFF
	breach_button.ignore_texture_size = true
	breach_button.stretch_mode = TextureButton.STRETCH_KEEP_ASPECT_CENTERED
	breach_button.custom_minimum_size = BREACH_SIZE
	breach_button.focus_mode = Control.FOCUS_ALL
	breach_button.tooltip_text = UiTip.fold(tr(BREACH_TIP))
	breach_button.disabled = held.size() < needed
	breach_button.pressed.connect(func() -> void: breach_pressed.emit())
	breach_button.focus_entered.connect(breach_button.queue_redraw)
	breach_button.focus_exited.connect(breach_button.queue_redraw)
	breach_button.draw.connect(_draw_breach_focus)
	buttons.add_child(breach_button)
	_breach_on = TextureRect.new()
	_breach_on.name = "BreachOn"
	_breach_on.texture = BREACH_ON
	_breach_on.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_breach_on.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	_breach_on.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_breach_on.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_breach_on.modulate.a = breach_t
	breach_button.add_child(_breach_on)
	back_button = Button.new()
	back_button.name = "Back"
	back_button.text = tr(BACK_WORDS)
	back_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	back_button.pressed.connect(func() -> void: back_pressed.emit())
	buttons.add_child(back_button)
	breach_button.set_meta(&"first_focus", true)
	if preview != null and lookup != null:
		var boss := _boss_of(preview)
		if boss != null:
			wheel = WheelView.new()
			wheel.name = "BossWheel"
			wheel.custom_minimum_size = WHEEL_SIZE
			wheel.mouse_filter = Control.MOUSE_FILTER_IGNORE
			row.add_child(wheel)
			wheel.show_combatant(boss, preview.state.satellites_of(boss.id), [], lookup)
	_card_t.resize(KINDS.size())
	_ring_t.resize(KINDS.size())
	_card_t.fill(0.0)
	_ring_t.fill(0.0)


func _ready() -> void:
	MotionSkip.register(self)
	play()
	if breach_button != null and not breach_button.disabled:
		breach_button.grab_focus.call_deferred()


## The boss the preview's fight opens on (its first enemy that is not a satellite).
static func _boss_of(preview: CombatSession) -> CombatantState:
	for e in preview.state.enemies:
		if not e.is_satellite:
			return e
	return null


## The keycard art of `kind` for this corp (the generator's card, at 2x).
func keycard_path(kind: int) -> String:
	return "%s%s_%s.png" % [KEYCARD_DIR, corp, String(RC.ExploitType.keys()[kind]).to_lower()]


func _socket(i: int) -> Control:
	var s := Control.new()
	s.name = "Socket%d" % (i + 1)
	s.custom_minimum_size = SOCKET_SIZE
	s.mouse_filter = Control.MOUSE_FILTER_IGNORE
	s.draw.connect(_draw_socket.bind(i, s))
	_sockets.append(s)
	var card := TextureRect.new()
	card.name = "Keycard"
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	card.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	card.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	card.offset_left = RING_WIDTH * 2.0
	card.offset_top = RING_WIDTH * 2.0
	card.offset_right = -RING_WIDTH * 2.0
	card.offset_bottom = -RING_WIDTH * 2.0
	var kind := KINDS[i]
	var path := keycard_path(kind)
	card.texture = load(path) as Texture2D if ResourceLoader.exists(path) else null
	card.visible = false
	card.tooltip_text = tr(KIND_WORDS[kind])
	s.add_child(card)
	_cards.append(card)
	return s


## True when socket `i` holds its Exploit.
func socket_filled(i: int) -> bool:
	return i >= 0 and i < KINDS.size() and held.has(KINDS[i])


## Plays the cards slapping in, the rings and BREACH turning pink (the end state at once
## when the motion is off).
func play() -> void:
	_stop()
	var step := Motion.seconds_live(STAGGER)
	var slap := Motion.seconds_live(SLAP)
	var ring := Motion.seconds_live(RING)
	var ready := Motion.seconds_live(READY)
	if (slap <= 0.0 and ring <= 0.0 and ready <= 0.0) or (held.is_empty() and held.size() < needed):
		_end_state()
		return
	_tween = create_tween()
	var at := 0.0
	for i in KINDS.size():
		if not socket_filled(i):
			continue
		_tween.parallel().tween_method(_card_step.bind(i), 0.0, 1.0, maxf(slap, 0.01)).set_delay(at)
		_tween.parallel().tween_method(_ring_step.bind(i), 0.0, 1.0, maxf(ring, 0.01)).set_delay(at + slap)
		at += step
	if held.size() >= needed:
		var e := Motion.entry(READY)
		var start := at + slap + ring - step if at > 0.0 else 0.0
		_tween.parallel().tween_property(self, "breach_t", 1.0, maxf(ready, 0.01)).set_delay(maxf(0.0, start)) \
			.set_ease(e.ease if e != null else Tween.EASE_OUT).set_trans(e.trans if e != null else Tween.TRANS_SINE)
	_tween.finished.connect(_end_state)


## True while the cards, rings or BREACH are moving (MotionSkip).
func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


## Lands the end state at once (MotionSkip).
func complete_motion() -> void:
	_stop()
	_end_state()


func _input(event: InputEvent) -> void:
	if motion_running():
		MotionSkip.handle(event, self)


func _stop() -> void:
	if _tween != null and _tween.is_valid():
		_tween.kill()
	_tween = null


func _end_state() -> void:
	_tween = null
	for i in KINDS.size():
		var on := 1.0 if socket_filled(i) else 0.0
		_card_step(on, i)
		_ring_step(on, i)
	breach_t = 1.0 if held.size() >= needed else 0.0


func _card_step(t: float, i: int) -> void:
	_card_t[i] = t
	var card := _cards[i]
	card.visible = t > 0.0
	card.modulate.a = clampf(t * 2.0, 0.0, 1.0)
	card.pivot_offset = card.size * 0.5
	var e := Motion.entry(SLAP)
	var turn := e.amplitude if e != null else 0.0
	card.scale = Vector2.ONE * lerpf(SLAP_FROM_SCALE, 1.0, t)
	card.rotation_degrees = lerpf(turn, 0.0, t)


func _ring_step(t: float, i: int) -> void:
	_ring_t[i] = t
	_sockets[i].queue_redraw()


## Card states for tests: per socket {"filled", "card", "ring"}.
func socket_states() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for i in KINDS.size():
		out.append({"filled": socket_filled(i), "card": _card_t[i], "ring": _ring_t[i]})
	return out


func _draw_socket(i: int, s: Control) -> void:
	var r := Rect2(Vector2.ZERO, s.size).grow(-RING_WIDTH * 0.5)
	var kind := KINDS[i]
	if _ring_t[i] > 0.0:
		var grow := (1.0 - _ring_t[i]) * _ring_amp()
		s.draw_rect(r.grow(grow), Color(Palette.corp_color(corp), _ring_t[i]), false, RING_WIDTH)
	else:
		_dashed_rect(s, r, Color(Palette.TEXT_LO, 0.9))
	if not socket_filled(i):
		var f := Palette.mono()
		var fs := roundi(KIND_FONT * Settings.text_scale)
		var word := tr(KIND_WORDS[kind])
		var w := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		s.draw_string(f, Vector2((s.size.x - w) * 0.5, s.size.y * 0.5), word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.TEXT_LO)


func _ring_amp() -> float:
	var e := Motion.entry(RING)
	return e.amplitude if e != null else 0.0


func _draw_extra(e: Control) -> void:
	var r := Rect2(Vector2.ZERO, e.size).grow(-1.0)
	_dashed_rect(e, r, Color(Palette.TEXT_LO, 0.8))
	var c := r.get_center()
	var arm := minf(r.size.x, r.size.y) * PLUS_SHARE
	e.draw_line(c - Vector2(arm, 0), c + Vector2(arm, 0), Palette.TEXT_LO, DASH_WIDTH)
	e.draw_line(c - Vector2(0, arm), c + Vector2(0, arm), Palette.TEXT_LO, DASH_WIDTH)


static func _dashed_rect(ci: CanvasItem, r: Rect2, col: Color) -> void:
	var pts := [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y), r.position]
	for k in 4:
		var a: Vector2 = pts[k]
		var b: Vector2 = pts[k + 1]
		var length := a.distance_to(b)
		var dir := (b - a) / maxf(length, 0.001)
		var t := 0.0
		while t < length:
			ci.draw_line(a + dir * t, a + dir * minf(t + DASH, length), col, DASH_WIDTH)
			t += DASH + DASH_GAP


## The pad / keyboard focus on BREACH: a lime frame round the vinyl (§2.10).
func _draw_breach_focus() -> void:
	if breach_button.has_focus():
		breach_button.draw_rect(Rect2(Vector2.ZERO, breach_button.size).grow(FOCUS_GROW), Palette.CELL_ACID, false, FOCUS_WIDTH)
