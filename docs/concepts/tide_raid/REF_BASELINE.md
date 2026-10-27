# Tide raid: reference baseline (fresh critic, 2026-10-27)

Purpose: set the bar a REBEL_CELL city-map raid screen must beat (BRIEF_POLISH "Target"). Rubric: each axis /10, with 10 = best
shipped example in the genre. V is against AAA. Readability = squint read, colour-blind safety, clutter control. Motion/feel
and Wordlessness are as defined in the brief.

## Bar summary (updated 2026-10-27 with footage; see "Motion evidence" at the end)
**S 8 · V 9 · Readability 9 · Motion 9 (was 8) · Wordlessness 9.** Only Motion moved: Cyberpunk 2077's quickhack overlay
(footage-verified) sets it to 9. Motion strips: `ref_motion/` (36 files); timing cheat-sheet at the end of this file.

## Evidence and honesty flags
- **Update:** Motion (and the WD2/CP2077 overlays) are now re-scored from Steam trailer footage; see "Motion evidence". The line
  below that says every Motion score is from knowledge is superseded for every game except Google Maps.
- Images: official Steam store screenshots, in `D:/rc_scratch/tide_concepts/refs/<game>/`, URLs in `refs/SOURCES.md`.
  Contact sheet: `ref_baseline_sheet.jpg` (4 frames per game, 8 games).
- **Seen as images:** Into the Breach, Mini Metro, Frostpunk, Invisible Inc., Frozen Synapse, Bad North.
- **Frames fetched but not the target screen (scored partly from knowledge):** Watch Dogs 2 (the store frames are open-world
  beauty shots, no ctOS overlay) and Cyberpunk 2077 (store frames show no Breach Protocol or scanner).
- **No images fetched, scored from knowledge only:** Google Maps 3D / Immersive View.
- Motion/feel is never visible in stills: every Motion score is from knowledge of the games' animation, flagged as such.

## Score table

| Reference | S | V | Read | Motion | Wordless |
|---|---|---|---|---|---|
| Into the Breach (enemy-intent turn) | 7 | 6 | **9** | 6 | 7 |
| Watch Dogs 2 (ctOS / DedSec) | 7 | 8 | 5 | 6 (was 7) | 6 |
| Cyberpunk 2077 (Breach, scanner) | 7 | **9** | 5 | **9** (was 7) | 4 |
| Google Maps 3D / Immersive View | 3 | **9** | 8 | **8** | 8 |
| Mini Metro | 6 | 5 | **9** | **8** | **9** |
| Frostpunk | **8** | **9** | 6 | 6 | 6 |
| Invisible Inc. | 7 | 7 | 8 | 6 (was 5) | 6 |
| Frozen Synapse | 7 | 5 | 8 | 7 | 7 |
| Bad North | **8** | 8 | 8 | 7 (was 8) | **9** |

## Per-reference notes

### Into the Breach (S7 V6 R9 M6 W7)
- **Earns it:** the intent telegraph is the genre's best readability: every enemy attack is an arrow and a red-tinted target
  tile, shown before you commit. A grid of flat-lit tiles, one hue per meaning (blue = yours, red = threat), a clean dark
  frame. Tension comes from the deterministic "you can see exactly what will go wrong" board. 3D-ish isometric props give
  depth without noise.
- **Borrow/beat:** (1) intent is drawn ON the world, from source to target tile, always visible, never behind a hover;
  (2) one threat colour, one friendly colour, one neutral: all else is desaturated; (3) the previewed outcome (damage pips on
  the target) is shown in-place, so the player never does arithmetic. REBEL_CELL must beat it on lighting and material
  (ITB is flat sprites) while keeping its legibility.
- **Weaknesses:** low V (sprite tiles, UI-heavy chrome, text-dense side panels); the board is small and static, so little
  spectacle; red/blue read is mostly hue, weak for deutan without the arrows; animation is brisk but plain.

