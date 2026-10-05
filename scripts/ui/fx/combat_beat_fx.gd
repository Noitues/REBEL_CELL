class_name CombatBeatFx
extends RefCounted
## ART-2 2C (ART_BIBLE v2 §3.20): which locked effect a replay beat plays, and where. The
## combat scene calls `play` once per beat (one line in its `_play_beat`); this reads the
## wheels' public geometry (centre, rim, HP ring, slices, satellites) and calls the FX
## layer. View only: it never changes state; scatter is hashed, never an RNG.
##
## D16 (plan default, pending the designer): a card-caused beat's effect leaves from the
## card's slap point on its target wheel (CardFx.origin), never from the hand.

## The HP arc's place round the wheel (rad, y down: from the lower right, frac 0, to the
## lower left, frac 1). Mirrors WheelView.hp_ring_spot (2A owns the wheel; a public
## `hp_arc_spot(frac)` there would replace this).
const HP_ARC_FROM := PI * 0.1
const HP_ARC_SPAN := PI * 0.8
## The drained (or healed) arc's segment points a stream feeds.
const ARC_TARGETS := 6
## The evade token sits on the rim facing the foe, this share of the radius out.
const TOKEN_OUT := 1.12


## Plays beat `b`'s effect: `tv` is the wheel it lands on (host of a satellite target),
## `player` and `target` the operative's and the targeted enemy's wheels (who faces whom),
## `src_spot` the resolving slice or needle (Vector2.INF when none), `on_host` whether the
## target is the wheel itself (not a docked satellite), `impact` when a hit arrives (s from
## now), `color` the attacker's colour.
static func play(fx: CombatFxLayer, b: Dictionary, tv: WheelView, player: WheelView, target: WheelView, src_spot: Vector2,
		on_host: bool, impact: float, color: Color) -> void:
	if fx == null or tv == null or tv.combatant == null:
		return
	var kind := String(b.get("kind", ""))
	var center := tv.global_center()
	var r := tv.disc_radius()
	var origin := CardFx.origin(b, fx.slap_point, src_spot if src_spot != Vector2.INF else center)
	var foe := target if tv == player else player
	var foe_at := foe.global_center() if foe != null and foe != tv else center + Vector2.LEFT * r
	match kind:
		"damage":
			var amount := int(b.get("amount", 0))
			var hp_after := int(b.get("hp_after", -1))
			var blocked := int(b.get("blocked", 0)) + int(b.get("shielded", 0)) > 0
			var hit_at := tv.hp_ring_spot() if on_host else tv.satellite_spot(StringName(String(b.get("target", ""))))
			var targets: Array[Vector2] = [hit_at]
			if on_host and src_spot != Vector2.INF and src_spot.distance_to(center) > 1.0:
				# The shards burst where the hit strikes the rim (facing the attacker) and curve
				# round it into the HP arc.
				hit_at = center + (src_spot - center).normalized() * r
			if on_host and hp_after >= 0 and amount > 0:
				targets = arc_targets(tv, hp_after, hp_after + amount)
			fx.hit_shards(hit_at, center, r, targets, color, maxi(amount, int(b.get("raw", amount))), bool(b.get("crit", false)), impact, blocked)
			if src_spot != Vector2.INF and b.has("source") and _is_satellite(b):
				fx.drone_attack(src_spot, color)
		"evaded":
			if src_spot != Vector2.INF:
				fx.evade_token(token_spot(center, r, foe_at), src_spot, color, impact)
		"evade":
			fx.evade_gain(token_spot(center, r, foe_at), origin)
		"block":
			fx.wall(center, r, foe_at, "brick", origin)
		"shield":
			fx.wall(center, r, foe_at, "hex", origin)
		"heal":
			var hp_after := int(b.get("hp_after", -1))
			var amount := int(b.get("amount", 0))
			if on_host and hp_after >= 0 and amount > 0:
				fx.heal_inflow(center, r, arc_targets(tv, hp_after - amount, hp_after))
		"status":
			if int(b.get("status", RC.Status.NONE)) == RC.Status.CORRUPTED and int(b.get("slot", -1)) >= 0 and on_host:
				fx.corrupt_apply(tv.slot_spot(int(b["slot"])), origin, impact)
		"corrupted":
			var hp_after := int(b.get("hp_after", -1))
			var amount := int(b.get("amount", 0))
			var at := tv.slot_spot(int(b["slot"])) if int(b.get("slot", -1)) >= 0 else tv.hp_ring_spot()
			var targets: Array[Vector2] = [tv.hp_ring_spot()]
			if on_host and hp_after >= 0 and amount > 0:
				targets = arc_targets(tv, hp_after, hp_after + amount)
			fx.corrupt_tick(at, center, r, targets, impact)


## True when beat `b`'s source is a drone or satellite (its own wheel's token).
static func _is_satellite(b: Dictionary) -> bool:
	return not bool(b.get("wheel_source", true))


## Where the evade token sits: on the rim of the wheel at `center` (radius `r`) facing `foe_at`.
static func token_spot(center: Vector2, r: float, foe_at: Vector2) -> Vector2:
	var d := (foe_at - center).normalized() if foe_at.distance_to(center) > 1.0 else Vector2.UP
	return center + (d + Vector2.UP).normalized() * r * TOKEN_OUT


## ARC_TARGETS points along `v`'s HP arc between HP `from_hp` and `to_hp` (global).
static func arc_targets(v: WheelView, from_hp: int, to_hp: int) -> Array[Vector2]:
	var c := v.combatant
	var center := v.global_center()
	var ring := (v.hp_ring_spot() - center).length()
	var mx := maxf(1.0, float(c.max_hp))
	var f0 := clampf(float(mini(from_hp, to_hp)) / mx, 0.0, 1.0)
	var f1 := clampf(float(maxi(from_hp, to_hp)) / mx, 0.0, 1.0)
	return BitPath.arc_points(center, ring, HP_ARC_FROM + HP_ARC_SPAN * f0, HP_ARC_FROM + HP_ARC_SPAN * f1, ARC_TARGETS)


## A drone deployed (a "spawn" beat, after its token docked on `tv`): bits stream to its dock
## from the slap point (a card's, D16) or the hub, and pack into it.
static func spawn(fx: CombatFxLayer, b: Dictionary, tv: WheelView) -> void:
	if fx == null or tv == null or tv.combatant == null:
		return
	var id := StringName(String(b.get("target", "")))
	if id == tv.combatant.id:
		return
	fx.drone_deploy(tv.satellite_spot(id), CardFx.origin(b, fx.slap_point, tv.global_center()), Palette.SLICE_TROJAN)


## Where RAM chip `k` of `bar` stands (global), as RamBar draws it (2D owns the bar; a public
## `pip_spot(k)` there would replace this).
static func ram_pip(bar: RamBar, k: int) -> Vector2:
	var s := Settings.text_scale
	var x0 := bar._label_x() - bar.max_ram * RamBar.STEP * s - RAM_LABEL_GAP
	return bar.global_position + Vector2(x0 + k * RamBar.STEP * s + RamBar.CHIP * s * 0.5, 1.0 + RamBar.CHIP * s * 0.5)


## RamBar's gap between its chips and its count (px), as its `_label_x` draws it.
const RAM_LABEL_GAP := 6.0


## The chips from `from_k` up to (not with) `to_k` (global).
static func ram_pips(bar: RamBar, from_k: int, to_k: int) -> Array[Vector2]:
	var out: Array[Vector2] = []
	if bar == null:
		return out
	for k in range(mini(from_k, to_k), maxi(from_k, to_k)):
		out.append(ram_pip(bar, k))
	return out
