class_name DaemonTray
extends Control
## The installed Daemons, opened from the top bar's DAEMONS icon: a row of unique sigils
## on a terminal strip under the bar. Hovering a sigil shows its card; clicking pins its
## detail. Click outside or Esc closes. View only.

signal closed

## Art pass W8c (§4.2, §12): the card's width, its head's height and the name's gap from the
## sigil at text scale 1.0 (px; they grow with the text). The body is narrower than the card
## by the panel's inner gap (UiTheme.SP_M).
const CARD_W := 320.0
const HEAD_H := 56.0
const NAME_X := 62.0
const SIGIL_R := 24.0
## M14 12Q-MAIN: the gap kept between the tray and the screen piece it stands beside (px).
const CLEAR_GAP := 8.0
## The screen's edge margin the tray keeps (px).
const EDGE := 10.0
## The strip's minimum width (px).
const STRIP_MIN_W: float = 200.0
## The width each sigil button adds to the strip (px).
const STRIP_PER_ICON_W: float = 48.0
## The strip's horizontal padding added to its width (px).
const STRIP_PAD_W: float = 30.0
## The design-space screen width the tray is laid out against (px).
const SCREEN_W: float = 1270.0
## The strip's top offset below the subtitles (px).
const STRIP_TOP: float = 60.0
## The gap between sigil buttons (px).
const ROW_SEP: int = 8
## The sigil button's side (px).
const SIGIL_BTN: float = 40.0
## The radius the sigil is drawn at in its button (px).
const BTN_SIGIL_R: float = 17.0
## The radius of the focus/hover ring around a sigil button (px).
const RING_R: float = 20.0
## The focus/hover ring's line width (px).
const RING_W: float = 1.5
## The ring's arc point count.
const RING_POINTS: int = 24

var ids: Array[StringName] = []
var lookup: ContentLookup
var _strip: PanelContainer
var _card: TerminalWindow = null
var _card_id: StringName = &""
## M14 12Q-MAIN (audit L44: the strip and the card sat over the ROUTE window, hiding GRID VIEW and Save &
## quit): a screen rect (global) the strip and the card stand beside, never over; empty for none.
var keep_clear: Rect2 = Rect2()


## `owner_name` (the operative whose Daemons these are) leads the strip when given; `p_keep_clear`
## (global) is a piece of the screen the tray stands beside (the ROUTE window).
func _init(p_ids: Array[StringName], p_lookup: ContentLookup, anchor_x: float, owner_name: String = "", p_keep_clear: Rect2 = Rect2()) -> void:
	ids = p_ids
	lookup = p_lookup
	keep_clear = p_keep_clear
	name = "DaemonTray"
	# H24 S4: its words come translated (tr, TextDb) and show as given.
	TextDb.shown_as_given(self)
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	_strip = PanelContainer.new()
	_strip.theme_type_variation = &"TerminalPanel"
	var w := maxf(STRIP_MIN_W, ids.size() * STRIP_PER_ICON_W + STRIP_PAD_W)
	if anchor_x < STRIP_MIN_W:
		anchor_x = SCREEN_W  # the icon sits at the bar's right end
	_strip.position = Vector2(clampf(anchor_x - w, EDGE, SCREEN_W - w), SubtitleStrip.top_below(STRIP_TOP))  # under the subtitles (H21)
	add_child(_strip)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", ROW_SEP)
	_strip.add_child(row)
	if owner_name != "":
		var who := Label.new()
		who.name = "Owner"
		who.text = owner_name.to_upper()
		who.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(who)
	if ids.is_empty():
		var none := Label.new()
		none.text = tr("No Daemons installed.")
		row.add_child(none)
	for id in ids:
		var b := Button.new()
		b.flat = true
		b.name = "Daemon_" + String(id)
		b.custom_minimum_size = Vector2(SIGIL_BTN, SIGIL_BTN)
		b.add_theme_stylebox_override("focus", StyleBoxEmpty.new())
		var did := id
		b.draw.connect(func() -> void:
			var d := lookup.get_content(did) as DaemonData
			DaemonSigil.draw_sigil(b, b.size * 0.5, BTN_SIGIL_R, did, d.rarity if d != null else RC.Rarity.UNCOMMON)
			if b.has_focus() or b.is_hovered():
				b.draw_arc(b.size * 0.5, RING_R, 0, TAU, RING_POINTS, Palette.CELL_ACID, RING_W))
		var dd := lookup.get_content(did) as DaemonData
		b.tooltip_text = TextDb.t(dd, "display_name") if dd != null else String(did)
		b.mouse_entered.connect(func() -> void: show_card(did, false))
		b.focus_entered.connect(func() -> void: show_card(did, false))
		b.pressed.connect(func() -> void: show_card(did, true))
		row.add_child(b)