### Watch Dogs 2 (S7 V8 R5 M7 W6; overlay from knowledge)
- **Earns it:** a real, lit, occluded city (fog over the bridge, towers, depth) with the ctOS layer as glyphs and
  wireframe-ish markers anchored to world objects. The jack-in is the player's power fantasy; objects get hacked "in place"
  so the overlay feels like part of the city.
- **Borrow/beat:** (1) markers pinned to world geometry with depth fade and occlusion; (2) hover-to-reveal context (the
  ping/profiler): much info appears only on focus; (3) photographic city as the base, thin line-art as the layer.
- **Weaknesses:** overlay clutter in dense scenes, icon soup, small text, white/cyan on bright daylight washes out;
  the hacking overlay is a utility, not a composed spectacle; colour carries too much meaning.

### Cyberpunk 2077 Breach Protocol and scanner (S7 V9 R5 W4 M7; from knowledge)
- **Earns it:** AAA lighting, neon and atmosphere; the scanner desaturates the world and tints interactables, a strong
  "mode shift" that makes the layer feel like a different way of seeing. Breach Protocol is a tight green-on-black
  code matrix with a timer: tense, stylish, instantly its own thing.
- **Borrow/beat:** (1) the world-grade shift on entering the hack layer (desaturate, contrast, tint the actionables);
  (2) one saturated accent against a restrained field; (3) type with rhythm: monospaced, tracked, tiny labels as texture.
- **Weaknesses:** scanner is cluttered and text-heavy; Breach is almost pure text/hex (Wordless 4); fine type and thin
  glow fail the squint test; red/green/yellow semantics are poor for colour-blind players; Breach has no map.

### Google Maps 3D / Immersive View (S3 V9 R8 M8 W8; no images fetched, from knowledge)
- **Earns it:** photoreal city with correct occlusion, soft light and fog; the route is a single bold ribbon draped on
  the streets with a halo, the rest of the city is quietly de-emphasised. Camera flights ease like a film dolly. It is
  the benchmark for "a route over a real 3D city reads at a glance".
- **Borrow/beat:** (1) a route ribbon with an outer halo and a bright core that hugs the street, occluded by buildings
  with a faint see-through ghost; (2) de-emphasis by blur/desaturation of everything off-route; (3) eased, parallax
  camera moves that frame the route, not cuts.
- **Weaknesses:** no tension or stakes; no threat grammar; zero spectacle (S3); uniform tone, so no drama; labels are
  text-based for places.

### Mini Metro (S6 V5 R9 M8 W9)
- **Earns it:** pure squint design: flat colour field, thick coloured lines, five shape icons. Meaning is carried by
  shape + colour + position, with a tiny text count. Tension is the mounting pile of waiting shapes and a ring timer
  (pressure with no words). Motion: trains glide and settle with soft easing, lines snap and redraw smoothly, and the
  whole thing feels hand-made. Audio-reactive (from knowledge).
- **Borrow/beat:** (1) pressure shown as a physical quantity (a ring filling, a pile growing) not a number; (2) shape-coded
  identity so colour is never the only channel; (3) smooth eased line redraws that read as intent.
- **Weaknesses:** V is deliberately flat (nowhere near AAA); little depth; no lighting or material.

### Frostpunk (S8 V9 R6 M6 W6)
- **Earns it:** painterly, moody isometric city under snow with a heat-glow palette; the heat-map overlay (frame 4) is
  a real data layer over geometry with warm/cool contrast. Strong light-on-dark composition, fire as the focal point;
  the city reads as a living thing under threat (cold front, storm), conveying stakes through the world.
- **Borrow/beat:** (1) the whole city lit by a single threat/relief colour logic (cold = bad, orange glow = safe);
  (2) a data-overlay mode that extrudes the layer on top of the same geometry (frame 4 style); (3) the approaching
  storm as a horizon-scale, readable front.
- **Weaknesses:** the UI is dense and small-text; overlay colours (red/yellow/cyan on a heat map) are poor for deutan;
  mid-zoom is busy; motion is mostly ambient rather than a choreographed beat.

