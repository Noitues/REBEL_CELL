extends Node
## M14 FOLLOW-UP letterhead probe (dev tool, never exported): pictures the letterhead of every
## corp-paper document (the raid work order, the corp memo, the operative dossier) for every
## corporation at each text scale, before (no letterhead name: the display name, fitted with its
## ellipsis; the dossier's mark word) and after (the corp's letterhead name, whole). Writes one
## PNG per picture: <out>/<kind>_x<scale>_<corp>_<before|after>.png (the sheet's top). Needs a
## renderer: run only through tools/run_windowed.py:
##   python tools/run_windowed.py --log <file> -- --resolution 1280x720 \
##       res://tools/visual_qa/letterhead_probe.tscn -- --out=<abs dir> [--scales=1.0,2.0]

const KINDS: Array[String] = ["order", "memo", "dossier"]
## The memo's width on the event screen (NetrunScene.EVENT_MEMO_W) and the picture's margin and
## height of the sheet's top it keeps (px at text scale 1.0).
const MEMO_W := 470.0
const MARGIN := 10.0
const TOP_H := 120.0
const SETTLE_FRAMES := 3
## The backdrop the sheets lie on (the HQ board's dark).
const BOARD := Color(0.08, 0.08, 0.1)

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
		push_error("letterhead_probe: --out=<abs dir> is required")
		get_tree().quit(1)
		return
	DirAccess.make_dir_recursive_absolute(out_dir)
	Settings.path = "user://letterhead_probe_settings.cfg"
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
				for kind in KINDS:
					await _shot(kind, corp, after, k)
	Settings.set_text_scale(was)
	get_tree().quit(0)


func _shot(kind: String, corp: StringName, after: bool, k: float) -> void:
	var doc := _make(kind, corp, after, k)
	add_child(doc)
	doc.position = Vector2(MARGIN, MARGIN) * 3.0
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var sx := float(img.get_width()) / get_viewport().get_visible_rect().size.x
	var r := doc.get_global_rect()
	var top := Rect2(r.position - Vector2(MARGIN, MARGIN), Vector2(r.size.x + MARGIN * 2.0, minf(r.size.y, TOP_H * k) + MARGIN * 2.0))
	var px := Rect2i(Vector2i(top.position * sx), Vector2i(top.size * sx)).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	img.get_region(px).save_png(out_dir.path_join("%s_x%.1f_%s_%s.png" % [kind, k, corp, "after" if after else "before"]))
	print("letterhead_probe: %s x%.1f %s %s" % [kind, k, corp, "after" if after else "before"])
	doc.queue_free()
	await get_tree().process_frame


func _make(kind: String, corp: StringName, after: bool, k: float) -> Control:
	var res := RunManager.lookup().get_content(corp)
	var display := TextDb.t(res, "display_name")
	var letterhead := CorpPaperPanel.letterhead_of(res) if after else ""
	match kind:
		"order":
			var sheet := RaidPaper.new(corp, "COLLECTIONS: FIRST NOTICE", RaidPaper.STAMP_INTERCEPTED, "WO 25-%s-452" % String(RaidSkin.CODES.get(corp, "XX")))
			sheet.paper.letterhead_name = letterhead
			sheet.custom_minimum_size = Vector2(HqLayout.ORDER_WIDTH * HqLayout.words_scale(k), 0.0)
			return sheet
		"memo":
			var memo := CorpMemo.new(display, Palette.corp_color(corp), k, letterhead)
			memo.custom_minimum_size = Vector2(MEMO_W, 0.0)
			var text := Label.new()
			text.text = "TO: ALL TIER LEADS"
			memo.body.add_child(text)
			return memo
	var d := OperativeDossier.new()
	d.show_file({"corp": display, "letterhead": letterhead, "corp_color": Palette.corp_color(corp), "subject": "Vex",
		"class_word": "Runner", "class_id": "runner", "operative_id": "op_vex", "rank": 2, "hp": 20, "max_hp": 24, "ram": 4,
		"wheel": ["A", "B"], "hub": "Core", "deck": 12, "station": ["+1 ICE"]})
	return d
