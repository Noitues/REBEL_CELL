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

## File-ownership matrix (wave 1)
| Path | Owner |
|---|---|
| raid views (hq_scene raid parts, kit/raid_*, city_map_overlay raid layer) | 3A |
| netrun route / map parts of netrun_scene.gd, route kit, jack-in transition | 3B |
| shop / loot / event parts of netrun_scene.gd; hq_scene look | Group 4 (4A; 4C) |
| combat_scene.gd, wheel_view.gd, combat FX | Group 2 |
| palette / theme, materials, glyphs, city spike | Group 1 |
| ui_motion.tres, REQUIRED_IDS, lab DEMOS, test_manifest.json, strings.csv, Settings additions, DECISIONS | union |
