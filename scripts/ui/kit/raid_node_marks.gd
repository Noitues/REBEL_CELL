class_name RaidNodeMarks
extends RefCounted
## RAID-VIS F2 (designer D28): each node shows its own raid outcome as grease pencil, in the playout (when
## it happens), on the after-action report's map and at the HQ until the node is repaired or reclaimed.
##   DOWN:  a cross-out over the node, the node dimmed.
##   TAKEN: a ring round the node with a corporation flag, the node in the corporation's colour.
##   HOLDS: a pencil check, shown briefly.
## ONE helper draws all three (`draw`, `tint`): art's pencil toolbox module (`art/look-toolbox`, its wax stroke
## API) is not on main yet, so the strokes go through the kit's PencilSet / GreasePencilMark (the wax ink). When
## the toolbox lands, `draw` is the one place that changes. Pure geometry + the pool calls; no state.

const DOWN := "down"
const TAKEN := "taken"
const HOLDS := "holds"

## The mark's reach round a node (x the node's radius in px).
const CROSS_REACH := 1.0
const RING_RX := 1.35
const RING_RY := 1.2
## The flag: pole top above the node and the pennant's size (x the radius), the pole's offset from the centre.
const FLAG_X := 0.95
const FLAG_FOOT := -0.55
const FLAG_TOP := -2.0
const FLAG_W := 1.0
const FLAG_H := 0.7
## The check (x the radius): its three points.
const CHECK_A := Vector2(-0.5, 0.0)
const CHECK_B := Vector2(-0.1, 0.45)
const CHECK_C := Vector2(0.65, -0.55)
## The tint discs under a mark: alpha of the dimmed DOWN node's shade and the TAKEN node's corporation colour,
## and their reach (x the radius).
const DOWN_SHADE_ALPHA := 0.55
const TAKEN_TINT_ALPHA := 0.5
const TINT_REACH := 1.15


## True for an outcome that has a mark.
static func has_mark(outcome: String) -> bool:
	return outcome == DOWN or outcome == TAKEN or outcome == HOLDS


## The wax ink of an outcome's mark (the losses are the threat's red, the check the plan's yellow).
static func ink_of(outcome: String) -> GreasePencilMark.Ink:
	return GreasePencilMark.Ink.PLAN if outcome == HOLDS else GreasePencilMark.Ink.THREAT


## The strokes of the outcome's mark round centre `c` for a node of radius `r` (px), in writing order; empty for
## an outcome without one.
static func strokes(outcome: String, c: Vector2, r: float, seed: int = 1) -> Array[PackedVector2Array]:
	var out: Array[PackedVector2Array] = []
	match outcome:
		DOWN:
			out = PencilSet.cross_strokes(Rect2(c - Vector2(r, r) * CROSS_REACH, Vector2(r, r) * 2.0 * CROSS_REACH))
		TAKEN:
			out.append(PencilShapes.hand_circle(c, Vector2(r * RING_RX, r * RING_RY), seed))
			var foot := c + Vector2(r * FLAG_X, r * FLAG_FOOT)
			var top := c + Vector2(r * FLAG_X, r * FLAG_TOP)
			out.append(PackedVector2Array([foot, top]))
			out.append(PackedVector2Array([top, top + Vector2(r * FLAG_W, r * FLAG_H * 0.5), top + Vector2(0.0, r * FLAG_H)]))
		HOLDS:
			out.append(PackedVector2Array([c + CHECK_A * r, c + CHECK_B * r, c + CHECK_C * r]))
	return out


## Writes the outcome's mark for node `key` on `pool` (a PencilSet; points in the pool's px): written to `write`
## (0..1) and wiped from `wipe` (0..1). Returns the mark, or null for an outcome without one.
static func draw(pool: PencilSet, key: String, outcome: String, c: Vector2, r: float, write: float = 1.0, wipe: float = 0.0, seed: int = 1) -> GreasePencilMark:
	if pool == null or not has_mark(outcome):
		return null
	return pool.stroke("node_%s" % key, strokes(outcome, c, r, seed), ink_of(outcome), clampf(write, 0.0, 1.0), clampf(wipe, 0.0, 1.0), false, seed)


## The disc under a mark: DOWN dims the node, TAKEN puts it in the corporation's colour (`corp`), `alpha` scaling
## both (a fade-in). Drawn on `ci` at `c` (the canvas's px) for a node of radius `r`.
static func tint(ci: CanvasItem, outcome: String, c: Vector2, r: float, corp: Color, alpha: float = 1.0) -> void:
	if alpha <= 0.0:
		return
	if outcome == DOWN:
		ci.draw_circle(c, r * TINT_REACH, Color(Palette.GLYPH_INK, DOWN_SHADE_ALPHA * alpha))
	elif outcome == TAKEN:
		ci.draw_circle(c, r * TINT_REACH, Color(corp, TAKEN_TINT_ALPHA * alpha))


## The standing marks of a Grid: site id (String) -> DOWN or TAKEN, from the campaign's own state (a DOWN node, a
## TAKEN Site), so the HQ shows them until the node is repaired or the Site reclaimed.
static func of_grid(grid: GridState) -> Dictionary:
	var out := {}
	if grid == null:
		return out
	for id in grid.sites:
		var sid := StringName(id)
		if grid.is_taken(sid):
			out[String(sid)] = TAKEN
		elif grid.is_claimed(sid) and int(grid.site(sid).get("condition", GridState.Condition.OK)) == GridState.Condition.DOWN:
			out[String(sid)] = DOWN
	return out


## The marks of a resolved raid's `nodes` map (id -> {outcome}): DOWN, TAKEN, and HOLDS for a node that held.
## The home node is left out (its verdict is the stamp).
static func of_raid(nodes: Dictionary, home: StringName) -> Dictionary:
	var out := {}
	for id in nodes:
		if StringName(id) == home:
			continue
		var outcome := String((nodes[id] as Dictionary).get("outcome", ""))
		if has_mark(outcome):
			out[String(id)] = outcome
	return out
