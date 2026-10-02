# Round 20: raid UI (the world half is in `round20_raid_world/`)

Locked from round 19 and kept as they were:
- lime links;
- the node status key;
- city detail;
- the EXPOSED spotlight gif (still a proposal for the GDD);
- the CELL HOLDS sticker stamp.

## Files
| File | What |
|---|---|
| `raid_setup_night.png` | Setup with option E panels. Threat routes are back to **red grease pencil**, and the ICE LOCK card hovers over the Vault. |
| `raid_wave_night.png` | Playout: pencil routes, DOWN / INCOMING marks (they wipe, see gifs), health drained by lit fraction, hover numbers on the Safehouse. |
| `raid_result.png` | **Post-raid report**: the CELL HOLDS stamp, nodes kept / disabled with the repair cost, Schematics, and the **Heat change settled here**. |
| `node_health.png` + `node_health.gif` | The health combo: sequence strip, hover / always-show numbers, and the wave with always-show on. |
| `threat_lured.png` + `interactions_gifs/16_threat_lured_decoy.gif` | Tile 17 redone: the decoy on its node, the original pencil route, then the dashed bend to the decoy. |
| `panel_mediums_v2.png` + `panel_options/opt_*.png` | Five panel mediums, each on the full setup screen, with matching speed / skip controls. |
| `interactions_gifs/` | 27 looping gifs (each ≤ 2 MB), plus `index.md` and `index.jpg`. |
| `contact_sheet.jpg`, `scripts/` | |

Rebuild:
1. `python scripts/run_blender.py`
2. `blender -b --factory-startup --python scripts/vehicles.py -- <abs>/scratch/bl sprites` (the Halcyon sprites at 4 headings)
3. `python scripts/screens20.py`

Everything is seeded.

## Changes from round 19
1. **Routes are red grease pencil again** (`ui20.pencil_routes`). The red trace lanes are gone from the street; the street only carries our own network, sockets and threat rings.
2. **Pencil state marks wipe away.** DOWN, INCOMING, LOST and the routes of a cleared wave write on, hold for a beat, then a cloth wipe sweeps across and leaves a faint smear that fades (`Pencil.composite(wipe=…)`). BREACHED stays, because it is the end state.
   - Gifs: 12 (incoming), 17 (down), 20 (lost), 23 (wave cleared).
   - Suggested timing: write ~0.4 s, hold ~1.5 s, wipe ~0.4 s.
3. **The DECOY lure is clear now:**
   1. The decoy pylon (violet holo rings + a hook) stands on the Relay socket and broadcasts violet rings over the street.
   2. The threat's original route B is drawn in solid pencil.
   3. When the threat re-targets, the abandoned segment wipes and a dashed pencil bend draws to the decoy; the unit follows it.

   This is true to `raid_resolver._target_of`: only `decoy_pull` assets re-route, and the strongest pull wins.
4. **Node health combo** (`netdecal20.health_pad`):
   - Health is how much of the socket is **lit**. Damage fades it from the **north** point (screen top) toward the south.
   - The faded part takes the disabled look (dashed frame, dark pins, dim glyph) but keeps the active colour. A thin bright front marks the drain line.
   - At 0 the socket switches to the disabled amber with the dashed outline.
   - Numbers appear only on **hover** (or with an Options toggle, *Always show node health*) as diegetic floats above the north point: a numeral plus a 10-segment bar, coloured lime / amber / red by health.
5. **Gifs for everything that changes.** Round 19's tiles 16 (ice), 17 (decoy) and 25 (escalation) are fixed:
   - Ice is now gif 15: the unit stops on the Firewall, the ring freezes into an ice crystal, it frosts, shows HELD 2 > 1, then moves on.
   - Decoy is gif 16.
   - Escalation is removed (point 6).
6. **No Heat escalation during the raid.** Per GDD 4.3–4.4 / 11.5, Heat sets raid strength *before* the raid (shown in the intel line `STRENGTH +52% (HEAT)`). The only raid-related Heat change comes after it: +5 for a lost raid (`config.lost_raid_heat`), ±0 for a win. A won raid pays Schematics (GDD 11.4).
   - The result screen (`raid_result.png`, gif 24) shows the stamp, every node kept / disabled / lost with its repair cost, the reward and the Heat line.
   - The in-raid escalation state is removed from the interaction list.
7. **Panel mediums v2.** Each medium follows what the panel *is* in the fiction:

   | Panel | In the fiction | Fits |
   |---|---|---|
   | YOUR NETWORK | the Cell's own system status | C screens & data (it is our computer) |
   | RAID INCOMING | an intercepted Halcyon work order | a corp document: printout, letterhead, redactions, INTERCEPTED stamp |
   | THREAT INTEL | scanned / decrypted surveillance | a sensor readout: holo with the scanned vehicle silhouettes |
   | LOADOUT | the armory's physical assets | stickers (static objects), unchanged |
   | SPEED / SKIP | a control on the Cell's deck | the same medium as the network panel |

   The five options, each shown on the full setup screen:
   - **A, projected holo** (the designer's lean): every panel is a projected readout with an emitter bar and light fan. Round 20 adds a dark scrim behind the holo so it keeps contrast over neon. Speed / skip uses holo buttons.
   - **B, CRT monitor bezels:** each panel is a small physical monitor (plastic bezel, curved glass, power LED, CELL-OS label). Speed / skip uses chunky hardware keys with an amber step readout.
   - **C, tablet glass pane:** a smoked glass slate. **Grease pencil is allowed on it**: the Cell circled the Vault-priority line in red. Speed / skip uses etched touch buttons.
   - **D, decrypted windows:** OS windows (`CELL_NET.exe`, `DECRYPT_v3.exe`) around C screens, with a progress bar and glitch slices. The Halcyon seal is cracked red on corp files. Speed / skip uses a terminal strip.
   - **E, by fiction (recommended):** network = CRT terminal, order = intercepted memo under glass, intel = surveillance holo. Every medium sits where its fiction puts it, and the holo the designer leans toward carries the intel, where "scanned" makes it most believable. If one medium must cover everything, A (holo) with B or D as the fallback.
   - **Known gap:** the IF PLACED preview is a CRT terminal in all five options; a production pass should match it to the chosen medium.
8. **Speed / skip match each medium** (`ui20.speed_ctrl`, shown on every option screen).

## A note for the designer: Vault priority
GDD §3.2 says of the Vault Terminal: "raids prioritise it". In the code this is `raid_priority` on the node, read by HIGHEST_VALUE threats (`_target_of`). So intel that says a threat goes for the VAULT is **true to the rules for HIGHEST_VALUE threats**. Couriers, Inspectors and Landers do this; WEAKEST_NODE threats such as the Bailiff and Hauler do not. Round 19 removed "THEY WANT THE VAULT" as untrue; it would be correct if it is attached to those threats only. Round 20 intel rows read `> weakest node / > VAULT (priority)` per pair.

## Weakest / open
- **Threat sprites are small at map zoom.** The Halcyon units read mostly by their red ring and the pencil, so the threat-moving gifs are best watched at full size.
- **The wipe smear** is a single stroke; a real cloth wipe might want a streak texture.
- **Decrypt windows (D):** the glitch slices cost some legibility, by design. Tune them down if D is chosen.
- **For the designer:**
  - Pick a panel medium (E recommended; A if one medium for all).
  - Say whether *Always show node health* defaults to off.
  - Decide whether EXPOSED goes into the GDD.
