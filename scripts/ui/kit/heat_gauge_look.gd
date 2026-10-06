class_name HeatGaugeLook
extends Resource
## HQ-B (M14, designer ruling Q1 2026-10-05): the HEAT gauge's look, shared by every screen
## that shows it in the top bar's first slot (`HeatGauge`; the HQ's at `content/config/
## heat_gauge_look.tres`, the run's screens take the same file). Sizes in px at 1280x720 and
## text scale 1.0 (the HQ redesign's `heat_indicator.jpg`: a 370 x 64 tag at 1080). The gauge
## is a drawn object: it grows with the text only up to `scale_max` (STYLE 5.6). Read-only
## content: a view never writes it.

@export_group("Box")
## The gauge's size at text scale 1.0.
@export var size: Vector2 = Vector2(240, 44)
## Inner padding (left / right, top).
@export var pad: Vector2 = Vector2(7, 5)
## The drawn object's largest growth with the text size (STYLE 5.6: x1.3).
@export var scale_max: float = 1.3

@export_group("Lettering")
## The "HEAT" caption over the number, the number (bare Anton), the band word and "/max".
@export var caption_px: int = 10
@export var number_px: int = 28
@export var band_px: int = 14
@export var max_px: int = 10
## Width kept for the number column (share of the box's width).
@export var number_share: float = 0.19
## The band word's letter spacing (px).
@export var band_spacing: float = 1.5

@export_group("Strip")
## The five-band strip: its height, the threshold ticks' overhang, the Heat marker's size and
## how dim the part of a band above the Heat is (alpha).
@export var strip_height: float = 6.0
@export var tick_overhang: float = 4.0
@export var marker_px: float = 7.0
@export var unlit_alpha: float = 0.28

@export_group("Button")
## The caret that says the tag opens the Heat terminal (side, px) and the press's hover glow.
@export var caret_px: float = 7.0
@export var hover_alpha: float = 0.12
