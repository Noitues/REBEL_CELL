class_name FocusTip
extends PanelContainer
## A control's tooltip shown while it has keyboard or pad focus (H23 S8: a shop card's
## text is cut on the sticker and a pad player never hovers, so the whole text never
## showed). The tip hangs under the control (over it when there is no room below), inside
## the screen, in the theme's tooltip look; it goes when focus leaves. Not shown while the
## mouse is over the control (the ordinary tooltip does that). View only.

## Gap between the control and the tip (px).
const GAP := 6.0
## ANIM-R2 E8: when every spot covers something, the tip is folded narrower (these shares
## of its columns, never under FOLD_MIN columns) and the spot covering least wins, so a
## tall narrow tip can go beside the loot row instead of over Skip.
## Art pass W2 (ART_BIBLE 6.8): the folds are the columns between UiTip.COLUMNS (36) and
## UiTip.MIN_COLUMNS (26), widest first.
const FOLD_COLUMNS: Array[int] = [31, 26]
## ANIM-R4 C7: a fold never goes under this many columns (at 1.6 a 16-column fold put one
## word per line and the tall tip covered the MODEM sign and a loot card); a crowded tip
## keeps that width, tries the screen's edges and steps its lettering down (FONT_SHARES),
## never under the caption step (ART_BIBLE 4.3 rule 2).
const FOLD_MIN := UiTip.MIN_COLUMNS


## Shows `control`'s tooltip while it has focus (not while the mouse is over it).
static func attach(control: Control) -> void:
	if control.focus_entered.is_connected(_show_for.bind(control)):
		return
	control.focus_entered.connect(_show_for.bind(control))
	control.focus_exited.connect(_hide_for.bind(control))


## The tip on screen for `control` (null when none).
static func tip_of(control: Control) -> FocusTip:
	return control.get_node_or_null(^"FocusTip") as FocusTip


static func _show_for(control: Control) -> void:
	if not is_instance_valid(control) or control.tooltip_text == "" or not control.is_inside_tree():
		return
	if control.get_global_rect().has_point(control.get_global_mouse_position()) and not Settings.pad_active:
		return
	# ANIM-R2 E8: a page's own first focus (its entrance) shows no tip for a mouse player
	# (the loot's first card showed its tip over Skip with nothing pressed); a key or pad
	# moving focus does.
	if not Settings.pad_active and not Input.is_anything_pressed():
		return
	_hide_for(control)
	var tip := FocusTip.new()
	tip.name = "FocusTip"
	tip.theme_type_variation = &"TooltipPanel"
	tip.top_level = true
	tip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tip.z_index = 50
	tip.text = control.tooltip_text
	tip.add_child(UiTip.make(control.tooltip_text))
	control.add_child(tip)
	tip._place.call_deferred(control)
	# Animation pass ANIM-6: the tip fades in (`focus_tip_in`).
	tip.modulate.a = 0.0
	Motion.fade(tip, 1.0, &"focus_tip_in")


static func _hide_for(control: Control) -> void:
	if not is_instance_valid(control):
		return
	var old := tip_of(control)
	if old != null:
		control.remove_child(old)
		old.queue_free()


## The tip's words (unfolded).
var text: String = ""


func _place(control: Control) -> void:
	if not is_instance_valid(control):
		return
	size = get_combined_minimum_size()
	var screen := control.get_viewport_rect()
	var avoid := avoid_rects(control)
	var r := control.get_global_rect()
	var at := spot(r, size, screen, avoid)
	var hits := covered(Rect2(at, size), r, avoid)
	if hits > 0.0 and text != "":
		# ANIM-R2 E8: narrower folds, the one covering least. ANIM-R4 C7: never under FOLD_MIN
		# columns; when every fold still covers something the lettering steps down
		# (FONT_SHARES) at the same folds before a word a line ever would.
		var best_cols := -1
		var best_font := 1.0
		var chrome: Vector2 = get_combined_minimum_size() - (get_child(0) as Control).get_combined_minimum_size()
		for fshare in FONT_SHARES:
			for fold_cols in FOLD_COLUMNS:
				var c := maxi(FOLD_MIN, fold_cols)
				var body := _body(c, fshare)
				add_child(body)
				var sz: Vector2 = body.get_combined_minimum_size() + chrome
				remove_child(body)
				body.free()
				var p := spot(r, sz, screen, avoid)
				var h := covered(Rect2(p, sz), r, avoid)
				if h < hits:
					hits = h
					at = p
					best_cols = c
					best_font = fshare
				if h == 0.0:
					break
			if hits == 0.0:
				break
		if best_cols > 0:
			var old := get_child(0)
			remove_child(old)
			old.queue_free()
			add_child(_body(best_cols, best_font))
			size = Vector2.ZERO
			size = get_combined_minimum_size()
	global_position = at


