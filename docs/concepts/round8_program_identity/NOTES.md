# Round 8: program identity (V2 "living programs", bold imagery)

## What I kept and what I changed

**Kept from earlier rounds:**
- C's CRT slice frame: scanlines, phosphor glow, barrel bulge, per-slice bezel.
- V2's telemetry readout ring, unchanged.
- The white glyph and value on a dark plate.

**Changed:** the faint V2 mascot is replaced by a bold, original splash image per program,
drawn to fill the screen behind the glyph.

How each slice screen is built:
1. A copy of the program's own screen (hex dump, brick text, and so on), dimmed to 30%, so it still reads as a hacker splash screen.
2. A category glow.
3. The image, drawn as shaded silhouette layers: an ink outline, a vertical gradient, a top-left rim light and a bottom-right core shadow. It is sized to the full screen height.
4. A tight, strong plate (84%) just under the glyph block, so the image stays visible all around it.

On enemies, the corp skin shows through and the image is tinted 45% toward the corp colour.

## Icon taxonomy

**Primary** is used on the wheels. Images marked **\*** belong to proposed programs or variants that
are not slice types in `content/` yet: PHISHING, SHIELD, ENCRYPT, RECON.

| Category | Program (slice type) | Primary | Alternates | Animation idea |
|---|---|---|---|---|
| **ATTACK** (pink / red / orange) | EXPLOIT (ATTACK) | flaming skull | fire, bomb (skull mark, lit fuse) | flames flicker, eyes pulse |
| | ZERO-DAY (CRIT) | skull, strengthened: cracked, glowing sockets | skull with a lit bomb fuse; skull and crossbones | jaw chatters, glitch slice |
| | VIRUS (AFFLICT) | poison vial (skull label) | biohazard bug; storm cloud raining corrupt pixels | poison drips and bubbles; the bug's legs skitter; lightning flashes |
| | TROJAN (DEPLOY) | Trojan horse on wheels, belly hatch glowing with a skull payload | open envelope with a bomb emerging | the eye turns red, the payload pulses; the fuse sparks |
| | PHISHING \* (AFFLICT / DEPLOY) | phishing hook with an envelope | hook carrying a `***` password card | the hook sways |
| **DEFENCE** (cyan / steel) | FIREWALL (DEFEND) | burning brick wall (steel bricks + fire) | brick wall with a shield | the wall burns |
| | SANDBOX (SHIELD) | bank-vault door | steel safe with a dial | bolts slide, the wheel turns, it seals (lamp on); the dial spins |
| | SHIELD \* variant | riveted shield | blast door | the blast doors close and the seam light dies |
| | ENCRYPT \* | padlock with a `***` password field | heavy padlock (keyhole) | `***` typing; the shackle snaps shut |
| **UTILITY** (green / violet) | PROXY (EVADE) | anonymous mask: an original theatre mask with slanted slits, cheek bars and a thin smile (no moustache or goatee) | cloud with speed lines (EVADE) | mask glitch slices; the cloud drifts |
| | PATCH (HEAL) | key with a spark | fingerprint with a scan line; chip being repaired | the spark glints; the scan sweeps; a repair trace runs across the crack |
| | NULL (MISS) | magnifying glass over empty static (grey glow) | unplugged chip ("z z") | the static crawls |
| | RECON \* | magnifier over scrolling code | debug bug `</>`; `***` password dialog | code scrolls; typing |

The padlock is now **defence only** (ENCRYPT and the Citation special). No attack uses it.

Special enemy slices map to the same library:

| Special | Image |
|---|---|
| Tariff | phishing hook (it fishes for your RAM) |
| Dose | poison vial |
| Solar Flare | storm cloud |
| Citation | padlock |

## Files
| File | What it shows |
|---|---|
| `identity_library.png` | Each primary and alternate as a 3-tick tile, how it actually plays, with the raw image underneath. Grouped Attack / Defence / Utility. |
| `wheel_breaker.png`, `wheel_ghost.png` | Hero player wheels with primary images and the V2 telemetry ring. |
| `wheel_enemy_meridian.png` | Drone Dispatcher: Meridian container skin, corp-tinted art, Tariff as the phishing hook, docked couriers. |
| `boss_manifest.png` | V2 hologram crown and a second ring of 12 programs, with the same art. |
| `anim.gif` (1.4 MB), `anim_strip.png` | 6 programs over a 24-frame loop. |
| `small_and_grey.png` | r = 60 colour and greyscale, plus the hero in greyscale. |
| `scripts/` | `icons8.py` (the 31 images), `make_round8.py [library\|wheels\|anim\|small\|all]`, and the round 6/7 scripts it builds on. |

## Readability
- **Wide wheel slices (60°, real data).** The image wraps around the glyph and reads clearly.
- **3-tick tiles.** The glyph block covers the middle of the image. Each image is built so its key feature still shows: flames above, the vial's liquid below, the wall's fire line.
- **r = 60.** The glyph and value stay readable. The images become category-coloured shapes, which still help: skull white, wall cyan.
- **Greyscale.** Images keep their silhouettes thanks to the ink outline and rim light.

## Picks and open questions
**My picks:**
- skull (ZERO-DAY);
- flaming skull (EXPLOIT);
- burning wall (FIREWALL);
- vault door (SANDBOX);
- anonymous mask (PROXY);
- poison vial (VIRUS).

**Open questions for the designer:**
1. Should PHISHING, ENCRYPT, RECON or a SHIELD variant become real programs? They need data.
2. Should PATCH lead with the key or with the fingerprint?
