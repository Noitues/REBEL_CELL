class_name CityHeatRig
extends RefCounted
## ART-5 5c: where the city's Heat and suspicion lights stand (ART_BIBLE §4.3, §2.8; round 37
## calm Heat B; round 24 `make_heat.py`; round 6 suspicion). Pure placement, deterministic:
## - every hardened node (one Heat has made harder) gets one soft circling light on a thin
##   HEAT_B ring, alternating red and blue by node;
## - the band's look (COOL, NOTICED, FLAGGED, HUNTED; PURGE takes HUNTED's, designer ruling
##   2026-10-05) sets the rig round the hardened nodes' centre (home when none): searchlights
##   and alarm beacons on roofs, police strobes on street corners, choppers and drones
##   circling with spotlights;
## - suspicion (round 6) puts its own police, choppers and drones round the Cell's home.
## Picks spread round the centre (anchor directions), nearest roof / street to each anchor,
## ties by building key then lot; phases from the index (golden-ratio spread), no RNG.

enum Band { COOL, NOTICED, FLAGGED, HUNTED, PURGE }
const GOLDEN := 0.61803398875

var node_lights: Array[Dictionary] = []
var searchlights: Array[Dictionary] = []
var alarms: Array[Dictionary] = []
var police: Array[Dictionary] = []
var choppers: Array[Dictionary] = []
var drones: Array[Dictionary] = []
var centre: Vector3 = Vector3.ZERO
var look: int = Band.COOL


## The look of Heat band `band`: PURGE uses HUNTED's until it is designed.
static func look_of(band: int) -> int:
	return clampi(band, Band.COOL, Band.HUNTED)


## The rig for Heat band `band`, the hardened nodes at `hardened` (world, in node-id order)
## and suspicion on or off.
static func build(cfg: CityMotionConfigData, site: CityMotionSite, band: int, hardened: Array[Vector3],
		suspicion: bool) -> CityHeatRig:
	var r := CityHeatRig.new()
	r.look = look_of(band)
	for k in hardened.size():
		r.node_lights.append({"pos": hardened[k], "blue": k % 2 == 1, "phase": fposmod(k * GOLDEN, 1.0)})
	r.centre = site.home
	if not hardened.is_empty():
		var c := Vector3.ZERO
		for p in hardened:
			c += p
		r.centre = Vector3(c.x, 0.0, c.z) / float(hardened.size())
	var used: Array[Vector3] = []
	var b := r.look
	for p in _roofs(cfg, site, r.centre, cfg.band_searchlights[b], cfg.searchlight_min_roof, 0.0, used):
		r.searchlights.append({"pos": p, "phase": fposmod(r.searchlights.size() * GOLDEN, 1.0),
			"yaw": TAU * r.searchlights.size() / maxf(1.0, cfg.band_searchlights[b]), "alpha": cfg.band_searchlight_alpha[b]})
	for p in _roofs(cfg, site, r.centre, cfg.band_alarms[b], 0.0, 0.5, used):
		r.alarms.append({"pos": p, "phase": fposmod(r.alarms.size() * GOLDEN, 1.0)})
	r._air(cfg, site, r.centre, cfg.band_police[b], cfg.band_choppers[b], cfg.band_drones[b])
	if suspicion:
		r._air(cfg, site, site.home, cfg.suspicion_police, cfg.suspicion_choppers, cfg.suspicion_drones)
	return r


