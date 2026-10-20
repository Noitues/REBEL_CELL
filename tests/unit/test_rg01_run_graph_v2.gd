extends GutTest
## RG-01 / RG-06: run_graph v2. The contract version is 2 and the schema takes the new kinds; a seed
## gives byte-identical JSON; a v1 call of the generator is unchanged; v2 kinds exist only in v2
## graphs; the lint rejects Intel, Relay and Ambush nodes unless allow-listed.

const SchemaCheck := preload("res://tools/netrun_art/schema_check.gd")
const SEEDS := 200

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = CombatFixture.config()


func _gen(seed: int, v2: bool, tier: int = 2) -> MapGraph:
	return MapGenerator.generate(tier, _cfg, RngStreams.make_stream(seed, &"map"), 0.0, v2)


func test_run_graph_json_is_v2_and_valid_against_the_schema() -> void:
	for seed in 20:
		var d := NetrunArtExport.run_graph_json(_gen(seed, true), "r")
		assert_eq(d["version"], 2)
		var parsed: Dictionary = JSON.parse_string(NetrunArtExport.canonical(d))
		assert_eq(SchemaCheck.validate(parsed, SchemaCheck.schema("run_graph")).size(), 0, "seed %d" % seed)


func test_same_seed_is_byte_identical_json() -> void:
	for seed in 50:
		var a := NetrunArtExport.canonical(NetrunArtExport.run_graph_json(_gen(seed, true), "r"))
		var b := NetrunArtExport.canonical(NetrunArtExport.run_graph_json(_gen(seed, true), "r"))
		assert_eq(a, b, "seed %d" % seed)


func test_v1_call_is_unchanged_and_carries_no_version_key() -> void:
	for seed in 50:
		var g := _gen(seed, false)
		assert_eq(g.version, 1)
		assert_false(g.to_dict().has("version"), "v1 hashes as before")
		for n in g.all_nodes():
			assert_lt(int(n["type"]), RC.InfilNodeType.REST, "no v2 kind in a v1 graph")
		assert_eq(g.graph_hash(), _gen(seed, false).graph_hash())


func test_v2_graphs_validate_and_round_trip() -> void:
	for seed in SEEDS:
		var g := _gen(seed, true, 1 + seed % 4)
		assert_eq(g.version, 2)
		assert_true(g.validate(_cfg).is_empty(), "seed %d: %s" % [seed, g.validate(_cfg)])
		assert_eq(MapGraph.from_dict(g.to_dict()).graph_hash(), g.graph_hash())


func test_a_v2_kind_in_a_v1_graph_is_invalid() -> void:
	var g := _gen(3, false)
	var t: Dictionary = MapV2.terminals(g, 2, 6)[0]
	t["type"] = RC.InfilNodeType.REST
	assert_false(g.validate(_cfg).is_empty())
	g.version = 2
	assert_true(g.validate(_cfg).is_empty(), "the same node is fine in a v2 graph")


func test_lint_rejects_intel_relay_ambush_unless_allow_listed() -> void:
	var g := _gen(5, true)
	assert_true(g.lint(_cfg.map_unique_allow).is_empty(), "a normal map has none")
	var n: Dictionary = MapV2.terminals(g, 2, 6)[0]
	for kind in ["intel", "relay", "ambush"]:
		n["unique_kind"] = kind
		n["unique_id"] = "somewhere_else"
		assert_eq(g.lint(_cfg.map_unique_allow).size(), 1, kind)
	n["unique_kind"] = "relay"
	n["unique_id"] = "orbital_uplink_dish"
	assert_true(g.lint(_cfg.map_unique_allow).is_empty(), "the Orbital Uplink Dish is allow-listed")
	assert_true(MapGraph.from_dict(g.to_dict()).get_node(n["id"]).has("unique_kind"), "the unique keys are saved")


func test_normal_maps_pass_the_lint_over_many_seeds() -> void:
	for seed in SEEDS:
		assert_true(_gen(seed, true, 1 + seed % 4).lint(_cfg.map_unique_allow).is_empty(), "seed %d" % seed)
