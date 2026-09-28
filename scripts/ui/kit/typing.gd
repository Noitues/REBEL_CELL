class_name Typing
extends Node
## Text that types in on screen (Animation pass ANIM-6, ANIMATION_HANDOFF 4.13 / 4.21): the
## Terminal event's words (`dispatch_type`) and the HQ's pirate radio (`radio_type`), at the
## entry's seconds per character. Only what is drawn changes (`visible_characters`): the
## text itself is whole from the start, so tests and screen readers read it all. Honours
## the Options switch (Settings.subtitle_typing: off shows the words at once), reduce
## effects and headless. Any press (MotionSkip) shows the words whole and is consumed (it
## does nothing else); so do `finish` and PageTransition.settle.

const META := &"typing_tween"
const NODE_NAME := "Typing"

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


func _input(event: InputEvent) -> void:
	if MotionSkip.is_press(event) and typing(label):
		finish(label)
		MotionSkip.consume(self)
