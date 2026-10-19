extends Node
## NA-23b tool: derive the street on the game's own city for every corporation x campaign seed x launchable Site, print the
## result and write the derive inputs (`city`, `net`, `run_graph`, `site`) so the Python oracle can run on the same world.
##   godot --headless --path . res://tools/netrun_art/dump_game_worlds.tscn -- --out=<dir> [--seeds=1,2,3,4] [--corps=meridian,...]
## Prints `NA23B <corp> <seed> <site> layers=<n> ok span=<n> | ERROR <message>` lines.


func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			args[kv[0]] = kv[1]
	var out_dir := String(args.get("out", ""))
	var seeds := String(args.get("seeds", "1,2,3,4")).split(",")
	var corps := String(args.get("corps", "halcyon,meridian,orbital,rebel_cell,solace")).split(",")
	if out_dir != "":
		DirAccess.make_dir_recursive_absolute(out_dir)
	var rm: Node = RunManager
	rm.save_slot = "dump_game_worlds"
	rm.scene_switching_enabled = false
	rm.profile = null   # no profile: every corporation is available
	for corp in corps:
		for s in seeds:
			rm.new_campaign(int(s), StringName(corp))
			var got := String(rm.corporation.id)
			var site_ids: Array = []
			for site: SiteData in rm.launchable_sites():
				site_ids.append(site.id)
			for sid: StringName in site_ids:
				rm.netrun = null
				var session: NetrunSession = rm.start_run(&"", sid)
				if session == null:
					print("NA23B %s %s %s no run" % [corp, s, sid])
					continue
				var cfg := CityView3D.CONFIG
				var cseed := int(args.get("city", str(cfg.city_seed)))
				var data: StreetRouteData = StreetRouteData.build(session, CityModel.shared(cfg, cseed), cfg, CityLayout.site_points(rm.corporation))
				var layers := 0
				for n: Dictionary in data.run_graph.get("nodes", []):
					layers = maxi(layers, int(n["layer"]))
				print("NA23B %s(%s) seed=%s city=%d %s layers=%d %s" % [corp, got, s, cseed, sid, layers,
					"ERROR " + data.error if data.error != "" else "ok span=%s" % data.derive.get("span")])
				if out_dir != "" and not data.city.is_empty():
					var w := {"city": data.city, "net": data.net, "run_graph": data.run_graph, "site": String(sid), "corp": got, "seed": s}
					var f := FileAccess.open("%s/%s_c%d_%s_%s.json" % [out_dir, corp, cseed, s, sid], FileAccess.WRITE)
					f.store_string(JSON.stringify(w))
					f.close()
	get_tree().quit(0)
