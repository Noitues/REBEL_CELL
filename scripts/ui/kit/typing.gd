class_name Typing
extends Node
## Text that types in on screen (Animation pass ANIM-6, ANIMATION_HANDOFF 4.13 / 4.21): the
## Terminal event's words (`dispatch_type`) and the HQ's pirate radio (`radio_type`), at the
## entry's seconds per character. Only what is drawn changes (`visible_characters`): the
## text itself is whole from the start, so tests and screen readers read it all. Honours
## the Options switch (Settings.subtitle_typing: off shows the words at once), reduce
## effects and headless. Any press (MotionSkip) shows the words whole; it is consumed unless
## it works the screen (ANIM-R3: a focus move, accept on a button, a click on a button pass
## on); so do `finish` and PageTransition.settle. ANIM-R2: the press shows
## every word typing on screen at once (all Typing labels and the Dialogue subtitle), so an
## event's story and its subtitle need one press, not two.

const META := &"typing_tween"
const NODE_NAME := "Typing"
## Every live Typing skip node (finish_all shows them all).
const GROUP := &"typing_skip"

var label: Control = null


## Types `label`'s words in (a Label or RichTextLabel) with `id`'s speed; returns the
## seconds it takes (0: shown whole at once).
static func type_in(p_label: Control, id: StringName = &"dispatch_type") -> float:
	finish(p_label)
	if p_label == null or not p_label.is_inside_tree() or not Settings.subtitle_typing or not Motion.live(id):
		return 0.0
	var total: int = p_label.get_total_character_count()
	if total <= 0:
		return 0.0
	var seconds := total * Motion.seconds(id)
	# ANIM-R4 C7: an entry with an amplitude types the whole text within that many seconds
	# (an event's story took 8 s, its panel empty meanwhile).
	if Motion.amplitude(id) > 0.0:
		seconds = minf(seconds, Motion.amplitude(id) / maxf(Motion.speed, Motion.SPEED_MIN))
	# ANIM-R5 B1: the words are shaped whole while they type, so a label that sizes to its
	# text (fit_content, autowrap) keeps its full height from the first frame (by default
	# only the shown characters were laid out: the event's paper collapsed to a sliver).
	p_label.set(&"visible_characters_behavior", TextServer.VC_CHARS_AFTER_SHAPING)
	p_label.set(&"visible_characters", 0)
	var e := Motion.entry(id)
	var tw := p_label.create_tween()
	tw.tween_property(p_label, "visible_characters", total, seconds).set_delay(Motion.delay_of(id)).set_ease(e.ease).set_trans(e.trans)
	tw.tween_callback(finish.bind(p_label))
	p_label.set_meta(META, tw)
	var skip := Typing.new()
	skip.name = NODE_NAME
	skip.label = p_label
	p_label.add_child(skip)
	skip.add_to_group(GROUP)
	return seconds


## True while `label` is still typing.
static func typing(p_label: Control) -> bool:
	if p_label == null or not is_instance_valid(p_label) or not p_label.has_meta(META):
		return false
	var tw: Tween = p_label.get_meta(META)
	return tw != null and tw.is_valid()


## Shows `label`'s words whole at once.
static func finish(p_label: Control) -> void:
	if p_label == null or not is_instance_valid(p_label):
		return
	if p_label.has_meta(META):
		var tw: Tween = p_label.get_meta(META)
		p_label.remove_meta(META)
		if tw != null and tw.is_valid():
			tw.kill()
		p_label.set(&"visible_characters", -1)
	var skip := p_label.get_node_or_null(NodePath(NODE_NAME))
	if skip != null:
		skip.queue_free()


## Shows every label typing in under `tree` whole, and the Dialogue subtitle (ANIM-R2: one
## press reads everything on screen).
static func finish_all(tree: SceneTree) -> void:
	if tree == null:
		return
	for n in tree.get_nodes_in_group(GROUP):
		var t := n as Typing
		if t != null and is_instance_valid(t.label):
			finish(t.label)
	var dialogue := tree.root.get_node_or_null(^"Dialogue") if tree.root != null else null
	if dialogue != null and dialogue.has_method(&"finish_typing"):
		dialogue.call(&"finish_typing")


## True while any label under `tree` is typing in.
static func any_typing(tree: SceneTree) -> bool:
	if tree == null:
		return false
	for n in tree.get_nodes_in_group(GROUP):
		var t := n as Typing
		if t != null and typing(t.label):
			return true
	return false


## ANIM-R3 A3: a press shows every typing word whole; a press that works the screen
## (MotionSkip.works_ui: a focus move, the Settings key, accept on the focused button, a
## click on a button: the first click on City Grid or JACK IN while the pirate radio types)
## passes on to what it works. Only a press aimed at the words (a click on them, a key or
## pad button that works nothing) is consumed. While a PauseMenu is open presses are its.
## ANIM-R5: by the one rule (MotionSkip.handle), which completes every running motion
## (every typing label and the subtitle among them: this skip node is registered).
func _input(event: InputEvent) -> void:
	if typing(label):
		MotionSkip.handle(event, self)


func _ready() -> void:
	MotionSkip.register(self)


## MotionSkip (ANIM-R5): the label is still typing.
func motion_running() -> bool:
	return typing(label)


## MotionSkip (ANIM-R5): the label's words whole.
func complete_motion() -> void:
	finish(label)
