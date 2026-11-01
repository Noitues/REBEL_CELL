# E10 combat screen: element-by-element design brief (art director)

Date: 2026-10-31. Branch art-pass, documentation only. Solace vertical slice, art only.

**Source of truth:** approved plate E10 `D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png` (plus p2_preview, p2b_hover, p3_resolve, p1_nowords); generator `D:/rc_scratch/combat_polish/E7_waves/E10/src/build10.py` + `e10lib.py` (+ e9lib, e8lib, cv_over, cv_board, cv_chrome, cv_lib); sim state `state_e10.json`; rules `D:/rc_tmp/combat_concepts/D4_E10/rules.md`; ART_BIBLE 2, 3.1, 3.22; `docs/concepts/ART_BIBLE_AMENDMENTS_DRAFT.md`; cutaway backdrop `docs/concepts/combat_backdrop/v2/NOTES.md`; golden plates `docs/concepts/golden_plates/street_overview.png`, `hq_rebel_cell_overview.png`.

**Designer rulings this brief serves:** E10 "as a whole meets the visuals we want", but the micro details and sub-elements need real design (amendments draft, open items). Process ruling 2026-10-31: every element gets a design goal and look, options, iteration to a settled look, with the art director pruning and deciding and keeping the whole view cohesive.

## 1. How to use this brief

- Each element below has: **design goal** (what the player must read, in order, and how fast), **look and feel** (the target in words a designer can act on), **current problems** (minute level, as seen in E10), and a crop in `brief_crops/` (`<cluster>__<id>.png`, cut from the plate named in the Src column; contact sheets `brief_crops/contact_<cluster>.jpg`).
- Elements marked **LATENT** are drawn by the generator but not visible in this sim state (no crop). They are part of the screen vocabulary and must be designed with their family so a later state does not break the look.
- Hard limits: game content is fixed (state, numbers, counts, words); judge on room_bio_bare at 1920x1080; never overwrite the approved plates or E10 source; never run `python -`.
- Re-run `python brief_crops/make_crops.py` then `python brief_crops/build_brief.py` after editing `brief_crops/inventory.json`; the build fails loudly if an element loses its crop or a source draw call loses its element.

## 2. Cluster moves (from the task's starting list)

Keys are fixed; these elements were moved so each object is designed in one place:
- **HOLD NEXT / HOLD THEN zones**: wave_rings -> **outer_rings** (they are cells of the one schedule bezel with `+2 THIS TURN`).
- **Landing arcs** (frame, kind disc, wear, now dot, turn dots, chevrons, diamonds, check, soak/brace, twist mark): **outer_rings** as one object (the task split them between wave_rings and outer_rings).
- **Soak and clamp marks**: the slice versions (Brace plate, slice soak marks) go to **wheel_core**; the arc versions stay with the landing arc in outer_rings.
- **Gun tracers, nudge ghost**: **wheel_core** (they come from the tower). **Ward arc, consumed-unit state**: wave_rings.
- **Option chips, chain strip, plan underline, BEST LINE, WITHOUT TWIST, TRIG groups**: **top_hud** (they are states of the bill). **RAM refund pop**: objectives. **Trigger path, twist badge, refund burst, hover tag/path/dim, resolve fire lines**: **actions** (plan / preview affordances).


## 3. Cohesion bible (every designer follows this; the whole E10 read stays)

### 3.1 What E10 already does well (keep, do not redesign away)
- **One board.** Tower in the centre, three wave rings, the schedule bezel, landing arcs outside; the right column is the bill; the hand bottom right. The layout is locked (3.1, 3.22).
- **Depth four ways** (position, lane outline, token base, NOW / +1 / +2 words). Keep all four.
- **Threat grammar:** red chevrons pointing at the tower = hit; red diamonds = HP that gets through; solid = now, hollow = growth to come. This is the strongest idea on the screen.
- **Counts are tallies** (groups of 5), digits only in the hero `lands -> through` pair, tags and the hover tag.
- **Ink keylines** under every coloured mark give the print/sticker feel that ties the board to the stickers and cards.
- **Media split** (1.2): CRT terminal plates for data, vinyl stickers for identity and the verb, grease pencil only for the player's plan.
- **Muted mauve unit screens** so the red pops (PL10). Keep the value relationship even where pink is now allowed case by case (amendments draft, Part 3.1).
- **One warm mass:** the live schedule cell is the one big orange shape; the board reads first at 320 px.

### 3.2 Value hierarchy (squint order at 320 px, on room_bio_bare)
1. **L1 threat:** red chevrons, red diamonds, the solid threat trim, the hero THROUGH digit. Highest saturation x contrast on screen.
2. **L2 board structure:** the live schedule cell, slice icons, unit tokens, the Adjuster. One step below L1. The live schedule cell must not outweigh L1 (today it does).
3. **L3 HUD data:** bill tallies, RAM / Trace pips, card art bands, SEND IT (SEND IT is L2 by size but sits away from the board).
4. **L4 containers and engraving:** panel frames, gutters, empty cells, labels, ticks, future wave arcs.
5. **L5 backdrop:** the cutaway room is the lit second mass (value up to x0.84 in its focus hull per the cutaway NOTES); the city around it is texture. Nothing on the board may sit at L5 value, and the room may never exceed L2.
- Rule of thumb: a mark's value tier is set by what the player must read first, never by how new it is.

### 3.3 Colour tokens (hex) and their one meaning
| Token | Hex | Meaning on this screen | Never |
|---|---|---|---|
| `HARM` | #FF4433 | Damage that will happen: chevrons, diamonds, threat trim (now), lost-this-turn slashes, THROUGH digit, NOW lane | decoration, Trace, card cost |
| `PENCIL_THREAT` | #FF1C2C | Grease pencil threat (Trigger hit reaching the tower) | non-pencil marks |
| `GAIN` | #7BE07B | Player HP left, slice HP left, enemy shot dead (X), nothing through (check) | Worm wear, route icons, Solace identity |
| `NET_CYAN` | #5CE1FF | Ours / the tower: code-base frame, terminal edges, RAM, SHOT, ABSORBED, gun tracers, TOWER card family | enemy elements |
| `PENCIL_PLAN` | #FFE200 | The player's plan only: pencil paths, hover path and tag edge, plan underline, twist badge, selected option, BEST LINE, TRIG group | SEND IT fill, help button, card cost, hazard ticks |
| Vinyl yellow | #FFEE60 -> #FFB60E | SEND IT sticker material (gradient, 2.10) | flat fills |
| `SCHEDULE_ORANGE` (`RING_AVAILABLE`) | #FF8C1A | The wave schedule: bezel cells, WAVES LEFT, future normal waves, WAVE card family | soak, heat, corp identity |
| `SOAK` | **#6A6CFF indigo** (R1 ruling; was #FF9628) | Slice takes pips instead of HP; always with the chevron notch / funnel shape | orange; any fill of LANE_PLUS1 |
| `CRT_AMBER` / `WARN` | #FFB000 | Heat consequence (ENDS = HEAT), caution | boss, reward |
| `BOSS_GOLD` | #FFC428 | The Adjuster: body, cell edge, ward arc, warded mark, its HP progress | refund, generic reward |
| Reward gold | #FFD24D (`RESIST_GOLD`) | Stars met (with the star shape only) | boss marks |
| `CREAM` | #FFF4D6 | Enemy HP segments | Brace (player's), boss HP if the boss gets its own colour |
| `LANE_PLUS1` | #78AAFF | Ring +1 outline, next-turn threat trim | Trace |
| `LANE_PLUS2` | #ECF0FF dashed | Ring +2 outline, later threat trim | turn dots, HP |
| `RIDER_LAV` | #BEA0FF | Rider (Adjuster turn rider) | Trace |
| `TRACE_VIOLET` | #A03CFF | Trace pips and anything that adds Trace (card loud tab) | rider, Jammer |
| Unit mauve | #7C4068 Packet, #6A4482 Worm, #5E568A Jammer, #76446A Payload (washes) | Unit screens only | HUD |
| `STEEL` / `STEEL_HI` | #96A2B6 / #E2E9F6 | Armor | lane outlines |
| `INK` | #0C0A16 | Keylines, glyph outlines | |
| `TERMINAL_BG` | #050D1C at 93 percent | CRT plates | |
| `TEXT_HI` / `TEXT_MID` / `TEXT_LO` | #F2F6FF / #AFC0D6 / #7A889C | Text on dark | |
| `SCRIM` | #02030A at 55 percent + 6 px blur | Under the board and HUD over the room | |

Rules: every colour pairs with a shape, glyph or word (5.1). A corp hue never takes a UI role (2.4); Solace lime #96FF46 sits next to GAIN, so Solace shows on this screen by **material and crest only** (bezel, ring cells), never as lime fill. Pink: allowed case by case (amendments draft), but never on a mark that must read as threat or as ours.

### 3.4 Type ladder (1080p px)
| Role | Face | Sizes | Notes |
|---|---|---|---|
| Verb sticker | Anton, ink keyline 5 px | 62 (SEND IT) | die-cut border 0.14 x size, max 12 px |
| Hero digits | Anton, keyline 3-5 px | 58 | the only raw number on the board/HUD besides tags |
| Display L | Anton | 30-34 | header turn number, nameplate, cost digit |
| Display M | Anton | 22-28 | card titles, sector digits, operators |
| Tag | Anton with keyline | 17-20 | ring tags only; raise toward 20 where space allows |
| Terminal | Share Tech Mono caps +8 percent | 18 floor, 22 for rows that lead | HUD labels are 16 today: raise to 18 (2.9 floor) |
| Rail / bezel arc text | Share Tech Mono | >= 16 (3.22 rail rule) | flip on the lower half |
| Body / tooltip | IBM Plex Sans Condensed Regular + Medium | 20 (hover tag; 18 today) | keywords Medium in their colour, 36-60 chars a line |
| Card rules (resting) | Plex Sans Condensed | 16 (= 10.7 at 720p, inside the resting-card exception) | grown card keeps the 12 px 720p floor |

### 3.5 Stroke and ink ladder
| Tier | Width | Use |
|---|---|---|
| Hairline | 1.2-1.6 px | engraving: bezel ticks, segment outlines |
| Fine | 2-2.6 px | containers: terminal edges, tags, chips, token rings |
| Medium | 3-4 px | identity borders: lane outlines (now 4, +1 / +2 3), boss cell edge |
| Bold | 5.5-8 px | action and threat: threat trim, chevrons (6 on 10.5 ink), grease pencil 7 + ink |
- Ink keyline = coloured stroke + about 4.5 px (each side about 2.25), colour INK. Every coloured mark on the board has one; text on plates does not.
- A tier means something: a container never uses the bold tier, a threat mark never uses hairline.

### 3.6 Corner and bevel language
- HUD (rectilinear): radius ladder 3 (pips, segments) / 6 (tags, chips) / 8 (terminal plates) / 16 (cards, stickers outer). One panel style for every HUD plate (today there are three: cyan terminal, white bill box, grey objectives).
- Board (polar): arc bands with a fixed inset (4 px radial, 3 deg angular) for every cell, unit or empty; no rounded rectangles on the board except tags; slices keep family-C rounded wedges.
- Shapes carry meaning: circle = identity token or count dot; square/rounded segment = HP or resource pip; diamond = HP through (red) or boss (gold), so no unit glyph may be a diamond; chevron = hit; X = removed (green = enemy dies, red = our slice breaks).
- Bevel: none on HUD (flat CRT glass with scanlines). Board materials (bezel, cells) may carry one soft inner bevel, light from the top-left, matching the cutaway's fixed light (-0.5, -0.3, 0.81).

### 3.7 Glow and bloom
- Default: no glow. Allowed emissive marks: the solid threat trim (now) and the live schedule cell, soft bloom 4-6 px at up to 35 percent; the hover / plan pencil gets no glow (wax, not neon).
- Dark ink halos (pools) under tokens and the boss are allowed (they are shadow, not glow) at up to 75 percent, blur 4.
- No glow on text, tallies or HUD plates. The board never blooms more than the backdrop's brightest neon.

### 3.8 Icon grid and style
- Bible 3.5 glyph set (round 17 package): white silhouette, ink outline 7.5 percent of size, 512 grid, 2-3 parts, no interior detail under 2 px at use size.
- Sizes: 70 card art, 44 slice, 37 unit token, 28 arc disc, 24 boss skull, 20 chips and options; nothing below 16 (5.2): today's 13 px wave-arc glyphs fail.
- No media-player shapes (play, pause, skip): the Packet, HOLD and needle all read as media buttons today.
- No letter-like glyphs (Worm reads as "M").
- One meaning per silhouette: today the shield is used for the SHIELD slice, the warded mark and (nearly) the Brace glyph; the diamond for Payload, HP-through and the boss.

### 3.9 Process rules for every option
- Render on `docs/concepts/combat_backdrop/v2/room_bio_bare.png` (room framed at screen 1500, 612) at 1920x1080; never on the old crane backdrop.
- Content is fixed: state_e10.json, every count, number and word stays; design changes how, never what. Draw asserts (assert_draw_log) must still pass for anything that is counted.
- Check each option in context (full plate), at 320 px squint, deutan, and the nowords variant (`actions__nowords_variant.png` shows the HUD with words stripped: every element must still read by shape).
- Work on copies of src/; never overwrite the approved plates or E10 source.

### 3.10 Do-nots
1. Do not add a colour token; reuse 3.3, or bring a token change to the art director with a reason.
2. Do not let any orange other than the schedule fill an area larger than a chip.
3. Do not put plan yellow on anything that is not the player's plan.
4. Do not put an X, slash or badge over an icon it describes; place states beside or around.
5. Do not stack more than two parallel arcs within 12 px (today up to six).
6. Do not add digits to the board (tallies only), except the existing tags and hero pair.
7. Do not use a corp hue (Solace lime, Meridian orange) for a UI role; Meridian art is hibernated.
8. Do not draw nudge buttons on the ring wheel (3.22 Open).
9. Do not use media shapes or letters as glyphs.
10. Do not add glow to fix a weak read; fix value and size first.
11. Do not let the board's outer arcs touch the screen edge (keep a 24 px margin) or let stickers crop at the frame.

### 3.11 Round 1 rulings (art director, 2026-11-01; these override any cluster favourite; detail in REVIEW_R1.md section 1)
1. **Shape per resource:** RAM = cyan coin (disc + inner ring hairline): RAM pips 24, card cost 34 with an INK digit, refund token = coin + plus. Trace = violet square r3 (incl. the card loud tab). Heat = amber flame. No other mark uses these three silhouettes (the Firewall card glyph is a brick wall only).
2. **SOAK = #6A6CFF + chevron notch** on every soak mark (slice, arc, split row, plan glyph). LANE_PLUS1 is outline/trim only. Deutan and tritan check required.
3. **Brace = NET_CYAN + the clamp-plate silhouette** everywhere. Cream = enemy HP only. **Boss HP = BOSS_GOLD** on board and HUD.
4. **Bezel = Solace teal enamel.** No orange rim glow.
5. **One glyph master library** (seeded from card_icon_set A): Spin = arrow ring cut into N; Breaker crest = cracked ring (hub, nameplate, nowords); Jammer = relay pylon with broken arcs; Ring unit = chain links; HOLD = hourglass (card, bezel cells, plan glyphs); Twist = open circular arrow; Packet = cube; Payload = bomb; Worm = one-bend hook with head and eye. The pause glyph and the ring-with-bar are retired. Burst and turret bullets tilt 35 deg (never read as pause); repair = one strip (never an X); the needle is never a symmetric rhombus.
6. **HP grammar** (slice bars, unit rows, HP ring, YOU tally, arc wear): rounded segment r3; lost now = HARM + white slash + ink; lost to soak = SOAK + notch; mend = GAIN outline + plus; gone = dark socket + solid 1.4 px hairline. Empty sockets in the HUD use the gone pip.
7. **Dashed = later/growth only** (+2 lane, hollow chevrons, +2 trim, ghosts, the played liner's empty slot); cyan dash = gun tracer.
8. **No code text on any board screen;** one 3 px phosphor mesh shared by slice screens and unit CRT bowls.
9. **One continuous 8 px INK spoke** per sector boundary from the hub to the bezel.
10. **Ground:** one grade (room hull sharp, city 2 px blur and x0.85) + frosted board pool + two HUD slabs. The room focus hull never blurs.
11. **One terminal kit** on every HUD plate (incl. UNDO and the hover tag); **one sticker material** on SEND IT, nameplate and cards; one shadow (4,8) blur 8 k 0.5, grown card (8,16) blur 14.
12. **Type:** labels mono 18 (22 for a leading row); Anton only for the header, hero pair, titles, sector digits, tags and stickers.
13. **Content guard:** no option may drop or move a number, word or angle the state shows (the xN digit, NO TARGET words and true wave angles stay; no new tallies). Wordless forms live in nowords only.
14. **HUD height budget:** column x1072..1896, 8 px gaps, p1 bottom <= y 384, p2/p3 within +12 px of E10.
15. **Focus = lime corner brackets** (2.10), one drawing used on every focusable element.
16. **Plan yellow audit:** the hero arrow and option pair arrow go neutral TEXT_HI; the help button goes white; the trig_lands tally goes HARM (a tally is not pencil).

## 4. Element inventory (183 elements, 22 of them LATENT; R1 review: +17 / -1, see section 8)

### 4.1 Wheel core (`wheel_core`, 39 elements)

Contact sheet: `brief_crops/contact_wheel_core.jpg`

#### `hub_disc`: Hub core disc and rim
- Crop: [wheel_core__hub_disc.png](brief_crops/wheel_core__hub_disc.png) (from p1)
- **Design goal:** Read 1) this is the player's tower centre, 2) whose class it is (Breaker). Under 0.3 s, by position alone; it must never compete with the slices or threat marks.
- **Look and feel:** A quiet dark lens: near-black CRT glass with a single cyan rim at medium weight, a faint inner bevel and no fill gradient. It is the still eye of the board, one value step darker than the slices.
- **Current problems:** Rim is the same weight and cyan as the code-base frame ring 100 px out, so the two rings blur into one cyan system; disc fill is flat with no material; at 320 px squint the hub vanishes into the gutters; the gap between hub rim and slice tips is uneven (slice wedges touch on some sides, 3 px gap on others).

