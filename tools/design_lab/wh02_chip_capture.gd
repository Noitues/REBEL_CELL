extends Node
## Plan 2 WH-02 review capture (dev tool, windowed only through tools/run_windowed.py): the
## netrun HUD with its theme chip filled by a placeholder (no theme rule fills it yet), at
## 1920x1080 and 1280x720. Writes 1920.png and 1280.png into `--out=<abs dir>`;
## tools/design_lab/wh02_chip_sheet.py joins them with a close crop of each bar.
##   res://tools/design_lab/wh02_chip_capture.tscn -- --out=<abs dir>

const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const SLOT := "gut_wh02_chip"
const BAKE_FRAMES := 600
const SETTLE := 30
## The placeholder a Solace rule would show (dev tool only; no TextDb key).
const PLACEHOLDER := "BLOOM CLOSE  GAP 1.5"
const SIZES: Array[Vector2i] = [Vector2i(1920, 1080), Vector2i(1280, 720)]

var _out := ""


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
	DirAccess.make_dir_recursive_absolute(_out)
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	_run.call_deferred()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _run() -> void:
	DisplayServer.window_set_size(SIZES[0])
	await _frames(4)
	RunManager.reset()
	RunManager.new_campaign(1, &"solace")
	var net: Node = NETRUN.instantiate()
	add_child(net)
	net.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(2)
	net.start_run(1)
	for f in BAKE_FRAMES:
		if net.arrival_ready():
			break
		await get_tree().process_frame
	await _frames(SETTLE)
	for sz in SIZES:
		DisplayServer.window_set_size(sz)
		await _frames(SETTLE)
		net.hud.set_theme_chip(PLACEHOLDER, RunThemeState.ChipKind.WARN)
		await _frames(6)
		var img := get_viewport().get_texture().get_image()
		print("WH02 chip: size %s image %s chip visible %s rect %s" % [sz, img.get_size(), net.hud.theme_chip.visible, net.hud.theme_chip.get_global_rect()])
		img.save_png("%s/%d.png" % [_out, sz.x])
	RunManager.delete_save()
	get_tree().quit()
