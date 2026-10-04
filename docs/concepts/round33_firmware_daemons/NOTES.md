# Round 33: Firmware ("microchips") and Daemons

This round answers GDD_ART_COVERAGE §2.1 and §2.2. Every chip and Daemon drawn here is a real one, with the name, effect text and rarity from `content/firmware/*.tres` and `content/daemons/*.tres`.

## Files

| File | What it shows |
|---|---|
| `firmware_set.png` | All 18 chips at shop size (100 px), each with its name, rarity, valid slices and effect. They are also socketed on an r = 220 wheel and on r = 60 / r = 110 wheels, plus a greyscale check and the rarity legend. |
| `firmware_socket.png` | The anatomy of a slice with a chip, and the chip alongside tiers I–III and six state overlays. It also shows socketing (valid, invalid and occupied slices), the 4-beat trigger cue, and the specific cues for Mirror, Shunt, Burner and Hardened. |
| `firmware_trigger.gif` (2.2 MB) | The wheel lands clockwise of centre on a Mirror slice: the chip flares, a gold trace runs to the neighbour, and the slice reads FIREWALL 5. A second spin lands on Leech: the RAM pip flies to the RAM bar (5 → 6). |
| `firmware_medium.png` | Option A, the socketed die (**recommended**), against option B, the sticker-chip. |
| `daemon_set.png` | All 24 sigils on their CRT tiles, with names, rarity, trigger family and effect. It also has the family colour legend, the rarity treatment, 48 px colour and greyscale, 24 px tiles and 16 px bare sigils. |
| `daemon_row.png` | The Daemon rack on the round 31 combat screen. Kernel Sync and Botnet Seed are firing, Clean Signal is hovered with its tooltip, and Twin Pointer's second pointer sits at the bottom of the wheel. An inset shows the tile states (idle, fire, pips, stack, once, spent). |
| `daemon_trigger.gif` (0.8 MB) | A Perfect lands, then three Daemons fire in turn. Kernel Sync goes from +2 to +3 DMG. Clean Signal reaches 3/3, fires −2 Heat and resets. Botnet Seed drops a drone onto the slice. |
| `shop_v3.png` | The round 32 MAINFRAME shop with real MICROCHIPS and DAEMONS rows. The sign is still round 32's placeholder. |
| `contact_sheet.jpg` | Everything above on one sheet. |

## Firmware: the medium decision

**Recommendation: A, the socketed die.**

- **What it looks like.** A small faceted chip (an octagonal die with 3-tone facets).
  - A gold pin comb runs along one edge. Those pins plug into the slice bezel.
  - The DIP orientation notch is on the opposite edge.
  - There is an LED in the rarity colour, plus 1 to 3 white rarity pips.
  - The effect glyph sits on the dark top plate.
- **Why A:**
  - Slices are CRT hardware, and the GDD's word is "socket". A chip is a part that *changes what the slice does*.
  - The LED is a light source, so the trigger cue comes free.
  - Rarity reads twice (colour and pips), so it survives greyscale and r = 60.
- **Why not B, the sticker-chip:**
  - In the UI kit, stickers are words and things that never change. A sticker reads as a label, not a part.
  - It can't light up.
  - Its white die-cut border fights the tier III gold.
- **The word.** "Microchip" is the shop's section label (the Dymo tape) and the UI word in strings.csv. "Firmware" is the rules word, used in tooltips (`FIRMWARE` tag) and the codex. One object, two registers.
  - *Log in DECISIONS (GDD_ART_COVERAGE 2.1 item 5).*

### The 18 glyphs (effect family, never a slice glyph)

