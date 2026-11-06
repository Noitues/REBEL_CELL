# G1 round 28, branch art/tide-r28 (from 7e517839). Outputs in r28/: lookdev_vs_round6.jpg, compare_r27_r28.jpg (plan, hotspot, street A/B, seed 3), highway_closeup_r28.png, tools/.
**Honest state:** the city now reads as the round-6 family (cel bands, wobbly ink, faceted muted concrete, sparse square windows, neon rims, masts, coloured avenues), but it is NOT yet round 6's saturation and clarity: it is greyer and murkier (see lookdev_vs_round6.jpg), and the bay lost its deep navy. The look-dev iteration was short (about 8 hotspot renders). Notes of what is left are below.
**BUILD HAND-OFF (unchanged):** `CityView3D.art_look` (false in route_rig.gd); new in this round: it also gates the r6 look (`r6_look`).
## Existing machinery found first (no new shader written)
The raid city already had the toon bands (building ramp, 3 hard bands, tone jitter per facet, grime) and the wobbly ink in `city_post.gdshader` (normal / depth / id edges) at grade level 0; the realism grade (level 3) was what hid them. So the main change is to run the raid city's post at `r6_grade_level = 0`.
## Per-trait checklist against round 6
1. Faceted low-poly bodies (Cv2): PARTLY. Facets / tone jitter per triangle come from the existing legacy path (tone range widened to 0.72-1.22); facet sizes are the existing `facet_cell`. Not re-authored like round 6's lowpoly.py.
2. Cel (E): DONE. Hard 3-band ramp (lightened: 0.30 / 0.52 / 0.82 violet-grey) + ink from id / normal / depth edges; ink width scales with zoom (`r6_ink_width` x (0.6 + 160 / ortho)). The ink is heavier than round 6's and a bit rough on the tallest towers.
3. Shape variety: PARTLY. Sprawl shape weights from r25 (fewer plain boxes); hex / octagon / wedge forms exist in CityShapeKit; not extended this round. Heights unchanged (layout).
4. Colour: PARTLY. Concrete families mauve / teal / slate / dusty rose / grey (`r6_families`) x value 0.75-1.15, tinted 38 % toward the corp colour; windows small squares (pitch 3.0 x 3.6, size 1.1 x 0.95, share 20 %) pulled to the corp colour. Value is lighter and more varied than r27, but desaturated and grey-green overall.
5. Neon: DONE (rims, strips, masts). Corp roof-top rim outlines on 85 % of roofs, vertical edge strips on 30 %, antenna masts with crossed-diamond glowing tips on 40 % of buildings of 9 BU or more (`CityNeonKit.masts`). The mast tips tone-map to near white.
6. Streets: DONE, with A/B. `CityNeonKit.avenue_strips`: solid coloured strips down straight built-up street lots, one colour per street line (corp colours, cyan, amber, violet; no pink), no strips in highway zones, on the river or on open ground (audited, test `test_avenue_strips_audit_and_masts`). Strength config `r6_avenue_strength` (committed 0.8). A/B in compare_r27_r28.jpg row 3: 0.25 (dim, the designer's earlier dim grid) vs 1.4 (round-6 strength). The strips are pale pastel blocks with gaps at intersections, not round 6's saturated glowing avenues: needs more work. The old amber avenue lines are off.
7. Light spill: PARTLY. Sign / neon haze fans and street spills stay; the old street spill gain on the ground and buildings is set to 0 for this look. A pink-lilac haze remains on some open ground (source not removed).
8. Highways and traffic: PARTLY. A colour rail along both deck edges, one colour per highway (green / cyan / amber / violet); thin individual head / tail streaks, denser (gaps 2.5-11 BU); ramps are one-way (one colour, one direction), highways two-way; cars stay per-entity quads. NOT DONE: occlusion of traffic under upper decks is only what the opaque decks give for free; glow-only-on-top-deck is not implemented separately.
9. Night only, light rain: unchanged. No pink in gardens (the park ground stays green); pink is not used for avenues.
10. Realism grade bits dropped: DONE by grade level 0 (no lilac lift, hero glow or wet sheen); bloom reduced to 0.3 (`r6_bloom`).
## Not done / open
- Round 6's saturation and clarity: add a saturating grade and bring back the navy bay and the green ground tone that level 0 greyed.
- Toon bands are subtle on walls; more key-light contrast would read stronger.
- Avenue strips should join at intersections and be more saturated; masts should keep their colour (cap their gain).
- Shape kit extension (hex / octagon towers, wedges) and the traffic occlusion rule.
## Numbers
Plan luma p1/5/25/50/75/95 0.061 0.097 0.167 0.286 0.397 0.726 (lighter blacks, lower highlights than r27). GPU p95 9.55 ms (limit 12.57; the cel post is cheaper than the realism grade, so nothing was cut). Tests: neon kit 15, a2 16 + 2, grade 13, lamp plan 9, shape kit 7, city3d model 12 pass.
Slips: none (no `python -`).
