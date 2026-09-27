class_name TutorialOverlay
extends Control
## Guided first fight (gap analysis 2.5 onboarding): zine notes that explain the wheel,
## precision, nudges and resistance, cards and the preview, rewind and checkpoints, End
## Turn and the resolution order, then Heat and banking. Steps advance on the matching
## combat events (or Next); Skip ends it. Marks Settings.tutorial_done when finished.

signal finished

## Height kept for the Next / Skip row under the note.
const BUTTON_ROW_HEIGHT := 40.0

const STEPS: Array[Dictionary] = [
	{"title": "THE WHEEL", "text": "Each white needle reads the slice under it: that slice is what the wheel does when you SEND IT. The tag above each wheel shows it, and its chips show every result (red HP = damage coming, BLK = block, RAM, HEAT...). Glyphs: ▲ attack, ✦ crit, ■ defend, ⬢ shield, ◇ evade, ⬡ deploy, ✚ heal, ◈ afflict, ✕ miss. {inspect_how} anything to read it.", "until": ""},
	{"title": "NUDGE", "text": "Land dead centre for PERFECT (full output plus your class hook), 1 tick off for GOOD, 2 off for PARTIAL (half). The curved arrows over a wheel turn it one tick: the right one clockwise, the left one back. {nudge_how}", "until": "nudge"},
	{"title": "RESISTANCE", "text": "Enemy wheels resist: each point absorbs one tick of your manipulation before it moves. Flip and Respin are blocked while resistance is up. Strip it, breach the Hub, or spin past it.", "until": ""},
	{"title": "CARDS", "text": "Cards spin, nudge and flip wheels; they cost RAM. {card_how} Nudge cards go on an arrow (that sets the way they turn), slice cards on a slice. While you aim, the tags and the dashed acid arc show the result before you commit.", "until": "card"},
	{"title": "UNDO", "text": "{undo_how} undoes anything back to the last random event (the start-of-turn respin). Undo is free and unlimited within a turn; a Respin or a random slice pick sets a new checkpoint.", "until": "rewind"},
	{"title": "SEND IT", "text": "SEND IT {end_turn} resolves every needle at once: defensive slices, then offensive, then statuses. The tags already show the outcome.", "until": "turn_start"},
	{"title": "HEAT & BANKING", "text": "Every Rack you capture banks Schematics for the Cell and adds Heat. Heat thresholds bring raids on your home server. Bank early, cool off at Heat objectives, and never leave loot unbanked when you jack out.", "until": ""},
]

var step: int = 0
var note: ZineNote
var next_button: Button
var skip_button: Button
var row: HBoxContainer


func _init(p_size: Vector2 = Vector2(380, 190)) -> void:
	custom_minimum_size = p_size
	size = p_size
	note = ZineNote.new("TUTORIAL", Vector2(p_size.x, p_size.y - BUTTON_ROW_HEIGHT)).make_reference()
	add_child(note)
	row = HBoxContainer.new()
	row.position = Vector2(10, p_size.y - BUTTON_ROW_HEIGHT + 2)
	add_child(row)
	next_button = Button.new()
	next_button.text = "Next"
	next_button.pressed.connect(advance)
	row.add_child(next_button)
	skip_button = Button.new()
	skip_button.text = "Skip tutorial"
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
	note.custom_minimum_size = Vector2(p_size.x, p_size.y - BUTTON_ROW_HEIGHT)
	note.size = note.custom_minimum_size
	row.position = Vector2(10, p_size.y - BUTTON_ROW_HEIGHT + 2)


func _show() -> void:
	note.clear()
	var s: Dictionary = STEPS[step]
	note.append("[b]%d/%d %s[/b]" % [step + 1, STEPS.size(), s["title"]])
	note.append(step_text(step))
	note.label.scroll_to_line.call_deferred(0)  # the step title first, at any text scale
	next_button.text = "Finish" if step == STEPS.size() - 1 else "Next"


## Step `i`'s text with the current binds filled in (pad buttons when a pad is in use).
static func step_text(i: int) -> String:
	var keys := {}
	for action in [&"nudge_left", &"nudge_right", &"rewind", &"end_turn", &"inspect"]:
		keys[String(action)] = Settings.hint(action)
	var pad := Settings.pad_active
	keys["inspect_how"] = "Press %s on" % Settings.key_text(&"inspect") if pad else "Hover or right-click"
	keys["nudge_how"] = ("%s and %s nudge the wheel the arrows mark." % [Settings.key_text(&"nudge_left"), Settings.key_text(&"nudge_right")]) if Settings.key_text(&"nudge_left") != "" else ""
	keys["card_how"] = "Pick a card with A, choose a glowing target with the D-pad, press A again (B cancels)." if pad else "Drag a card onto a glowing target (or click it, then click the target; right-click cancels). Keys 1-9 pick cards."
	keys["undo_how"] = "UNDO %s" % Settings.hint(&"rewind")
	return String(STEPS[i]["text"]).format(keys)


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
