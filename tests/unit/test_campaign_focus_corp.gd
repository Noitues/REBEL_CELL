extends GutTest
## Solace vertical: `campaign_focus_corp` (config, "" = all corporations). Off leaves campaign state
## byte-identical; on yields only the focus corporation wherever the corp is chosen.

var _cfg: CampaignConfigData
var _focus_cfg: CampaignConfigData
var _lookup: ContentLookup
var _breaker: ClassData


func before_all() -> void:
	_cfg = CombatFixture.config()
	_focus_cfg = _cfg.duplicate() as CampaignConfigData   # never edit the loaded resource
	_focus_cfg.campaign_focus_corp = &"solace"
	_lookup = GridFixture.lookup()
	_breaker = ContentRegistry.get_content(&"breaker") as ClassData


func test_shipped_default_is_off() -> void:
	assert_eq(_cfg.campaign_focus_corp, &"")


func test_focus_off_returns_the_request_for_every_corp() -> void:
	for id in [&"solace", &"meridian", &"halcyon", &"nope"]:
		assert_eq(CampaignRules.focused_corporation_id(_cfg, _lookup, id), id)


func test_focus_on_forces_the_focus_corp() -> void:
	for id in [&"solace", &"meridian", &"halcyon"]:
		assert_eq(CampaignRules.focused_corporation_id(_focus_cfg, _lookup, id), &"solace")


func test_unknown_focus_falls_back_to_the_request() -> void:
	var c := _cfg.duplicate() as CampaignConfigData
	c.campaign_focus_corp = &"no_such_corp"
	assert_eq(CampaignRules.focused_corporation_id(c, _lookup, &"meridian"), &"meridian")
	assert_eq(CampaignRules.available_corporations(ProfileState.new(), _lookup, c).size(), CampaignRules.available_corporations(ProfileState.new(), _lookup).size())


func test_focus_off_campaign_state_is_byte_identical() -> void:
	for corp_id in [&"solace", &"meridian"]:
		var corp := ContentRegistry.get_content(corp_id) as CorporationData
		var direct := CampaignRules.new_campaign(corp, _cfg, _lookup, 7, _breaker, GridFixture.home_node())
		var focus_id := CampaignRules.focused_corporation_id(_cfg, _lookup, corp_id)
		var via := CampaignRules.new_campaign(ContentRegistry.get_content(focus_id) as CorporationData, _cfg, _lookup, 7, _breaker, GridFixture.home_node())
		assert_eq(JSON.stringify(via.to_dict(), "", true), JSON.stringify(direct.to_dict(), "", true), String(corp_id))


func test_focus_on_picker_lists_only_solace_even_with_unlocks() -> void:
	var profile := ProfileState.new()
	var ids := []
	for c in CampaignRules.available_corporations(profile, _lookup, _focus_cfg):
		ids.append(c.id)
	assert_eq(ids, [&"solace"])


func test_focus_on_grid_is_solace_only() -> void:
	var id := CampaignRules.focused_corporation_id(_focus_cfg, _lookup, &"meridian")
	var corp := ContentRegistry.get_content(id) as CorporationData
	var c := CampaignRules.new_campaign(corp, _focus_cfg, _lookup, 7, _breaker, GridFixture.home_node())
	assert_eq(c.corporation_id, &"solace")
	assert_eq(c.grid.sites.size(), (ContentRegistry.get_content(&"solace") as CorporationData).city_grid.sites.size())
	for s in CampaignRules.launchable_sites(c, corp, _focus_cfg):
		assert_true(corp.city_grid.get_site(s.id) != null)


func test_simulator_with_focus_plays_solace_content() -> void:
	var sim := CampaignSimulator.new(CombatResolver.new(_focus_cfg, ContentLookup.new().add_registry(ContentRegistry)), &"meridian")
	assert_eq(sim.corp.id, &"solace")
	var off := CampaignSimulator.new(CombatResolver.new(_cfg, ContentLookup.new().add_registry(ContentRegistry)), &"meridian")
	assert_eq(off.corp.id, &"meridian")
