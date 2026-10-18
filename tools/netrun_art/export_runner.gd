extends RefCounted
## NA-02: the body of tools/netrun_art/export_contract.gd, loaded once the autoloads exist
## (a `-s` script cannot name an autoload at compile time).

const CITY_CONFIG := "res://content/config/city_config.tres"
const CAMPAIGN_CONFIG := "res://content/config/campaign_config.tres"

var _args: PackedStringArray = PackedStringArray()


## Writes the files; returns the exit code.
func run(args: PackedStringArray) -> int:
	_args = args
	return _run()


func _arg(name: String, fallback: String) -> String:
	for a in _args:
		if a.begins_with("--%s=" % name):
			return a.substr(name.length() + 3)
	return fallback


func _run() -> int:
	var cfg: CityConfig = load(CITY_CONFIG)
	var city_seed := int(_arg("city-seed", str(cfg.city_seed)))
	var out_dir := _arg("out", OS.get_environment("TEMP").path_join("netrun_art"))
	DirAccess.make_dir_recursive_absolute(out_dir)
	var t0 := Time.get_ticks_usec()
	var model := CityModel.build(cfg, city_seed)
	var t1 := Time.get_ticks_usec()
	var conflicts := NetrunArtExport.bid_conflicts(model.prisms)
	if not conflicts.is_empty():
		push_error("export_contract: building id collisions: %s" % str(conflicts))
		return 1
	var city := NetrunArtExport.city_json(model.city_seed, cfg.lot_bu, cfg.district_centre, model.prisms, model.streets,
		model.plazas, model.hqs)
	var city_text := NetrunArtExport.canonical(city)
	var index := NetrunArtExport.lot_index(city["buildings"])
	var t2 := Time.get_ticks_usec()
	if not _write(out_dir.path_join("city.json"), city_text):
		return 1
	var corp := ContentRegistry.get_content(StringName(_arg("corp", "meridian"))) as CorporationData
	if corp == null or corp.city_grid == null:
		push_error("export_contract: no corporation Grid '%s'." % _arg("corp", "meridian"))
		return 1
	var points := CityLayout.site_points(corp)
	var cc: CampaignConfigData = load(CAMPAIGN_CONFIG)
	var lookup := ContentLookup.new().add_registry(ContentRegistry)
	var home := (ContentRegistry.get_content(&"home_standard") as HomeServerVariantData).core
	var campaign := CampaignRules.new_campaign(corp, cc, lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, home)
	var site_id: StringName = corp.city_grid.get_site(corp.city_grid.home_site_id).links[0]
	var result := {}
	var run_us := [0]
	NetrunArtExport.sink = func(s: NetrunSession) -> void:
		var a := Time.get_ticks_usec()
		result.merge(NetrunArtExport.export_run(s, city, index, points, cfg.art_site_bid_reach_lots))
		run_us[0] = Time.get_ticks_usec() - a
	NetrunSession.start(CombatResolver.new(cc, lookup), campaign, campaign.roster[0].id, int(_arg("tier", "1")), site_id,
		int(_arg("run-seed", "5")), corp)
	NetrunArtExport.sink = Callable()
	if result.is_empty() or result["error"] != "":
		push_error("export_contract: %s" % result.get("error", "the hook did not run"))
		return 1
	var files: Dictionary = result["files"]
	for name: String in files:
		if not _write(out_dir.path_join(name), files[name]):
			return 1
	print("NA-02 export: %s (%d buildings, %d Sites of %s)" % [out_dir, city["buildings"].size(), corp.city_grid.sites.size(), corp.id])
	print("  city build %.1f ms; city.json + lot index %.1f ms; run files (exporter, hook) %.2f ms" % [
		(t1 - t0) / 1000.0, (t2 - t1) / 1000.0, run_us[0] / 1000.0])
	return 0


func _write(path: String, text: String) -> bool:
	var f := FileAccess.open(path, FileAccess.WRITE)
	if f == null:
		push_error("export_contract: cannot write %s." % path)
		return false
	f.store_buffer(text.to_utf8_buffer())
	return true
