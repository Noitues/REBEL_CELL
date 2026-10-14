class_name RaidReportPencil
extends Control
## ART-6 3A / R8 (W3-RAID): the Cell's grease pencil on the intercepted after-action report
## (ART_BIBLE v2 §4.8 "Raid report"). R8: only one pencil word is left, CELL HOLDS, written at
## the spot the report keeps for it ("CellHolds", a plain Control sized to the word) in our
## yellow: no circles, no checks, no THEY LOST / OURS / RIP. It writes on (`raid_mark_write`,
## real time; one press ends it; at once when motion doesn't play). A full-screen layer over the
## page (no UI ever covers grease pencil); it takes no input. View only.

const WRITE := &"raid_mark_write"
## Pencil: the word's type step (a title step) and its slant (rad).
const WORD_STEP := UiTheme.TITLE
const WORD_TILT := -0.1
## Smallest write-on duration divisor guard (s).
const WRITE_MIN_DURATION: float = 0.001

var report: Control
var result: Dictionary = {}
var held: bool = true
var reward: int = -1
var _t: float = 0.0
var _pool: RaidPencilPool = null


func _init(p_report: Control = null, p_result: Dictionary = {}, p_held: bool = true, p_reward: int = -1) -> void:
	report = p_report
	result = p_result
	held = p_held
	reward = p_reward
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	MotionSkip.register_passive(self)
	if not Motion.live(WRITE):
		_t = INF


func _process(delta: float) -> void:
	if not is_visible_in_tree():
		return
	if _t < _total():
		_t += delta
	_lay()


func _exit_tree() -> void:
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


func _total() -> float:
	return Motion.entry(WRITE).duration if Motion.entry(WRITE) != null else 0.4


## MotionSkip: the mark still writing.
func motion_running() -> bool:
	return _t < _total()


## MotionSkip: the mark written.
func complete_motion() -> void:
	_t = INF


## The pencil words on show now (their texts): CELL HOLDS when the Cell held, else none.
func words() -> PackedStringArray:
	var out := PackedStringArray()
	if held and _spot().has_area():
		out.append(tr(RaidVerdict.CELL_HOLDS))
	return out


## The spot the report keeps for CELL HOLDS (global rect; empty when missing).
func _spot() -> Rect2:
	if report == null or not is_instance_valid(report):
		return Rect2()
	var l := report.find_child("CellHolds", true, false) as Control
	if l == null or not l.is_visible_in_tree():
		return Rect2()
	return l.get_global_rect()


## Lays CELL HOLDS on 1B's grease pencil (RaidPencilPool, above the paper and every panel).
func _lay() -> void:
	if _pool == null:
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	var spot := _spot()
	if held and spot.has_area():
		var u := clampf(_t / maxf(_total(), WRITE_MIN_DURATION), 0.0, 1.0)
		_pool.word("holds", tr(RaidVerdict.CELL_HOLDS), spot.get_center(), WORD_STEP, GreasePencilMark.Ink.PLAN, 1.0, u, 0.0, WORD_TILT)
	_pool.end()
