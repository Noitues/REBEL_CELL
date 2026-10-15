class_name TutorialOverlay
extends Control
## Guided first fight (gap analysis 2.5 onboarding): terminal notes (ART-2 2D: TerminalNote,
## TerminalButton Next / Skip, the words name the HUD v4 parts) that explain the wheel,
## precision, nudges and resistance, cards and the preview, rewind (UNDO) and where it stops, End
## Turn and the resolution order, then Heat and banking. Steps advance on the matching
## combat events (or Next); Skip ends it. Marks Settings.tutorial_done when finished.

signal finished
## ANIM-R6 A16: a new step shows (its box is sized to its text).
signal step_changed

## Height kept for the Next / Skip row under the note.
const BUTTON_ROW_HEIGHT := 40.0

## B-TEACH: the event the scene sends when your wheel reads PERFECT after your play (the AIM beat ends on it).
const AIM_PERFECT := "aim_perfect"

## ANIM-R5 combat 9: the steps' titles and texts are translation keys (`# TR`: exported,
## translated where they are shown; the tutorial stayed English under pseudolocalisation).
const STEPS: Array[Dictionary] = [
	{
		"title":
			"THE WHEEL",  # TR
		"text":
			"The white needle points at a slice. That slice is what the wheel does when you SEND IT. The chips beside each HP show this turn's result if you SEND IT now. {inspect_how} anything to read it.",  # TR
		"until": "",
	},
	{
		"title":
			"THE TAGS",  # TR
		"text":
			"The tag by the needle rates your aim. PERFECT: full power plus your class hook. GOOD: full power. WEAK: half power. NULL: the NULL slice does nothing.",  # TR
		"until": "",
	},
	{
		"title":
			"AIM",  # TR
		"text":
			"Aim for PERFECT. The round buttons above a wheel turn it one tick. {nudge_keys} Nudge until the tag says PERFECT.",  # TR
		"until": AIM_PERFECT,
	},
	{
		"title":
			"FREE NUDGE",  # TR
		"text":
			"FREE NUDGE in the title bar counts the nudges you still get free this turn. After that each nudge costs RAM, and the (-N) next to RAM shows what it will spend. Nudge once more to see it.",  # TR
		"until": "nudge",
	},
	{
		"title":
			"SWITCHES",  # TR
		"text":
			"{nudge_switch}",  # TR
		"until": "",
	},
	{
		"title":
			"RESISTANCE",  # TR
		"text":
			"Enemy wheels resist: each point absorbs one tick of your nudges. Flip and Respin are blocked while it is up. Strip it, breach the Hub, or spin past it.",  # TR
		"until": "",
	},
	{
		"title":
			"CARDS",  # TR
		"text":
			"Cards spin, nudge and flip wheels, and cost RAM. {card_how} The dashed arc shows where a card lands before you commit.",  # TR
		"until": "card",
	},
	{
		"title":
			"STAGED",  # TR
		"text":
			"A card you play is staged: it waits in THIS TURN until you SEND IT. Hovering or raising a card only previews it.",  # TR
		"until": "",
	},
	{
		"title":
			"RAM FORECAST",  # TR
		"text":
			"The (-N) next to RAM is what will be spent. THIS PLAY is what the card under your pointer costs. AT SEND IT is what SEND IT itself changes, with nothing played.",  # TR
		"until": "",
	},
	{
		"title":
			"UNDO",  # TR
		"text":
			"{undo_how} or Esc takes back your last staged play or nudge. It stops at the last random event, like a Respin. Nudge your wheel, then undo it.",  # TR
		"until": "rewind",
	},
	{
		"title":
			"SEND IT",  # TR
		"text":
			"Aim for PERFECT, then SEND IT {end_turn}. Every needle resolves at once: defense, then offense, then statuses.",  # TR
		"until": "turn_start",
	},
	{
		"title":
			"HEAT & BANKING",  # TR
		"text":
			"Every Rack you capture banks Schematics for the Cell and adds Heat. Heat brings raids on your home server. Bank early, and never leave loot unbanked when you jack out.",  # TR
		"until": "",
	},
]

var step: int = 0
var note: ZineNote
var next_button: Button
var skip_button: Button
var row: HBoxContainer


