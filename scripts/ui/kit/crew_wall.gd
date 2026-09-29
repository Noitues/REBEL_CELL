class_name CrewWall
extends GridContainer
## Art pass W8d (ART_BIBLE §11 Campaign end, §7.1, critique 62/63): the campaign's crew as
## Polaroids taped to the wall, one per operative who served (the roster, in its order).
## Each photo is the operative's own face (W5 PortraitArt) in the expression the end gives
## it (`expression_for`): a win leaves the living TRIUMPHANT, a loss leaves them HURT, and
## the dead are FLATLINED either way. Each is taped at the top and tilted a little (fixed
## per place, never random). The stage sets `columns` to fit the room. View only.

## The photo's size at text scale 1.0 (px), the most it grows with the text, the gap round
## each one and the tape strip (px at 1.0).
const PHOTO := Vector2(96, 118)
const GROW_MAX := 1.3
const GAP := UiTheme.SP_M
const TAPE := Vector2(40, 12)
## The tilts the photos take in turn (degrees; §2 PAPER: within ±4).
const TILTS: Array[float] = [-3.0, 2.5, -1.5, 3.5, -2.5, 1.5, -3.5, 2.0]
## The tape's own small tilts in turn (degrees).
const TAPE_TILTS: Array[float] = [4.0, -3.0, 2.0, -5.0]

var polaroids: Array[Polaroid] = []
var cells: Array[Control] = []


## `crew` = [{id, class_id, name, alive}, ...] (the roster, in order); `won` picks the living
## operatives' expression.
func _init(crew: Array = [], won: bool = true) -> void:
	name = "CrewWall"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var k := minf(Settings.text_scale, GROW_MAX)
	add_theme_constant_override("h_separation", roundi(GAP * k))
	add_theme_constant_override("v_separation", roundi(GAP * k))
	columns = maxi(1, crew.size())
	for i in crew.size():
		var op: Dictionary = crew[i]
		var cell := Control.new()
		cell.name = "Wall%d" % i
		cell.mouse_filter = Control.MOUSE_FILTER_PASS
		cell.custom_minimum_size = cell_size()
		var photo := Polaroid.new(String(op.get("name", "")), "[PORTRAIT]", TILTS[i % TILTS.size()])
		photo.name = "Photo"
		photo.size = photo_size()
		photo.custom_minimum_size = photo_size()
		photo.position = Vector2(0, TAPE.y * 0.5 * k)
		photo.set_operative(StringName(op.get("class_id", &"")), StringName(op.get("id", &"")))
		photo.set_expression(expression_for(bool(op.get("alive", true)), won))
		cell.add_child(photo)
		var tape := ColorRect.new()
		tape.name = "Tape"
		tape.mouse_filter = Control.MOUSE_FILTER_IGNORE
		tape.color = PaperInk.opaque(Palette.NOTE_TAPE)
		tape.size = TAPE * k
		tape.pivot_offset = tape.size * 0.5
		tape.position = Vector2((photo_size().x - tape.size.x) * 0.5, 0.0)
		tape.rotation_degrees = TAPE_TILTS[i % TAPE_TILTS.size()]
		cell.add_child(tape)
		# The name in full on hover or focus (the caption may shorten it to fit, W5/WF).
		cell.tooltip_text = String(op.get("name", ""))
		add_child(cell)
		cells.append(cell)
		polaroids.append(photo)


## The expression an operative's photo takes at the end (§11, W5 Polaroid): the dead
## flatlined; the living triumphant on a win, hurt on a loss.
static func expression_for(alive: bool, won: bool) -> int:
	if not alive:
		return PortraitArt.Expr.FLATLINED
	return PortraitArt.Expr.TRIUMPHANT if won else PortraitArt.Expr.HURT


## One photo's size at the player's text size (px).
static func photo_size() -> Vector2:
	return (PHOTO * minf(Settings.text_scale, GROW_MAX)).round()


## One place on the wall: the photo plus its tape's overhang (px).
static func cell_size() -> Vector2:
	var k := minf(Settings.text_scale, GROW_MAX)
	return photo_size() + Vector2(0, roundf(TAPE.y * 0.5 * k))


## The width `n` places take in a row (px).
static func row_width(n: int) -> float:
	var k := minf(Settings.text_scale, GROW_MAX)
	return cell_size().x * n + roundf(GAP * k) * maxi(0, n - 1)


## The crew as the wall takes it, from the campaign's roster (read only).
static func crew_of(roster: Array) -> Array:
	var out: Array = []
	for op in roster:
		out.append({"id": op.id, "class_id": op.class_id, "name": op.name, "alive": op.alive})
	return out
