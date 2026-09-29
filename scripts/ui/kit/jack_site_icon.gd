class_name JackSiteIcon
extends Control
## ANIM-R6 B13: the Site a jack connects to, as the City Grid draws it: the tier hexagon
## with its "T2" (CityMapOverlay.draw_icon) and the tier pips under it (draw_tier), beside
## the destination's name on the jack's cover. Draw only; hidden when there is no tier.

## The pips' height under the icon as a share of the side, and their scale per px of side.
const PIPS_SHARE := 0.22
const PIP_SCALE_PER_PX := 0.03

var tier: int = 0
var color: Color = Palette.NET_CYAN


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE


## Shows tier `p_tier` (0: nothing) in `p_color` in a square of `side` px.
func show_tier(p_tier: int, side: float, p_color: Color) -> void:
	tier = p_tier
	color = p_color
	custom_minimum_size = Vector2(side, side)
	size = custom_minimum_size
	visible = tier > 0
	queue_redraw()


func _draw() -> void:
	if tier <= 0:
		return
	var side := minf(size.x, size.y)
	var pips := side * PIPS_SHARE
	var r := (side - pips) * 0.5
	CityMapOverlay.draw_icon(self, CityMapOverlay.KIND_TIER, Vector2(size.x * 0.5, r), r, color, CityMapOverlay.tier_text(tier))
	CityMapOverlay.draw_tier(self, Vector2(size.x * 0.5, side - pips * 0.4), tier, color, side * PIP_SCALE_PER_PX)
