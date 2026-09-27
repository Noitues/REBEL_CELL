class_name BuyButton
extends StickerButton
## A shop item's buy button (H23 S8: the Modem's price tags and the BUY / SHRED notes on
## its sign did not read as buttons): a taped yellow sticker at the foot of the item's
## card or tile reading "BUY ⊙45" (the coin drawn), "BUY ⊙100-150" when the price depends
## on the slot, and the pad button that presses it ("A") while its item has focus and a
## pad is in use. The item stays the focus stop (pad focus walks the items as before);
## pressing the sticker presses the item. Its lettering follows the item's text size and
## shrinks to the item's width. View only.

## Lettering and height at the item's text scale 1.0 (px), the least lettering (px), and
## the margin kept from the item's sides and foot (px).
const BUY_FONT := 13
const BUY_HEIGHT := 22.0
const MIN_FONT := 8
const EDGE := 4.0
## The coin's radius and the gap after it at scale 1.0 (px).
const COIN_R := 5.5
const COIN_GAP := 3.0

var host: ZineCard = null
var verb: String = "BUY"
var _font_px: int = BUY_FONT


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
		host.mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
		host.mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	Settings.hints_changed.connect(refit)


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
	var room := (host.size.x if host != null and host.size.x > 0.0 else 9999.0) - EDGE * 2.0
	_font_px = roundi(BUY_FONT * s)
	while _font_px > MIN_FONT and _needed(_font_px, s) > room:
		_font_px -= 1
	var w := minf(room, _needed(_font_px, s))
	custom_minimum_size = Vector2(w, BUY_HEIGHT * s)
	size = custom_minimum_size
	if host != null:
		position = Vector2((host.size.x - size.x) * 0.5, host.size.y - size.y - EDGE * s)
		disabled = host.disabled
		tooltip_text = host.tooltip_text


## The width the sticker needs at lettering `fs`.
func _needed(fs: int, s: float) -> float:
	return (COIN_R * 2.0 + COIN_GAP) * s + Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + PADDING * 0.6 * s


## Re-measures and places the sticker (the item moved, took focus, or the device changed).
func refit() -> void:
	_fit()
	queue_redraw()


func _press_host() -> void:
	if host != null and not host.disabled:
		host.pressed.emit()


func _draw() -> void:
	var s := _scale()
	var rr := Rect2(Vector2.ZERO, size)
	var off := disabled or (host != null and host.disabled)
	if _hot and not off:
		draw_rect(rr.grow(3), Color(Palette.CELL_ACID, 0.5))
	draw_rect(Rect2(rr.position + Vector2(2, 3), rr.size), Palette.SHADOW)
	draw_rect(rr, Palette.NOTE_PINK if off else paper)
	draw_rect(rr, Color(Palette.INK, 0.6), false, 1.0)
	var ink := Palette.INK if not off else Color(Palette.INK, 0.6)
	var coin := Vector2(PADDING * 0.3 * s + COIN_R * s, rr.size.y * 0.5)
	StatIcon.draw(self, coin, COIN_R * s, StatIcon.CYCLES, ink)
	var fs := _font_px
	var base := (rr.size.y + Palette.marker().get_ascent(fs) - Palette.marker().get_descent(fs)) * 0.5
	var x := coin.x + COIN_R * s + COIN_GAP * s
	draw_string(Palette.marker(), Vector2(x, base), text, HORIZONTAL_ALIGNMENT_LEFT, rr.size.x - x, fs, ink)