### Invisible, Inc. (S7 V7 R8 M5 W6)
- **Earns it:** a stylised isometric office with strong value structure: dark ambient, warm pools of light, red vision
  cones and tile outlines as the only saturated elements. Rooms outside vision go dark, so occlusion/fog is drawn into the
  design. White tile outlines for move/targets, red striped zones for guard sight: threat is a shape, not a label.
- **Borrow/beat:** (1) threat zones as hatched/striped shapes, giving a non-hue channel; (2) darken everything not
  in play so lit things pop; (3) outline-on-tile for selectable targets, one consistent line weight.
- **Weaknesses:** animation is functional and slow; the environment is repetitive; the stakes are shown by small icons
  and text.

### Frozen Synapse (S7 V5 R8 M7 W7)
- **Earns it:** plan-then-simulate is exactly the raid loop: you draw paths, then a playout resolves, with a scrub-able
  replay. A restrained blue-on-blue world with glowing emissive lines for shots, bright flare impacts and a clear
  "what will happen" preview line.
- **Borrow/beat:** (1) the planning-to-playout transition as a visible mode change; (2) impact flares: a bloom
  flash plus streak lines make a hit feel earned; (3) a scrub timeline on the playout.
- **Weaknesses:** abstract, bare geometry (V5); a single palette, so threat vs friend relies on hue; no atmosphere.

### Bad North (S8 V8 R8 M8 W9)
- **Earns it:** toy-diorama islands with soft light, long shadows and fog; the incoming longships are seen from far out
  and read by silhouette; the pressure is in the sea itself. Colour is limited (red raiders vs blue defenders), so
  the squint read is strong. Animation (waves, ship approach, buildings burning) sells the moment with no text.
- **Borrow/beat:** (1) the silhouette-first threat: the incoming thing is the biggest dark shape in the frame;
  (2) a soft, desaturated environment with two accent hues only; (3) fire and collapse as the loss language.
- **Weaknesses:** stylised, not AAA-realistic; red/blue has deutan risk (mitigated by silhouettes); lighting is
  low-contrast and flat at times.

## The bar (best score per axis)

| Axis | Best | Held by | What it means |
|---|---|---|---|
| S (spectacle / tension) | **8** | Frostpunk, Bad North | The threat is a world-scale presence; the loss is visible on the map |
| V (visual quality vs AAA) | **9** | Cyberpunk 2077, Google Immersive View, Frostpunk | Real lighting, occlusion, materials, atmosphere |
| Readability | **9** | Into the Breach, Mini Metro | One meaning per colour, shape-coded, intent drawn on the board |
| Motion / feel | **9** | Cyberpunk 2077 quickhack overlay (footage-verified); next: Mini Metro 8, Google 8 (knowledge) | Eased, readable, wordless animation; asymmetric fast-out/short-in mode switches, held impacts |
| Wordlessness | **9** | Mini Metro, Bad North | The state is readable with all text removed |

(No single reference beats 8 on S, so S is the easiest axis to clear; V and Readability are the hard ones because the
best-in-class on each is held by a different game: nobody combines AAA V9 with Readability 9.)

## What "beating it" requires of a city-map raid screen
Beating = a fresh critic scores the plate set **S 9, V 10 (or at least 9 plus the clearest read of any of them),
Readability 10 (at minimum 9 with no axis below the reference)** on this rubric. Concretely:

1. **V >= 9 while R >= 9 at once.** Real Blender-lit city with occlusion, materials, fog and bloom (CP2077 / Google
   level), yet the squint strip shows exactly three things: the beam, the HOME, the defended Sites. Nobody in the
   baseline has both; this is the win condition.
2. **The threat as a physical object, not a UI glyph.** Beams and the Bloom front are lit geometry in the street canyon,
   occluded by buildings with a faint see-through ghost (Google route ribbon), with a silhouette readable at 25% size
   (Bad North). Intent is drawn on the map from source to target (ITB), with the preview damage in place.
