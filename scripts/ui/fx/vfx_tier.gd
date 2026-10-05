class_name VfxTier
extends RefCounted
## VFX tiers (ART_BIBLE 8, art pass W6): spectacle scales with importance. The one place
## the tier limits live as named numbers: coverage, duration, flash alpha, shake and
## hit-stop per tier. Every motion entry declares its tier (`UiMotionEntryData.tier`); the
## FX layers (Fx, CombatFxLayer, RaidFxLayer) clamp what they draw to it and refuse a
## full-screen effect below T4. View only: pure numbers, no state.
##
## | Tier | Coverage              | Max duration | Flash alpha | Shake / hit-stop |
## | T0   | backdrop (behind scrim)| loop >= 3 s | none        | none             |
## | T1   | element + 16 px       | 0.25 s       | +20% glow   | none             |
## | T2   | element + 25% region  | 0.6 s        | 60% local   | 2 px, 2 frames   |
## | T3   | the region            | 1.2 s        | 70% local   | 4 px, 3 frames   |
## | T4   | full screen           | 2.5 s        | 40% white   | camera, not shake|

const T0 := UiMotionEntryData.Tier.T0_AMBIENT
const T1 := UiMotionEntryData.Tier.T1_FEEDBACK
const T2 := UiMotionEntryData.Tier.T2_OUTCOME
const T3 := UiMotionEntryData.Tier.T3_MOMENT
const T4 := UiMotionEntryData.Tier.T4_CINEMATIC
const COUNT := 5
const NAMES: Array[String] = ["T0 ambient", "T1 feedback", "T2 outcome", "T3 moment", "T4 cinematic"]

## How much of the screen a tier may cover.
enum Coverage { BACKDROP, ELEMENT, ELEMENT_REGION, REGION, FULL_SCREEN }
const MAX_COVERAGE: Array[Coverage] = [Coverage.BACKDROP, Coverage.ELEMENT, Coverage.ELEMENT_REGION, Coverage.REGION, Coverage.FULL_SCREEN]
## T1 reaches this far past its element (px); T2 this share of its region past it.
const T1_MARGIN_PX := 16.0
const T2_REGION_SHARE := 0.25
## Longest one-shot effect per tier (s); T0 loops have no end but a slowest-allowed period.
const MAX_SECONDS: Array[float] = [INF, 0.25, 0.6, 1.2, 2.5]
const T0_MIN_PERIOD := 3.0
## Brightest flash per tier (alpha): T0 none; T1 a +20% glow (a 0.2 lift); T2 60% and T3
## 70%, local only; T4 a white flash at 40%, once.
const MAX_FLASH_ALPHA: Array[float] = [0.0, 0.2, 0.6, 0.7, 0.4]
## Largest shake (px) and hit-stop (frames) per tier. T4 moves the camera instead.
const MAX_SHAKE_PX: Array[float] = [0.0, 0.0, 2.0, 4.0, 0.0]
const MAX_HIT_STOP_FRAMES: Array[int] = [0, 0, 2, 3, 0]


## True when `tier` is T0..T4.
static func valid(tier: int) -> bool:
	return tier >= T0 and tier <= T4


static func _i(tier: int) -> int:
	return clampi(tier, T0, T4)


## Only T4 may cover the whole screen (no full-screen colour flash below T4).
static func allows_full_screen(tier: int) -> bool:
	return valid(tier) and tier == T4


## `alpha` held to `tier`'s flash limit.
static func clamp_alpha(tier: int, alpha: float) -> float:
	return clampf(alpha, 0.0, MAX_FLASH_ALPHA[_i(tier)])


## `seconds` held to `tier`'s duration limit (T0 is a loop: unbounded).
static func clamp_seconds(tier: int, seconds: float) -> float:
	return clampf(seconds, 0.0, MAX_SECONDS[_i(tier)])


## A shake of `px` held to `tier`'s limit (0 below T2 and at T4).
static func clamp_shake(tier: int, px: float) -> float:
	return clampf(px, 0.0, MAX_SHAKE_PX[_i(tier)])


## A hit-stop of `frames` held to `tier`'s limit.
static func clamp_hit_stop(tier: int, frames: int) -> int:
	return clampi(frames, 0, MAX_HIT_STOP_FRAMES[_i(tier)])


## The farthest an effect of `tier` may reach from its element's centre (px): an element
## of `element_radius` in a region of `region_radius` (a wheel's element is its disc, its
## region the wheel with its HP arc and tags). INF at T4 (the screen) and T0 (backdrop).
static func max_radius(tier: int, element_radius: float, region_radius: float) -> float:
	match _i(tier):
		T1:
			return element_radius + T1_MARGIN_PX
		T2:
			return element_radius + region_radius * T2_REGION_SHARE
		T3:
			return maxf(element_radius, region_radius)
	return INF


## `radius` held to `tier`'s reach (see max_radius).
static func clamp_radius(tier: int, radius: float, element_radius: float, region_radius: float) -> float:
	return minf(radius, max_radius(tier, element_radius, region_radius))


## The tier motion entry `id` declares (T1 when it has no entry).
static func of(id: StringName) -> int:
	if not Motion.has(id):
		return T1
	var e := Motion.entry(id)
	return int(e.tier) if e != null else T1


## An entry's duration fits its tier (T0 loops: a period of at least T0_MIN_PERIOD is not
## required of every T0 entry, only of the backdrop's; ART_BIBLE 8 lists it as a floor).
static func fits(e: UiMotionEntryData) -> bool:
	return e != null and valid(int(e.tier)) and e.duration <= MAX_SECONDS[_i(int(e.tier))]
