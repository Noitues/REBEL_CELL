# REBEL_CELL — Animation & Motion Handoff

A brief for the agent who takes over motion: tweens, transitions, feedback and ambient
animation. The visual pass (static look) is done and is recorded in `docs/STYLE_GUIDE.md`
§1.1, §4 and `docs/DECISIONS.md` ("Visual pass" entries). This document is the motion
roadmap: what exists, how to work with the owner, and every animation still to build, in
priority order.

Read first: `CLAUDE.md` (the rules), `docs/STYLE_GUIDE.md` §5 Motion & §6 Accessibility,
`docs/GDD.md` §9.2 Combat readability, §9.4 Heat feedback, §9.6 Accessibility.

---

## 1. Ground rules (non-negotiable)

1. **Views only.** Motion lives in `scripts/ui/` and the `Fx` autoload. Never in
   `scripts/core/`; never changes game state; never uses game RNG. Decoration randomness
   comes from hashes (see `NeonCity._h`), never `randf()`.
2. **Reduce effects.** Every animated effect checks `Fx.effects_enabled()`. With reduce
   effects on, show the end state immediately (or a single short fade), no shake, no
   flicker, no distortion.
3. **Flash limiter.** Screen flashes go through `Fx.flash()`, which caps at 3 per second.
   Do not bypass it.
4. **Headless and tests.** Animations must not block logic. Tests run headless and read
   the end state at once: use `DisplayServer.get_name() == "headless"` or
   `not Fx.effects_enabled()` to skip (see `combat_scene._instant_playback()` and the
   raid playout in `hq_scene`). Never `await` a tween inside a rule path.
5. **Readability wins.** Nothing may animate over the wheels in a way that hides a slice,
   a pointer or a value at the moment the player decides (GDD 9.2). Motion settles before
   input is needed.
6. **No magic numbers.** Every duration, ease, amplitude and delay goes in one resource
   (section 3), not inline.
7. **Tests.** Each new animation keeps `godot --headless -s addons/gut/gut_cmdln.gd
   -gdir=res://tests -gexit` green, plus the schema smoke test and content validation.
   Add a test where a rule is involved (e.g. "reduce effects shows the end state at once").

## 2. What already exists

| Where | What | Notes |
|---|---|---|
| `Fx.jack_in / jack_out` | CRT push-in / pull-out between HQ and netrun (0.7 s) | Used by `RunManager`. Crude: a rect grows and fades. Needs the real version (4.1). |
| `Fx.flash` | Full-screen colour flash, limited | Used on Perfect, enemy Perfect, previews. |
| `Fx.freeze_frames(n)` | Short hit-stop | Perfect landing (2 frames). |
| `Fx.heat_pulse` | Distortion pulse | **Defined but never called.** Wire to Heat thresholds (4.6). |
| `Fx.show_saved` | "SAVED" fades out | Fine. |
| `combat_scene` | Partial = 4-step shake; Good = alpha blink; migrating pointers flicker (looping tween on `pointer_alpha`) | See `_feedback()` and `_flicker_view()`. |
| `NeonCity` | Beacon blink, slow menu pan (Lissajous), rain | `_process` / `_draw_fx`. |
| `RaidPlayoutPanel` + `hq_scene` | Step-by-step raid playout with 1x/2x/4x/Skip | Stepping only; no tweened motion along paths yet. |
| `DripButton` | Hover halo (static jitter copies) | No motion yet. |

## 3. First task: the motion config and a motion lab

Before building effects, make motion tunable so the owner can react to numbers, not code.

1. **`content/config/ui_motion.tres`** (schema `scripts/data/ui_motion_data.gd`,
   read-only at runtime): one entry per animation id with `duration`, `delay`, `ease`
   (Tween.EaseType), `trans` (Tween.TransitionType), `amplitude` (px or scale), `enabled`.
   Keep the schema change minimal, update `tools/schema_smoke_test.gd`, log it in
   `docs/DECISIONS.md` (CLAUDE.md rule 8).
2. **`scripts/ui/kit/motion.gd`** (`class_name Motion`): small helpers that read the config
   by id and build tweens (`Motion.pop(node, &"card_hover")`, `Motion.slide_in(...)`), and
   return at once under reduce effects / headless.