func _init(p_size: Vector2 = Vector2(380, 190)) -> void:
	custom_minimum_size = p_size
	size = p_size
	note = TerminalNote.new(tr("TUTORIAL"), Vector2(p_size.x, p_size.y - BUTTON_ROW_HEIGHT)).make_reference()
	add_child(note)
	row = HBoxContainer.new()
	row.position = Vector2(10, p_size.y - BUTTON_ROW_HEIGHT + 2)
	add_child(row)
	next_button = Button.new()
	next_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # its words translate in _show (once)
	next_button.text = tr("Next")
	next_button.theme_type_variation = UiTheme.TERMINAL_BUTTON
	next_button.pressed.connect(advance)
	# B-TEACH (PT-002 C9: NEXT looked greyed out): it wears the lit terminal color; Skip stays quiet.
	for state_color in [&"font_color", &"font_hover_color", &"font_pressed_color", &"font_focus_color"]:
		next_button.add_theme_color_override(state_color, HudSkin.TERMINAL_HI)
	row.add_child(next_button)
	skip_button = Button.new()
	skip_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	skip_button.text = tr("Skip tutorial")
	skip_button.theme_type_variation = UiTheme.TERMINAL_BUTTON
	skip_button.pressed.connect(skip)
	row.add_child(skip_button)
	_show()
	# A rebind or a switch between keyboard and pad rewrites the step at once (H20).
	Settings.hints_changed.connect(_show)


## Resizes the overlay (note above, Next / Skip row under it). ANIM-R6 A16: a step whose text
## is longer than the note shows it in pages that fit (Next turns the page), never cut.
func fit(p_size: Vector2) -> void:
	custom_minimum_size = p_size
	size = p_size
	note.custom_minimum_size = Vector2(p_size.x, p_size.y - BUTTON_ROW_HEIGHT)
	note.size = note.custom_minimum_size
	row.position = Vector2(10, p_size.y - BUTTON_ROW_HEIGHT + 2)
	_show()


## ANIM-R6 A16: the note's text room: its label's width and height, the lettering's line
## height, and the lines a page holds under the title.
func _room(p_size: Vector2) -> Dictionary:
	var fs := note.label.get_theme_font_size(&"normal_font_size")
	var font := note.label.get_theme_font(&"normal_font")
	var line_h := font.get_height(fs) + note.label.get_theme_constant(&"line_separation")
	var w := p_size.x - note.label.offset_left + note.label.offset_right - TEXT_SLACK
	var h := p_size.y - BUTTON_ROW_HEIGHT - note.label.offset_top + note.label.offset_bottom
	# ART-2 2D (audit P2: a page was cut mid-sentence): room for the title and the line that
	# says how to go on, and a line of margin (the label's own wrap can take one more line).
	# M14 12Q-MENUS: compact (big text in a short box), the line under the page goes to NEXT's tooltip.
	return {"font": font, "fs": fs, "line_h": line_h, "w": w, "lines": maxi(1, floori(h / line_h) - 1 - (0 if _compact else REASON_LINES))}


## ANIM-R6 A16: `text` wrapped at word breaks to `width` px in `font` at `fs`.
static func wrap_words(text: String, font: Font, fs: int, width: float) -> PackedStringArray:
	var lines := PackedStringArray()
	var line := ""
	for word in text.split(" ", false):
		var trial := word if line == "" else line + " " + word
		if line != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > width:
			lines.append(line)
			line = word
		else:
			line = trial
	if line != "":
		lines.append(line)
	return lines


## ANIM-R6 A16: the height the overlay needs at `width` px to show the current step whole
## (its title, its text, the Next / Skip row): the scene sizes the box to it.
func needed_height(width: float) -> float:
	var r := _room(Vector2(width, BUTTON_ROW_HEIGHT))
	var n := wrap_words(step_text(step), r["font"], int(r["fs"]), float(r["w"])).size() + 1 + REASON_LINES
	return n * float(r["line_h"]) + note.label.offset_top - note.label.offset_bottom + BUTTON_ROW_HEIGHT + TEXT_SLACK


