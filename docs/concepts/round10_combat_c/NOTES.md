# Round 10: back to Screens & Data (C) slices, VIRUS/PROXY rework, combat on the new city

The low-poly identity-art slices from rounds 8â€“9 are dropped. Every slice is a C screen again:
- a per-slice bezel with a hairline and an LED;
- live CRT content;
- a bold white glyph and value with a dark outline, on a darkened read plate.

The round 6 roster verdicts still apply: SANDBOX uses the guard-ring PCB, PROXY has a bolder route, and VIRUS is toned down. The border is the round 7 V2 telemetry ring: a scrolling class or corp readout with emblem badges at the quarters.

## Files
| File | What it shows |
|---|---|
| `slices_rework.png` | Old VIRUS/PROXY next to options A/B/C. Each at hero tile size, inside a full r = 60 wheel (colour and greyscale), plus a greyscale row of hero tiles. |
| `combat_night_regular.png` | Breaker against Route Optimizer (Meridian regular, 2 readers at ticks 0 and 15), over the night city. |
| `combat_night_boss.png` | Breaker against The Manifest (Meridian boss, phase 1), over the night city. |
| `combat_day_boss.png` | The same boss shot over the day city. |
| `contact_sheet.jpg` | All four images above. |

The scripts are in `scripts/`:
- `python make_rework.py all` builds the rework sheet.
- `python make_combat.py all` builds the combat shots and the contact sheet.

Renders are cached in `scratch/`, which git ignores.

## Task 1: VIRUS and PROXY

| Option | Glyph | Screen |
|---|---|---|
| **VIRUS A (recommended)** | Poison vial: round flask, liquid line, bubbles | Violet blotches grow over a scrolling hex dump and eat it. The infection front glows lavender and drips run down from the rim. |
| VIRUS B | Skull-drop: a teardrop with a skull face | Glossy ooze slides down from the rim. Drips hang, fall and pool, and the data cells under the pools turn violet. |
| VIRUS C | Biohazard trefoil | The round 6 toned cell spread, unchanged. |
| **PROXY A (recommended)** | Guy Fawkes-style mask: arched brows, slit eyes, upturned moustache, thin smile, goatee | Round 6's bold reroute, with the dead route still shown as a red broken trace with an X. The route and the packet now leave 3 fading afterimages stepped sideways, as a dodge trail. |
| PROXY B | Dodge arrow: a solid arrow swerving off, with a hollow afterimage of the old line | A red trace beam locks straight down the screen. The packet's route bends around it and leaves hollow afterimages on the beam. |
| PROXY C | Mask | Onion relay hops with IP labels. The red tracker crosshair is left at hop 1, and the screen reads TRACE LOST. |

Why A for both:
- **The vial is the only VIRUS silhouette nothing else on the wheel shares.**
  - The skull-drop (B) competes with ZERO-DAY's skull screen and burst glyph.
  - The biohazard (C) turns into a three-blob smudge at r = 60.
- **The mask still reads at about 24 px.** You can see the moustache, goatee and eye slits. It also says "anonymous / masked", where the old chevrons said "fast forward".
- **The DODGE arrow (B) is the fallback if a face icon is unwanted.** It blurs below r = 60.

Brightness: VIRUS A peaks at about 0.5 of violet, before the slice glow is added. On the wheel it sits level with EXPLOIT and FIREWALL, not above them (see the player wheel in the combat shots).

## New rule: upright value blocks
The glyph and value block now stays upright and counter-rotates as the wheel spins.

In rounds 5â€“8 the block rotated with its slice. On the bottom slice, Breaker's EXPLOIT **6** read as **9** (visible in round 8's `wheel_breaker.png`).

The read plate is now a screen-space ellipse sized to the block. This is a small change to `slicelib.render_slice` (`opts["upright"]`).

## Wheels used
- **Player: Breaker** (`content/classes/breaker.tres`). The real wheel is ZERO-DAY 12, EXPLOIT 6 Ã—3, FIREWALL 5, NULL.
  - **Mock change: Breaker has no VIRUS or PROXY.** For these shots, slot 2 (an EXPLOIT) shows **VIRUS 3** and slot 5 (the NULL) shows **PROXY 4**. Values 3 and 4 are round 5's defaults.
  - Inner ring x2 / PIERCE / BLANK, from content.
  - HP 41/60 and RAM 5/12 are invented turn-3 state (the class has max RAM 12).
