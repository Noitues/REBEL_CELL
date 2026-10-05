# Round 42: the HQ room

The Cell's den sits above the canyon street. The window view is the locked canyon render (`round30_rebel_cell/canyon_home.jpg`, and `round34_rebel_cell/canyon_dispatch.jpg` for the DISPATCH variant). The room is Cv2 low-poly with E toon bands and ink lines, rendered in Blender.

It follows the locked mediums:
- **CRT** for the Cell's systems;
- **stickers** for objects and station labels;
- **grease pencil** for plans (on the window glass only);
- **paper** for corp documents (the WANTED poster).

Portraits are the round 39 cel busts on the CRT feed.

## Files

| File | What it shows |
|---|---|
| `hq_room.png` | The room at night, in rain. Every station is in view and labelled with a sticker. |
| `hq_actions.png` | Four actions in use: patch home and repair nodes, Black Market, crew roster, scrub Heat. |
| `hq_room_dispatch.png` | The betrayal variant: the same room after DISPATCH is revealed. |

## Stations (GDD 3.3, 5.4, 11.4; art_asset G8, C3)

| Station | Where | Medium | Action |
|---|---|---|---|
| **The deck** | Desk, front left: a big CRT showing the City Grid mini-map | CRT, JACK IN sticker | Opens the City Grid, then JACK IN |
| **Cell status** | Desk, front right: a CRT | CRT | Home integrity, exploits, sites, armory, Schematics, Heat band |
| **Crew wall** | Left wall: 6 stacked TVs, one live feed per operative | CRT feeds, CREW sticker | Loadout, Station / Recall. Feeds show stationed (tinted), hurt, flatlined (NO SIGNAL; the slot is kept) and an open slot (recruit, grey). |
| **Home server rack** | Right corner: a rack with blinking LEDs and an integrity CRT | CRT, HOME sticker | Patch: 1 Schematic per integrity point |
| **Repair bench** | Under the window: node modules with LEDs, a soldering iron, a lamp | Sticker REPAIR | Repair Disabled nodes for 50 % of install |
| **WANTED poster and scrubber** | Back wall, left of the window: the corp's poster (paper), the scrub CRT and the pirate radio on a shelf | Paper and CRT | −5 Heat for 25 Schematics, +10 each purchase. The poster updates with Heat. |
| **Black Market** | Right wall: a half-open roller-shutter hatch with warm light, a counter and crates, and the fixer's CRT feed beside it | Sticker BLACK MARKET, fixer feed | Recruit (15), next-run boosts, profile unlocks |
| **Window** | Back wall | Grease pencil on the glass | Tonight's plan in yellow (LANE 15 circled with an arrow), threats in red (DRONES) |

**Lived-in props:**
- the mattress, crates, plants and rug;
- the noodle cup, the can and a paper plan on the desk;
- the cable bundle along the ceiling, the bare bulb and the pink Cell neon strip;
- the "NEVER SLEEP" tube sign over the window (the title slogan, placed once);
- a "TRUST NO ONE" sticker on a monitor.

**Rule kept: no UI over grease pencil.** The pencil lives only on the window glass, and every panel and label sits outside it.

## Action panels (`hq_actions.png`)

Each panel opens over its station, with the room blurred behind it.

| Panel | Contents |
|---|---|
| **Patch + Repair** (the HOME CRT) | Integrity bar 31 → 41 with a ghosted preview segment, the cost line, and a repair list (Disabled nodes with their costs). |
| **Black Market** (amber CRT) | The fixer's live feed with a quote. Three rookies on grey recruit feeds at 15 Schematics each, next-run boosts, and a profile unlock (class 80). |
| **Crew roster** (lime CRT) | One row per operative: feed, name, class and rank, status, and the order buttons LOADOUT \| STATION or RECALL. A flatlined row keeps its slot. |
| **Scrub Heat** | The paper WANTED poster takes a "−5 HEAT" stamp and its bar drops, 52 → 47. The scrub CRT shows the band, the cost, the next price and the wallet. |

## DISPATCH variant (`hq_room_dispatch.png`)

The same room after the reveal (GDD 8.2: DISPATCH was the AI all along; REBEL_CELL is a corporation):

| Element | What happens |
|---|---|
| Lights | Every light and screen turns REBEL_CELL red. |
| Window | Shows the DISPATCH canyon (the fist hologram, the struck-out signs). |
| Neon sign | Flips to NO MORE MAN. |
| Crew wall | The TVs become DISPATCH voice traces (UNLINKED, FLESH IS A BUG): it has cut the crew's feeds. |
| City Grid | Reads REBEL_CELL // OWNED, NO MORE MAN, and JACK IN [REVOKED]. |
| Status monitor | OBSOLETE: YOU. |
| Black Market | CONTACT LOST, and the hatch glows red. |
| Home server | OWNED by REBEL_CELL. |
| WANTED poster | Stamped OBSOLETE. |
| Station stickers | Faded to grey; JACK IN and CREW are peeling. |
| The plan | Tonight's plan is scratched out in red, with "IT WAS DISPATCH" circled. |
| Glitch | The whole frame glitches with horizontal tears. |

## Godot build notes

- **The room:** a pre-rendered backdrop (or the low-poly scene in a SubViewport). Each screen is a quad with the CRT CanvasItem shader, fed by a SubViewport running the live Control UI.
  - `hq_scene.py` exports every screen quad's corners (`quads_*.json`) so the warps line up.
  - In Godot the screens are MeshInstance3D quads with ViewportTextures.
- **Hover and select:** hovering a station lifts its sticker (as for cards) and brightens its screen. Clicking dollies the camera toward the station and opens its CRT panel full-size, with the room blurred behind it (as in `hq_actions.png`).
- **Window:** the window shows the corp district of the current campaign. The rain is a shader on the glass. The grease pencil is a Line2D layer clipped to the window rect, holding the plan for the next run.
- **DISPATCH variant:** a theme swap (light colour, screen content, sign text, the window plate) plus a glitch post-process.

## Open for the designer
- The Black Market is a hatch in the wall with a fixer behind it. Should it be a separate place instead, like the Modem?
- Station-by-dolly (diegetic) or a flat menu over the room?
- Where do the Codex, Settings and Save live? The proposal is the deck's menu (art_asset G8).

## Scripts

| Script | What it does |
|---|---|
| `run_room.py` | Prepares the two window views and renders the room twice in Blender (`hq_scene.py`). |
| `render_busts.py all` | Renders the portrait busts (`bust_rig.py` from round 39). |
| `hq2d.py` | Warps screens, adds rain, pencil, neon and stickers, and writes the three PNGs. |
| `r31lib.py`, `sticker_lib19.py`, `portraits.py` | Copied. |
| `clear_scratch.py` | Clears scratch. |
