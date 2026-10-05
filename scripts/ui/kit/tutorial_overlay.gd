class_name TutorialOverlay
extends Control
## Guided first fight (gap analysis 2.5 onboarding): zine notes that explain the wheel,
## precision, nudges and resistance, cards and the preview, rewind (UNDO) and where it stops, End
## Turn and the resolution order, then Heat and banking. Steps advance on the matching
## combat events (or Next); Skip ends it. Marks Settings.tutorial_done when finished.

signal finished
## ANIM-R6 A16: a new step shows (its box is sized to its text).
signal step_changed

## Height kept for the Next / Skip row under the note.
const BUTTON_ROW_HEIGHT := 40.0

## ANIM-R5 combat 9: the steps' titles and texts are translation keys (`# TR`: exported,
## translated where they are shown; the tutorial stayed English under pseudolocalisation).
const STEPS: Array[Dictionary] = [
	{
		"title":
			"THE WHEEL",  # TR
		"text":
			"Each white needle reads the slice under it: that slice is what the wheel does when you SEND IT. The tag above each wheel shows it (the dots: how well the needle sits) and its chips show every result: HITS, BLOCK, statuses, RAM, HEAT. The dashed NEXT plate by the HP is the forecast; the grey LAST TURN line under it is what the last SEND IT did. {inspect_how} anything to read it.",  # TR
		"until": "",
	},
	{
		"title":
			"NUDGE",  # TR
		"text":
			"Land dead centre for PERFECT (full output plus your class hook), 1 tick off for GOOD AIM, 2 off for HALF POWER. The curved arrows over a wheel turn it one tick: the right one clockwise, the left one back. {nudge_how}",  # TR
		"until": "nudge",
	},
	{
		"title":
			"RESISTANCE",  # TR
		"text":
			"Enemy wheels resist: each point absorbs one tick of your manipulation before it moves. Flip and Respin are blocked while resistance is up. Strip it, breach the Hub, or spin past it.",  # TR
		"until": "",
	},
	{
		"title":
			"CARDS",  # TR
		"text":
			"Cards spin, nudge and flip wheels; they cost RAM. {card_how} Nudge cards go on an arrow (that sets the way they turn), slice cards on a slice. While you aim, the tags and the dashed acid arc show the result before you commit.",  # TR
		"until": "card",
	},
	{
		"title":
			"UNDO",  # TR
		"text":
			"{undo_how} undoes anything back to the last random event (the start-of-turn respin). Undo is free and unlimited within a turn; UNDO stops at a Respin or a random slice pick.",  # TR
		"until": "rewind",
	},
	{
		"title":
			"SEND IT",  # TR
		"text":
			"SEND IT {end_turn} resolves every needle at once: defensive slices, then offensive, then statuses. The tags already show the outcome.",  # TR
		"until": "turn_start",
	},
	{
		"title":
			"HEAT & BANKING",  # TR
		"text":
			"Every Rack you capture banks Schematics for the Cell and adds Heat. Heat thresholds bring raids on your home server. Bank early, cool off at Heat objectives, and never leave loot unbanked when you jack out.",  # TR
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
	note = ZineNote.new(tr("TUTORIAL"), Vector2(p_size.x, p_size.y - BUTTON_ROW_HEIGHT)).make_reference()
	add_child(note)
	row = HBoxContainer.new()
	row.position = Vector2(10, p_size.y - BUTTON_ROW_HEIGHT + 2)
	add_child(row)
	next_button = Button.new()
	next_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED  # its words translate in _show (once)
	next_button.text = tr("Next")
	next_button.pressed.connect(advance)
	row.add_child(next_button)
	skip_button = Button.new()
	skip_button.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	skip_button.text = tr("Skip tutorial")
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
	return {"font": font, "fs": fs, "line_h": line_h, "w": w, "lines": maxi(1, floori(h / line_h) - 1)}


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
	var n := wrap_words(step_text(step), r["font"], int(r["fs"]), float(r["w"])).size() + 1
	return n * float(r["line_h"]) + note.label.offset_top - note.label.offset_bottom + BUTTON_ROW_HEIGHT + TEXT_SLACK


## ANIM-R6 A16: the current step's pages at this size (one when its text fits).
func pages() -> PackedStringArray:
	var r := _room(size)
	var lines := wrap_words(step_text(step), r["font"], int(r["fs"]), float(r["w"]))
	var per := int(r["lines"])
	var out := PackedStringArray()
	var i := 0
	while i < lines.size():
		out.append(" ".join(lines.slice(i, i + per)))
		i += per
	if out.is_empty():
		out.append("")
	return out


## Room kept beside the text for the label's scroll bar and rounding (px).
const TEXT_SLACK := 6.0
## The page of the current step on show.
var page: int = 0
var _pulse: Tween = null


func _show() -> void:
	note.clear()
	var s: Dictionary = STEPS[step]
	var all := pages()
	page = clampi(page, 0, all.size() - 1)
	var head := "[b]%d/%d %s[/b]" % [step + 1, STEPS.size(), tr(String(s["title"]))]
	if all.size() > 1:
		head += " (%d/%d)" % [page + 1, all.size()]
	note.append(head)
	note.append(all[page])
	note.label.scroll_to_line.call_deferred(0)  # the step title first, at any text scale
	var last := step == STEPS.size() - 1 and page == all.size() - 1
	next_button.text = tr("Finish") if last else tr("Next")
	# ANIM-R6 A16: Next pulses when it is what moves the tutorial on (a step no play of the
	# fight ends, or a page to turn), so the box never sits unread on one step.
	var waits := String(s["until"]) == "" or page < all.size() - 1
	if waits and (_pulse == null or not _pulse.is_valid()):
		_pulse = Motion.loop_pulse(next_button, ^"modulate:a", &"tutorial_next_pulse")
	elif not waits:
		Motion.stop(next_button)
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
	keys.nudge_how = (t.call("%s and %s nudge the wheel the arrows mark; %s switches between yours and the target, %s between the outer and inner ring.") % [Settings.key_text(&"nudge_left"), Settings.key_text(&"nudge_right"), Settings.key_text(&"toggle_nudge_wheel"), Settings.key_text(&"toggle_ring")]) if Settings.key_text(&"nudge_left") != "" else ""  # TR
	keys.card_how = (t.call("Pick a card with %s, choose a glowing target with the D-pad, press %s again (%s cancels).") % [Settings.key_text(&"ui_accept"), Settings.key_text(&"ui_accept"), Settings.key_text(&"ui_cancel")]) if pad else t.call("Drag a card onto a glowing target (or click it, then click the target; right-click cancels). The number keys pick cards.")  # TR
	keys.undo_how = t.call("UNDO %s") % Settings.hint(&"rewind")  # TR
	# ANIM-R5 combat 9: the step translated, its keys filled in, then pseudolocalised once (so the
	# {placeholders} survive a scrambled build).
	var text := message(String(STEPS[i]["text"])).format(keys)
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
