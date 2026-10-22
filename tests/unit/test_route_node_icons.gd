extends GutTest
## Nodes round 2 (designer pick: direction C "slap-tag"): REST, WORKSHOP and CACHE have their own route stickers (own silhouette, own cut-off
## look), the key lists them, and CACHE's hue is clear of every other kind hue under normal, protan, deutan and tritan vision. The kind
## hues are Palette tokens (RouteInk.accent_of), and the three room glow colours in street_route.tres equal them (a sticker and its room
## are one colour).

const NEW_KINDS: Array[String] = [CityMapOverlay.KIND_REST, CityMapOverlay.KIND_WORKSHOP, CityMapOverlay.KIND_CACHE]
const OLD_KINDS: Array[String] = [CityMapOverlay.KIND_FIGHT, CityMapOverlay.KIND_ELITE, CityMapOverlay.KIND_EVENT, CityMapOverlay.KIND_SHOP, CityMapOverlay.KIND_RACK]
## The least dE76 between CACHE's hue and every other kind hue or ring colour (designer, nodes round 2), per vision type.
const CACHE_MIN_DE := 30.0
## The least silhouette difference at the legend's size: the new stickers' soft IoU against each shipped sticker stays under it
## (the shipped discs score 0.98 against each other; the slap-tags 0.53 to 0.75).
const MAX_IOU := 0.80
const LEGEND_PX := 17
## Machado 2009, severity 1, linear RGB.
const MACHADO := {
	"protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
	"deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
	"tritan": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}


func test_each_new_kind_has_its_own_sticker_and_cut_off_look() -> void:
	var seen := {}
	for kind in NEW_KINDS + OLD_KINDS:
		var base := RouteOverlay.sticker_art(kind)
		var past := RouteOverlay.sticker_art(kind, true)
		assert_not_null(base, "%s has a sticker" % kind)
		assert_not_null(past, "%s has a cut-off look" % kind)
		assert_false(seen.has(base.resource_path), "%s's sticker is its own file" % kind)
		seen[base.resource_path] = kind
		assert_true(RouteOverlay.STICKER_ART.has(kind), "%s is in STICKER_ART" % kind)
	for kind in NEW_KINDS:
		assert_true(StreetRouteOverlay.ART_OF.has(kind), "the street overlay draws %s from the art, not the provisional D4 shapes" % kind)
		assert_eq(RouteOverlay.sticker_art(kind).get_size(), Vector2(130, 130), "%s keeps the family's canvas" % kind)


func test_the_cache_legend_glyph_is_its_own_file_and_the_others_are_not() -> void:
	assert_ne(RouteOverlay.sticker_art(CityMapOverlay.KIND_CACHE, false, true).resource_path, RouteOverlay.sticker_art(CityMapOverlay.KIND_CACHE).resource_path,
			"CACHE's 16.8 px key glyph is a simplified file (fewer, fatter bricks)")
	assert_eq(RouteOverlay.sticker_art(CityMapOverlay.KIND_REST, false, true), RouteOverlay.sticker_art(CityMapOverlay.KIND_REST))
	assert_eq(RouteOverlay.sticker_art(CityMapOverlay.KIND_CACHE, true, true), RouteOverlay.sticker_art(CityMapOverlay.KIND_CACHE, true), "the cut-off look has one file")


func test_the_legend_lists_rest_workshop_and_cache() -> void:
	var legend: RouteLegend = autofree(RouteLegend.new(RouteLegend.ORDER))
	for kind in NEW_KINDS:
		assert_true(legend.kinds.has(kind), "the key lists %s" % kind)
		assert_not_null(legend.strip.get_node_or_null("Kind_%s" % kind), "%s has its row" % kind)
	var nodes: Array = []
	for kind in NEW_KINDS:
		nodes.append({"kind": kind})
	assert_eq(RouteLegend.kinds_of(nodes), NEW_KINDS, "a route with only the new kinds lists them in the key's order")


func test_the_new_silhouettes_are_not_the_shipped_discs() -> void:
	# The 16 px rule on outline (ART_BIBLE 5.2), at the legend's size, against every shipped sticker.
	for kind in NEW_KINDS:
		var mine := _alpha_mask(RouteOverlay.sticker_art(kind, false, true))
		for other in OLD_KINDS:
			var iou := _iou(mine, _alpha_mask(RouteOverlay.sticker_art(other)))
			assert_lt(iou, MAX_IOU, "%s against %s: soft IoU %.2f" % [kind, other, iou])