## ANIM-R6 A16: the current step's pages at this size (one when its text fits).
func pages() -> PackedStringArray:
	var r := _room(size)
	var lines := wrap_words(step_text(step), r["font"], int(r["fs"]), float(r["w"]))
	var per := maxi(1, int(r["lines"]) - _cut)
	var out := PackedStringArray()
	var i := 0
	while i < lines.size():
		out.append(" ".join(lines.slice(i, i + per)))
		i += per
	if out.is_empty():
		out.append("")
	return out


## Room kept beside the text for the label's scroll bar and rounding (px).
const TEXT_SLACK := 18.0
## ART-2 2D: lines kept under the page for what moves the tutorial on (and a margin).
const REASON_LINES := 2
## The page of the current step on show.
var page: int = 0
var _pulse: Tween = null
## M14 12Q-MENUS (QA matrix P2: "11 of 12 lines visible" at 1.0, at 2.0 the page ended "More on the next"): lines
## taken off the measured page size after the note's own label said the page ran past its room (the title or
## the line under the page wrapped to more lines than the estimate kept).
var _cut: int = 0
## M14 12Q-MENUS: the most lines a page is shortened by (the estimate is never further off).
const CUT_MAX := 6
## M14 12Q-MENUS (2.0 in the fight's short notes box: the title, one line of text and the line under it did not
## fit): compact pages: the title on one line without the page count, no line under the page (NEXT pulses and
## its tooltip says what moves the tutorial on), the room to the text.
var _compact: bool = false


func _show() -> void:
	_cut = 0
	_compact = false
	# M14 12Q-MENUS: every line of every page shows: the step's pages are shortened until the label's own wrap
	# fits each of them, then they go compact (one paging for the whole step, so its page count holds).
	var shown := page
	while not _all_pages_fit():
		if _cut < CUT_MAX and int(_room(size)["lines"]) - _cut > 1:
			_cut += 1
		elif not _compact:
			_compact = true
			_cut = 0
		else:
			break
	page = shown
	_render()


## M14 12Q-MENUS: whether every page of the step, as paged now, fits the note (each is rendered to measure).
func _all_pages_fit() -> bool:
	for p in pages().size():
		page = p
		_render()
		if not page_fits():
			return false
	return true


## M14 12Q-MENUS: true while the pages are compact (tests).
func compact() -> bool:
	return _compact


## M14 12Q-MENUS: whether the note's label shows the whole page (title, text and the line under it) unscrolled.
func page_fits() -> bool:
	var l := note.label
	return l.size.y <= 0.0 or float(l.get_content_height()) <= l.size.y + 1.0


func _render() -> void:
	note.clear()
	var s: Dictionary = STEPS[step]
	var all := pages()
	page = clampi(page, 0, all.size() - 1)
	var head := "[b]%d/%d %s[/b]" % [step + 1, STEPS.size(), tr(String(s["title"]))]
	if all.size() > 1 and not _compact:
		head += " (%d/%d)" % [page + 1, all.size()]
	# ART-2 2D (audit P2: "Next" read as greyed with no reason): what moves it on, in words.
	var more := page < all.size() - 1
	var is_last := step == STEPS.size() - 1 and not more
	var reason := tr("More on the next page: press NEXT.") if more else (tr("Press NEXT to go on.") if String(s["until"]) == "" else tr("Do it in the fight to go on (or press NEXT)."))
	if is_last:  # C-2: the button says FINISH on the last page, so the line says FINISH
		reason = tr("Press FINISH to close the tutorial.") if String(s["until"]) == "" else tr("Do it in the fight to finish (or press FINISH).")
	next_button.tooltip_text = UiTip.fold(reason)
	note.append(head)
	if _compact:
		note.label.append_text(all[page])  # M14 12Q-MENUS: the last line has no line break after it
	else:
		note.append(all[page])
		# M14 12Q-MENUS: the last line has no line break after it (an empty line under the page).
		note.label.append_text("[color=#%s]%s[/color]" % [HudSkin.TERMINAL_HI.to_html(false), reason])
	note.label.scroll_to_line.call_deferred(0)  # the step title first, at any text scale
	var last := step == STEPS.size() - 1 and page == all.size() - 1
	next_button.text = tr("Finish") if last else tr("Next")
	# ANIM-R6 A16: Next pulses when it is what moves the tutorial on (a step no play of the
	# fight ends, or a page to turn), so the box never sits unread on one step.
	# M14 12Q-ACCESS (L81): not under high contrast: the pulse dips Next's alpha, and its words
	# under 7:1 (4.42:1 caught mid-pulse); Next stays whole, its tip says what moves it on.
	var waits := (String(s["until"]) == "" or page < all.size() - 1) and not HighContrast.on()
	if waits and (_pulse == null or not _pulse.is_valid()):
		_pulse = Motion.loop_pulse(next_button, ^"modulate:a", &"tutorial_next_pulse")
	elif not waits:
		Motion.stop(next_button)
		next_button.modulate.a = 1.0
		_pulse = null


