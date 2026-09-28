extends SceneTree
## ANIM-R2 R11 (dev tool): bakes one region of the net city twice, once the game's way (the
## geometry built in slices on the worker pool, submitted a chunk at a time, the picture
## copied on the GPU) and once the old synchronous way (built in the painter's first draw,
## read back to the CPU), and compares the two images pixel by pixel. Needs a real display
## (never headless):
##
##   godot --path . -s tools/design_lab/bake_compare.gd [-- --region=x,y,w,h --district=solace]
##
## Prints "bake_compare: <w>x<h>, <n> pixels differ (max channel diff <d>)". Class names that
## touch autoloads are loaded at run time (a -s script compiles before the autoloads exist).

var _region := Rect2(-2560, -1280, 1792, 1152)
var _district := &"solace"
var _cache: GDScript
var _city: Control
var _frames := 0
var _step := 0
var _img_a: Image


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--region="):
			var v := a.trim_prefix("--region=").split(",")
			_region = Rect2(float(v[0]), float(v[1]), float(v[2]), float(v[3]))
		elif a.begins_with("--district="):
			_district = StringName(a.trim_prefix("--district="))
	_cache = load("res://scripts/ui/kit/city_bake_cache.gd")
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	root.add_child(holder)
	_city = (load("res://scripts/ui/kit/neon_city.gd") as GDScript).new()
	_city.set("net_mode", true)
	_city.set("district", _district)
	_city.visible = false
	holder.add_child(_city)


func _bake(key: String, threaded: bool) -> void:
	_cache.set("threaded", threaded)
	_cache.set("gpu_copy", threaded)
	var look: String = _city.call("look_key")
	var painter: Object = _city.call("make_painter", _region, 1.0)
	_cache.call("request", key, look, painter, _city)


func _image(key: String) -> Image:
	var e: Dictionary = _cache.call("entry", key)
	var tex: Texture2D = e.get("texture")
	if tex == null:
		return null
	var img := tex.get_image()
	if img != null:
		img.convert(Image.FORMAT_RGBA8)
	return img


func _process(_delta: float) -> bool:
	_frames += 1
	match _step:
		0:
			if _frames > 5:
				_bake("threaded", true)
				_step = 1
		1:
			if bool(_cache.call("has", "threaded")):
				_img_a = _image("threaded")
				_bake("sync", false)
				_step = 2
		2:
			if bool(_cache.call("has", "sync")):
				var b := _image("sync")
				_report(_img_a, b)
				_cache.call("shutdown")
				return true
	return _frames > 3000


func _report(a: Image, b: Image) -> void:
	if a == null or b == null:
		print("bake_compare: an image is missing (threaded %s, sync %s)" % [a != null, b != null])
		return
	if a.get_size() != b.get_size():
		print("bake_compare: sizes differ %s vs %s" % [a.get_size(), b.get_size()])
		return
	var differ := 0
	var worst := 0.0
	var box := Rect2i()
	for y in a.get_height():
		for x in a.get_width():
			var ca := a.get_pixel(x, y)
			var cb := b.get_pixel(x, y)
			if ca != cb:
				box = Rect2i(x, y, 1, 1) if differ == 0 else box.expand(Vector2i(x, y))
				differ += 1
				worst = maxf(worst, maxf(maxf(absf(ca.r - cb.r), absf(ca.g - cb.g)), maxf(absf(ca.b - cb.b), absf(ca.a - cb.a))))
	print("bake_compare: %dx%d, region %s, %d pixels differ (max channel diff %.4f)%s" % [a.get_width(), a.get_height(), _region, differ, worst,
		(" within image px %s" % box) if differ > 0 else ""])
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--dump=") and differ > 0:
			var dir := arg.trim_prefix("--dump=")
			a.save_png(dir.path_join("bake_threaded.png"))
			b.save_png(dir.path_join("bake_sync.png"))