## The tip's body folded to `cols` columns, its lettering at `fshare` of the theme's (never
## under the caption step).
func _body(cols: int, fshare: float) -> Control:
	var fs := 0
	if fshare < 1.0:
		fs = maxi(UiTheme.font_px(UiTheme.CAPTION), roundi(get_theme_font_size(&"font_size", &"TooltipLabel") * fshare))
	return UiTip.make(text, "", cols, fs)


## ANIM-R4 C7: the lettering steps a crowded tip tries (shares of the theme's size).
const FONT_SHARES: Array[float] = [1.0, 0.85, 0.72]


## How much of `avoid` (and the control's own rect `own`) a tip at `box` covers (0: none).
static func covered(box: Rect2, own: Rect2, avoid: Array[Rect2]) -> float:
	var hits := 0.0
	for a in avoid:
		if box.intersects(a):
			hits += box.intersection(a).get_area() + 1.0
	if box.intersects(own):
		hits += box.intersection(own).get_area() + 1.0
	return hits


## ANIM-R1 M11: where a `tip`-sized tip for a control at `r` goes on `screen`: under it,
## beside it (right, then left) or over it, the first spot inside the screen that covers
## none of `avoid` (the page's buttons, tags and titles: the loot's tip hid Skip and the
## window's title); else the one covering the least. Pure (tests).
static func spot(r: Rect2, tip: Vector2, screen: Rect2, avoid: Array[Rect2]) -> Vector2:
	var tries: Array[Vector2] = [Vector2(r.position.x, r.end.y + GAP), Vector2(r.end.x + GAP, r.position.y),
		Vector2(r.position.x - GAP - tip.x, r.position.y), Vector2(r.position.x, r.position.y - GAP - tip.y),
		Vector2(r.end.x + GAP, r.end.y - tip.y), Vector2(r.position.x - GAP - tip.x, r.end.y - tip.y),
		# ANIM-R2 E8: the screen's side margins, level with the control (a middle loot card's
		# tip beside it covered its neighbour).
		Vector2(screen.position.x + GAP, r.position.y), Vector2(screen.end.x - GAP - tip.x, r.position.y),
		# ANIM-R4 C7: the screen's top and bottom edges above / below the control, then its
		# corners (a wide tip that fits nowhere beside a big-text loot row goes under the page).
		Vector2(r.get_center().x - tip.x * 0.5, screen.end.y - GAP - tip.y), Vector2(r.get_center().x - tip.x * 0.5, screen.position.y + GAP),
		Vector2(screen.position.x + GAP, screen.end.y - GAP - tip.y), Vector2(screen.end.x - GAP - tip.x, screen.end.y - GAP - tip.y)]
	var best := Vector2.INF
	var best_hits := INF
	for at in tries:
		var p := Vector2(clampf(at.x, screen.position.x, maxf(screen.position.x, screen.end.x - tip.x)),
			clampf(at.y, screen.position.y, maxf(screen.position.y, screen.end.y - tip.y)))
		var box := Rect2(p, tip)
		var hits := 0.0
		for a in avoid:
			if box.intersects(a):
				hits += box.intersection(a).get_area() + 1.0
		# The tip never covers its own control either.
		if box.intersects(r):
			hits += box.intersection(r).get_area() + 1.0
		if hits < best_hits:
			best_hits = hits
			best = p
			if hits == 0.0:
				break
	return best


## What a tip keeps off (screen rects): the usable controls and legends on screen (as the
## SAVED stamp does), graffiti titles and terminal window title bars, except `control`
## and what is inside it.
static func avoid_rects(control: Control) -> Array[Rect2]:
	var out: Array[Rect2] = []
	if not control.is_inside_tree():
		return out
	var own := control.get_global_rect()
	for r in Fx.avoid_rects(control.get_tree().root):
		if not own.encloses(r):
			out.append(r)
	_titles(control.get_tree().root, out)
	return out


static func _titles(node: Node, out: Array[Rect2]) -> void:
	for c in node.get_children():
		if c is CanvasItem and not (c as CanvasItem).visible:
			continue
		# ANIM-R4 C7: the MODEM sign too (a tip lay over it at 1.6).
		if c is GraffitiTag or c is ModemSign or (c is Label and c.name == &"TerminalTitle"):
			out.append((c as Control).get_global_rect())
		_titles(c, out)