| Firmware | Glyph |
|---|---|
| Patch+ | double plus |
| Hardened | armoured hex with three holes (`***` = ENCRYPTED) |
| Burner | gas-ring burner |
| Leech | fanged drop |
| Mirror | ▶ \| ◀ |
| Shunt | fork with two arrowheads |
| Overvolt | bolt |
| Bulkhead | blast door |
| Siphon | siphon pipe |
| Static Coat | zig-zag shield |
| Barbed Wire | barbed wire |
| Recycler | three-arrow triangle |
| Counterstrike | ⇄ |
| Nanite Mesh | hex cluster |
| Power Cell | battery |
| Tracer | tracer round |
| Skimmer | skimmed coin stack |
| Coolant Loop | radiator coil |

Round 31's mock borrowed slice glyphs (Overvolt = EXPLOIT). These replace them.

### Rarity

The LED and pips follow the content files.

| Rarity | LED | Pips | Firmware |
|---|---|---|---|
| COMMON | cool white | 1 | 12 chips, including the GDD six (Patch+, Hardened, Burner, Leech, Mirror, Shunt), which have no rarity line and so default to COMMON |
| UNCOMMON | cyan | 2 | Counterstrike, Nanite Mesh, Power Cell, Tracer, Skimmer |
| RARE | gold | 3 | Coolant Loop |

The same colours are used for Daemon bezels.

### How a chip attaches to a slice (GDD 6.1, `WheelSlotData.firmware`)

- **The socket.** It sits in the slice's **outer counter-clockwise corner**:
  - polar position: ρ = 326 / 360 of R_OUT, at mid − 0.60 × half-span;
  - chip width: 58 master px.

  The round 17 status badge keeps the outer clockwise corner (mid + 0.66 × half-span). Hardware is on the left and transient status on the right, and neither touches the read block.
- **Orientation.** The chip body is radial, with its pins toward the rim. The glyph is counter-rotated to stay upright, like the read block.
- **The socket lip.** The socket is a dark recess with a 1–2 px lip in the rarity colour. The lip is what still reads at r = 60.
- **LOD:**
  - **r ≥ 150:** glyph on the chip.
  - **r < 150:** the socket rides the bezel itself (ρ 352, 0.70 × half-span), at 0.8× size, with die, LED and pins only. Its name is in the slice tooltip.
  - Enemy wheels use the same socket (`BossPhaseData.wheel_override` can swap chips).
- **Layer order.** Screen > tier pass > state overlay > **chip** > read block.
  - Permanent states from chips (Hardened = ENCRYPTED, Burner = OVERCLOCKED) still draw the normal overlay.
  - A dashed link runs from the chip to the badge, and the badge gets a small pin notch, so the player knows the state is permanent.
- **Socketing (drag from loot, the Modem or a Terminal):**
  - **Valid** slots (`allowed_slice_types`; empty = any) get the lime focus brackets.
  - **Invalid** slots go greyscale at 55 % dark, refuse the drop and show "ATK ONLY".
  - An **occupied** slot shows an amber "REPLACE <chip>?" confirm, and the old chip is destroyed.
  - **OPEN QUESTION for the designer (log in DECISIONS):** the GDD doesn't say whether chips can be replaced, or whether a replaced chip returns to the stash. I picked the simplest option: replace and destroy, with a confirm.

### Trigger cue (the same for every chip, so players learn one grammar)

1. **LAND.** The slice resolves as normal.
2. **FLARE (0.10 s).** The LED, socket lip and pins flash in the rarity colour, with a white-gold bloom over the glyph.
3. **TRACE (0.18 s).** A gold PCB trace runs from the chip along the rim, then in to the read block (or to the neighbour). A bright pulse dot leads it.
4. **PAYOFF.** The effect leaves the chip as a terminal chip or a pip:
   - +1 RAM: a pip flies to the RAM bar (Leech, Power Cell, Recycler);
   - +1 HEAT in Heat orange (Burner);
   - heal, +Cycles, −resistance (the rest).

Specific cues:

