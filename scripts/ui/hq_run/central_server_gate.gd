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
## Parity S-HQRUN (designer group ruling 2026-10-05; exploits.py `panel()` / `backdrop()` on
## art-concepts-r43): the panel is the concept's bordered card (dark glass, a 2 px edge in the
## corp colour once the breach is ready, grey before, the corp bar down its left side) at the
## concept's size, each socket's kind word under it, BREACH centred under the panel; the page
## behind is blurred and dimmed (the shared GlassScrim) and darker behind the panel and the
## wheel; the page's own CENTRAL SERVER chip steps aside while the gate is open (one label).
## The exploit-effect card (INTEL // ... BREACHED) and the cut slices on the preview are G6:
## listed, not built.

signal breach_pressed
signal back_pressed

## The group an open gate is in (the page's chip comes back when the last one leaves).
const GROUP := &"central_server_gate"

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

## Design sizes (px at 1280 x 720: the concept's 1920 board at two thirds; times the text
## scale where they hold words). The panel's width, its corner radius, edge and the corp bar
## down its left side (width, inset from the top and bottom), its padding.
const PANEL_WIDTH := 427.0
const PANEL_WIDTH_SCALE_MAX := 1.5
const PANEL_RADIUS := 9
const PANEL_EDGE := 2
const BAR_WIDTH := 4.0
const BAR_INSET := 7.0
const PANEL_PAD := Vector2(19, 11)
## A socket (the keycard plus its ring room), an extra socket, their gaps.
const SOCKET_SIZE := Vector2(128, 175)
const EXTRA_SIZE := Vector2(80, 53)
const SOCKET_GAP := 5.0
const EXTRA_GAP := 54.0
const SOCKET_RADIUS := 8
const RING_WIDTH := 2.0
const DASH := 9.0
const DASH_GAP := 6.0
const BREACH_SIZE := Vector2(200, 92)
const WHEEL_SIZE := Vector2(400, 400)
## The page's margin left of the panel, and the free width right of the wheel against the
## width between the panel and the wheel (the concept's wheel centre at 65 % of the width).
const PAGE_MARGIN := 40
const WHEEL_RIGHT_RATIO := 1.5
## Lettering (px at text scale 1.0): the header, the subtitle, EXPLOITS and the count, the
## "minimum" words, a socket's kind word, the EXTRA line, the footer.
const HEAD_FONT := 15
const SUB_FONT := 12
const EXPLOITS_FONT := 23
const COUNT_FONT := 29
const MIN_FONT := 12
const KIND_FONT := 12
const EXTRA_FONT := 12
const FOOTER_FONT := 19
const ROW_GAP := 6
const BUTTON_GAP := 24
## The concept's panel colours (exploits.py panel()) as the nearest palette tokens: the glass
## (10, 9, 15 at 228 -> the night background at PANEL_GLASS_ALPHA), the idle edge, the header,
## subtitle and "minimum" greys, an empty socket's fill and dash, an extra's dash, an idle kind
## word; a lit socket's fill is the corp colour darkened by SOCKET_LIT_DARK.
const PANEL_GLASS_ALPHA := 0.894
const PANEL_FILL := Color(Palette.NET_BG_OUTER, PANEL_GLASS_ALPHA)
const EDGE_IDLE := Palette.DISABLED
const HEAD_COLOR := Palette.TEXT_MID
const SUB_COLOR := Palette.TEXT_LO
const MIN_COLOR := Palette.TEXT_MID
const SOCKET_EMPTY_FILL := Palette.DESK_DARK
const SOCKET_DASH := Palette.TEXT_LO
const EXTRA_DASH := Palette.DISABLED
const KIND_IDLE := Palette.TEXT_LO
const SOCKET_LIT_DARK := 0.88
## GATE-03: the page behind darkens further toward the panel's side (exploits.py backdrop():
## x 0.45 at the left edge, nothing past SHADE_REACH of the width) and under the wheel (a
## soft dark disc SHADOW_SHARE of the wheel's size, SHADOW_ALPHA at its centre).
const SHADE_ALPHA := 0.45
const SHADE_REACH := 0.4
const SHADOW_SHARE := 0.75
const SHADOW_ALPHA := 0.67
const SHADOW_SEGMENTS := 48
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
## The panel (the concept's bordered card) and the page's blur behind the gate.
var panel: PanelContainer = null
var scrim: GlassScrim = null
var _cards: Array[TextureRect] = []
var _sockets: Array[Control] = []
var _breach_on: TextureRect = null
var _count_label: Label = null
var _footer: Label = null
var _shade: Control = null
var _wheel_box: Control = null
var _tween: Tween = null


