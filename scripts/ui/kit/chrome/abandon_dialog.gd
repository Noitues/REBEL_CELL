class_name AbandonDialog
extends ConfirmDialog
## ART-10 4C (ART_BIBLE v2 §4.13 "Abandon dialog", round 33 `abandon_dialog.jpg`): the confirm
## for losing something for good, on 2D's ConfirmDialog / HudDialogPanel (`> CONFIRM // TITLE`,
## CANNOT UNDO in HARM, yellow CANCEL with the default focus, the pink verb). Under the question
## its body in Plex, then the costs (terminal CAPS names, live numbers, two pairs a row), the
## Heat line in HARM and what stays in GAIN. View only: the caller says what the costs are and
## what a confirm does.

## The costs' type step and the gap between the two pairs of a row (px at text scale 1.0).
const COST_STEP := UiTheme.BODY
const PAIR_GAP := 36
## The least width of a cost's name column (px at text scale 1.0).
const NAME_W := 150.0
## The answer stickers' lettering (px at 1.0) and tilts (degrees; abandon.py places CANCEL at
## +2 and the verb at -3 counter-clockwise), and the baked art's key prefix.
const STICKER_PX := 40.0
const SAFE_TILT := -2.0
const VERB_TILT := 3.0
const ART_PREFIX := "dialog_"

## Designer ruling 2026-10-05 (round 33 `abandon_dialog`: "BURN IT needs a 0.8 s hold (lime ring
## fills) so it is never a stray press"): with `require_hold`, the pad / keyboard confirm is a
## hold of `dialog_hold_confirm` (read raw: never sped up, and reduce effects still fills the
## ring); a mouse click confirms at once; letting go early empties the ring.
const HOLD_MOTION := &"dialog_hold_confirm"

## The verb needs the hold (`require_hold`), its ring, how full it is (0..1) and whether the
## accept is held now.
var hold_to_confirm: bool = false
var hold_ring: HoldRing = null
var hold_progress: float = 0.0
var holding: bool = false

## The costs grid (names and values), the Heat line and the line that says what stays.
var costs_grid: GridContainer = null
var heat_label: Label = null
var kept_label: Label = null


## `costs` = [[name key, value], ...] (names translated here, values shown as given); `heat`
## (translated) is the Heat the loss adds, in HARM; `kept` (translated) says what stays, in GAIN.
## The rest as ConfirmDialog: `question` and `body` come translated, the answers and the title
## are keys, `yes_note` / `no_note` are the captions under the stickers.
func _init(question: String, yes_text: String, title: String, body: String = "", costs: Array = [], heat: String = "",
		kept: String = "", yes_note: String = "", no_note: String = "") -> void:
	super(question, yes_text, "CANCEL", title, body, true, yes_note, no_note) # TR
	var box := panel.body.get_child(0) as VBoxContainer
	var rule_at := box.get_child_count() - 2  # the rule over the stickers' row
	var body_label := box.find_child("Body", false, false) as Label
	if body_label != null:
		# The round 33 body reads in Plex, like the question.
		body_label.add_theme_font_override(&"font", HudSkin.body())
		body_label.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.LABEL))
	var extra: Array[Control] = []
	if not costs.is_empty():
		costs_grid = GridContainer.new()
		costs_grid.name = "Costs"
		costs_grid.columns = 4
		costs_grid.add_theme_constant_override(&"h_separation", roundi(PAIR_GAP * Settings.text_scale))
		for c in costs:
			var pair: Array = c
			var n := Chrome.caps_label(tr(String(pair[0])).to_upper(), COST_STEP, Palette.TEXT_MID)
			n.custom_minimum_size.x = maxf(n.custom_minimum_size.x, NAME_W * Settings.text_scale)
			costs_grid.add_child(n)
			var v := Chrome.caps_label(str(pair[1]), COST_STEP, Palette.TEXT_HI)
			v.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
			v.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
			costs_grid.add_child(v)
		extra.append(costs_grid)
	if heat != "":
		heat_label = Chrome.caps_label(heat, COST_STEP, Palette.HARM)
		heat_label.name = "Heat"
		heat_label.custom_minimum_size.x = 0.0  # it may wrap at big text
		extra.append(heat_label)
	if kept != "":
		kept_label = Chrome.body_label(kept, UiTheme.BODY, Palette.GAIN)
		kept_label.name = "Kept"
		extra.append(kept_label)
	for i in extra.size():
		box.add_child(extra[i])
		box.move_child(extra[i], rule_at + i)


