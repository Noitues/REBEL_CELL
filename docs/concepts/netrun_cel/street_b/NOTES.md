# Campaign B street: branches + six node kinds (B-096, B-098)

Concept plates only, PIL compositing, built from approved plates. Not committed.

## Files
- **`street_branch_A_band.png`** (pick B variant A, band): the staged street (golden `street_overview.png` framing) with a real fork, two lanes and a rejoin.
  - Pick B runs from the fork through the hovered lane to the rejoin.
  - The beam rises from the rejoin.
  - The other lane is dimmed but still a choice.
- **`street_branch_B_next.png`** (pick B variant B, next only): the same street.
  - Pick B is a pad on the hovered next room only, with the beam rising from that room behind the rooms stacked above it.
  - The rest of the hovered lane is plain "ahead" (white dashes, full rooms).
  - The old single `street_branch.png` is removed.
- **`node_kinds.png`**:
  - a key strip of the six kinds with what each does;
  - the locked round 31/32 stickers beside the proposal silhouettes;
  - silhouette, greyscale and 16 px checks;
  - the six kinds in context, 1:1 at the approved zoom.
- **`street_b_sheet.jpg`**: both branch variants and node kinds, with the three references they are built from.
- **`src/`**: the scripts. Run order is `street_samples.py`, `street_branch.py` (writes both variants), `node_kinds.py`, `sheet.py`. Scratch files are in `D:/rc_scratch/street_b/`.

## Rulings and answers recorded
- **Designer ruling, 2026-11-15: "Keep the web".** The street is drawn as the four-floor web the generator makes (2-4 rooms a layer on four stories, paths crossing and merging, all rejoining at the last node), not as two lanes. The plates already draw it that way. "Two lanes" survives only as the name for a fork that splits into exactly two rooms and rejoins.
- **B-098 (build, answering A-125):**
  1. Draw the web as generated. Done.
  2. The sixth kind is **SERVER RACK** (not CACHE).
  3. The on-screen word for type `elite` is **ELITE ROUTER**. It replaces ELITE on every plate (key strip, stickers, labels, in-context strip, branch plates). The content's `node_labels` still says "ELITE"; build owns that change.
  4. Depth is **8** for a site street and **10** for the HQ street.
  5. Show both pick B variants; the designer picks at review. Done (A band, B next only).
  6. The zoom-window re-check for 8 and 10 layers waits for build's Godot ping. Not done here, on purpose.

## Sources of each rule (all read only, from `port-campaign-b`)
- **Node kinds**: `content/b/street_rules/b_street_rules.tres` (`node_labels`); types are in `scripts/state/street_node_state.gd`. Screen words follow B-098.
- **Generation**: `scripts/core/street_generator.gd`. Levers come from `tools/proto_web/export/data/street_gen.json`: `streetDepth` 8, `streetMin` 2, `streetMax` 4, `rackMid` 4, `eliteFrom`/`eliteTo` 3/6 at 85 %, `mfFrom`/`mfTo` 3/5, `mfExtraPct` 10, `terminalPct` 25, `linkExtraPct` 45, `hqDepth` 10, `reclaimDepth` 3.
- **What each kind does**: `scripts/core/street_session.gd` (`enter_node`, `finish_fight`, `_event_move`, `next_floor`, `shop_move`). `is_elite()` covers elite and rack. Levers: `termHeal` 5, `rackHeal` 6, `heatElite` 1.
- **Player picks**: in `street_session.move("go:NODE")`, the move is legal only for a node in `street.next_nodes()`, which are the current node's links.
- **Rows are stories**: `story_labels` are ground floor, 2nd floor, 3rd floor and top floor. The lever text reads "at most 4: four stories".
- **Real streets**: the 10 samples in `content/b/street_sample/`. `src/street_samples.py` parses them and finds every fork-to-rejoin window.
- **Look**:
  - bible 4.6: hybrid D (rooms in the frontage, vinyl-sticker nodes, wax links, the ring states orange/lime/white/grey, the whole graph shown);
  - ZOOM_RULES 5.1 / 6: framing, 40 px nodes;
  - round 7b candB: edge (1.0, 0.18, 0.62), 4 px line, fill 0.22, beam_k 3.0;
  - sticker art: `route_map_graph/hq_halcyon/scripts/r32ui.py` (imported, not modified).

## Node kinds (screen words per B-098)
| type id | on-screen word | what it does (port) |
|---|---|---|
| fight | ROUTER | Takeover fight. A win offers 3 class cards, plus credits for segments held over the cap. |
| elite | ELITE ROUTER | Elite fight. A win adds Heat +1 and gives the rich card offer plus 2 implants. |
| event | TERMINAL | No fight. Pick one: heal 5 run health, take an implant, or upgrade 2 random cards. |
| shop | MAINFRAME | Buy cards or an implant, upgrade, remove, transform, patch. The first tier-1 visit gets one free action. |
| rack | SERVER RACK | Fight configured as elite, rich reward, then BANKS the run's loot. The mid rack (layer 4) also heals 6 and adds Heat +1. The last-layer rack ends the street cleared. |
| boss | BLOCK SERVER | Only on the HQ street (10 layers), as its last node. HQ boss fight; the result ends the campaign (won or lost). |

## How branching works (per the rules)
- A **site street is 8 layers** and the **HQ street is 10**. Layer sizes:
  - layer 1 and the next-to-last layer: 2-3 nodes;
  - the layers between: 2-4 nodes;
  - layer 4 (the mid rack): at least 3;
  - the last layer: 1 node (SERVER RACK, or BLOCK SERVER on the HQ street).
  Site samples have 20-24 nodes. A walk visits one node a layer.
