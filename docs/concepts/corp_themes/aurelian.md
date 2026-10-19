DRAFT (Batch API, Sonnet, 2026-10-18; AD review pending)

# Aurelian Concord: campaign theme, ART plan

Theme name (working): **THE RING**. A colosseum of rings. Keys and gates lead inward.
Status: concept plan only. Nothing is built.

## 0. Ground rules

### 0.1 What overrides what

| Item | Decision |
|---|---|
| HQ landmark | Keep the approved canonical colosseum (concept B, `aurelian_landmark.py canonical()`, spec 8.6b). The silhouette does not change. |
| "Rotating gate rings" (draft) | **Not built as geometry.** The draft's four turning barrier rings change the canonical massing. The mechanic behind them is unapproved (DESIGN §8). |
| Gates (designer ruling 2026-10-18) | Built as **inset gate frames on the existing route links**: vomitoria, the rim crossing, the arena stair. They are HQ-only additions, like the doorway bays. |
| Rotation | Optional art variant (B-ROT). It is a lit window sliding on the fixed ring-edge line. It is built only if the game adopts a gate rule (Q1). |
| Draft counts (6/5/4/3 rooms, 19 nodes) | Not used. Slots are generated on demand from the graph. |
| Draft Grand Stand and Favor crowd light | Not used. The vault is THE CONCORDAT VAULT in the Rostrum tholos (A3). |
| Draft teal/verdigris terraces | Not used. Neon is gilt. Verdigris is rim light only in the HQ (ruling 13.1). |

### 0.2 Shared rules (all four parts)

| Rule | Value |
|---|---|
| Loop | 4 s at 24 fps = **96 frames**. Every loop is seamless. Phase offsets are multiples of 12 frames. |
| One-shots | Entrance beat, step moves and crossing beats are not loops. They are hand-set or driven by game state. |
| Netrun frame median | 0.14 ± 0.03, set by light, not exposure. Under-0.10 share 25–40 %. Over-0.85 share ≤ 2.5 %. |
| Landmark vs local background | Target 2.0 (1.8–2.2). Under 1.5 fails. Over 2.0 warns. Finals v1 sit at 2.22–2.52, so every new emissive is paid for by trimming existing light (see B). |
| Route priority | Option links stay brighter and thicker than any theme line. Gilt lines are × 0.45 in DECISION and HOVER (`GILT_DIM_DECISION`). |
| Hover | Hovered branch lit. Others power-cut × 0.20 and 70 % desaturated (spec 9.4). Exempt from the value band. |
| Colour | Gilt #C9A35A for world lines. No verdigris paint in netruns. Verdigris #29DBA6 may be used on the raid map and Grid UI (pins, crest, wedges). Never on a Terminal edge. Never for heal or gain. |
| Stickers | ≥ 24 px at 1280 × 720. Room target 46 px tall at OVERVIEW 1920 × 1080. |
| Typography | Inscription capitals, V for U, interpuncts, Roman numerals (e.g. `PORTA · III`). |
| Room states | Use the existing UNREAD / READ / CURRENT / CLEARED look from `hq_kit.states`. The theme adds no room states. |

### 0.3 Occlusion rule (never hide route rooms)

1. Theme geometry is drawn **behind or beside** room volumes. Never in front.
2. Keep-out per room: its projected bbox inflated by 8 px (street) or 10 % (HQ). Any theme prop whose projection overlaps a keep-out is moved along its link. If it cannot move, it drops to a ghost (line only, × 0.3).
3. Theme props are dropped before city blocks are ghosted (spec 7).
4. The columns are compound geometry and are never cut.
5. Gate windows are masked by room openings (the loge openings are in the riser). They render under rooms, never over.
6. Theme props never sit on a room's door bay or arch.

## A. Street netrun: light form

**Idea:** the Ring seen at street scale. One lot ring and one triumph arch, with no keys and no vault.

### A.1 What is drawn

| Part | Look | Size (placeholder, city BU) |
|---|---|---|
| **Lot ring** | A thin gilt tube arc on the ground around each room's lot. The ellipse has ratio 0.8, echoing the bowl. The arc **opens toward the outgoing link**, and that gap is the "gate". | semi-major 3 × room width; stroke 0.12 |
| **Triumph arch** | A free-standing travertine pier pair with a gilt tube line across the top. It spans the street where a route link **crosses a boulevard**. Maximum one per crossing. | span ≈ boulevard width (9.5); height ≈ 6; thin piers |
| **Skyline laurel** (optional, off by default) | A faint far gilt ring-arc glint over the HQ direction. | n/a |

### A.2 States

