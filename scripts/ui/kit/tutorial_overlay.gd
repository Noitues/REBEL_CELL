class_name TutorialOverlay
extends Control
## Guided first fight (gap analysis 2.5 onboarding): zine notes that explain the wheel,
## precision, nudges and resistance, cards and the preview, rewind and checkpoints, End
## Turn and the resolution order, then Heat and banking. Steps advance on the matching
## combat events (or Next); Skip ends it. Marks Settings.tutorial_done when finished.

signal finished

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
			"{undo_how} undoes anything back to the last random event (the start-of-turn respin). Undo is free and unlimited within a turn; a Respin or a random slice pick sets a new checkpoint.",  # TR
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
## Art pass W9F: a row, or a column when both buttons don't fit the width (2.0).
var row: BoxContainer


func _init(p_size: Vector2 = Vector2(380, 190)) -> void:
	custom_minimum_size = p_size
	size = p_size
	note = ZineNote.new(tr("TUTORIAL"), Vector2(p_size.x, p_size.y - BUTTON_ROW_HEIGHT)).make_reference()
	add_child(note)
	row = BoxContainer.new()
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


## Resizes the overlay (note above, Next / Skip row under it); the note scrolls when the
## step's text is longer than it.
func fit(p_size: Vector2) -> void:
	custom_minimum_size = p_size
	size = p_size
	# Art pass W9F (§12: nothing clips at 2.0): the buttons stack when side by side they'd run
	# past the column ("Skip tutorial" ran off the screen), and their row takes its real height.
	var sep := float(row.get_theme_constant(&"separation"))
	var both := next_button.get_combined_minimum_size().x + sep + skip_button.get_combined_minimum_size().x
	row.vertical = both > p_size.x - ROW_INSET * 2.0
	row.reset_size()
	var row_h := maxf(BUTTON_ROW_HEIGHT, row.get_combined_minimum_size().y + ROW_INSET)
	note.custom_minimum_size = Vector2(p_size.x, maxf(0.0, p_size.y - row_h))
	note.size = note.custom_minimum_size
	row.position = Vector2(ROW_INSET, p_size.y - row_h + 2)


## The button row's inset from the note's edges (px).
const ROW_INSET := 10.0


func _show() -> void:
	note.clear()
	var s: Dictionary = STEPS[step]
	note.append("[b]%d/%d %s[/b]" % [step + 1, STEPS.size(), tr(String(s["title"]))])
	note.append(step_text(step))
	note.label.scroll_to_line.call_deferred(0)  # the step title first, at any text scale
	next_button.text = tr("Finish") if step == STEPS.size() - 1 else tr("Next")


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
	if step >= STEPS.size() - 1:
		_finish()
		return
	step += 1
	_show()


func skip() -> void:
	_finish()


## Combat events from the engine: the current step advances when its trigger appears.
func on_events(events: Array[Dictionary]) -> void:
	var until := String(STEPS[step]["until"])
	if until == "":
		return
	for e in events:
		if String(e.get("type", "")) == until:
			advance()
			return


func _finish() -> void:
	Settings.set_tutorial_done(true)
	finished.emit()
	queue_free()
