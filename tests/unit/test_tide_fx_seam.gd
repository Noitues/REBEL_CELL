extends GutTest
## B-082 (tier fast): the tide raid screen draws through TideFx. The map layer, the glyph view, the odds bar and the screen hold no raw draw
## call, StyleBox builder or theme override of their own (the art pass owns tide_fx.gd and tide_look.tres); the shipped look validates and
## ships the art hooks off (shake strength 0, so the pixels are today's); the camera shake is a no-op at strength 0; the wash helper adds a
## full-rect ColorRect over its host.

const VIEW_FILES: Array[String] = [
	"res://scripts/ui/raid/tide_raid_layer.gd",
	"res://scripts/ui/raid/tide_raid_screen.gd",
	"res://scripts/ui/raid/tide_glyph_view.gd",
	"res://scripts/ui/raid/tide_odds_bar.gd",
]
const FORBIDDEN: Array[String] = ["draw_circle(", "draw_arc(", "draw_line(", "draw_rect(", "draw_polyline(", "draw_colored_polygon(", "draw_string(",
	"UiTheme.box(", "add_theme_stylebox_override(", "add_theme_font_size_override(", "add_theme_color_override("]


func test_views_hold_no_raw_drawing() -> void:
	for path in VIEW_FILES:
		var text := FileAccess.get_file_as_string(path)
		assert_ne(text, "", path)
		for word in FORBIDDEN:
			var hits := 0
			for line in text.split("\n"):
				var t := line.strip_edges()
				if not t.begins_with("#") and t.contains(word) and not t.contains("TideFx."):
					hits += 1
			assert_eq(hits, 0, "%s still draws with %s" % [path, word])


func test_look_validates_and_hooks_ship_off() -> void:
	var lk := TideFx.look()
	assert_not_null(lk)
	assert_eq(lk.validate().size(), 0, str(lk.validate()))
	assert_eq(lk.home_hit_shake_strength, 0.0)
	assert_eq(lk.city_lost_shake_strength, 0.0)
	assert_true(TideLookData.new().validate().is_empty())


func test_shake_is_off_at_zero_strength() -> void:
	CityMapCamera.shake(0.0, 0.5)
	assert_eq(CityMapCamera.shake_offset(), Vector2.ZERO)


func test_wash_fills_its_host() -> void:
	var host: Control = add_child_autofree(Control.new())
	host.size = Vector2(200, 100)
	var w := TideFx.wash(host, TideFx.lost_wash_color())
	assert_eq(w.get_parent(), host)
	assert_eq(w.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq(w.color, TideFx.lost_wash_color())
