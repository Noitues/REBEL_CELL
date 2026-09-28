class_name Typing
extends Node
## Text that types in on screen (Animation pass ANIM-6, ANIMATION_HANDOFF 4.13 / 4.21): the
## Terminal event's words (`dispatch_type`) and the HQ's pirate radio (`radio_type`), at the
## entry's seconds per character. Only what is drawn changes (`visible_characters`): the
## text itself is whole from the start, so tests and screen readers read it all. Honours
## the Options switch (Settings.subtitle_typing: off shows the words at once), reduce
## effects and headless. Any press (MotionSkip) shows the words whole and is consumed (it
## does nothing else); so do `finish` and PageTransition.settle. ANIM-R2: the press shows
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


func _input(event: InputEvent) -> void:
	if MotionSkip.is_press(event) and typing(label):
		finish_all(get_tree())
		MotionSkip.consume(self)
