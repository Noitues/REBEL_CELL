# AURELIAN CONCORD (the Roman corporation): concept package (2026-10-15)

An exploratory sixth/seventh corporation: a corporate empire in neon. It is not locked content, and nothing is
committed. The Godot build is untouched.

## Files

| File | Section | What it is |
|---|---|---|
| `identity.md` + `identity_board.png` | A | Name, tagline, what they sell, the slots, the house rule, palette with the clash check, type accent, voice |
| `crest_icons.png` | B | The LAUREL ARCH crest (vinyl, flat, 64/32/16 px), Site marker states, 7 Site-type stickers, the 32 px + twin check, the boss emblem (reference), the letterhead |
| `district.png` | C | The ordinary district in the AAA-2 night look (Blender) |
| `building_kit.png` | C | Every building generator on a plinth |
| `hq_overview.png` | D | THE CIRCUS AURELIUS: the HQ netrun overview with the route, the gates and the TARGET on THE ROSTRUM |
| `hq_mechanic.png` | D | THE TURNING GATES: four steps and the visual states (PROPOSAL) |
| `site_street.png` | F | A Site run in the V3 side-view street |
| `boss_wheel_options.png`, `boss_wheel.png` | E | **Reference only**: boss wheels moved to `docs/concepts/boss_wheel_v2/` (below) |
| `boss_wheel_ideas.md` | E | Ideas for the Boss Wheel v2 agent |
| `scripts/` | | Everything needed to rebuild (see "Rebuild") |

## Design rationale
- **Distinct from the four corps:**
  - Meridian is freight, Solace implants, Halcyon civic services and Orbital the sky. Aurelian is **food, spectacle
    and patronage debt**: bread and circuses as a subscription.
  - Its villainy is consent: you are a *client*, and the House collects.
- **Distinct from Tethys:**
  - **Up versus down:** stone, sky, statues and crowds, against water, depth and silence.
  - **Loud versus quiet.**
  - **Hue:** verdigris green against abyss blue.
  - **HQ mechanic:** a rotating plan (gates) against a vertical cycle (tide).