| State | Lot ring | Arch |
|---|---|---|
| UNREAD | Gilt × 0.30, open | Line × 0.30 |
| READ | × 0.50, open | × 0.50 |
| CURRENT | × 1.0, open, with the pulse | × 1.0 |
| CLEARED | Closed (gap filled), travertine-dim, × 0.40 | × 0.60 |
| HOVER | Follows the hover rule (× 0.20, desaturated) | same |

### A.3 Motion (96 frames)

- CURRENT lot ring: one bright segment runs once around the arc. f0 → f96, linear, seamless.
- Arch top line: breathes ±10 % sine, one period.
- All other rings are static.

### A.4 Overlay

None. The light form is world-only. The existing room stickers and link labels are unchanged.

### A.5 Colour and value

- Gilt only. No verdigris.
- Theme props never outshine the room they frame: ≤ 1.3 × local background.
- Props' pixels above 0.5 luma are ≤ 1 % of the frame, so the 0.14 median is not lifted.

### A.6 Occlusion

- Rule 0.3 applies in full.
- Lot rings are flat on the ground, so they cannot cover room faces. The arch is placed at least one room-width away from the nearest room front, and is checked in projection.

### A.7 Frames

| ID | Content |
|---|---|
| A01 | Street netrun, full route, CURRENT mid-route, f0 |
| A02 | Same, f48 (pulse half way round) |
| A03 | State strip: UNREAD / READ / CURRENT / CLEARED lot rings on one street |
| A04 | Arch crossing a boulevard, link passing through |
| A05 | Arch moved to ghost by the keep-out rule (forced overlap test) |
| A06 | HOVER frame with a power-cut ring |
| A07 | Value check frame with a luma histogram |
| A08 | (optional) Skyline laurel on |

## B. HQ netrun: full form

**Idea:** the approved canonical colosseum, with the route going outside-in. It climbs the loggia tiers, crosses the rim, then descends the four seating rings through gates to the Rostrum tholos.

### B.1 What is drawn

- **Landmark:** canonical, unchanged.
- **Route levels:** T1–T3, AT, R1–R4, VAULT, with slots generated per concept B.
- **Gate frames (new, HQ-only).** One at each level-change link:
  - the rim crossing;
  - R1→R2, R2→R3 and R3→R4 (vomitoria);
  - the R4→vault arena stair.
- **Gate look:** a gilt tube arch inset in the riser, about 2.4 wide × 3.0 tall (fits the 3–4.5 BU risers). It has travertine jambs and a lit threshold slab. The link runs through it.
- **Vault:** unchanged, with the red pencil TARGET ring on the plinth.
- **Entrance beat (hand-set):** a street-level triumph arch with **three key sockets** (INTEL, BREACH, VIRUS) lit by the owned Exploit count. Conditional on Q3.

### B.2 States

| Element | State | Look |
|---|---|---|
| Rooms | UNREAD / READ / CURRENT / CLEARED | Existing look |
| Gate | Link available (option) | Lit, full |
| Gate | Link taken (CLEARED) | Settled, × 0.5 |
| Gate | Link not offered | Power-cut × 0.20 |
| Gate | HOVER | Lit, with a `PORTA · III` tag |
| Gate | SHUT *(conditional, Q1)* | Bronze shutter slats in the arch, threshold dark |
| Vault core | Existing state-driven emission | Unchanged |
| **B-ROT** *(conditional, Q1)* | Gate is a lit window on the ring-edge gilt line | Slides 36 frames, ease in-out. A pencil-yellow ghost window shows the next position. |

### B.3 Motion (96 frames)

| Loop | Detail |
|---|---|
| Ring-edge pulse | A highlight travels along each ring-edge gilt line. Phase offset +12 frames per ring, outer to inner, so the pulse reads as "inward". |
| Laurel ring | Rotates 22.5° (one of 16 leaves) f0 → f96. Seamless by symmetry. |
| Core rings | 4 gilt rings breathe ±12 % sine, staggered 24 frames. |
| Searchlights | Sweep ±6° sine. Cone stays above 10°, no shadow. |
| Open gates | Breathe ±8 %, 48-frame period. |
| Crown beam | Pulse ±10 %, one period. |

The pulse and the gate breath are removed in HOVER frames.

### B.4 Overlay glyphs and gauges

- **Depth gauge:** 9 pips (T1, T2, T3, AT, R1–R4, VAULT). The current pip is filled. Travertine on a porphyry back. Pips ≥ 24 px at 720p. This is a pure data readout of the current level.
- **Gate tag:** `PORTA · I…IV`, hover only.
- **Key row** (entrance beat only): three Exploit icons in their existing art.
- **TARGET sticker:** unchanged (engine behaviour).

### B.5 Colour and value

