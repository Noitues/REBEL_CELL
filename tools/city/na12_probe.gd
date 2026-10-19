extends SceneTree
## NA-12 probe (headless): tallies why the city generator's single attempts fail over N seeds.
##   godot --headless --path . -s tools/city/na12_probe.gd -- [--seeds=300] [--corps=a,b] [--full=1 (whole generations)]
## Prints NA12PROBE lines: attempts, passes, and each failure reason's count.


func _init() -> void:
	var n := 300
	var extra: Array = []
	var full := false
	for a in OS.get_cmdline_user_args():
		if a == "--full=1":
			full = true
		if a.begins_with("--seeds="):
			n = int(a.trim_prefix("--seeds="))
		elif a.begins_with("--corps="):
			for c in a.trim_prefix("--corps=").split(",", false):
				extra.append(StringName(c))
	var cfg: CampaignConfigData = load(CityPlan.FIXED_CONFIG_PATH)
	var ids: Array = []
	for t in NeonCity.TERRITORIES:
		if t["id"] != &"":
			ids.append(t["id"])
	ids.append_array(extra)
	IdSort.sort_ids(ids)
	var tally := {}
	var passes := 0
	for s in n:
		var rng := RngStreams.make_stream(s * 7919 + 13, RngStreams.CITY_LAYOUT_STREAM)
		var p: CityPlan
		if full:
			p = CityGenerator.generate(rng, cfg, CityView3D.CONFIG.city_rect, ids, NeonCity.FIST_TERRITORY, NeonCity.HQ_LOTS,
				CityPlan.site_frame())
		else:
			p = CityGenerator._attempt(rng, cfg, CityView3D.CONFIG.city_rect, ids, NeonCity.FIST_TERRITORY, NeonCity.HQ_LOTS,
				CityPlan.site_frame())
		if p.fallback:
			var key := p.failure.split(" ")[0] + " " + " ".join(p.failure.split(" ").slice(1)) if p.failure != "" else "?"
			tally[key] = int(tally.get(key, 0)) + 1
		else:
			passes += 1
	print("NA12PROBE attempts=%d passes=%d" % [n, passes])
	var keys: Array = tally.keys()
	keys.sort()
	for k: String in keys:
		print("NA12PROBE %4d  %s" % [tally[k], k])
	quit(0)
