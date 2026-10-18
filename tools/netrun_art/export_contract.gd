extends SceneTree
## NA-02: writes the netrun-art data contract v1 for one city seed and one netrun, headless:
##   godot --headless --path . -s tools/netrun_art/export_contract.gd -- [--corp=meridian]
##       [--run-seed=5] [--tier=1] [--city-seed=<CityConfig.city_seed>] [--out=<dir>]
## Output (default %TEMP%/netrun_art): city.json (a FULL-city CityModel build), net.json,
## run_graph.json, key_locations.json, derive_<run>.json. The run files come from the
## NetrunSession.start hook (NetrunArtExport.sink), so the game's own start path is exercised.
## Prints the measured times. Exit 0 on success.

const RUNNER := "res://tools/netrun_art/export_runner.gd"

var _done := false


func _process(_delta: float) -> bool:
	if _done:
		return true
	_done = true
	var runner: RefCounted = (load(RUNNER) as GDScript).new()
	quit(runner.call(&"run", OS.get_cmdline_user_args()))
	return true