- **Regular: Route Optimizer** (`content/enemies`). Its slices are EXPLOIT 8 Ã—3, ZERO-DAY 14, FIREWALL 5 and NULL, with 2 readers at ticks 0 and 15. Shown at HP 30/48.
- **Boss: The Manifest.**
  - Phase 1 slices from content, including TARIFF 3, which drains RAM.
  - Boss treatment:
    - drawn at 120% of the regular wheel's size (r 258 against 215);
    - a heavier bezel: the telemetry ring plus a hazard-striped outer band with crown studs;
    - a nameplate banner hung on chains;
    - P2 and P3 phase pips on the HP arc, at the content thresholds.
- Each HP arc shows the **predicted loss** as red hatched segments.
- **Forecast numbers.**
  - Each NEXT plate matches its forecast tag. For example, ZERO-DAY 12 minus BLOCK 5 gives 7, so the enemy's NEXT is 23 (âˆ’7).
  - The boss has a +4 shield from its hub core, so the same hit does 8.
  - The aim pips and the "RING x2 ON PERFECT" chip are illustrative.
- **Hand:** five cards from `content/cards`: Flick, Ghost Step, Corrupt Packet, Bulwark and Heavy Spin. The RAM costs are real. Corrupt Packet is hovered and aimed, and the RAM meter shows its 1 RAM as "about to be spent".

## How the wheels sit on the city
- **Framing.** The city is cropped so the Meridian district sits behind the enemy wheel (art_asset C4: "framed on the district of the corporation being fought").
- **Base treatment.**
  - Gaussian blur of 2.2 px and desaturation to 75% (62% for day).
  - Dimmed to 52% of its brightness at night and 72% by day.
  - An extra darkening pool behind each wheel: 50% at night, 60% by day, falling off at 1.35 Ã— the wheel radius.
  - A darker band under the hand (down to 45% brightness) and a darker top bar.
  - A soft contact shadow under each wheel.
- **Light spill.** The bright parts of each wheel are blurred (two radii), multiplied back into the city and added faintly on top:
  - Night: Ã—1.9 multiply, +0.2 add. The pink and orange wash on nearby buildings is clearly visible.
  - Day: Ã—1.1 multiply, +0.08 add. Day light swamps it, as it should.
- **Overlay marks (5).** Values and HP stay clear of all of them.
  1. A pink vinyl sticker name plate, CELL-9 // BREAKER.
  2. A yellow vinyl SEND IT sticker, the main verb.
  3. A yellow grease-pencil aim arrow from the hovered card to the enemy pointer.
  4. A yellow grease-pencil loop around the enemy pointer.
  5. A red grease-pencil underline and "!" under the player's NEXT plate.

  The cards are C-C die-cut vinyl sticker cards; they are the hand, so they are not counted as marks.

## Conflicts noticed
1. **The city's baked district labels show through the combat screen.** THE SPRAWL, ORBITAL and HALCYON are visible behind the HUD; the MERIDIAN label is hidden under the enemy wheel. They read as UI and compete with the HUD plates. The combat arena should use a label-free city render (or a mask that hides labels).
2. **Day and night restyles are close in brightness.** Day is only about 10-15% brighter in this crop, so the day shot needed a lighter dim (72% against 52%) to look different. Day reads flatter: the wheels are more "UI on a map" and less "neon in the city".
3. **The enemy forecast tag fights the pointer and banner for the top of the screen.** On the boss, the tag had to move to the gap between the wheels. Needs a layout rule: either the tag goes beside the banner, or the banner carries the forecast.
4. **Busy screen skins against the busy city.** Meridian's corrugated skin and barcode stickers against the dense city is the noisiest mix. The read plate keeps the values clear, but the screen texture gain could drop by about 15% in combat.
5. **The hand cards sit partly off-screen** (their value lines are cut). Only the hovered card shows full text. That is fine if hovering is the way to read a card, but the bottom edge needs a decision.
6. **The second reader on the regular (tick 15) sits on the HP arc gap at the bottom.** It reads, but it is close to the predicted-loss segments.

