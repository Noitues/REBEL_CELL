extends "res://tools/visual_qa/review_pack.gd"
## M14 SPILL probe (dev tool, never exported): finds every screen reader (a CanvasItem whose shader
## takes `hint_screen_texture`) on each review-pack screen and tells whether it reads a stale copy
## of the screen. Since B1a b the scrim's AfterScrim is the last viewport copy before most UI, so a
## reader drawn after it reads the world as it stood there; when something drawn in between matters
## (or a mipmapped reader in between rewrote the copy) the reader paints a stale or blurred picture
## over its rect (the Mainframe's SignSpill, DECISIONS "Mainframe subtitle fits the screen").
## Per reader it captures the screen as is, with a viewport BackBufferCopy inserted just before it
## (a fresh copy), as is again (the noise floor: the city moves) and with the reader hidden. A
## reader whose fresh-copy picture differs from the as-is one past the noise floor reads a stale
## copy. Writes <out>/spill_probe.json (one row per reader) and, for a flagged reader, its three
## pictures (<screen>__<n>_{base,hidden,fresh}.png). Same arguments as review_pack, plus
## --glitch (Settings.heat_glitch on, so the Heat glitch's reader is probed too).
## Run only through tools/run_windowed.py (needs a renderer):
##   python tools/run_windowed.py --log <file> -- --fixed-fps 30 --resolution 1280x720 \
##       res://tools/visual_qa/spill_probe.tscn -- --out=<abs dir> [--screens=a,b] [--glitch]

## Downscaled size the pictures are compared at.
const CMP_SIZE := Vector2i(320, 180)
## A pixel counts as changed when a channel moves by more than this (0..255).
const PX_THRESHOLD := 24
## A reader is flagged when its fresh-copy picture changes this share of its rect more than the
## noise floor does.
const FLAG_SHARE := 0.01

var _rows: Array = []
var _glitch := false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a == "--glitch":
			_glitch = true
	super._ready()


func _setup_settings() -> void:
	super._setup_settings()
	if _glitch:
		Settings.heat_glitch = true
		Settings.changed.emit()


func _teardown() -> void:
	_write_json(out_dir.path_join("spill_probe.json"), {"rows": _rows})
	super._teardown()


func _capture(screen: String, method: String, what: String) -> void:
	await super._capture(screen, method, what)
	await _probe(screen)


func _probe(screen: String) -> void:
	var readers := _readers()
	if readers.is_empty():
		_rows.append({"screen": screen, "reader": "", "note": "no screen reader on this screen"})
		return
	var n := 0
	for ci in readers:
		if not is_instance_valid(ci) or not ci.is_visible_in_tree():
			continue
		var base := await _grab()
		var parent := ci.get_parent()
		var bbc := BackBufferCopy.new()
		bbc.name = "SpillProbeCopy"
		bbc.copy_mode = BackBufferCopy.COPY_MODE_VIEWPORT
		parent.add_child(bbc)
		parent.move_child(bbc, ci.get_index())
		var fresh := await _grab()
		bbc.free()
		var after := await _grab()
		ci.visible = false
		var hidden := await _grab()
		ci.visible = true
		var rect := _rect_of(ci, base.get_size())
		# The fresh picture sits between the two as-is ones: the noise is what moved between those.
		var noise := _changed_share(base, after, rect)
		var stale := minf(_changed_share(base, fresh, rect), _changed_share(after, fresh, rect))
		var off := _changed_share(after, hidden, rect)
		var mat := ci.material as ShaderMaterial
		var row := {
			"screen": screen, "reader": str(get_tree().root.get_path_to(ci)),
			"shader": mat.shader.resource_path, "canvas_layer": _canvas_layer_index(ci),
			"after_scrim": _after_scrim(ci), "rect": [rect.position.x, rect.position.y, rect.size.x, rect.size.y],
			"noise": noise, "stale": stale, "hidden_change": off,
			"flagged": stale > noise + FLAG_SHARE,
		}
		if row["flagged"]:
			var stem := out_dir.path_join("%s__%d" % [screen, n])
			base.save_png(stem + "_base.png")
			hidden.save_png(stem + "_hidden.png")
			fresh.save_png(stem + "_fresh.png")
			row["pictures"] = stem
		_rows.append(row)
		print("spill_probe: %s %s stale=%.4f noise=%.4f hidden=%.4f%s" % [screen, row["reader"], stale, noise, off, " FLAGGED" if row["flagged"] else ""])
		n += 1


