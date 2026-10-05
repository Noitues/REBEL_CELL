# Group 3 — City: ART-5 unified city, ART-6 raid, ART-7 netrun, ART-8 HQ runs (M14)

**Wave 1 (started 2026-10-05, before the city render spike reports):** the parts of ART-6 and ART-7 that do
not depend on how the city is rendered — panels, documents, stickers, pencil, icons, transitions — on the
**current** raid map and netrun route. **Wave 2 (after 1D's `docs/handoff/art_1/city_spike_report.md`):**
ART-5 the unified city model and motion, the raid / netrun / HQ-run map views on it, ART-8 compounds.
Designer: "start any group you can in parallel"; DECISIONS "groups in parallel, fast checks only".

Every agent reads `process/agent_common_rules.txt` first. Source: `docs/ART_BIBLE.md` §1.2, §4.1–4.9,
§5–6; refs `docs/art_reference/{raid,netrun,hq,city}/`; plan §4.2 ART-5…8. Generator scripts:
`art-concepts-r43:docs/concepts/<round>/scripts/`. Visual impact first; capture windowed next to the
reference, iterate. Fast checks + own scripts only. Foundations (1A palette/theme, 1B materials incl.
grease pencil + holo + corp paper + stickers, 1C glyphs) land in parallel: seams, then `git merge main` when
messaged.

**Must survive:** the raid verdict sweep matches `raid_verdict`; reading holds never shortened at 2x / 4x;
the route sweeps for every corp (labels, you-are-here, fits); MotionSkip one press (the jack-in transition
skips with one press, STYLE 5.1); reduce effects = end state; headless never waits; motion entries + demos;
tokens only; layouts at 1.0/1.6/2.0; pad reachability; views never change state. **No unapproved
mechanics** (G9 EXPOSED, decoy destroyed, raid intel decrypt state, G11 netrun rules, G12 HQ mechanics):
their art stays in `docs/art_reference/`.

**Presentation rulings built on plan defaults, pending designer confirmation:** D13 an "Always show all
nodes" setting (additive Settings key) with hidden-node visibility on the netrun map (nodes not next are
hidden; legend hover and node hover reveal); D14 netrun presentation — unavailable nodes/links white, past
nodes grey, TARGET circle, tier shown, Heat shown, irrelevant city greyed, node panel only when decrypted —
**only where it matches the current rules (GDD 4.2)**; list anything that would need a rule change.

## Wave 1 areas

### 3A — Raid presentation (ART-6 2D parts; bible §4.8; ruling 6.2 words, ruling 11 DOWN)
Owns the raid setup / playout / report views (`hq_scene.gd` raid parts, `kit/raid_*`, `city_map_overlay.gd`
raid layer), raid strings. Refs: `raid/round21_raid_ui/*` (node health, path rules, raid report),
`round22_raid_ui/node_status_key.jpg`, `round22_raid_world/vehicle_icons_v4.jpg`, `unit_health.gif`,
`class_colours_v2.jpg`, `operator_rigger`, `round23_raid_ui/interactions_gifs/*` (drag dock preview, swap,
node taken v2, home breached), `round23_raid_world/bonus_*`, `round20_raid_world/building_nodes_v2.jpg`.
1. Panels by fiction (E): YOUR NETWORK = CRT terminal with status chips; RAID INCOMING = intercepted work
   order (corp paper); THREAT INTEL = decrypted holo with the cracked seal + DECRYPTED; panels re-skin per
   raiding corp; Speed / Skip as the terminal strip below START DEFENSE (START peels away in playout).
2. Node status key; node health v2 (fill drains north → south, outline and icon stay lit; repair rises);
   DOWN = the Site markers' white bolt over a greyed marker (ruling 11), no amber dashed socket.
3. Grease-pencil rules on the current map: red routes (solid active / dashed what-if), A/B/C entry circles;
   state marks INCOMING / DOWN / TAKEN written ~0.4 s, held ~1.5 s, wiped ~0.4 s; TAKEN v2; BREACHED one
   slow heavy pass; CELL HOLDS sticker slapped on the report.
4. Card drag model: the defence sticker peels and parks above its hand slot, a yellow pencil arrow to the
   cursor, snap circle yellow (IF PLACED terminal) / red + X (NO SLOT); remove = click the node; swap = one
   motion. Keep ANIM drag behaviour and its tests.
5. Threat vehicle icons v4 (shape = type, fill = corp colour = health draining, dashed status ring with pips,
   heading arrow on hover); R3 class beacons for stationed operatives; slow field under units; freeze
   crystals; repair rise.
6. Raid report as the raiding corp's after-action report (paper, CLASSIFIED) with the Cell's pencil and
   CELL HOLDS on top.
- Accept: raid verdict sweep; reading holds at 2x / 4x; every changing state captured vs its reference.

### 3B — Netrun presentation (ART-7 2D parts; bible §4.6; D13, D14)
Owns the netrun route / map parts of `netrun_scene.gd`, route kit views, the jack-in transition.
Refs: `netrun/round36_netrun/*` (city states, node backdrop), `round37_netrun/*` (default, heat calm, legend
hover, transition mix), `round38_netrun_transit/*` (transit v3).
1. Node states A (outline rings white / orange / lime), TARGET, tiers, calm Heat on the route; hidden nodes +
   the always-show setting (D13), within current rules (D14).