- Each node sits on a **row 0-3, which is a story**. Each node links forward to 1-3 nodes of the next layer: its nearest row index, plus each neighbour at 45 %. Every next-layer node gets at least one parent.
- The **player picks** any linked next node (`go:NODE`). Nodes are never revisited.
- **There are no persistent lanes.** Paths cross and merge every layer, and all of them rejoin at the last node.
  - Pure fork-to-rejoin windows appear in every sample (usually 1 layer long).
  - Seed 2 tier 2 and seed 3 tier 1 have a 2-layer pair. The plates use seed 2 tier 2 from fork 52: 52 → {61 → 71, 62 → 72} → 81.
- Counter wheels (35 %, tier 2+) are only ever placed where a route around them exists.

## Calls I made
1. **A lane is a run of rooms on floors**, not a road lane. The data says rows are stories, and the locked route view already reads "PICK A FLOOR".
2. **Pick B lives on the facade**, where it sits on the road lots in the city band; the rooms stay clear so their kind light reads.
   - Variant A is a band from the fork to the rejoin, with the beam from the rejoin. A beam from a mid node would cross the rooms stacked above it.
   - Variant B is a rounded pad around the next room, with the beam from that room drawn behind the rooms above it. The rest of the lane uses the plain "ahead" grammar (white dashes).
3. **Dimming of the other lane** is softer than the bible's hover power cut (×0.20): rooms ×0.6, wax at 55 %, sticker at 78 %, orange ring kept. It must stay readable as an option. Outside the highlight the frame drops only ×0.86.
4. **Staging.** The golden plate's camera has closed walls and no rooms. I cut the rooms into its frontage, using room interiors from the locked AAA2r3 render (one interior per kind). The 4-story columns, the room size (86×50, 66 px pitch) and the column placement are mine, not derived from a camera or a city layout. The BLOCK SERVER room is the rack room re-lit red; no render of it exists.
5. **Stickers.** I kept the locked round 31/32 art inside every sticker and proposed a die-cut silhouette per kind:
   - ROUTER: circle (unchanged);
   - ELITE ROUTER: 8-point burst (pointed = attack);
   - TERMINAL: monitor;
   - MAINFRAME: price tag (the shop's kraft tags);
   - SERVER RACK: tall rack;
   - BLOCK SERVER: a crenellated keep with a padlock. This is a new sticker (proposal), built from the locked glyph `state_locked`.

   Kind colours follow `sidekit.TYPE_COL`, so ELITE ROUTER red-orange and SERVER RACK amber are split; both used MER orange in r32ui. No raid_v3 icon fitted.
6. **The in-game key strip** uses the B-098 words. The ring states are the locked ones.
7. Sticker size is 40 px (ZOOM_RULES 6.3). All 12 nodes of layers 5-8 are drawn, with the unreachable ones grey (whole-graph rule, and now the designer's "keep the web").

## Weak points
- **16 px silhouettes.**
  - Filled stickers stay blobs at 16 px. Soft IoU in the proposal is at worst 0.86 (ROUTER/TERMINAL), and 3 of 15 pairs are under 0.68. The locked set is 1.00 (4 of 5 are circles).
  - The shapes read from about 24 px and clearly at the 40 px street size.
  - The bible's 0.68 glyph rule is not met at 16 px by any sticker set (`D:/rc_scratch/street_b/silhouette_iou.json`).
- **Elite colour.** ELITE ROUTER red-orange sits close to the "next" orange ring; the burst shape carries the difference.
- **Variant B pad.** The rooms above and below the hovered room sit 16 px away, so the pad's bottom edge is partly hidden by the room below. The pink reads on the sides, the top and through the beam. Variant B is quieter overall and easier to miss than A.
- **Staged camera.**
  - The street_overview camera cannot show 4 floors of rooms over 4 layers in real buildings; the columns are staged.
  - The layer spacing is uneven (360 / 250 / 290 px).
  - The current node sits at x 0.27, not the 0.33 third.
- **Frame load.** There are 12 nodes in frame against ZOOM_RULES 6.3's "at most 6". The web ruling wins, but the frame is busy at layers 5-6.
- **Room scale.** Rooms are small (50 px tall) against the plate's 60 px ground floors, and the AAA2r3 interiors are a different render; the match is close but not exact.
- **Process slips**, both harmless:
  - one build step piped two python scripts together, so they ran at the same time;
  - one stray `python -` (stdin from /dev/null) hung and was stopped. It ran no code.

  Everything was rebuilt one process at a time afterwards.

## Open questions (still open)
1. **Silhouettes and sticker.** Approve the silhouette-per-kind proposal (it changes the locked circles' outline only) and the BLOCK SERVER keep sticker.
2. **Pick B variant:** A band or B next only. The designer picks at review (B-098).
3. **Elite word in content.** `node_labels` still says ELITE; build to change it to ELITE ROUTER in the content when it lands.
4. **Zoom window** for 8 / 10 layers (ZOOM_RULES assumes 7 and a 3.5-layer window). Waits for build's Godot ping (B-098 item 6).

## Designer pick, 2026-11-15
**Pick B variant B, next room only** (`street_branch_B_next.png`). Variant A (band to the rejoin) was not taken. Known
weak point to carry into the build: the pad sits 16 px from the rooms above and below, so the beam and the pad sides carry
the read.
