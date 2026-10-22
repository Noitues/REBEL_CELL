extends GutTest
## LOOK Solace HQ: the aaa2 compound's state (look blend held at 1, ink and grain off, the whole-city night look, the HQ-page gains)
## belongs to the staged HQ page alone. The combat backdrop (set_night_share) reached without unstage_compound must see the toon
## day it always had: the view equals one that never staged. Headless: the renderer-free state of the view's materials.

const CFG: CityConfig = preload("res://content/config/city_config.tres")
const CORP := &"solace"
## What the aaa2 page overrides on the building material.
const PAGE_KEYS: Array[StringName] = [&"look_blend", &"kit_dark", &"kit_band_k", &"hq_pool", &"hq_pool_col", &"win_emit", &"win_share",
	&"terr_win_k", &"terr_wall_emit", &"pbr_spec_k", &"haze_col", &"window_colors"]
## Plus what the backdrop's day look sets.
const DAY_KEYS: Array[StringName] = [&"window_gain", &"ramp_shadow", &"ramp_mid", &"ramp_lit"]
const POST_KEYS: Array[StringName] = [&"aaa_on", &"ink_fade", &"fog_amount"]


func _view() -> CityView3D:
	var v := CityView3D.new()
	v.size = Vector2i(160, 90)
	v.use_model(CityModel.build(CFG, 7, Rect2i(20, -4, 6, 6)))
	add_child_autofree(v)
	return v


## A view that never staged, its netrun setup done as in any view that has had a look blend.
func _control() -> CityView3D:
	var v := _view()
	v.set_look_blend(0.0)
	return v


## Stages the compound as run_solace does (headless draws no glTF: a bare node stands in for it).
func _stage_solace(v: CityView3D) -> void:
	var m := HqCompoundStage.manifest(CORP)
	var at := HqCompoundStage.place(CFG, CORP, m)
	v.stage_compound(CORP)
	var node := Node3D.new()
	v.add_child(node)
	v._enter_aaa_page(CORP, node, at)


func _backdrop_look(v: CityView3D) -> void:
	v.set_night_share(0.0, BackdropCatalog.city_look(CFG, "hq"))  # CombatBackdrop._light_city


## The shaders' own defaults of what a view that never staged has not set (the headless renderer reports no default).
const SHADER_DEFAULT := {&"kit_dark": 1.0, &"kit_band_k": 1.0, &"hq_pool": Vector4(), &"hq_pool_col": Vector3(), &"terr_win_k": 0.0, &"terr_wall_emit": 0.0}


## A building parameter: the set value, else the shader's default.
func _param(v: CityView3D, k: StringName) -> Variant:
	var x: Variant = v._building_mat.get_shader_parameter(k)
	return x if x != null else SHADER_DEFAULT.get(k)


func _same(v: CityView3D, c: CityView3D, keys: Array[StringName]) -> void:
	for k in keys:
		assert_eq(_param(v, k), _param(c, k), "building %s as a view that never staged" % k)


func test_the_staged_page_holds_the_aaa2_state() -> void:
	var v := _view()
	_stage_solace(v)
	assert_eq(v.look_blend, 1.0, "the page holds the look blend at 1")
	assert_true(v.whole_look, "the whole-city look is on")
	assert_eq(float(v._post.get_shader_parameter(&"ink_fade")), 1.0, "ink off")
	assert_eq(v._building_mat.get_shader_parameter(&"kit_dark"), CFG.hq_page_kit_dark, "the HQ-page gains")
	v.set_look_blend(0.0)
	assert_eq(v.look_blend, 1.0, "still held at 1")


func test_the_backdrop_after_run_solace_without_unstage_sees_toon_day() -> void:
	var v := _view()
	var control := _control()
	_backdrop_look(control)
	_stage_solace(v)
	_backdrop_look(v)
	assert_eq(v.look_blend, 0.0, "look blend back to toon day")
	assert_false(v.whole_look, "no whole-city night look")
	assert_true(v._compound_aaa.is_empty(), "the aaa2 state is cleared")
	assert_eq(v._hq_pool_at, Vector3.INF)
	assert_true(v._compound_fog.is_empty())
	assert_eq(v._aaa_exposure, control._aaa_exposure, "the exposure is the view's own")
	assert_eq(float(v._post.get_shader_parameter(&"ink_fade")), 0.0, "the ink fade is the toon day's (look blend 0)")
	for k in POST_KEYS:
		assert_eq(v._post.get_shader_parameter(k), control._post.get_shader_parameter(k), "post %s as a view that never staged" % k)
	_same(v, control, PAGE_KEYS)
	_same(v, control, DAY_KEYS)
	assert_eq(v._lane_mat.get_shader_parameter(&"lane_gain"), control._lane_mat.get_shader_parameter(&"lane_gain"), "the highways' gain")
	if v._glow_line_mat != null:
		assert_eq(v._glow_line_mat.get_shader_parameter(&"gain"), control._glow_line_mat.get_shader_parameter(&"gain"), "the road glow gain")


func test_a_later_look_blend_is_not_held_after_the_backdrop_took_the_view() -> void:
	var v := _view()
	_stage_solace(v)
	_backdrop_look(v)
	v.set_look_blend(0.0)
	assert_eq(v.look_blend, 0.0)
	v.unstage_compound(CORP)  # the late unstage stays harmless
	assert_eq(v.look_blend, 0.0)
	assert_false(v.compounds.has(CORP))


func test_unstage_gives_the_view_back_as_before() -> void:
	var v := _view()
	var control := _control()
	_stage_solace(v)
	v.unstage_compound(CORP)
	_same(v, control, PAGE_KEYS)
	assert_eq(v.look_blend, 0.0)
	assert_false(v.whole_look)
