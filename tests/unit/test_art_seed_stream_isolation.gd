extends GutTest
## NA-02 (spec §12.3.1; contract C3: no RngService stream is read or advanced): golden
## replays. At 3 seeds, the RNG stream states (the run's streams, the campaign's RngService
## streams, the global RNG) after an export equal those after no export, before and after a
## save round trip; exporting changes no saved field; the save version is unchanged and the
## save written before the export loads.

const CITY_CONFIG := "res://content/config/city_config.tres"
const SEEDS: Array[int] = [3, 77, 90210]

var _cfg: CityConfig
var _meridian: CorporationData
var _points: Dictionary
var _city: Dictionary
var _index: Dictionary
var _resolver: CombatResolver


func before_all() -> void:
	_cfg = load(CITY_CONFIG)
	_meridian = ContentRegistry.get_content(&"meridian") as CorporationData
	_points = CityLayout.site_points(_meridian)
	var lo := Vector2i(1 << 30, 1 << 30)
	var hi := -lo
	for id: Variant in _points:
		lo = lo.min(Vector2i((_points[id] as Vector2).floor()))
		hi = hi.max(Vector2i((_points[id] as Vector2).floor()))
	var m := _cfg.art_site_bid_reach_lots + 2
	var model := CityModel.build(_cfg, _cfg.city_seed, Rect2i(lo - Vector2i(m, m), hi - lo + Vector2i(2 * m + 1, 2 * m + 1)))
	_city = NetrunArtExport.city_json(model.city_seed, _cfg.lot_bu, _cfg.district_centre, model.prisms, model.streets,
		model.plazas, model.hqs)
	_index = NetrunArtExport.lot_index(_city["buildings"])
	_resolver = CombatFixture.resolver()


func after_each() -> void:
	NetrunArtExport.sink = Callable()


func _start(run_seed: int, exporting: bool) -> NetrunSession:
	RngService.seed_campaign(run_seed * 31 + 1)
	var c := CampaignRules.new_campaign(_meridian, CombatFixture.config(), GridFixture.lookup(), 3,
		ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	NetrunArtExport.sink = _export if exporting else Callable()
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"m1_a", run_seed, _meridian)
	NetrunArtExport.sink = Callable()
	return s


func _export(s: NetrunSession) -> void:
	var r := NetrunArtExport.export_run(s, _city, _index, _points, _cfg.art_site_bid_reach_lots)
	assert_eq(r["error"], "")


## Every RNG state the game keeps: the run's streams, the campaign streams, and a draw of the
## global RNG from a fixed seed (no global RNG call may happen in between).
func _golden(s: NetrunSession) -> Dictionary:
	return {"run": s.streams.to_dict(), "campaign": RngService.to_dict(), "session": s.state_hash(),
		"campaign_state": s.campaign.state_hash()}


func test_stream_states_identical_with_and_without_export() -> void:
	for run_seed in SEEDS:
		seed(run_seed)
		var plain := _start(run_seed, false)
		var g_plain := _golden(plain)
		var global_plain := randi()
		seed(run_seed)
		var exported := _start(run_seed, true)
		var g_exp := _golden(exported)
		assert_eq(randi(), global_plain, "global RNG untouched (seed %d)" % run_seed)
		assert_eq(g_exp, g_plain, "stream states after export == no export (seed %d)" % run_seed)


func test_identical_across_save_and_reload() -> void:
	for run_seed in SEEDS:
		var plain := _start(run_seed, false)
		var exported := _start(run_seed, true)
		var save_plain := JSON.stringify(plain.to_dict())
		var save_exp := JSON.stringify(exported.to_dict())
		assert_eq(save_exp, save_plain, "the export changes no saved field (seed %d)" % run_seed)
		var camp_plain := JSON.stringify(plain.campaign.to_dict())
		assert_eq(JSON.stringify(exported.campaign.to_dict()), camp_plain, "nor the campaign save")
		# Reload the save written before any export, export from the reloaded run, compare.
		var c1 := CampaignState.from_dict(JSON.parse_string(camp_plain))
		var c2 := CampaignState.from_dict(JSON.parse_string(camp_plain))
		var r1 := NetrunSession.from_dict(_resolver, c1, JSON.parse_string(save_plain), _meridian)
		var r2 := NetrunSession.from_dict(_resolver, c2, JSON.parse_string(save_plain), _meridian)
		assert_not_null(r1, "the pre-export save loads")
		var before := RngService.to_dict()
		_export(r2)
		assert_eq(RngService.to_dict(), before, "campaign streams unchanged by an export after reload")
		assert_eq(r2.streams.to_dict(), r1.streams.to_dict(), "run streams after reload + export == reload (seed %d)" % run_seed)
		assert_eq(r2.state_hash(), r1.state_hash())
		assert_eq(JSON.stringify(r2.to_dict()), JSON.stringify(r1.to_dict()))


func test_save_version_unchanged() -> void:
	assert_eq(SaveService.SAVE_VERSION, 4, "NA-02 adds no save field (N8 moved it to 3, N12 to 4)")