- **Mirror:** the trace runs to the neighbour on the landed side, which gets a cyan outline. The slice's own read block dims, and a cyan phosphor ghost of the neighbour's glyph and value replaces it. On a Perfect, both neighbours ghost in, stacked.
- **Shunt:** the trace runs to the neighbour on the side you landed toward, which gets a lime outline and an "x1.5" chip.
- **Hardened:** no flash (it is passive). There is a dashed cyan link from the chip to the ENCRYPTED badge.
- **Burner:** a Heat-orange trace and "+1 HEAT" on every trigger.
- **Coolant Loop, Skimmer:** their once / twice per combat limits show as the LED going dark when spent.

## Daemons: what they are

- **What it looks like.** A Daemon is a **process the Cell keeps running**: a sigil on a small CRT tile. It is in the terminal medium because Daemons are the Cell's systems.
- **Phosphor colour = trigger family.** You can see *when* a Daemon fires before you read it.

| Family | Colour | When it fires |
|---|---|---|
| PERFECT | yellow | on a Perfect |
| MISS | red | on the Miss slice |
| TURN | cyan | combat or turn start, or always-on |
| ACTION | pink | on your nudge or card |
| RUN | lime | after a won fight or a Server Rack capture |
| HEAT | orange | netrun or Heat |

- **Rarity.** It shows on the bezel, with pips at bottom left:
  - Common: gunmetal, 1 pip;
  - Uncommon: cyan edge, 2 pips;
  - Rare: gold bezel and corner brackets, 3 pips.

  The data defaults to UNCOMMON when a file has no rarity line, which covers the GDD six.
- **The sigils.** There are 24, all unique. None is a slice glyph or card picto. The old duplicate (Salvager and Feedback Loop both `picto_again`) is gone:
  - Salvager = crane hook;
  - Feedback Loop = speaker with a feedback arc;
  - Warm Boot = power symbol;
  - Log Wiper = page with an eraser.
- **Readable sizes.** The tile reads at 48 and 24 px. At 16 px, the bare sigil is for tooltip rows and the tray header.
- **Idle animation:**
  - the scan bar rolls (2.4 s period, phase offset per slot);
  - the sigil glow breathes ±12 %;
  - the heartbeat LED blinks once per period.
- **Fire (0.35 s):**
  - white glass flash;
  - the sigil scales ×1.14 with an RGB split;
  - the LED goes solid;
  - a dashed packet line in the family colour runs from the tile to whatever it changes (a read block, a slice, HP, RAM, Heat).
- **Counters** sit under the tile:
  - pips: Clean Signal 3, Cascade 2, Botnet Seed drones 2;
  - a stack: Kernel Sync "+N DMG";
  - READY / SPENT: Stolen Intent. When spent, the glass goes to grey static.

### How Daemons attach (GDD 6.2, 6.3, 4.2)

- **Not on a slice.** Daemons belong to the operative for the run. They live in the **Daemon rack**, a narrow CRT plate on the left edge of the combat screen beside the player wheel.
  - Tiles are 60 px, stacked in install order.
  - With more than 6, the 6th becomes "+N" and opens the tray. The tray is the same tiles in a grid, and it replaces STYLE_GUIDE's "ghost" top-bar icon with the rack plate's header.
- **Daemons that change the wheel:**
  - **Twin Pointer:** a second pointer in Daemon cyan sits at the bottom of the player wheel, carrying the sigil. When both pointers trigger, it pulses with the top pointer and a "TWIN READ: <slice>" chip shows.
  - **Botnet Seed:** its 1-HP drone (round 17 drone glyph, Botnet yellow ring, HP tag) docks on the triggered slice's outer clockwise rim. The tile's pips count drones (max 2).
  - **Zero Day:** a Perfect on the Miss slice turns its read block into a ZERO-DAY-style CRIT burst with "x3". It reuses the CRIT screen; it is not drawn yet.
  - **Stolen Intent:** two swap arrows between the wheels' resolved slices, then the tile goes SPENT. Not drawn yet.
  - **Linked Bus:** a ghosted copy of the nudge arc on your wheel. Not drawn yet.
- **Not drawn yet:** the Mirror elite's "hub running your data Daemons" (GDD 8.5). Proposal: the elite's hub shows your rack's tiles in a ring, recoloured to the elite's corp tint.

