class_name PageTransition
extends Node
## Screen transitions (Animation pass ANIM-6, ANIMATION_HANDOFF 4.17, STYLE_GUIDE 5.3): a page
## (or a panel: the pause menu, a dialog, a dossier) enters in its world's way. Terminal
## glass slides in from a screen edge (`panel_in`) with a one-frame CRT roll
## (`panel_crt_roll`: the glass jumps a few px and a bright band crosses it); paper drops
## in from above and settles on its tape (`panel_drop`). Both stay under 0.25 s.
##
## The helper is a child node of the page. It moves the page by an offset from wherever
## its container lays it out (a container that sorts again mid-motion gives the new rest
## position), so it works inside any container. Focus lands when the motion ends (the
## caller's `on_done`); any key, button or click during it completes it at once and does
## nothing else, like a SEND IT skip. Under reduce effects, headless (tests) and for a
## disabled entry nothing moves: `on_done` runs at once. View only: never game state.

enum Look { GLASS, PAPER }

## Share of the motion the page takes to fade in from clear.
const FADE_SHARE := 0.4
## The CRT roll band's height as a share of the page's.
const ROLL_BAND_SHARE := 0.12
const NODE_NAME := "PageTransition"
## ANIM-R1 M11: a page whose glass is only some of its controls (windows over the city)
## names them in this meta (Array of Controls); the roll band crosses each of them only.
const GLASS_META := &"page_glass"

var page: Control = null
var look: int = Look.GLASS
## -1: from the left edge, 1: from the right (glass); paper always drops from above.
var direction: int = 1
var _on_done: Callable = Callable()
var _t: float = 0.0
var _started: bool = false
var _rest: Vector2 = Vector2.ZERO
var _last_set: Vector2 = Vector2.INF
var _roll: Control = null
## Seconds of the CRT roll still to show (it starts once the glass is fully shown).
var _roll_left: float = 0.0
var _alpha: float = 1.0
var _done: bool = false


## Plays `p_look`'s entrance on `p_page` and runs `on_done` when it ends (at once when the
## motion doesn't play). Returns the helper, or null when nothing moves.
static func enter(p_page: Control, p_look: int = Look.GLASS, on_done: Callable = Callable(), p_direction: int = 1) -> PageTransition:
	var old := of(p_page)
	if old != null:
		old.finish()
	var id := id_for(p_look)
	if not Motion.live(id) or not p_page.is_inside_tree():
		if on_done.is_valid():
			on_done.call()
		return null
	var tr_node := PageTransition.new()
	tr_node.name = NODE_NAME
	tr_node.page = p_page
	tr_node.look = p_look
	tr_node.direction = -1 if p_direction < 0 else 1
	tr_node._on_done = on_done
	tr_node._alpha = p_page.modulate.a
	# Clear until the first frame lays the page out (its rest position is known then).
	p_page.modulate.a = 0.0
	p_page.add_child(tr_node)
	return tr_node


## ANIM-R1 M11: marks page `p` as a page of windows over the city: the roll band crosses
## its outermost terminal windows only.
static func glass_is_windows(p: Control) -> void:
	p.set_meta(GLASS_META, windows_of(p))


