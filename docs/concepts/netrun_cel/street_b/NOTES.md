# Campaign B street: branches + six node kinds (B-096)

Concept plates only, PIL compositing, built from approved plates. Not committed.
- `street_branch.png`: the staged street (golden `street_overview.png` framing) with a real fork, two lanes and a rejoin. Lane 2 is hovered in round 7b pick B. Lane 1 is dimmed but still a choice.
- `node_kinds.png`: a key strip of the six kinds with what each does; the locked round 31/32 stickers next to the proposal silhouettes; silhouette, greyscale and 16 px checks; the six kinds in context, 1:1 at the approved zoom.
- `street_b_sheet.jpg`: both plates with the three references they are built from.
- `src/`: the scripts. Run order is `street_samples.py`, `street_branch.py`, `node_kinds.py`, `sheet.py`. Scratch files are in `D:/rc_scratch/street_b/`.

## Sources of each rule (all read only, from `port-campaign-b`)
- **Node kinds and words**: `content/b/street_rules/b_street_rules.tres` `node_labels`. Types are in `scripts/state/street_node_state.gd` (`T_FIGHT .. T_BOSS`).
- **Generation**: `scripts/core/street_generator.gd`. Levers come from `tools/proto_web/export/data/street_gen.json`: `streetDepth` 8, `streetMin` 2, `streetMax` 4, `rackMid` 4, `eliteFrom`/`eliteTo` 3/6 at 85 %, `mfFrom`/`mfTo` 3/5, `mfExtraPct` 10, `terminalPct` 25, `linkExtraPct` 45, `hqDepth` 10, `reclaimDepth` 3.
- **What each kind does**: `scripts/core/street_session.gd` (`enter_node`, `finish_fight`, `_event_move`, `next_floor`, `shop_move`). `is_elite()` covers elite and rack. Levers: `termHeal` 5, `rackHeal` 6, `heatElite` 1.
- **Player picks**: in `street_session.move("go:NODE")`, the move is legal only for a node in `street.next_nodes()`, which are the current node's links.
- **Rows are stories**: `story_labels` are ground floor, 2nd floor, 3rd floor and top floor. The lever text reads "at most 4: four stories".
- **Real streets**: the 10 samples in `content/b/street_sample/`. `src/street_samples.py` parses them and finds every fork-to-rejoin window.
- **Look**: bible 4.6 (hybrid D: rooms in the frontage, vinyl-sticker nodes, wax links, the ring states orange/lime/white/grey, the whole graph shown) and ZOOM_RULES 5.1 / 6 (framing, 40 px nodes). Round 7b candB gives the pick B values: edge (1.0, 0.18, 0.62), 4 px line, fill 0.22, beam_k 3.0. Sticker art comes from `route_map_graph/hq_halcyon/scripts/r32ui.py` (imported, not modified).

## Node kinds (exact port words)
| type | word | what it does (port) |
|---|---|---|
| fight | ROUTER | Takeover fight. A win offers 3 class cards, plus credits for segments held over the cap. |
| elite | ELITE | Elite fight. A win adds Heat +1 and gives the rich card offer plus 2 implants. |
| event | TERMINAL | No fight. Pick one: heal 5 run health, take an implant, or upgrade 2 random cards. |
| shop | MAINFRAME | Buy cards or an implant, upgrade, remove, transform, patch. The first tier-1 visit gets one free action. |
| rack | SERVER RACK | Fight configured as elite, rich reward, then BANKS the run's loot. The mid rack (layer 4) also heals 6 and adds Heat +1. The last-layer rack ends the street cleared. |
| boss | BLOCK SERVER | Only on the HQ street, as its last node. HQ boss fight; the result ends the campaign (won or lost). |

## How branching works (per the rules)
- A street is **8 layers** (`streetDepth`). Layer sizes:
  - layer 1 and layer 7: 2-3 nodes;
  - layers 2-6: 2-4 nodes;
  - layer 4 (the mid rack): at least 3;
  - layer 8: 1 node (SERVER RACK, or BLOCK SERVER on the HQ street).
  The samples have 20-24 nodes. A walk visits 8 of them.
- Each node sits on a **row 0-3, which is a story**. Each node links forward to 1-3 nodes of the next layer: its nearest row index, plus each neighbour at 45 %. Every next-layer node gets at least one parent.
- The **player picks** any linked next node (`go:NODE`). Nodes are never revisited.
- **There are no persistent lanes.** Paths cross and merge every layer, and every path rejoins at the single final node. The designer's "two lanes in places" is what a run looks like where a node has exactly 2 links and the two runs stay apart until a shared node.
  - Pure fork-to-rejoin windows appear in every sample (e.g. layer 6 → 7 → 8), usually 1 layer long.
  - Seed 2 tier 2 and seed 3 tier 1 have a 2-layer pair. The plate uses seed 2 tier 2 from fork 52: 52 → {61 → 71, 62 → 72} → 81.
