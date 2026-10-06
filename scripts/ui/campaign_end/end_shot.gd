class_name EndShot
extends Node
## B5 (integration review Q8: "Won and abandoned network photos: yes. Shoot them from the unified city at the final
## state"): the shot a won or abandoned campaign's audit dossier prints, as the lost campaign's lock takes its own
## (RansomLock._take_snapshot): once the host's city has settled with the Cell's network on it (`ready_check`, or
## after WAIT_FRAMES), the next drawn frame is read back with the network's node points (`nodes_provider`), and
## `taken(image, points)` goes up; the host builds the dossier's prints from them (HqScene.end_photos). Headless
## (no frame to read) it hands back no image at once. View only; it changes nothing.

signal taken(image: Image, points: Array)

## The most frames it waits for the city before it shoots anyway (the lock's own wait).
const WAIT_FRAMES := 240

var nodes_provider: Callable = Callable()
var ready_check: Callable = Callable()
var _frames: int = 0
var _done: bool = false


func _init(p_nodes: Callable = Callable(), p_ready: Callable = Callable()) -> void:
	name = "EndShot"
	nodes_provider = p_nodes
	ready_check = p_ready


func _process(_delta: float) -> void:
	if _done:
		return
	_frames += 1
	var ready := not ready_check.is_valid() or bool(ready_check.call())
	if ready or _frames >= WAIT_FRAMES or DisplayServer.get_name() == "headless":
		_done = true
		set_process(false)
		_shoot()


func _shoot() -> void:
	var points: Array = nodes_provider.call() if nodes_provider.is_valid() else []
	if DisplayServer.get_name() == "headless" or not is_inside_tree():
		taken.emit(null, points)
		return
	await RenderingServer.frame_post_draw
	if not is_inside_tree():
		return
	var tex := get_viewport().get_texture()
	taken.emit(tex.get_image() if tex != null else null, points)
