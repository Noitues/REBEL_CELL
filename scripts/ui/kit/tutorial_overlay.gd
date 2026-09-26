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
	{"title": "THE WHEEL", "text": "30 ticks, 6 slices. The white pointer reads the tick under it; the slice it lands on is what you do this turn. Glyphs: ▲ attack, ✦ crit, ■ defend, ⬢ shield, ◇ evade, ⬡ deploy, ✚ heal, ◈ afflict, ✕ miss. Right-click any slice to inspect it.", "until": ""},
	{"title": "PRECISION", "text": "Land dead centre for PERFECT (full output plus your class hook), 1 tick off for GOOD (full), 2 off for PARTIAL (half). Press {nudge_left} or {nudge_right} to nudge your wheel one tick.", "until": "nudge"},
	{"title": "RESISTANCE", "text": "Enemy wheels resist: each point absorbs one tick of your manipulation before it moves. Flip and Respin are blocked entirely while resistance is up. Strip it, breach the Hub, or spin past it.", "until": ""},
	{"title": "CARDS & PREVIEW", "text": "Cards spin, nudge and flip wheels; they cost RAM. Hover a card to see exactly what will resolve (dashed acid arc = where your pointer ends up). Play a card with 1-9 or a click.", "until": "card"},
	{"title": "REWIND", "text": "Press {rewind} to undo anything back to the last random event (the start-of-turn respin). Undo is free and unlimited within a turn; a Respin or a random slice pick sets a new checkpoint.", "until": "rewind"},
	{"title": "SEND IT", "text": "End Turn resolves every pointer at once: defensive slices, then offensive, then statuses. The preview strip already shows the result. Press {end_turn}.", "until": "turn_start"},
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


## Step `i`'s text with the current key binds filled in.
static func step_text(i: int) -> String:
	var keys := {}
	for action in [&"nudge_left", &"nudge_right", &"rewind", &"end_turn"]:
		keys[String(action)] = Settings.key_text(action)
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