2. The operative dossier on corp paper; decrypted node panels.
3. The jack-in transition: terminal connect → window despawns → wheel spins up → lens zoom (~4.4 s), one
   press skips, reduce effects = end state.
4. Dressed-room node backdrops (baked stills from the generator scripts per node type / corp).
5. Transit v3 path look (straight cable runs, solid walked path) on the current route view; the real-city
   version comes in wave 2.
- Accept: route sweeps for every corp; the transition skips with one press; captures vs references.

## Wave 2 (critical path; re-planned 2026-10-05 to pull the M14 finish in)

Order: 1D posts an interim render pick (`docs/handoff/art_1/city_spike_interim.md`) → 5a/5c/5d start on it;
5b and 8p start **now** because the models are needed whichever technique wins (Blender is the source for
both real-time glTF and baked layers). 1D's optimisation round and final report run alongside; its final
numbers can still change the pick, so keep the asset pipeline technique-neutral where cheap.

### 5b — Landmarks for the five corps (ART-5; bible §4.4; refs `city/round26_hq_targets/*`,
`round27_hq_targets/*`, `round31_meridian_combat/*`, `round34_rebel_cell/*`, `foundations/round2/*`)
Meridian container castle (texture A, moat, gantry keep, train), Solace lit helix + hospital, Halcyon
Court + eye scan + the Justice statue, Orbital in-ground silo + TV station, REBEL_CELL red-window fist with
the blackout reveal. Blender 5.2 headless from the concept generator scripts; versioned export scripts in
`tools/art_pipeline/city/` (not under docs); exports in `assets/city/landmarks/<corp>/` as glTF 2.0 **and**
a day/night layered-sprite set at 2×, each with a manifest (source script, commit, settings) and a
validator hook. Game-sized, compressed. Renders compared with the references.

### 8p — HQ compound prep (ART-8; bible §4.7; refs `hq/round43_hq_mechanics/hq_*_compound.jpg`,
`hq/round35_netrun/hq_compound.jpg`)
The overhead compound per corp as static layouts on the **current** HQ-run rules (moving parts — crane /
train, strands, switchback eye, silo loop, Sync Strike — wait for G12): the same pipeline and export
pair as 5b under `assets/city/hq_compounds/<corp>/`, plus a layout table in content that maps each current
HQ-run node to a compound position (schema minimal, smoke-checked). No view changes yet.

### 5a / 5c / 5d — after the interim pick
5a city kit + layout from the game's layout table + the orthographic camera and zoom; 5c city motion
(sky lanes, cars with 3 LOD tiers, helicopters and drones, searchlights, billboards, day / night /
suspicion, Heat lights) with reduce-motion pauses; 5d Grid site markers v4 + plain-language legend +
Exploit badges on T2 Sites + fight-won lights + the Grid map key. Then the optimisation round, then the
raid / netrun / HQ-run views move onto the city.

## File-ownership matrix (wave 1)
| Path | Owner |
|---|---|
| raid views (hq_scene raid parts, kit/raid_*, city_map_overlay raid layer) | 3A |
| netrun route / map parts of netrun_scene.gd, route kit, jack-in transition | 3B |
| shop / loot / event parts of netrun_scene.gd; hq_scene look | Group 4 (4A; 4C) |
| combat_scene.gd, wheel_view.gd, combat FX | Group 2 |
| palette / theme, materials, glyphs, city spike | Group 1 |
| ui_motion.tres, REQUIRED_IDS, lab DEMOS, test_manifest.json, strings.csv, Settings additions, DECISIONS | union |

## Wave 2b (after 5a, re-planned 2026-10-05 15:35 with the full coverage check)
- **5e City integration** (critical path): place 5b's landmark glTFs and 8p's compound glTFs in CityModel
  (`landmark_slot` / `hide_stand_in`, manifests' origin + footprint); attach 5c's `CityViewMotion` and 5d's
  `SiteMarkerLayer` + `GridMarkerProjection.from_view` on the live Grid (CityMapOverlay keeps routes only); the
  Cell's red-window crest from 5b's crest mask in the window shader with the blackout reveal; off-screen TARGET
  chevrons + pencil marker; spread the Site layout ×2 so the Grid frames at ortho 440 (round 39) — presentation
  only, rules unchanged (verify `raid_verdict` / route sweeps); fix the unresolved "no buildings" captures.
- **7w Netrun on the city**: transit v3 cables routed on the 3D streets (cable router: 45° jogs, bridge hops,
  crossing avoidance), the route page on CityView3D at the NETRUN band, the CLOSE car tier at netrun close-ups
  (art pass: `cars_lod`), node rooms unchanged.
- **8w HQ runs on the city**: HQ-run pages on the compounds at the HQ zoom (static, current rules); DISPATCH's run in
  the round 43 Tokyo canyon; the Central Server breach look (bible §4.9); D17 combat backdrops swapped from 2B's
  baked stills to city close-ups through `BackdropCatalog` (keep the stills as the Deck-tier fallback if cheaper).
- **6w Raid on the city** (starts when 3A hands back): the raid map on CityView3D at the RAID band, building nodes as
  uplink pads, 3A's marks / icons / pencil projected through the city camera, raid zoom fit.
