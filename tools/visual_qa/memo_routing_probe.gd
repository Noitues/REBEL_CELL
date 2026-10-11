extends Node
## M14 FIX-2 memo routing probe (dev tool, never exported): pictures the corp memo of every
## corporation whole at each text scale, before (the routing line on one line, clipped at the
## sheet's width: the code before FIX-2, kept here as `ClippedMemo`) and after (CorpMemo's own
## wrap, then fold). Writes <out>/memo_x<scale>_<corp>_<before|after>.png. Needs a renderer: run
## only through tools/run_windowed.py:
##   python tools/run_windowed.py --log <file> -- --resolution 1280x720 \
##       res://tools/visual_qa/memo_routing_probe.tscn -- --out=<abs dir> [--scales=1.0,2.0]

## The memo's width on the event screen (NetrunScene.EVENT_MEMO_W) and the picture's margin (px).
const MEMO_W := 470.0
const MARGIN := 10.0
const SETTLE_FRAMES := 3
## The backdrop the sheets lie on (the HQ board's dark).
const BOARD := Color(0.08, 0.08, 0.1)
const STORY := "Asset recovery is behind schedule. The Cell's runners were seen near the relay twice this week; tier leads are to log every sighting before the shift change."


## The memo as drawn before FIX-2: the routing line on one line, clipped at the sheet's width.
class ClippedMemo extends CorpMemo:
	func _fit_routing() -> void:
		pass

	func _draw_head(on: Control) -> void:
		var s := text_scale
		var r := Rect2(Vector2.ZERO, size)
		on.draw_rect(Rect2(Vector2((r.size.x - TAPE.x * s) * 0.5, -TAPE.y * s * 0.45), TAPE * s), Palette.NOTE_TAPE)
		var paper := Palette.paper_bold()
		var ts := roundi(TITLE_PX * s)
		var y := head_h() + 6.0 * s + paper.get_ascent(ts)
		on.draw_string(paper, Vector2(PAD.x * s, y), tr(head_word), HORIZONTAL_ALIGNMENT_LEFT, -1, ts, Palette.PAPER_TYPE_INK)
		var ms := roundi(META_PX * s)
		y += paper.get_descent(ts) + Palette.paper().get_ascent(ms) + 4.0 * s
		on.draw_string(Palette.paper(), Vector2(PAD.x * s, y), routing_text(), HORIZONTAL_ALIGNMENT_LEFT, r.size.x - PAD.x * 2.0 * s, ms, Palette.TEXT_LO)


var out_dir := ""
var scales: Array[float] = [1.0, 2.0]


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--scales="):
			scales.clear()
			for v in a.trim_prefix("--scales=").split(","):
				scales.append(float(v))
	if out_dir == "":
		push_error("memo_routing_probe: --out=<abs dir> is required")
		get_tree().quit(1)
		return
	DirAccess.make_dir_recursive_absolute(out_dir)
	Settings.path = "user://memo_routing_probe_settings.cfg"
	AudioDirector.muted = true
	var back := ColorRect.new()
	back.color = BOARD
	back.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(back)
	var was := Settings.text_scale
	for k in scales:
		Settings.set_text_scale(k)
		for corp: StringName in RaidSkin.CORPS:
			for after in [false, true]:
				await _shot(corp, after, k)
	Settings.set_text_scale(was)
	get_tree().quit(0)


func _shot(corp: StringName, after: bool, k: float) -> void:
	var res := RunManager.lookup().get_content(corp)
	var memo: CorpMemo = CorpMemo.new(TextDb.t(res, "display_name"), Palette.corp_color(corp), k, CorpPaperPanel.letterhead_of(res)) if after \
		else ClippedMemo.new(TextDb.t(res, "display_name"), Palette.corp_color(corp), k, CorpPaperPanel.letterhead_of(res))
	memo.custom_minimum_size = Vector2(MEMO_W, 0.0)
	memo.rotation_degrees = 0.0
	var text := Label.new()
	text.text = STORY
	text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.custom_minimum_size = Vector2(MEMO_W - CorpMemo.PAD.x * 2.0 * k, 0)
	text.add_theme_font_override(&"font", Palette.paper())
	text.add_theme_font_size_override(&"font_size", roundi(14 * k))
	text.add_theme_color_override(&"font_color", Palette.PAPER_TYPE_INK)
	memo.body.add_child(text)
	add_child(memo)
	memo.position = Vector2(MARGIN, MARGIN) * 3.0
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	memo.size = memo.get_combined_minimum_size()
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var sx := float(img.get_width()) / get_viewport().get_visible_rect().size.x
	var r := memo.get_global_rect().grow(MARGIN)
	var px := Rect2i(Vector2i(r.position * sx), Vector2i(r.size * sx)).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	img.get_region(px).save_png(out_dir.path_join("memo_x%.1f_%s_%s.png" % [k, corp, "after" if after else "before"]))
	print("memo_routing_probe: x%.1f %s %s lines=%d" % [k, corp, "after" if after else "before", memo.routing_lines().size()])
	memo.queue_free()
	await get_tree().process_frame
