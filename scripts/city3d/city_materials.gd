class_name CityMaterials
extends RefCounted
## ART-5 5a: the ONE seam between the city and its shaders (bible §1.2 World, §6.1). Every
## city material is made here from CityConfig: the faceted buildings and the ground use the
## city shaders (`shaders/city/`), which take 1B's toon bands and banded light spill from the
## kit include (`shaders/kit/toon_bands.gdshaderinc`; ToonInkMaterial.set_spill feeds them);
## the ink, see-through, bloom, fog, haze, rain and grade are the city's post pass (1D's
## post40 port: a depth / normal ink beats the inverted hull on big city meshes, 1B's note).
## Props, landmarks and HQ compounds use ToonInkMaterial itself. Builders only; a view.

const BUILDING := preload("res://shaders/city/city_building.gdshader")
const GROUND := preload("res://shaders/city/city_ground.gdshader")
const POST := preload("res://shaders/city/city_post.gdshader")
const NETWORK := preload("res://shaders/city/city_network.gdshader")
const NETWORK_XRAY := preload("res://shaders/city/city_network_xray.gdshader")
const MAP_VEIL := preload("res://shaders/city/city_map_veil.gdshader")
## S-MAPVIEW: the map veil's render priority: after the ambient layers (beams 11) and before
## the network decal (19 / 20).
const MAP_VEIL_PRIORITY := 15


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)


## The toon ramp (3 bands) on material `m`.
static func ramp(cfg: CityConfig, m: ShaderMaterial) -> void:
	m.set_shader_parameter("ramp_shadow", _v3(cfg.ramp[0]))
	m.set_shader_parameter("ramp_mid", _v3(cfg.ramp[1]))
	m.set_shader_parameter("ramp_lit", _v3(cfg.ramp[2]))
	m.set_shader_parameter("ramp_edges", cfg.ramp_edges)
	m.set_shader_parameter("spill_mid", ToonInkMaterial.SHADE_MID)
	m.set_shader_parameter("spill_low", ToonInkMaterial.SHADE_LOW)


## The buildings' material: facets, windows, ledges, shopfronts, roof trim in `inks`.
static func building(cfg: CityConfig, inks: Array[Color]) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = BUILDING
	ramp(cfg, m)
	m.set_shader_parameter("tone_min", cfg.tone_min)
	m.set_shader_parameter("tone_max", cfg.tone_max)
	m.set_shader_parameter("roof_gain", cfg.roof_gain)
	var wc: Array[Vector3] = []
	for c in cfg.window_colors:
		wc.append(_v3(c))
	m.set_shader_parameter("window_colors", wc)
	m.set_shader_parameter("window_pitch", cfg.window_pitch)
	m.set_shader_parameter("window_size", cfg.window_size)
	m.set_shader_parameter("window_first", cfg.window_first)
	m.set_shader_parameter("window_share", cfg.window_share)
	m.set_shader_parameter("window_dim_min", cfg.window_dim_min)
	m.set_shader_parameter("window_gain", cfg.window_gain)
	m.set_shader_parameter("trim_bu", cfg.roof_trim_bu)
	m.set_shader_parameter("neon_gain", cfg.neon_gain)
	m.set_shader_parameter("ledge_every", cfg.ledge_every)
	m.set_shader_parameter("ledge_bu", cfg.ledge_bu)
	set_inks(m, inks)
	return m


## The roof-trim ink palette (CityMeshKit.ink_palette, at most 16) on building material `m`.
static func set_inks(m: ShaderMaterial, inks: Array[Color]) -> void:
	var ink_v: Array[Vector3] = []
	for c in inks:
		ink_v.append(_v3(c))
	while ink_v.size() < 16:
		ink_v.append(Vector3.ONE)
	m.set_shader_parameter("ink_colors", ink_v)


## The ground (asphalt, plazas, street lots), or with `lane` the lane glow strips.
static func ground(cfg: CityConfig, lane: bool) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = GROUND
	ramp(cfg, m)
	m.set_shader_parameter("lane", lane)
	return m