3. **Pressure shown as quantity, not numbers** (Mini Metro ring/pile; Frostpunk cold front): a visible HOME integrity
   and a Bloom that creeps in the frame, so S >= 9 without reading text.
4. **Shape + hatch + value, not only hue.** Every state has a non-colour channel (Invisible Inc. hatched zones, Mini
   Metro shapes); deutan and tritan sims must keep every state distinct; one threat accent, one friendly accent.
5. **A world-grade shift on jack-in** (CP2077 scanner / WD2 ctOS): the city desaturates and the actionable things are
   tinted, rather than a UI skin laid over an unchanged city. De-emphasise everything off the route (Google).
6. **Beat impact language.** A playout with flare + streak + screen-space bloom at the HIT and a held aftermath
   (Frozen Synapse), with a visible loss state (Bad North fire). A static plate must show the impact frame at full finish.
7. **Wordlessness test:** strip all text; a naive viewer still states what is attacking, what is defended and what is
   about to be lost. Text, when present, is large, short and typographically final (CP2077 fine-type is the cautionary
   tale: not thin, not tiny).
8. **Motion concepts must match the best (Mini Metro, Bad North, Google):** eased, anticipatory, with holds on the
   impact; each has a reduce-motion variant that keeps the meaning (a hold and a flash instead of a travel).

## Top 5 techniques to beat or borrow
1. **Intent drawn on the world, source to target, with the outcome previewed in place** (Into the Breach).
2. **Route/beam as a lit ribbon hugging the street with a halo, occluded by buildings, off-route city de-emphasised**
   (Google Immersive View, Watch Dogs 2 depth-pinned markers).
3. **World-grade shift when the layer opens: desaturate the city, one saturated accent, tint the actionables**
   (Cyberpunk scanner, Frostpunk heat-map overlay on the same geometry).
4. **Pressure and loss as physical quantity and silhouette, not numbers** (Mini Metro pile/ring, Bad North longships,
   Frostpunk storm front).
5. **Non-hue channel on every state (hatch, shape, outline weight) plus an impact flare/streak with a hold** (Invisible
   Inc. striped sight zones, Mini Metro shapes, Frozen Synapse impact bloom).

## Caveats
- Scores are one critic's judgement on partial evidence (see flags above); the Google and the two hacking-layer scores
  are knowledge-based and should be re-checked against captured frames if the bar becomes contentious.
- Reference games differ in genre; the bar is an axis maximum, not a single game to match.

---

# Motion evidence (footage, 2026-10-27)

Source: official Steam store trailers (URLs and sizes in `D:/rc_scratch/tide_concepts/ref_video/SOURCES.md`; videos are scratch-only, not
committed). Strips with timestamps and frame offsets (30 fps, so +3f = 100 ms): `docs/concepts/tide_raid/ref_motion/<game>_<moment>_<K>f.jpg`
where `<K>f` is the frame interval between cells. Four `hold_*` single frames. Frame counts below are read off those strips.

## Limits of this evidence (read first)
- Trailers are edited: cuts, slow-mo and time-dilation are the editor's or the game's, not always UI behaviour. 480p for ITB, Mini Metro,
  Frostpunk, Frozen Synapse, Bad North, Invisible Inc.; 720p for WD2 and CP2077.
- **Breach Protocol was not found** in the two CP2077 videos used (Netrunner build video, Gameplay trailer); the Breach score is still
  knowledge. The CP2077 evidence is the quickhack/scanner overlay and the camera-hack/net view.
- **WD2 in-game ctOS profiler/hack overlay is barely in WD2 footage.** The "ctOS city map" and "DedSec takeover" frames are marketing
  motion-graphic stings; the 85-107 s profiler tags look like Watch_Dogs 1 B-roll. They are valid as motion-language references, not as
  evidence of WD2's in-game overlay behaviour.
