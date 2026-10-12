class_name HighContrastWalk
extends RefCounted
## M14 12Q-ACCESS (qa_matrix_audit L78): high contrast on every screen, through the kit.
## HighContrast.apply turns the shared theme high contrast, but most views give their words and
## boxes their own colours (theme overrides), which the theme never reaches: on the combat, HQ,
## Grid, raid and route screens the setting changed almost nothing. This walk restyles every
## Control's own overrides while `Settings.high_contrast` is on, and puts them back when it goes
## off:
## - a box of its own (StyleBoxFlat "panel", "normal", a button's states) that is see-through
##   becomes opaque `HighContrast.BG` with its tint kept as a solid, thicker edge
##   (HighContrast.restyle_box); an opaque box (a sticker's paper) keeps its fill;
## - words of their own colour reach HighContrast.HC_MIN_CONTRAST against what is behind them
##   (HighContrast.lift): the label's own opaque box, else, for light words, a thick
##   HighContrast.BG outline (HighContrast.outline_px) that backs them over the city, the
##   cards and the art; dark words (ink on paper) are lifted against PAPER;
## - a Label's LabelSettings get the same treatment on a copy (never the shared resource).
## Controls are restyled when they enter the tree (deferred, after their own _ready), again when
## a view re-colours them (`theme_changed`), and all at once when the setting or the text scale
## changes. Text a view draws itself goes through HighContrast.draw_text / plate / edge.

## Meta keys: the overrides as the view gave them ({slot: value or null}) and as this walk set them.
const META_SAVED := &"hc_walk_saved"
const META_APPLIED := &"hc_walk_applied"
const META_HOOKED := &"hc_walk_hooked"
const META_FRAME := &"hc_walk_frame"
## The most restyles of one Control in one frame.
const MAX_PASSES := 8
## The colour overrides that are words, per Control kind.
const LABEL_COLORS: Array[StringName] = [&"font_color"]
const BUTTON_COLORS: Array[StringName] = [&"font_color", &"font_hover_color", &"font_pressed_color",
	&"font_focus_color", &"font_hover_pressed_color"]
const RICH_COLORS: Array[StringName] = [&"default_color"]
## The box overrides a Control of each kind draws behind its words.
const PANEL_BOXES: Array[StringName] = [&"panel"]
const LABEL_BOXES: Array[StringName] = [&"normal"]
const BUTTON_BOXES: Array[StringName] = [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]
const FIELD_BOXES: Array[StringName] = [&"normal", &"focus", &"read_only"]
## A box this opaque already backs its words (a sticker's paper): it keeps its fill.
const OPAQUE_ALPHA := 0.9
## Words a view gives less alpha than this are hidden (a layout stand-in, a reveal not begun).
const HIDDEN_ALPHA := HighContrast.HIDDEN_ALPHA
## Words with less contrast than this on HighContrast.BG are ink: they sit on paper or a sticker.
const INK_MAX_CONTRAST := HighContrast.INK_MAX_CONTRAST

static var _installed := false
static var _pending: Array = []
static var _flush_queued := false
## The (high contrast, text scale) the tree was last walked at.
static var _walked_hc := false
static var _walked_scale := 1.0


## Starts the walk (once): Controls entering the tree and Settings changes. UiTheme.apply calls it.
static func install() -> void:
	if _installed:
		return
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null:
		return
	_installed = true
	_walked_hc = Settings.high_contrast
	_walked_scale = Settings.text_scale
	tree.node_added.connect(HighContrastWalk._on_node_added)
	Settings.changed.connect(HighContrastWalk._on_settings_changed)
	if Settings.high_contrast:
		walk(tree.root, true)


## Restyles `node` and everything under it for high contrast `on` (off: the views' own looks back).
static func walk(node: Node, on: bool) -> void:
	if node == null or not is_instance_valid(node):
		return
	if node is Control:
		restyle(node as Control, on)
	for c in node.get_children(true):
		walk(c, on)