func test_the_kind_hues_are_palette_tokens() -> void:
	assert_eq(RouteInk.accent_of(CityMapOverlay.KIND_REST), Palette.ROUTE_REST)
	assert_eq(RouteInk.accent_of(CityMapOverlay.KIND_WORKSHOP), Palette.ROUTE_WORKSHOP)
	assert_eq(RouteInk.accent_of(CityMapOverlay.KIND_CACHE), Palette.ROUTE_CACHE)
	var rooms: Dictionary = StreetRouteConfigData.shipped().rooms["colors"]
	for kind in NEW_KINDS:
		var c := _room_colour(rooms[kind])
		assert_lt(absf(c.r - RouteInk.accent_of(kind).r) + absf(c.g - RouteInk.accent_of(kind).g) + absf(c.b - RouteInk.accent_of(kind).b), 3.0 / 255.0,
				"the %s room glows in the sticker's hue" % kind)


func test_cache_is_clear_of_every_kind_hue_for_every_vision() -> void:
	var cache := Palette.ROUTE_CACHE
	var rest: Dictionary = {}
	for kind in OLD_KINDS + [CityMapOverlay.KIND_REST, CityMapOverlay.KIND_WORKSHOP]:
		rest["kind " + kind] = RouteInk.accent_of(kind)
	var rooms: Dictionary = StreetRouteConfigData.shipped().rooms["colors"]
	for k in ["router", "terminal", "mainframe", "server_rack"]:
		rest["room " + k] = _room_colour(rooms[k])
	rest["room elite"] = _room_colour(StreetRouteConfigData.shipped().rooms["elite"])
	rest["ring walked"] = RouteInk.RING_WALKED
	rest["ring next"] = RouteInk.RING_AVAILABLE
	rest["ring not yet"] = RouteInk.RING_UNAVAILABLE
	rest["Cell pink"] = Palette.CELL_PINK
	for vision in ["normal", "protan", "deutan", "tritan"]:
		for who in rest:
			var de := _de76(cache, rest[who], vision)
			assert_gt(de, CACHE_MIN_DE, "CACHE vs %s under %s: dE %.1f" % [who, vision, de])


# --- helpers -------------------------------------------------------------------------------------------------------

func _room_colour(a: Array) -> Color:
	return Color(float(a[0]), float(a[1]), float(a[2]))


func _alpha_mask(tex: Texture2D) -> PackedFloat32Array:
	var img := tex.get_image()
	img.decompress()
	img.resize(LEGEND_PX, roundi(float(LEGEND_PX) * img.get_height() / img.get_width()), Image.INTERPOLATE_LANCZOS)
	var canvas := Image.create(LEGEND_PX + 4, LEGEND_PX + 4, false, Image.FORMAT_RGBA8)
	canvas.blit_rect(img, Rect2i(Vector2i.ZERO, img.get_size()), Vector2i((canvas.get_width() - img.get_width()) / 2, (canvas.get_height() - img.get_height()) / 2))
	var out := PackedFloat32Array()
	for y in canvas.get_height():
		for x in canvas.get_width():
			out.append(canvas.get_pixel(x, y).a)
	return out


func _iou(a: PackedFloat32Array, b: PackedFloat32Array) -> float:
	var inter := 0.0
	var union := 0.0
	for i in a.size():
		inter += minf(a[i], b[i])
		union += maxf(a[i], b[i])
	return inter / maxf(0.000001, union)


func _lin(c: float) -> float:
	return c / 12.92 if c <= 0.04045 else pow((c + 0.055) / 1.055, 2.4)


func _lab(c: Color, vision: String) -> Vector3:
	var lin := Vector3(_lin(c.r), _lin(c.g), _lin(c.b))
	if vision != "normal":
		var m: Array = MACHADO[vision]
		lin = Vector3(Vector3(m[0][0], m[0][1], m[0][2]).dot(lin), Vector3(m[1][0], m[1][1], m[1][2]).dot(lin), Vector3(m[2][0], m[2][1], m[2][2]).dot(lin))
		lin = Vector3(clampf(lin.x, 0.0, 1.0), clampf(lin.y, 0.0, 1.0), clampf(lin.z, 0.0, 1.0))
	var x := (0.4124 * lin.x + 0.3576 * lin.y + 0.1805 * lin.z) / 0.95047
	var y := 0.2126 * lin.x + 0.7152 * lin.y + 0.0722 * lin.z
	var z := (0.0193 * lin.x + 0.1192 * lin.y + 0.9505 * lin.z) / 1.08883
	var f := func(t: float) -> float: return pow(t, 1.0 / 3.0) if t > 0.008856 else 7.787 * t + 16.0 / 116.0
	return Vector3(116.0 * f.call(y) - 16.0, 500.0 * (f.call(x) - f.call(y)), 200.0 * (f.call(y) - f.call(z)))


func _de76(a: Color, b: Color, vision: String) -> float:
	return _lab(a, vision).distance_to(_lab(b, vision))
