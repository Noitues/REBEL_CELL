class_name CardFx
extends RefCounted
## ART-2 2C (ART_BIBLE v2 §3.18): the sticker card's play, as pure numbers the FX layer
## draws: the D16 origin rule, the slap's squash and the dissolve A layout. No nodes.
##
## D16 (plan default, pending the designer): every card-caused effect stems from the card's
## slap point on the target wheel; its bits leave from there, never from the hand. Effects
## no card causes keep their own source (a slice, the hub, the turn start, an enemy).

## The slap (§3.18 step 5): drop, squash to SQUASH (x, y), overshoot, settle. The squash's
## share of the slap, then the overshoot's share and size (a scale past 1).
const SQUASH := Vector2(1.13, 0.86)
const SQUASH_SHARE := 0.35
const OVERSHOOT_SHARE := 0.35
const OVERSHOOT := Vector2(0.96, 1.05)
## Dissolve A (§3.18 step 6, round 19's fix): 17 px cells, glyphs 19-25 px shrinking to
## 10 px, the scan front's share of the dissolve, each glyph's hold and release jitter
## (shares of the dissolve), its travel and the absorbed share (the last 30 %).
const CELL_PX := 17.0
const GLYPH_MIN := 19.0
const GLYPH_MAX := 25.0
const GLYPH_END := 10.0
const SCAN_SHARE := 0.4
const HOLD_SHARE := 0.08
const JITTER_SHARE := 0.15
const TRAVEL_SHARE := 0.32
const TRAVEL_SPREAD_SHARE := 0.05
## The white-hot core of a fresh glyph (§3.18: 80 ms).
const HOT_SECONDS := 0.08


## Where a beat's effect starts (D16): a card-caused beat (the "act" phase of a played
## card, while the card's slap is known) starts at `slap`; any other beat keeps
## `own_source` (its slice, hub, the turn start or the enemy). Vector2.INF = no slap.
static func origin(beat: Dictionary, slap: Vector2, own_source: Vector2) -> Vector2:
	if caused_by_card(beat) and slap != Vector2.INF:
		return slap
	return own_source


## True when a beat is the effect of a played card (ResolveBeats' "act" phase), not of a
## slice, the hub, the turn start or an enemy.
static func caused_by_card(beat: Dictionary) -> bool:
	return String(beat.get("phase", "")) == "act"


## The slap's scale at `p` (0..1 through the slap): squash, overshoot, settle to 1.
static func slap_scale(p: float) -> Vector2:
	if p < SQUASH_SHARE:
		return Vector2.ONE.lerp(SQUASH, sin(p / SQUASH_SHARE * PI * 0.5))
	if p < SQUASH_SHARE + OVERSHOOT_SHARE:
		return SQUASH.lerp(OVERSHOOT, (p - SQUASH_SHARE) / OVERSHOOT_SHARE)
	var q := (p - SQUASH_SHARE - OVERSHOOT_SHARE) / maxf(0.001, 1.0 - SQUASH_SHARE - OVERSHOOT_SHARE)
	return OVERSHOOT.lerp(Vector2.ONE, q)


## Dissolve A's bits for a card at `rect` (global) dissolving over `seconds` into `hub`:
## scale 1.0 cells at `cell_scale` (the text scale) so a bigger card keeps 17 px glyph cells.
static func dissolve_path(rect: Rect2, seconds: float, hub: Vector2, cell_scale: float = 1.0) -> BitPath:
	var s := maxf(0.5, cell_scale)
	return BitPath.dissolve(hash(rect.position.snapped(Vector2.ONE)), rect, CELL_PX * s, seconds * SCAN_SHARE, seconds * HOLD_SHARE,
		seconds * JITTER_SHARE, seconds * TRAVEL_SHARE, seconds * TRAVEL_SPREAD_SHARE, hub, GLYPH_MIN * s, GLYPH_MAX * s, GLYPH_END / GLYPH_MAX)