## Restyles one Control (not its children) for high contrast `on`.
static func restyle(c: Control, on: bool) -> void:
	if not on:
		_restore(c)
		return
	if not c.has_meta(META_HOOKED):
		c.set_meta(META_HOOKED, true)
		c.theme_changed.connect(HighContrastWalk._queue.bind(c))
	# A view that answers a theme change by setting its colours again would bounce with the walk
	# for ever: at most MAX_PASSES restyles of one Control a frame.
	var frame := Engine.get_process_frames()
	var mark: Vector2i = c.get_meta(META_FRAME, Vector2i(-1, 0))
	var passes := mark.y + 1 if mark.x == frame else 1
	c.set_meta(META_FRAME, Vector2i(frame, passes))
	if passes > MAX_PASSES:
		return
	var boxes := _boxes_of(c)
	for box_name in boxes:
		if not c.has_theme_stylebox_override(box_name):
			continue
		var sb := c.get_theme_stylebox(box_name)
		if not (sb is StyleBoxFlat):
			continue
		if (c.get_meta(META_APPLIED, {}) as Dictionary).get("s:" + String(box_name)) == sb:
			continue  # this walk's copy is on already (the view has not changed it since)
		var orig := _original(c, "s:" + String(box_name), sb) as StyleBoxFlat
		if orig == null:
			continue
		var want: StyleBoxFlat = orig
		if not (orig.draw_center and orig.bg_color.a >= OPAQUE_ALPHA):
			want = orig.duplicate() as StyleBoxFlat
			HighContrast.restyle_box(want, box_name, c is BaseButton)
		_put(c, "s:" + String(box_name), want, func() -> void: c.add_theme_stylebox_override(box_name, want))
	# The opaque fill behind the words when the Control has one (its own box or the theme's).
	var backing := _own_backing(c)
	var colors := _colors_of(c)
	if colors.is_empty():
		return
	var main := colors[0]
	var shown := c.get_theme_color(main)
	if c.has_theme_color_override(main):
		shown = _original(c, "c:" + String(main), shown) as Color
	var light := is_light(shown)
	for color_name in colors:
		if not c.has_theme_color_override(color_name):
			continue
		var orig_c := _original(c, "c:" + String(color_name), c.get_theme_color(color_name)) as Color
		var bg := backing if backing.a > 0.0 else (HighContrast.BG if is_light(orig_c) else Palette.PAPER)
		var want_c := HighContrast.lift(orig_c, bg)
		if orig_c.a < HIDDEN_ALPHA:
			want_c.a = orig_c.a  # words a view hides by their colour stay hidden
		_put(c, "c:" + String(color_name), want_c, func() -> void: c.add_theme_color_override(color_name, want_c))
	if c is Label and (c as Label).label_settings != null:
		_label_settings(c as Label)  # its own colour and outline (the theme's are not read)
		return
	if light and backing.a <= 0.0:
		var px := _font_px(c)
		var outline := HighContrast.outline_px(px)
		var size_key := &"outline_size"
		var cur_o: Variant = c.get_theme_constant(size_key) if c.has_theme_constant_override(size_key) else null
		var orig_o: Variant = _original(c, "k:outline_size", cur_o)
		var want_o := maxi(int(orig_o) if orig_o != null else 0, outline)
		_put(c, "k:outline_size", want_o, func() -> void: c.add_theme_constant_override(size_key, want_o))
		var outline_color := &"font_outline_color"
		if c.has_theme_color_override(outline_color):
			_original(c, "c:font_outline_color", c.get_theme_color(outline_color))
		else:
			_original(c, "c:font_outline_color", null)
		_put(c, "c:font_outline_color", HighContrast.BG, func() -> void: c.add_theme_color_override(outline_color, HighContrast.BG))


## True when `c` is words for a dark ground (every colour but ink: the screens are dark, and a
## dim caption on glass is lifted, never darkened); ink (under INK_MAX_CONTRAST on BG) sits on paper.
static func is_light(c: Color) -> bool:
	return Palette.contrast(Color(c, 1.0), HighContrast.BG) >= INK_MAX_CONTRAST


## The opaque colour behind `c`'s words under high contrast, as the walk leaves it: its own
## opaque box, HighContrast.BG under light words (the outline), PAPER under dark ones (tests).
static func backing_of(c: Control) -> Color:
	var own := _own_backing(c)
	if own.a > 0.0:
		return own
	var colors := _colors_of(c)
	if colors.is_empty():
		return HighContrast.BG
	return HighContrast.BG if is_light(c.get_theme_color(colors[0])) else Palette.PAPER


## The opaque fill `c` draws behind its own words (its first box, override or theme), or a
## clear colour when it has none.
static func _own_backing(c: Control) -> Color:
	var boxes := _boxes_of(c)
	if boxes.is_empty() or c is Panel or c is PanelContainer:
		return Palette.CLEAR
	var sb := c.get_theme_stylebox(boxes[0]) as StyleBoxFlat
	if sb != null and sb.draw_center and sb.bg_color.a >= OPAQUE_ALPHA:
		return Color(sb.bg_color, 1.0)
	return Palette.CLEAR


static func _boxes_of(c: Control) -> Array[StringName]:
	if c is BaseButton:
		return BUTTON_BOXES
	if c is Label:
		return LABEL_BOXES
	if c is LineEdit or c is TextEdit or c is RichTextLabel:
		return FIELD_BOXES
	if c is PanelContainer or c is Panel:
		return PANEL_BOXES
	return []


static func _colors_of(c: Control) -> Array[StringName]:
	if c is Button:
		return BUTTON_COLORS
	if c is Label or c is LineEdit:
		return LABEL_COLORS
	if c is RichTextLabel:
		return RICH_COLORS
	return []


static func _font_px(c: Control) -> int:
	if c is RichTextLabel:
		return c.get_theme_font_size(&"normal_font_size")
	if c is Label and (c as Label).label_settings != null:
		return (c as Label).label_settings.font_size
	return c.get_theme_font_size(&"font_size")