## Every visible screen reader drawn into the main viewport (the scrim's own pools excluded: its
## BeforeScrim copy sits right before them).
func _readers() -> Array[CanvasItem]:
	var out: Array[CanvasItem] = []
	for node in get_tree().root.find_children("*", "CanvasItem", true, false):
		var ci := node as CanvasItem
		if ci == null or not ci.is_visible_in_tree() or ci.get_viewport() != get_viewport():
			continue
		var mat := ci.material as ShaderMaterial
		if mat == null or mat.shader == null or not mat.shader.code.contains("hint_screen_texture"):
			continue
		if ci.get_parent() is UiScrimPools:
			continue
		out.append(ci)
	return out


func _grab() -> Image:
	for i in 2:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	return get_viewport().get_texture().get_image()


## The reader's rect on screen (px of the picture): a Control's global rect, a LightSpill's rect,
## else the whole picture.
func _rect_of(ci: CanvasItem, size: Vector2i) -> Rect2:
	var full := Rect2(Vector2.ZERO, Vector2(size))
	var r := full
	var c := ci as Control
	if c != null:
		r = c.get_global_rect()
	elif ci is Node2D and ci.has_method(&"rect"):
		r = (ci as Node2D).get_global_transform() * (ci.call(&"rect") as Rect2)
	var scale := Vector2(size) / get_viewport().get_visible_rect().size
	r = Rect2(r.position * scale, r.size * scale).intersection(full)
	return r if r.has_area() else full


## Share of the rect's pixels (compared at CMP_SIZE) where a channel moved past PX_THRESHOLD.
func _changed_share(a: Image, b: Image, rect: Rect2) -> float:
	var sa := a.duplicate() as Image
	var sb := b.duplicate() as Image
	sa.resize(CMP_SIZE.x, CMP_SIZE.y, Image.INTERPOLATE_BILINEAR)
	sb.resize(CMP_SIZE.x, CMP_SIZE.y, Image.INTERPOLATE_BILINEAR)
	var k := Vector2(CMP_SIZE) / Vector2(a.get_size())
	var x0 := clampi(floori(rect.position.x * k.x), 0, CMP_SIZE.x - 1)
	var y0 := clampi(floori(rect.position.y * k.y), 0, CMP_SIZE.y - 1)
	var x1 := clampi(ceili(rect.end.x * k.x), x0 + 1, CMP_SIZE.x)
	var y1 := clampi(ceili(rect.end.y * k.y), y0 + 1, CMP_SIZE.y)
	var moved := 0
	var t := PX_THRESHOLD / 255.0
	for y in range(y0, y1):
		for x in range(x0, x1):
			var ca := sa.get_pixel(x, y)
			var cb := sb.get_pixel(x, y)
			if maxf(maxf(absf(ca.r - cb.r), absf(ca.g - cb.g)), absf(ca.b - cb.b)) > t:
				moved += 1
	return float(moved) / float((x1 - x0) * (y1 - y0))


func _canvas_layer_index(ci: CanvasItem) -> int:
	var cl := ci.get_canvas_layer_node()
	return 0 if cl == null else cl.layer


## True when a visible AfterScrim on the same canvas comes before the reader in tree order.
func _after_scrim(ci: CanvasItem) -> bool:
	for node in get_tree().root.find_children("AfterScrim", "BackBufferCopy", true, false):
		var bbc := node as BackBufferCopy
		if bbc.is_visible_in_tree() and bbc.get_canvas() == ci.get_canvas() and ci.is_greater_than(bbc):
			return true
	return false
