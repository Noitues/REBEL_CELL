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

## The dialog's width and the question's width at text scale 1.0 (px).
const DIALOG_W := 560.0
const QUESTION_FONT := 22
const STICKER_FONT := 40
## The widest the dialog grows with the text, and the question's inset from its width (px).
const MAX_SCALE := 1.4
const TEXT_INSET := 60.0
const BUTTON_GAP := 48


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
	panel.resized.connect(func() -> void: size = panel.size)  # the dialog is as big as its panel
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	panel.body.add_child(box)
	var l := Label.new()
	l.name = "Question"
	l.text = question
	UiWrap.whole_words(l)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
	l.custom_minimum_size = Vector2(DIALOG_W * minf(s, MAX_SCALE) - TEXT_INSET, 0)
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
		b.add_theme_color_override("font_color", HudSkin.TERMINAL_TEXT)
		box.add_child(b)
	var rule := ColorRect.new()
	rule.color = Color(PaletteSkins.chrome(HudSkin.TERMINAL_EDGE), 0.35)
	rule.custom_minimum_size = Vector2(0, 1)
	box.add_child(rule)
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", BUTTON_GAP)
	box.add_child(row)
	no_button = _sticker(row, no_text, no_note, HudSkin.VINYL_YELLOW)
	no_button.name = "No"
	no_button.pressed.connect(func() -> void: cancelled.emit(); _close())
	yes_button = _sticker(row, yes_text, yes_note, HudSkin.VINYL_PINK)
	yes_button.name = "Yes"
	yes_button.pressed.connect(func() -> void: confirmed.emit(); _close())


## A vinyl sticker answer with its caption under it (no system word: the caption is the
## line under the sticker).
func _sticker(row: Container, word: String, note: String, paint: Color) -> Button:  # ART-10 4C: AbandonDialog overrides it
	var b := SendItSticker.new(word, "", paint, STICKER_FONT)
	b.system_word = ""
	b.system_line = note
	b.tilt = -2.0
	b.tooltip_text = tr(note) if note != "" else ""
	b._fit_size()
	row.add_child(b)
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
	var scrim := GlassScrim.backdrop_for(self, get_viewport_rect().size)
	move_child(scrim, 0)  # ART-2 2D: drawn before the panel, so the blur stays behind the dialog
	panel.z_index = 1  # (a top-level scrim can still draw late: the panel is drawn over it)
	PageTransition.open_modal(self)
	# The panel drops in (Animation pass ANIM-6); a press during the drop completes it.
	PageTransition.enter(panel, PageTransition.Look.GLASS)
	UiFocus.trap.call_deferred(self)  # Yes <-> No, and never out to the screen behind
	# Pad / keyboard: the safe answer takes focus.
	if no_button != null:
		no_button.grab_focus.call_deferred()


func _notification(what: int) -> void:
	if what == NOTIFICATION_EXIT_TREE and _return_focus != null and is_instance_valid(_return_focus) 			and _return_focus.is_inside_tree() and not _return_focus.is_queued_for_deletion():
		_return_focus.grab_focus.call_deferred()