## The view's own value of `slot` on `c`: `current` the first time, or when the view changed
## it since the walk last set it (a view re-colouring its words); the saved one otherwise.
static func _original(c: Control, slot: String, current: Variant) -> Variant:
	var saved: Dictionary = c.get_meta(META_SAVED, {})
	var applied: Dictionary = c.get_meta(META_APPLIED, {})
	if saved.has(slot) and applied.has(slot) and _same(applied[slot], current):
		return saved[slot]
	if saved.has(slot) and current == null:
		return saved[slot]
	saved[slot] = current
	c.set_meta(META_SAVED, saved)
	return current


static func _put(c: Control, slot: String, value: Variant, apply: Callable) -> void:
	var applied: Dictionary = c.get_meta(META_APPLIED, {})
	if applied.has(slot) and _same(applied[slot], value) and _same(_current(c, slot), value):
		return
	applied[slot] = value
	c.set_meta(META_APPLIED, applied)
	apply.call()


static func _same(a: Variant, b: Variant) -> bool:
	if a is Color and b is Color:
		return (a as Color).is_equal_approx(b as Color)
	return typeof(a) == typeof(b) and a == b


static func _current(c: Control, slot: String) -> Variant:
	var key := StringName(slot.substr(2))
	match slot.substr(0, 2):
		"s:":
			return c.get_theme_stylebox(key) if c.has_theme_stylebox_override(key) else null
		"c:":
			return c.get_theme_color(key) if c.has_theme_color_override(key) else null
		"k:":
			return c.get_theme_constant(key) if c.has_theme_constant_override(key) else null
		"l:":
			return (c as Label).label_settings if c is Label else null
	return null


static func _label_settings(l: Label) -> void:
	var ls := l.label_settings
	var orig := _original(l, "l:", ls) as LabelSettings
	if orig == null:
		return
	var light := is_light(orig.font_color)
	var need := HighContrast.outline_px(orig.font_size) if light else 0
	var fc := HighContrast.lift(orig.font_color, HighContrast.BG if light else Palette.PAPER)
	if orig.font_color.is_equal_approx(fc) and orig.outline_size >= need and (not light or orig.outline_color.is_equal_approx(HighContrast.BG)):
		_put(l, "l:", orig, func() -> void: l.label_settings = orig)
		return
	if ls != orig:
		return  # this walk's copy is on already (the view has not changed it since)
	var copy := orig.duplicate() as LabelSettings
	copy.font_color = fc
	if light:
		copy.outline_size = maxi(orig.outline_size, need)
		copy.outline_color = HighContrast.BG
		copy.shadow_color = Color(HighContrast.BG, 0.0)
	_put(l, "l:", copy, func() -> void: l.label_settings = copy)


static func _restore(c: Control) -> void:
	if not c.has_meta(META_SAVED):
		return
	var saved: Dictionary = c.get_meta(META_SAVED, {})
	var applied: Dictionary = c.get_meta(META_APPLIED, {})
	for slot in saved:
		if applied.has(slot) and not _same(_current(c, slot), applied[slot]):
			continue  # the view changed it since: its own value stays
		var key := StringName(String(slot).substr(2))
		var v: Variant = saved[slot]
		match String(slot).substr(0, 2):
			"s:":
				if v == null:
					c.remove_theme_stylebox_override(key)
				else:
					c.add_theme_stylebox_override(key, v)
			"c:":
				if v == null:
					c.remove_theme_color_override(key)
				else:
					c.add_theme_color_override(key, v)
			"k:":
				if v == null:
					c.remove_theme_constant_override(key)
				else:
					c.add_theme_constant_override(key, v)
			"l:":
				if c is Label:
					(c as Label).label_settings = v
	c.remove_meta(META_SAVED)
	c.remove_meta(META_APPLIED)
	c.remove_meta(META_FRAME)


static func _on_node_added(node: Node) -> void:
	if Settings.high_contrast and node is Control:
		_queue(node)


## Restyles `node` once the frame's work is done (after its own _ready and the view's colours).
static func _queue(node: Node) -> void:
	if not Settings.high_contrast:
		return
	_pending.append(node)
	if not _flush_queued:
		_flush_queued = true
		HighContrastWalk._flush.call_deferred()


## Restyles every Control queued since the last flush (headless tests call it to settle).
static func flush() -> void:
	_flush()


static func _flush() -> void:
	_flush_queued = false
	var batch := _pending
	_pending = []
	if not Settings.high_contrast:
		return
	for n in batch:
		if is_instance_valid(n) and (n as Node).is_inside_tree():
			restyle(n as Control, true)


static func _on_settings_changed() -> void:
	var tree := Engine.get_main_loop() as SceneTree
	if tree == null:
		return
	var hc := Settings.high_contrast
	if hc == _walked_hc and (not hc or is_equal_approx(Settings.text_scale, _walked_scale)):
		return
	_walked_hc = hc
	_walked_scale = Settings.text_scale
	walk(tree.root, hc)
