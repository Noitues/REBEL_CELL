# Round 34: Firmware socket moved to the core side, Daemon colours, FIRMWARE shop label

## Designer's verdict on round 33

- **Firmware:** the socketed die was chosen over the sticker-chip.
- **Daemons:** the sigils, the combat rack and the animations were approved.

Round 33 stays as it was. This round only changes three things.

## 1. The Firmware socket moves to the inner (hub-side) band

**Placement**
- The chip now sits on the slice midline, in the band between the hub ring and the read block.
- It is rotated radially so its **pins point into the core**: the slice reads as if it were wired from the core outward.
  - The glyph stays upright, like the read block.
- Constants in `scripts/fwlib.py` (these are tuning numbers, so they go in config):
  - `SOCKET_RHO = 160` master px (the range is R_IN 130 to R_OUT 360);
  - `SOCKET_DA = 0`;
  - `CHIP_MASTER = 50`.
- **Below r = 150 (the LOD):** the chip shows only the die, LED, pins and the rarity-coloured lip, at 0.9×. It keeps the same position.

**Collision checks**

| Check | Result |
|---|---|
| r = 220 wheel, all 6 slices | Clear, including the side slices, where the upright read block reaches furthest toward the hub ("12" on ZERO-DAY). The first try at ρ 176 / 54 px touched "12"; the final values are ρ 160 / 50 px. |
| Tiers I–III | Clear. The tier flair is inside the border, so the chip sits inside the gold III border. |
| State overlays (6) | Clear. The chip draws over the overlay and under the read block. |
| Status badge | Untouched: it stays in the outer clockwise corner. |
| r = 60 and r = 110 | The chip stays in the band, clear of the values. |

**One change to locked art.** The round 17 OVERCLOCKED / PARASITE rule tags (x1.5 / x0.5) used to sit at the inner edge, which is where the socket now goes. They now sit just under their status badge, in the outer clockwise corner.
- This is a one-line move in this round's copy of `lib17/overlays.py`.
- **It needs the designer's OK.**

**The trace now runs core outward.**
- On its own slice, the gold trace runs from the chip straight up into the read block.
- For a neighbour (Mirror, Shunt), it drops to a "bus" on the hub ring (ρ 140), runs along it, then rises into the neighbour's read block.

**Redone files**
- `firmware_socket.png`
- `firmware_trigger.gif` (2.1 MB)
- `firmware_set.png`, with the r = 220 and r = 60/110 wheels

## 2. Daemon colours: MISS and ACTION are now well apart

| Family | Round 33 | Round 34 |
|---|---|---|
| ACTION | pink `#FF5CBE` | violet-lavender `#BA92FF` (lighter) |
| MISS | `#FF5460` | deeper red `#EC303A` (darker) |

The other four families are unchanged.

`daemon_colours.png` checks the pair (Fault Tolerance vs Tuning Fork) in colour, greyscale, and under protan, deutan and tritan simulation (Machado 2009, applied in linear RGB). ΔE is CIE76.

| View | Round 33 | Round 34 |
|---|---|---|
| Normal ΔE | 50 | 97 |
| Protan ΔE | 49 | 80 |
| Deutan ΔE | 49 | 97 |
| Tritan ΔE | **21** | 94 |
| Greyscale luma | **136 vs 151** | 105 vs 170 |

- **Other close pairs.** Some pairs stay close under colour-blind simulation (PERFECT / RUN, RUN / HEAT).
  - Colour is the second cue only. Each Daemon has its own sigil, and every tooltip names its family.
  - If the designer wants all six families to separate under every simulation, the next step is a shape cue for each family on the tile's LED.
- **Re-rendered with the new colours:** `daemon_set.png`, `daemon_row.png` and `daemon_trigger.gif`.

## 3. The shop says FIRMWARE

`shop_v3.png` is built on round 33's latest layout: the offscreen slice wheel and the recycle bin. `scripts/shop_layout.py` is a copy of `round33_shop/scripts/shop3.py` with two changes:
- the section label reads **FIRMWARE**;
- the placeholders are removed.

`shop_v3.py` draws the two rows.

**FIRMWARE row**
- 3 chips pushed pins-first into the anti-static foam: Overvolt 80, Skimmer 110 (hovered), Coolant Loop 150.
- Each has a Dymo name, rarity, valid slots and a price tag.
- A terminal tooltip shows VALID: ATK.

**DAEMONS row**
- Kernel Sync 150 and Twin Pointer 245, as tiles in cartridge housings.
- Twin Pointer's tag prints red because the wallet is 160.

**Naming.** "Microchip" no longer appears in the UI. The `strings.csv` "MICROCHIPS" key should become FIRMWARE; log this in DECISIONS.

## Scripts

| Script | What it builds |
|---|---|
| `firmware_set.py` | `firmware_set.png` |
| `firmware_socket.py [still\|gif]` | `firmware_socket.png` and `firmware_trigger.gif` |
| `daemon_colours.py` | `daemon_colours.png` |
| `daemon_set.py` | `daemon_set.png` |
| `daemon_row.py [still\|gif]` | `daemon_row.png` and `daemon_trigger.gif` |
| `shop_v3.py` | `shop_v3.png` |
| `contact.py` | `contact_sheet.jpg` |

- **Copied from earlier rounds:** `fwlib.py` and `fwfx.py` (round 33, updated here); `r31lib.py`, `sticker_lib19.py`, `shop.py` and `removal.py`; `shop2.py`, `assets.py` and `recycle.py` (from round33_shop); `lib17/`.
- **Cleanup:** `clear_scratch.py` empties `scratch/`.
- **Randomness:** all of it is seeded.
