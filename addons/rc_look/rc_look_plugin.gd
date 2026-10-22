@tool
extends EditorPlugin
## LOOK-TOOLBOX module 17: registers the post-import slot stamp (RcLookImportPlugin) for scene imports. Editor only; the game
## never loads it.

var _import: EditorScenePostImportPlugin = null


func _enter_tree() -> void:
	_import = preload("res://addons/rc_look/import/rc_look_import_plugin.gd").new()
	add_scene_post_import_plugin(_import)


func _exit_tree() -> void:
	if _import != null:
		remove_scene_post_import_plugin(_import)
		_import = null
