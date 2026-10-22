class_name ConfirmDialog
extends Control
## A confirm: a terminal panel (`> CONFIRM // <TITLE>`, ART_BIBLE v2 §4.13, round 33
## `abandon_dialog`) with the question and its body, a yellow vinyl sticker for the safe
## answer (CANCEL, default focus) and a pink one for the committing verb (§2.10: two-sticker
## choice), each with its small terminal caption. Emits confirmed or cancelled and frees
## itself. Used for quitting, deleting saves and abandoning campaigns.
## ART-0 F (ported from art-pass W8a, ART_BIBLE v1 §10 / v2 SCRIM): it is a modal: a
## GlassScrim backdrop behind it takes the clicks meant for the page, it opens and closes
## with PageTransition's modal motion (`open_modal` / `close_modal`), and a page change
## waits for it to close (`PageTransition.after_modals`).
## ART-2 2D: restyled on F's behaviour (the scrim, the modal motion, the focus trap and the
## safe answer's default focus are F's, unchanged).

signal confirmed
signal cancelled

var yes_button: Button
var no_button: Button
## The terminal panel (the glass that drops in).
var panel: HudDialogPanel
var _box: VBoxContainer
var _room: MarginContainer

## The dialog's width and the question's width at text scale 1.0 (px).
const DIALOG_W := 560.0
const QUESTION_FONT := 22
const STICKER_FONT := 40
## The widest the dialog grows with the text, and the question's inset from its width (px).
const MAX_SCALE := 1.4
const TEXT_INSET := 60.0
const BUTTON_GAP := 48
## A-077: the dialog's words sit in from the frame by the title line's inset (`HudDialogPanel.PAD` x 0.5, px at text 1.0).
const TEXT_PAD := HudDialogPanel.PAD * 0.5
## A-077: room kept each side of the sticker row for a focused sticker's grow, tilt and lime halo (px at text 1.0),
## so the focused stickers stay inside the dialog's inner frame.
const FOCUS_ROOM := 14.0
## A-077: room kept between a sticker and its caption for a focused sticker's grow, tilt and halo (px at text 1.0).
const CAPTION_ROOM := VinylSticker.FOCUS_HALO_PX + 8.0
## Layout frames waited before the sticker room is measured (each re-measures), and the slack past the halo (px).
const FIT_PASSES := 3
const FIT_SLACK := 2.0


## `question` comes translated (H24 S4: the dialog shows its words as given); the answers,
## the title and the captions are keys, translated here. `body` (translated) goes under the
## question; `destructive` marks the panel CANNOT UNDO in HARM.
func _init(question: String, yes_text: String = "YES", no_text: String = "CANCEL", title: String = "ARE YOU SURE?", # TR
		body: String = "", destructive: bool = false, yes_note: String = "", no_note: String = "") -> void:
	var s := Settings.text_scale
	custom_minimum_size = Vector2(DIALOG_W * minf(s, MAX_SCALE), 0)

	TextDb.shown_as_given(self)
	panel = HudDialogPanel.new(tr(title), destructive)
	add_child(panel)
	panel.custom_minimum_size.x = custom_minimum_size.x  # W0 SCREENSFIX: the panel is as wide as the dialog, so centering the dialog centers the panel
	panel.resized.connect(func() -> void: size = panel.size)  # the dialog is as big as its panel
	var inset := MarginContainer.new()
	inset.name = "TextInset"
	inset.add_theme_constant_override("margin_left", roundi(TEXT_PAD * s))
	inset.add_theme_constant_override("margin_right", roundi(TEXT_PAD * s))
	panel.body.add_child(inset)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	inset.add_child(box)
	_box = box
	var l := Label.new()
	l.name = "Question"
	l.text = question
	UiWrap.whole_words(l)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	l.custom_minimum_size = Vector2(DIALOG_W * minf(s, MAX_SCALE) - TEXT_INSET - TEXT_PAD * 2.0 * s, 0)
	l.add_theme_font_override("font", HudSkin.body())
	l.add_theme_font_size_override("font_size", roundi(QUESTION_FONT * s))
	l.add_theme_color_override("font_color", HudSkin.TERMINAL_HI)
	box.add_child(l)
	if body != "":
		var b := Label.new()
		b.name = "Body"
		b.text = body
		UiWrap.whole_words(b)
		b.custom_minimum_size = l.custom_minimum_size
		b.add_theme_font_override("font", HudSkin.body())  # W0 SCREENSFIX: one text style for both lines
		b.add_theme_font_size_override("font_size", roundi(QUESTION_FONT * s))
		b.add_theme_color_override("font_color", HudSkin.TERMINAL_TEXT)
		box.add_child(b)
	var rule := ColorRect.new()
	rule.color = Color(PaletteSkins.chrome(HudSkin.TERMINAL_EDGE), 0.35)
	rule.custom_minimum_size = Vector2(0, 1)
	box.add_child(rule)
	var room := MarginContainer.new()
	room.name = "StickerRoom"
	_room = room
	var room_px := roundi((VinylSticker.FOCUS_HALO_PX + FOCUS_ROOM) * s)
	room.add_theme_constant_override("margin_left", room_px)
	room.add_theme_constant_override("margin_right", room_px)
	box.add_child(room)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", BUTTON_GAP)
	room.add_child(row)
	no_button = _sticker(row, no_text, no_note, HudSkin.VINYL_YELLOW)
	no_button.name = "No"
	no_button.pressed.connect(func() -> void: cancelled.emit(); _close())
	yes_button = _sticker(row, yes_text, yes_note, HudSkin.VINYL_PINK)
	yes_button.name = "Yes"
	yes_button.pressed.connect(func() -> void: confirmed.emit(); _close())
	# W0 SCREENSFIX: the stickers keep room under them (their fold and tilt) from the panel's bottom edge.
	var pad := Control.new()
	pad.name = "StickerPad"
	pad.custom_minimum_size = Vector2(0, roundi(UiTheme.SP_M * s))
	pad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(pad)


