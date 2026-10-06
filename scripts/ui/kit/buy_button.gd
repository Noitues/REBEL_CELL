class_name BuyButton
extends StickerButton
## A shop item's buy button (H23 S8: the Mainframe's price tags and the BUY / SHRED notes on
## its sign did not read as buttons): a taped yellow sticker at the foot of the item's
## card or tile reading "BUY ⊙45" (the coin drawn), "BUY ⊙100-150" when the price depends
## on the slot, and the pad button that presses it ("A") while its item has focus and a
## pad is in use. The item stays the focus stop (pad focus walks the items as before);
## pressing the sticker presses the item. Its lettering follows the item's text size and
## shrinks to the item's width. View only.

## Lettering and height at the item's text scale 1.0 (px), the least lettering (px), and
## the margin kept from the item's sides and foot (px).
const BUY_FONT := 13
const BUY_HEIGHT := 28.0
const MIN_FONT := 8
const EDGE := 4.0
## The coin's radius and the gap after it at scale 1.0 (px).
const COIN_R := 5.5
const COIN_GAP := 3.0
## A second line's step as a share of the lettering's height (marker lines sit close).
const LINE_SHARE := 0.8
## ART-9 4A: the kraft tag art's left part (notch, hole, Cycles mark) and right edge (concept px),
## and the left part's width as a share of the tag's height.
const TAG_LEFT_PX := 58.0
const TAG_RIGHT_PX := 6.0
const TAG_LEFT_K := 58.0 / 46.0
## ART-9 4A: the padlock on a tag out of reach (radius, px at scale 1.0).
const LOCK_R := 4.5
## ART-9 4A: the host meta that hangs the tag at the item's top instead of its foot.
const TAG_AT_TOP := &"buy_tag_at_top"
## ART-9 4A: the host meta that hangs the tag under the item (a shop card, round 34 shop_v5).
const TAG_BELOW := &"buy_tag_below"
## ART-9 4A: the host metas that put the tag's centre at a spot (local) and turn it (radians).
const TAG_SPOT := &"buy_tag_spot"
const TAG_TURN := &"buy_tag_turn"
## ART-9 4A: the kraft tag's notched end (px at scale 1.0; the string hole sits in it).
const NOTCH := 12.0
## One line may shrink to this share of the text size before the words go on two lines.
const TWO_LINES_BELOW := 0.85

var host: ZineCard = null
var verb: String = "BUY"
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


## The words on the sticker: "BUY 45", and the pad button while its item has focus
## ("BUY 45  A").
func label_text() -> String:
	var t := ("%s %s" % [tr(verb), host.price_words() if host != null else ""]).strip_edges()
	var key := pad_key()
	return ("%s  %s" % [t, key]) if key != "" else t


## The pad button that buys (shown while the item has focus and a pad is in use).
func pad_key() -> String:
	if not Settings.pad_active or host == null or not host.has_focus():
		return ""
	return Settings.key_text(&"ui_accept")


func _scale() -> float:
	return host.text_scale if host != null else Settings.text_scale


func _fit() -> void:
	var s := _scale()
	text = label_text()
	# ART-9 4A: the kraft tag shows its price after the Cycles mark (r31lib.price_tag), and the pad
	# button while focused; the verb stays the button's words (its tip, its reader).
	var shown := tag_words()
	var room := (host.size.x if host != null and host.size.x > 0.0 else 9999.0) - EDGE * 2.0
	var full := roundi(BUY_FONT * s)
	_lines = PackedStringArray([shown])
	_font_px = full
	while _font_px > MIN_FONT and _needed(_font_px, s) > room:
		_font_px -= 1
	# More lines at a bigger size than one line allows: the verb, then the price (and key);
	# then a price range split after its dash ("100-" over "150").
	var options: Array[PackedStringArray] = []
	var dash := shown.find("-")
	if dash > 0:
		options.append(PackedStringArray([shown.substr(0, dash + 1), shown.substr(dash + 1).strip_edges()]))
	for lines in options:
		if _font_px >= roundi(full * TWO_LINES_BELOW):
			break
		var fs2 := full
		while fs2 > MIN_FONT and _needed_lines(lines, fs2, s) > room:
			fs2 -= 1
		if fs2 > _font_px:
			_lines = lines
			_font_px = fs2
	var h := BUY_HEIGHT * s + Palette.display().get_height(_font_px) * LINE_SHARE * (_lines.size() - 1)
	var w := minf(room, _needed_lines(_lines, _font_px, s))
	custom_minimum_size = Vector2(w, h)
	size = custom_minimum_size
	if host != null:
		# ART-9 4A: a slice on the stock wheel hangs its tag at its top (on the rim).
		var top: bool = host.get_meta(TAG_AT_TOP, false)
		position = Vector2((host.size.x - size.x) * 0.5, EDGE * s if top else host.size.y - size.y - EDGE * s)
		if host.get_meta(TAG_BELOW, false):
			# a shop card's tag hangs under the card (round 34 shop_v5), its top tied to the foot
			position.y = host.size.y - EDGE * s
		if host.has_meta(TAG_SPOT):
			# a wedge's tag hangs on its rim, turned with it (its centre at the spot)
			position = Vector2(host.get_meta(TAG_SPOT)) - size * 0.5
			pivot_offset = size * 0.5
			rotation = float(host.get_meta(TAG_TURN, 0.0))
		disabled = host.disabled
		tooltip_text = host.tooltip_text