func _init() -> void:
	name = "CentralServerGate"
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


## GATE-02: the HQ-run page under the gate hides its CENTRAL SERVER chip while the gate is
## open (the gate's header names the server once).
func _enter_tree() -> void:
	add_to_group(GROUP)
	get_tree().call_group(HqRunView.GROUP, &"set_gate_open", true)


## The page gets its chip back once the last gate leaves (a gate freed while a new one opens
## leaves the new one's page as it is).
func _exit_tree() -> void:
	for g in get_tree().get_nodes_in_group(GROUP):
		if g != self:
			return
	get_tree().call_group(HqRunView.GROUP, &"set_gate_open", false)


## True when the breach has every Exploit it needs (the panel's edge and footer in the corp
## colour, BREACH pink).
func ready_to_breach() -> bool:
	return held.size() >= needed


## Builds the gate for `corp` (`corp_name`, the Central Server `server_name` at `tier`) with
## the Exploit kinds `p_held` of the `p_needed` the breach takes, and the boss of `preview`
## (NetrunSession.breach_preview(); null: no wheel).
func setup(p_corp: StringName, corp_name: String, server_name: String, tier: int, p_held: Array[int], p_needed: int,
		preview: CombatSession, lookup: ContentLookup) -> void:
	corp = p_corp
	held = p_held.duplicate()
	needed = p_needed
	var k := Settings.text_scale
	var accent := Palette.corp_color(corp)
	scrim = GlassScrim.new()
	scrim.name = "Scrim"
	scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(scrim)
	_shade = Control.new()
	_shade.name = "Shade"
	_shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_shade.draw.connect(_draw_shade)
	add_child(_shade)
	var page := MarginContainer.new()
	page.name = "Page"
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	page.add_theme_constant_override("margin_left", PAGE_MARGIN)
	page.add_theme_constant_override("margin_right", PAGE_MARGIN)
	add_child(page)
	var row := HBoxContainer.new()
	row.name = "Row"
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.add_child(row)
	var col := VBoxContainer.new()
	col.name = "PanelColumn"
	col.alignment = BoxContainer.ALIGNMENT_CENTER
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_theme_constant_override("separation", roundi(UiTheme.SP_S * k))
	row.add_child(col)
	panel = PanelContainer.new()
	panel.name = "ServerPanel"
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.custom_minimum_size.x = PANEL_WIDTH * clampf(k, 1.0, PANEL_WIDTH_SCALE_MAX)
	var box := StyleBoxFlat.new()
	box.bg_color = PANEL_FILL
	box.border_color = accent if ready_to_breach() else EDGE_IDLE
	box.set_border_width_all(PANEL_EDGE)
	box.set_corner_radius_all(PANEL_RADIUS)
	box.content_margin_left = PANEL_PAD.x
	box.content_margin_right = PANEL_PAD.x
	box.content_margin_top = PANEL_PAD.y
	box.content_margin_bottom = PANEL_PAD.y
	panel.add_theme_stylebox_override(&"panel", box)
	panel.draw.connect(_draw_panel_bar)
	col.add_child(panel)
	var body := VBoxContainer.new()
	body.name = "Body"
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_theme_constant_override("separation", ROW_GAP)
	panel.add_child(body)
	var head := _label(tr(TITLE) % server_name, Palette.body_medium(), HEAD_FONT, HEAD_COLOR)
	head.name = "ServerTitle"
	head.uppercase = true
	body.add_child(head)
	var sub := _label(tr(SUBTITLE) % [corp_name.to_upper(), tier], Palette.mono(), SUB_FONT, SUB_COLOR)
	sub.name = "Subtitle"
	body.add_child(sub)
	var count_row := HBoxContainer.new()
	count_row.name = "CountRow"
	count_row.add_theme_constant_override("separation", roundi(UiTheme.SP_L * k))
	body.add_child(count_row)
	count_row.add_child(_label(tr(EXPLOITS_WORD), Palette.display(), EXPLOITS_FONT, Palette.PAPER, false))
	_count_label = _label("%d/%d" % [held.size(), needed], Palette.display(), COUNT_FONT, accent if ready_to_breach() else Palette.PAPER, false)
	_count_label.name = "ExploitCount"
	count_row.add_child(_count_label)
	var mn := _label(tr(MIN_WORDS), Palette.body_medium(), MIN_FONT, MIN_COLOR)
	mn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	mn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	count_row.add_child(mn)
	var sockets := HBoxContainer.new()
	sockets.name = "Sockets"
	sockets.alignment = BoxContainer.ALIGNMENT_CENTER
	sockets.add_theme_constant_override("separation", roundi(SOCKET_GAP))
	body.add_child(sockets)
	for i in KINDS.size():
		sockets.add_child(_socket(i, accent))
	body.add_child(_label(tr(EXTRA_WORDS), Palette.body_medium(), EXTRA_FONT, SUB_COLOR))
	var extras := HBoxContainer.new()
	extras.name = "Extras"
	extras.alignment = BoxContainer.ALIGNMENT_CENTER
	extras.add_theme_constant_override("separation", roundi(EXTRA_GAP))
	body.add_child(extras)
	for i in EXTRA_SOCKETS:
		var e := Control.new()
		e.name = "Extra%d" % (i + 1)
		e.custom_minimum_size = EXTRA_SIZE
		e.mouse_filter = Control.MOUSE_FILTER_IGNORE
		e.draw.connect(_draw_extra.bind(e))
		extras.add_child(e)
	_footer = _label((tr(READY_WORDS) if ready_to_breach() else tr(LOCKED_WORDS)) % [held.size(), needed], Palette.display(), FOOTER_FONT,
		accent if ready_to_breach() else Palette.TEXT_LO)
	_footer.name = "Footer"
	body.add_child(_footer)
	var buttons := HBoxContainer.new()
	buttons.name = "Buttons"
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
	breach_button.disabled = not ready_to_breach()
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
	var gap := Control.new()
	gap.name = "Gap"
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(gap)
	_wheel_box = CenterContainer.new()
	_wheel_box.name = "WheelBox"
	_wheel_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_wheel_box.custom_minimum_size = WHEEL_SIZE
	row.add_child(_wheel_box)
	var right := Control.new()
	right.name = "Right"
	right.mouse_filter = Control.MOUSE_FILTER_IGNORE
	right.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right.size_flags_stretch_ratio = WHEEL_RIGHT_RATIO
	row.add_child(right)
	if preview != null and lookup != null:
		var boss := _boss_of(preview)
		if boss != null:
			wheel = WheelView.new()
			wheel.name = "BossWheel"
			wheel.custom_minimum_size = WHEEL_SIZE
			wheel.mouse_filter = Control.MOUSE_FILTER_IGNORE
			_wheel_box.add_child(wheel)
			wheel.show_combatant(boss, preview.state.satellites_of(boss.id), [], lookup)
	_wheel_box.resized.connect(_shade.queue_redraw)
	_card_t.resize(KINDS.size())
	_ring_t.resize(KINDS.size())
	_card_t.fill(0.0)
	_ring_t.fill(0.0)