- The Invisible, Inc. hack overlay at 0-3 s is a CGI cinematic; its in-game grid reveal at 30 s is real. Mini Metro's trailer is mostly an
  animation; only about 4 s is the real network.
- Screen shake / hit-stop: checked at 1-2 frame spacing on the ITB hit, the CP2077 hack burst and the Frozen Synapse flare. No shake and no
  hit-stop in any of the three (backgrounds stay locked); the weight is carried by flash, bloom and a held peak. Shake in uncaptured
  moments cannot be ruled out.

## Re-scored Motion (and corrections)
| Reference | Motion was | Motion now | Basis | S / V / Read / Wordless corrections |
|---|---|---|---|---|
| Cyberpunk 2077 | 7 | **9** | footage-verified (quickhack, camera hack) | none: UI-over-world is text-heavy, Read 5 and Wordless 4 confirmed; V 9 confirmed |
| Mini Metro | 8 | 8 | footage-verified (trailer animation + 4 s real) | none |
| Google Maps 3D | 8 | 8 | **knowledge** (not on Steam) | none |
| Bad North | 8 | **7** | footage-verified | impacts are unreadable at island scale (units tiny, no punch); approach wakes and fire glow are strong. S 8, V 8, Read 8, Wordless 9 stand |
| Frozen Synapse | 7 | 7 | footage-verified (impact flare, replay) | none |
| Into the Breach | 6 | 6 | footage-verified | Read 9 confirmed (orange tiles + dotted arc); motion is crisp but plain: hard snaps, no eases, no shake |
| Frostpunk | 6 | 6 | footage-verified (trailer is mostly cinematic camera and event-card cuts) | none |
| Invisible, Inc. | 5 | **6** | footage-verified (in-game grid reveal; the CGI overlay is not counted) | none |
| Watch Dogs 2 | 7 | **6** | footage-verified for stings and the camera-feed switch; in-game overlay not captured | stings have an 8-level motion language, but the one in-game mode switch is slow (below); S/V/Read/Wordless unchanged |

## Updated bar
| Axis | Bar | Held by |
|---|---|---|
| S | 8 | Frostpunk, Bad North (stills + trailer) |
| V | 9 | Cyberpunk 2077, Google (knowledge), Frostpunk |
| Readability | 9 | Into the Breach, Mini Metro |
| **Motion** | **9** | **Cyberpunk 2077 quickhack overlay (footage-verified)** |
| Wordlessness | 9 | Mini Metro, Bad North |

Beating Motion therefore means 9 or 10 on the CP2077 standard: fast in, faster out, held impact, one telegraph that waits.

## Moments studied (strips in ref_motion/)
Frame counts are at 30 fps, relative to the first visible change.

**1. Mode switch into an overlay**
- `cp2077_quickhack_enter_2f`, `cp2077_camera_hack_mode_6f`: the world is already graded (green, or dark red with red scan lines for the
  camera hack) before the panel arrives. Target marker pops at +2f, header meter and panel at +4f, full list readable by +6-8f (about
  0.25 s). The grade is the mode change; UI is secondary and staggered in under 10 frames. Reduce-motion: keep the grade as a cross-fade,
  drop the stagger.
- `cp2077_quickhack_exit_1f`, `cp2077_quickhack_exit_to_effect_3f`: the exit is faster than the entry. Panels gone by +3f, green grade
  lifted by about +5f, then a rainbow chromatic fringe and one purple scanline glitch for 6-8f before the effect fires. Asymmetric: in
  about 8f, out about 3f. Reduce-motion: remove the fringe and scanline, keep the instant UI drop.
- `wd2_camera_feed_modeswitch_8f`: static noise, black within 8f, image fades up over 24-40f (about 1 s), then a tag slides in. Too slow;
  beat it.
- `invisible_hack_overlay_open_8f` (CGI): the building flips from lit to wireframe in about 16f, the floor grid grows over about 24f, the
  "FIREWALL Detected" tag types in over about 12f (glitch letters) then holds. Slower and more cinematic than CP2077; the reference for the
  one-time first jack-in only.