3. **`tools/design_lab/motion_lab.tscn`**: one screen that loops any animation id on real
   UI pieces (a card, a wheel, a sticker, SEND IT, a panel), with sliders for duration,
   amplitude and ease, a speed control (0.25x-2x) and "copy values" that prints the
   `.tres` lines. The owner tunes here, locally, and pastes the numbers back.

## 4. Roadmap (priority order)

Each item: trigger → what moves → feel → acceptance. Durations are starting points for the
config, to be tuned with the owner.

### P1 — Combat (the core loop; do first)

4.1 **Jack in / jack out.** Trigger: leaving HQ for a netrun and back. The camera pushes
into the deck CRT, the screen dissolves to the wireframe city, scanlines roll. Feel:
heavy, 0.6-0.9 s. Jack out reverses. Acceptance: no frame shows both scenes' UI at once;
reduce effects = a 0.2 s fade.

4.2 **Spin.** Trigger: any wheel rotation (card spin, respin, enemy turn). The wheel
rotates the exact ticks with ease-out and a slight overshoot-settle; slices blur a little
above a speed threshold. Feel: mechanical, snappy, 0.25-0.6 s by distance. Acceptance:
ends on the exact tick the core computed; the preview is correct the moment it settles.

4.3 **Nudge.** Trigger: nudge left/right. One-tick step with a click and a 1-2 px recoil.
Feel: crisp, under 0.12 s. Acceptance: repeated fast presses queue and never desync.

4.4 **Precision landing.** Perfect: latch snap + wheel-local inversion + 2-frame freeze +
limited flash (exists: polish it); Good: clean click and a small ring pulse; Partial:
stutter (exists); Miss: static burst over the slice only. Acceptance: each is
distinguishable with sound off and in greyscale.

4.5 **Card play.** Hover: lift 12 px, tilt to 0°, glow. Play: the card flies to the wheel it
targets and "stamps" onto it, then dissolves into the effect. Draw: cards deal in from the
deck pile with a fan. Discard/exhaust: exhaust burns (paper curl + ember). Feel: zine,
tactile, 0.2-0.35 s. Acceptance: the hand never reflows mid-animation in a way that moves
a card under the cursor.

4.6 **SEND IT / resolution.** Press: the drip lettering squashes and the drips run a few
px. Resolution order plays as a sequence: defensive pointers, then offensive, then
statuses, each pointer pulsing as it resolves, numbers popping from the slice. Feel:
punchy, readable, total under 1.5 s at 1x with a skip on click. Acceptance: matches the
end-turn preview exactly (preview = real result).

4.7 **Damage, block and heal numbers.** Float up from the wheel with the slice colour,
bold with a white outline (same rule as the slice icons); crits bigger with a star burst.
HP arc drains with a lag bar (white trailing segment). Acceptance: numbers never cover the
pointer of the next resolving slice.

4.8 **Intent tags.** When the preview changes, the taped tag flips (paper flip, 0.15 s).

4.9 **Rewind.** A quick reverse scrub (tape-rewind stutter, VHS lines) back to the
checkpoint. Acceptance: never crosses a checkpoint visually.

4.10 **Migrating / orbiting pointers.** Existing flicker; add the orbit trail as a fading
arc. Acceptance: GDD 9.2.

4.11 **Enemy death / breach.** The enemy wheel cracks along slice borders and the pieces
fall with the city visible through; hub breach = the hub glass shatters.

### P2 — Heat, HQ and the map

4.12 **Heat thresholds (25/50/75).** Call `Fx.heat_pulse` on each crossing (GDD 9.4). The
ransom HEAT letters shake once; the wanted poster stamps a new band. Net: the corporate
wireframe creeps over the zine layer (tween the creep uniform). Acceptance: pulses, never
stays on.

4.13 **HQ.** Idle: CRT hum flicker on the deck screen, pirate radio text types in, JACK IN
ring breathes slowly. Crew Polaroids tilt slightly on hover.

4.14 **City Grid / raid setup.** Selecting a Site: the roof outline draws on (stroke
reveal), the camera eases to it. Threat routes: dashes crawl along the path toward home.
Deploying an asset: the card drops onto the node with a stamp.

