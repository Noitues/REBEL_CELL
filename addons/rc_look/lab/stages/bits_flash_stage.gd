extends RcLookLabStage
## LOOK-TOOLBOX module 16: the hot flash, old next to new. The instant a bit spawns it is fully hot (age 0: WHITE_HOT in the
## old looks, PAPER in the ruled ones, no colour mixed in). Per group (burst GPU, burst CPU fallback, stream): the flash
## panels old | new (dark | light halves) at the sheet's scale, then a 4x nearest crop of one flash bit, old | new, on dark and
## on light, so the stroke weight and the rim can be compared. Run as `--module=bits_flash`. View only.

## The groups are the ruled sheet's.
const RULED := preload("res://addons/rc_look/lab/stages/bits_ruled_stage.gd")
const MARGIN := Vector2(190.0, 60.0)
const GAP := 6.0
const ROW_GAP := 36.0
const LABEL_SIZE := 13
const GLYPH_PX := 22.0
const BITS := 16
const CROP_PX := 32
const ZOOM := 4
## Every flash is at its spawn instant.
const FLASH_AGE := 0.0
## A pixel counts as lit above this luma.
const LIT_LUMA := 0.5
const PANEL_SIZE := Vector2(190.0, 190.0)

var _dark_vps: Array[SubViewport] = []
var _dark_names: Array[String] = []


func _ready() -> void:
	var view := get_viewport_rect().size
	var panel_h := (view.y - MARGIN.y - 30.0 - ROW_GAP * RULED.GROUPS.size()) / RULED.GROUPS.size()
	for g in RULED.GROUPS.size():
		var grp := RULED.GROUPS[g]
		var y := MARGIN.y + g * (panel_h + ROW_GAP)
		_label(String(grp["title"]), Vector2(20.0, y), 15)
		_label("old: %s\nnew: %s" % [grp["old"], grp["new"]], Vector2(20.0, y + 24.0), 12)
		var x := MARGIN.x
		for side in 2:
			var v := RcLookBitsView.new()
			v.position = Vector2(x + side * (PANEL_SIZE.x + GAP), y)
			v.size = Vector2(PANEL_SIZE.x, panel_h)
			v.preset = RcLookBits.preset(StringName(grp["old"] if side == 0 else grp["new"]))
			v.mode = &"grid"
			v.clock_s = FLASH_AGE
			v.age_s = FLASH_AGE
			v.split = true
			v.bits = BITS
			v.glyph_px = GLYPH_PX
			add_child(v)
			_label("old" if side == 0 else "NEW", Vector2(v.position.x, y + panel_h + 1.0), 11)
		x += 2.0 * PANEL_SIZE.x + 60.0
		for dark in 2:
			for side in 2:
				var vp := SubViewport.new()
				vp.size = Vector2i(CROP_PX, CROP_PX)
				vp.transparent_bg = false
				vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
				var z := RcLookBitsView.new()
				z.size = Vector2(CROP_PX, CROP_PX)
				z.preset = RcLookBits.preset(StringName(grp["old"] if side == 0 else grp["new"]))
				z.mode = &"zoom"
				z.age_s = FLASH_AGE
				z.zoom_dark = dark == 1
				z.glyph_px = GLYPH_PX
				vp.add_child(z)
				if dark == 1:
					_dark_vps.append(vp)
					_dark_names.append("%s_%s" % [grp["title"], "old" if side == 0 else "new"])
				add_child(vp)
				var tr := TextureRect.new()
				tr.texture = vp.get_texture()
				tr.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
				tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
				tr.stretch_mode = TextureRect.STRETCH_SCALE
				tr.position = Vector2(x + (dark * 2 + side) * (CROP_PX * ZOOM + GAP), y)
				tr.size = Vector2(CROP_PX, CROP_PX) * ZOOM
				add_child(tr)
				_label(("on dark " if dark == 1 else "on light ") + ("old" if side == 0 else "NEW"), Vector2(tr.position.x, y + tr.size.y + 1.0), 11)
	_report(_dark_vps, _dark_names)


func _label(text: String, at: Vector2, size: int = LABEL_SIZE) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", size)
	add_child(l)


## The lit pixels (luma above LIT_LUMA) of every dark crop, old and new, written to `--flash_report=<json>` (a number for the
## stroke weight: the stage's eyes can be fooled by colour).
func _report(vps: Array[SubViewport], names: Array[String]) -> void:
	var path := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--flash_report="):
			path = a.trim_prefix("--flash_report=")
	if path == "":
		return
	for k in 6:
		await get_tree().process_frame
	var out := {}
	for i in vps.size():
		var img := vps[i].get_texture().get_image()
		var n := 0
		var mass := 0.0
		for y in img.get_height():
			for x in img.get_width():
				var l := img.get_pixel(x, y).get_luminance()
				mass += l
				if l > LIT_LUMA:
					n += 1
		out[names[i]] = {"lit_px": n, "luma_mass": snappedf(mass, 0.01)}
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f != null:
		f.store_string(JSON.stringify(out, "\t"))