- `invisible_grid_reveal_8f` (in-game): lines draw over 10-12f, red zones pop in at +12f, blue pillar markers rise in about 12f.

**2. Intent telegraph**
- `itb_threat_tiles_telegraph_6f`, `itb_arc_preview_and_resolve_5f`, `hold_itb_arc_preview`: orange threat tiles snap on in 1-2f (no ease),
  a yellow dotted arc draws source to target over 6-12f and then stays on screen for the whole turn. Meaning without text: tile colour,
  arc and target reticle. The telegraph is persistent, not animated.
- `cp2077_contagion_telegraph_to_burst_4f`: a small red marker sits on the target and waits about 40f (1.3 s) with almost no motion, then
  the burst fires in 1f. Anticipation is a long still hold, not a wind-up animation.
- Reduce-motion: both are already static; keep as is.

**3. Travel**
- `itb_projectile_splash_6f`: acid arc, about 18f travel then a 12f splash that spreads.
- `itb_enemy_attack_hit_6f`: a pink line extends source to target in about 6f before the hit.
- `badnorth_longships_approach_12f`: longships arrive slowly (seconds) with white wake trails; the silhouette is the cue, not speed.
- CP2077 hacks have no travel: instant, which is why the telegraph hold matters.

**4. Impact + hold**
- `cp2077_hack_burst_1f` (1-frame spacing): f0 nothing, f1 spark on target, f2-3 electric arcs, f4-7 white-hot bloom growing, peak f5-7, still
  bright at f11+. No shake, no camera move.
- `itb_hit_impact_1f` (1-frame): f0-2 blood spatter, f3 first white flash frame, f4-7 white/orange burst, peak f6-7, f8-11 decays to
  embers. About 12f total, no shake. Damage numbers stay on screen afterwards.
- `frozensynapse_impact_flare_2f` (2-frame): radial starburst rises to peak over about 6f, held about 6f, fades over about 8f (about 20f
  total), soft bloom and a background dim; additive white; no shake.
- Reduce-motion: replace travel with a cut to the held peak; keep the flash as a single 2-3f brightness step (no flicker) at a capped
  luminance.

**5. Hit on a base / loss**
- `itb_base_damage_6f`: red "POWER LOST" tags pop in on the damaged buildings, tiles darken, a portrait with a dialogue plate arrives about
  6f later and holds. State change shown in place, no shake.
- `frostpunk_event_cut_10f`: city view hard-cuts (smoke-wipe vignette) to the event card in about 10f; the card then holds.
- `badnorth_raid_fire_12f`: loss as a growing flame glow over several seconds; no sharp impact.
- Reduce-motion: static state swap plus the in-place tag; drop the wipe.

**6. Area takeover / spread**
- `wd2_ctos_citymap_reveal_6f`, `hold_wd2_ctos_citymap_labels` (sting, not in-game): static to city blocks over 6f; cyan street lines draw
  on over about 18f in three steps of about 6f; labels pop in one by one about every 6f with a scale pop, then settle. The spread is
  staggered so the eye follows it.
- `itb_projectile_splash_6f`: acid splashes spread over about 12f.
- `minimetro_ring_and_line_build_10f`, `minimetro_train_glide_8f`: a ring pops from blur to sharp in about 10f; a line extrudes from the
  ring over about 10f with a short end cap; trains glide at constant speed.

**7. Reveal / poster slam**
- `cp2077_quickhack_upload_glitch_4f`: the target dissolves into red pixel blocks over about 12f while a column of green light holds above.
- `wd2_dedsec_takeover_slam_12f`, `wd2_marcus_glitch_transition_6f`: hard 3-6f cuts, pixel-block dissolves of 8-12f, then a sticker pops in
  with a jitter overshoot (about 6f) and holds 24-36f. Reads as a poster being slapped on. Reduce-motion: keep the hold frame, drop the
  block dissolve and jitter.