- Counter wheels (35 %, tier 2+) are only ever placed where a route around them exists.

## Calls I made
1. **A lane is a run of rooms on floors**, not a road lane. The data says rows are stories, and the locked route view already reads "PICK A FLOOR". So the fork is drawn as rooms splitting across floors in the frontage: the hovered lane climbs, the other stays on the ground floor.
2. **Pick B moved from road lots to the facade band.** The pink 22 % fill and 4 px edge run as a band from the fork through the hovered lane to the rejoin, which is the street-level twin of the city band's segment. The fill skips the rooms so their kind light stays readable.
3. **The beam rises from the rejoin**, the final rack on the top floor. Every other node has rooms stacked above it, so a beam there would cross them.
4. **Dimming of the other lane** is softer than the bible's hover power cut (×0.20): rooms ×0.6, wax at 55 %, sticker at 78 %, orange ring kept. It must stay readable as an option. Outside the band the frame drops only ×0.86.
5. **Staging.** The golden plate's camera has closed walls and no rooms. I cut the rooms into its frontage, using room interiors from the locked AAA2r3 render (one interior per kind). The 4-story columns, the room size (86×50, 66 px pitch) and the column placement are mine, not derived from a camera or a city layout. The BLOCK SERVER room is the rack room re-lit red; no render of it exists.
6. **Stickers.** I kept the locked round 31/32 art inside every sticker and proposed a die-cut silhouette per kind:
   - ROUTER: circle (unchanged);
   - ELITE: 8-point burst (pointed = attack);
   - TERMINAL: monitor;
   - MAINFRAME: price tag (the shop's kraft tags);
   - SERVER RACK: tall rack;
   - BLOCK SERVER: a crenellated keep with a padlock. This is a new sticker (proposal), built from the locked glyph `state_locked`.

   Kind colours follow `sidekit.TYPE_COL`, so ELITE red-orange and SERVER RACK amber are split; both used MER orange in r32ui. No raid_v3 icon fitted.
7. **The in-game key strip** uses the port words. The ring states are the locked ones.
8. Sticker size is 40 px (ZOOM_RULES 6.3). All 12 nodes of layers 5-8 are drawn, with the unreachable ones grey (bible 4.6 whole-graph rule).

## Weak points
- **16 px silhouettes.**
  - Filled stickers stay blobs at 16 px. Soft IoU in the proposal is at worst 0.86 (ROUTER/TERMINAL), and 3 of 15 pairs are under 0.68. The locked set is 1.00 (4 of 5 are circles).
  - The shapes read from about 24 px and clearly at the 40 px street size.
  - The bible's 0.68 glyph rule is not met at 16 px by any sticker set (`D:/rc_scratch/street_b/silhouette_iou.json`).
- **Elite colour.** ELITE red-orange sits close to the "next" orange ring; the burst shape carries the difference.
- **Staged camera.**
  - The street_overview camera cannot show 4 floors of rooms over 4 layers in real buildings; the columns are staged.
  - The layer spacing is uneven (360 / 250 / 290 px).
  - The current node sits at x 0.27, not the 0.33 third.
- **Frame load.** There are 12 nodes in frame against ZOOM_RULES 6.3's "at most 6". The bible's whole-graph rule wins, but the frame is busy at layers 5-6.
- **Room scale.** Rooms are small (50 px tall) against the plate's 60 px ground floors, and the AAA2r3 interiors are a different render; the match is close but not exact.
- **Process.** One build step mistakenly piped two python scripts together, so they ran at the same time. Both only read and wrote scratch/plate files; everything was rebuilt one process at a time afterwards.

## Open questions for the designer / build
1. Should the street show the whole 4-row web, as the rules generate it, or did "two lanes in places" mean the generator should change to at most 2 nodes per layer in places? The plates follow the current rules.
2. PORT_SPEC (UI table) lists node cards "fight, elite, shop, event, **cache**, boss". The generator has **rack** (SERVER RACK); NAME_MAP has both CACHE and Server Rack. Which is the sixth kind's word?
3. `node_labels` say **ELITE**; NAME_MAP and GDD say **Elite Router**. Which goes on screen?
4. HQ street depth: the lever says `hqDepth` 10, but `b_street_sample_seed1_tier4_hq` is 8 deep. Which is current? (BLOCK SERVER ends it either way.)
5. Approve the silhouette-per-kind proposal (it changes the locked circles' outline only) and the BLOCK SERVER keep sticker.
6. Pick B on the street: the band from the fork to the end (as drawn), or only the hovered next room plus its link?
7. The ZOOM_RULES camera spec says 7 layers; Campaign B has 8 (10 on the HQ street). The dolly window (3.5 layers) needs a re-check.