## A label in `font` at `px` x the text scale in `color`; `wrap` breaks it at whole words.
func _label(text: String, font: Font, px: int, color: Color, wrap: bool = true) -> Label:
	var l := Label.new()
	l.text = text
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	l.add_theme_font_override(&"font", font)
	l.add_theme_font_size_override(&"font_size", maxi(1, roundi(px * Settings.text_scale)))
	l.add_theme_color_override(&"font_color", color)
	if wrap:
		UiWrap.whole_words(l)
	return l


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


## A socket: the keycard's slot (its ring, the card) and the kind word under it in the corp
## colour once filled (the concept's INTEL / BREACH / VIRUS line).
func _socket(i: int, accent: Color) -> Control:
	var holder := VBoxContainer.new()
	holder.name = "Holder%d" % (i + 1)
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	holder.add_theme_constant_override("separation", roundi(UiTheme.SP_XS * Settings.text_scale))
	var s := Control.new()
	s.name = "Socket%d" % (i + 1)
	s.custom_minimum_size = SOCKET_SIZE
	s.mouse_filter = Control.MOUSE_FILTER_IGNORE
	s.draw.connect(_draw_socket.bind(i, s))
	_sockets.append(s)
	holder.add_child(s)
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
	var word := _label(tr(KIND_WORDS[kind]), Palette.display(), KIND_FONT, accent if socket_filled(i) else KIND_IDLE, false)
	word.name = "Kind"
	word.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	holder.add_child(word)
	return holder


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
	if ready_to_breach():
		var e := Motion.entry(READY)
		var start := at + slap + ring - step if at > 0.0 else 0.0
		var breach := _tween.parallel().tween_property(self, "breach_t", 1.0, maxf(ready, 0.01)).set_delay(maxf(0.0, start))
		if e != null:
			breach.set_ease(e.ease).set_trans(e.trans)
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
	breach_t = 1.0 if ready_to_breach() else 0.0


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
	var sb := StyleBoxFlat.new()
	sb.set_corner_radius_all(SOCKET_RADIUS)
	if _ring_t[i] > 0.0:
		var accent := Palette.corp_color(corp)
		sb.bg_color = Color(accent.darkened(SOCKET_LIT_DARK), _ring_t[i])
		sb.border_color = Color(accent, _ring_t[i])
		sb.set_border_width_all(roundi(RING_WIDTH))
		s.draw_style_box(sb, r.grow((1.0 - _ring_t[i]) * _ring_amp()))
		return
	sb.bg_color = SOCKET_EMPTY_FILL
	s.draw_style_box(sb, r)
	_dashed_rect(s, r, SOCKET_DASH)
	_plus(s, r, SOCKET_DASH)


