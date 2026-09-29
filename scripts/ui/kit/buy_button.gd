class_name BuyButton
extends StickerButton
## A shop item's buy button (H23 S8: the Modem's price tags and the BUY / SHRED notes on
## its sign did not read as buttons): a taped yellow sticker at the foot of the item's
## card or tile reading "BUY ⊙45" (the coin drawn), "BUY ⊙100-150" when the price depends
## on the slot. The item stays the focus stop (pad focus walks the items as before);
## pressing the sticker presses the item. Its lettering follows the item's text size and
## shrinks to the item's width. View only.
##
## Art pass W8c (ART_BIBLE §6.4, §6.7, §3.7, critique 52/55, §5 "BUY 76 A"):
## - In the Modem a sticker is always a button: every BUY / SHRED sticker lifts and flaps
##   on hover and focus, and presses its item (the sign's decorative notes are gone).
## - Out of reach: W2's locked state (the paper kept, a `DISABLED` edge and the lock badge)
##   and the reason on the sticker, "NEED 141 · HAVE 120", never a paler pink.
## - The pad's button is its own element (a PadGlyph beside the sticker while the item has
##   focus and a pad is in use), never letters inside the price ("BUY 76 A").

## Lettering and height at the item's text scale 1.0 (px), the least lettering (§4.2: the
## caption step), and the margin kept from the item's sides and foot (px).
const BUY_FONT := 13
const BUY_HEIGHT := 22.0
const MIN_FONT := UiTheme.CAPTION
const EDGE := 4.0
## The coin's radius and the gap after it at scale 1.0 (px).
const COIN_R := 5.5
const COIN_GAP := 3.0
## A second line's step as a share of the lettering's height (marker lines sit close).
const LINE_SHARE := 0.8
## One line may shrink to this share of the text size before the words go on two lines.
const TWO_LINES_BELOW := 0.85
## The pad glyph's gap from the sticker (px at 1.0), and the locked edge's width (px).
const GLYPH_GAP := 4.0
const LOCKED_EDGE := 1.5
## The separator of NEED and HAVE (the refusal's own words, ART_BIBLE 6.7).
const NEED_SEP := " · "

var host: ZineCard = null
var verb: String = "BUY"
## The Cycles in hand (the screen sets it): an item out of reach says NEED n · HAVE m.
## -1: unknown (the sticker only shows the lock).
var have: int = -1
## The pad button beside the sticker (shown while its item has pad focus).
var glyph: PadGlyph = null
var _font_px: int = BUY_FONT
## H24 S10: the words on two lines (the verb over the price) when one line would have to
## shrink below the text size to fit the item ("BUY 100-150" on a slice tile at 1.6).
var _lines: PackedStringArray = PackedStringArray()


func _init(p_host: ZineCard = null, p_verb: String = "BUY") -> void:
	host = p_host
	verb = p_verb
	super("", Palette.NOTE_YELLOW, 0.0)
	name = "Buy"
	focus_mode = Control.FOCUS_NONE
	mouse_filter = Control.MOUSE_FILTER_STOP
	pressed.connect(_press_host)
	glyph = PadGlyph.new(maxi(0, PadGlyph.button_for_action(&"ui_accept")))
	glyph.name = "PadGlyph"
	glyph.visible = false
	add_child(glyph)
	if host != null:
		host.resized.connect(refit)
		host.focus_entered.connect(refit)
		host.focus_exited.connect(refit)
		host.mouse_entered.connect(func() -> void: _hot = true; queue_redraw(); flap(true))
		host.mouse_exited.connect(func() -> void: _hot = false; queue_redraw(); flap(false))
		host.focus_entered.connect(flap.bind(true))
		host.focus_exited.connect(flap.bind(false))
	Settings.hints_changed.connect(refit)


## The sticker flaps on its tape while its item is hovered or focused (Animation pass
## ANIM-6: `note_flap` degrees about its top edge) and settles back after.
func flap(on: bool) -> void:
	if not is_inside_tree():
		return
	pivot_offset = Vector2(size.x * 0.5, 0.0)
	Motion.run(&"note_flap", self, ^"rotation_degrees", Motion.amplitude(&"note_flap") if on and not disabled else 0.0)


func _ready() -> void:
	refit()


## True when the item is out of reach for want of Cycles (its price over `have`).
func short_of_money() -> bool:
	return host != null and host.disabled and have >= 0 and host.price > have


## The words on the sticker: "BUY 45", or "NEED 45 · HAVE 12" when the Cycles don't reach
## (art pass W8c: the pad button is a glyph of its own, never in these words).
func label_text() -> String:
	if short_of_money():
		return tr("NEED %d · HAVE %d") % [host.price, have]
	return ("%s %s" % [tr(verb), host.price_words() if host != null else ""]).strip_edges()


## The pad button that buys (shown while the item has focus and a pad is in use), as its
## glyph's name ("A"; "" when none shows).
func pad_key() -> String:
	if not Settings.pad_active or host == null or not host.has_focus():
		return ""
	return Settings.key_text(&"ui_accept")


func _scale() -> float:
	return host.text_scale if host != null else Settings.text_scale