## The width the sticker needs at lettering `fs`.
func _needed(fs: int, s: float) -> float:
	return _needed_lines(PackedStringArray([tag_words()]), fs, s)


## The width the tag needs to letter its words at the item's full text size on one line (px).
func full_width() -> float:
	var s := _scale()
	# the price alone (the pad button shown while focused may shrink it: the item never resizes on focus)
	return _needed_lines(PackedStringArray([host.price_words() if host != null else ""]), roundi(BUY_FONT * s), s)


## The words on the tag: the price (and the pad button while its item has focus).
func tag_words() -> String:
	var t := host.price_words() if host != null else ""
	var key := pad_key()
	return ("%s  %s" % [t, key]) if key != "" else t


## The width the sticker needs for `lines` at lettering `fs` (the widest line).
func _needed_lines(lines: PackedStringArray, fs: int, s: float) -> float:
	var w := 0.0
	for l in lines:
		w = maxf(w, Palette.display().get_string_size(l, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	return BUY_HEIGHT * s * TAG_LEFT_K + w + PADDING * 0.3 * s + LOCK_R * 2.5 * s


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
	# ART-9 4A (ART_BIBLE v2 §4.10): the concept's kraft price tag (r31lib.price_tag: kraft stock,
	# the notch, the string hole and the Cycles mark; MainframeArt "tag"), its middle stretched to
	# the price; out of reach the concept's red print ("tag_short") and, so it is never colour alone,
	# a padlock (naive-reader audit P2). S-CARDFACE (SHOP-04): no pencil strike: struck through, the
	# price read as "sold" rather than "not yet".
	var s := _scale()
	var rr := Rect2(Vector2.ZERO, size)
	var off := disabled or (host != null and host.disabled)
	var left := rr.size.y * TAG_LEFT_K
	if _hot and not off:
		draw_rect(rr.grow(3), Color(Palette.CELL_ACID, 0.55))
	# the string it hangs on (shop.tag_on)
	draw_line(Vector2(left * 0.25, rr.size.y * 0.5), Vector2(-left * 0.3, -rr.size.y * 0.6), Color(Palette.PAPER, 0.85), 1.2 * s, true)
	MainframeArt.draw_h3(self, "tag_short" if off else "tag", rr, TAG_LEFT_PX, TAG_RIGHT_PX)
	if off:
		var lk := rr.position + Vector2(rr.size.x - LOCK_R * s - 3.0 * s, rr.size.y * 0.5)
		draw_arc(lk + Vector2(0, -LOCK_R * 0.35 * s), LOCK_R * 0.6 * s, PI, TAU, 8, Palette.KRAFT_RED, 1.6 * s, true)
		draw_rect(Rect2(lk + Vector2(-LOCK_R, -LOCK_R * 0.35) * s, Vector2(LOCK_R * 2.0, LOCK_R * 1.35) * s), Palette.KRAFT_RED)
	var ink := Palette.KRAFT_RED if off else Palette.KRAFT_INK
	var f := Palette.display()
	var fs := _font_px
	var lh := f.get_height(fs) * LINE_SHARE
	var first := (rr.size.y - lh * (_lines.size() - 1) + f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	for i in _lines.size():
		draw_string(f, Vector2(left, first + i * lh), _lines[i], HORIZONTAL_ALIGNMENT_LEFT, rr.size.x - left, fs, ink)
