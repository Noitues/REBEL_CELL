extends GutTest
## Plan 2 N1 sweep: every shipped enemy x the four tier factors. Its heal / block / shield
## amounts (wheel slices and Hub passives) are whole, never negative, non-decreasing in tier
## when FLAT and constant when PERCENT.

const TIER_FACTORS: Array[float] = [1.0, 1.3, 1.69, 2.2]
const AMOUNT_SLICES := [RC.SliceType.HOTFIX, RC.SliceType.DEFRAG, RC.SliceType.SANDBOX]
const AMOUNT_EFFECTS := [RC.EffectType.HEAL, RC.EffectType.GAIN_BLOCK, RC.EffectType.GAIN_SHIELD]

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


## {label: [amount at each factor]} and {label: percent?} for one enemy.
func _amounts(data: EnemyData) -> Array:
	var by_label := {}
	var percent := {}
	for f in TIER_FACTORS:
		var c := EffectInterpreter.make_combatant(data, &"sweep", false)
		CombatResolver._scale_enemy(c, 1.0, f)
		for i in c.wheel.slot_slice_ids.size():
			var s := _resolver.fx.slice_of(c.wheel, i)
			if s == null or not (s.slice_type in AMOUNT_SLICES):
				continue
			var pct := s.amount_mode == RC.AmountMode.PERCENT
			var label := "slot %d %s" % [i, s.id]
			percent[label] = pct
			by_label.get_or_add(label, []).append(roundi(CombatResolver.slice_base(c, s) * (1.0 if pct else c.output_scale)))
		var hub := _resolver.fx.hub_of(c.wheel)
		if hub == null:
			continue
		for t in hub.passive_effects.size():
			var te := hub.passive_effects[t]
			for k in te.effects.size():
				var e := te.effects[k]
				if e == null or not (e.type in AMOUNT_EFFECTS):
					continue
				var label := "hub %s %d.%d" % [hub.id, t, k]
				percent[label] = e.amount_mode == RC.AmountMode.PERCENT
				by_label.get_or_add(label, []).append(_resolver.fx.effect_amount(e, c))
	return [by_label, percent]


func _enemies() -> Array[EnemyData]:
	var out: Array[EnemyData] = []
	for id in ContentRegistry.all_ids():
		var d := ContentRegistry.get_content(id) as EnemyData
		if d != null and d.wheel != null:
			out.append(d)
	return out


func test_all_enemy_amounts_whole_non_negative_and_ordered_by_tier() -> void:
	var checked := 0
	for d in _enemies():
		var got := _amounts(d)
		var by_label: Dictionary = got[0]
		for label in by_label:
			var values: Array = by_label[label]
			assert_eq(values.size(), TIER_FACTORS.size(), "%s %s" % [d.id, label])
			for v in values:
				assert_true(v is int and int(v) >= 0, "%s %s: %s" % [d.id, label, values])
			if bool(got[1][label]):
				assert_eq(values.count(values[0]), values.size(), "%s %s PERCENT is the same at every tier: %s" % [d.id, label, values])
			else:
				for i in range(1, values.size()):
					assert_true(int(values[i]) >= int(values[i - 1]), "%s %s FLAT never drops with tier: %s" % [d.id, label, values])
			checked += 1
	assert_gt(checked, 0, "the sweep found enemy heal / block / shield amounts")
