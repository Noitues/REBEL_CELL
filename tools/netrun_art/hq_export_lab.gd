extends Control
## HQ-EXPORT lab (art-pass A-042; headless is enough, no renderer): writes the HQ plate inputs of each corporation from the game's own
## objects (HqPlateExport) into <out>/hq_<corp>/{hq_compound.json, run_graph.json, hq_overview_capture.json}.
##   godot --headless --path . res://tools/netrun_art/hq_export_lab.tscn -- --out=<dir> [--corps=meridian,solace,...] [--seed=11]
##     [--size=1920x1080] [--reach=24]
## Schema: docs/handoff/netrun_art/plate_inputs/HQ_EXPORT.md. Prints HQEXPORT lines.

const ALL_CORPS := "meridian,solace,halcyon,orbital,rebel_cell"
const VIEW_NAME := "overview"
const REACH_DEFAULT := 24
const HQ_TIER := 4
const RUN_SEED := 5

var _args: Dictionary = {}


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	var out := String(_args.get("out", "user://hq_export"))
	var wh := String(_args.get("size", "1920x1080")).split("x")
	var px := Vector2i(int(wh[0]), int(wh[1]))
	var code := 0
	for corp in String(_args.get("corps", ALL_CORPS)).split(","):
		if not _export_corp(StringName(corp), out, px):
			code = 1
	RunManager.delete_save()
	get_tree().quit(code)


func _export_corp(corp: StringName, out: String, px: Vector2i) -> bool:
	RunManager.save_slot = "lab_hqexport"
	RunManager.new_campaign(int(_args.get("seed", "11")), corp)
	var c := RunManager.campaign
	var cd := RunManager.corporation
	var site: StringName = &""
	for sd in cd.city_grid.sites:
		if sd != null and sd.objective == RC.SiteObjective.CENTRAL_SERVER:
			site = sd.id
	var s := NetrunSession.start_special(RunManager.resolver, c, c.living_operatives()[0].id, "boss", site, HQ_TIER, RUN_SEED, cd.final_boss.id,
		CampaignRules.boss_overrides(c, cd), cd)
	var v := HqRunView.new()
	v.size = Vector2(px)
	add_child(v)
	v.show_run(corp, s.run.map, &"", [], s.available_nodes(), HqCompoundStage.server_name(HqCompoundStage.manifest(corp)))
	var cfg := CityView3D.CONFIG
	var model := CityModel.shared(cfg, CityPlan.current_seed())
	var files := HqPlateExport.files(corp, v, model, cfg, px, int(_args.get("reach", str(REACH_DEFAULT))), VIEW_NAME,
		"hq_%s_%s" % [corp, str(_args.get("seed", "11"))])
	var dir := "%s/hq_%s" % [out, corp]
	DirAccess.make_dir_recursive_absolute(dir)
	for fn: String in files:
		var f := FileAccess.open("%s/%s" % [dir, fn], FileAccess.WRITE)
		if f == null:
			print("HQEXPORT FAIL cannot write ", dir, "/", fn)
			return false
		f.store_buffer(String(files[fn]).to_utf8_buffer())
		f.close()
	print("HQEXPORT ", corp, " -> ", dir, " parts ", (JSON.parse_string(files["hq_compound.json"]) as Dictionary)["parts"].size())
	v.queue_free()
	return true
