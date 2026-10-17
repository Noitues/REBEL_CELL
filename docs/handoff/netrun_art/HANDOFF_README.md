# Netrun art: hand-off package for the BUILD session

Prepared 2026-10-16 by the art-pass session (AD). Paths below are relative to `docs/concepts/` unless noted.
Spec: `route_map_graph/PIPELINE_SPEC.md` (cited as "spec §n").

## 1. Purpose and status

This package gives the build session what the art direction needs it to build: what, in what order, where the
rules are, and where the approved reference images are. The art direction is **approved by the designer**.

**Do not cut slices or start implementation until the designer approves this package.**

## 2. What to build, in priority order

| # | Item | Spec |
|---|---|---|
| 1 | Netrun art pipeline tools in `tools/netrun_art/` (does not exist yet): modules, data flow, acceptance checks | §2, §2.2, §2.3, §12 |
| 2 | Per-seed city and route generation, art side (derive the street netrun from the game's city, graph and seed; art seeds; layout input is the planner JSON schema) | §2.0, §2.0b, §3, §3.5, §3.5b |
| 3 | HQ netrun views for the 6 corps (shared kit, slots, per-corp landmark modules, canonical landmarks) | §8 (esp. 8.4-8.6d), §6.4 |
| 4 | Entry storyboard sequence (dive from the city into the netrun; animatic times are the game times) | §6.3, §10 |
| 5 | Occlusion rule (cut / ghost; Python and GDScript twins) | §7 |
| 6 | LOD reveal tiers (detail appears with camera distance) | §5.1, §5.2, §5.2b |
| 7 | Hover power cut (one 2D grade for street and HQ) | §9.4 |
| 8 | Edge arrow for an off-screen TARGET (no arrow above 50 % visible) | §9.5b |

Parity test between the Python and GDScript twins: spec §12.6.

## 3. Godot mapping summary

Full detail: spec §11 (baked vs real time 11.1, shaders 11.2, lighting 11.3, budgets 11.4, formats 11.5).
- **Shaders:** `city_fog` (FogMaterial), `beam_shaft` (beams as soft cones), section cut (`city_building` corridor
  uniforms, `z_cut`), occlusion fade (per-instance `cut_height`, `opacity`; §7.4), interior mapping for Solace windows
  (§11.2, §8.6d), `wet_street`, `streak_lane`, water (Tethys look, §8.7).
- **Instancing:** MultiMesh with `INSTANCE_CUSTOM` for per-building and per-window data (cut, opacity, dissolve;
  interior `variant`, `lit`, `blind`, `tint`).
- **Baked vs real time:** far-city impostors and look-dev plates are baked; rain, puddles, section, occlusion and the
  overlay (pencil, stickers, rings) are real time.
- Godot is Y-up: every z in the spec is world Y.
- Open numbers for the build session: LOD distances (N1), performance budgets (N3), beam thresholds (N4), fog
  calibration (N5). Spec §14.1.

## 4. Mainline layout-rule changes (designer-approved)

Spec §3.2 (DR 1385-1388). These change the mainline city generator:
- Frontage buildings of at least 6 floors.
- Border streets 8 BU wide.
- The hero signage rule (spec §9.1).
- The street r2 height passes.
- Unique building ids required.

## 5. Game-design hand-off items (not art; owned by the build and design sessions)

Spec §14.3. The art tools read these and never decide them.
1. Per-seed city generation (lots, streets, territories, HQ lot per corp); order in spec §2.0. The generator should
   emit the planner JSON schema (spec §2.0b), and the art layout rules (§3.2) must be ported into it.
2. Non-HQ landmarks: the central-server access-key locations (how many, where, what they unlock, how a netrun reaches
   them). Art supplies the building types (§8.8).
3. Route mechanics: the run graph per run, and the HQ run mechanics (eye, yard cycle, retargets, read rule, sync strike).
4. The data contract: `city.json`, `net.json`, `run_graph.json`, key-location list, `art_seeds` (§2.2, §2.3).
5. Heal / rest markers: not in the GDD (GDD 4.2 has no such node). No art until it does (§14.1).

## 6. GDD naming notes

- **THE PANOPTICON** is Halcyon's HQ boss site / Central Server (GDD 11.7). GDD 8.4c still calls it "The Civic Core".
- **Central Server names conflict across GDD sections.** Meridian: "THE MASTER MANIFEST" (11.7) vs "The Manifest"
  (8.4b). Orbital: "Launch Control" (11.7) vs "the Commons Array" (8.4d) vs "the missile bay" (round 43). Solace:
  "THE GENOME CORE" (11.7) vs "the Renewal Engine" (8.3 / App. A). Tethys: "THE BLACK SMOKER"
  (`route_map_graph/hq_tethys/DESIGN.md`). Sources: `route_map_graph/hq_*/NOTES.md` (grep "Central Server", "flagged").
  The designer needs to pick one name per corp; art uses the 11.7 names.
- **Two new corps:** Aurelian Concord (`new_corps/roman/identity.md`) and Tethys Deep (`new_corps/atlantis/identity.md`;
  "Atlantis" is the arcology's product name). Adding a corp to the kit: spec §8.7.

## 7. Known gaps

Spec §14 (14.2 ROUTE_REQUIREMENTS gaps, 14.4 art gaps):
- Road cuttings and tunnels are not built (roads ride the terrain).
- A straight sea edge at the far right of the city hero frame.
- Planner JSON elements not mapped: undercity, drone corridors, ferry routes, checkpoints, civic glyphs.
- Heal / rest markers (no GDD node). Heat-per-node, raid-threshold and shared-graph-language items are proposals only
  (14.2 items 8, 9, 12).
- Meridian and Tethys landmark modules were not re-tuned beyond a look (`city_all_corps/NOTES.md`).
- Tethys has no final decision or hover frame (see the index).

## 8. File index (approved deliverables)

Checked on 2026-10-16. Everything below exists unless marked MISSING.

**Spec and decisions**
- `route_map_graph/PIPELINE_SPEC.md`
- `DIRECTION_REVIEW.md` (the decision log)
- `route_map_graph/decisions/` (`DECISIONS.md`, Q4, Q6, Q9 sheets)
- `route_map_graph/proc_vs_custom/` (`COMPARISON.md`, sheets p1-p4, `metrics/`)

**Storyboard**
- `route_map_graph/storyboard/storyboard.mp4` (also `storyboard_v3_dive.mp4`, `storyboard_sheet.jpg`)

**HQ finals** (OVERVIEW, DECISION, HOVER)
- Halcyon: `route_map_graph/hq_halcyon/H_overview_v2.png`, `H_decision_E_v2.png`, `H_hover_E_v2.png`
- Orbital: `route_map_graph/hq_orbital/H_overview_v2.png`, `H_decision_v2.png`, `H_hover_v2.png`
- Rebel Cell: `route_map_graph/hq_rebel_cell/H_overview_v3.png`, `H_decision_v3.png`, `H_hover_v3.png` (red states `H_red_*_v3.png`)
- Solace: `route_map_graph/hq_solace/H_overview_v4.png`, `H_decision_v4.png`, `H_hover_v4.png`
- Meridian: `route_map_graph/hq_meridian_v3/H_overview_v3.png`, `H_decision_v3.png`, `H_hover_v3.png`
- Tethys: `route_map_graph/hq_tethys/H_overview_v2.png`, `tethys_closeup_v2.png`. Decision and hover finals: **MISSING**.
- Landmark modules: `route_map_graph/hq_meridian_v3/scripts/meridian_landmark.py`,
  `route_map_graph/hq_tethys/scripts/tethys_landmark.py`

**City**
- `city_all_corps/city_all_corps_night.png`, `city_all_corps_labeled.png`, `city_all_corps_day.png`,
  `zoning_map.png`, `NOTES.md` (scripts in `city_all_corps/scripts/`)
- `city_planner/city_A2.json`, `design_A2_horseshoe_bay.md`, `plan_A2_horseshoe_bay.png`, `map_A2_horseshoe_bay.png`

**Street**
- `route_map_graph/street_r2/stills/` (`01_OVERVIEW_closed_s1.png`, `02_DECISION_closed_s1.png`,
  `03_OVERVIEW_route_overlay_s1.png`, `04_OVERVIEW_closed_seed2.png`), `metrics_r2.md`, `NOTES.md`

**Not yet existing**
- `tools/netrun_art/` in the repo: **MISSING** (to be built; item 1 in section 2).

## 9. Draft message to the build session

DRAFT — not sent

```
Subject: Netrun art hand-off package (art direction approved)

The designer has approved the netrun art direction. Everything you need
is in one place: docs/concepts/HANDOFF_PACKAGE/README.md (art-pass
branch). It lists what to build in priority order with spec section
links, the Godot mapping, the mainline layout-rule changes to port
(spec 3.2), the game-design items that are yours (spec 14.3), the GDD
naming conflicts, known gaps, and an index of every approved image.

The spec is docs/concepts/route_map_graph/PIPELINE_SPEC.md. Start with
sections 2, 3 and 11. Please propose your slice plan to the designer
and wait for their go-ahead before cutting slices or implementing.

Questions on the art rules: reply here and I will answer or amend the
spec (changes are marked "AD" with a date).
```