## The line sets the words may take, in the order tried: one line, then the verb over the
## price (or NEED over HAVE), then a price range split after its dash ("100-" over "150").
func _options(t: String) -> Array[PackedStringArray]:
	var options: Array[PackedStringArray] = []
	var sep := t.find(NEED_SEP.strip_edges())
	if short_of_money() and sep > 0:
		options.append(PackedStringArray([t.substr(0, sep).strip_edges(), t.substr(sep + 1).strip_edges()]))
		return options
	var gap := t.find(" ")
	if gap > 0:
		var rest := t.substr(gap + 1).strip_edges()
		options.append(PackedStringArray([t.substr(0, gap), rest]))
		var dash := rest.find("-")
		if dash > 0:
			options.append(PackedStringArray([t.substr(0, gap), rest.substr(0, dash + 1), rest.substr(dash + 1).strip_edges()]))
	return options


func _fit() -> void:
	var s := _scale()
	text = label_text()
	var room := (host.size.x if host != null and host.size.x > 0.0 else 9999.0) - EDGE * 2.0
	var full := roundi(BUY_FONT * s)
	_lines = PackedStringArray([text])
	_font_px = full
	while _font_px > MIN_FONT and _needed(_font_px, s) > room:
		_font_px -= 1
	for lines in _options(text):
		if _font_px >= roundi(full * TWO_LINES_BELOW):
			break
		var fs2 := full
		while fs2 > MIN_FONT and _needed_lines(lines, fs2, s) > room:
			fs2 -= 1
		if fs2 > _font_px or (fs2 == _font_px and _needed_lines(lines, fs2, s) < _needed(_font_px, s)):
			_lines = lines
			_font_px = fs2
	var h := BUY_HEIGHT * s + Palette.marker().get_height(_font_px) * LINE_SHARE * (_lines.size() - 1)
	var w := minf(room, _needed_lines(_lines, _font_px, s))
	custom_minimum_size = Vector2(w, h)
	size = custom_minimum_size
	if host != null:
		position = Vector2((host.size.x - size.x) * 0.5, host.size.y - size.y - EDGE * s)
		disabled = host.disabled
		tooltip_text = host.tooltip_text
	_place_glyph()


## The pad glyph beside the sticker while its item has pad focus (never inside the price).
func _place_glyph() -> void:
	if glyph == null:
		return
	glyph.visible = pad_key() != ""
	if glyph.visible:
		glyph.button = maxi(0, PadGlyph.button_for_action(&"ui_accept"))
		glyph.size = glyph.custom_minimum_size
		glyph.position = Vector2(size.x + GLYPH_GAP * _scale(), (size.y - glyph.size.y) * 0.5)


## The width the sticker needs at lettering `fs`.
func _needed(fs: int, s: float) -> float:
	return _needed_lines(PackedStringArray([text]), fs, s)


## The width the sticker needs for `lines` at lettering `fs` (the widest line).
func _needed_lines(lines: PackedStringArray, fs: int, s: float) -> float:
	var w := 0.0
	for l in lines:
		w = maxf(w, Palette.marker().get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	return (COIN_R * 2.0 + COIN_GAP) * s + w + PADDING * 0.6 * s


## The sticker's lines of words as drawn (one, or the verb over the price).
func shown_lines() -> PackedStringArray:
	return _lines


## The lettering size in use (px).
func lettering_px() -> int:
	return _font_px


## Re-measures and places the sticker (the item moved, took focus, or the device changed).
func refit() -> void:
	_fit()
	queue_redraw()
	if host != null:
		host.queue_redraw()  # its text keeps clear of the sticker's height (H24 S10)


func _press_host() -> void:
	if host != null and not host.disabled:
		host.pressed.emit()


func _draw() -> void:
	var s := _scale()
	var rr := Rect2(Vector2.ZERO, size)
	var off := disabled or (host != null and host.disabled)
	if _hot and not off:
		draw_rect(rr.grow(HOT_GROW), Color(Palette.FOCUS, HOT_ALPHA))
	draw_rect(Rect2(rr.position + SHADOW_OFFSET * 0.7, rr.size), Palette.SHADOW)
	# W2's locked state (§6, §3.7): the paper kept (lighter stock), a DISABLED edge and the
	# lock badge; the words stay INK at full contrast.
	draw_rect(rr, Palette.PAPER_ALT if off else paper)
	if off:
		draw_rect(rr, Palette.DISABLED, false, LOCKED_EDGE)
		StyleBoxLocked.draw_lock_badge(get_canvas_item(), Vector2(rr.end.x, rr.position.y), StyleBoxLocked.BADGE_R * s)
	else:
		draw_rect(rr, Color(Palette.INK, EDGE_ALPHA), false, 1.0)
	if Settings.high_contrast:
		draw_rect(rr, Palette.INK, false, LOCKED_EDGE)
	var ink := Palette.INK
	var coin := Vector2(PADDING * 0.3 * s + COIN_R * s, rr.size.y * 0.5)
	StatIcon.draw(self, coin, COIN_R * s, StatIcon.CYCLES, ink)
	var fs := _font_px
	var x := coin.x + COIN_R * s + COIN_GAP * s
	var lh := Palette.marker().get_height(fs) * LINE_SHARE
	var first := (rr.size.y - lh * (_lines.size() - 1) + Palette.marker().get_ascent(fs) - Palette.marker().get_descent(fs)) * 0.5
	for i in _lines.size():
		draw_string(Palette.marker(), Vector2(x, first + i * lh), _lines[i], HORIZONTAL_ALIGNMENT_LEFT, rr.size.x - x, fs, ink)
