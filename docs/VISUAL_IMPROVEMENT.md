# REBEL_CELL: path to AAA-calibre visuals

Companion to `VISUAL_CRITIQUE.md`. The critique lists what's broken; this document is about what it would take for REBEL_CELL to *look* like a top-tier release. Screen references (`30`, `gifs/04`, …) are to the review pack.

"AAA calibre" here doesn't mean a bigger budget. It means three things:
1. **Every screen is authored.** Nothing looks like default UI.
2. **Every state change is felt.** Anything the player causes gets motion, light and sound, scaled to how much it matters.
3. **Every pixel is intentional.** Consistent systems, no collisions, no placeholders, readable at any setting.

The benchmarks worth studying for this genre and budget: *Hades* (hierarchy, VFX restraint, UI that feels part of the world), *Slay the Spire 2* / *Balatro* (juice on card and number feedback), *Cyberpunk 2077* and *Ghostrunner* (neon UI language), *Persona 5* (a graphic-design identity carried into the UI), *Citizen Sleeper* (text-heavy screens that still look designed).

---

## 0. North star

> **"A zine taped to a hacker's monitor, over a city that's watching you."**

Every surface belongs to one of three layers, and each layer has its own rules:

| Layer | Material | Used for | Rules |
|---|---|---|---|
| **World** | Neon wireframe city, volumetric haze | Backdrop, grid, route, raid map | Always alive, never competes with UI. Dimmed and blurred under panels. |
| **System** | Glass/terminal: dark glass, scanlines, 1 px neon rules, monospace | Data, lists, settings, feeds, maps UI | Precise, cool, cyan-led. No paper, no stickers. |
| **Voice** | Zine: paper, tape, stickers, marker, drip graffiti | Player intent and emotion: verbs (SEND IT), stamps, forecasts, loot, crew, rewards | Warm and handmade. Used sparingly, so it stays special. |

Today the layers bleed into each other: cream cards inside terminal panels, native dropdowns on zine pages. Writing these rules down as a one-page art bible is the single most important step, and every item below follows from it.

---

## 1. Art direction foundations

1. **Write the art bible (10–15 pages).** Layer rules, palette with semantic roles, type scale, spacing grid, icon grammar, motion spec, VFX tiers, do/don't examples taken from the current build.
2. **Semantic colour system.** Take roles away from the corporations and give them to meaning:
   - Harm → red
   - Protection → cyan
   - Gain/HP → green
   - Focus/target → yellow
   - Player brand → magenta
   - Corp colours come from a separate set that never collides with those (see §7 of the critique: Orbital white, Rebel Cell red and Halcyon purple all collide today).
   - Every role also gets a **shape or pattern**, so nothing depends on colour alone.
3. **Type system.**
   - Keep the drip display face for **verbs only** (SEND IT, LOOT, VICTORY).
   - Keep the marker face for headings.
   - Replace the default monospace with a licensed, characterful mono that has good small sizes (e.g. JetBrains Mono, Berkeley Mono, Iosevka).
   - Add a humanist sans for long body text (Codex, events).
   - Build a 6-step type scale (12 / 14 / 16 / 20 / 28 / 44 px at 720p) and use nothing else.
   - Render everything as MSDF fonts in Godot, so text stays crisp at 1.6 and at 4K.
4. **Resolution strategy.** Design at 1920×1080, with 720p as the minimum, plus 4K and ultrawide safe areas. The stills are 1280×720 and many elements are 7–9 px; at 1080p the same layout needs a larger type scale, not bigger boxes.
5. **One icon grammar.** About 120 icons on a 24 px grid, 2 px stroke, filled-when-active, and a shared corner radius. Today slice, status, menu and legend icons come from different visual families.

---

## 2. The world (backdrop, grid, route, raid map)

The city is already the best asset in the game. Push it from a pretty illustration to a living place.

1. **Lighting pass.**
   - Real emissive neon with HDR bloom (Godot Forward+ glow, per-channel tuned).
   - Volumetric fog in layered depth bands.
   - Rain or haze particles.
   - Wet-street reflections (screen-space reflections, or baked reflection cards on the ground plane).
   - The pack's backdrop is flat-lit wireframe; lighting is the biggest single "production value" jump available.