## Police strobes, choppers and drones round `c`.
func _air(cfg: CityMotionConfigData, site: CityMotionSite, c: Vector3, n_police: int, n_choppers: int, n_drones: int) -> void:
	for p in _streets(cfg, site, c, n_police):
		police.append({"pos": p, "phase": fposmod(police.size() * GOLDEN, 1.0)})
	var orbit := cfg.chopper_orbit
	for k in n_choppers:
		var ang := TAU * float(k) / float(n_choppers)
		var off := Vector3(cos(ang), 0.0, sin(ang)) * orbit * 0.6 * float(k % 2)
		choppers.append({"centre": c + off, "radius": orbit * (1.0 - 0.3 * float(k % 2)), "dir": 1.0 if k % 2 == 0 else -1.0,
			"phase": fposmod(k * GOLDEN, 1.0)})
	var cols := maxi(1, int(ceil(sqrt(float(n_drones)))))
	for k in n_drones:
		var gx := float(k % cols) - float(cols - 1) * 0.5
		var gz := float(k / cols) - float(cols - 1) * 0.5
		var p := c + Vector3(gx, 0.0, gz) * cfg.drone_orbit * 3.0
		drones.append({"centre": p, "dir": 1.0 if k % 2 == 1 else -1.0, "phase": fposmod(k * GOLDEN, 1.0)})


## `n` roof points spread round `c` (anchors at angle k / n, `rig_radius_lots` * (0.45 +
## `ring` * 0.3) out), each the nearest roof at least `min_h` high and `rig_spacing_lots`
## from a pick in `used` (which it extends). Ties by building key.
static func _roofs(cfg: CityMotionConfigData, site: CityMotionSite, c: Vector3, n: int, min_h: float, ring: float,
		used: Array[Vector3]) -> Array[Vector3]:
	var out: Array[Vector3] = []
	var reach := cfg.rig_radius_lots * site.lot_bu
	var space := cfg.rig_spacing_lots * site.lot_bu
	for k in n:
		var ang := TAU * (float(k) + ring) / float(n)
		var anchor := c + Vector3(cos(ang), 0.0, sin(ang)) * reach * (0.45 + ring * 0.3)
		var best := -1
		var best_d := INF
		for i in site.roofs.size():
			var rf: Dictionary = site.roofs[i]
			var p: Vector3 = rf["pos"]
			if float(rf["h"]) < min_h or Vector2(p.x - c.x, p.z - c.z).length() > reach:
				continue
			var far := true
			for u in used:
				if Vector2(p.x - u.x, p.z - u.z).length() < space:
					far = false
					break
			if not far:
				continue
			var d := Vector2(p.x - anchor.x, p.z - anchor.z).length()
			if d < best_d:
				best_d = d
				best = i
		if best >= 0:
			var p: Vector3 = site.roofs[best]["pos"]
			out.append(p)
			used.append(p)
	return out


## `n` street points round `c` (corners first), spread like `_roofs`. Ties by lot.
static func _streets(cfg: CityMotionConfigData, site: CityMotionSite, c: Vector3, n: int) -> Array[Vector3]:
	var out: Array[Vector3] = []
	var reach := cfg.rig_radius_lots * site.lot_bu
	var space := cfg.rig_spacing_lots * site.lot_bu * 0.5
	for k in n:
		var ang := TAU * float(k) * GOLDEN
		var rad := reach * (0.25 + 0.6 * fposmod(float(k) * GOLDEN * 3.0, 1.0))
		var anchor := c + Vector3(cos(ang), 0.0, sin(ang)) * rad
		var best := -1
		var best_d := INF
		for i in site.streets.size():
			var st: Dictionary = site.streets[i]
			var l: Vector2i = st["lot"]
			var p := site.lot_to_world(Vector2(l) + Vector2(0.5, 0.5))
			if Vector2(p.x - c.x, p.z - c.z).length() > reach:
				continue
			var far := true
			for u in out:
				if Vector2(p.x - u.x, p.z - u.z).length() < space:
					far = false
					break
			if not far:
				continue
			# Corners first: a street lot that is no corner counts as half a lot further.
			var d := Vector2(p.x - anchor.x, p.z - anchor.z).length() + (0.0 if bool(st["corner"]) else site.lot_bu * 0.5)
			if d < best_d:
				best_d = d
				best = i
		if best >= 0:
			var l: Vector2i = site.streets[best]["lot"]
			out.append(site.lot_to_world(Vector2(l) + Vector2(0.5, 0.5)))
	return out


## Every placed light as a comparable list (tests: PURGE == HUNTED, same input same rig).
func signature() -> Array:
	return [look, node_lights.size(), searchlights, alarms, police, choppers, drones]
