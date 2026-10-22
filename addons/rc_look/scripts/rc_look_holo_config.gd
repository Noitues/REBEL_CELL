class_name RcLookHoloConfig
extends Resource
## LOOK-TOOLBOX module 15 (decrypted holo): every number of the holo look in one resource
## (addons/rc_look/config/look_holo.tres). Numbers that change with the quality tier or an accessibility flag (the RGB
## split, the blur, the band roll and strength, the glass alpha, the scanlines, the backing) live under module "holo"
## in look_quality.tres and come through RcLookQuality; this resource holds the rest, the same at every tier.

const DEFAULT_PATH := "res://addons/rc_look/config/look_holo.tres"

@export_group("Glass")
## The tint's share over the deep colour at the glass's foot, as a share of its share at the head (a grade).
@export var fill_foot_share: float = 0.7
## How much of the blurred city shows through: the city's brightness before it mixes with the glass.
@export var city_dim: float = 0.9
@export_group("Scanlines")
## Scanline period (px).
@export var scan_px: float = 4.0
@export_group("Bands")
## Slow bands down the panel: how many, the seconds of one pass, the falloff exponent of the trail, and where they
## stand when frozen (a share of one band period).
@export var band_count: float = 3.0
@export var band_seconds: float = 6.0
@export var band_trail: float = 2.5
@export var band_pose: float = 0.35
@export_group("Edge")
## The edge line (px), its outer glow (px) and how far the edge's ink is lifted toward white.
@export var edge_px: float = 2.0
@export var edge_glow_px: float = 7.0
@export var edge_lift: float = 0.45
@export_group("Seal")
## The cracked corp seal (px at radius 40, scaled with the radius): ring weights and the gap between the rings, the
## ring's and the disc's alpha, the two halves' offsets, the fracture (segments, sideways jitter as a share of the
## radius, width, glow width and alpha, side branches and their length as a share of the radius), the crest's share of
## the radius, the gap the fracture cuts in the ring (radians) and the seed (the jitter is a hash of it, never RNG).
@export var seal_ring_px: float = 3.0
@export var seal_ring_inner_px: float = 1.0
@export var seal_inner_gap: float = 6.0
@export var seal_ring_alpha: float = 0.85
@export var seal_disc_alpha: float = 0.16
@export var crack_left: Vector2 = Vector2(-4.0, 3.0)
@export var crack_right: Vector2 = Vector2(2.0, -3.0)
@export var crack_segments: int = 6
@export var crack_jitter: float = 0.16
@export var crack_px: float = 2.5
@export var crack_glow_px: float = 7.0
@export var crack_glow_alpha: float = 0.35
@export var crack_branches: int = 2
@export var crack_branch_len: float = 0.34
@export var crest_share: float = 0.62
@export var ring_gap: float = 0.22
@export var seal_seed: int = 7