2. **Life.** Slow traffic streams along the ramps, blinking aircraft lights, drone patrols, billboard loops showing corp ads (in each corp's colour and branding), window lights switching on and off, a very slow day/night drift over a campaign.
3. **The city reacts to state.** This is what separates AAA from indie.
   - **Heat:** 0–25 calm. At 25 (NOTICED), search-light sweeps. At 50, sirens and red/blue rim light. At 75 and above, patrol drones and a desaturated, oppressive grade.
   - **Territory:** claimed districts get the player's graffiti tags projected onto buildings and magenta light leaking into the fog, instead of today's khaki hatch (`gifs/16`).
   - **The corp at war:** the whole city grade shifts toward the target corp's palette as the campaign progresses.
4. **Parallax and camera.**
   - Three to four depth layers with subtle mouse or stick parallax.
   - Cinematic camera moves between pages: dolly along a ramp from HQ to the Grid, a crane down into a Site on jack-in.
   - Replace hard cuts (`gifs/22`, `gifs/23`) with continuous camera travel through one persistent world.
5. **No placeholders.** Pre-bake the next district during transitions so the flat block city (`gifs/18`, `gifs/23`) never shows. Keep a low-res pre-render as a fallback, never flat blocks.
6. **Map readability layer.** Use depth of field or a luminance mask to push buildings back and lift nodes, routes and labels forward on the Grid, Route and Raid maps. Resolve label collisions with an automatic leader-line layout.

---

## 3. Combat: make the wheels the hero

Combat is where the store-page screenshots and most of the playtime come from.

1. **Wheels as physical objects.**
   - Model or paint the wheels as hardware: a machined bezel, glass cover, emissive slice inlays, a physical needle with a counterweight, and a hub screen.
   - The player's wheel is a scratched, sticker-covered custom rig; enemy wheels are cold corporate hardware in their corp's colour.
   - Instant ownership read, and a strong silhouette.
2. **Class identity in the wheel.** Each of the eight classes gets a unique bezel shape, hub animation and slice-inlay style (Botnet: swarming dots; Ghost: flickering transparency; Wrecker: welded, damaged bezel; etc.). Fixes the identical pairs in `69–76`.
3. **Enemy presence.**
   - Give each enemy a portrait or bust, or an animated hologram above its wheel, not just a name in the hub.
   - Bosses get a full-height hologram or silhouette behind the wheel, a nameplate banner with phase pips, and their own intro sting (camera push, name slam, music drop).
   - Today the boss (`43`) looks like any other enemy.
4. **Spin feel.**
   - Physically based spin with momentum, friction and a detent click per tick.
   - Needle bounce on landing.
   - A slow-motion last 3 ticks when the landing matters (lethal, Perfect).
   - Every tick is a haptic pulse on controller and a click in the audio.
5. **Resolve choreography (the SEND IT sequence).**
   - A crafted 2–3 s sequence with anticipation (the camera pushes in slightly, the UI recedes), impact frames (2–3 frame hit-stop, local chromatic kick, particle burst from the slice icon), and a clear read (one net number, flying to the HP bar, which drains in two stages: white chunk, then fill).
   - Unique VFX per slice type: crit = shattered-glass burst, shield = hex-plate deploy, afflict = glitch-crawl, evade = afterimage smear.
   - Speed options (1×, 2×, instant) and hold-to-fast-forward.
6. **HP and damage language.** Thick, segmented HP rings; a ghost segment for forecast damage; a two-stage drain; colour state (green → amber → red); a heartbeat pulse under 25%; a screen-edge vignette when the player is at lethal risk.
7. **Card presentation (see §5).** Hovered cards lift and fan with physics tilt toward the cursor. Drag uses a spring-follow. Valid targets get a magnetic snap. On play, the card burns into the target with a cause → effect trail.
8. **Victory, defeat and phase moments.** Each gets a 1.5–2.5 s mini-cinematic:
   - Victory: the enemy wheel shatters in slow motion, the camera pulls back, VICTORY slams in as a paper sticker with tape.
   - Defeat: the operative's portrait flatlines, the city grade goes grey, a FLATLINED stamp.
   - Boss phase: the wheel physically reconfigures (slices slide and flip), the new needle rotates into place, and the phase name slams.

---

## 4. Characters and crew

1. **Painted portraits** for all eight classes, plus expression variants (neutral, hurt, triumphant, flatlined) used in combat, dossiers, barks and end screens. The current icon-style silhouettes (`14`, `15`) are the biggest gap in character appeal.
2. **Distinct silhouettes and palettes per class.** No shared tints. Ideally a clear gear-and-costume read per class (goggles, cables, drone rig, and so on).
3. **Crew personalisation.** Portrait variants per recruit (face, hair, colour), and Polaroids that pick up damage, tape and doodles over the campaign. This is presentation of existing state, not a new mechanic.
4. **Barks with presence.** An animated portrait (lip flap or eye blink) next to typed barks. Subtitles use a proper speaker plate.

---

## 5. Card art and card frame

1. **Illustrate every card.** Every card is currently text on a coloured blank (`54`). Style: duotone or risograph halftone illustrations that fit the zine layer, e.g. a 2-colour print with misregistration, over photocopy texture.
   - Budget-conscious route: about 30 base illustrations tinted per rarity and effect, then unique art for rares and class cards.
2. **Card frame system.**
   - Rarity shown by material (photocopy → glossy sticker → holographic foil with a shader).
   - Cost in a consistent top-left gem.
   - Effect glyph plus the key number, large, in a bottom band.
   - Rules text at 14 px or more with keyword highlighting.
   - Hover shows an expanded tooltip for keywords.
3. **Card motion.** Draw, discard, exhaust and shred animations with distinct feel (exhaust = burns to ash; shred = paper strips, already started in `gifs/14`).
4. **Foil and holo shader** for rare and loot cards, responding to cursor or stick tilt. This is the cheapest high-impact "premium" signal available.

---

## 6. UI system (system layer and voice layer)

1. **Build a component library in Godot Themes** and ban ad-hoc styling:
   - Panel (glass), Card (paper)
   - Button: primary, secondary, danger, disabled
   - Toggle, Slider (with value), Dropdown (custom)
   - Tab set, Toast (one style), Tooltip, Stat chip, Stamp, Sticker
   - Each one designed in every state: idle, hover, focus, pressed, disabled, error.
2. **Glass panels done properly.**
   - Background blur of the city (a screen-texture blur shader), inner glow, 1 px bevel highlight, subtle animated scanline and noise, corner brackets.
   - Replace the flat navy boxes.
   - Panels size to their content; no big empty panels (pause menus, event panels, crew roster).
3. **Replace every native control.** Dropdowns become radial or tile pickers. Spinners become stepper chips. Text lists become cards. This removes most of the "debug UI" read (`02`, `03`, `28`, `52`).
4. **Grid and alignment.** An 8 px spacing grid, fixed safe margins, consistent panel gutters. Every screen gets a layout pass against it.
5. **The top bar as a signature piece.** The taped sticky-note stat bar is great; make it a crafted object. Notes flutter slightly, update with a peel-and-restick animation, and important stats pin themselves with a pushpin when they change.
6. **Diegetic framing.** Present HQ as the actual cyberdeck: a CRT bezel with curvature, a keyboard edge at the bottom, cables. The City Grid is on its monitor, the WANTED poster is taped to the wall. Settle the screen-space UI into a physical space.
7. **Redesign the key screens from scratch** (they currently read as unfinished):
   - **Title:** animated logo, a slow camera crane over the city, menu on glass, the city reacting to hover.
   - **Campaign slots:** each slot is a case file (folder, corp logo, Heat meter, crew Polaroids, last-played date).
   - **New campaign:** a corkboard or "planning table" with the corp as a dossier, the crew as Polaroids and the modifiers as stickers.
   - **Campaign end (won/lost):** full-bleed illustrated splash per corp, a crew wall, stamped verdict, a stats scroll.
   - **FLATLINED:** the portrait flatline animation, the city going grey, the stamp, then stats.
   - **Codex:** an illustrated zine spread with section tabs.

---

## 7. VFX

1. **VFX tiers**, so spectacle follows importance:
   - T0 ambient: city, idle wheels
   - T1 feedback: hover, tick, nudge
   - T2 outcome: hit, block, buy
   - T3 moment: Perfect, kill, phase, level-up
   - T4 cinematic: boss intro, victory, campaign end
   - Each tier has a maximum screen coverage, duration and brightness. No full-screen flashes below T4, and none at all in Reduce Effects mode (the flashes in `gifs/02` and `gifs/25` break this today).
2. **Signature shaders.**
   - Glitch/datamosh transitions (jack-in, `gifs/18`, is a good start: make it full-resolution and art-directed).
   - CRT/scanline overlay with curvature.
   - Chromatic aberration kicks on impact.
   - Holographic foil.
   - Paper burn and dissolve.
   - Marker-stroke reveal for stamps and circles (extend the lovely marker circle in `55`).
3. **Particles.** Consistent shapes per damage type, with light emission onto nearby UI. Sparks cast brief light on the wheels.
4. **Post-processing stack.** Glow/bloom, subtle film grain, vignette, per-scene LUT colour grading (HQ warm/dirty, Grid cool, combat high contrast, corp-tinted endgame). Every effect gets a reduce-effects toggle.

---

## 8. Motion and game feel

1. **Motion spec (one table everyone uses).**

| Action | Duration | Easing |
|---|---|---|
| Page transition | 350 ms | ease-in-out-quart, continuous camera |
| Modal | 220 ms | back-out, 1.02 overshoot |
| Stamp | 120 ms in | 3-frame squash, then 600 ms hold |
| Number rise | 400 ms | ease-out-expo |
| Toast | 180 ms in | 2.5 s hold, 200 ms out |
| Hover | 90 ms | scale 1.04 |

2. **Juice budget per interaction:** anticipation → action → follow-through → settle. Apply it to every drag and drop (crew → JACK IN, ring segment swap and asset placement are currently nearly invisible: `gifs/09`, `gifs/10`, `gifs/07`).
3. **Hit-stop and screen shake** for T2 and above, scaled by magnitude, off in reduce-effects mode.
4. **Idle animation everywhere.** Breathing panels (1–2% glow pulse), drifting stickers, a blinking cursor in terminals, wheels ticking slightly at idle. Static screens read as unfinished.
5. **Input latency and responsiveness.** Every input gets a visual acknowledgement within 50 ms, even if the full animation follows later. Everything is skippable or speed-up-able after its first viewing.

---

## 9. Audio-visual sync

AAA polish is audiovisual, and the visuals will feel twice as good with matched sound:
- A tick click per wheel detent, with pitch rising as the spin slows.
- A distinct stamp thud, tape rip and marker squeak for the zine layer.
- A glass hum and data chirps for the system layer.
- Impact stingers matched to VFX tiers; music ducking on T3 and above.
- The Heat level drives the music layer and ambient city sound (sirens and helicopters at high Heat).
- Controller haptics matched to ticks, impacts and stamps.

---

## 10. Accessibility at AAA standard

Treat these as part of the visual quality bar, not extras:
- Text scale up to 2.0 with **no** clipping. Layouts reflow and panels scroll (the 1.6 issues in the critique §5).
- Colour-blind modes (deutan, protan, tritan) with palette remaps, plus the pattern and shape redundancy from §1.
- Reduce effects removes full-screen effects, shake, chromatic aberration and flicker. Plus a separate "reduce motion" setting and a flash limiter that is actually enforced by the VFX tier system.
- High-contrast UI mode (solid panels, no background blur, 7:1 text).
- Controller glyph sets (Xbox, PlayStation, Switch, Steam Deck) that switch automatically, and TV-distance focus states.
- Everything localisable. The logo and signature graffiti are baked art with translated subtitles; everything else has 40% width slack and font fallbacks for CJK and Cyrillic.

---

## 11. Technical art (Godot 4.7)

- **Shaders:** screen-space blur for glass, foil, dissolve/burn, glitch transition, CRT overlay, and SDF marker strokes. Keep them in one shader library with shared uniforms.
- **Fonts:** MSDF font import for every face; set a theme-wide font size scale so text scale touches everything.
- **UI rendering:** CanvasLayer structure (world → world UI → system UI → voice UI → overlays), with a SubViewport for the backdrop so it can be blurred and graded independently.
- **Performance targets:** a locked 60 fps at 1080p on Steam Deck; 120 fps and 4K on desktop. Budget the post stack and particles per tier.
- **Capture tooling:** the existing review-pack harness is excellent. Extend it to render every screen at 1080p, 4K, 1.0, 1.6, 2.0 and each colour-blind mode, and diff the output against the previous build for visual regressions.
- **Layout linting:** an automated test that flags any Label with a fixed font size, overlapping Control rects, clipped text (`get_visible_line_count` vs line count) and contrast below 4.5:1.

---

## 12. Marketing-grade assets

- Key art: an illustrated hero piece (the cell on a rooftop over the neon city, SEND IT graffiti), in capsule, header, library and hero sizes.
- A logo lockup with an animated version for the trailer and title screen.
- A trailer built around the three screenshot-ready moments: a SEND IT resolve with a Perfect, the city reacting to Heat, and a boss phase change.
- A photo mode or capture mode (hide the UI, free camera over the city). Cheap to build, and community sharing does the marketing.

---

## 13. Roadmap (suggested order)

| Phase | Focus | Outcome |
|---|---|---|
| **1. Foundation** (4–6 wks) | Art bible, colour and type system, component library, 8 px grid, fix every critique issue | Consistent, readable and accessible; no screen looks like debug UI |
| **2. Combat hero pass** (6–8 wks) | Physical wheels, class identity, HP language, resolve choreography, card lift and drag feel, VFX tiers | Screenshots and GIFs of combat sell the game |
| **3. Art content** (8–12 wks, can run in parallel) | Class portraits and expressions, card illustrations and frames, enemy and boss holograms, corp branding | Character appeal and a sense of a premium product |
| **4. World and cinematics** (6–8 wks) | City lighting, life and state reactivity, continuous camera, key-screen redesigns, end-screen cinematics | The world feels alive and responds to the player |
| **5. Polish and marketing** (4 wks) | Idle motion, audio sync, haptics, LUT grading, photo mode, key art, trailer | Ship-ready AAA presentation |

**If you can only do five things**, do these:
1. The art bible with layer, colour and type rules.
2. A custom component library that replaces every native control.
3. Physical wheels with a proper HP language and SEND IT choreography.
4. Card illustrations with a foil/holo frame.
5. City lighting plus state reactivity to Heat.

Those five take the game from "promising indie with rough edges" to "premium-looking release".
