@tool
extends EditorScenePostImportPlugin
## LOOK-TOOLBOX module 17: the Blender exports' post-import step. Every scene import gets the option `rc_look/stamp_slots`,
## on by default for a file under a folder of RcLookSlotsConfig.post_import_dirs (look_slots.tres; the repo ignores
## *.import, so the step is wired here, not per file). When on, each MeshInstance3D is stamped with its slots
## (RcLookSlots.META: "family:role" per surface) and a slot name no family lists is reported at import, where a renderer
## would otherwise give it a fallback without a word. Materials are not changed: the views still assign them by role at
## runtime, so the imported scene draws exactly as before.

const OPTION := "rc_look/stamp_slots"


func _get_import_options(path: String) -> void:
	add_import_option(OPTION, RcLookSlots.wants(path))


func _post_process(scene: Node) -> void:
	if not bool(get_option_value(OPTION)):
		return
	var bad := RcLookSlots.stamp(scene)
	if not bad.is_empty():
		push_warning("rc_look slots: %s has unlisted material slots %s (add them to look_slots.tres)" % [scene.name, ", ".join(bad)])