func _ready() -> void:
	_strip.resized.connect(_clear_strip)
	_clear_strip.call_deferred()
	UiFocus.hold(self)  # modal for keys and the pad (H20)
	UiFocus.focus_first.call_deferred(_strip)
	# ART-0 F (ported from art-pass W8a, §10): a modal: it opens with the modal motion and a
	# page change waits for it (PageTransition.after_modals). It closes at once (main's
	# UiFocus.release, so focus goes back the same frame).
	PageTransition.open_modal(self)


## The Daemon's card under the strip (`pinned` from a click keeps it while hovering others).
func show_card(id: StringName, pinned: bool) -> void:
	if _card != null and is_instance_valid(_card):
		_card.queue_free()
	var d := lookup.get_content(id) as DaemonData
	_card_id = id
	_card = TerminalWindow.new(tr("DAEMON") + (tr(" // PINNED") if pinned else ""), DaemonSigil.color_of(id))
	_card.name = "DaemonCard"
	var s := Settings.text_scale
	_card.custom_minimum_size.x = CARD_W * s
	_card.position = Vector2(minf(_strip.position.x, 1270.0 - CARD_W * s - UiTheme.SP_M), _strip.position.y + 62)
	var head := Control.new()
	head.name = "DaemonHead"
	head.custom_minimum_size = Vector2(CARD_W * s - UiTheme.SP_M, HEAD_H * s)
	var title := (TextDb.t(d, "display_name") if d != null else String(id))
	# DAEMON-01: the name at the `title` step x the text size, centred on the sigil.
	head.draw.connect(func() -> void:
		var fs := UiTheme.font_px(UiTheme.TITLE)
		DaemonSigil.draw_sigil(head, Vector2(HEAD_H, HEAD_H) * s * 0.5, SIGIL_R * s, id, d.rarity if d != null else RC.Rarity.UNCOMMON)
		var f := Palette.display()
		HighContrast.draw_text(head, f, Vector2(NAME_X * s, (head.size.y + f.get_ascent(fs) - f.get_descent(fs)) * 0.5), title.to_upper(),
			HORIZONTAL_ALIGNMENT_LEFT, head.size.x - NAME_X * s, fs, Palette.PAPER))
	_card.body.add_child(head)
	var desc := Label.new()
	desc.name = "DaemonText"
	UiWrap.whole_words(desc)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	desc.custom_minimum_size.x = CARD_W * s - UiTheme.SP_M
	# DAEMON-01: the card's words never repeat its title ("CASCADE" over "Daemon Cascade"):
	# the Daemon's own text only.
	desc.text = TextDb.t(d, "description") if d != null else String(id)
	_card.body.add_child(desc)
	add_child(_card)
	_card.resized.connect(_clear_card.bind(_card))
	_clear_card.call_deferred(_card)


## M14 12Q-MAIN (audit L44): `rect` moved left so it stands beside `keep_clear` (its right edge before
## the clear rect's left) when it would cover it; kept on screen.
func beside_clear(rect: Rect2) -> Rect2:
	if not keep_clear.has_area() or not rect.intersects(keep_clear):
		return rect
	rect.position.x = maxf(EDGE, keep_clear.position.x - CLEAR_GAP - rect.size.x)
	return rect


func _clear_strip() -> void:
	if is_instance_valid(_strip):
		_strip.position = beside_clear(Rect2(_strip.position, _strip.size)).position


func _clear_card(card: Control) -> void:
	if is_instance_valid(card) and is_instance_valid(_strip):
		var r := Rect2(Vector2(minf(_strip.position.x, SCREEN_W - card.size.x), card.position.y), card.size)
		card.position = beside_clear(r).position


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		close()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		close()
	elif UiFocus.is_device_input(event):
		get_viewport().set_input_as_handled()  # no hotkey reaches the screen behind


func close() -> void:
	closed.emit()
	UiFocus.release(self)
