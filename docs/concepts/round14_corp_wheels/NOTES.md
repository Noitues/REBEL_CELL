# Round 14: corp wheels, and the card-play preview

**Locked going in:**
- D4 "Lens & rail" frame (round 13);
- C "Screens & Data" slices with the current glyphs (the glyph, tier and state redesign is happening separately in `round14_slice_system/`);
- the V2 telemetry ring;
- phase pips.

## Files
| File | What it shows |
|---|---|
| `preview_indicator.png` | Three styles of the card-play preview on the D4 player wheel. Each shows Heavy Spin 9 (large), Flick 1, and nudge −1/+1. |
| `corp_meridian.png`, `corp_solace.png`, `corp_halcyon.png`, `corp_orbital.png`, `corp_rebel_cell.png` | One sheet per corp (layout below). |
| `corps_compare.jpg` | The 5 bosses side by side: phase 1 on top, phase 3 below. |
| `combat_orbital.png` | Night fight: Breaker vs The Commons Array in phase 2 (two readers, orbit +4, Solar Flare re-skin). **No Orbital target building exists yet,** so the backdrop is the round 6 night city view, blurred, dimmed and cooled (`make_combat.city_base`). |
| `scripts/` | Everything needed to rebuild. |

**Each corp sheet shows:**
- the theme kit: screen material, crest, accent palette, rim language with the type panel, and 6 per-type slice tiles, each with its loop described;
- then regular → elite → boss P1 → P2 → P3, with notes on what changed at each step.

**Rebuild**, from `scripts/`:
1. `python make_round14.py preview`
2. `python make_round14.py corp <meridian|solace|halcyon|orbital|rebel_cell>` (you can run the 5 corps in parallel)
3. `python make_round14.py compare`
4. `python make_round14.py combat orbital`

Renders are cached in `scratch/r`. To clear them, run `python clear_cache.py all`.

**New code:**
- `motifs.py`: the corp type panels and motifs, the type wash, and the P3 overdrive.
- `d4corp.py`: the generalised D4 frame (rails, pins, tiers, phases, preview).
- `specs14.py`, `tiles.py` and `make_round14.py`.

`skins.corp_texture` now calls `motifs.draw`. `frames.blade` gained `glyph` (special slices show their glyph in the window) and `rank` (elite chevrons).

## 1. Card-play preview (the standing NEXT arrows are gone)
The preview appears only while a spin or nudge card is hovered or aimed, or a nudge button is hovered. A spin of N moves the slices N ticks clockwise, so the landing point is the spot at −12N° on the current wheel. Aim pips are worked out from the landing tick's offset from the slice centre: 0 = PERFECT, ±1 = GOOD, ±2 = PARTIAL.

- **A Ghost blade.** A hollow dashed blade sits on the landing tick, with a ghost window showing the landing value in its program colour and aim pips under it. A comet sweep runs in the telemetry channel from the live blade to the ghost, with one dot per tick. The landing slice gets a dashed outline.
  - The strongest "where": it reads like the real pointer.
  - At ±1 it crowds the real blade (see the Flick and nudge cases).
- **B Rail jump.** The landing slice gets its own hatched rail in the ring, and a chevron run links the live rail to it. A chip outside the rim reads "FIREWALL 5 ●●○ GOOD". There is no second blade.
  - It reuses D4's rail language, so it feels native.
  - The chip is the best "what". On a small ±1 move the two rails merge into one wide band, which still reads.
- **C Ticker + split window.** Tick dots count round the hub edge to the landing tick, labelled with the count. The landing slice is hatched with a small notch at its rim. The live blade window splits to "12 ▸ 5".
  - Quietest on the slices, and best at small size and for nudges.
  - The tick dots are faint at r ≈ 100.
- **Recommendation:** B for spin cards (most informative, native to D4), and C for nudges and small enemy wheels (its split window still works at r = 60). **Open question:** the order in which multiple queued spins are previewed.