## The full-screen post pass (quality tier `q`, CityLod.quality), the see-through ground
## pass texture `ground_tex`.
static func post(cfg: CityConfig, q: Dictionary, ground_tex: Texture2D) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = POST
	m.render_priority = -100
	m.set_shader_parameter("ground_tex", ground_tex)
	m.set_shader_parameter("see_dark", cfg.see_through_dark)
	m.set_shader_parameter("see_chroma", cfg.see_through_chroma)
	m.set_shader_parameter("see_window", cfg.see_through_window_gain)
	m.set_shader_parameter("ink_on", q["ink"])
	m.set_shader_parameter("ink_color", _v3(cfg.ink))
	m.set_shader_parameter("ink_normal_edge", cfg.ink_normal_edge)
	m.set_shader_parameter("ink_depth_edge", cfg.ink_depth_edge)
	m.set_shader_parameter("ink_wobble_px", cfg.ink_wobble_px)
	m.set_shader_parameter("ink_width", cfg.ink_width_px)
	m.set_shader_parameter("rain_density", cfg.rain_density)
	m.set_shader_parameter("cam_distance", cfg.camera_distance)
	m.set_shader_parameter("grime", cfg.grime)
	m.set_shader_parameter("spill", cfg.spill)
	m.set_shader_parameter("bloom", cfg.bloom)
	m.set_shader_parameter("glow_threshold", cfg.glow_threshold)
	m.set_shader_parameter("glow_lod", cfg.glow_mip)
	m.set_shader_parameter("haze_color", _v3(cfg.haze))
	m.set_shader_parameter("haze_k", cfg.haze_k)
	m.set_shader_parameter("fog_on", q["fog"])
	m.set_shader_parameter("fog_color", _v3(cfg.fog))
	m.set_shader_parameter("fog_amount", cfg.fog_amount)
	m.set_shader_parameter("rain_on", q["rain"])
	m.set_shader_parameter("rain_color", _v3(cfg.rain))
	m.set_shader_parameter("rain_alpha", cfg.rain_alpha)
	m.set_shader_parameter("grade", _v3(cfg.grade))
	m.set_shader_parameter("map_saturation", cfg.map_saturation)
	m.set_shader_parameter("map_contrast", cfg.map_contrast)
	m.set_shader_parameter("map_mid", cfg.map_mid)
	m.set_shader_parameter("map_bloom", cfg.map_bloom)
	return m


## S-MAPVIEW: the map mode's veil (a full-screen quad between the city's ambient layers and
## the network decal).
static func map_veil(cfg: CityConfig) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = MAP_VEIL
	m.render_priority = MAP_VEIL_PRIORITY
	m.set_shader_parameter("veil_color", cfg.map_veil)
	m.set_shader_parameter("veil_alpha", cfg.map_veil_alpha)
	return m


## The network decal (`xray`: its pass through buildings, depth test inverted).
static func network(cfg: CityConfig, xray: bool) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = NETWORK_XRAY if xray else NETWORK
	m.render_priority = 20 if xray else 19
	m.set_shader_parameter("trace_px", cfg.net_trace_px)
	m.set_shader_parameter("halo_px", cfg.net_halo_px)
	m.set_shader_parameter("node_px", cfg.net_node_px)
	m.set_shader_parameter("ring_px", cfg.net_ring_px)
	m.set_shader_parameter("bus_gap_px", cfg.net_bus_gap_px)
	m.set_shader_parameter("packet_speed", cfg.net_packet_speed)
	m.set_shader_parameter("packet_gap", cfg.net_packet_gap)
	m.set_shader_parameter("dash_bu", cfg.net_dash_bu)
	m.set_shader_parameter("gain", cfg.net_gain)
	m.set_shader_parameter("halo", cfg.net_halo)
	m.set_shader_parameter("keyline", _v3(cfg.ink))
	return m


## Sets the light spill sources (LightSpill.uniforms_3d input) on the city's materials.
static func set_spill(mats: Array[ShaderMaterial], sources: Array) -> void:
	for m in mats:
		ToonInkMaterial.set_spill(m, sources)
