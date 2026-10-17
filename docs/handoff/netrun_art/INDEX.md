# Netrun art: index (not copied; pinned to art-pass@7f021c21)

Fetch with: git show 7f021c21:<path>. Never checkout or merge art-pass.

## Approved images and video (README section 8)
- art-pass@7f021c21:docs/concepts/route_map_graph/storyboard/storyboard.mp4
- art-pass@7f021c21:docs/concepts/route_map_graph/storyboard/storyboard_v3_dive.mp4
- art-pass@7f021c21:docs/concepts/route_map_graph/storyboard/storyboard_sheet.jpg
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_halcyon/H_overview_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_halcyon/H_decision_E_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_halcyon/H_hover_E_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_orbital/H_overview_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_orbital/H_decision_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_orbital/H_hover_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_rebel_cell/H_overview_v3.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_rebel_cell/H_decision_v3.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_rebel_cell/H_hover_v3.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_solace/H_overview_v4.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_solace/H_decision_v4.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_solace/H_hover_v4.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_meridian_v3/H_overview_v3.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_meridian_v3/H_decision_v3.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_meridian_v3/H_hover_v3.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_tethys/H_overview_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_tethys/tethys_closeup_v2.png
- art-pass@7f021c21:docs/concepts/route_map_graph/street_r2/stills/01_OVERVIEW_closed_s1.png
- art-pass@7f021c21:docs/concepts/route_map_graph/street_r2/stills/02_DECISION_closed_s1.png
- art-pass@7f021c21:docs/concepts/route_map_graph/street_r2/stills/03_OVERVIEW_route_overlay_s1.png
- art-pass@7f021c21:docs/concepts/route_map_graph/street_r2/stills/04_OVERVIEW_closed_seed2.png
- (red states: art-pass@7f021c21:docs/concepts/route_map_graph/hq_rebel_cell/H_red_*_v3.png)
- art-pass@7f021c21:docs/concepts/city_all_corps/city_all_corps_night.png
- art-pass@7f021c21:docs/concepts/city_all_corps/city_all_corps_labeled.png
- art-pass@7f021c21:docs/concepts/city_all_corps/city_all_corps_day.png
- art-pass@7f021c21:docs/concepts/city_all_corps/zoning_map.png
- art-pass@7f021c21:docs/concepts/city_planner/plan_A2_horseshoe_bay.png
- art-pass@7f021c21:docs/concepts/city_planner/map_A2_horseshoe_bay.png
- MISSING upstream: Tethys decision and hover finals

## Other text sources (not copied)
- art-pass@7f021c21:docs/concepts/city_all_corps/NOTES.md
- art-pass@7f021c21:docs/concepts/city_planner/city_A2.json
- art-pass@7f021c21:docs/concepts/city_planner/design_A2_horseshoe_bay.md
- art-pass@7f021c21:docs/concepts/route_map_graph/proc_vs_custom/COMPARISON.md
- art-pass@7f021c21:docs/concepts/route_map_graph/street_r2/metrics_r2.md
- art-pass@7f021c21:docs/concepts/route_map_graph/street_r2/NOTES.md

## Concept scripts to port (pinned to 7f021c21)
- art-pass@7f021c21:docs/concepts/route_map_graph/storyboard/scripts/sb_onecity.py
- art-pass@7f021c21:docs/concepts/route_map_graph/side_view/v3_aaa/scripts/cam_rig.py
- art-pass@7f021c21:docs/concepts/route_map_graph/storyboard/scripts/cam_rig.py
- art-pass@7f021c21:docs/concepts/city_all_corps/scripts/zoning.py
- art-pass@7f021c21:docs/concepts/city_all_corps/scripts/zoning_a2.py
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_halcyon/scripts/hq_landmark.py
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_meridian_v3/scripts/meridian_landmark.py
- art-pass@7f021c21:docs/concepts/route_map_graph/hq_tethys/scripts/tethys_landmark.py
- Not found: any HK/*.py (no such path in 7f021c21). Other cam_rig variants: side_view/v3_aaa/r2, r3, v3_dynamic
- Other hq_*/scripts/*_landmark.py: only the three above exist

## Path abbreviations and landmark sources (art director, 2026-10-16)
- `HK/` = `docs/concepts/route_map_graph/hq_meridian/scripts/hq_kit/` (`__init__`, city_ring, downtown, layout, lod, orbit, section, states). Port from hq_meridian; the occlusion rule is in `section.py`. Other abbreviations (SB/, V3D/, HM/, HQ_<corp>/) are defined in PIPELINE_SPEC §0.
- Landmarks: only Meridian v3 and Tethys are standalone module files. Halcyon / Solace / Orbital / Aurelian / Rebel Cell are functions in `city_all_corps/scripts/landmarks.py` (city scale); the HQ-netrun-scale builders are `route_map_graph/hq_<corp>/scripts/hq_build*.py`.
- Art-pass queue (after the reset, per D8): extract each landmark into a standalone `<corp>_landmark.py` with the build(ctx) contract, and export glb.
