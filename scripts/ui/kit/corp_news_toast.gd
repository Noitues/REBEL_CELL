class_name CorpNewsToast
extends PanelContainer
## B4 (M14 integration review D7; ART_BIBLE v2 §4.13 "Toasts: ... corp news = holo strip; 2.4 s
## at the foot"; round 44 `hq_idle.png`): the HQ's corporate news, intercepted, as one holo
## strip at the page's foot (the corp's tint, DecryptedHoloPanel's scanlines and bands, the
## words in the holo's ink) instead of a standing band under the top bar. It shows for the
## `toast` motion entry's hold (2.4 s) then fades over its duration, or longer while a long line
## needs its reading time (Dialogue's own rate: a line is never cut before it can be read). A
## new line replaces the one showing. Headless it stays up (tests read it); under reduce effects
## it goes without the fade. Ignores the mouse and focus. View only.

## The toast's hold and fade (the shared toast entry: delay 2.4 s, duration the fade).
const MOTION := &"toast"
## Reading time per character (s): Dialogue's rate.
const SECONDS_PER_CHAR := 0.045
## Room round the words (px at text scale 1.0).
const PAD := Vector2(14, 7)
const NODE_NAME := "CorpNews"
## The most lines the words take.
const LINES := 2

var holo: DecryptedHoloPanel
var label: Label
var _tween: Tween = null


func _init(corporation: StringName = &"halcyon") -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	visible = false
	var skin := RaidSkin.of(corporation)
	var box := StyleBoxEmpty.new()
	box.content_margin_left = PAD.x * Settings.text_scale
	box.content_margin_right = PAD.x * Settings.text_scale
	box.content_margin_top = PAD.y * Settings.text_scale
	box.content_margin_bottom = PAD.y * Settings.text_scale
	add_theme_stylebox_override("panel", box)
	holo = DecryptedHoloPanel.new()
	holo.name = "Holo"
	holo.scrim = false
	holo.corp_color = skin.hue
	holo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(holo, false, Node.INTERNAL_MODE_FRONT)
	label = Label.new()
	label.name = "Words"
	label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # given translated
	label.add_theme_font_override("font", Palette.mono())
	label.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	label.add_theme_color_override("font_color", DecryptedHoloPanel.ink(skin.holo))
	# Whole words over at most LINES lines (a long line keeps its reading time, never cut
	# mid-word; the whole of it is in the tooltip).
	UiWrap.whole_words(label)
	label.max_lines_visible = LINES
	label.text_overrun_behavior = TextServer.OVERRUN_TRIM_WORD_ELLIPSIS
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)


func _ready() -> void:
	# A strip, not a file: no DECRYPTED stamp on it.
	if holo.stamp_slot != null:
		holo.stamp_slot.visible = false


## Lays the strip out `width` px wide (its words wrap inside).
func set_width(width: float) -> void:
	var box := get_theme_stylebox(&"panel")
	label.custom_minimum_size.x = maxf(1.0, width - box.get_margin(SIDE_LEFT) - box.get_margin(SIDE_RIGHT))
	size = Vector2(width, get_combined_minimum_size().y)


func _notification(what: int) -> void:
	if (what == NOTIFICATION_RESIZED or what == NOTIFICATION_SORT_CHILDREN) and holo != null:
		holo.position = Vector2.ZERO
		holo.size = size


## How long `text` stays up before its fade (s): the entry's hold, or its reading time.
static func hold_for(text: String) -> float:
	return maxf(Motion.delay_of(MOTION), text.length() * SECONDS_PER_CHAR)


## Shows `text` (translated); it goes after its hold.
func show_news(text: String) -> void:
	label.text = text
	tooltip_text = text
	modulate.a = 1.0
	visible = true
	if _tween != null and _tween.is_valid():
		_tween.kill()
	if DisplayServer.get_name() == "headless":
		return  # stays up for tests to read; the next line replaces it
	_tween = create_tween()
	_tween.tween_interval(hold_for(text))
	if Fx.effects_enabled():
		var e := Motion.entry(MOTION)
		_tween.tween_property(self, "modulate:a", 0.0, Motion.seconds(MOTION)).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_callback(hide)


## The words on show ("" when hidden).
func text() -> String:
	return label.text if visible else ""