## Shop (shop_v3.png)

- **MICROCHIPS.** Chips hang **pins-first in a pink anti-static foam strip** (how loose chips are really stored).
  - Each has a Dymo name, a kraft price tag (Firmware 75–150, GDD 11.2), and its rarity plus valid slots in mono.
  - Hover gives a terminal tooltip with VALID and "drag onto a slot". Dropping opens the mini spinner from `firmware_socket.png`.
- **DAEMONS.** Each tile sits in a **cartridge housing** on a hook (a process sold as a cartridge), with a Dymo name and a tag (150–250).
  - An unaffordable tag prints red, with the grease-pencil note "can't afford".

## Godot build notes

- **Chip** = `TextureRect` children of the slice node.
  - The socket lip (a 9-patch in the rarity colour), the die body (one atlas texture per rarity: facets, pins, LED off) and the LED as its own sprite with an additive glow.
  - The glyph sprite uses `top_level` rotation 0 to stay upright, the same as the read block.
  - **Order:** after the overlay CanvasItem, before the read block.
  - **Position:** from `SOCKET_RHO` / `SOCKET_DA` (the constants in `scripts/fwlib.py`). These are tuning values, so they go in config.
- **Trigger:**
  - an `AnimationPlayer` on the chip: LED energy 1 → 3 → 1, then lip modulate;
  - the trace is a `Line2D`, with points from the rim arc, a width curve, and its gradient offset tweened 0 → 1 over 0.18 s;
  - the payoff chips are the round 31 toast / terminal-chip scene.

  All of it comes from a `firmware_triggered(slot, effect)` signal emitted by the combat view (Signal Up).
- **Daemon tile** = a `Panel` (bezel 9-patch per rarity) with a `TextureRect` sigil, under one shared CRT `ShaderMaterial`:
  - uniforms `phosphor`, `fire`, `phase` and `spent`;
  - scanlines, the roll bar, the RGB split and the static are all in the shader.

  The counter is a small HBox under it. The packet line is a `Line2D` with a dash texture.
  - Fire order within the same hook: rack order, top-down, 0.12 s stagger (deterministic: install order, then content id).
- **Twin Pointer** is a second pointer node on the wheel, and its visibility follows the Daemon. **Botnet drones** reuse the DEPLOY dock node.
- **Sigils and glyphs** are flat white 256 px masks. Export them from `fwlib.icon()` (2 px ink outline at small sizes), tinted with `modulate`.

## Scripts (`scripts/`)

| Script | What it does |
|---|---|
| `fwlib.py` | The content tables, the 42 glyph and sigil drawings, `chip()`, `daemon_tile()`, `counter_strip()`, `socket_wheel()` |
| `fwfx.py` | Trigger FX: scenes, trace, ghost, outline, pops, RAM bar |
| `firmware_set.py` | Builds `firmware_set.png` |
| `firmware_socket.py` | `[still\|gif\|all]` builds `firmware_socket.png` and `firmware_trigger.gif` |
| `firmware_medium.py` | Builds `firmware_medium.png` |
| `daemon_set.py` | Builds `daemon_set.png` |
| `daemon_row.py` | `[still\|gif\|all]` builds `daemon_row.png` and `daemon_trigger.gif` |
| `shop3.py` | Builds `shop_v3.png` (imports round 32's `shop2.py`; the `placeholder()` boxes are swapped out) |
| `contact.py` | Builds `contact_sheet.jpg` |

- **Copied from round 32:** `r31lib.py`, `sticker_lib19.py`, `shop.py`, `shop2.py`, `removal.py`, `assets.py` and `lib17/`.
- **Inspection helpers:** `icon_check.py`, `crop.py` and `gif_sheet.py` write to `scratch/probe/`.
- **Cleanup:** `clear_scratch.py` removes `scratch/` and the caches.
- **Randomness:** all of it is seeded.
