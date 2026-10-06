# Round 44 A: map screens the concepts never designed

These are concept renders of the art director's calls in `INTEGRATION_REVIEW/REVIEW.md` (section f, D5, D7, D14,
D17, the designer rulings, and Q1, Q4, Q9, Q10, Q15). Each one redraws a build screen. Nothing is committed, and
`scratch/` is cleared.

## Files

| File | What it shows |
|---|---|
| `hq_idle.png` | **The HQ page, direction B, built to its design and cleaned (D7).** See "HQ idle" below. |
| `hq_node_selected.png` | **The same page with the CORE home node selected.** See "CORE selected" below. |
| `route_page.png` | **The netrun route page (D14, f, Q4, Q15).** See "Route page" below. |
| `route_page_hover_all.png` | **The same page while hovering the key strip ("SHOWING ALL LINKS").** Every link of the run appears as a thin hairline in 25 % white. Hidden nodes stay hidden, with no grey discs (Q15). |
| `raid_setup.png` | **Raid setup at text scale 1.6.** See "Raid setup" below. |
| `topbar_by_page.png` | **The resource bar on each page, at 1:1 in its real 1080p position, all in one terminal style.** See "Resource bar by page" below. |
| `contact_A.jpg` | Each render (right) beside the build capture it replaces (left), with labels. Sources: `g_final.jpg` idle and claim, `ROUTE_c.jpg` after Meridian 1.0, `MAPVIEW.jpg` route start, and `HEAT_ALL.jpg` raid_setup ×1.6 and its page column. |
| `scripts/` | Everything needed to rebuild. See "Rebuild" below. |

### HQ idle (`hq_idle.png`)
- **The city:**
  - The unified city is at the City Grid look, with solid buildings.
  - Outside the network's fit rectangle it is darkened to ×0.68 and slightly desaturated, but keeps its hue.
  - Inside the rectangle it is at ×0.86.
  - It is fully lit only inside a soft vignette round the selected Site, Priority Lane Exchange (T2).
- **Markers:** only the Sites that bible 4.5 pins, drawn with the v4 markers:
  - yours (the fists), CORE (the heart) and cleared Sites;
  - 2 Exploit Sites and 4 Heat-objective Sites;
  - the selection.
- **One name tag**, for the selected Site.
- **TARGET:** Meridian HQ is off-screen at this framing, so it gets the City Grid's red pencil edge marker. Its `CENTRAL SERVER // EXPLOITS 1/3` chip sits clear of the pencil.
- **The one plan:** a yellow pencil arrow along the border link from Returns Processing to the circled Site. The RUNNER tag on CELL-9's polaroid says who goes.
- **The page furniture:**
  - The crew polaroids use the locked portrait v2 busts. The flatlined operative is greyscale with a FLATLINED stamp.
  - The CREW / MARKET / DEFENCE tabs are terminal. DEFENCE says RAID PENDING.
  - The intercepted work order is the one paper document.
  - The Site file is a holo, with IF CLEARED chips inside it.
  - JACK IN is the idle verb, shown mid rainbow-sweep, with its system word `> jack --to …` washed out under it.
  - The full resource bar is shown, and the Heat gauge has no stamp.
  - There is no news band. A corp-news holo toast sits at the foot.

### CORE selected (`hq_node_selected.png`)
- The vignette moves to CORE. CORE gets lime focus brackets, the cursor and its own name tag.
- The CORE card is a **terminal**, because it is the Cell's node:
  - integrity 44/50 as a bare Anton number with a pip bar;
  - its defences, links and stationed operative;
  - **PATCH** and **HEAT SCRUB** as terminal actions under `> HQ ACTIONS`.
- The one pink verb is **UPGRADE**, with its cost as the washed-out system word. JACK IN, the plan and the toast are gone.

### Route page (`route_page.png`)
- **Plate:** the round 38 v3 transit camera (ortho 130) on the unified city. It is finished at the locked translucency v3 (`SOLID40`: opacity 0.68, ×0.86, chroma ×1.35), so the city stays violet and is not grey slate.
- **What is drawn:**
  - Only the links the route uses: the walked path as a solid lime line, and the edges to the two options as orange dashes.
  - Only the walked nodes, the current node, the options and the TARGET. Hidden nodes are fully hidden.
  - Node stickers are 48 to 76 px.