## 2. Theme inheritance
| Level | What lives there | Godot |
|---|---|---|
| **Corp** (inherited by every regular, elite and boss of the corp) | screen material, type-panel style, per-type motif loop, type wash, bezel base colour, rim language, crest, accent palette | one `CorpTheme` resource per corp: atlas + uniforms. One shared slice `ShaderMaterial` per corp (`corp_id`, `accent`, `dim`, `hot`, `paper`, `material_tex`, `motif_atlas`). |
| **Type** (inside the corp) | the motif loop played in the type panel, plus the type hairline, tab and wash colour | per-slice uniforms: `type_id`, `type_color`, `motif_cell`, `time_offset`. The glyph and value block stays universal and is a separate counter-rotated `Sprite2D` + `Label`. |
| **Enemy** | slots and values, readers (pointers), orbit, drones, hub name and core, RES badge, specials | data only (`EnemyData`, `WheelData`). No art fork per enemy. |
| **Tier** | ELITE: gold collar with corp dashes, small crest lugs, 2 gold rank chevrons on the blade, gold type-panel frame. BOSS: threat ring, crest lugs, banner-mounted crowned blade (corp colour), phase pips. | `tier` uniform plus toggled frame nodes (`EliteCollar`, `ThreatRing`, `Banner`). |
| **Phase** (bosses) | P2: the boss's own re-skin (round 6 signatures: PEAK SEASON, PAYMENT OVERDUE, STATE OF EMERGENCY, SOLAR FLARE, "runs YOUR programs"), the threat ring runs hot (red), and new readers appear as numbered **pins** with their own rails. P3: **armour plates bolt on** outside the threat ring, screens **overdrive** (contrast, accent scan bands, flicker blocks), drones dock, orbit tag; DISPATCH's two adjacent ZERO-DAY 24 slices **merge** into one 120° screen ("MERGED x2"). | `boss_phase` uniform on the corp material (0/1/2 → re-skin, overdrive). The armour is an `AnimatedSprite2D` bolt-on (plates slam in one by one). The merge is a slice node that hides its seam and spans two slots visually; the logic stays two slots. Readers come from `BossPhaseData.pointers`. |

**Corp kits (motif loops are listed on each sheet):**
| Corp | Material | Type panel | Rim | Crest | Motifs |
|---|---|---|---|---|---|
| Meridian | container steel and barcodes | shipping label | hazard stripes + notched teeth | hex | conveyors, stamps, container walls, tariff receipt |
| Solace | frosted teal cells | frosted capsule | white porcelain bezel, mint capsule studs, glass glow ring | porcelain roundel | injector, ECG spike, vial rack, mitosis, dose capsule |
| Halcyon | blueprint | title block | pale colonnade + gold halo arc | gold shield | demolition X lots, siren ENFORCE, zoning perimeter, utility nodes, citation ticket |
| Orbital | star map, **18 % brighter than round 6** | HUD brackets | steel-blue azimuth ring, 000–330 | ringed planet | debris strike, down-link beam, deflector hexes, transfer orbit, corona |
| REBEL_CELL (DISPATCH) | corrupted Cell PCB | torn terminal | broken offset black-red segments, hex rivets | broken hex | order-log lines, tear bars, port blocks, ORDER stamp |

**Godot build.**
- **Slice:** a `Polygon2D` wedge with the corp `ShaderMaterial` (shared per corp, so batching holds), with per-slice uniforms set from content.
- **Motifs:** short loops (8–12 frames) in a per-corp atlas, played inside the type-panel rect by UV (the panel sits on the inner band, outside the read plate). Swapping to a flipbook in `round14_slice_system/` would change only the atlas.
- **Frame nodes:** D4 frame (`Bezel` baked per corp, `TelemetryRing` shader, `Rails` with an array of reader angles, `Blade` + `ReaderPin` ×n), `EliteCollar`, `ThreatRing`, `ArmourPlates`, `Crest` ×2, `Banner`.
- **Preview:** a `PreviewOverlay` node fed by the forecast system's `landing_tick(card, wheel)`. It is the same code path as the forecast tag, so the preview always equals the real result (rule 6).

## Choices / open questions
- **Regular and elite drones** (for example, Care Swarm's 3 Care Drones) are not drawn on the kit wheels. Only the boss's P3 docked drones are shown.
- **The Mirror elite was replaced by The Handler** for REBEL_CELL. The Mirror copies the player's wheel, so it doesn't show the corp kit.
- **The merge rule is mine.** It applies only when a phase override puts identical adjacent slices side by side (DISPATCH P3).
- **Weakest parts.**
  - Type-panel motifs are small at r ≈ 120: they read as "this corp", not as individual loops.
  - The Halcyon material swatch is sparse.
  - In the preview, the ghost blade crowds the real blade at ±1.