## A vinyl sticker answer with its caption under it (no system word: the caption is the
## line under the sticker).
func _sticker(row: Container, word: String, note: String, paint: Color) -> Button:  # ART-10 4C: AbandonDialog overrides it
	var b := SendItSticker.new(word, "", paint, STICKER_FONT)
	b.system_word = ""
	b.fold_room = true  # 1B-STICKER F2: every verb sticker keeps its fold room
	b.system_line = note
	b.caption_room = CAPTION_ROOM * Settings.text_scale if note != "" else 0.0
	b.tilt = -2.0
	b.tooltip_text = tr(note) if note != "" else ""
	b._fit_size()
	row.add_child(b)
	return b


## W0 SCREENSFIX (art review G14): a row of two chips under the question, `to_name` going in and `from_name` struck
## (the one destroyed): [icon] NEW -> [icon] OLD. `icon_kind` is a StatIcon kind.
func add_swap_row(to_name: String, from_name: String, icon_kind: StringName) -> void:
	var s := Settings.text_scale
	var row := HBoxContainer.new()
	row.name = "SwapRow"
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", UiTheme.SP_M)
	row.add_child(_swap_chip(to_name, icon_kind, false))
	var arrow := Label.new()
	arrow.text = "→"
	arrow.add_theme_font_override("font", HudSkin.body())
	arrow.add_theme_font_size_override("font_size", roundi(QUESTION_FONT * s))
	arrow.add_theme_color_override("font_color", HudSkin.TERMINAL_HI)
	row.add_child(arrow)
	row.add_child(_swap_chip(from_name, icon_kind, true))
	_box.add_child(row)
	_box.move_child(row, 1)


func _swap_chip(chip_name: String, icon_kind: StringName, struck: bool) -> Control:
	var s := Settings.text_scale
	var chip := HBoxContainer.new()
	chip.name = "OldChip" if struck else "NewChip"
	chip.add_theme_constant_override("separation", UiTheme.SP_S)
	var side := roundi(QUESTION_FONT * s * 1.4)
	var mark := IconMark.new(icon_kind, Palette.HARM if struck else Palette.CELL_ACID)
	mark.custom_minimum_size = Vector2(side, side)
	chip.add_child(mark)
	var l := Label.new()
	l.text = chip_name
	l.add_theme_font_override("font", HudSkin.body())
	l.add_theme_font_size_override("font_size", roundi(QUESTION_FONT * s))
	l.add_theme_color_override("font_color", Palette.HARM if struck else HudSkin.TERMINAL_HI)
	chip.add_child(l)
	if struck:
		var line := ColorRect.new()
		line.name = "Strike"
		line.color = Palette.HARM
		line.mouse_filter = Control.MOUSE_FILTER_IGNORE
		line.set_anchors_preset(Control.PRESET_HCENTER_WIDE)
		line.anchor_top = 0.55
		line.anchor_bottom = 0.55
		line.offset_top = 0.0
		line.offset_bottom = 2.0
		l.add_child(line)
	return chip


## W0 SCREENSFIX (art review G14): the committing answer becomes a red-outlined terminal button (not a sticker as
## loud as the safe one); `word` is a key. Returns the button.
func use_destructive_yes(word: String) -> Button:
	var b := use_terminal_yes(word)
	for st in [&"normal", &"hover", &"pressed", &"hover_pressed"]:
		var fill := PaletteSkins.chrome(Palette.TERMINAL_BG_HOT if st == &"hover" else Palette.TERMINAL_BG)
		b.add_theme_stylebox_override(st, UiTheme.box(fill, Palette.HARM, 2, UiTheme.BUTTON_PAD_H, UiTheme.BUTTON_PAD_V))
	b.add_theme_color_override("font_color", Palette.HARM)
	b.add_theme_font_size_override("font_size", roundi(STICKER_FONT * 0.6 * Settings.text_scale))
	return b