- **No text tags and no "YOU ARE HERE".** The lime token (the operative's sword) marks the position. The options keep only the locked small number chips "1" and "2" (key hints, no words).
- **Panels:**
  - the corp-paper dossier on the left;
  - the FIGHT // L3 holo for the hovered option (the cursor is on it);
  - the ROUTE terminal reduced to GRID VIEW and Save & quit;
  - a top strip with Heat, HP and Cycles only;
  - the NETRUN title sticker in yellow;
  - the key strip.

### Raid setup (`raid_setup.png`)
- Same camera and finish as the locked `raid_view_v3`.
- The yellow RAID SETUP title sticker is back (Q10).
- **The map:**
  - No node text tags. Status is on the node: holds is the lime/green frame and the fill drain, disabled is the grey frame and a de-powered link.
  - The forecast is the dashed outer ring in the outcome colour: green for holds, pink for home, amber for disabled.
  - Only this raid's entry Sites are drawn (Q4).
  - The red pencil routes, the A/B/C circles and the Meridian convoy icons are as locked.
- **Right column** (Q9; nothing in it covers the network or the pencil), top to bottom:
  - THREAT INTEL as a holo: corp tint, 4 px scanlines, three bands, RGB edge split, 0.88 scrim, scanned HAULER / COURIER silhouettes, the cracked Meridian seal with DECRYPTED;
  - YOUR NETWORK as a terminal: the 4 nodes on the routes plus "5 MORE (scroll)";
  - START DEFENSE, the one verb;
  - the Speed/Skip strip.
- **Left column:** the title and the work order, the one paper document.
- **Bottom:** the MAP KEY collapsed to a key strip, and the 6 defence cards.

### Resource bar by page (`topbar_by_page.png`)
| Page | What the bar shows |
|---|---|
| HQ | The full bar. |
| Netrun pages | Heat, HP and Cycles. |
| Shop | Cycles, placed after the MAINFRAME sign. |
| Combat | No bar, only a 120 × 32 terminal Heat chip at top left. |
| Loot | DECK, the only thing the pick changes. |
| Event | HP, Cycles and Crew, the things that event's choices change. |

The rows for the shop, combat, loot and event pages are drawn over the locked concept screens.

## Decisions (mine; flag if wrong)
1. **HQ framing.**
   - At the real Meridian scope, CORE and the HQ are 70 lots apart. Framing both would shrink the network, so the HQ page frames the network and the selected Site.
   - The off-screen TARGET uses the City Grid's red pencil edge marker (bible 4.1).
   - Direction B's large HQ in frame only works with a compact campaign.
2. **Selectable Sites at HQ.**
   - Following D7, I show only the 4.5 pins plus the selection.
   - The other selectable Sites (orange) are hidden until hover. Their border links are hidden too, except when the other end is pinned.
   - The pinned objective Sites still give 6 orange or white markers. That is more than direction B's ~8 marks in total, but true to 4.5.
3. **Plan pencil.** The arrow runs along the real border link the run will use. It does not go from the polaroid across the map: that path crossed four markers and is less true. CELL-9 is marked as the runner with a cyan tag.
4. **The dossier's HEAT stamp is dropped on the route page.** The strip now carries Heat, and two Heat readouts were clutter. Bible 4.3 says "the number lives on the dossier stamp", so **this needs the designer**.
5. **Option numbers stay** as small orange chips with no words (bible 4.6 locks numbered options). Only the "[1] Fight" words go.
6. **Raid setup has no resource bar.** YOUR NETWORK is the page's one terminal for the Cell's state, and Heat settles on the raid report.
7. **Text scale 1.6** scales the terminal, holo and paper text and their panels. The sticker cards keep their 1080p size (about 156 × 179, Q6), and the title and verb stickers keep theirs.
8. **The work order** at 1.6 shortens "IF IT RAN NOW" to "IF RUN NOW" so it fits a 365 px column. This is a copy change for the designer.
9. **Polaroids:** the photo is a print, so the name and rank are printed on it. The status changes, so it sits on a clipped terminal chip.
10. **Rainbow gloss sweep (designer ruling this round):** exactly one sticker per screen is mid-sweep: JACK IN, START DEFENSE. UPGRADE and the title stickers are at rest. No sticker shows a hover or focus state in these stills, so no corner curl appears. The rule is: focus or hover is the peel-back only.
11. **Shop bar position:** it goes after the MAINFRAME sign rather than at x = 16, so it never covers the locked sign.

## Not done / limits
- The Godot build itself is untouched. These are concepts.
- The run-map nodes come from the round 38 v3 run map on the Priority Lane link. The hover holo reads FIGHT // L3, not L1: the page is shown mid-run so the walked path is visible.
- The raid setup shows no card being dragged, so there is no IF PLACED terminal and no yellow targeting arrow. That interaction is locked in round 40's gifs.
- At 1080p the forecast rings read small. At text 1.6 only the panels grow, not the map decals.

## Rebuild (from `scripts/`, Blender 5.2 headless; nothing here launches Godot)
1. Build the layout:
   - `python layout36.py`
   - `python emblems20.py`
   - `NET36=net_scope.json python scope39.py`
   - `RUN_V3=1 NET36=net_scope.json python runmap38.py`
2. Render the plates:
   - `NET36=net_scope.json python run38.py` (the transit camera, `t_run38`);
   - `ONLY39=r_raid,g_zoom NET36=net_scope.json python run39.py r39` (the raid camera);
   - `python run44.py hq veh` (the HQ camera `h_hq`, and the vehicle matrix for the intel silhouettes).
3. Make the screens:
   - `python hq44.py`
   - `python route44.py`
   - `python raid44.py`
   - `python topbar44.py`
   - `python contact44.py`
4. Helpers: `plan_cam.py` (where nodes land for a camera), `probe44.py` and `peek_net.py`.
5. `kit44.py` is this round's shared kit. The rest are copies of the locked kits:
   - rounds 32 and 40 (`ui31`, `sticker_lib31`, `post40`, `ui19`–`ui22`, `screens39`);
   - round 38 (`transit38`, `runmap38`);
   - round 42 (`markers42`, `city_view`, `r35ui`).
   - Their relative paths are patched for this folder's depth.

All randomness is seeded.
