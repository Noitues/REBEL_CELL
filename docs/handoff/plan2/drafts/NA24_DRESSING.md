# NA-24: street dressing, reveal tiers, district languages

Round W1 NA-24. Spec: PIPELINE_SPEC 3.5, 5.2b, 9.1, 9.6, 12.5; DERIVE_V2_REVIEW item 14 (lane `L = k speed T`).
Config: `content/config/dressing_config.tres` (`DressingConfigData`). Code: `NetrunArtDress` (twin of `dress.py`, byte-identical on
the 12 fixtures), `DressReveal`, `DressDistricts`, `DressPalette`, `DressKit` (meshes), `StreetDressing` (assembler, mounted by `RouteRig`).

## Asset classes and reveal (visibility_range from config, never literals)

Every group names a `reveal` asset + `tier` of `netrun_art.tres reveal` (spec 5.2b distances, "N1 calibration pending"); a tier that
the asset does not list is the big layer (always, range 0). A tier node is visible below `far` and fades over `far - near`
(`visibility_range_end`, `end_margin`, FADE_SELF). Tiers share position and footprint (one dress item, several MultiMesh groups).

| Class (group) | Source | reveal asset / tier |
|---|---|---|
| hero blade sign: neon block / panels + band / flicker overlay | dress `signs` | hero_sign 1 (always) / 2 / 3 |
| city blade sign: neon block / panels / flicker | route-side frontage rule (below) | street_sign 1 / 2 / 3 |
| shopfront strip / awning | frontage rule | shopfront 1 (always) / 2 |
| roof billboard: panel / content | frontage rule | billboard 1 (always) / 2 |
| kerb lamp: glow dot / ground spill | dress `lamps` | kerb_lamp 1 / 2 |
| traffic lane (individual streaks) | dress `streak_lanes` | traffic 2 |
| steam plume | frontage rule | steam_plume 1 |
| beam shaft, ground glow, facade wash | dress `beams`, `glows`, `washes` | big layer (always) |
| fog | `street_route.tres` density, NA-22 octave weights | fog_detail (NA-22 `octave_weights`) |

## City signage rules (no RNG stream)

Non-route buildings on the route side of the street, within `frontage.along_pad` of the street span and `frontage.depth_max` of the
street line, with a roof above `frontage.min_top`: an item is chosen when `FNV1a(class, bid) / 2^64 < share * hq_band.sign_mul`.
A pure hash of the building id: same layout seed, same city, same transforms; no new stream is registered. Faces come from the
building box nearest the street line (lots are axis aligned).

## District languages (placeholders until the art-pass assets land)

Palette sets: `neon_bay` and `sodium_teal` (look preset, spec 4.1), plus `placeholder_verdant` and `placeholder_ember`
(marked placeholders). District (`terr` of the building under an item) -> set: halcyon neon_bay, meridian sodium_teal, solace
placeholder_verdant, orbital placeholder_ember, rebel_cell neon_bay, the Sprawl neon_bay. Dress items keep palette ids only; the
set resolves an id to a colour at draw time (`DressPalette`).

## HQ-distance variance bands

Distance (BU) of a building from the nearest corporation HQ building: bands of `hq_bands` scale the city-sign share, the emission
and the plume share (inner dense and bright, outer sparse and dim).

## Always-alive loops (T = 4 s)

Lanes, beams, fog (NA-22), sign flicker and plumes are pure functions of `anim_t` (`dress_neon.gdshader`, `dress_plume.gdshader`:
integer cycles per loop). Under reduce effects the clock stops at `anim_t_frozen`.

## Budgets

<= 6 beams, <= 14 glow lights (the 6 fog-only lights stay; lamps use ground discs, not lights), 1080p GPU <= 14 ms, fog <= 3 ms.
