@tool
extends EditorScenePostImport
## LOOK-TOOLBOX module 17: the Blender exports' post-import step. Set as a glb's import script
## (`nodes/import_script` / `import_script/path` in its .import): every MeshInstance3D gets its slots stamped
## (RcLookSlots.META: "family:role" per surface, from addons/rc_look/config/look_slots.tres) and a slot name no family lists
## is reported at import, where the renderers would otherwise give it a fallback without a word. Materials are not changed:
## the views still assign them by role at runtime, so the imported scene draws exactly as before.


func _post_import(scene: Node) -> Object:
	var bad := RcLookSlots.stamp(scene)
	if not bad.is_empty():
		push_warning("rc_look slots: %s has unlisted material slots %s (add them to look_slots.tres)" % [get_source_file(), ", ".join(bad)])
	return scene
