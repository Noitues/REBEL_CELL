class_name RaidPencilPool
extends PencilSet
## ART-6 3A: the raid's grease pencil on the kit's one wax material (a PencilSet, B1b): a pool
## of marks and words its owner asks for each frame by key (`begin`, then `stroke` / `word`
## for every mark it shows, then `end`), with the progress the owner drives, so the raid keeps
## its own timing (reading holds in real time, a skip at the end state) while the wax, its
## width, its shader, its under-shadow and PencilLint's group are the kit's. The pool lives on
## the scene's raid pencil CanvasLayer (LAYER: above every UI layer the raid shows, under Fx's
## jack cover), so no UI ever covers the pencil (§1.2); its owner frees it when it leaves
## (`release`). Points are global (screen) px: every raid layer maps its map anchors through
## one seam (RaidMapAnchor) first. The combat aim (AimLinePencil) uses it too.

## The raid pencil's CanvasLayer order: over Dialogue's subtitles (90), under Fx (100).
const LAYER := 95
const LAYER_NAME := "RaidPencilLayer"


## A pool on the raid pencil layer of `host`'s scene (made once per scene).
static func make(host: Node) -> RaidPencilPool:
	var pool := RaidPencilPool.new()
	var scene := host
	while scene.get_parent() != null and scene.get_parent() != host.get_tree().root:
		scene = scene.get_parent()
	var layer := scene.get_node_or_null(LAYER_NAME) as CanvasLayer
	if layer == null:
		layer = CanvasLayer.new()
		layer.name = LAYER_NAME
		layer.layer = LAYER
		scene.add_child(layer)
	layer.add_child(pool)
	return pool


## Frees the pool (its owner left).
func release() -> void:
	queue_free()