## The outermost terminal windows under `root`, in tree order.
static func windows_of(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for c in root.get_children():
		if c is TerminalWindow:
			out.append(c as Control)
		else:
			out.append_array(windows_of(c))
	return out


## The motion id of a look.
static func id_for(p_look: int) -> StringName:
	return &"panel_drop" if p_look == Look.PAPER else &"panel_in"


## The look a page enters with: paper when its main surface is a zine paper panel (the
## event's note, the codex), glass otherwise.
static func look_of(p: Control) -> int:
	if p is ZinePanel and not (p as ZinePanel).terminal or p is ZineNote:
		return Look.PAPER
	for child in p.get_children():
		if child is ZinePanel and not (child as ZinePanel).terminal or child is ZineNote:
			return Look.PAPER
		if child is Container:
			for grand in child.get_children():
				if grand is ZinePanel and not (grand as ZinePanel).terminal:
					return Look.PAPER
	return Look.GLASS


## The transition running on `p`, or null.
static func of(p: Node) -> PageTransition:
	if p == null or not is_instance_valid(p):
		return null
	var n := p.get_node_or_null(NodePath(NODE_NAME)) as PageTransition
	return n if n != null and not n._done else null


## True while `p` is still entering.
static func running(p: Node) -> bool:
	return of(p) != null


## Seconds the whole entrance takes for `p_look` (at the current speed).
static func seconds_for(p_look: int) -> float:
	return Motion.delay_of(id_for(p_look)) + Motion.seconds(id_for(p_look))


## Ends every screen motion under `root` at once (a press during an entrance): the
## entrance itself, cards fanning or dealing in, drips growing, the Modem sign warming up,
## menu lines typing, top bar bumps.
static func settle(root: Node) -> void:
	if root == null or not is_instance_valid(root):
		return
	if root is PageTransition:
		(root as PageTransition).finish()
	elif root is ZineCard:
		if (root as ZineCard).dealing():
			(root as ZineCard).finish_deal()
	elif root is DripButton:
		(root as DripButton).settle_motion()
	elif root is ModemSign:
		(root as ModemSign).settle()
	elif root is HudStats:
		(root as HudStats).settle()
	elif root is MenuMotion:
		(root as MenuMotion).finish()
	elif root.has_meta(Typing.META):
		Typing.finish(root as Control)
	for child in root.get_children():
		settle(child)


## The entrance's own clock (ANIM-R3 A8): its progress 0..1 as of its last frame (0 before
## the delay has run, 1 once done). The CRT roll shows only from FADE_SHARE on.
func progress() -> float:
	if _done:
		return 1.0
	var id := id_for(look)
	return clampf(maxf(0.0, _t - Motion.delay_of(id)) / maxf(0.0001, Motion.seconds(id)), 0.0, 1.0)


## Ends the entrance now: the page at rest, opaque, focus given (on_done).
func finish() -> void:
	if _done:
		return
	_done = true
	if is_instance_valid(page):
		if _started:
			page.position = _rest
		page.modulate.a = _alpha
	if _roll != null and is_instance_valid(_roll):
		_roll.queue_free()
	_roll = null
	var cb := _on_done
	_on_done = Callable()
	if cb.is_valid():
		cb.call()
	queue_free()


func _ready() -> void:
	set_process(true)
	set_process_input(true)


func _input(event: InputEvent) -> void:
	if _done:
		return
	# ANIM-R1 (MotionSkip): a press completes the entrance and is consumed.
	if MotionSkip.is_press(event):
		MotionSkip.consume(self, event)
		var p := page
		finish()
		settle(p)


func _process(delta: float) -> void:
	if _done or not is_instance_valid(page):
		return
	if not _started:
		# The container has sorted the page by now: that is where it rests.
		_started = true
		_rest = page.position
		if look == Look.GLASS:
			_add_roll()
			_roll_left = Motion.seconds(&"panel_crt_roll")
	elif page.position != _last_set:
		# The container laid the page out again: the offset rides on the new rest.
		_rest = page.position
	_t += delta
	var id := id_for(look)
	var e := Motion.entry(id)
	var d := maxf(0.0001, Motion.seconds(id))
	var local := maxf(0.0, _t - Motion.delay_of(id))
	var k := clampf(local / d, 0.0, 1.0)
	if k >= 1.0:
		finish()
		return
	var eased := Tween.interpolate_value(0.0, 1.0, k, 1.0, e.trans, e.ease) as float
	var amp := Motion.amplitude(id)
	var from := Vector2(0.0, -amp) if look == Look.PAPER else Vector2(amp * direction, 0.0)
	var offset := from * (1.0 - eased)
	# ANIM-R2 E8: the CRT roll comes once the glass is fully shown (the fade's end), not on the
	# entrance's first frame: over the still-clear page the band read as a half-drawn screen.
	if look == Look.GLASS and k >= FADE_SHARE and _roll_left > 0.0 and Motion.live(&"panel_crt_roll"):
		# The CRT roll: for its one frame the glass jumps down and a band crosses it.
		_roll_left -= delta
		offset.y += Motion.amplitude(&"panel_crt_roll")
		if _roll != null:
			_roll.visible = true
	elif _roll != null:
		_roll.visible = false
	page.position = _rest + offset
	_last_set = page.position
	page.modulate.a = _alpha * clampf(k / FADE_SHARE, 0.0, 1.0)


## The roll band: a bright scan band across the glass, drawn over the page (top level, so
## no container lays it out) for the roll's frame.
func _add_roll() -> void:
	if not Motion.live(&"panel_crt_roll"):
		return
	_roll = Control.new()
	_roll.name = "CrtRoll"
	_roll.top_level = true
	_roll.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_roll.focus_mode = Control.FOCUS_NONE
	var r := page.get_global_rect()
	_roll.global_position = r.position
	_roll.size = r.size
	_roll.visible = false
	var band := ROLL_BAND_SHARE
	# The glass the band crosses (page-local rects): the page, or the controls it names.
	var glass: Array[Rect2] = []
	for g in page.get_meta(GLASS_META, []):
		if g is Control and is_instance_valid(g):
			var gr := (g as Control).get_global_rect()
			glass.append(Rect2(gr.position - r.position, gr.size))
	if glass.is_empty():
		glass.append(Rect2(Vector2.ZERO, r.size))
	_roll.draw.connect(func() -> void:
		for gr: Rect2 in glass:
			var h := gr.size.y * band
			var y := gr.position.y + gr.size.y * 0.3
			_roll.draw_rect(Rect2(gr.position.x, y, gr.size.x, h), Color(Palette.NET_CYAN, 0.32))
			_roll.draw_rect(Rect2(gr.position.x, y + h * 0.45, gr.size.x, 2.0), Color(Palette.PAPER, 0.7)))
	page.add_child(_roll)


func _exit_tree() -> void:
	if not _done and is_instance_valid(page) and page.is_queued_for_deletion():
		_done = true