- Gilt lines × 0.45 in DECISION and HOVER.
- Verdigris appears only as rim light.
- **Gate light budget:** each new gate emissive is paid for by trimming `ov_loggia` or the arch glow in the same frame. OVERVIEW is already at 2.52 and must not rise. Target 2.0–2.2.
- Gate emission ≤ 0.8 × a lit option link.
- Per-frame stop trims are kept as in the last test.

### B.6 Occlusion

- Gates sit at link ends. Room azimuth keep-out = room half-width 1.65 + 1.0 BU.
- Gate frames never enter loge openings or doorway bays.
- Rule 0.3 for B-ROT: the sliding window is masked under rooms, and fades when it comes within 8 px of a room bbox.
- Near-half gates are seen only from DECISION cameras, as for near-half slots.

### B.7 Frames

| ID | Content |
|---|---|
| B01 | OVERVIEW, full route, f0 (value frame) |
| B02 | OVERVIEW, f48 (ring pulse offset) |
| B03 | DECISION, loggia, at T3 → AT |
| B04 | DECISION at the AT → R1 crossing (rim gate, opposite normals) |
| B05 | DECISION, cavea, R2 with the R2→R3 gate offered |
| B06 | HOVER on a gate with the `PORTA · III` tag |
| B07 | Gate state strip: available / taken / not offered / HOVER |
| B08 | Vault DECISION, TARGET lit |
| B09 | Entrance beat, last frame, arch with 0 / 2 / 3 keys (three small insets) |
| B10 | (conditional) B-ROT: gate window at f0 / f18 / f36, with the pencil ghost |
| B11 | (conditional) SHUT gate close-up |
| B12 | Value sheet for B01, B03, B05 (median, shares, ratio) |

## C. Raid hook (city / raid map)

**Idea:** an Aurelian raid draws the colosseum around the raided node. Rings close in, with keys on the outer ring, gates in each ring, and the Levy wedges approaching along the lanes.

Assumption: the centre is the defended home-server node (Q4).

### C.1 What is drawn

| Part | Look |
|---|---|
| **Ring set** | 4 concentric ellipses (ratio 0.8) centred on the node. Verdigris, 2 px at 1080p, alpha ≤ 0.6. |
| **Gates** | A gap in each ring, drawn as a small arch glyph in gilt. Count and azimuth come from data. |
| **Keys** | 3 key glyphs on the outer ring, using the existing Exploit icons. |
| **Lanes** | Radial dashed approach lines from the outer ring to the centre. |
| **Levy wedges** | The existing legion wedge markers (verdigris) and the gilded float. |
| **Ring index** | Roman chips I–IV at each ring's north tick. |

### C.2 States

| State | Look |
|---|---|
| PENDING | Rings as ticks only (dashed, × 0.4) |
| ACTIVE | Rings lit, wedges on lanes |
| Ring breached | That ring's gate arch opens (gap widens), ring dims to × 0.6 |
| Key held / not held | Icon lit / outlined |
| DEFENDED | Rings fade out inward (24 frames) |
| LOST | Rings collapse to the centre and the pin takes the PACIFIED stamp |

### C.3 Motion (96 frames)

- Ring dashes march inward. The dash offset is one period per 96 frames, with +12 frames of phase per ring.
- Key glyphs breathe ±10 % (held keys only).
- Wedge advance is state-driven, not looped.

### C.4 Overlay

Ring chips, key icons and gate arches are the whole overlay. Chips and key icons are ≥ 24 px at 720p. The LEVY RECEIPT is a separate after-action screen and is out of scope here.

### C.5 Colour and value

- Verdigris ring lines on the map. Never used for a heal or gain chip.
- Gilt arches only in small doses.
- Key icons keep their Exploit gold. Keep ring strokes thin so they do not read as Exploit gold.
- No netrun luma band applies. The overlay stays below node pins in brightness.

### C.6 Occlusion

- Ring strokes sit **under** all pins, labels and other raid markers.
- A mask of pin radius + 6 px breaks the strokes at every pin.
- Ring labels never overlap the node pin.

### C.7 Frames

| ID | Content |
|---|---|
| C01 | PENDING |
| C02 | ACTIVE, wedges on the outer ring, f0 |
| C03 | ACTIVE, f48 (dash phase) |
| C04 | Ring 2 breached, one gate open |
| C05 | Key states: 0 / 1 / 3 held |
| C06 | DEFENDED fade, f0 / f12 / f24 |
| C07 | LOST |
| C08 | Pin mask test over a dense node cluster |

## D. Grid (city map) layer

**Recommendation:** a small layer. A full second system is not needed.

### D.1 What is drawn

