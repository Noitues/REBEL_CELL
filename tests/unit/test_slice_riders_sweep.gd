extends GutTest
## Plan 2 N20 sweep: every rider combination (hits 1-4, perfect_multiplier 1 / 4, pierce)
## x precision (PERFECT / GOOD / WEAK) x tier factor (T1-T4) x BLOCK (0 / 7) x operative
## needles (1 / 2): preview == result, and the HP lost equals the closed form.

const F := preload("res://tests/helpers/rider_fixture.gd")
const TIER_FACTORS := [1.0, 1.3, 1.69, 2.197]
const BASE := 5


## The closed form: per-hit amount, then BLOCK spent hit by hit (unless pierce).
func _expected(hits: int, mult: float, pierce: bool, offset: int, factor: float, block: int, needles: int, cfg: CampaignConfigData) -> int:
	var m := factor
	if offset == 2:
		m *= cfg.weak_multiplier
	elif offset == 0:
		m *= mult
	var amount := roundi(BASE * m)
	var left := block
	var lost := 0
	for i in hits * needles:
		var through := amount
		if not pierce:
			var b := mini(left, through)
			left -= b
			through -= b
		lost += through
	return lost


func test_sweep_riders_preview_equals_result() -> void:
	var cfg := CombatFixture.config()
	var n := 0
	for hits in [1, 2, 3, 4]:
		for mult: float in [1.0, 4.0]:
			for pierce: bool in [false, true]:
				for offset in [0, 1, 2]:
					for fi in TIER_FACTORS.size():
						for block in [0, 7]:
							for needles in [1, 2]:
								var tag := StringName("rs_%d_%d_%d_%d_%d_%d_%d" % [hits, int(mult), int(pierce), offset, fi, block, needles])
								var s := F.session(tag, F.rider(StringName("%s_shim" % tag), BASE, hits, mult, pierce), [0, 15] if needles == 2 else [0])
								CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0, offset)
								s.state.get_combatant(&"enemy_0").output_scale = TIER_FACTORS[fi]
								s.state.player.block = block
								var out := F.end(s)
								var want := _expected(hits, mult, pierce, offset, TIER_FACTORS[fi], block, needles, cfg)
								if out["lost"] != want or out["preview_lost"] != out["lost"]:
									fail_test("%s: lost %d, preview %d, want %d" % [tag, out["lost"], out["preview_lost"], want])
									return
								n += 1
	assert_eq(n, 4 * 2 * 2 * 3 * 4 * 2 * 2)