## B5 (integration review section c: "Quit uses yellow KEEP GOING plus a cyan terminal 'save & quit', not two
## stickers of competing hue"): the committing answer becomes a terminal button in the Cell's cyan (`word`, a key,
## with its key hint) beside the safe sticker; the dialog's one sticker is the safe answer. Returns the button.
func use_terminal_yes(word: String, key_hint: String = "") -> Button:
	var old := yes_button
	var row := old.get_parent()
	var at := old.get_index()
	row.remove_child(old)
	old.queue_free()
	var b := Button.new()
	b.name = "Yes"
	b.text = ("%s  %s" % [tr(word), key_hint]).strip_edges()
	b.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	b.theme_type_variation = UiTheme.TERMINAL_BUTTON
	b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	b.tooltip_text = b.text
	b.pressed.connect(func() -> void: confirmed.emit(); _close())
	row.add_child(b)
	row.move_child(b, at)
	yes_button = b
	return b


## F7: the dialog is modal: mouse events outside its panel never reach the page behind (the scrim cannot take them
## itself, see `GlassScrim.backdrop_for`). Events over the panel go on to its buttons.
func _input(event: InputEvent) -> void:
	if event is InputEventMouse and is_inside_tree() and not panel.get_global_rect().has_point((event as InputEventMouse).global_position):
		get_viewport().set_input_as_handled()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		cancelled.emit()
		get_viewport().set_input_as_handled()
		_close()


## Closes the dialog: through PageTransition.close_modal (it fades out, then frees) unless it
## is already closing (a page change closed it first).
func _close() -> void:
	if bool(get_meta(PageTransition.META_MODAL_CLOSING, false)) or is_queued_for_deletion():
		return
	if is_in_group(PageTransition.MODAL_GROUP):
		PageTransition.close_modal(self)
	else:
		queue_free()


## Who had focus before the dialog opened; it gets focus back when the dialog closes.
var _return_focus: Control = null


func _enter_tree() -> void:
	StickerSweepQueue.calm_enter(self)  # no scheduled sweep on any sticker while a confirm is open (B1d)


func _exit_tree() -> void:
	StickerSweepQueue.calm_leave(self)


func _ready() -> void:
	_return_focus = UiFocus.owner_of(self)
	# ART-0 F: a modal over a SCRIM (the page behind blurred and dimmed; it takes the clicks
	# meant for the page), opened with the modal motion.
	var scrim := GlassScrim.backdrop_for(self, get_viewport_rect().size, Palette.SCRIM_DIALOG_ALPHA)
	move_child(scrim, 0)  # ART-2 2D: drawn before the panel, so the blur stays behind the dialog
	panel.z_index = 1  # (a top-level scrim can still draw late: the panel is drawn over it)
	PageTransition.open_modal(self)
	# The panel drops in (Animation pass ANIM-6); a press during the drop completes it.
	PageTransition.enter(panel, PageTransition.Look.GLASS)
	UiFocus.trap.call_deferred(self)  # Yes <-> No, and never out to the screen behind
	# Pad / keyboard: the safe answer takes focus.
	if no_button != null:
		no_button.grab_focus.call_deferred()
	# A-077: the focused (grown, tilted, haloed) stickers stay inside the inner frame: measured once the layout is in.
	for i in FIT_PASSES:
		await get_tree().process_frame
		if not is_inside_tree():
			return
		_fit_room()


## A-077: widens the sticker row's side room by however far a focused sticker (its die-cut grown to the hover
## amplitude, tilted, plus the lime halo) would reach past the panel body's frame, on the side it reaches furthest
## (the row is centred, so both sides take it). Every two-sticker dialog goes through here.
func _fit_room() -> void:
	if _room == null or panel == null:
		return
	var frame := panel.body.get_global_rect()
	var amp := Motion.amplitude(VinylSticker.HOVER)
	var lo := INF
	var hi := -INF
	for b in [no_button, yes_button]:
		var sticker := b as SendItSticker
		if sticker == null or sticker.art == null or sticker.art.body_rect.size.x <= 0.0:
			continue
		var t := sticker.art.get_global_transform()
		var r := sticker.art.body_rect
		var grow := r.size * maxf(amp - sticker.art.scale.x, 0.0) * 0.5 + Vector2.ONE * (VinylSticker.FOCUS_HALO_PX + FIT_SLACK)
		for c in [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y)]:
			var g: Vector2 = t * c
			lo = minf(lo, g.x - grow.x)
			hi = maxf(hi, g.x + grow.x)
	var excess := maxf(maxf(frame.position.x - lo, hi - frame.end.x), 0.0)
	if excess < 0.5:
		return
	var more := ceili(excess)
	_room.add_theme_constant_override("margin_left", _room.get_theme_constant("margin_left") + more)
	_room.add_theme_constant_override("margin_right", _room.get_theme_constant("margin_right") + more)


func _notification(what: int) -> void:
	if what == NOTIFICATION_EXIT_TREE and _return_focus != null and is_instance_valid(_return_focus) 			and _return_focus.is_inside_tree() and not _return_focus.is_queued_for_deletion():
		_return_focus.grab_focus.call_deferred()
