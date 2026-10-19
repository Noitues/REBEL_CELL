# NA-11 layout rules (W1)

Python oracle: `tools/netrun_art/layout.py` (`apply_rules`). GDScript twin: `scripts/netrun_art/netrun_art_layout_rules.gd`
(`NetrunArtLayoutRules`). Numbers: `layout.LAYOUT_RULES` + `layout.R2_RULES`, exported to `content/config/netrun_art.tres`
field `layout_rules` by `python -m netrun_art.gen_twin_config` (the twin-config route; no literal 8 or 6 in code).
Live use: `CityModel.finish` -> `CityLayoutRuler.apply` (switch `CityConfig.layout_rules_on`), full city only.

Order (PIPELINE_SPEC §3.2): 1. frontage minimum + border width, 2. `frontage.silhouette`, 3. `horizon.break`.

| Rule | Spec | Constant (config key) | Code |
|---|---|---|---|
| Frontage minimum | §3.2 `frontage_min_floors` | `frontage_min_floors` 6, plus `abs(key) % 3` jitter | `apply_layout_rules` (3.2 sb_onecity.py:134-138) |
| Border street width | §3.2 `border_street_width` | `border_street_width` 8.0, `base_street_width` 6.0, `face_tol` 0.05; each face steps back `(8-6)/2` | `apply_layout_rules` |
| Frontage band, extension | §3.3 | `layout.front_band` (0.8, 6.5), `layout.extend` (12, 60) | `frontage_rows` |
| Frontage silhouette | §13.1 `frontage.silhouette`; r2_config.py `RULES_R2["frontage.silhouette"]`, r2_rules.py:115-215 | `silhouette.floors_low/mid/tall`, `rhythm_p`, `height_step_min` 2, `triple_span_min` 6, `rotate_run` 2, `route_sign_floors` 3 | `frontage_silhouette` |
| Hero sign zone | §9.1 hero_sign_rule; r2_config.py `route_sign_floors` | `route_sign_floors` 3, `hero_sign_rule` {blade, band, palette} | route column lifts to top room floor + 3 (`route_tops`); the sign count and palette stay in `dress.signs` / `NetrunArtDress` (one blade + band per column, palette alternating) |
| Horizon break | §13.1 `horizon.break`; r2_rules.py:216-251 | `horizon.spikes_min/max` 3..5, `spike_k` 2.0, `backdrop_band` (24, 170), `spike_min_w` 4, `spike_spacing_bu` 30, `pick_jitter` 25 | `horizon_break` |
| Unique ids | §3.2 `unique_building_id` | `bid` "i:j", "hq:<corp>" | `NetrunArtExport.city_json`, checked by `bid_conflicts`, `hq_overlaps` |

Changes from the art-pass r2 originals (all logged in DECISIONS 2026-10-19 NA-11): draws are splitmix64 art streams
(`frontage`/`bid`, `spikes`/link ids, `spike_pick`/`bid`), not Python's `random`; the sightline term (needs the overview camera) and
the screen-projected spike height (camera) are dropped, spikes reach `max(spike_k * median, top)`; a building with stacked parts is
never changed; the reference street of the horizon pass is the first leg of the first link; the fixed city counts every Grid link as a
border street (state ignored). Source revision: art-pass `ded90765` (r2 scripts, this repo's history); `ed8675a8` was not present.