#### `hub_inner_rings`: Hub inner concentric rings (lens material)
- Crop: [wheel_core__hub_inner_rings.png](brief_crops/wheel_core__hub_inner_rings.png) (from p1)
- **Design goal:** Give the hub lens a glass material so it reads as an object, not a hole; carries no information.
- **Look and feel:** Either one deliberate inner bevel ring (hairline, one value step above the fill, light from the top-left per 3.6) or nothing; never a ring stack that reads as a target or a dial.
- **Current problems:** draw_hub paints faint white rings at alpha 10 every 9 px from r 16 to r 36: invisible at 1080p and at 320 px, so the hub still reads flat; if raised as-is, five concentric rings would read as a bullseye under the BREAKER word and the emblem.

#### `hub_label`: Hub class word (BREAKER)
- Crop: [wheel_core__hub_label.png](brief_crops/wheel_core__hub_label.png) (from p1)
- **Design goal:** Confirm class identity once; secondary to the CELL-9 nameplate that says the same thing. Readable but never the first thing seen.
- **Look and feel:** Anton in white with an ink keyline, sized to sit inside the lens with clear margin; or demoted to a class emblem only, with the word moved to the nameplate.
- **Current problems:** Word duplicates the nameplate (CELL-9 // BREAKER); Anton at ~22 px with no keyline and pixel-stepped edges; text is centred low and crowds the lower rim; the nowords plate leaves an empty hub, which shows the label is carrying the identity instead of an emblem.

#### `hub_emblem`: Hub class emblem (Breaker pick tick)
- Crop: [wheel_core__hub_emblem.png](brief_crops/wheel_core__hub_emblem.png) (from p1)
- **Design goal:** Carry class identity without words; read as an emblem, not as a needle or pointer.
- **Look and feel:** A proper Breaker class emblem from the class glyph set, centred, in the class accent at reduced value, inset like an engraving.
- **Current problems:** Reads as a stray cyan pointer at 1 o'clock, which suggests a dial needle and conflicts with the real needle at sector 0; it is aliased (stair-stepped) and sits off-centre above the word; thin stroke below the 16 px glyph rule.

#### `slice_frame`: Slice tile frame (wedge outline)
- Crop: [wheel_core__slice_frame.png](brief_crops/wheel_core__slice_frame.png) (from p1)
- **Design goal:** Separate the six tower slices and tell their TYPE by colour plus icon (bible 2.3: green repair, pink attack, cyan shield). Read the 6-way division in under 0.2 s.
- **Look and feel:** Family-C CRT screen wedge: rounded inner and outer corners, a thin type-colour edge at fine weight with an ink line outside it, consistent inset from neighbours.
- **Current problems:** Edge colours are hard to tell apart (shield teal, turret magenta, burst pink, repair lime-green all at the same thin weight); outline weight varies by slice as the texture bleeds into it; corner radii are uneven between the hub side and the rim side; the frame line is thinner than the HP bar inside it, so the bars read as the frame.

#### `slice_screen`: Slice programme screen texture
- Crop: [wheel_core__slice_screen.png](brief_crops/wheel_core__slice_screen.png) (from p1)
- **Design goal:** Give each slice material and life (CRT programme screen) without carrying any information. Must stay a backdrop to the icon.
- **Look and feel:** Low-contrast CRT texture in the type colour, scanlines and soft code text, value capped below the icon and below the red threat marks; one consistent treatment across all six.
- **Current problems:** BURST slices carry a loud rainbow chromatic halo, the most saturated thing in the wheel, competing with red threat and reading as a non-existent status effect; texture contrast varies wildly between slice types (bright green waterfall on REPAIR, dark pink hex on TURRET, flat teal grid on SHIELD). Readable code text is a separate element (slice_screen_code_text).

#### `slice_screen_code_text`: Readable code and hex text in slice screens
- Crop: [wheel_core__slice_screen_code_text.png](brief_crops/wheel_core__slice_screen_code_text.png) (from nw)
- **Design goal:** None; texture only. The slice screen may suggest code, but no legible word or digit may appear on the board (no-words / tallies-only rule).
- **Look and feel:** Glyph noise below legibility: sub-8 px pseudo-characters or blurred columns under 10 percent contrast, the same density in all six slices; nothing that survives as a word in p1_nowords.
- **Current problems:** Legible strings in the REPAIR waterfall ('goto fail', 'return 0', 'head') and hex columns in the TURRET screen survive in p1_nowords; they are the only words left on the nowords board and they sit right under the slice icons, adding texture contrast exactly where the icon needs a quiet ground.

#### `slice_gutters`: Slice gutters and spokes
- Crop: [wheel_core__slice_gutters.png](brief_crops/wheel_core__slice_gutters.png) (from p1)
- **Design goal:** Show the sector boundaries that line up with ring sectors outward (one radial strip per sector).
- **Look and feel:** Even ink-black gutters, the same width as the ring gutters, so the 6 radial strips read continuously from hub to bezel.
- **Current problems:** Slice gutters are visibly narrower than the ring gutters, so the radial strip breaks at the HP ring; gutter ends meet the hub at different depths; the sector line does not continue through the HP ring or the code-base frame.

#### `icon_burst`: BURST slice icon
- Crop: [wheel_core__icon_burst.png](brief_crops/wheel_core__icon_burst.png) (from p1)
- **Design goal:** Read 'two-shot gun' (BURST) at a glance; identical silhouette on both BURST slices.
- **Look and feel:** Bible 3.5 glyph: white silhouette, ink keyline at 7.5 percent, about 44 px, centred on the slice's visual centre, no glow.
- **Current problems:** Starburst with a hole reads as 'explosion / damage taken' more than 'burst fire'; sits on the rainbow halo so its edge loses contrast; slightly off the wedge centroid (pushed toward the hub).

#### `icon_shield`: SHIELD slice icon
- Crop: [wheel_core__icon_shield.png](brief_crops/wheel_core__icon_shield.png) (from p1)
- **Design goal:** Read 'this slice blocks 2' at a glance (PL10 ask 4).
- **Look and feel:** Half-filled heater shield in white with ink keyline, same size and baseline rule as the other slice icons.
- **Current problems:** Half-black fill reads as 'half broken' when the slice is intact; same shield shape as the gold warded mark and the cream Brace glyph, so three different meanings share one silhouette; when the slice breaks the red X lands on top of the icon and hides it.

#### `icon_turret`: TURRET slice icon (sword)
- Crop: [wheel_core__icon_turret.png](brief_crops/wheel_core__icon_turret.png) (from p1)
- **Design goal:** Read 'single-shot gun' (TURRET).
- **Look and feel:** A gun/turret glyph from the set that reads as ranged fire, same size and weight as the other icons.
- **Current problems:** A sword reads as melee attack, not a turret shot; it is visibly thinner and smaller than the other icons and tilted, so it looks weaker; the red X is drawn over it.

#### `icon_repair`: REPAIR slice icon (bandage)
- Crop: [wheel_core__icon_repair.png](brief_crops/wheel_core__icon_repair.png) (from p1)
- **Design goal:** Read 'mends 1 slice pip per turn'.
- **Look and feel:** Crossed bandage glyph in white with keyline; consistent size and centring.
- **Current problems:** Bandage detail (pad square) fills in at 320 px; the bright green code-waterfall texture under it fights the icon; slightly larger than the burst icon.

#### `slice_hp_bars`: Slice HP bar set (2 capsules per slice, five pip states)
- Crop: [wheel_core__slice_hp_bars.png](brief_crops/wheel_core__slice_hp_bars.png) (from p1)
- **Design goal:** Read intact / cracked / broken and which pips change THIS turn, under 0.5 s per slice. The bar owns geometry and the five pip states as one designed set: lit, lost to harm, lost to soak, mend pending, gone.
- **Look and feel:** Thin floating capsules at the outer edge, equal length and gaps on all six slices, one end cap shape, ink under each; the five states differ by shape first (solid / slashed / soak-marked / outlined-plus / empty socket) and colour second.
- **Current problems:** Capsules (r 132), threat trim (r 142) and HP ring (r 147-157) make three parallel green/red/salmon arcs within 25 px that merge; capsule ends inconsistent; bar length differs per slice; the code draws five pip states but they were never designed together, so one bar can show salmon and orange lost pips side by side (SHIELD sector 1, p2). State-specific problems sit in slice_pip_lost_harm, slice_pip_lost_soak, slice_pip_mend and slice_pip_gone.

#### `slice_pip_lost_harm`: Slice pip lost to harm this turn (salmon + slash)
- Crop: [wheel_core__slice_pip_lost_harm.png](brief_crops/wheel_core__slice_pip_lost_harm.png) (from p1)
- **Design goal:** Read 'this pip is lost at END TURN to enemy hits' on a slice, in the same family as the HP ring's and YOU tally's lost marks.
- **Look and feel:** HARM red capsule with a clear white slash (Fine tier, ink under), or a hollowed capsule with a red slash; the same lost grammar as hp_ring and you_hp_tally.
- **Current problems:** Salmon #FF968C with a 2 px white slash: the slash vanishes at 320 px and salmon sits next to the red threat trim at r 142, so the lost pip reads as part of the trim; it does not match the hp_ring lost red, so slice loss and player HP loss look like two different things.

#### `slice_pip_lost_soak`: Slice pip lost to SOAK (orange capsule, p2)
- Crop: [wheel_core__slice_pip_lost_soak.png](brief_crops/wheel_core__slice_pip_lost_soak.png) (from p2)
- **Design goal:** Read 'this slice pip pays for overflow instead of your HP' (the player's choice), distinct from a pip lost to harm in the same bar.
- **Look and feel:** The new soak token (hue and shape clear of schedule orange, open call 1) applied to the capsule: for example a capsule with the soak mark notched in, never just a recoloured lost pip.
- **Current problems:** tower_slice_bars' by_soak branch paints the pip SOAK_C #FF9628, nearly schedule orange; with no slash it reads as a lit pip in the wrong colour or as part of the orange soak rim arc beside it; next to the salmon harm pip in the same bar the two lost states differ only by a small hue step.

#### `slice_pip_mend`: Slice pip mend pending (REPAIR heal preview) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read 'this pip comes back at END TURN' (REPAIR mends 1). The only GAIN-preview mark on the tower.
- **Look and feel:** GAIN-family capsule as an outline or ghost with a small plus, clearly a preview (not yet lit), in the same set as the lost states.
- **Current problems:** Not in this state (no slice regains a pip in f1/f2); code draws a pale green (170,240,170) capsule with a white 3/3 dash, nearly identical to a lit green pip at 320 px, and the white dash is the same mark as the harm slash, so mend and loss would share a shape.

#### `slice_pip_gone`: Slice pip already gone (empty socket) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read a pip lost in an earlier turn: socket empty, not a change this turn.
- **Look and feel:** Dark empty socket with a hairline outline, quieter than any this-turn state, same geometry as a lit capsule.
- **Current problems:** Not in this state (all slices at 2/2 before END TURN); code draws a dashed socket line that looks like the +2 dashed lane language and like the hp_ring gone segment only by chance.

#### `slice_break_x`: Slice breaks-this-turn X
- Crop: [wheel_core__slice_break_x.png](brief_crops/wheel_core__slice_break_x.png) (from p1)
- **Design goal:** Read 'this slice breaks at END TURN, its ability is lost' (sectors 1 and 2). Must be the strongest slice state.
- **Look and feel:** A heavy ink-keylined X in harm red placed off the icon (corner), plus a state treatment of the whole wedge (hatch or dim preview) per bible 3.22 BROKEN; red X never sits over the icon.
- **Current problems:** X is drawn over the icon and hides what will be lost; it is the same red and size as the gun-tracer impacts and the threat trim so it does not read as a state; no hatch/dim preview as the bible's BROKEN rule asks; the soaked variant (p2) turns the X orange, which collides with the schedule orange.

#### `threat_trim`: Threat trim on slices (now / next / later)
- Crop: [wheel_core__threat_trim.png](brief_crops/wheel_core__threat_trim.png) (from p1)
- **Design goal:** Read which slices get hit THIS turn (solid red), next turn (dashed pale blue) and in two turns (dashed white). The first thing the eye finds on the wheel.
- **Look and feel:** An LED arc on each slice's outer edge: solid harm red bold for now, dashed pale blue medium for next, dashed white fine for later; the only glowing element on the wheel.
- **Current problems:** The three trims sit at r 142 / 146 / 150, so the next-turn and later trims are drawn ON the HP ring (r 147-157) and merge with it and the slice bars into a five-line band; next-turn pale blue matches the +1 lane colour (good) but at 3 px dashed over green HP it disappears; trim length (50 deg) differs from the slice bar span (about 42 deg) so the ends misalign.

#### `hp_ring`: Player HP ring (rim ring segments)
- Crop: [wheel_core__hp_ring.png](brief_crops/wheel_core__hp_ring.png) (from p1)
- **Design goal:** Read the player's 15 HP around the tower and how many are lost this END TURN (6 red). Must agree with the YOU tally in the HUD.
- **Look and feel:** 15 equal segments in a socket ring: green lit, harm red with a fine white slash for lost-this-turn, dark for gone; segment gaps aligned so groups of 5 are visible.
- **Current problems:** No groups of 5 (the HUD tally uses groups, the ring does not), so the two HP displays do not match; the lost run always sits at the end of the ring (216-360 deg, over sectors 4-5) whatever slices are hit, so position on the ring suggests a sector meaning it does not have; red lost segments sit beside red threat trim and read as more threat; the ring is 10 px thick, thicker than the slice bars, so it reads as the wheel frame.

#### `codebase_frame`: Code-base frame rings (cyan)
- Crop: [wheel_core__codebase_frame.png](brief_crops/wheel_core__codebase_frame.png) (from p1)
- **Design goal:** Close the tower as one object and mark it as 'ours' (cyan, per 3.22).
- **Look and feel:** One fine cyan ring at the HP ring's outer edge, with an ink line; not two.
- **Current problems:** Two cyan rings drawn about 1 px apart (a doubled, uneven line) plus the hub rim give a cyan circle system with no job beyond 'ours'; the ring is crossed by the threat trims and the gun nubs; adds line noise without information.

#### `nudge_ghost`: Nudge ghost arrows (cyan triangles at sector 0)
- Crop: [wheel_core__nudge_ghost.png](brief_crops/wheel_core__nudge_ghost.png) (from p1)
- **Design goal:** Hint that the tower can be turned (Spin cards). Tertiary.
- **Look and feel:** Either remove (bible 3.22: draw no nudge buttons on the ring wheel until build settles it) or a pair of hollow cyan chevrons engraved in the bezel at the needle.
- **Current problems:** Contradicts the bible 'Open' note (no nudge on the ring wheel); the hollow triangles sit on top of the ring-0 Worm cell and the gun nubs, cluttering the most loaded spot on the board; they look like play/rewind media buttons.

#### `gun_tracers`: Gun tracer line (default fire)
- Crop: [wheel_core__gun_tracers.png](brief_crops/wheel_core__gun_tracers.png) (from p1)
- **Design goal:** Read each gun's default target as a line from slice rim to target; after threat, before HUD. The line only: each result end mark is its own element (gun_result_*).
- **Look and feel:** Cyan dashed tracer with ink edge, one dash rhythm shared with nothing else on the board (or matched deliberately to lane dashes), ending on the target cell centre or token, never on an edge.
- **Current problems:** Turret tracer to the Adjuster crosses its gold edge, so the hit point is ambiguous; dash 10/4 differs from lane dashes 10/7 by a near miss; two-shot BURST shown only as two lines 9 px apart; a second, thinner tracer style exists in p3 (resolve_fire_lines) and an idle stub style (gun_idle_stub).

#### `gun_result_hit`: Gun result: hit (white impact dot)
- Crop: [wheel_core__gun_result_hit.png](brief_crops/wheel_core__gun_result_hit.png) (from p1)
- **Design goal:** Read 'the shot lands and deals damage' at the tracer end.
- **Look and feel:** A white spark / impact glyph with ink, at least token-detail size (16 px+), in one set with the armor, ward and shield-pop results.
- **Current problems:** A 14 px white dot, too small to read as a hit and the same shape as turn dots and wave-arc width dots; at the Adjuster it sits on the gold edge.

#### `gun_result_armor`: Gun result: armor bounce (steel ricochet) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read 'the shot does nothing: armored' (Payload, Adjuster in strike phase).
- **Look and feel:** Steel ricochet glyph with ink (STEEL token), same size and family as the hit spark; ties to armor_cap.
- **Current problems:** Not reached in f1/f2 (no gun targets the Payload); code draws a small steel mark that has never been judged at size or next to the armor cap.

#### `gun_result_ward`: Gun result: ward bounce (gold ricochet) - LATENT on the plates, reached by the sim
- Crop: LATENT (no crop)
- **Design goal:** Read 'the shot is weakened by the Adjuster's ward' (h 0 here).
- **Look and feel:** Ricochet glyph in BOSS_GOLD with ink, keyed to warded_mark and ward_arc; same set as hit and armor.
- **Current problems:** The sim reaches it in f2 (BURST sector 4's two shots into warded Packet uid 6, both 'ward', h 0) but p2/p3 draw no tracers, so the glyph has never been seen; it must be designed with gun_tracers_preview.

#### `gun_result_shield_pop`: Gun result: shield pop (cyan) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read 'the shot strips a shield layer, not HP' (Jammer).
- **Look and feel:** Cyan pop glyph that matches shield_bracket, same set as the other results.
- **Current problems:** No shielded Jammer in this state; cyan pop would share NET_CYAN with the tracer itself, so it needs a shape that does not vanish into the line.

#### `gun_result_sealed`: Gun result: sealed (stale branch) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** None: the seal mechanic was removed in E9. Decision element: delete the branch or design it.
- **Look and feel:** Recommendation: retire (no look); if a seal returns, it gets a glyph from the results set.
- **Current problems:** gun_tracers10 still has a live 'sealed' branch (dark disc, white 2.4 px ring at ri + 16) that would draw a mark meaning nothing in the current rules.

#### `gun_idle_stub`: Idle-gun tracer stub - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read 'this gun has no target this turn' without a word (pairs with no_target_tag, and is the nowords form of it).
- **Look and feel:** A short cyan stub ending in an empty-target mark (open ring or bar), same tracer family, clearly not a shot.
- **Current problems:** Code draws a 2 px cyan dash 4/8 line from r 145 to 175: thinner than every tracer, crosses the trim and HP ring band, and ends in nothing, so it reads as a stray dash; it stays in nowords where the NO TARGET tag is gone.

#### `gun_tracers_preview`: Gun tracers under the plan (preview / resolve) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** In p2 show what the guns do under the previewed plan (here: BURST sector 4 into warded Packet 6, 'ward' x2); in p3 show what fired. The data is in state f2; showing it is a HOW decision.
- **Look and feel:** Same tracer and result set as the decide state, at plan value (or ghosted) so it is clearly the plan outcome; one tracer style across p1/p2/p3.
- **Current problems:** p2 draws no tracers at all and p3 draws only bare fire lines (resolve_fire_lines), so the preview hides the only state where a ward bounce happens and the player cannot see their guns change under the plan.

#### `gun_tracer_burst_pair`: Gun muzzle nubs (BURST double shot)
- Crop: [wheel_core__gun_tracer_burst_pair.png](brief_crops/wheel_core__gun_tracer_burst_pair.png) (from p1)
- **Design goal:** Show the shot leaves this slice, and that BURST fires 2.
- **Look and feel:** Two small muzzle pips on the slice rim, drawn as part of the tracer, same cyan, sized to the tracer.
- **Current problems:** Double circles look like a 'lollipop' or an eye; they overlap the threat trim and the HP ring; size (12 px) bigger than the tracer impact so the start is louder than the end.

#### `brace_plate`: Brace plate on a slice (p2)
- Crop: [wheel_core__brace_plate.png](brief_crops/wheel_core__brace_plate.png) (from p2)
- **Design goal:** Read 'this slice blocks the next landing entirely this turn'. A player-chosen defence: must read as the player's, not the enemy's.
- **Look and feel:** A heavy clamp plate around the wedge with rivets and the Brace glyph disc; colour from the player's side, clearly not the cyan unit shield and not enemy cream.
- **Current problems:** Cream is the enemy-HP colour (unit HP rows, Adjuster bar), so Brace reads as an enemy element; the glyph disc covers the turret icon; rivets are 10 px dots that read as bolts on a sticker, not a clamp; the plate's corner radius differs from the slice frame under it.

#### `slice_soak_marks`: Soak chevrons on a slice (p2)
- Crop: [wheel_core__slice_soak_marks.png](brief_crops/wheel_core__slice_soak_marks.png) (from p2)
- **Design goal:** Read 'this slice takes overflow pips instead of your HP' (player-marked END TURN choice). This entry is the inward chevrons; the rim arc, soak break X and soak-lost pip are separate elements of the same token family.
- **Look and feel:** Soak token distinct from schedule orange by hue and shape; a toggle the player clearly owns; placed beside the icon, never over it.
- **Current problems:** Soak #FF9628 is nearly identical to schedule #FF8C1A; inward chevrons mimic enemy hit chevrons, implying damage not absorption; the chevrons sit on top of the SHIELD icon (3.10 rule 4). Four marks for one choice (chevrons, rim arc, break X, soak pip): the family needs pruning to one or two.

#### `slice_soak_rim_arc`: Soak rim arc on the soaked slice (p2)
- Crop: [wheel_core__slice_soak_rim_arc.png](brief_crops/wheel_core__slice_soak_rim_arc.png) (from p2)
- **Design goal:** Mark the whole slice as soaking, at a glance.
- **Look and feel:** If kept: a soak-token edge treatment on the slice frame, not on the threat-trim radius; or removed in favour of the pip and one badge.
- **Current problems:** soak_marks draws an orange arc, 5.5 px on 9 px ink, at r 142 +/-26 deg: the exact radius and weight of the HARM threat trim, so in p2 it reads as a threat trim in the wrong colour and adds a fourth parallel arc in the band.

#### `slice_soak_break_x`: Soak break X (orange X when soaked to break, p2)
- Crop: [wheel_core__slice_soak_break_x.png](brief_crops/wheel_core__slice_soak_break_x.png) (from p2)
- **Design goal:** Read 'this slice breaks at END TURN because you soaked into it' (a chosen break, not an enemy break).
- **Look and feel:** The slice_break_x state shape (corner, off the icon) with a soak-token cue, so chosen and forced breaks share one break grammar.
- **Current problems:** Orange X drawn over the SHIELD icon (3.10 rule 4), in schedule-like orange; same shape as the red break X and the green dead X, so three X marks carry three meanings.

#### `slice_cracked_mark`: Cracked slice mark (white zigzag) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read 'slice already at 1 pip, holds this turn' without opening the HP bars.
- **Look and feel:** A short crack line in the screen glass at the rim, white with ink, consistent with the break X family.
- **Current problems:** Not drawn in this state (all slices at 2 HP); code draws a 4-point zigzag at 2 px that will vanish at 320 px; must be designed now so the slice state family (intact / cracked / breaks / broken) is one set.

#### `slice_broken_state`: Broken slice black-out - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read 'this slice is gone, ability lost' (persistent state).
- **Look and feel:** Bible 3.22 BROKEN: black-out wedge with red X plus the word or badge; distinct from the breaks-this-turn preview.
- **Current problems:** Not in this state; code uses a 170-alpha dark wedge and a 7 px red X at the slice centre, the same X as the preview, so preview and final state are indistinguishable.

#### `trigger_tower_hit`: Trigger hit landing on the tower - LATENT
- Crop: LATENT (no crop)
- **Design goal:** In a Trigger preview, show a pierce that reaches the tower: red pencil to the slice and the hit chevrons on it.
- **Look and feel:** Grease pencil in threat red (PENCIL_THREAT) ending in the chevron stack on the slice rim.
- **Current problems:** Not reached in this state; code uses HARM #FF4433 instead of the bible's PENCIL_THREAT #FF1C2C, so it would look like a unit chevron, not a plan.

#### `spin_ghost_preview`: Spin / Nudge card-hover ghost of the rotated tower - LATENT
- Crop: LATENT (no crop)
- **Design goal:** On hovering a Spin/Nudge card, show where slices and tracers end up (GDD 9.2 ghost preview on card hover) without losing the live tower.
- **Look and feel:** A ghost of the slices and tracers at plan value (outline or 40 percent), clearly secondary to the live wheel; rotation hinted by one plan-pencil arc, never by a media arrow.
- **Current problems:** Not drawn by the generator; only the Trigger preview exists, so there is no rule for how a rotated-tower ghost reads against the live tower and the threat trim.

### 4.2 Wave rings and units (`wave_rings`, 29 elements)

Contact sheet: `brief_crops/contact_wave_rings.jpg`

#### `empty_cell`: Empty ring cell (dark glass)
- Crop: [wave_rings__empty_cell.png](brief_crops/wave_rings__empty_cell.png) (from p1)
- **Design goal:** Read 'nothing here' instantly so occupied cells pop; keep the sector grid legible.
- **Look and feel:** Bible 3.22: dark glass with a 30 percent lane-style border; uniform fill, faint inner glass highlight.
- **Current problems:** Empty cells are near-black and larger in area than the units, so the board reads as mostly black holes; each empty cell gets two edges (a dim orange master outline from the board render plus the 30 percent lane border from the overlay); the dashed +2 border reads as grey noise at 320 px.

#### `ring_separators`: Ring gutters and sector spokes
- Crop: [wave_rings__ring_separators.png](brief_crops/wave_rings__ring_separators.png) (from p1)
- **Design goal:** Separate the three rings (depth) and the six sectors.
- **Look and feel:** Even ink gutters, slightly lighter than the backplate, the same width everywhere, continuous with the slice gutters.
- **Current problems:** Gutter width varies visibly between rings and between occupied and empty cells (unit cells inset 4 px with a 3 deg end inset, empty cells 3 px with 1.5 deg); some spokes are drawn by empty-cell outlines and others by unit cell edges, so the grid is irregular.

#### `unit_cell_screen`: Unit cell screen (muted mauve wash + programme texture)
- Crop: [wave_rings__unit_cell_screen.png](brief_crops/wave_rings__unit_cell_screen.png) (from p1)
- **Design goal:** Read 'an enemy unit occupies these sectors', its width, and its ring; the cell is the body that chevrons and HP sit on.
- **Look and feel:** Darkened, desaturated mauve programme screen (PL10), subtle per-kind tint, value clearly above empty cells and below the red chevrons; flat enough to carry marks.
- **Current problems:** All kinds share nearly the same mauve; ring-0 and ring-2 cells too close in value so depth reads only from outlines; CRT dot grids moire at 1080p; wide cells show the texture's own corner bezels mid-cell (unit_screen_bezel). Typed hex/code text is a separate element (unit_screen_code_text).

#### `unit_screen_bezel`: Unit screen bezel corners (programme slice frame)
- Crop: [wave_rings__unit_screen_bezel.png](brief_crops/wave_rings__unit_screen_bezel.png) (from p1)
- **Design goal:** None; it is the slice renderer's family-C frame showing at cell ends.
- **Look and feel:** Either a deliberate cell end-cap in the lane colour or removed; one end treatment for every unit.
- **Current problems:** Pink rounded corners from the programme frame appear at cell ends (e.g. 9 o'clock and 3 o'clock) and inside wide cells, a third outline on top of the lane outline and the HP socket; pink here breaks the 'pink = unit screen fill only' read.

#### `unit_screen_code_text`: Readable hex/code text in unit screens
- Crop: [wave_rings__unit_screen_code_text.png](brief_crops/wave_rings__unit_screen_code_text.png) (from p1)
- **Design goal:** None; texture only. No legible characters on the board.
- **Look and feel:** Same rule as slice_screen_code_text: sub-legible glyph noise under 10 percent contrast or none; never competing with the HP row or chevrons.
- **Current problems:** Hex columns ('01 00 2C 3F'...) are legible inside the Packet screens (ring 1 sector 0 next to the token, ring 2 sector 5) and survive in p1_nowords; a fourth programme-screen artefact besides moire, the bezel corners and the skull motif.

#### `unit_cell_outline`: Unit cell lane outline (NOW red / +1 blue / +2 dashed white)
- Crop: [wave_rings__unit_cell_outline.png](brief_crops/wave_rings__unit_cell_outline.png) (from p1)
- **Design goal:** Read ring depth on the unit itself (bible 3.22 four cues): now = solid red 4 px, +1 = solid pale blue 3 px, +2 = dashed white 3 px.
- **Look and feel:** One clean outline per cell, inset 4 px, with an ink line outside, dash rhythm fixed.
- **Current problems:** Outlines are partly hidden under the cream HP sockets and the armor cap; dashed white on ring 2 runs right beside cream HP segments and the white dashed landing lane, three white dashes in a row; ring-0 red outline merges with red chevrons and threat trim.

#### `token_disc`: Unit token disc (fill and size)
- Crop: [wave_rings__token_disc.png](brief_crops/wave_rings__token_disc.png) (from p1)
- **Design goal:** Anchor each unit: kind (glyph) on a disc that is the hover handle. This entry is the disc fill and size; the lane-style base ring and the dark halo are separate elements.
- **Look and feel:** 54 px disc (bible), darkened kind fill one value step off the cell mauve, glyph centred.
- **Current problems:** 48 px, below the bible's 54; fill nearly the cell's mauve so it reads only by outline; one unit looks different on the board and on its arc disc (arc_glyph_disc is darker).

#### `token_lane_base`: Token lane-style base ring (solid red / solid blue / 14-dash white)
- Crop: [wave_rings__token_lane_base.png](brief_crops/wave_rings__token_lane_base.png) (from p1)
- **Design goal:** Repeat ring depth on the token itself (depth four ways, 3.1).
- **Look and feel:** Fine-tier ring in the lane colour with ink, dash rhythm that survives at 320 px (fewer, longer dashes for +2), same weights as the lane outline tiers.
- **Current problems:** The 14-dash ring-2 base fills in to a grey ring at 320 px; ring-0 red base merges with the red chevrons beside it; base weights do not follow the lane outline ladder (4/3/3).

#### `token_halo`: Token dark halo (ink pool)
- Crop: [wave_rings__token_halo.png](brief_crops/wave_rings__token_halo.png) (from p1)
- **Design goal:** Lift the token off busy screens (shadow, 3.7: up to 75 percent, blur 4).
- **Look and feel:** Tight soft ink pool, even on all tokens, under 75 percent, never wider than ~6 px past the disc.
- **Current problems:** Wide dark halo makes a muddy blot on the mauve screen, larger on some tokens than others; it darkens neighbouring HP cream and chevrons.

#### `glyph_packet`: Packet glyph (square with arrow)
- Crop: [wave_rings__glyph_packet.png](brief_crops/wave_rings__glyph_packet.png) (from p1)
- **Design goal:** Identify the Packet kind (bible 3.22 twin-checked glyphs).
- **Look and feel:** White silhouette, ink keyline, the same visual weight as the Worm and Payload glyphs.
- **Current problems:** The white rounded square is the heaviest glyph on the board and reads as a 'next / skip' media button; arrow points right regardless of travel direction (units travel inward and clockwise), so it implies wrong motion.

#### `glyph_worm`: Worm glyph (zigzag, the 'M' badge)
- Crop: [wave_rings__glyph_worm.png](brief_crops/wave_rings__glyph_worm.png) (from p1)
- **Design goal:** Identify the Worm kind.
- **Look and feel:** Zigzag silhouette that reads as a worm/virus, not a letter.
- **Current problems:** Reads as the letter M (players will call it 'the M unit'); the glyph is larger than its disc and touches the rim; letter-like glyphs clash with the no-digits/word discipline of the board.

#### `glyph_payload`: Payload glyph (diamond with two bars)
- Crop: [wave_rings__glyph_payload.png](brief_crops/wave_rings__glyph_payload.png) (from p1)
- **Design goal:** Identify the Payload kind (armored).
- **Look and feel:** Diamond with two bars, white with keyline; must not share the diamond shape language used for HP-through and the boss.
- **Current problems:** Diamond shape collides with red HP-through diamonds and the gold Adjuster diamond (three meanings, one shape); the two bars read as an equals sign.

#### `unit_hp_row`: Unit HP row (cream segments in socket)
- Crop: [wave_rings__unit_hp_row.png](brief_crops/wave_rings__unit_hp_row.png) (from p1)
- **Design goal:** Read the unit's HP left, grouped per sector, and pips lost this END TURN (red slash).
- **Look and feel:** Cream segments in a dark socket along the cell's outer edge, small gap at each sector boundary, ink keylines, lost pips slashed in harm red.
- **Current problems:** Segments are long thin dashes that read as a dashed border, not countable pips (a 9-HP Packet shows 9 cream dashes along 180 deg); socket covers the lane outline; lost slash at 2.6 px is invisible at 320 px; cream on wide cells forms long cream arcs that become the strongest ring on the board after the orange schedule.

#### `chev_solid_stack`: Body chevrons, solid (hit now)
- Crop: [wave_rings__chev_solid_stack.png](brief_crops/wave_rings__chev_solid_stack.png) (from p1)
- **Design goal:** Read how hard the unit hits each slice it covers (1-4 chevrons, pointing at the tower). The main threat read on the board.
- **Look and feel:** Nested inward V chevrons in harm red with ink keyline, 28 px wide, fixed pitch, stem only on stacks of 2+; centred on each covered sector's axis.
- **Current problems:** The stem plus V forms an arrow/'Y' (crow's foot) that reads as a direction sign more than a count; stacks at the same sector on all three rings line up into one long red column (see chev_sector_column) that reads as one big arrow; chevrons sit on the inner edge so they overlap the lane outline and the ring gutter.

#### `chev_hollow`: Body chevrons, hollow (growth to come)
- Crop: [wave_rings__chev_hollow.png](brief_crops/wave_rings__chev_hollow.png) (from p1)
- **Design goal:** Read 'this unit will hit 1 harder by the time it lands' (PL10 ask 2).
- **Look and feel:** Same size and pitch as solid chevrons, outlined red with dark core, stacked outward of the solid ones.
- **Current problems:** Hollow chevrons have a 3.6 px dark core that closes at 320 px, so they read as solid; the outer ink makes them heavier than the solid ones.

#### `chev_sector_column`: Chevron columns through the rings (composite)
- Crop: [wave_rings__chev_sector_column.png](brief_crops/wave_rings__chev_sector_column.png) (from p1)
- **Design goal:** When units in several rings share a sector, the player must still count per unit.
- **Look and feel:** Per-unit stacks separated by a clear gap at each ring gutter; the column rhythm reads as 'unit, unit, unit'.
- **Current problems:** At sector 3 the stacks of rings 0, 1 and 2 plus stems chain into a 170 px red spine; the eye counts 9 chevrons as one threat.

#### `armor_cap`: Armor cap (steel rim on Payload)
- Crop: [wave_rings__armor_cap.png](brief_crops/wave_rings__armor_cap.png) (from p1)
- **Design goal:** Read 'armored: gun shots do nothing, Trigger it' at a glance.
- **Look and feel:** Steel band on the cell's outer edge with rivets and a highlight, clearly metal, distinct from the cream HP and the white lane dash.
- **Current problems:** Steel grey sits next to cream HP and a dashed white lane line, so it reads as a third pale stripe, not armor; rivets are 3 px dots that disappear; no armor cue on the token itself.

#### `warded_mark`: Warded mark (gold shield on units in the Adjuster's sector)
- Crop: [wave_rings__warded_mark.png](brief_crops/wave_rings__warded_mark.png) (from p1)
- **Design goal:** Read 'gun shots on this unit deal less while the Adjuster lives'.
- **Look and feel:** Small gold boss-ward badge tied to the Adjuster's visual language (diamond/skull family), not a shield.
- **Current problems:** Shield silhouette repeats the SHIELD slice icon and the Brace glyph; 22 px with a 2 px inner bar, below the 16 px detail rule; placed at an arbitrary spot in the cell, not next to the token.

#### `dead_x`: Shot-dead X (green X disc)
- Crop: [wave_rings__dead_x.png](brief_crops/wave_rings__dead_x.png) (from p1)
- **Design goal:** Read 'our guns kill this unit this turn, it never lands'.
- **Look and feel:** Gain-green X disc with ink, at the token, and the unit's cell treated as 'gone' (dim / cross-hatch preview).
- **Current problems:** 28 px disc floats in an empty gap far from the dying Worm's token; the dying unit's cell still shows full red chevrons, so it still looks like a threat; green X vs red slice X are the same shape with opposite meanings.

#### `adjuster_cell`: Adjuster cell (gold-edged glass)
- Crop: [wave_rings__adjuster_cell.png](brief_crops/wave_rings__adjuster_cell.png) (from p1)
- **Design goal:** Read 'the boss sits here, on ring +1 sector 2'. Boss must read as the boss in any form (3.22).
- **Look and feel:** Dark gold glass cell with a gold outline at medium weight and ink; its own material distinct from unit mauve.
- **Current problems:** Gold outline (4 px) is the same weight as lane outlines so it reads as a fourth lane colour; fill is muddy olive-black; the gold cell edge overlaps the ring 0/1 gutter and the ward arc.

#### `adjuster_diamond`: Adjuster body (gold diamond with skull)
- Crop: [wave_rings__adjuster_diamond.png](brief_crops/wave_rings__adjuster_diamond.png) (from p1)
- **Design goal:** Read 'boss' first among enemy pieces; its HP and that it can be killed for a star.
- **Look and feel:** Gold diamond with double edge and skull, the one boss emblem, sized above unit tokens, with a dark halo.
- **Current problems:** 60 px diamond is barely larger than unit tokens; the gun tracer ends on its edge; the skull at 24 px is detailed; the inner pale-gold second line is 1.6 px and aliases.

#### `adjuster_hp_bar`: Adjuster HP bar (10 cream segments)
- Crop: [wave_rings__adjuster_hp_bar.png](brief_crops/wave_rings__adjuster_hp_bar.png) (from p1)
- **Design goal:** Read boss HP 10 and the 1 pip lost this END TURN.
- **Look and feel:** Segmented bar in the boss's own colour family, on the cell's outer edge, with the lost pip slashed; groups of 5.
- **Current problems:** Same cream as unit HP, so boss HP does not read as special; no grouping of 5; the HUD KILL ADJUSTER tally is gold, so the two displays of the same HP use different colours.

#### `ward_arc`: Ward arc (gold arc inside ring NOW at the Adjuster's sector)
- Crop: [wave_rings__ward_arc.png](brief_crops/wave_rings__ward_arc.png) (from p1)
- **Design goal:** Show which sector is warded by the Adjuster.
- **Look and feel:** A gold arc engraved on the ring-0 inner edge, keyed to the warded marks and the Adjuster.
- **Current problems:** Drawn at r 157, on the outer edge of the player HP ring, between the cyan code-base ring, the red threat trim and the green HP ring: a 5-colour stripe (green, cyan, red, gold, salmon) at 4 o'clock that reads as a selection highlight, not as a ward on ring NOW.

#### `consumed_unit`: Consumed unit state (Trigger used it up, p2)
- Crop: [wave_rings__consumed_unit.png](brief_crops/wave_rings__consumed_unit.png) (from p2)
- **Design goal:** In preview, read 'used up by the Trigger' (plan yellow), dimmed, not a threat. Trigger-killed is a separate element.
- **Look and feel:** Cell dimmed to ~40 percent, plan-yellow outline, token greyed, shares one ghost treatment with hover dimming.
- **Current problems:** Consumed Payload loses its cell art in some regions and leaves a dark hole with a faint outline, while the skull motif stays bright; dimmed token hard to find; no shared ghost treatment with hover dimming.

#### `trigger_killed_unit`: Trigger-killed unit state (p2)
- Crop: [wave_rings__trigger_killed_unit.png](brief_crops/wave_rings__trigger_killed_unit.png) (from p2)
- **Design goal:** In preview, read 'the Trigger kills this unit: it never lands' (and pays the refund), dimmed, not a threat.
- **Look and feel:** Same ghost treatment as consumed_unit with a harm-red (killed) outline and the dead-X family mark at the token; the refund token sits beside, not on top.
- **Current problems:** The killed Packet's greyed token is hidden under the refund burst; the red outline is the same red as the NOW lane outline, so a dead unit reads as a live ring-0 unit.

#### `screen_motif_skull`: Programme screen motif (faint skull in a unit screen)
- Crop: [wave_rings__screen_motif_skull.png](brief_crops/wave_rings__screen_motif_skull.png) (from p1)
- **Design goal:** None; it is texture.
- **Look and feel:** Unit screens carry no pictograms; any motif stays below 10 percent contrast and never uses a boss or glyph-set shape.
- **Current problems:** A pale skull in the Payload's ZERO-DAY screen at 8 o'clock reads as a second Adjuster or a dead unit; the most misleading artefact on the board; it shows more strongly in p2, where the consumed Payload keeps its cell art (keep_all) and the skull is the brightest thing left in the dimmed cell.

#### `shield_bracket`: Unit shield bracket (Jammer cyan) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read a separate cyan shield layer that empties before HP.
- **Look and feel:** Cyan bracket over the first share of the HP row, dashed when lost.
- **Current problems:** No shielded Jammer in this state; the code bracket is 4.2 px and sits on the cell rim where the lane outline is, so it will collide; must be designed with the HP row.

#### `adjuster_armor_strike`: Adjuster armor cap and strike chevrons - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read the boss's strike phase (armored, strikes the tower).
- **Look and feel:** Same steel cap as unit armor; strike chevrons from the boss body to the slice.
- **Current problems:** Not in this state (phase 1, no strike); code draws strike chevrons at the bezel (old satellite position), not from the ring body.

#### `ring_unit_wide6`: Full-ring unit (climax Ring, width 6) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read one unit that covers the whole ring.
- **Look and feel:** One continuous cell band with one token and a per-sector HP row.
- **Current problems:** Not in this state; the code paints a full annulus with no start/end mark, so where the token sits and where HP starts are arbitrary.

### 4.3 Outer rings and timing (`outer_rings`, 31 elements)

Contact sheet: `brief_crops/contact_outer_rings.jpg`

#### `board_scrim`: Board scrim / backdrop pool (radial pool under the board)
- Crop: [outer_rings__board_scrim.png](brief_crops/outer_rings__board_scrim.png) (from p1)
- **Design goal:** Give the board air over the cutaway, board first, without a visible box. The radial pool only; the global backdrop grade is backdrop_grade.
- **Look and feel:** A soft radial darkening (scrim, bible SCRIM token) under the board on room_bio_bare, value graded so the room stays the second mass.
- **Current problems:** E10's dim pool was baked for the old crane backdrop; on room_bio_bare tower windows show as a grid through ring gaps and beyond the outer arcs; the board's right edge meets the room with no transition.

#### `backdrop_grade`: Global backdrop grade (dim x0.80 + 2.5 px blur)
- Crop: [outer_rings__backdrop_grade.png](brief_crops/outer_rings__backdrop_grade.png) (from p1)
- **Design goal:** Keep the cutaway room the lit second mass (L5) behind every UI element, without double grading it.
- **Look and feel:** One grade decision: either room_bio_bare's own grade (city x0.58, focus hull x0.84 per the cutaway NOTES) is final and E10 adds nothing, or a stated extra dim/blur is applied once; documented as a token with SCRIM.
- **Current problems:** cv_lib.backdrop applies a global x0.80 dim and 2.5 px Gaussian blur to the whole backdrop before the pool; room_bio_bare is already graded, so the stack dims the room's focus hull below its intended x0.84 and softens its pixel detail; undecided and unowned until now.

#### `board_backplate`: Board backplate disc
- Crop: [outer_rings__board_backplate.png](brief_crops/outer_rings__board_backplate.png) (from p1)
- **Design goal:** One dark plate under the wheel so gaps read as gutters, not holes into the city.
- **Look and feel:** Near-black disc to the bezel inner edge, subtle radial value, ink edge.
- **Current problems:** Plate stops at the bezel, but the landing arcs and wave arcs outside sit directly on the backdrop, so the outer 120 px of the board has no ground and reads loose.

#### `bezel_ring`: Wave bezel ring (brushed metal)
- Crop: [outer_rings__bezel_ring.png](brief_crops/outer_rings__bezel_ring.png) (from p1)
- **Design goal:** Frame the board and carry the schedule cells and sector digits; owner kit (corp) by material.
- **Look and feel:** Brushed corp-material ring (bible 2.4: ownership by material), medium value, ink edges; for the Solace slice, Solace material, never a corp hue in a UI role.
- **Current problems:** It is the Meridian brushed brown-orange ring (Meridian is hibernated per the amendments draft; this is a Solace fight); the brushed texture has radial streaks that look like motion blur; low contrast between bezel and the dark landing lanes outside.

#### `bezel_rim_lines`: Bezel rim lines and baked light (orange edge glows)
- Crop: [outer_rings__bezel_rim_lines.png](brief_crops/outer_rings__bezel_rim_lines.png) (from p1)
- **Design goal:** Edge the bezel as a physical ring; carries no information.
- **Look and feel:** Ink edges plus at most one hairline highlight from the top-left (3.6 light), in the bezel material colour, never schedule orange or a corp hue.
- **Current problems:** ring_base adds orange (Meridian accent) glow rims at the outer edge (R1-1.5) and inner edge (R0+1.5) plus a directional light cos(th-315): two extra full orange circles at r ~356 and ~388 framing the schedule cells, so orange reads as a frame colour, not as the schedule's one meaning.

#### `bezel_ticks`: Bezel tick marks (60 minor, 6 major)
- Crop: [outer_rings__bezel_ticks.png](brief_crops/outer_rings__bezel_ticks.png) (from p1)
- **Design goal:** Engrave the dial; tertiary.
- **Look and feel:** Fine engraved ticks, major ticks at sector digits, one value step above the bezel.
- **Current problems:** Ticks are 1.2 px and invisible except where the bezel is dark; under the orange schedule cell they disappear; they add nothing the sector digits do not.

#### `sector_digits`: Sector digits 0-5 (turn tick numbers)
- Crop: [outer_rings__sector_digits.png](brief_crops/outer_rings__sector_digits.png) (from p1)
- **Design goal:** Name sectors 0-5 (the needle is 0) so cards and tags can refer to them; read on demand.
- **Look and feel:** Bible 3.22: engraved in the bezel; dark disc with orange ring and white Anton digit, keyline, legible at 22 px.
- **Current problems:** Digits are loose 30 px discs centred on r 385 that overhang the bezel's outer edge (r 389) by 11 px, rather than engraved; orange ring ties them to the schedule colour though they are not schedule; digit 0 sits right on top of the needle and they overlap.

#### `sector_digits_nowords`: Sector digit nowords proxies (white bars)
- Crop: [outer_rings__sector_digits_nowords.png](brief_crops/outer_rings__sector_digits_nowords.png) (from nw)
- **Design goal:** With words off, still tell the six sectors apart and mark sector 0.
- **Look and feel:** A non-digit sector code (tick counts 1-6 engraved, or pip clusters) in the same disc, or the discs dropped and the needle plus bezel majors carry the sector.
- **Current problems:** Each disc shows the same small white bar instead of 0-5, so all six discs look identical and carry no information; the generic L2.text proxy was never designed.

#### `needle`: Needle (sector 0 marker)
- Crop: [outer_rings__needle.png](brief_crops/outer_rings__needle.png) (from p1)
- **Design goal:** Mark sector 0 / the reading point of the schedule.
- **Look and feel:** One clean white triangle with ink, engraved into the bezel at 12 o'clock, not overlapping the digit.
- **Current problems:** Overlaps the sector-0 digit disc; it is the only white triangle on the board but looks like a 'play' arrow pointing down.

#### `sched_this_turn`: Schedule cell '+2 THIS TURN' (live)
- Crop: [outer_rings__sched_this_turn.png](brief_crops/outer_rings__sched_this_turn.png) (from p1)
- **Design goal:** Read the rings step +2 sectors at this END TURN, clockwise from the needle, arc length = step x 60 deg. The strongest warm mass; reads in under 0.5 s.
- **Look and feel:** Bright schedule orange bezel cell with ink text along the arc (mono >= 16 px) and pale direction chevrons; ink edge; the only filled orange on the board.
- **Current problems:** The live cell is the largest saturated area on the screen (120 deg x 26 px) and outweighs the red threat; text '+2 THIS TURN' is ink on orange at 17 px with the plus sign poorly formed; the cell's start butts into the digit-0 disc; no end cap, so the cell just stops at digit 2.

#### `sched_chevrons`: Schedule direction chevrons
- Crop: [outer_rings__sched_chevrons.png](brief_crops/outer_rings__sched_chevrons.png) (from p1)
- **Design goal:** Show the direction of ring travel (clockwise).
- **Look and feel:** Pale chevrons inside the cell at a fixed pitch, fine weight, pointing along travel.
- **Current problems:** Pale outline chevrons at 1.8 px look like V tick marks; they are spaced by a 12 deg rule so the pitch changes with cell length; they read as decoration.

#### `sched_hold_cells`: Schedule HOLD cells (HOLD NEXT / HOLD THEN)
- Crop: [outer_rings__sched_hold_cells.png](brief_crops/outer_rings__sched_hold_cells.png) (from p1)
- **Design goal:** Read the next two steps are 0 (rings hold), with a distinct 0-step glyph (E9 fix), never a dim gap.
- **Look and feel:** Dark bezel cells with an orange outline, a HOLD glyph disc (two bars) and mono text along the arc; same family as the live cell, clearly 'off'.
- **Current problems:** HOLD text sits on the lower half and is flipped correctly but is only 16 px with low-contrast orange on dark brown; the hold glyph disc (II) is 26 px and looks like a pause button (media language again); the cells are 40 deg each regardless of meaning, which is fine, but they meet the digit-3 disc.

#### `sched_hold_live`: Live HOLD cell (step 0 THIS TURN) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Read 'rings hold this END TURN' as the live cell when the current step is 0.
- **Look and feel:** Live-cell geometry and weight, HOLD glyph from the redesigned set, neutral (not orange fill) but clearly the current step.
- **Current problems:** Not in this state (schedule 2,0,0); bezel9 draws a white outline and white glyph, which matches the +2 lane white and nothing in the schedule family.

#### `ring_tags`: Ring tags (NOW W1 / +1 W2 / +2 W3)
- Crop: [outer_rings__ring_tags.png](brief_crops/outer_rings__ring_tags.png) (from p1)
- **Design goal:** State ring depth in words and which wave is on each ring (fourth depth cue).
- **Look and feel:** Small tags in the ring gutter at 30 deg, lane colour outline and text, Anton with keyline, consistent size.
- **Current problems:** Tags sit across ring boundaries and overlap the Worm cell (NOW W1) and gun nubs; '+1'/'+2' use a tiny raised plus that reads as a bullet; Anton at 17 px is below the bible's bare-number floor; three tags in a diagonal staircase add a fourth direction to the board.

#### `ring_tags_nowords`: Ring tags in nowords (empty boxes; W tags vanish)
- Crop: [outer_rings__ring_tags_nowords.png](brief_crops/outer_rings__ring_tags_nowords.png) (from nw)
- **Design goal:** With words off, still state ring depth and which wave sits on each ring.
- **Look and feel:** Depth by the lane-style mark inside the tag (solid / solid / dashed swatch) and wave by pip count, or tags removed in nowords with depth left to the other three cues.
- **Current problems:** The tags stay as empty outlined red/blue/white boxes that read as UI placeholders, while the W4-W6 tags disappear entirely, so nowords is inconsistent between the two tag kinds.

#### `landing_arc_frame`: Landing arc frame (one per landing unit)
- Crop: [outer_rings__landing_arc_frame.png](brief_crops/outer_rings__landing_arc_frame.png) (from p1)
- **Design goal:** Read, per landing unit, which slices it lands on and when, beside the bezel (PL10 ask 1).
- **Look and feel:** Dark band outside the bezel spanning the landing sectors, outlined in the unit's lane style, packed into the fewest lanes; one object per unit.
- **Current problems:** Up to 3 concentric lanes of long arcs (red, blue, dashed white) plus 3 wave arcs make 6-9 rings outside the bezel, the busiest region of the screen; the arcs are not visually tied to their unit (only by lane colour); ends are square-cut with no start cap, so direction and start sector are unclear.

#### `arc_glyph_disc`: Landing arc kind disc
- Crop: [outer_rings__arc_glyph_disc.png](brief_crops/outer_rings__arc_glyph_disc.png) (from p1)
- **Design goal:** Tie the arc to its unit kind at the arc start.
- **Look and feel:** Small token disc (same family as the board token) at the arc start with lane-style ring.
- **Current problems:** 38 px disc overlaps the arc edges and neighbouring lanes; repeats the M/arrow glyph problems; fill darker than the board token so the same unit looks different in two places.

#### `arc_wear_mark`: Worm wear mark on arc (green square with crack)
- Crop: [outer_rings__arc_wear_mark.png](brief_crops/outer_rings__arc_wear_mark.png) (from p1)
- **Design goal:** Read 'this Worm wears 1 extra slice pip on landing'.
- **Look and feel:** A wear glyph in the slice-damage family (not gain green).
- **Current problems:** Gain green (#7BE07B) implies a benefit; the crack line inside is 2 px; it looks like a battery or a map marker.

#### `arc_now_dot`: Lands-this-END-TURN dot (red)
- Crop: [outer_rings__arc_now_dot.png](brief_crops/outer_rings__arc_now_dot.png) (from p1)
- **Design goal:** Read 'this lands now'.
- **Look and feel:** A single harm-red dot with white ring, sized above the turn dots.
- **Current problems:** Reads like a notification badge or record button; floats between disc and chevrons with no alignment to the turn-dot slot it replaces.

#### `arc_turn_dots`: Turns-until dots (white)
- Crop: [outer_rings__arc_turn_dots.png](brief_crops/outer_rings__arc_turn_dots.png) (from p1)
- **Design goal:** Read how many turns until the unit lands (1 or 2).
- **Look and feel:** Small white dots with ink in a fixed slot after the disc; same slot as the now-dot.
- **Current problems:** 10 px dots look like the wave-arc width dots and the white dashes of the +2 lane they sit on; no label or grouping, so '2 dots' is not tied to 'turns'.

#### `arc_chevrons`: Landing arc chevrons (solid + hollow)
- Crop: [outer_rings__arc_chevrons.png](brief_crops/outer_rings__arc_chevrons.png) (from p1)
- **Design goal:** Read hit at landing per sector (solid now + hollow growth).
- **Look and feel:** Same chevron grammar as the body chevrons, scaled, pointing inward, centred on each landing sector.
- **Current problems:** Arc chevrons are smaller (13 px tall) and thinner than body chevrons, so the same count reads as a different scale; hollow ones are tiny outlined Vs that vanish; on the lower half they appear upside down relative to reading.

#### `arc_diamonds`: Red diamonds (HP through per sector)
- Crop: [outer_rings__arc_diamonds.png](brief_crops/outer_rings__arc_diamonds.png) (from p1)
- **Design goal:** Read the HP that gets through to the player per sector, after guns; the sum of this-turn diamonds equals THROUGH (6).
- **Look and feel:** Harm-red diamonds with ink, fixed pitch, right after the chevrons; the most important mark on the arc.
- **Current problems:** 16 px diamonds are the same size as the chevrons, so 'through' does not outrank 'hit'; diamonds of next-turn units are drawn the same as this turn's (only the arc lane says when); they share the diamond shape with the Payload glyph and the boss.

#### `arc_check`: Nothing-through check (green, p2)
- Crop: [outer_rings__arc_check.png](brief_crops/outer_rings__arc_check.png) (from p2)
- **Design goal:** Read 'this landing costs you nothing'.
- **Look and feel:** Gain-green check with ink in the diamond slot.
- **Current problems:** Fine shape, but small (17 px) and the only check on the board; green on a blue-outlined arc next to green HP reads as 'heal'.

#### `arc_soak_chevron`: Soak chevron on a landing arc (p2)
- Crop: [outer_rings__arc_soak_chevron.png](brief_crops/outer_rings__arc_soak_chevron.png) (from p2)
- **Design goal:** Read 'one pip of this landing is soaked by the slice' on the arc.
- **Look and feel:** The soak token from the slice family, scaled to the arc, in the diamond slot it replaces; never a chevron shape.
- **Current problems:** A single orange inward V reads as a growth chevron in the wrong colour; orange equals schedule orange.

#### `arc_brace_glyph`: Brace glyph on a landing arc (p2)
- Crop: [outer_rings__arc_brace_glyph.png](brief_crops/outer_rings__arc_brace_glyph.png) (from p2)
- **Design goal:** Read 'this landing is blocked by Brace' on the arc.
- **Look and feel:** The Brace mark from the redesigned brace_plate (player-side colour, open call 2), scaled to arc-mark size like the other arc marks.
- **Current problems:** A 28 px cream C_BRACE glyph (not a clamp), bigger than every other arc mark and in the enemy-HP cream.

#### `arc_twist_mark`: Twist mark on arc (p2)
- Crop: [outer_rings__arc_twist_mark.png](brief_crops/outer_rings__arc_twist_mark.png) (from p2)
- **Design goal:** Read that this unit's landing was moved by the played Twist.
- **Look and feel:** Small plan-yellow twist disc, same as the twist badge on the ring tag.
- **Current problems:** Bright yellow disc is the loudest mark on its arc; duplicates the twist badge at the ring tag.

#### `future_wave_arcs`: Future wave arcs (W4, W5, W6)
- Crop: [outer_rings__future_wave_arcs.png](brief_crops/outer_rings__future_wave_arcs.png) (from p1)
- **Design goal:** Preview the waves still to come beyond the rim; tertiary, read on demand.
- **Look and feel:** Thin full rings far outside, schedule orange for normal waves, harm red with hazard ticks for the climax, low value.
- **Current problems:** 3 px full rings at full saturation compete with the landing arcs; W4 (r 492) and W5 (r 509) run inside the third landing lane (r 480-510), so wave arcs and landing arcs overlap; W6 (r 526) comes within 10-14 px of the screen's left and top edges, so the board feels jammed into the frame.

#### `wave_arc_unit_pips`: Unit pips on future wave arcs
- Crop: [outer_rings__wave_arc_unit_pips.png](brief_crops/outer_rings__wave_arc_unit_pips.png) (from p1)
- **Design goal:** Show the kinds and widths of each future wave.
- **Look and feel:** Tiny glyph discs with white width ticks; must still pass the 16 px glyph rule.
- **Current problems:** Glyphs are 13 px (below the 16 px rule) in 18 px discs and are unreadable; width ticks are 6 px dots indistinguishable from turn dots.

#### `climax_hazard_ticks`: Climax hazard ticks (W6)
- Crop: [outer_rings__climax_hazard_ticks.png](brief_crops/outer_rings__climax_hazard_ticks.png) (from p1)
- **Design goal:** Mark the last wave as the climax.
- **Look and feel:** Short yellow-black hazard ticks along the red climax arc.
- **Current problems:** Ticks are thin yellow-green slashes at 190 alpha that look like stray scratches on the backdrop; they are 'yellow' but greener than plan yellow.

#### `wave_tags`: Wave tags W4 / W5 / W6
- Crop: [outer_rings__wave_tags.png](brief_crops/outer_rings__wave_tags.png) (from p1)
- **Design goal:** Name the future waves.
- **Look and feel:** Small mono tags at each arc's start, wave colour outline.
- **Current problems:** Three tags stack in a diagonal staircase at the top centre, squeezed against the screen edge (W6 at y 25); mono 16 below the 18 terminal floor; they are the only tags outside the board so they look orphaned.

#### `sched_plus_cells`: Schedule non-live +N cells - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Show later non-zero steps (e.g. +1 NEXT) as 'coming, not now'.
- **Look and feel:** Dark orange cell with pale chevrons and orange text, same geometry as the live cell.
- **Current problems:** Not in this state (schedule 2, 0, 0); code uses a dark brown fill nearly the same as the bezel, so a +1 NEXT cell would be hard to find.

### 4.4 Turn header and damage panel (`top_hud`, 35 elements)

Contact sheet: `brief_crops/contact_top_hud.jpg`

#### `header_plate`: Turn header plate
- Crop: [top_hud__header_plate.png](brief_crops/top_hud__header_plate.png) (from p1)
- **Design goal:** Frame the fight title and the waves count; one glance orientation.
- **Look and feel:** CRT terminal plate: navy glass, cyan edge, faint scanlines, r 8.
- **Current problems:** Plate edge 2 px cyan at 210 alpha is softer than the bill box's 3 px white edge, so two different panel languages sit stacked; the header is narrower in height (46 px) than the type inside needs; right end crowded by the help button.

#### `header_title`: Header title (TURN 2 | SHIFTING WAVES)
- Crop: [top_hud__header_title.png](brief_crops/top_hud__header_title.png) (from p1)
- **Design goal:** Read the turn number first, then the combat mode.
- **Look and feel:** Anton white, turn number given weight; divider bar consistent with the plate edge.
- **Current problems:** Turn number has the same size as the mode name, so 'turn 2' does not lead; the '|' divider is a font glyph thinner than every other stroke; no keyline on white Anton over a translucent plate.

#### `waves_left`: WAVES 6 LEFT label and pips
- Crop: [top_hud__waves_left.png](brief_crops/top_hud__waves_left.png) (from p1)
- **Design goal:** Read how many waves remain (6) and that the last is the climax (red pip).
- **Look and feel:** Schedule-orange label and 6 pips, climax pip red, grouped at the right with even spacing.
- **Current problems:** Label (Anton 24 orange) is louder than the turn title; there is a 90 px empty gap between label and pips; pips are 14 x 20 rounded rects, a different pip shape from the HUD tally segments and the RAM pips.

#### `help_button`: Help button (?)
- Crop: [top_hud__help_button.png](brief_crops/top_hud__help_button.png) (from p1)
- **Design goal:** Offer the legend/help; read as a button, tertiary.
- **Look and feel:** Small terminal chip button with ? glyph in neutral or cyan, focus brackets on focus (2.10).
- **Current problems:** Plan-yellow circle draws the eye in the top-right corner every time (yellow is the plan colour); the ? glyph is Anton, heavy, and touches the ring; it is outside the header plate's padding.

#### `bill_frame`: Damage bill frame (YOU box)
- Crop: [top_hud__bill_frame.png](brief_crops/top_hud__bill_frame.png) (from p1)
- **Design goal:** Contain the bill as one hero box (bible 3.22 bill item 2).
- **Look and feel:** Terminal plate language shared with the header (cyan edge), slightly heavier edge as the hero box; internal rows as inset terminal strips.
- **Current problems:** White 3 px outline at r 10 is a different panel style from all other HUD plates (cyan 2 px r 8); inner rows have their own cyan outlines, giving nested boxes 3 deep; the box is 202 px tall, the largest HUD mass, and its white edge is brighter than the board's own outlines.

#### `terminal_plate_kit`: Shared HUD terminal plate component (fill, edge, radius, scanlines)
- Crop: [top_hud__terminal_plate_kit.png](brief_crops/top_hud__terminal_plate_kit.png) (from p1)
- **Design goal:** One panel language for every HUD plate (3.6), so the column reads as one instrument.
- **Look and feel:** TERMINAL_BG fill, one edge spec (cyan Fine), r 8, scanlines at a set alpha that never moire with text; hero variant by weight only; used by header, bill, strips, objectives, RAM, option chips, chain strip, UNDO, hover tag, NO TARGET.
- **Current problems:** cv_lib.terminal (238 alpha fill, cyan 2 px at 210 alpha, r 8, 1 px scanlines every 4 px at alpha 38) is used by some plates while the bill (white 3 px r 10), objectives and chain strip (grey) and option chips (grey/yellow) go off-kit; scanlines show through gaps as stripes over the room and nobody owns the component.

#### `hud_scrim`: HUD and hand scrim over the room
- Crop: [top_hud__hud_scrim.png](brief_crops/top_hud__hud_scrim.png) (from p1)
- **Design goal:** Seat the right column and the hand on the room so they read as UI over the scene (SCRIM token 'under the board and HUD over the room').
- **Look and feel:** One soft SCRIM shape under the column and one under the hand (or panel fills that do the job), graded so the room focus hull stays the second mass.
- **Current problems:** No element owns it: plates sit on the lit room at 215-238 alpha with gaps between plates showing the room; the cards sit directly on the lit lobby; the column grows in p2/p3 into the focus hull.

#### `layout_grid`: Right column grid and screen safe margins
- Crop: [top_hud__layout_grid.png](brief_crops/top_hud__layout_grid.png) (from p2)
- **Design goal:** Align every HUD plate to one grid and keep all UI inside a safe frame; the column must not collide with the board or the room focus.
- **Look and feel:** One left edge and inner padding for every plate, one vertical gap, a defined safe frame (24 px, 3.10 rule 11) for board arcs and stickers; a rule for p2/p3 growth.
- **Current problems:** Header starts at x 1066, other plates at 1062, inner strips at 1068; vertical gaps 8 / 10 / 4 px; p2 chips and p3 chain push objectives/RAM to y ~400 into the focus hull; outer arcs (r 526) come within ~20 px of the column and 10-14 px of the left/top edges; SEND IT crops at the screen edges.

#### `you_hp_tally`: YOU HP tally (15 segments, lost slashed)
- Crop: [top_hud__you_hp_tally.png](brief_crops/top_hud__you_hp_tally.png) (from p1)
- **Design goal:** Read your HP 15 and the 6 you lose this END TURN, in groups of 5.
- **Look and feel:** Gain-green segments, lost-this-turn as a distinct salmon/red with slash, groups of 5 with clear gaps; same segment shape as the HP ring.
- **Current problems:** Lost segments are pale salmon with a white slash, weaker than the red THROUGH digit they correspond to; segments (13 x 22) differ from the HP ring segments in shape; the YOU label is 16 px mono at the far top-left, detached from the tally.

#### `hero_pair`: Hero pair LANDS -> THROUGH (12 -> 6)
- Crop: [top_hud__hero_pair.png](brief_crops/top_hud__hero_pair.png) (from p1)
- **Design goal:** THE number: how much lands and how much gets through to you this END TURN. The one raw-digit exception (3.22). Read in under 0.3 s, first in the HUD.
- **Look and feel:** Anton 58 with ink keyline: LANDS in white, THROUGH in harm red (or gain green at 0), joined by a bold arrow; labels small above.
- **Current problems:** The yellow arrow is plan yellow (no plan here) and touches the 12; the digits have a 2.5 px stroke that is thinner than the sticker keyline rule (5 px); labels LANDS/THROUGH are left-aligned to different x than the digits; the pair floats in the middle of the box with no relation to the tally rows below.

#### `hero_nowords_proxy`: Hero pair nowords proxy (12 -> 6 as bars)
- Crop: [top_hud__hero_nowords_proxy.png](brief_crops/top_hud__hero_nowords_proxy.png) (from nw)
- **Design goal:** With words off, THE number must still read: lands vs through, and that through is the cost.
- **Look and feel:** A tally form of the pair (grouped segments in the hero size, white lands, red through) on the same baseline and arrow.
- **Current problems:** L2.text replaces the digits with bars whose width scales with n: a small white square for 12 and a smaller red bar for 6, so the hero becomes the quietest thing in the bill; the plan-yellow arrow remains and is now the loudest mark.

#### `eq_row`: Equation row (RAW - SHOT - BRACE - RIDER = LANDS)
- Crop: [top_hud__eq_row.png](brief_crops/top_hud__eq_row.png) (from p1)
- **Design goal:** Show how LANDS is built: raw hit minus shot down minus braced minus rider = lands; every count as a tally. Read on demand, left to right.
- **Look and feel:** Inset terminal strip, labels above each group, operators between, tallies in the group's token colour.
- **Current problems:** Groups are spaced by text width, so the operators float at uneven gaps; RAW tally (16) wraps into 4 groups and dominates; the strip has its own outline inside the bill box outline (double frame).

#### `eq_labels`: Equation and split labels (mono 16)
- Crop: [top_hud__eq_labels.png](brief_crops/top_hud__eq_labels.png) (from p1)
- **Design goal:** Name each group.
- **Look and feel:** Share Tech Mono caps +8 percent tracking, TEXT_MID, at the 18 px terminal floor.
- **Current problems:** 16 px is below the bible's 18 px terminal floor; labels sit 14 px above the tallies but are left-aligned to the group start, which drifts from the operator positions; SOAK and YOU labels change colour (orange, red) while the others stay grey.

#### `tally_segments`: HUD tally segments (groups of 5)
- Crop: [top_hud__tally_segments.png](brief_crops/top_hud__tally_segments.png) (from p1)
- **Design goal:** Make every count countable without digits (groups of 5).
- **Look and feel:** Rounded segments r 3 with ink, token colour, 10 px gap per group of 5; one size per row.
- **Current problems:** Segment sizes differ per row (9 x 18, 11 x 18, 11 x 14, 13 x 22) with no system; group gap 10 px is barely larger than the 3-4 px segment gap at 320 px; red RAW and red LANDS use the same red, so 'raw' looks like damage taken.

#### `operators`: Operators (-, =, +)
- Crop: [top_hud__operators.png](brief_crops/top_hud__operators.png) (from p1)
- **Design goal:** Make the bill read as an equation.
- **Look and feel:** Anton operators sized to the tally height, centred on the tally baseline, consistent gap.
- **Current problems:** Minus signs are tiny 6 px bars that read as an empty socket; the = sits lower than the tallies; operators are white while labels are grey, so they jump forward.

#### `empty_socket`: Empty socket (zero-count group)
- Crop: [top_hud__empty_socket.png](brief_crops/top_hud__empty_socket.png) (from p1)
- **Design goal:** Show a group that is zero (BRACE 0, RIDER 0) without a digit.
- **Look and feel:** One dim outlined slot, clearly 'none'.
- **Current problems:** Empty sockets (9 x 18 dark outlined) look the same as a minus sign next to them; the eye reads '- [ ]' as noise.

#### `split_row`: Split row (ABSORBED + SOAK -> slice + YOU -> HP)
- Crop: [top_hud__split_row.png](brief_crops/top_hud__split_row.png) (from p1)
- **Design goal:** Show where LANDS goes: absorbed by slices, soaked by marked slices, through to you.
- **Look and feel:** Inset strip with three destinations, each with a small route arrow and destination icon, tallies in token colours.
- **Current problems:** Route arrows and mini destination icons (a green capsule for slice, a green pip for HP) sit above the labels in a second line, so the row has 3 stacked baselines; YOU in red here vs YOU in grey at the top of the box; '+' operators float under the labels.

#### `route_arrows`: Route arrows with destination pips
- Crop: [top_hud__route_arrows.png](brief_crops/top_hud__route_arrows.png) (from p1)
- **Design goal:** Say 'soak goes to a slice', 'through goes to your HP'.
- **Look and feel:** Bold arrows in the route colour with a clear destination icon (slice wedge, HP pip) the same as on the board.
- **Current problems:** The slice destination is a green pill that matches nothing on the board; the HP destination is a green square; arrows are 22 px with heavy ink, louder than their labels.

#### `next_row`: NEXT ghost row
- Crop: [top_hud__next_row.png](brief_crops/top_hud__next_row.png) (from p1)
- **Design goal:** Show next turn's bill if nothing more is played (taken 10, absorbed 2, slice 1), as a ghost.
- **Look and feel:** Same tally grammar at 50 percent value, clearly secondary, aligned to the columns above.
- **Current problems:** 120 alpha ghost of red reads as dark maroon blocks; the NEXT row is not column-aligned with the split row; no label for which group is which (red / cyan / green only).

#### `plan_pencil_underline`: Plan pencil underline under YOU (p2)
- Crop: [top_hud__plan_pencil_underline.png](brief_crops/top_hud__plan_pencil_underline.png) (from p2)
- **Design goal:** While a plan is previewed, mark the HP result as the plan's (bible 3.1: yellow pencil underline).
- **Look and feel:** Grease pencil: plan yellow 7 px with ink edge, wax texture, slightly wobbly.
- **Current problems:** A clean straight 6 px line, not wax pencil; it runs under the tally into the empty space, longer than the HP it underlines.

#### `best_line_tag`: BEST LINE tag (p2/p3)
- Crop: [top_hud__best_line_tag.png](brief_crops/top_hud__best_line_tag.png) (from p2)
- **Design goal:** Say the previewed plan is the planner's best (HP-first).
- **Look and feel:** Small mono tag in plan yellow, right-aligned in the box header line.
- **Current problems:** Mono 16 floating with no container in the top-right of the box; it is far from the plan it names (option chips below).

#### `without_twist_row`: WITHOUT TWIST comparison (p2/p3)
- Crop: [top_hud__without_twist_row.png](brief_crops/top_hud__without_twist_row.png) (from p2)
- **Design goal:** Show the Twist's payoff: next turn 2 through without it vs 1 with it.
- **Look and feel:** One line in the NEXT row: twist glyph, words, hollow pips > solid pips.
- **Current problems:** Hollow red squares vs solid red squares with a '>' read as 'greater than', meaning the opposite (2 > 1 is the bad case); mixed into the ghost NEXT row at full value.

#### `option_chips`: Option chip frame and layout (two states, p2)
- Crop: [top_hud__option_chips.png](brief_crops/top_hud__option_chips.png) (from p2)
- **Design goal:** Compare plans as a list: one chip per plan, selected = best. This entry is the chip frame, its two states and the column layout inside it; glyphs, label, bar and pair are separate elements.
- **Look and feel:** Stacked terminal chips in the shared plate kit; selected with plan-yellow edge; fixed columns so glyphs, label, bar and pair align across chips.
- **Current problems:** Grey frame (unselected) is a fourth panel style; contents float at fixed x leaving a dead middle; three chips push objectives and RAM down into the room focus hull.

#### `option_plan_glyphs`: Option chip plan glyph sequence (p2)
- Crop: [top_hud__option_plan_glyphs.png](brief_crops/top_hud__option_plan_glyphs.png) (from p2)
- **Design goal:** Read the plan as a short sentence of card glyphs in play order.
- **Look and feel:** 20 px glyphs from the card icon set, one colour family (plan yellow or white) with consistent spacing; soak and refund shown with the shared tokens or omitted.
- **Current problems:** Per-card colours (cyan, cream, yellow) plus orange soak chevrons and a refund burst with pip make an unreadable string; glyphs at 20 px with thin strokes.

#### `option_name_label`: Option chip name label (TRIGGER ONLY ... BEST: ALL THREE)
- Crop: [top_hud__option_name_label.png](brief_crops/top_hud__option_name_label.png) (from p2)
- **Design goal:** Name each plan.
- **Look and feel:** Share Tech Mono 18, TEXT_MID, BEST in plan yellow, aligned to one column.
- **Current problems:** Mono 16 below the floor; the BEST prefix duplicates the BEST LINE tag and the selected edge.

#### `option_outcome_bar`: Option chip outcome bar (p2)
- Crop: [top_hud__option_outcome_bar.png](brief_crops/top_hud__option_outcome_bar.png) (from p2)
- **Design goal:** Show where each plan's LANDS goes (the split) as one compact tally.
- **Look and feel:** Same tally segments and token colours as split_row, starting at a fixed column.
- **Current problems:** Bars start at a fixed x leaving a dead middle; mixes red, orange and cyan segments with no group gaps, so counts are hard to compare between chips.

#### `option_pair`: Option chip lands > through pair ('6 > 1')
- Crop: [top_hud__option_pair.png](brief_crops/top_hud__option_pair.png) (from p2)
- **Design goal:** Give each plan its lands -> through result.
- **Look and feel:** Anton with ink, the same arrow as the hero pair, smaller.
- **Current problems:** Uses '>' where the hero uses an arrow, reading as greater-than; white and red not differentiated as the hero does.

#### `chain_strip`: Resolve chain strip frame and layout (p3)
- Crop: [top_hud__chain_strip.png](brief_crops/top_hud__chain_strip.png) (from p3)
- **Design goal:** Replay END TURN order (Twist, Trigger, Brace, guns, lands, rings step) with results, as one numbered list. This entry is the frame and row layout; discs, glyphs, names and results are separate elements.
- **Look and feel:** Shared terminal plate kit, fixed row height and columns.
- **Current problems:** Grey frame is a fourth panel style; rows are not column-aligned with the bill above; pushes objectives/RAM into the room focus hull.

#### `chain_step_discs`: Chain step number discs (p3)
- Crop: [top_hud__chain_step_discs.png](brief_crops/top_hud__chain_step_discs.png) (from p3)
- **Design goal:** Give the replay order.
- **Look and feel:** Small mono numbers or the pip language, not a new disc style.
- **Current problems:** 22 px white-ringed number discs are a fifth disc style on the screen and the loudest white in the strip.

#### `chain_step_glyphs`: Chain step glyph set (twist, trigger, brace, lightning, red skull, down arrow; p3)
- Crop: [top_hud__chain_step_glyphs.png](brief_crops/top_hud__chain_step_glyphs.png) (from p3)
- **Design goal:** Identify each step by picture.
- **Look and feel:** Glyphs reused from the card and board vocabulary (card icons for cards, tracer mark for guns, landing chevron for lands, schedule chevron for rings step); one colour family.
- **Current problems:** The red skull for LANDS reuses the Adjuster boss silhouette for "units land"; the lightning for GUNS appears nowhere else on screen; the down arrow reads as download.

#### `chain_step_names`: Chain step name labels (p3)
- Crop: [top_hud__chain_step_names.png](brief_crops/top_hud__chain_step_names.png) (from p3)
- **Design goal:** Name each step.
- **Look and feel:** Mono 18 TEXT_MID, one colour; colour lives in the glyph only.
- **Current problems:** Six step-name colours (yellow, yellow, cream, cyan, red, orange) make the strip read as a legend; mono 16.

#### `chain_result_tallies`: Chain result tallies (p3)
- Crop: [top_hud__chain_result_tallies.png](brief_crops/top_hud__chain_result_tallies.png) (from p3)
- **Design goal:** Show each step's count result.
- **Look and feel:** The bill tally segments and colours, column-aligned.
- **Current problems:** Tallies start at different x per row; the LANDS row mixes red and cream groups with prose between.

#### `chain_result_prose`: Chain result prose (p3)
- Crop: [top_hud__chain_result_prose.png](brief_crops/top_hud__chain_result_prose.png) (from p3)
- **Design goal:** Short words for results that are not counts (fixed text).
- **Look and feel:** Mono 18 TEXT_MID after the tally column, never interleaved with tallies.
- **Current problems:** Prose and tallies mix on one line ('brace' between tally groups); mono 16.

#### `trig_groups`: TRIG group in the equation (Trigger-removed pips, p2)
- Crop: [top_hud__trig_groups.png](brief_crops/top_hud__trig_groups.png) (from p2)
- **Design goal:** Show the pips the Trigger removes (TRIG) as part of building LANDS.
- **Look and feel:** Same group grammar, plan-yellow tally (the plan removed them).
- **Current problems:** TRIG correctly in plan colour but its 5-tally matches the RAW tally size, so it reads as raw damage in yellow.

#### `trig_lands_group`: TRIG LANDS group (Trigger hits landing on the tower) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Show Trigger pierces that reach the tower as a separate group in the bill.
- **Look and feel:** Same group grammar in PENCIL_THREAT, matching trigger_tower_hit on the board.
- **Current problems:** Never reached in this state; code reuses the RAW red tally, so it would be indistinguishable from raw enemy damage.

### 4.5 Objectives and resources (`objectives`, 13 elements)

Contact sheet: `brief_crops/contact_objectives.jpg`

#### `objectives_frame`: Objectives panel frame
- Crop: [objectives__objectives_frame.png](brief_crops/objectives__objectives_frame.png) (from p1)
- **Design goal:** Contain the star objectives as one row.
- **Look and feel:** Terminal strip in the shared HUD plate language.
- **Current problems:** Grey (110,120,140) 2 px outline at r 8 is a third panel style (not cyan terminal, not white bill); the row is 44 px tall with 16 px text, lots of dead space at the right.

#### `star_glyph`: Star glyphs (open / met / failed)
- Crop: [objectives__star_glyph.png](brief_crops/objectives__star_glyph.png) (from p1)
- **Design goal:** Read each objective's state: open (outline), met (gold fill), failed (dark with red slash).
- **Look and feel:** Five-point star, white outline when open, gold fill when met, ink keyline in all states.
- **Current problems:** Open star is a 2.2 px white outline with no ink, which looks disabled; all four stars are the same size, so WIN (its own reward) is not distinguished; star points are sharp polygons that alias.

#### `win_label`: WIN objective label
- Crop: [objectives__win_label.png](brief_crops/objectives__win_label.png) (from p1)
- **Design goal:** Read the win itself is a star with its own reward.
- **Look and feel:** Gold label next to its star, slightly larger than the challenges.
- **Current problems:** Gold mono 16 is the same style as the challenges except colour; 'WIN' alone is cryptic next to 'SLICES KEPT'.

#### `challenge_labels`: Challenge labels (SLICES KEPT / KILL ADJUSTER / TRACE LOW)
- Crop: [objectives__challenge_labels.png](brief_crops/objectives__challenge_labels.png) (from p1)
- **Design goal:** Name the three drawn challenges.
- **Look and feel:** Mono caps white, even column pitch.
- **Current problems:** Columns are on a fixed 238 px pitch, so short labels leave gaps and KILL ADJUSTER's tally crowds TRACE LOW; mono 16 below the 18 floor.

#### `challenge_tallies`: Challenge progress tallies
- Crop: [objectives__challenge_tallies.png](brief_crops/objectives__challenge_tallies.png) (from p1)
- **Design goal:** Show progress: Adjuster HP left (10, gold), Trace (3, violet); SLICES KEPT has none.
- **Look and feel:** Mini tallies in the same colour as the board element they track, groups of 5.
- **Current problems:** Tally pips are 4-6 px wide and 12 tall, unreadable at 320 px; Adjuster HP shown gold here but cream on the board; SLICES KEPT has no progress mark at all although 6 slice pips are lost this turn.

#### `challenge_trigger_hits`: TRIGGER HITS challenge - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Name and track the card challenge (Trigger hits).
- **Look and feel:** Same label/tally grammar as the other challenges, tally in the colour of what it counts, never plan yellow.
- **Current problems:** Not drawn this run; stars_row would draw it with a plan-yellow mini tally, breaking the PENCIL_PLAN rule.

#### `ram_trace_frame`: RAM / TRACE terminal frame
- Crop: [objectives__ram_trace_frame.png](brief_crops/objectives__ram_trace_frame.png) (from p1)
- **Design goal:** Contain the resources (bible 3.22 bill item 5).
- **Look and feel:** Terminal plate, cyan edge, shared language.
- **Current problems:** It is the only true terminal plate in the column besides the header; its 48 px height crops the 26 px pips with little margin.

#### `ram_trace_labels`: RAM and TRACE row labels
- Crop: [objectives__ram_trace_labels.png](brief_crops/objectives__ram_trace_labels.png) (from p1)
- **Design goal:** Name the two resources.
- **Look and feel:** Share Tech Mono 18 TEXT_MID, aligned to the pip rows, same style as the bill labels.
- **Current problems:** Mono 16 CRT_TXT below the floor; label-to-pip gap differs between RAM and TRACE; ENDS = HEAT label uses another colour.

#### `ram_pips`: RAM pips (4 cyan)
- Crop: [objectives__ram_pips.png](brief_crops/objectives__ram_pips.png) (from p1)
- **Design goal:** Read RAM left to spend (4 of 4) and, in p2, the refund pip.
- **Look and feel:** Terminal pips, cyan lit, dark socket when spent, square-ish r 4; the same pip as the card cost.
- **Current problems:** Pips are 28 x 26, larger than any other pip in the HUD; spent state (dark navy) has little contrast; no link to card cost badges (yellow discs), so cost and RAM do not read as one currency.

#### `trace_pips`: TRACE pips (6, 3 lit)
- Crop: [objectives__trace_pips.png](brief_crops/objectives__trace_pips.png) (from p1)
- **Design goal:** Read Trace level (3 of 6) and the cap.
- **Look and feel:** Violet pips, unlit as dark violet sockets, cap pip hatched.
- **Current problems:** Violet #A03CFF is close to the rider lavender and the Jammer kind colour; unlit sockets are mid-violet outlines that look half lit.

#### `trace_cap_hatch`: Trace cap hatch (last pip)
- Crop: [objectives__trace_cap_hatch.png](brief_crops/objectives__trace_cap_hatch.png) (from p1)
- **Design goal:** Read 'at this pip, lockdown/limit'.
- **Look and feel:** Clear hazard hatch or lock glyph on the cap pip.
- **Current problems:** White diagonal hatch at 110 alpha reads as a glitch or a broken pip.

#### `ends_heat`: ENDS = HEAT label and pips
- Crop: [objectives__ends_heat.png](brief_crops/objectives__ends_heat.png) (from p1)
- **Design goal:** Read 'Trace left when the fight ends becomes Heat' and the forecast (2).
- **Look and feel:** Heat colour (bible 2.8 amber/orange band colours), label and pips in one colour.
- **Current problems:** Label is amber but the pips are gold (boss colour); 'ENDS = HEAT' is cryptic; the forecast pips are 11 x 18, another pip size.

#### `ram_refund_pop`: RAM refund pop in the RAM row (p2)
- Crop: [objectives__ram_refund_pop.png](brief_crops/objectives__ram_refund_pop.png) (from p2)
- **Design goal:** Show the +1 RAM refund from the Trigger kill in the resource row.
- **Look and feel:** The refunded RAM pip with a plus and a short burst, same as on the board.
- **Current problems:** The gold 12-point burst is bigger than the pip and covers its neighbour; gold reads as boss/reward rather than RAM.

### 4.6 Card hand (`cards`, 16 elements)

Contact sheet: `brief_crops/contact_cards.jpg`

#### `hand_fan`: Hand fan and spacing
- Crop: [cards__hand_fan.png](brief_crops/cards__hand_fan.png) (from p1)
- **Design goal:** Read the 4 playable cards, their costs and names in one sweep; the hand must sit under the room, not on top of the board.
- **Look and feel:** Vinyl sticker cards in a shallow fan, even overlap, cost and title always visible, consistent tilt.
- **Current problems:** Cards (200 px wide on a 140 px step) overlap by about 60 px so the right edge of each art band is cut (the 'x3' on SPIN 3 is clipped by TRIGGER); the fan tilts are only 3.5 deg, reading as misaligned rather than fanned; the hand covers the cutaway room's lobby and runs under SEND IT.

#### `card_frame`: Card frame (die-cut sticker)
- Crop: [cards__card_frame.png](brief_crops/cards__card_frame.png) (from p1)
- **Design goal:** Read 'a card you can play' (sticker media, bible 3.18).
- **Look and feel:** Bible 3.18 sticker card: white die-cut border, ink keyline, dark body, r 16 outer / r 10 inner, drop shadow.
- **Current problems:** White border is 9 px with a 2 px ink edge, thinner than the sticker die-cut rule; the shadow offset (4, 8) differs from the stickers' (5, 9); body corners are r 10 while art band corners are square.

#### `card_header_strip`: Card header strip (dark band above the art)
- Crop: [cards__card_header_strip.png](brief_crops/cards__card_header_strip.png) (from p1)
- **Design goal:** Set the card's top rhythm and hold the cost badge and loud tab.
- **Look and feel:** A strip whose height and content survive the fan overlap: cost and loud tab both inside the visible part.
- **Current problems:** The ~34 px dark band carries the cost badge (hanging off the corner) and loud tab; the 60 px fan overlap cuts into it, so the loud tab hides under the next card at rest.

#### `cost_badge`: Cost badge (yellow disc)
- Crop: [cards__cost_badge.png](brief_crops/cards__cost_badge.png) (from p1)
- **Design goal:** Read the RAM cost (0 or 1) before anything else on the card.
- **Look and feel:** Badge in the RAM currency language (cyan pip), number in Anton with ink.
- **Current problems:** Yellow disc is plan yellow and SEND IT yellow; it hangs off the card corner and overlaps the neighbour; cost is RAM but does not look like RAM.

#### `art_band`: Card art band (family colour + scanlines)
- Crop: [cards__art_band.png](brief_crops/cards__art_band.png) (from p1)
- **Design goal:** Read the card family (TOWER cyan / WAVE orange) at a glance.
- **Look and feel:** Family colour band with CRT scanlines, mid value, icon on top.
- **Current problems:** WAVE orange band uses schedule orange (fine meaning) but at the same value as the bezel cell, so cards and bezel compete; scanlines are 1 px at 4 px pitch and moire when the card is rotated.

#### `card_icon`: Card art icon (glyph)
- Crop: [cards__card_icon.png](brief_crops/cards__card_icon.png) (from p1)
- **Design goal:** Recognise the card by picture (Brace, Spin, Trigger, Twist...).
- **Look and feel:** 70 px bible glyph, white, ink keyline, centred in the band.
- **Current problems:** The Brace card icon (bracket with diamond) shares a glyph with the slice plate's disc, but the plate's real silhouette (clamp with rivets) is not on the card, so card and effect do not match; Trigger crosshair reads as 'aim', fine, but the Twist icon is the generic refresh symbol; icons are pushed left when a multiplier is present.

#### `card_icon_set`: Card icon set (all 11 cards) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Every card in the deck (Nudge, Spin2, Spin3, Brace, Firewall, Pull, Shove, Twist, Hold, Trigger, Strike) has an icon from one family.
- **Look and feel:** One glyph family, one weight, one grid.
- **Current problems:** Only 4 cards are in hand; Nudge/Spin2/Spin3 share one glyph with a multiplier; Pull, Hold, Strike and Firewall glyphs are ad-hoc PIL shapes (cv_lib/e8lib) not from the bible set.

#### `card_multiplier`: Card multiplier (x3 on SPIN 3)
- Crop: [cards__card_multiplier.png](brief_crops/cards__card_multiplier.png) (from p1)
- **Design goal:** Read how many steps the Spin turns.
- **Look and feel:** Anton number with ink, part of the icon lockup, never clipped.
- **Current problems:** x3 is clipped by the next card in the fan; it duplicates the '3' in the title SPIN 3.

#### `card_title`: Card title (Anton 28)
- Crop: [cards__card_title.png](brief_crops/cards__card_title.png) (from p1)
- **Design goal:** Read the card name.
- **Look and feel:** Anton white with ink, left-aligned, one size.
- **Current problems:** No keyline on white Anton over the dark body; titles nearly touch the type band below; long names (FIREWALL) would not fit the 158 px body at 28 px.

#### `type_band`: Card type tag (TOWER / WAVE)
- Crop: [cards__type_band.png](brief_crops/cards__type_band.png) (from p1)
- **Design goal:** Read the family in words.
- **Look and feel:** Family-colour strip with ink mono caps.
- **Current problems:** Duplicates the art band's family colour; mono 16 right-aligned in a full-width strip leaves the left empty; the TOWER strip cyan equals the RAM and terminal cyan.

#### `rules_text`: Card rules text (Plex 16)
- Crop: [cards__rules_text.png](brief_crops/cards__rules_text.png) (from p1)
- **Design goal:** Read the effect in a few words (fixed text).
- **Look and feel:** IBM Plex Sans Condensed, 16 px resting (720p 10 px exception), keyword in Medium.
- **Current problems:** Text runs to the card edge with 8 px margin and is clipped by the next card ('Turn one ring 1' touches the edge); no keyword emphasis.

#### `loud_tab`: Loud / Trace tab (red eye +N)
- Crop: [cards__loud_tab.png](brief_crops/cards__loud_tab.png) (from p2)
- **Design goal:** Read that playing this card adds Trace (+1).
- **Look and feel:** Small tab in the Trace colour family with an eye glyph and +N.
- **Current problems:** Red reads as harm, but this is Trace (violet in the HUD), so the card's cost does not match the TRACE pips it fills; on resting cards the tab is hidden under the next card (p1), showing only a red pill.

#### `loud_tab_resting`: Loud tab on a resting card (p1)
- Crop: [cards__loud_tab_resting.png](brief_crops/cards__loud_tab_resting.png) (from p1)
- **Design goal:** Same as loud_tab, at rest.
- **Look and feel:** Tab placed where the fan never covers it.
- **Current problems:** On TRIGGER at rest only the eye shows; the +1 is under TWIST.

#### `card_hover_grow`: Hovered card (grown, curl, p2)
- Crop: [cards__card_hover_grow.png](brief_crops/cards__card_hover_grow.png) (from p2)
- **Design goal:** Show the focused card large, readable, lifted.
- **Look and feel:** Card at 1.22x, lifted, peel-back corner curl (2.10 focus), shadow deeper.
- **Current problems:** Curl is a flat grey triangle; the grown card overlaps the option chips' area visually and its shadow is the same as the resting cards'.

#### `played_liner`: Played card liner (p3)
- Crop: [cards__played_liner.png](brief_crops/cards__played_liner.png) (from p3)
- **Design goal:** Show which cards were played this turn, as empty slots.
- **Look and feel:** Outline liner with the ghost glyph and PLAYED, low value.
- **Current problems:** Liners are transparent outlines with a grey glyph and PLAYED in mono 17, barely legible over the backdrop; on room_bio_bare they sit over the lit lobby, so the room shows through busy; three liners take more space than the one live card.

#### `cards_nowords`: Cards in nowords (blank cost, no title, type or rules)
- Crop: [cards__cards_nowords.png](brief_crops/cards__cards_nowords.png) (from nw)
- **Design goal:** With words off, every card must still read by art band and icon, and show its cost.
- **Look and feel:** Cost as RAM pips in the badge (not a digit), family by band, identity by icon; title area left quiet, not an empty box.
- **Current problems:** Blank yellow cost discs carry no cost; the empty title/type/rules areas read as unfinished; SPIN 3 loses its multiplier so it is identical to any Spin.

### 4.7 Actions and identity (`actions`, 20 elements)

Contact sheet: `brief_crops/contact_actions.jpg`

#### `send_it`: SEND IT sticker
- Crop: [actions__send_it.png](brief_crops/actions__send_it.png) (from p1)
- **Design goal:** The one committing verb; findable in under 0.5 s, bottom right.
- **Look and feel:** Vinyl sticker, die-cut white border, Anton with ink, tilt -3; colour per 3.22 (yellow on this screen) with the sticker gradient.
- **Current problems:** Flat plan yellow, not the vinyl gradient; it is cropped by the screen edge on the right and bottom; the die-cut border is cut off at the bottom; the hint text is drawn underneath it and is hidden.

#### `undo_chip`: UNDO [Z] chip
- Crop: [actions__undo_chip.png](brief_crops/actions__undo_chip.png) (from p1)
- **Design goal:** Offer undo; tertiary; show locked state with a grey tick (3.1).
- **Look and feel:** Terminal chip, mono 18, cyan edge.
- **Current problems:** Floats 60 px above SEND IT with no relation to it; same width as nothing else; the key hint [Z] is the same size as the word.

#### `nameplate`: CELL-9 // BREAKER nameplate sticker
- Crop: [actions__nameplate.png](brief_crops/actions__nameplate.png) (from p1)
- **Design goal:** Identify the player cell and class (3.1: bottom left).
- **Look and feel:** Cyan vinyl sticker (3.22), Anton with ink, tilt 2.
- **Current problems:** Bible 3.1 places it above the RAM readout; here it is alone in the bottom-left corner over the board's outer arcs; cyan sticker is the same cyan as terminals, so it reads as a panel.

#### `sticker_material`: Shared vinyl sticker material (die-cut, plate, ink, shadow)
- Crop: [actions__sticker_material.png](brief_crops/actions__sticker_material.png) (from p1)
- **Design goal:** One sticker material for CELL-9, SEND IT and the cards (3.18, 1.2 media split).
- **Look and feel:** White die-cut border 0.14 x type size (max 12 px), coloured plate with 3 px ink edge, r 16/10, one drop shadow (shadow_paste k 0.5, blur 8, one offset), vinyl gradient where the bible asks.
- **Current problems:** Shadow offsets differ (stickers 5,9 vs cards 4,8); card border 9 px vs sticker 12 px; flat fills where the vinyl gradient is required; no element owned the material until now.

#### `stickers_nowords`: Stickers and UNDO in nowords (blank plates)
- Crop: [actions__stickers_nowords.png](brief_crops/actions__stickers_nowords.png) (from nw)
- **Design goal:** With words off, the verb and the identity still read.
- **Look and feel:** SEND IT keeps a non-word verb mark (go glyph / arrow-through-ring from the set), CELL-9 a class emblem, UNDO an undo glyph.
- **Current problems:** CELL-9 and SEND IT become blank colour plates and UNDO an empty terminal: the committing verb has no non-word form.

#### `card_targeting`: Card targeting and keyboard target focus - LATENT
- Crop: LATENT (no crop)
- **Design goal:** While a card is held or aimed, show valid targets (Brace -> slice, Trigger / Pull / Shove -> unit, Twist -> ring, Spin -> tower) and the Tab-cycle focus (GDD 9.2 explicit targeting, 9.5 Tab cycle target).
- **Look and feel:** 2.10 focus language (lime corner brackets) on the focused target, a quiet valid-target cue on the rest; never plan yellow (that is the plan, after commit).
- **Current problems:** Not drawn by the generator; no rule exists for target cues on slices, unit cells or ring tags, which all already carry dense marks.

#### `bottom_hint`: Bottom hint text (> turn_resolve.exe)
- Crop: [actions__bottom_hint.png](brief_crops/actions__bottom_hint.png) (from p1)
- **Design goal:** Flavour line under SEND IT (terminal command).
- **Look and feel:** Mono, TEXT_MID, fully visible below or beside SEND IT, or removed.
- **Current problems:** Drawn at y 1070 under the SEND IT sticker and is mostly covered; mono 16 below the floor.

#### `hover_tag`: Hover tag (p2b CRT tag)
- Crop: [actions__hover_tag.png](brief_crops/actions__hover_tag.png) (from p2b)
- **Design goal:** On unit hover, state the unit's facts in words and digits (the only place digits show): kind, width, HP, hit, growth, landing, cost to you.
- **Look and feel:** One CRT tag (3.22), terminal plate in plan yellow edge, Plex 20, two lines, near the hovered unit.
- **Current problems:** Pinned to the screen's top-left corner, 500 px from the hovered unit; Plex 18 below the 20 body floor; long run-on lines (70+ chars, bible 36-60); two text colours.

#### `hover_path`: Hover path (yellow pencil with arrowhead, p2b)
- Crop: [actions__hover_path.png](brief_crops/actions__hover_path.png) (from p2b)
- **Design goal:** Show the hovered unit's route through the cell centres to the slices it hits.
- **Look and feel:** Grease pencil, plan yellow 7 px with ink edge (3.22), wax texture, one arrowhead.
- **Current problems:** Clean vector line, not wax; its arrowhead is a large filled triangle; the dashed yellow outline on the hovered cell adds a second yellow line beside it.

#### `hover_slice_highlight`: Hover slice highlight (yellow arcs on hit slices, p2b)
- Crop: [actions__hover_slice_highlight.png](brief_crops/actions__hover_slice_highlight.png) (from p2b)
- **Design goal:** Mark which slices the hovered unit hits.
- **Look and feel:** Plan-yellow arc on the slice rim, replacing (not adding to) the threat trim while hovering.
- **Current problems:** Yellow arcs are added on top of the red trim, HP ring and slice bars, a sixth parallel arc.

#### `hover_focus_dim`: Hover focus dimming: unit screen grade (p2b)
- Crop: [actions__hover_focus_dim.png](brief_crops/actions__hover_focus_dim.png) (from p2b)
- **Design goal:** Make the hovered unit the only one in focus (3.22: others at 38 percent). This entry is the unit-screen darkening; the overlay-mark dim is hover_dim_overlay.
- **Look and feel:** Non-hovered unit screens graded down uniformly, the same ghost treatment as consumed/killed units.
- **Current problems:** grade_units darkens non-hovered unit screens to 50 percent while overlays use 36 percent: two dims in one state; bezel, slices, trim and schedule stay full, so focus gain is small; neither value is the bible 38 percent.

#### `hover_dim_overlay`: Hover focus dimming: overlay marks and removed arcs (p2b)
- Crop: [actions__hover_dim_overlay.png](brief_crops/actions__hover_dim_overlay.png) (from p2b)
- **Design goal:** Quiet the non-hovered units' chevrons, HP and arcs so the hovered unit's marks lead.
- **Look and feel:** One dim value for all non-hovered overlay marks and landing arcs (dimmed, not removed, so the board does not change shape on hover).
- **Current problems:** Overlay marks drop to 36 percent alpha but the non-hovered landing arcs are removed outright, so the outer rings change shape on hover.

#### `hovered_cell_outline`: Hovered cell outline (yellow 5 px, p2b)
- Crop: [actions__hovered_cell_outline.png](brief_crops/actions__hovered_cell_outline.png) (from p2b)
- **Design goal:** Mark the hovered unit.
- **Look and feel:** Focus language from 2.10 (lime corner brackets) or a plan-yellow outline, one only.
- **Current problems:** Yellow dashed outline duplicates the pencil path colour; bible focus is lime brackets, never yellow.

#### `trigger_path`: Trigger path (yellow pencil + X, p2)
- Crop: [actions__trigger_path.png](brief_crops/actions__trigger_path.png) (from p2)
- **Design goal:** Show the Trigger's pierce: from the triggered unit inward, X on each unit hit.
- **Look and feel:** Grease pencil plan yellow with ink, X in pencil at each pierced unit (3.22).
- **Current problems:** Straight clean line with a yellow X that looks typed, not drawn; the X sits on the cell edge; the line is short (70 px) and hides behind chevrons.

#### `twist_badge`: Twist badge on the ring tag (p2)
- Crop: [actions__twist_badge.png](brief_crops/actions__twist_badge.png) (from p2)
- **Design goal:** Show the played Twist: ring +1 turns one extra sector clockwise.
- **Look and feel:** Plan-yellow twist disc with direction chevrons, attached to the ring tag.
- **Current problems:** 34 px disc is larger than the ring tag it attaches to; direction chevrons are thin; a third yellow mark style in the plan language.

#### `refund_burst`: Refund placement on the board (p2/p3)
- Crop: [actions__refund_burst.png](brief_crops/actions__refund_burst.png) (from p2)
- **Design goal:** Show the Trigger kill pays +1 RAM at the killed unit, with the REFUND tag. The token itself is refund_token.
- **Look and feel:** refund_token beside the killed unit's token (not on the cell edge), mono 18 tag.
- **Current problems:** Burst sits on the dead cell edge over the trigger path and covers the killed Packet's token; tag mono 16; a second mini burst inside ram_pip_pop.

#### `refund_token`: Refund token (RAM pip with plus, burst) - shared
- Crop: [actions__refund_token.png](brief_crops/actions__refund_token.png) (from p2)
- **Design goal:** One token meaning '+1 RAM refunded', drawn the same in its four places: board, RAM row, option chips, chain strip.
- **Look and feel:** The cyan RAM pip with a plus and a small cyan (not gold) burst, one design scaled by a fixed ladder.
- **Current problems:** Gold 12-point burst plus cyan pip drawn at four sizes in four places with no owner; gold reads boss/reward, not RAM; in the RAM row the burst covers the neighbouring pip.

#### `resolve_fire_lines`: Resolve fire lines (p3 cyan dashed)
- Crop: [actions__resolve_fire_lines.png](brief_crops/actions__resolve_fire_lines.png) (from p3)
- **Design goal:** On resolve, show the guns that fired.
- **Look and feel:** Same tracer as decide state, lower value, or removed in favour of the chain strip.
- **Current problems:** A thinner 2.4 px dash variant of the tracer (a second tracer style); lines end in nothing.

#### `no_target_tag`: NO TARGET tag (idle gun) - LATENT
- Crop: LATENT (no crop)
- **Design goal:** Say an idle gun has no target (3.22 default fire).
- **Look and feel:** Small terminal tag on the gun's sector, cyan.
- **Current problems:** Not in this state (every gun has a target); code puts a 104 px tag across the ring-0 cell, which would cover a unit cell.

#### `nowords_variant`: Nowords variant rule (screen-wide)
- Crop: [actions__nowords_variant.png](brief_crops/actions__nowords_variant.png) (from nw)
- **Design goal:** Own the nowords behaviour as one rule: every element must read by shape with words off (3.9), and no words may remain hidden in textures.
- **Look and feel:** A designed non-word form per word-carrying element (hero, digits, ring tags, cards, stickers, labels), listed in one table; texture text removed; L2.text proxy bars retired.
- **Current problems:** Nowords was spread over many elements and owned by none: generic L2.text bars replace digits and words, tags and stickers go blank, and words survive inside slice and unit screen textures.

## 5. Completeness audit (nothing omitted)

Method: (a) every drawing call in the E10 generator that reaches any of the five plates was listed from the source and mapped to element ids; (b) every element must map back to a call; (c) every visible element has a crop and every crop has an element; (d) all five plate states were scanned for state-only elements (p2 Brace, soak, option chips, refund, twist; p2b hover tag, path, dim; p3 chain strip, liners, fire lines; nowords). The build script checks (a)-(c) on every run.

| Source draw call | Element ids |
|---|---|
| cv_board.render_board: back plate disc | `board_backplate` |
| cv_board.render_board: ring_base (brushed bezel) | `bezel_ring` |
| cv_board.ring_base: orange rim glows R0+1.5 / R1-1.5 + cos(th-315) light | `bezel_rim_lines` |
| cv_board.render_board: render_slice x6 (frame, screen, glyph) | `slice_frame`, `slice_screen`, `slice_gutters`, `icon_burst`, `icon_shield`, `icon_turret`, `icon_repair` |
| cv_board.render_slice: programme screen code/hex text | `slice_screen_code_text` |
| cv_board.render_board: unit programme screens | `unit_cell_screen`, `unit_screen_bezel`, `screen_motif_skull` |
| cv_board unit programme screens: hex/code text | `unit_screen_code_text` |
| cv_board.render_board: empty cells (dark glass) | `empty_cell`, `ring_separators` |
| cv_board.render_board: code-base frame rings | `codebase_frame` |
| cv_board.render_board: draw_hub (disc, emblem, name) | `hub_disc`, `hub_emblem`, `hub_label` |
| cv_board.draw_hub: inner rings alpha 10, r 16-36 step 9 | `hub_inner_rings` |
| cv_lib.backdrop: radial dim pool | `board_scrim` |
| cv_lib.backdrop: global x0.80 dim + GaussianBlur 2.5 | `backdrop_grade` |
| cv_lib.terminal (fill 238, cyan edge 2 px / 210, r 8, scanlines 4 px / 38) | `terminal_plate_kit` |
| cv_lib.text with NOW[words] off (L2.text proxy bars) | `nowords_variant`, `hero_nowords_proxy`, `sector_digits_nowords`, `ring_tags_nowords`, `cards_nowords`, `stickers_nowords` |
| cv_lib.shadow_paste + sticker plates | `sticker_material` |
| build10 layout constants (column x, gaps, board centre and radii) | `layout_grid` |
| SCRIM token (BRIEF 3.3; not drawn under the HUD/hand today) | `hud_scrim` |
| e10lib.grade_units (mauve post-grade, p2b dim) | `unit_cell_screen`, `hover_focus_dim` |
| build10 p2b overlay alpha 36 percent + non-hovered arcs skipped | `hover_dim_overlay` |
| cv_over.hp_ring | `hp_ring` |
| e9lib.bezel9 (ticks, live cell, chevrons, HOLD cells, arc text) | `bezel_ticks`, `sched_this_turn`, `sched_chevrons`, `sched_hold_cells`, `sched_plus_cells` |
| e9lib.bezel9: live HOLD branch (white outline + glyph) | `sched_hold_live` |
| cv_over.sector_digits (+ needle) | `sector_digits`, `needle` |
| cv_over.cell_border (empty cells, 30 percent) | `empty_cell` |
| e10lib.wave_arcs10 (arcs, pips, width dots, hazard, W tags) | `future_wave_arcs`, `wave_arc_unit_pips`, `climax_hazard_ticks`, `wave_tags` |
| e8lib.ward_arc | `ward_arc` |
| e9lib.tower_slice_bars (bars, crack, break X, broken) | `slice_hp_bars`, `slice_break_x`, `slice_cracked_mark`, `slice_broken_state` |
| e9lib.tower_slice_bars: harm-lost pip (255,150,140) + slash | `slice_pip_lost_harm` |
| e9lib.tower_slice_bars: by_soak lost pip SOAK_C | `slice_pip_lost_soak` |
| e9lib.tower_slice_bars: mend pip (170,240,170) + 3/3 dash | `slice_pip_mend` |
| e9lib.tower_slice_bars: gone pip dashed socket | `slice_pip_gone` |
| e9lib.brace_plate | `brace_plate` |
| e9lib.soak_marks: inward chevrons | `slice_soak_marks` |
| e9lib.soak_marks: rim arc r s1-1, +/-26 deg | `slice_soak_rim_arc` |
| e9lib.tower_slice_bars / soak_marks: orange break X | `slice_soak_break_x` |
| e9lib.threat_trim | `threat_trim` |
| e10lib.lit_cell / unit_mask (incl. the width-6 branch) | `unit_cell_screen`, `ring_unit_wide6` |
| e8lib.cell_outline | `unit_cell_outline`, `consumed_unit`, `hovered_cell_outline` |
| e8lib.token + cv_over.lane_base_style | `token_disc`, `token_lane_base`, `token_halo`, `glyph_packet`, `glyph_worm`, `glyph_payload` |
| e8lib.hp_row (segments, lose slash, shield bracket) | `unit_hp_row`, `shield_bracket` |
| e8lib.armor_cap | `armor_cap` |
| e10lib.chevrons_h / chev_stack_h | `chev_solid_stack`, `chev_hollow`, `chev_sector_column` |
| e9lib.warded_mark | `warded_mark` |
| e8lib.dead_x | `dead_x` |
| build10.draw_units: consumed branch | `consumed_unit` |
| build10.draw_units: trigdead branch | `trigger_killed_unit` |
| e10lib.adjuster_body (cell, HP bar, armor cap, diamond, skull, strike) | `adjuster_cell`, `adjuster_hp_bar`, `adjuster_diamond`, `adjuster_armor_strike` |
| e10lib.gun_tracers10 (tracer line, muzzle nubs, NO TARGET tag) | `gun_tracers`, `gun_tracer_burst_pair`, `no_target_tag` |
| e10lib.gun_tracers10: result hit / armor / ward / shield / sealed | `gun_result_hit`, `gun_result_armor`, `gun_result_ward`, `gun_result_shield_pop`, `gun_result_sealed` |
| e10lib.gun_tracers10: idle stub dash 4/8 r 145-175 | `gun_idle_stub` |
| build10.make p2/p3: gun tracers not called (state f2 has guns) | `gun_tracers_preview` |
| GDD 9.2 / 9.5 (not drawn): card-hover ghost, targeting, Tab focus | `spin_ghost_preview`, `card_targeting` |
| e10lib.landing_arcs (band, disc, wear, twist, dots, chevrons, clamp, diamonds, soak, check) | `landing_arc_frame`, `arc_glyph_disc`, `arc_wear_mark`, `arc_twist_mark`, `arc_now_dot`, `arc_turn_dots`, `arc_chevrons`, `arc_soak_chevron`, `arc_brace_glyph`, `arc_diamonds`, `arc_check` |
| build10.ring_tags | `ring_tags` |
| build10.nudge_ghost | `nudge_ghost` |
| build10.twist_badge (p2/p3) | `twist_badge` |
| build10.refund_marks (placement + REFUND tag) | `refund_burst` |
| e10lib.burst + ram_pip_pop (token, drawn in 4 places) | `refund_token` |
| e8lib.trigger_paths + pencil_line / pencil_x (p2) | `trigger_path`, `trigger_tower_hit` |
| build10.hover_path (p2b) | `hover_path`, `hover_slice_highlight` |
| build10.make p3: cyan fire lines | `resolve_fire_lines` |
| build10.header (plate, title, waves left, pips, ?) | `header_plate`, `header_title`, `waves_left`, `help_button` |
| build10.bill_box (frame, YOU, hero, eq row, split, NEXT, pencil, BEST LINE, without Twist) | `bill_frame`, `you_hp_tally`, `hero_pair`, `eq_row`, `eq_labels`, `tally_segments`, `operators`, `empty_socket`, `trig_groups`, `trig_lands_group`, `split_row`, `route_arrows`, `next_row`, `plan_pencil_underline`, `best_line_tag`, `without_twist_row` |
| build10.option_chip (frame, glyph sequence, label, bar, pair) | `option_chips`, `option_plan_glyphs`, `option_name_label`, `option_outcome_bar`, `option_pair` |
| build10.chain_strip (frame, discs, glyphs, names, tallies, prose) | `chain_strip`, `chain_step_discs`, `chain_step_glyphs`, `chain_step_names`, `chain_result_tallies`, `chain_result_prose` |
| build10.stars_row (frame, stars, labels, tallies, card challenge) | `objectives_frame`, `star_glyph`, `win_label`, `challenge_labels`, `challenge_tallies`, `challenge_trigger_hits` |
| build10.ram_trace (frame, labels, RAM, refund pip, Trace, cap hatch, ENDS = HEAT) | `ram_trace_frame`, `ram_trace_labels`, `ram_pips`, `ram_refund_pop`, `trace_pips`, `trace_cap_hatch`, `ends_heat` |
| cv_chrome.hand (fan, hover grow, liners) | `hand_fan`, `card_hover_grow`, `played_liner` |
| cv_chrome.card_img (frame, band, glyph, x, title, type band, text, cost, loud tab, curl) | `card_frame`, `card_header_strip`, `art_band`, `card_icon`, `card_icon_set`, `card_multiplier`, `card_title`, `type_band`, `rules_text`, `cost_badge`, `loud_tab`, `loud_tab_resting`, `card_hover_grow` |
| build10.stickers (CELL-9, SEND IT, UNDO, hint) | `nameplate`, `send_it`, `undo_chip`, `bottom_hint` |
| build10.hover_tag (p2b) | `hover_tag` |

Granularity rule (completeness review): COVER is keyed per drawn part (branch, colour state, sub-mark), not per function, so a sub-draw cannot hide inside a covered function. Entries for parts that are not drawn (GDD asks, the SCRIM token) are listed so the element still has an owner.

**Retired, not designed:** the sealed hatching + padlock (`e8lib.sealed_marks`, SEALED +2 tag) and the Adjuster rim satellite (`e8lib.adjuster_satellite`), `e8lib.twist_chip` and `e9lib.rim_chips`: dropped by the E9/E10 rules or replaced by landing arcs / the Adjuster body; not called by build10.
**Not elements (fixed):** the backdrop itself (cutaway pick, its own kit), and the plate layout (locked 3.1/3.22).

**Audit result:** PASS: 183 elements in 7 clusters, 161 crops, 72 source draw calls mapped, 0 gaps.


## 6. Completeness review (2026-11-01)

An independent review of the 133-element inventory reported 28 missing elements, 15 lumped or vague entries and one process gap. The art director checked each finding against the five plates (crops at 2-4x) and the generator source (e9lib.tower_slice_bars, e9lib.soak_marks, e10lib.gun_tracers10, cv_lib.backdrop, cv_lib.text, build10.stars_row) and the f1/f2 sim state. **Every finding was confirmed. None is rejected.** Two are handled differently from the review's suggestion; both are noted below. The inventory now has **183 elements, 22 of them LATENT (was 9); 161 crops; COVER 48 -> 72 entries**.

**Added (missing elements)**
- wheel_core: `hub_inner_rings` (alpha-10 rings: confirmed in source, invisible on the plate; kept as the hub's material decision), `slice_screen_code_text` (legible 'goto fail' / hex survives in p1_nowords), `slice_pip_lost_soak` (orange pip beside the salmon pip in the SHIELD sector 1 bar, p2), `slice_pip_mend` (LATENT), `slice_soak_rim_arc` (orange arc on the threat-trim radius, p2), `gun_idle_stub` (LATENT), `gun_result_sealed` (LATENT, stale branch; recommendation: retire), `gun_tracers_preview` (LATENT on the plates: f2 has BURST sector 4 'ward' x2 into Packet 6, but p2/p3 draw no tracers), `spin_ghost_preview` (LATENT, GDD 9.2).
- wave_rings: `unit_screen_code_text` (hex columns in the Packet screens, still there in nowords).
- outer_rings: `bezel_rim_lines` (two orange rim glows at r ~356 / ~388 plus baked light), `backdrop_grade` (global x0.80 dim and 2.5 px blur stacked on room_bio_bare's own grade), `sector_digits_nowords`, `ring_tags_nowords`.
- top_hud: `hud_scrim` (nothing seats the column or the hand on the lit room), `terminal_plate_kit` (the shared plate component and its scanlines), `layout_grid` (x 1066 vs 1062 vs 1068, gaps of 8/10/4 px, p2/p3 growth into the focus hull, edge margins), `hero_nowords_proxy` (white square and red bar replace 12 -> 6, while the yellow arrow stays loudest).
- objectives: `ram_trace_labels`, `challenge_trigger_hits` (LATENT, plan-yellow tally).
- cards: `card_header_strip`, `cards_nowords`.
- actions: `sticker_material` (shared die-cut / plate / shadow; card and sticker shadows differ), `stickers_nowords`, `card_targeting` (LATENT, GDD 9.2 / 9.5), `nowords_variant` (the existing nowords crop now has an owner element for the screen-wide nowords rule).
- `chain_step_glyphs` (red skull for LANDS reuses the boss silhouette; the lightning is used nowhere else) is listed under the splits below.

**Split (lumped entries)**
- `slice_hp_bars` -> the bar set plus `slice_pip_lost_harm`, `slice_pip_lost_soak`, `slice_pip_mend` (LATENT) and `slice_pip_gone` (LATENT): five pip states designed as one set.
- `slice_soak_marks` -> soak chevrons (kept id) + `slice_soak_rim_arc` + `slice_soak_break_x` (+ the soak pip). Four marks for one choice; the family is to be pruned in design.
- `gun_tracers` -> tracer line (kept id) + `gun_result_hit` (the only result visible) + `gun_result_armor`, `gun_result_ward`, `gun_result_shield_pop`, `gun_result_sealed`, `gun_idle_stub` (all LATENT).
- `chain_strip` -> frame (kept id) + `chain_step_discs`, `chain_step_glyphs`, `chain_step_names`, `chain_result_tallies`, `chain_result_prose`.
- `option_chips` -> frame and two states (kept id) + `option_plan_glyphs`, `option_name_label`, `option_outcome_bar`, `option_pair`.
- Refund token -> new owner element `refund_token` (one token drawn in four places at four sizes). `refund_burst` is now the board placement only. `ram_refund_pop`, option chips and the chain strip reference the token.
- `hover_focus_dim` -> unit-screen grade at 50 percent (kept id) + `hover_dim_overlay` (marks at 36 percent; the non-hovered arcs are **removed**, not dimmed).
- `board_scrim` -> radial pool (kept id) + `backdrop_grade`; the HUD/hand scrim is the new `hud_scrim`.
- `consumed_unit` -> consumed, yellow (kept id) + `trigger_killed_unit`, red (its greyed token is hidden under the refund burst).
- `token_disc` -> fill and size (kept id) + `token_lane_base` (three base rings) + `token_halo`.
- `arc_soak_brace` -> `arc_soak_chevron` + `arc_brace_glyph` (different owners: the cream glyph is 28 px and is not a clamp). The old crop was deleted.
- `trig_groups` -> TRIG group (kept id) + `trig_lands_group` (LATENT, reuses the RAW red).
- `sched_hold_cells` -> plus `sched_hold_live` (LATENT white live-HOLD branch).

**Sharpened:** `slice_screen` (code text moved out; per-type contrast named), `unit_cell_screen` (code text moved out), `screen_motif_skull` (stronger in p2 under keep_all), `gun_tracers` (second tracer style and idle style named).

**Handled differently from the review's suggestion (not rejected)**
- Hub inner rings: the review treated them as part of hub material. They are kept as their own element because the source draws them as a separate sub-draw. At alpha 10 they cannot be seen, so the designer decides whether to keep one bevel or remove them.
- Sealed result: the seal mechanic has no meaning in the current rules, so the element exists only to make a decision. The art director recommends deleting the branch rather than designing a glyph for it.

**Process fix:** COVER in `build_brief.py` is now keyed per drawn part (branch, colour state, sub-mark), not per function. It gained 24 entries for sub-draws that were hidden inside covered functions: ring_base rims, draw_hub rings, soak / mend / gone pips, idle stub, sealed, L2.text proxies, terminal() scanlines, shadow_paste, layout constants. It also lists the undrawn parts the screen needs (GDD ghost / targeting, the SCRIM token) so each one has an owner. The nowords crop is no longer exempt from the crop check.


## 7. Open calls for the art director (round 1)

1. Soak colour: needs a new hue/shape clear of schedule orange (decide in R1 from options).
2. Brace colour: cream is enemy HP; propose a player-side clamp colour (cyan family or steel) in R1.
3. Boss HP colour: cream (unit family) vs gold (boss family); the HUD and board must agree.
4. Bezel material for a Solace fight (Meridian brushed brown today); Solace by material and crest, not lime.
5. Card cost badge: plan yellow today; proposal to speak RAM (cyan pip) so cost and RAM read as one currency.
6. Glyph replacements (Packet media arrow, Worm "M", Payload diamond, turret sword, shield reuse) must go through the bible 3.5 twin check.

**Resolved in R1 (3.11):** 1 SOAK = #6A6CFF + notch; 2 Brace = NET_CYAN clamp plate; 3 boss HP = BOSS_GOLD; 4 Solace teal enamel; 5 cost = RAM coin; 6 glyph master library (twin check sheet due in R2).


## 8. Element list review after round 1 (2026-11-01)

Checked against the seven designers' omission reports and the E10 source (`cv_over.slice_badges` is never called; `cv_over.bezel` / 'WAVE TURNS' is called only by build8).
- **Added (17):** wave_rings `glyph_jammer`, `glyph_ring`, `token_placement`, `kind_colour_set`, `adjuster_cell_underlay`, `unit_gone_state`; outer_rings `ring_tag_no_wave` (LATENT), `landing_arc_full_circle` (LATENT); top_hud `row_tags`; cards `card_unaffordable`, `card_committed`, `card_exhaust_keyword`, `card_key_hint` (all LATENT); actions `send_it_states` (LATENT), `focus_brackets`, `adjuster_as_target` (LATENT).
- **Renamed:** `gun_tracer_burst_pair` -> `gun_muzzle_beads` (covers the TURRET single bead).
- **Moved:** `trigger_tower_hit` wheel_core -> actions; the tower back plate / 160-165 px gap is owned by outer_rings `board_backplate`; the UNDO plate by actions `undo_chip`; the twist badge anchor by actions `twist_badge`.
- **Retired:** `gun_result_sealed`; also not designed: `slice_badges` (p3 BLOCKED/HOLDS), the WAVE TURNS caption, the ring-with-bar HOLD glyph, the pause glyph.
- **Not added (new information, needs a game-content ruling):** draw/discard pile counters.
- **Inventory:** 199 elements. Still with no options: 8 wheel_core elements + trigger_tower_hit + every element added above. These come first in R2.