func _ring_amp() -> float:
	var e := Motion.entry(RING)
	return e.amplitude if e != null else 0.0


func _draw_extra(e: Control) -> void:
	var r := Rect2(Vector2.ZERO, e.size).grow(-1.0)
	_dashed_rect(e, r, EXTRA_DASH)
	_plus(e, r, EXTRA_DASH)


func _plus(ci: CanvasItem, r: Rect2, col: Color) -> void:
	var c := r.get_center()
	var arm := minf(r.size.x, r.size.y) * PLUS_SHARE
	ci.draw_line(c - Vector2(arm, 0), c + Vector2(arm, 0), col, DASH_WIDTH)
	ci.draw_line(c - Vector2(0, arm), c + Vector2(0, arm), col, DASH_WIDTH)


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


## The corp bar down the panel's left side (exploits.py panel(): inside the edge, short of
## the corners).
func _draw_panel_bar() -> void:
	var h := panel.size.y - BAR_INSET * 2.0
	if h > 0.0:
		panel.draw_rect(Rect2(PANEL_EDGE, BAR_INSET, BAR_WIDTH, h), Palette.corp_color(corp))


## GATE-03: the page behind darker toward the panel's side and under the wheel (over the
## blur and dim of the scrim).
func _draw_shade() -> void:
	var w := _shade.size.x
	var h := _shade.size.y
	var dark := Color(Palette.NIGHT_SKY, SHADE_ALPHA)
	var clear := Color(Palette.NIGHT_SKY, 0.0)
	_shade.draw_polygon(PackedVector2Array([Vector2.ZERO, Vector2(w * SHADE_REACH, 0), Vector2(w * SHADE_REACH, h), Vector2(0, h)]),
		PackedColorArray([dark, clear, clear, dark]))
	if _wheel_box == null or wheel == null:
		return
	var c := _wheel_box.global_position - _shade.global_position + _wheel_box.size * 0.5
	var r := WHEEL_SIZE.x * SHADOW_SHARE
	var pts := PackedVector2Array([c])
	var cols := PackedColorArray([Color(Palette.NIGHT_SKY, SHADOW_ALPHA)])
	for q in SHADOW_SEGMENTS + 1:
		pts.append(c + Vector2.from_angle(TAU * q / SHADOW_SEGMENTS) * r)
		cols.append(clear)
	for q in SHADOW_SEGMENTS:
		_shade.draw_polygon(PackedVector2Array([pts[0], pts[q + 1], pts[q + 2]]), PackedColorArray([cols[0], cols[q + 1], cols[q + 2]]))


## The rects (local) the gate lays out: the panel, BREACH, Back and the wheel (tests: on the
## page and apart at every text size).
func layout_rects() -> Dictionary:
	var out := {}
	for key: String in ["panel", "breach", "back", "wheel"]:
		var c: Control = {"panel": panel, "breach": breach_button, "back": back_button, "wheel": wheel}[key]
		if c != null:
			out[key] = Rect2(c.global_position - global_position, c.size)
	return out


## The pad / keyboard focus on BREACH: a lime frame round the vinyl (§2.10).
func _draw_breach_focus() -> void:
	if breach_button.has_focus():
		breach_button.draw_rect(Rect2(Vector2.ZERO, breach_button.size).grow(FOCUS_GROW), Palette.CELL_ACID, false, FOCUS_WIDTH)