## True while Next pulses (tests).
func next_pulsing() -> bool:
	return _pulse != null and _pulse.is_valid()


## Step `i`'s text with the current binds filled in (pad buttons when a pad is in use).
static func step_text(i: int) -> String:
	var keys := {}
	for action in [&"nudge_left", &"nudge_right", &"rewind", &"end_turn", &"inspect"]:
		keys[String(action)] = Settings.hint(action)
	var pad := Settings.pad_active
	var t := func(k: String) -> String: return message(k)
	keys.inspect_how = t.call("Press %s on") % Settings.key_text(&"inspect") if pad else t.call("Hover or right-click")  # TR
	var has_keys := Settings.key_text(&"nudge_left") != ""
	keys.nudge_keys = (t.call("%s turns it back, %s forward.") % [Settings.key_text(&"nudge_left"), Settings.key_text(&"nudge_right")]) if has_keys else ""  # TR
	keys.nudge_switch = (t.call("%s switches between your wheel and the target. %s switches between the outer and inner ring. The lit rim and the word OUTER or INNER show what a nudge turns.") % [Settings.key_text(&"toggle_nudge_wheel"), Settings.key_text(&"toggle_ring")]) if has_keys else t.call("The wheel with the lit rim is the one a nudge turns.")  # TR
	keys.card_how = (t.call("Pick a card with %s, choose a glowing target with the D-pad, press %s again (%s cancels).") % [Settings.key_text(&"ui_accept"), Settings.key_text(&"ui_accept"), Settings.key_text(&"ui_cancel")]) if pad else t.call("Drag a card onto a glowing target (or click it, then click the target; right-click cancels). The number keys pick cards.")  # TR
	keys.undo_how = t.call("UNDO %s") % Settings.hint(&"rewind")  # TR
	# ANIM-R5 combat 9: the step translated, its keys filled in, then pseudolocalised once (so the
	# {placeholders} survive a scrambled build).
	var text := message(String(STEPS[i]["text"])).format(keys).replace("  ", " ")  # an empty {nudge_keys} leaves no gap
	return String(TranslationServer.pseudolocalize(text)) if TranslationServer.pseudolocalization_enabled else text


## `key` in the player's language from the loaded catalogues, else `key` itself (never
## pseudolocalised here: step_text does that once, after filling the placeholders).
static func message(key: String) -> String:
	for locale in [TranslationServer.get_locale(), String(ProjectSettings.get_setting("internationalization/locale/fallback", "en"))]:
		var cat := TranslationServer.get_translation_object(locale)
		if cat != null and String(cat.get_message(key)) != "":
			return String(cat.get_message(key))
	return key


func current_title() -> String:
	return String(STEPS[step]["title"])


func advance() -> void:
	# ANIM-R6 A16: a longer step's next page first.
	if page < pages().size() - 1:
		page += 1
		_show()
		return
	_next_step()


func skip() -> void:
	_finish()


## Combat events from the engine: the current step advances when its trigger appears.
## ANIM-R6 A16: a step no play ends (the wheel, resistance, Heat) moves on with the turn (a
## new turn's start), so it never stays up turn after turn.
func on_events(events: Array[Dictionary]) -> void:
	var until := String(STEPS[step]["until"])
	if until == "":
		until = "turn_start"
	for e in events:
		if String(e.get("type", "")) == until:
			_next_step()
			return


## The next step (its first page), or the end.
func _next_step() -> void:
	if step >= STEPS.size() - 1:
		_finish()
		return
	step += 1
	page = 0
	Motion.stop(next_button)
	_pulse = null
	_show()
	step_changed.emit()


func _finish() -> void:
	Settings.set_tutorial_done(true)
	finished.emit()
	queue_free()