- **Cyberpunk, not a museum:**
  - The travertine is a brand skin over ordinary towers.
  - Statues are billboard mounts, uplit like ads.
  - The aqueduct carries data, not water.
  - The triumph arch is a toll gate with a neon inscription.
  - Neon is used as thin trim lines (the bible's skyline-trim rule), never as painted walls.
- **One idea across all scales:** the thumb (VERDICT) appears in the house rule, the boss hub, the boss emblem and the
  crowd scene on the special slice. The colosseum appears in the HQ, the boss rim and the arena Site (LUDUS).

## Designer review round (2026-10-15), applied

| Note | Change |
|---|---|
| Theme good, crest good | Kept |
| Boss emblem: good idea, bad execution | Redrawn as a clean thumbs-down with the toga cuff (`g_verdict3`). Then **moved to Boss Wheel v2**, kept here as reference |
| DOLE: profile loaf | `g_dole2`: a domed loaf in side view with three scored slashes, on a board |
| AQUEDUCT confused with a colosseum | `g_aqueduct2`: a long straight run of tall arches carrying a channel. Water rides on top and pours off the end. No rounded silhouette |
| New Senate icon | **CURIA**: a columned temple front (pediment, four columns, steps). It is the patrons' senate house, where client votes are cast. Placed after ATRIUM, so the debt office and the vote it buys sit together |
| THERMAE makes no sense | Reworked into a wheat sheaf and renamed **ANNONA** (below) |
| Boss wheel weak | Three options on the real D4 kit. A COLOSSEUM was picked. The work then moved to Boss Wheel v2 |
| Icon set check | Every icon is shown at 32 and 16 px on `crest_icons.png`. Soft IoU of the 32 px silhouettes was checked across all 18 new icons, crests and emblems of both corps: **max 0.61** (DOLE against LUDUS), under the bible's 0.68 twin limit |

**Why ANNONA.**
- The *annona* was Rome's state grain supply: the office that bought, stored and handed out grain.
- Here an ANNONA Site is Aurelian's **granary and grain office**: the vertical farm and silo where the dole's grain is
  grown and stored, and the ledger of who gets fed.
- It pairs with DOLE (where the bread is handed out): ANNONA is the supply, DOLE the hand-out.
- The name is short, Latin and unfamiliar enough to read as a brand, and it fits the inscription-caps type.
- The old THERMAE (bath-spa clinic) is retired. Its glyph is kept in `nc_kit.OLD` for the record.

## Designer review round 2 (2026-10-15), applied

| Note | Change |
|---|---|
| DOLE: no board, bring back the steam | `g_dole3`: the profile loaf with nothing under it, three steam curls rising from the crust |
| LUDUS: a front-facing centurion helmet | `g_ludus2`: face-on helmet: the transverse crest plume fanned across the top, the dome, the brow band, cheek guards, eye slits, a nose guard |
| AQUEDUCT: a couple of larger arches, two tiers, piers in water | `g_aqueduct3`: two big arches below and four smaller ones above (the kit's stacked style), the channel with water on top, the piers ending at a water line |
| Boss emblem: emoji style. The designer then clarified: the emoji **thumbs-down** look specifically | `emblem_thumb_cartoon()`: an original, chunky cartoon thumbs-down. A puffy rounded fist turned 12°, the thumb pointing down, flat skin-gold with one shadow side and one highlight, a thick ink outline, a gilt cuff with a verdigris laurel, an imperial-purple sleeve edge. Not a face (the emperor-face try is dropped). It sits on `crest_icons.png` as the reference and is noted in `boss_wheel_ideas.md` for Boss Wheel v2 (colosseum direction) |
| Kit: the triumph gate sat off its platform | `triumph_arch` now takes the slot's x (it was always built at x = 0) |
| Kit: statues → a piazza | `piazza()`: a paved travertine / marble square, a fountain with a three-figure statue group back to back, lit water jets, a verdigris line round the basin, lamp posts and benches, low colonnaded blocks framing two sides |
| Kit: arcade tower → a round campanile, not leaning | `campanile()`: a base drum, stacked arcaded galleries (a ring of 14 columns round each level's lit core, a cornice with a verdigris line), an open belfry with a gilt bell, and (designer note) **no cone: a flat crown** like Pisa's top: a cornice, a flat roof, a low parapet and a verdigris trim ring. The kit camera is now a **two-point (shifted) camera**: horizontal view, lens shift down. Verticals stay vertical, so no tower ever looks like it leans (the first preview's lean was wide-lens perspective). Campanili also replace a quarter of the district's second-row towers (`district.campanile_p` 0.25) |
| Re-check | The full sets at 32 px with the twin check: **max soft IoU 0.58** (CURIA against Tethys PUMP HOUSE). No twins |

## GDD fit

| Element | Status |
|---|---|
| A corporation = Sites (30-40), enemies + elites, a final boss at the Central Server, 3 Exploits (Intel / Breach / Virus), story paths, raids, events (GDD 4.1, 8.3-8.4d, 11.7) | Fits as is: `identity.md` fills every slot with names |
| Boss rule "X every turn unless its Hub is breached" | Fits the existing pattern (Manifest, Civic Core, Commons Array) |
| VERDICT house rule | **New rule.** It uses only existing statuses (OVERCLOCKED, CORRUPTED) and landing tiers. Needs a GDD line and a test (preview = result) |
| THE TURNING GATES (HQ mechanic) | **New rule (proposal)**, in the same family as round 43's HQ compounds (bible 4.7: all HQ mechanic rules are proposals). It needs the HQ compound itself to be accepted into the GDD first |
| Site types (DOLE, ANNONA, LUDUS, AQUEDUCT, ATRIUM, CURIA, TOLL GATE) | Art and naming only: the GDD's Sites have names, not types. The icons are the Site's regular crest disc variant |
| The 7th corp | GDD 8.5 says REBEL_CELL is the final unlock "by clearing every other corporation". Adding corps changes that unlock and the campaign count (open question 1) |

## The HQ: THE CIRCUS AURELIUS and THE TURNING GATES (proposal)

| Element | Rule (`roman_preset.PRESET["hq"]`) |
|---|---|
| Bowl | Outer wall r 150, h 46, 40 arcade bays a storey (4 storeys), neon trim per storey |
| Terraces | 4 rings `(r_out, r_in, floor_z)`: (142, 116, 34), (116, 92, 25), (92, 70, 16), (70, 50, 8). The arena floor is r < 50 |
| Rooms | Ring i has 6, 5, 4, 3 rooms (18) at preset azimuths on the far half, so they face the overview camera. They are cutaway boxes standing on the terrace against the riser behind |
| Gate rings | A bronze barrier at each terrace edge with 2 gates (`gates_now`, width `gate_w` 9°). Each step it turns `gate_step` (24, -26, 29, -31°: alternating CW/CCW) |
| Links | Along a ring: always open. Down: only where a gate stands at the room (the link passes through the gate anchor). Otherwise de-powered |
| Telegraph | The next step's gate positions in yellow pencil (round 43's one-step-ahead rule) |
| Server | THE ROSTRUM on the arena floor: porphyry plinth, a colonnade ring, a core column with lit rings, a laurel holo ring |
| Camera | High 3/4 from the south (`hq.cam`); the far half of the bowl faces it |

The route state in `hq_overview.png` is current = ring 1, room 3. Option 1 walks the ring; option 2 drops through the
open gate to ring 2.

## Procedural rules and preset keys (`scripts/roman_preset.py`)

| Key | Drives |
|---|---|
| `palette` | Verdigris, travertine, marble, porphyry, bronze, gilt |
| `light` | Neon, shop, window, streak, room, lamp, beam, uplight, HQ wash, server |
| `fog.density` | The night fog box (noise × height falloff) |
| `kit` | Storey 4.2, ground floor 6.4, column pitch 3.6, lit-window share |
| `district` | Street length, near-row cut-off, block widths, floors, tower heights, aqueduct y/z, arch y, billboards, beam rigs, camera |
| `hq` | Above |
| `street` | x range, block widths, floors, the route rooms `(column, floor)`, billboards, beams, camera |
| `kit_sheet` | The item list and the grid |
| `seeds` | district 6101, kit 6102, hq 6103, street 6104, jitter 6105, beams 6106, packets 6107 |
| `VARIANTS` | `aurelian_night` (default) and `aurelian_games` (brighter neon, denser fog: a game night) |

**Generators** (`roman_scene.py`):

| Generator | What it builds |
|---|---|
| `insula` | Colonnade ground floor with lit shopfronts, arched windows on the lower floors and a procedural window grid above, cornices every 3-4 floors with neon trims, a roof dressing (pediment with neon rakes / statue / crown) |
| `arcade_tower` | Stacked arcade tiers with setbacks, a crown ring and a beacon |
| `basilica` | Podium colonnade, drum and dome |
| `aqueduct` | Two arch tiers. The channel carries an emissive data stream with seeded packets |
| `triumph_arch` | Arch, attic, inscription, statue and laurel holo |
| `statue` | Plinth, toga cone, head and a raised arm with a laurel ring or a torch |
| `campanile` | A round, upright bell tower of arcaded galleries and a belfry with a flat crown (cornice, roof, parapet, neon ring) |
| `piazza` | A paved square with a fountain, a statue group, jets, lamps and framing blocks (review 2) |
| `room_cut` | The cutaway route room |

Lights are rule-placed: statues, aqueduct piers and the arch get uplights collected while building (`UPL`). Every face
carries a seeded tone jitter (`fj`), the Cv2 facet grain.

## Godot 4.7 feasibility
- **Geometry:** every generator is plain boxes, prisms and low-segment cylinders. Port them as a `@tool` builder from a
  corp district `.tres`, or bake them to meshes. One travertine triplanar material plus instance uniforms for the
  emission.
- **Windows:** the procedural window grid is a world-space shader (u = x + y, with per-cell white noise) and ports
  1:1.
- **The aqueduct's data stream:** a scrolling emissive band (UV × TIME) and packets on a MultiMesh.
- **Fog, beams, wet street and streaks:** as r3 (FogVolume, SpotLight3D with fog energy, SSR, the streak-lane shader).
  Nothing new.
- **THE TURNING GATES:** each gate ring is a MeshInstance3D rotated by a tween per step. Links are re-made with the
  existing link grammar. The pencil telegraph is the overlay layer.

## Open questions for the designer (for DECISIONS.md)
1. **A 6th/7th corporation** changes GDD 8.5 ("REBEL_CELL unlocks after every other corp at ICE 10") and the profile
   ladder. Is Aurelian a main-line corp or an unlockable?
2. **VERDICT:** is the GOOD landing "no verdict, the mark stays" right, or should GOOD clear the mark?
3. **THE TURNING GATES:** may you *wait* in place (a step passes without a fight) to catch a gate, or only walk? Walking
   costs a room (a fight), which is the current proposal.
4. **ANNONA and DOLE** are both food Sites. Keep both (supply and hand-out), or fold one into the Exploit Sites?
5. **Verdigris against GAIN green** (ΔE 27). Accept with the "corp hue never on a gain chip" rule, or shift verdigris
   a little toward teal (further from GAIN, nearer NET_CYAN)?
6. **Central Server name:** THE ROSTRUM (alternatives: THE CURIA, THE IMPERIAL BOX).

## Render log
See "Render log" at the end of this file (filled after the GPU queue).

## Rebuild
Run from `scripts/`. Blender 5.2 runs headless with logs in `D:/rc_scratch/new_corps/logs`. Nothing launches Godot, and
no `python -` is used.

1. **2D sheets:**
   - `python nc_sheets.py aurelian identity`
   - `python nc_sheets.py aurelian crest`
   - `python nc_mech.py aurelian`
2. **Previews** (no GPU lock): `python nc_run.py roman_scene.py <district|kit|hq|street> eevee 960x540`
3. **Finals** (hold `D:/rc_scratch/GPU_LOCK`): `python nc_run.py roman_scene.py <shot> cycles 2560x1440 samples=96`
4. **Compose:**
   - `python nc_compose.py aurelian hq plate=<npy> json=<json> res=[2560,1440]`
   - the same for `street` and `kit`;
   - `nc_post.py <npy> district.png` for the district.

**Shared scripts** (identical copies in `atlantis/scripts`):

| Script | Job |
|---|---|
| `nc_kit.py` | Corp data, glyphs |
| `nc_text.py` | Words |
| `nc_sheets.py` | A/B sheets |
| `nc_blend.py` | The Blender library |
| `nc_run.py` | The launcher; it refuses Cycles without the lock |
| `nc_post.py` | The finish |
| `nc_compose.py` | The overlays |
| `nc_mech.py` | The mechanic sheets |
| `wheel41.py` | The round 41 boss wheel plug-in (reference) |
| `glyph_test.py`, `contact.py`, `probe41.py` | Debug |

The locked kits are used read-only from `route_map_graph/hq_halcyon/scripts` and `round41_wheel_stack/scripts`.

## Render log (GPU block 16:42-16:53, designer-approved queue jump; lock released after 10.3 min)
All shots: Cycles HIP on the RX 6700 XT, plain BVH2, 2560 x 1440, 96 spp with adaptive sampling and OIDN.

| Shot | Render time | Output |
|---|---|---|
| HQ | 120 s | `hq_overview.png` |
| District | 70 s | `district.png` |
| Street | 37 s | `site_street.png` |

- `building_kit.png` is the Eevee design preview, upscaled (not in the block's priority list).
- **Known look gap.** The district's fog is light (density 0.005), so the beams barely show. Raise `fog.density` to
  about 0.008 for the next pass, or use the `aurelian_games` variant.