**8. Hover / selection / placement**
- `cp2077_quickhack_hover_queue_4f`: the selection outline jumps between list items in 1 frame (no tween); the description panel text swaps
  within about 4f.
- `itb_deploy_6f`: ring flash (6f), the unit appears about 6f later, tooltip pops in about 6f; about 18f total for a placement.
- ITB range tiles snap green in 1 frame on hover.

## Timing cheat-sheet (30 fps; storyboards must beat or borrow)
| Beat | Reference number (footage) | Borrow / beat |
|---|---|---|
| Jack-in mode switch | CP2077: the grade is the switch, UI stagger in 4-8f (0.13-0.27 s); exit 3f UI drop plus 6-8f chromatic/scanline fringe; WD2 camera feed fade 24-40f (too slow) | Enter: world grade ease-out over 8-10f, marker +2f, panel +4f, list stagger 2f apart, done by 12f. Exit faster: 3-4f UI drop, 6f un-grade. Asymmetric. The first-ever jack-in may take up to about 24f (Invisible CGI) once |
| Telegraph | ITB orange tiles snap in 1-2f, arc draws 6-12f, persists all turn; CP2077 marker waits about 40f then fires | Draw source to target over 10-12f ease-out, then keep it on screen; hold the marked target 30-40f before any resolve so the player can read it. Never hide it behind hover |
| Travel | ITB laser 6f, acid arc about 18f; Bad North longships seconds | Beam head 12-18f per street segment with a trailing wake; skip travel for hacks |
| Impact + hold | CP2077: spark f1, bloom peak f5-7, held 11f+; ITB: white flash f3, peak f6-7, about 12f total; Frozen Synapse about 20f flare | Flash frame f0-1 (white, brightest), peak f4-7, HOLD 6-8f at the peak, decay 8-12f, then an aftermath hold of 20-30f with the damage state in place. No reference uses shake or hit-stop, so nobody has a bar here: if we shake, 2-3 px for about 4f at the HOME hit only, and reduce-motion removes it |
| Base hit | ITB in-place "POWER LOST" tags, portrait +6f; Frostpunk event card in about 10f; Bad North fire over seconds | Hit flash 1-2f plus HOME state swap in place within 6f; a persistent damage mark that needs no text; loss escalation (fire/crack) over seconds, not frames |
| Spread (Bloom, takeover) | WD2 sting: line draw about 18f in 3 x 6f steps, labels staggered 6f; Mini Metro line extrusion about 10f | Stagger new cells every 4-6f along the front in distance order; each cell pops (scale 0.8 to 1.0, 6f ease-out) |
| Reveal (sealed / hunter) | CP2077 pixel dissolve about 12f; WD2 sticker pop about 6f overshoot then hold 24-36f | Dissolve 8-12f, then a jitter-overshoot pop of 6f and a hold of at least 24f for the poster read |
| Hover / selection | CP2077 outline jumps in 1f, panel text swaps in about 4f; ITB tiles snap in 1f | Hard snap (1-2f) for selection; give the response disc hover a 4-6f ease so it reads as a preview, not a commit |
| Placement | ITB: ring flash 6f, unit +6f, tooltip +6f (about 18f) | Card drops into the Site in about 12f with a 4f settle and a ring flash on landing |

Reduce-motion rules the footage implies: (1) keep the mode-change grade as a 6-8f cross-fade; (2) replace travel and spread with a state
cut plus the held peak; (3) flashes become one 2-3f brightness step below a luminance cap; (4) drop chromatic fringe, scanline glitch,
shake and jitter overshoot; (5) keep every hold (telegraph wait, impact peak, aftermath), because the holds carry the meaning.

## Note on the earlier prose
The per-reference notes above were written before the footage; where they conflict with this section on Motion, this section wins:
Cyberpunk's motion strength is the quickhack overlay (not the scanner clutter), Bad North's impacts are weak at island scale, and the
Watch Dogs 2 overlay motion could not be verified in-game.