4.15 **Raid playout.** Threats move along the street-routed paths (tween along the polyline),
turrets fire traces, damage numbers on nodes, held/seized flips. Speed controls scale the
config durations; Skip jumps to the summary.

4.16 **Netrun route.** Choosing the next node: a light pulse travels the link; the new
node pops up in the isometric view; visited nodes dim.

### P3 — Screens, menus and ambience

4.17 **Screen transitions.** Panels slide in from the edge with a 1-frame CRT roll
(terminal glass) or drop in with tape (paper). Keep under 0.25 s.

4.18 **Menus.** The `> ITEM` cursor blinks; the selected line types in; focus moves slide
the highlight.

4.19 **Modem.** The neon MODEM sign flickers on (tube warm-up) on entry, CYBER SHOP traces
light up along the circuit; buying: the item flies to the top bar icon; BUY / SELL notes
flap on hover.

4.20 **Loot / rewards.** Cards fan in; the picked card lifts to the deck icon; Schematics
count up.

4.21 **DISPATCH and subtitles.** Line types in at a readable speed (can be instant with a
setting); bar slides in. Combat docks it at the top (`Dialogue.dock_at`).

4.22 **Drip lettering.** Drips grow slowly on first appearance (0.6 s), then hold. Hover:
halo pulse. Never loops continuously.

4.23 **City ambience.** Traffic particles on the busiest streets (small bright dashes, very
sparse), sign flicker on a few HQ signs, beacon blink (exists), rain option (exists). All
off under reduce effects. Budget: the city stays a single static draw plus a light FX layer.

4.24 **Top bar stickies.** When a value changes, its sticky note bumps (scale 1.08, 0.12 s)
and the number rolls.

## 5. How to work with the owner

- **Show motion as frames.** The owner reviews still images. For each animation deliver a
  frame strip (6-10 frames across the motion on one image, labelled with ms) and, when
  useful, a GIF. Record with Movie Maker (see section 6), then montage with PIL.
- **Offer 2-3 variants side by side** (e.g. snappy / heavy / bouncy) with the config values
  printed under each. The owner picks; the values go in `ui_motion.tres`.
- **Ask the owner, per animation:** trigger, feel (snappy, heavy, bouncy), rough duration,
  a reference (another game or a clip), what must stay readable during it.
- **Log every choice** in `docs/DECISIONS.md` under a "Motion pass" heading, and update
  `docs/STYLE_GUIDE.md` §5.
- Commit small: one animation (or one family) per commit, criterion in the message.

## 6. Capturing motion (how the visual pass did it)

Screens have demo flags that jump straight to a state, e.g. (full list: `grep -o
'"--demo-[a-z_-]*' scripts/ui/*.gd`):

```
godot --path . res://scenes/netrun_map/netrun_scene.tscn -- --demo-combat
godot --path . res://scenes/hq/hq_scene.tscn -- --demo-playout
godot --path . res://scenes/menu/title_scene.tscn -- --demo-district=solace
```

Headless capture of every frame (a cloud box has no display; use a virtual one):

```
xvfb-run -a -s "-screen 0 1280x720x24" godot --rendering-driver opengl3 --path . \
  --resolution 1280x720 --write-movie /tmp/frames/f.png --fixed-fps 30 --quit-after 45 \
  res://scenes/netrun_map/netrun_scene.tscn -- --demo-combat
```

`--write-movie` with a `.png` path writes one numbered PNG per frame at a fixed frame
rate, so timing is exact and repeatable. Add a demo flag that triggers the animation
under review a few frames in (e.g. `--demo-anim=card_play`), then pick frames for the
strip. Large offline renders use a `SubViewport` tool (see
`tools/design_lab/city_poster.gd`, `portrait_concepts.gd`).

## 7. Checklist per animation

- [ ] Values in `ui_motion.tres`, none inline
- [ ] Reduce effects: end state at once (or a single short fade)
- [ ] Headless / tests: no waiting, end state immediately
- [ ] Never hides a slice, pointer or value when the player must decide
- [ ] Flashes through `Fx.flash` (limiter)
- [ ] Frame strip + variants shown to the owner; choice logged in DECISIONS
- [ ] Tests, schema smoke test, content validation green