- **HQ stamp:** the colosseum icon on the Aurelian HQ landmark.
- **Ring contours:** 3 faint ring lines around the HQ stamp (ratio 0.8), like contours. They show the district.
- **Toll arches:** small arch marks on boulevards at the district edge. They echo the TOLL GATE site and the street arch.
- **Heat flavour** (identity.md) is reused, not new:
  - NOTICED: lictor drone dots.
  - FLAGGED: statue eyes go red.
  - HUNTED: the arch marks switch to a sealed look.

### D.2 States

| State | Look |
|---|---|
| Default | Contours at alpha 0.25 |
| HQ unlocked (data) | Contours alpha 0.45, stamp lit |
| Heat bands | As identity.md. The contours are not changed by Heat. |

### D.3 Motion (96 frames)

One slow pulse runs outward along the three contours, 96-frame period, with a 12-frame phase between rings.

### D.4 Overlay

None added. The layer is one toggle among the existing Grid layers (Q7).

### D.5 Colour and value

- Verdigris for stamp and contours, as the corp pin colour.
- Gilt for arch marks.
- Contours ≤ 1 px at 1080p.

### D.6 Occlusion

Contours are drawn under node pins and the raid ring overlay. They are hidden when a raid overlay is active on a node inside the district.

### D.7 Frames

| ID | Content |
|---|---|
| D01 | Grid with the layer off |
| D02 | Layer on, default |
| D03 | HQ unlocked |
| D04 | Layer on with a raid overlay (C02) inside the district |
| D05 | Heat strip: NOTICED / FLAGGED / HUNTED |

## E. Kit reuse vs new

| Reuse (already in the notes) | New |
|---|---|
| `canonical()` landmark, city `build(ctx)`, `build_hq` | Gate frame prop (inset vomitorium gate, HQ-only) |
| `slots()`, `level_of()`, link geometry by step class | Lot-ring decal with travelling-pulse shader |
| `bays_for()` and the `Cutter` pattern (as the template for gate insets) | Triumph arch prop (street) |
| `hq_kit.states` state colours | Ring-edge pulse (the ring-edge lines are already separate objects) |
| `GILT_DIM_DECISION`, light rig, per-frame stop trims | Depth gauge overlay |
| `hq_mechui.py` (neutral panel pattern) | Raid ring overlay (rings, ticks, chips, lane dashes) |
| `downtown.build` `mast_pad` and `transparent_max_bounces` 128 | Grid ring contours and toll-arch marks |
| Exploit icons, legion wedge markers, TARGET sticker | Optional: B-ROT sliding window and SHUT shutter |

## F. Risks

| Risk | Mitigation |
|---|---|
| Gate arches read as extra rooms and break the 46 px room rule | Arch shape only, gilt line, no state-colour hues, low contrast |
| OVERVIEW ratio already 2.52 | Net-zero light budget (B.5). Re-test the OVERVIEW first. |
| Gilt pulse competes with orange option links | Gilt × 0.45 in DECISION. Option links stay brighter and thicker. |
| B-ROT window passes loge openings | Mask under rooms plus the 8 px fade. B-ROT is optional. |
| Street arch placement needs link-crosses-street data | Fall back to lot rings only (A without the arch) |
| Raid overlay and Grid contours clutter dense maps | Pin masks, alpha caps, contours hidden during a raid |
| Other corps' themes may use rings or arches | Check against the other four corps' campaign themes before finals |
| Near-half gates (more than 16 route layers) | DECISION-only visibility, accepted as for slots |

## G. Questions for the build session

| # | Question |
|---|---|
| Q1 | Does the game adopt a gate rule (open/shut, step clock)? Art default: gates are static markers on existing links. B-ROT and SHUT need the rule. |
| Q2 | If yes: per frame, which fields? Needed: `step_count`, `gate_angles_now`, `gate_angles_next`, per-link `powered` and `opens_in_steps`, `held_rings`. |
| Q3 | Are the keys the three Exploits (INTEL, BREACH, VIRUS)? Does the HQ entrance gate check them (`min_exploits_for_breach`)? Art needs the owned count. |
| Q4 | In the raid view, does "the HQ" mean the defended home-server node or the Aurelian HQ? Art centres the rings on the defended node. |
| Q5 | Raid data: how many rings and gates per raid, who holds keys, and what ring breach or key means for the player? |
| Q6 | Does a street netrun flag which link segments cross a boulevard? The arch needs that. Does the street netrun show the HQ landmark at all? (A.1 skyline laurel.) |
| Q7 | How are Grid layers toggled and how many are allowed on at once? |
| Q8 | Raid state names: do PENDING / ACTIVE / DEFENDED / LOST match the game's? |
| Q9 | Should the ring count of the HQ (4 seating rings) be a fixed art fact, or follow the generated level count? |