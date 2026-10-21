extends GutTest
## Q8: the launch menu the strategist reads. A Heat sink Site cuts Heat once; its repeat is a patrol
## (no objective), so the menu must say 0, else a policy farms a spent sink while Heat climbs.

const AgentSim := preload("res://tools/agent/agent_simulator.gd")

var _corp: CorporationData
var _c: CampaignState


func before_each() -> void:
	_corp = ContentRegistry.get_content(&"solace") as CorporationData
	_c = CampaignRules.new_campaign(_corp, CombatFixture.config(), GridFixture.lookup(), 7, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())


func test_a_fresh_heat_sink_reports_its_cut_and_a_cleared_one_reports_none() -> void:
	var sink := _corp.city_grid.get_site(&"scrub_records")
	assert_lt(sink.heat_change, 0)
	var fresh := AgentSim.launch_meta(_c, sink, 3)
	assert_eq(fresh["heat_change"], sink.heat_change)
	assert_eq(fresh["objective"], RC.SiteObjective.HEAT_REDUCTION)
	assert_false(fresh["patrol"])
	_c.grid.sites[sink.id]["status"] = GridState.SiteStatus.CLEARED
	var spent := AgentSim.launch_meta(_c, sink, 3)
	assert_true(spent["patrol"])
	assert_eq(spent["heat_change"], 0)
	assert_eq(spent["objective"], RC.SiteObjective.NONE)
	assert_eq(spent["op_rank"], 3)


func test_other_sites_report_no_heat_change() -> void:
	var m := AgentSim.launch_meta(_c, _corp.city_grid.get_site(&"t1_a"), 0)
	assert_eq(m["heat_change"], 0)
	assert_eq(m["tier"], 1)