## The answers are abandon.py's own stickers (baked by tools/art/bake_menus_r33.py: `dialog_cancel`,
## `dialog_delete`, `dialog_burn_it`, each with its lime focus halo), tilted as abandon.py places
## them, with the terminal caption under each. A word with no baked art (or a translated one) is
## the kit's vinyl sticker in the same fill.
func _sticker(row: Container, word: String, note: String, paint: Color) -> Button:
	var safe := paint == HudSkin.VINYL_YELLOW
	var shown := tr(word)
	var key := ART_PREFIX + word.to_lower().replace(" ", "_")
	var art := key if shown == word and ResourceLoader.exists(VerbSticker.ART_DIR + key + ".png") else ""
	var s := VerbSticker.new(shown, VerbSticker.Fill.YELLOW if safe else VerbSticker.Fill.PINK,
		STICKER_PX, SAFE_TILT if safe else VERB_TILT, art)
	s.pre_translated = true
	s.name = "Sticker"
	s.tooltip_text = tr(note) if note != "" else ""
	s.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	var col := VBoxContainer.new()
	col.name = "SafeAnswer" if safe else "VerbAnswer"
	col.add_theme_constant_override(&"separation", 2)
	col.add_child(s)
	if note != "":
		var c := Chrome.caps_label(tr(note), UiTheme.CAPTION, Palette.TEXT_MID if safe else Palette.STICKER_PINK)
		c.name = "Caption"
		c.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		c.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		col.add_child(c)
	row.add_child(col)
	return s


## The pad / keyboard confirm becomes a hold on the verb (see HOLD_MOTION); the lime ring
## fills round the sticker while it is held.
func require_hold() -> void:
	if hold_to_confirm:
		return
	hold_to_confirm = true
	hold_ring = HoldRing.new()
	yes_button.add_child(hold_ring)
	hold_ring.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	# The signal runs before the Button's own input: an accept taken here never presses it.
	yes_button.gui_input.connect(_on_verb_input)
	yes_button.focus_exited.connect(release_hold)


## How long the hold lasts (s): `dialog_hold_confirm`'s duration, raw.
static func hold_seconds() -> float:
	var e := Motion.entry(HOLD_MOTION)
	return e.duration if e != null else 0.0


func _on_verb_input(event: InputEvent) -> void:
	if event is InputEventMouse or not event.is_action("ui_accept"):
		return  # a click presses the sticker at once
	yes_button.accept_event()
	if event.is_pressed() and not event.is_echo():
		start_hold()
	elif not event.is_pressed():
		release_hold()


## The accept went down on the verb: the ring starts to fill.
func start_hold() -> void:
	holding = true
	set_process(true)


## The accept let go (or the focus left) before the ring filled: it empties.
func release_hold() -> void:
	holding = false
	_set_hold(0.0)


func _process(delta: float) -> void:
	if holding:
		advance_hold(delta)


## Fills the ring by `seconds` of hold; a full ring confirms (as a press of the verb).
func advance_hold(seconds: float) -> void:
	var total := hold_seconds()
	_set_hold(1.0 if total <= 0.0 else hold_progress + seconds / total)
	if hold_progress >= 1.0:
		holding = false
		set_process(false)
		yes_button.pressed.emit()


func _set_hold(k: float) -> void:
	hold_progress = clampf(k, 0.0, 1.0)
	if hold_ring != null:
		hold_ring.progress = hold_progress


## The words the costs show, name then value, in reading order (tests and the review pack).
func cost_words() -> PackedStringArray:
	var out := PackedStringArray()
	if costs_grid != null:
		for c in costs_grid.get_children():
			out.append((c as Label).text)
	return out
