# GDD art coverage audit (2026-10-03)

**Why this exists.** Microchips and Daemons appeared in the round 31 shop mockup without ever having had a concept pass. This audit re-reads the rules and checks every game element that needs a visual design against the concept rounds.

**Sources read:**
- `docs/GDD.md`, read in full.
- `docs/DECISIONS.md`: the milestone entries M0–M12 and batches 1–5, where later systems were added.
- `content/`: a count of every `.tres` type.
- The `scripts/data/` schemas: `rc.gd`, `firmware_data.gd`, `daemon_data.gd`, `wheel_slot_data.gd`, `exploit_data.gd`, `netrun_boost_data.gd` and `threat_data.gd`.
- `docs/art_asset.md` in the main checkout (read only).
- `docs/concepts/DIRECTION_REVIEW.md`, read in full.
- Every round's `NOTES.md`, plus the round 31 scripts, to see what the shop and reward mockups actually draw.

**Status key:**
- **locked**: DIRECTION_REVIEW records a designer lock.
- **in progress**: a concept exists, but it is unconfirmed or still being iterated. All of round 31 is in this state, because DIRECTION_REVIEW has no round 31 decisions yet.
- **missing**: no concept in the current (Cv2 + E, sticker / grease pencil / CRT) direction.

"Pre-direction only" means the item was only drawn before the direction was locked: in rounds 1–9, or in the W4/W5 pixel-art briefs under `docs/art_briefs/`.

## 0. Two facts first

1. **"Microchips" are Firmware.** The GDD never uses the word "Microchip". Both the game UI and art_asset use it as the Modem's shop-section label for Firmware:
   - art_asset G18: "four sections: Microchips (firmware), Cards, Slices, Daemons";
   - `assets/text/strings.csv`: "MICROCHIPS" and "Drag a microchip or a slice onto a slot";
   - DECISIONS ANIM-4b: "a microchip onto a slot of the new small spinner = 'Socket into Slot N'".

   So this is not a separate system. It is the GDD §6.1 Firmware system, and it has never had a design.
2. **Daemons are the GDD's run-wide relics** (GDD §6.2, `DaemonData`). There are 24 in content. The only art of them is a generic round 31 hex badge that reuses existing pictograms.

## Content inventory (counted from `content/`)

| Type | Count | Folder |
|---|---|---|
| Cards | 71 | `content/cards/` |
| Classes | 8 (4 base + 4 alternatives) | `content/classes/` |
| Hub cores | 17 files: 8 class cores, 8 Mk2 cores and Compliance Lock. The other enemy hubs (Auto-Renew, Priority Routing, Emergency Powers, Station Keeping, Root Access) are inline in the enemy files; art_asset counts 22. | `content/hub_cores/` |
| Inner rings / segments | 4 class rings / 7 segments | `content/rings/`, `content/rings/segments/` |
| Slices | 38 | `content/slices/` |
| Firmware ("microchips") | 18 | `content/firmware/` |
| Daemons | 24 | `content/daemons/` |
| Enemies | 58: regulars, elites, mini-bosses, 5 bosses and drone templates | `content/enemies/` |
| Corporations | 5 | `content/corporations/` |
| Events | 124 | `content/events/` |
| Network nodes | 11: 6 node types and 5 home-server variants | `content/nodes/` |
| Defence assets | 8 | `content/assets/` |
| Threats | 17 | `content/threats/` |
| Raids | 40 | `content/raids/` |
| Profile unlocks | 18 | `content/unlocks/` |
| Netrun boosts | 2 files (Field Kit, Overclocked Deck) plus `netrun_boosts.tres`. DECISIONS batch 2a also names Warm Cache. | `content/config/` |
| Voice line sets | 20 | `content/voice/` |
| Exploits | 3 kinds × 5 corporations = 15 named (inline in the corporations) | `ExploitData` |

---

## 1. Coverage table

### 1.1 Combat (wheel mechanics and the HUD)

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Wheel frame / bezel | GDD 2.1; art_asset E1 | round4, round7 (V2), round13_wheel_details (D4) | locked | D4 "Lens & rail" for every wheel. |
| Pointer (needle), 30-tick scale, Perfect mark | GDD 2.1, 2.3, 2.4 | round13_wheel_details D4 blade | in progress | The backlog still has "Wheel details: pointer, hub readout, 3D/layered depth" unticked. |
| Multiple pointers; Multiply / Migrate / Orbit | GDD 2.1, 2.11, 9.2 ("migrating pointers flicker a turn early; orbiting pointers show a trail") | round6_roster (numbered needles, orbit arc + ghost pointer); round13 D4 boss threat ring with NEXT telegraphs; round20/23 phase change (second needle) | in progress | Phase change v3 is locked. The Migrate flicker and the Orbit trail have only been drawn in pre-lock round 6. |
| Precision landing: Perfect / Good / Partial, and the Miss slice | GDD 2.4; GDD 10: "Perfect = latch + wheel-local inversion + 2-frame freeze; Good = clean click; Partial = stutter; Miss slice = static burst" | aim pips only (round10 and round14 "●●○ GOOD" chip) | **missing** | This is the core skill read (pillar 1), and the landing moment itself has no FX concept. |
| Nudge + spin resistance | GDD 2.5 | round20_combat_fx | locked | The `R n` hub badge is from round 6. |
| Spin (card) | GDD 2.5 | round18_combat_fx card play | locked | |
| Respin | GDD 2.5, 11.3 | round20/23 | locked | The label is RESPIN, not CHECKPOINT. |
| **Flip** | GDD 2.3, 2.5 (Mirror Flip, Flip Switch) | none | **missing** | The mirror move across the horizontal axis has never been drawn. Its audio "mechanical clack" is in GDD 10. |
| **Freeze** (wheel skips its next respin) | GDD 2.5; Freeze / Cold Snap / Blind Spot cards | FROZEN slice overlay (round13–15) | mismatch | The art is a *slice* state. The rule is *wheel-level*; round 13 itself notes this. |
| Card-play preview (ghost blade, ghost drones) | GDD 2.10, 9.2 | round14–17 | locked | Animated version. |
| Forecast tag / NEXT / LAST TURN / odds | GDD 2.10; art_asset E1 | partial: round10, round14 option B chip | in progress | No concept for the odds display (Respin, random picks) or for LETHAL. |
| Rewind / UNDO / checkpoint | GDD 2.10 | round23 (UNDO button holds the undo block) | in progress | No rewind effect is drawn. |
| Three-pass resolution (defence → offence → statuses / Daemon hooks) | GDD 2.2.3 | none | **missing** | The sequencing beat is undesigned. Damage, block and heal FX exist individually. |
| Damage shards (hit, crit) | GDD 2.6 | binary_damage, round18/19 | locked | |
| Block / Shield walls, Heal, Evade | GDD 2.6 | round19–23 | locked | Evade v4. |
| Enemy defeated / break | art_asset E1 | round19, round23 v2 | locked | **Enemy entering** is missing. |
| Hub Breach (enemy Hub disabled 1 turn) | GDD 2.8; Hub Breach / Shatter / Short Circuit cards | BREACH glyph only (round14) | **missing** | There is no "breached hub" state on the wheel. Every boss hinges on it (Auto-Renew, Priority Routing and the others heal or shield "unless Hub-Breached"). |
| Enemy satellites (mini-wheel, own intent, bodyguard, Undock) | GDD 2.1 ("2–3-slice mini-wheels (10 or 15 ticks per slice)"), 2.7 | round6 (CRT token + HP pill); round19/20/22 (drone deploy, destroyed); UNDOCK glyph | in progress | Drawn only as tokens. **No concept shows a satellite's own 2–3-slice mini-wheel and intent**, which the GDD requires. |
| Player drones (Botnet) | GDD 5.2 | round19 deploy, round22 destroyed v3 | locked | |
| Status overlays: CORRUPTED / OVERCLOCKED / ENCRYPTED / PARASITE | GDD 2.9; DECISIONS M6 (PARASITE) | round13–15; round23 corrupt apply v4 / tick v3 | locked | Apply FX exist for CORRUPTED only. OVERCLOCK (Overdrive, Hot Patch, Solar Flare), ENCRYPT and PARASITE apply FX are missing. |
| RAM meter / RAM gain | GDD 2.2, 11.3 | round20/21 (gain from the TURN banner) | in progress | Gain is locked. The meter, pending cost and refusal are not designed. |
| SEND IT | art_asset E6 | round22 | locked | |
| Heat on the combat screen | GDD 9.4 | round19–22 (H1 "city reacts") | locked | The glitch shader is an Options extra only. |
| Combat backdrop | art_asset C4 | round11, round24–30 | locked (per corporation) | REBEL_CELL is in progress (round 29). |
| **Daemon row in combat** | art_asset E6: "The installed daemons as sigils" | none | **missing** | See §2.2. |
| Operative portrait in the combat column | art_asset E6, B1 | round31 busts (treatment proof only) | in progress | |
| Tutorial overlay (7 steps) | DECISIONS batch 4 | none | **missing** | |

### 1.2 Cards

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Card frame | art_asset E5 | round4 C-C sticker card | locked | |
| Play: peel / slap / dissolve A | — | round18–19 | locked | |
| Card art (71 cards) | `content/cards/`; GDD A.1–A.2 | W4 briefs (35 families + 12 unique, pixel art) | **missing** | Pre-direction only. No card illustration exists in the locked style. |
| Card pictograms | art_asset E5 | round13–17 glyph pass | locked | The final package is exported (round 17). |
| Rarity on the card | `CardData.rarity`; art_asset F3 | none | **missing** | art_asset Part M #6. |
| Card type band (WHEEL / HACK / SYSTEM) | not in GDD or `CardData`; ART_BIBLE 7.3 colour only | round31 | mismatch | See §3. |
| Card states (can't afford, exhaust, discard, deal, deck/discard piles) | art_asset E5 | EXHAUST glyph (round14) | in progress | |
| Bug card (ICE 11–15) | GDD 11.9 | none | **missing** | |

### 1.3 Wheel and slices

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| 9 slice types (screen family C) | GDD 2.6; `RC.SliceType` | round5_slices/s_c, round6, round10, round13–17 | locked | The concept renames each type as a "program": see §3. |
| Corporation specials (Dose, Tariff, Citation, Solar Flare, Inertia) | GDD 8.3–8.4d; `content/slices/` | round13–19 corp kits | locked | Renames are pending: Tariff → PRIORITY, Inertia → WEIGHT, Heal → GROWTH. |
| Drain variants (`atk_7_drain`, `crit_12_drain`) | `content/slices/` | round13 ("−n RAM" chip) | locked | |
| Slice overwrite (Modem) | GDD 11.2 ("slice overwrite 100 (Miss slice 150)") | round31 shop tile "OVERWRITE 1 SLOT" | in progress | |
| Slice upgrade tiers I–III | **not in GDD** | round13–16 (V2 strong) | locked art / no rule | On the game to-do list. |
| **Firmware socket on a slice** | GDD 6.1 ("one socket per slice"); `WheelSlotData.firmware`; art_asset E1 ("has a firmware chip"), Part I ("firmware socket") | none | **missing** | See §2.1. |

### 1.4 Operatives and classes

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Class bezel ornament + accent colour (8) | GDD 5.2; art_asset B1 | round6_roster | in progress | Drawn before D4. D4 is "LOCKED for every wheel", but no round shows the class ornaments on D4. |
| Class emblem / mark | art_asset B1 | round6; round21 R3 class beacons | locked (as beacons) | |
| Character concept / full figure / bust | art_asset B1 | round31 Breaker bust (treatment proof); W5 pixel briefs | **missing** | Round 31 says: "Portraits get a dedicated pass later". |
| Portrait states (hurt, triumphant, flatlined, stationed, recruit) | art_asset B1 | round31 dialogue A (CRT feed proposal) | in progress | |
| Rank 0–3 indicator | GDD 5.3 | none | **missing** | |
| Stationing (beacon, station-bonus FX) | GDD 5.2, 5.4 | round20–22 | locked | Botnet "free asset per raid" is not drawn. |
| Crew roster / dossier / crew chip / recruit | GDD 5.4; art_asset H | round31_ui_chrome (Grid HUD roster) | in progress | The HQ dossier is missing. |

### 1.5 Hub cores

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Class Core emblem (8) | GDD 2.8, 5.2; `content/hub_cores/` | round6: hub core *name text* + class mark | **missing** | No emblem per core. art_asset Part M #10: "Hub cores ... are text only". |
| Mk2 cores (Rank 2 "Upgraded Hub Core") | GDD 5.3; DECISIONS M6 | none | **missing** | |
| Enemy hub passives (Compliance Lock, Auto-Renew, Priority Routing, Emergency Powers, Station Keeping, Root Access) | GDD 2.8, A.3, 8.4b–d; DECISIONS M8–M11 | round6: `R n HUB LOCK` badge only | **missing** | Boss hubs are what Hub Breach turns off. |
| Hub Breach state | GDD 2.8 | none | **missing** | See §1.1. |

### 1.6 Inner rings

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Inner ring (3 × 10-tick segments, independent rotation) | GDD 2.1, 6.4 | round6, round7, round10; round13 D4 (the hub "carries name, core and ring") | in progress | There is no locked D4 ring drawing. |
| Segment marks: ×2, Pierce, Corrupt, Anchor, Accelerator, Echo, blank | GDD 6.4; `content/rings/segments/` | round6 labels + glyphs (pre-lock) | **missing** | They are absent from the round 13–17 glyph pass. **Anchor has never been drawn.** |
| Segment triggers (Echo retrigger, ×2, Pierce) | GDD 6.4 | none | **missing** | |
| Rank 3 segment-swap UI | GDD 5.3; DECISIONS batch 1 | none | **missing** | |

### 1.7 Firmware ("Microchips")

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| 18 Firmware items | GDD 6.1, A.4; `content/firmware/`; DECISIONS M7 | round31 `chip_art` (generic die with pins, plus a borrowed slice glyph: Overvolt = `slice_exploit`, Static Coat = `slice_sandbox`) | **missing** (placeholder only) | No per-chip design. See §2.1. |
| Firmware drop (loot) with mini spinner + valid slots | art_asset G17; DECISIONS ANIM-4b | round31 `reward.py` firmware panel | in progress | |
| Modem MICROCHIPS section | art_asset G18 | round31 shop (pegboard) | in progress | |
| Chip shown on the wheel (player and enemy) | GDD 6.1; `WheelSlotData`; `BossPhaseData.wheel_override` swaps Firmware | none | **missing** | |
| Firmware trigger feedback | GDD 6.1 | none | **missing** | Covers Mirror / Shunt neighbour, Burner +Heat, Leech RAM and Hardened ENCRYPTED. |

### 1.8 Daemons

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| 24 Daemon sigils | GDD 6.2, A.4; `content/daemons/`; DECISIONS M7 | round31 `daemon_art` ("hex badge (run-wide rule), glyph in a ghostly ring") reusing pictos | **missing** (placeholder only) | Warm Boot = `picto_ram`; Salvager and Feedback Loop both = `picto_again`; Log Wiper = `status_cleanse`. See §2.2. |
| Daemon row / DAEMONS top-bar icon / Daemon tray | art_asset E6, G25, H | none | **missing** | STYLE_GUIDE icon is "ghost". |
| Daemon offers (Modem, Server Rack, Terminal) | GDD 6.3 | round31 shop and server_rack | in progress | |
| Daemon triggers on the wheel | GDD 6.2 | none | **missing** | Twin Pointer, Botnet Seed, Stolen Intent, Zero Day, Kernel Sync and Clean Signal. |

### 1.9 Enemies and bosses

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Corporation slice kits (5) | GDD 8.3–8.5 | round6, round14–19 | locked | "all five kits", round 19. |
| Regular / elite / boss variation, corp tiers 1–3 | DIRECTION_REVIEW r13/r15 | round15–17 | locked | |
| Bosses (5): heavier bezel, banner, phase pips | GDD 2.11, A.3 | round6, round13 D4 | in progress | DIRECTION_REVIEW §6 "say which boss phase 2 treatments you like" is still open. |
| Mini-bosses | DECISIONS M8–M11 | none | **missing** | Account Manager, Logistics Director, City Manager, Mission Director, The Handler. |
| Enemy busts / holograms above the wheel | art_asset B2; Part M #3 | none | **missing** | |
| 58 individual enemies | `content/enemies/` | round6 picks about 15 | in progress | Mechanics are drawn on the wheel. Identity beyond the corp skin is absent. |
| REBEL_CELL Mirror elites | GDD 8.5; DECISIONS M11 | round6 Mirror; round16 REBEL_CELL kit | locked | The Mirror's hub "running your data Daemons" depends on the Daemon sigils. |

### 1.10 Campaign map and city

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| City base style | GDD 9.1 | round2, round6_city_restyle | locked | Conflicts with GDD 9.1's "Wireframe Cyberspace": see §3. |
| City motion | — | round24, round26 | locked | |
| Corporation HQ landmarks (= boss Sites) | GDD 8.3–8.5 | round24–30 | locked | REBEL_CELL is in progress. |
| Regular Site per corporation | art_asset D1 | round25–27 | locked | One per corporation. The 160 named Sites have no individual art. |
| **Site markers: kind / tier / status** | GDD 4.1, 3.3; `RC.SiteObjective`; art_asset D1 | none for corporate Sites. round19 node key covers claimed nodes only. | **missing** | Covers Exploit Site, Heat-objective Site, boss, CORE, tier 1–4, and Corporate / Cleared / Claimed / Seized / Disabled. |
| Locked cross-links / opened by Intel | GDD 4.1, 11.7 | none | **missing** | The frozen-link ice (raid) is locked. |
| Territory change / marks | art_asset C2 | none | **missing** | |
| City Grid HUD | art_asset G9 | round31_ui_chrome `city_map_hud.png` | in progress | |
| Heat meter / bands on the map | GDD 4.3, 9.4 | round31 terminal gauge | in progress | |
| **HQ room** (deck, window, WANTED poster, radio, crew photos) | GDD 9.1 ("Physical: Diegetic Cyberdeck"); art_asset C3, G8 | round 1 `COMPARE_04_hq_modem` only (rejected styles) | **missing** | |
| Jack in / jack out transition | art_asset G14 | none | **missing** | |

### 1.11 Netrun

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Route map (7 layers) | GDD 4.2 | round31 `netrun_map.png` | in progress | |
| Node kinds: Router / Elite Router / Terminal / Modem / Server Rack | GDD 4.2 | round31 stickers | in progress | |
| Modem exterior + sign | — | round12 (F1), round27 (MARKET NEON) | locked | |
| Modem interior | art_asset G18 | round31 `shop_interior.png` | in progress | The pixel-smiley clerk is unconfirmed. |
| Server Rack capture / banking | GDD 4.2, 7.3 | round31 `server_rack.png` | in progress | It contains the non-GDD "flash" (see §3). |
| Terminal event screen | GDD 8.7; art_asset G19 | round31 event screens | in progress | |
| Event illustrations (124) | `content/events/` | one CAM feed (Locked Ward) | **missing** | |
| Dialogue / subtitles, DISPATCH | GDD 8.2, 9.6 | round31 dialogue A/B | in progress | "DISPATCH never gets a face." |
| Netrun complication (MINOR threshold) | GDD 4.3 | none | **missing** | |
| Run end: JACKED OUT / FLATLINED / HOME FELL | GDD 4.2; art_asset G21 | none | **missing** | |
| Mid-run raid interlude | GDD 4.4; art_asset G20 | none | **missing** | The HQ raid screens may cover most of it. |

### 1.12 Raids and defences

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Raid map: circuit-inlay nodes, links and routes | GDD 7.1–7.2, 9.3 | round18–23 | locked | |
| Node status, health, forecast, TAKEN / BREACHED / DOWN | GDD 3.3, 7.2 | round19–24 | locked | |
| Node type glyphs | GDD 3.2 | round19 key: Relay, Firewall, Vault, Proxy, Safehouse, CORE | in progress | **Compiler Rack is absent.** Glyphs are borrowed from placeholder slice glyphs (Proxy = SPOOF fingerprint, Safehouse = KEY, Vault = VAULT safe). |
| Node upgrades (level 1–2) | GDD 11.4; DECISIONS batch 2a | none | **missing** | |
| Home-server variants (5) | GDD 3.1; DECISIONS batch 2a, M12 | none | **missing** | Standard, Bunker, Fortress, Ghost, Relay Nest. The round 27/28 "fortress" is Meridian's castle, not a home variant. |
| Built-in defences | GDD 3.2; DECISIONS | none | **missing** | Firewall Relay turret, Bunker turret, Ghost lock. |
| Defence assets (8) | GDD A.5; DECISIONS M7; `content/assets/` | Turret, Railgun, Flak, Sentry: round18 tracers. ICE Lock: round19–22. Decoy: round20 pylon. Honeypot: mentioned. | in progress | **Tar Pit has none.** There is no unit or structure model per asset except the decoy pylon. |
| Asset cards / tray / drag | — | round18–23 | locked | |
| Threats (17) | GDD A.5; `content/threats/` | round19–22 vehicle matrix (FAST / HEAVY / SPECIAL / LANDER / FLYING × corporation) | locked (as types) | The named threats are not mapped to the types. Unmapped: Icebreaker opens locked links; Lockdown Unit freezes links; Signal Jammer; the REBEL_CELL Mirror threats Informant / Loyalist / Purger. |
| Playout speed / skip, raid report, campaign dossier, campaign lost | GDD 7.2 | round20–23 | locked | |
| Raid warning / RAID INCOMING / corp raid names (Collections) | GDD 8.3; art_asset J | none | **missing** | |
| Armory (max 6) | GDD 7.3 | counts on CRT only | **missing** | |

### 1.13 Shop and economy items

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Resource icons: Cycles, RAM, Schematics, Heat, HP, ICE, Rank | GDD 11.1; art_asset F1, I | round13 pictos (RAM chip, HP heart) | in progress | No locked resource icon set. |
| **Exploits** (Intel / Breach / Virus; 15 named) | GDD 11.7, 4.1, 8.3–8.4d; `ExploitData` | `Exploits x/3` text in round31 HUD | **missing** | The name also collides with the EXPLOIT slice program (§3). |
| Netrun boosts | GDD 11.4; `NetrunBoostData` | none | **missing** | |
| Profile unlocks (18) / achievements (10) | GDD 3.4; DECISIONS batch 4 | none | **missing** | art_asset Part M #9. |
| Price tags / BUY / SOLD / shredder | GDD 11.2 | round31 shop | in progress | |
| HQ spends: −5 Heat, patch home, repair, recruit, Black Market | GDD 3.3, 5.4, 11.4 | none | **missing** | |

### 1.14 Events, rewards, menus and meta

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Loot / reward screen | art_asset G17 | round31 reward A/B | in progress | |
| Story beats / Exploit reveals / finale | GDD 8.4, 8.6 | none | **missing** | |
| Title / main menu | art_asset G1 | round31_ui_chrome | in progress | |
| Options / settings | art_asset G5 | round31_ui_chrome | in progress | |
| Typography / UI kit | art_asset H, L | round31_ui_chrome | in progress | |
| New-campaign start page | art_asset G7 | none | **missing** | Corporation, ICE, home server and class pickers. |
| Campaign slots, stats, codex, pause | art_asset G2–G6 | none | **missing** | |
| Campaign end: WON | art_asset G13 | none | **missing** | LOST is locked (ransomware + dossier). |
| Logo / Cell mascot / Cell mark | art_asset A1 | REBEL_CELL neon sign (round31 title) | in progress | The mascot is missing. |
| Corporation emblems | art_asset A2 | crests partly via the HQ rounds (Halcyon eye, Meridian crane) | in progress | |
| Controller prompts | art_asset I | round31 pad prompts | in progress | |

### 1.15 VFX and audio-visual feedback

| Element | Where defined | Concept coverage | Status | Notes |
|---|---|---|---|---|
| Hit / crit shards, walls, heal, evade, drones, defeat, phase change | GDD 2.6 | round18–23 | locked | |
| Temporary word stickers that dissolve into bits | — | round23 | locked | |
| Precision landing FX (ties to GDD 10 audio) | GDD 10 | none | **missing** | See §1.1. |
| Flip / Freeze / Hub Breach / OVERCLOCK / ENCRYPT / PARASITE apply | GDD 2.5, 2.8, 2.9 | none | **missing** | |
| Heat crossing banner (NOTICED / FLAGGED / HUNTED) | GDD 9.4; art_asset J | none | **missing** | Heat *bands* on screens are locked. "Distortion **pulses** on threshold events" is not drawn. |
| Reduce-effects / flash limiter variants | GDD 9.6 | specified per effect in the round NOTES | locked | |

---

## 2. Missing designs, in priority order

### 2.1 Firmware ("Microchips"): highest priority

**What the rules say:**
- GDD §6, the rule line: "**Firmware changes what its slice does.** Inner Ring segments change wheel state or modify the outer slice. Daemons are run-wide rules."
- GDD §6.1 title: "Firmware (one socket per slice)".

| Firmware | GDD 6.1 effect |
|---|---|
| Patch+ | Slice output +50% |
| Hardened | Slice permanently ENCRYPTED |
| Burner | Permanently OVERCLOCKED (1.5×); each trigger +1 Heat |
| Leech | ATK slice restores 1 RAM on Good or better |
| Mirror | "Copies the clockwise neighbour when landing clockwise of centre, the counter-clockwise neighbour when landing counter-clockwise, **both** on Perfect" |
| Shunt | "Resolves the neighbour on the side you landed toward at 1.5×; nothing on Perfect" |

**Schema:**
- `FirmwareData`: "Socketed into one slice. Firmware changes what that slice does." Its fields are `allowed_slice_types` ("Empty = fits any slice type"), `output_multiplier`, `permanent_status`, `neighbor_rule` (MIRROR / SHUNT), `neighbor_multiplier`, `triggered_effects` and `rarity`.
- `WheelSlotData`: "One position on a wheel: a slice plus its optional Firmware."

**The 12 Firmware added in DECISIONS M7** (effects from art_asset's appendix):

| Firmware | Effect |
|---|---|
| Overvolt | ATK/CRIT +25% |
| Bulkhead | DEF/SHIELD +50% |
| Siphon | ATK heals 2 |
| Static Coat | DEF +2 shield |
| Barbed Wire | DEF deals 2 |
| Tracer | strip 1 resistance on Perfect |
| Coolant Loop | Perfect −1 Heat, once per combat |
| Skimmer | +3 Cycles on Perfect, twice |
| Counterstrike | EVADE deals 4 |
| Nanite Mesh | HEAL +50% and self-cleanse |
| Power Cell | SHIELD +1 RAM |
| Recycler | Miss slice +2 RAM |

**How it attaches:**
- One chip per slice of the operative's wheel.
- It is dragged onto a spinner slot (DECISIONS ANIM-4b), from loot (Routers drop common Firmware, `router_firmware_chance` 0.35) or from the Modem (75–150 Cycles, GDD 11.2).
- Enemy wheels can carry Firmware too: `BossPhaseData.wheel_override` "swaps slices, Firmware, statuses".
- Firmware is kept on run completion and lost on death (GDD 4.2).
- The GDD does not say whether a socketed chip can be replaced. That rule needs checking before the socket art is final.

**What the art must show:**
1. A chip object for each of the 18. Rarity must be visible (Common / Uncommon / Rare). The chip's glyph must name its *effect family*, not reuse a slice glyph: today's mock gives Overvolt the ATTACK (EXPLOIT) glyph.
2. **The socketed state on a slice, on every wheel and at r = 60.** It must stay readable on top of the locked slice screen, tier bezel, state overlays and docked drones.
3. Valid and invalid sockets for `allowed_slice_types`. Round 31 lights "VALID: ATK + CRIT".
4. Trigger feedback:
   - Mirror and Shunt pull a *neighbour* slice depending on which side of centre you landed;
   - Burner adds Heat each trigger;
   - Hardened shows a permanent ENCRYPTED;
   - Leech, Power Cell and Recycler add RAM.
5. Decide how "Microchip" (UI word) and "Firmware" (GDD word) relate, and log it in DECISIONS.

### 2.2 Daemons

**What the rules say:**
- GDD §6: "**Daemons are run-wide rules. Rule-breaking Daemons are expected.**"
- `DaemonData`: "Run-wide rule (relic). Simple Daemons are pure data; rule-breaking ones point custom_handler at a script that hooks the CombatEngine."
- GDD §2.2.3 resolves "Daemon hooks" in the third pass, with statuses.

The GDD 6.2 table:

| Daemon | Effect |
|---|---|
| Clean Signal | 3 consecutive Perfects: −2 Heat |
| Cold Exit | Finish a netrun without the Miss slice resolving: −3 Heat |
| Scrubber | Capturing a Server Rack removes 1 Heat instead of adding it |
| Fault Tolerance | Miss slice deals 3 damage to the pointer target |
| Kernel Sync | Each Perfect: +1 damage for the rest of the combat |
| Zero Day | A Perfect on the Miss slice resolves as a 3× Crit |
| Linked Bus | Nudging an enemy wheel (nudge actions, not cards) also moves your wheel the same way, free |
| Stolen Intent | Once per combat, when you would resolve Miss and the target would not, swap resolved slices |
| Twin Pointer | Your wheel is also read at the bottom; both trigger. Max RAM halved. |
| Botnet Seed | Each Perfect deploys a 1-HP drone on the triggered slice (max 2) |

Plus 14 added in M7: Warm Boot, Shield Cache, Idle Armor, Adrenal Loop, Fail Forward, Feedback Loop, Tuning Fork, Static Field, Cascade, Salvager, Field Medic, Bounty Code, Rack Skimmer and Log Wiper.

**How they attach:**
- Daemons are **not** on a slice. They belong to the operative for the run.
- They are kept on completion ("survivors return to HQ ... keeping deck, Firmware and Daemons", GDD 4.2) and lost on death.
- Acquisition (GDD 6.3): "Terminals: events offering Firmware, Daemons or rescued operatives · Modems: everything, for Cycles · Server Racks: rare Daemons + Schematics". The Modem price is 150–250 Cycles.
- Hooks are typed triggers (`RC.Trigger`): ON_PERFECT, ON_MISS_SLICE, ON_NUDGE, ON_TURN_START, ON_COMBAT_START/END, ON_SERVER_RACK_CAPTURE, ON_NETRUN_COMPLETE and others.
- Some change the wheel visibly:
  - Twin Pointer adds a pointer 15 ticks away and halves max RAM (DECISIONS batch 1);
  - Botnet Seed docks `seed_drone`s;
  - Stolen Intent swaps the resolved slices;
  - Linked Bus moves your wheel when you nudge an enemy's.
- REBEL_CELL Mirror elites run "a hub running your data Daemons" (GDD 8.5, M11).

**What the art must show:**
1. A unique sigil for each of the 24 (art_asset F2: "A unique **sigil** each; rarity visible"). These must be distinct from slice glyphs and card pictograms. Today the mock gives two Daemons the same `picto_again`.
2. The installed-Daemon row in combat and the DAEMONS icon / tray. STYLE_GUIDE's icon is a ghost.
3. A trigger cue when a hook fires:
   - counters for Clean Signal (3 Perfects) and Cascade (2 in a row);
   - a stacking counter for Kernel Sync;
   - a once-per-combat spent state for Stolen Intent.
4. The wheel-altering ones:
   - Twin Pointer's second pointer at the bottom;
   - Zero Day's Miss-slice-as-Crit;
   - the Botnet Seed drone.
5. How a Mirror elite's hub shows *your* Daemons.

### 2.3 Precision landing feedback (Perfect / Good / Partial / Miss slice)
- GDD 2.4: Perfect "Triggers the class Perfect hook and Perfect-based effects".
- GDD 10: "Perfect = latch + wheel-local inversion + 2-frame freeze; Good = clean click; Partial = stutter; Miss slice = static burst."

This is pillar 1, and it is undrawn. Many Firmware, Daemons and every Class Core hook off a Perfect.

### 2.4 Hub cores, Mk2, enemy hub passives and the Hub Breach state
- GDD 2.8: "Player Hubs hold the operative's **Class Core** (passive + Perfect hook). Enemy Hubs hold an enemy passive ... **Hub Breach** cards disable an enemy Hub for one turn."
- GDD 5.3: "Rank 2: Upgraded Hub Core."

The art must show:
- an emblem for each of the 8 cores, plus a Mk2 variant;
- 6 enemy hub passives;
- a hub that reads "breached / offline this turn". Every boss's heal or shield depends on it.

### 2.5 Inner ring and segments
- GDD 6.4: "Each class starts its standard ring at Rank 1 ... At Rank 3 the player may swap segments from: ×2, Pierce, Corrupt, Anchor, Accelerator, Echo."
- "Precision tiers are measured on the outer ring only."

The art must show:
- the 7 segment marks in the locked glyph language (Anchor has never been drawn);
- the ring in the D4 frame, with its own rotation;
- segment triggers;
- the Rank 3 swap UI.

### 2.6 Exploits and the Mainframe gate
- GDD 11.7: "Minimum **3 Exploits** to attempt the breach."
  - Intel: "Reveals boss phases and pointer moves; opens locked Grid links".
  - Breach: "Boss starts with one fewer pointer".
  - Virus: "Boss starts with CORRUPTED slices".
- GDD 4.2: "On T2+ targets, the final Rack holds the Site's Exploit."

The art must show:
- a symbol for each of the 3 kinds and the 15 named items;
- the Exploit Site marker;
- the x/3 gate;
- the effect on the boss at the breach. Breach's removed pointer and Virus's pre-corrupted slices must be visible on the boss wheel.

### 2.7 Enemy satellites as mini-wheels
- GDD 2.1: "Satellites: 2–3-slice mini-wheels (10 or 15 ticks per slice) docked on an enemy slice."
- GDD 2.7: "Satellites have their own mini-wheel and intent, resolve after their host, and can be nudged individually."

So far they are only tokens with an HP pill.

### 2.8 Operatives as characters
art_asset B1 asks for these per class: full figure, bust, dossier portrait and portrait states, plus the rank indicator (GDD 5.3) and the class ornaments re-done on the D4 frame.

### 2.9 Combat actions without FX
Flip (GDD 2.3), Freeze (wheel-level), Hub Breach, the OVERCLOCK / ENCRYPT / PARASITE apply, the three-pass resolution beat, the Migrate flicker / Orbit trail on D4, and the Heat threshold pulse (GDD 9.4).

### 2.10 Network and raids gaps
- The Compiler Rack glyph.
- Node upgrade levels.
- 5 home-server variants.
- Built-in defences.
- Tar Pit and Honeypot structures.
- Per-asset unit models.
- Named threats mapped onto the vehicle types.
- The RAID INCOMING / corporation raid warning.
- The Armory.

### 2.11 City Grid Site markers
- GDD 4.1: Sites have tiers T1–T4, Exploit Sites, "Heat objective Sites", the boss, and locked cross-links.
- GDD 3.3: Sites have the statuses Corporate / Cleared / Claimed / Seized / Disabled.

None of this has a marker in the locked style yet.

### 2.12 HQ room and meta screens
- The HQ room. GDD 9.1 "Physical" world: HQ, recruitment, stationing, loadout.
- The WANTED Heat poster.
- The jack-in transition.
- The new-campaign page.
- Campaign slots.
- The codex.
- Stats, achievements and unlock badges.
- The tutorial.
- The pause menu.
- The run end (FLATLINED).
- Campaign WON.
- Netrun boosts.
- The Bug card.

### 2.13 Content illustration volume
- 71 card illustrations.
- 124 event illustrations.
- 58 enemy busts.
- 5 mini-bosses.
- 160 Sites: one regular Site per corporation exists.

---

## 3. Mismatches: concept names and systems that are not in the GDD

"To-do?" says whether the item is on DIRECTION_REVIEW's "Game to-do list for reintegration".

| Concept item | GDD / content reality | To-do? | Note |
|---|---|---|---|
| **Slice "programs"**: EXPLOIT (ATTACK), ZERO-DAY (CRIT), FIREWALL (DEFEND), SANDBOX (SHIELD), PROXY (EVADE), PATCH (HEAL), VIRUS (AFFLICT), TROJAN (DEPLOY), NULL (MISS). Source: round5 s_c, round13 table. | GDD 2.6 and `RC.SliceType` use ATTACK / CRIT / DEFEND / SHIELD / EVADE / DEPLOY / HEAL / AFFLICT / MISS. No program name appears in GDD, DECISIONS, STYLE_GUIDE or ART_BIBLE. | **No** | Six of the names already mean something else in the game: **EXPLOIT** vs Exploits (the mainframe gate); **VIRUS** vs the Virus Exploit; **ZERO-DAY** vs the Zero Day Daemon; **FIREWALL** vs the Firewall card and the Firewall Relay node; **PROXY** vs the Proxy Relay node; **PATCH** vs the Patch+ Firmware and the Patch Up card. These need a naming decision before the art goes back into the game. |
| SANDBOX = SHIELD, and a separate placeholder "SHIELD" slice | GDD 2.6: SHIELD "Gain shield (persists across turns, cap 15)" | Yes | Round 13 lists both a SHIELD *type* (SANDBOX) and a SHIELD *placeholder*. |
| Upgrade tiers I–III (V2 strong); corp tiers 1–3 | `SliceData` has no tier | Yes | "Tier" collides with the netrun / Site tier T1–T4 (GDD 4.1, 11.4). |
| Server Rack "flash": upgrade a slice a tier, or swap one from the Rack drawer (round31) | GDD 4.2: a Rack banks Schematics; GDD 6.3: "rare Daemons + Schematics" | **No** | Flagged in round31 NOTES only. |
| Meridian TARIFF → JUDGEMENT → **PRIORITY**; CRIT → AIRMAIL | GDD 8.4b: "Tariffs (RAM drain)"; `tariff.tres` | Yes | **PRIORITY collides with Priority Routing**, The Manifest's hub (DECISIONS M8). |
| INERTIA → WEIGHT; HEAL → GROWTH (Solace) | GDD 8.4b "Inertia"; `atk_8_inertia` | Yes | |
| Placeholder slice types: PHISHING, ENCRYPT, RECON, BURN / TORCH / DISSOLVE, Guy Fawkes mask; **BOMB, VAULT, KEY, SPOOF, STORM** | not in the GDD | Partly | BOMB, VAULT, KEY, SPOOF and STORM are **not** on the to-do list. VAULT, KEY and SPOOF are already reused as raid *node* glyphs (Vault, Safehouse, Proxy, round19), so they would clash if they ever become slices. |
| Slice states FROZEN / LOCKED / BURNING / EMPOWERED | not in the game; GDD Freeze is wheel-level | Yes | FROZEN on a slice misrepresents the Freeze card. |
| CLEANSE "ability" (ESC key); KILL PROCESS (power symbol) | Cleanse is already a card (GDD A.2 #19, Sanitize); KILL PROCESS has no counterpart | Yes | CLEANSE is not new. Only KILL PROCESS is. |
| Gates (rim gates) | not in the GDD | Yes | |
| MOMENTUM dynamic pictogram | Momentum card (GDD A.2 #5) | Yes | |
| Card type band WHEEL / HACK / SYSTEM | not in the GDD; `CardData` has no type field (ART_BIBLE 7.3: colour = type) | **No** | Round 31 flag 3. |
| Shop clerk (pixel smiley); MARKET NEON with the NO → MoRE → MAN takeover | GDD node "Modem"; art_asset sign "MODEM / CYBER SHOP" | No | It is a new character, and the sign name differs from the node name. |
| EXPOSED (spotlit node takes extra damage); higher Heat brings more waves and routes | GDD 4.3: Heat 75 "Raid strength +25%"; ICE 16–20 "raids gain a second wave" | Yes | |
| Threat vehicle **upgraded** variants; FAST / HEAVY / SPECIAL / LANDER / FLYING types; targetable choppers and drones | `ThreatData` has routing / speed / `freezes_edges` / `alters_edges` / `heat_integrity_scaling`; there is no upgrade tier and no flying units | **No** | Only EXPOSED is listed. |
| Station bonuses for the alternates (sniper, drone operator, echo decoy, overclock); station "levelling" | GDD 5.2 bonuses for the base classes; GDD 5.3 "Station bonuses scale with rank" (M6 rank multiplier) | Yes | Levelling could map onto rank, which already exists. |
| Raid words TAKEN, CELL HOLDS, BREACHED, DOWN | GDD 3.3 / 7.2 say **Seized**, **Disabled**, "Holds" | No | Vocabulary drift from the GDD terms. |
| Raid intel "decrypted / not decrypted" | not in the GDD | Yes | |
| Decoy destroyed / route reverts | the raid code has no defence damage | Yes | |
| Heat glitch Options setting | not in Settings | Yes | |
| REBEL_CELL as "the player's home for most of the game, until the betrayal reveal", with home and DISPATCH versions | GDD 8.5: a separate final-unlock corporation (cleared after all others at ICE 10), built from your profile; GDD 8.2: DISPATCH is the twist | No | Narrative reading not in the GDD. art_asset A2 also warns that "The Cell ... Needs its own identity separate from the hidden REBEL_CELL corporation", yet the concept gives REBEL_CELL the rebel-fist crest. |
| Visual baseline: Cv2 low-poly cel city for the net; CRT terminals; vinyl stickers; grease pencil; spray rejected | GDD 9.1 (**locked**): Net = "Wireframe Cyberspace (glowing geometry)"; Cell = "Punk Zine (paper, tape, marker, spray paint)". GDD 9.4: "corporate wireframe creeps over the zine layer". GDD 9.2: "Zine elements never cover the wheels". | No | The concept direction overrides a **locked** GDD section, and round 31 says "Pencil may cross anything". It needs a DECISIONS entry and a GDD 9 update. |
| Corporation landmarks: Meridian container castle, Orbital missile silo | art_asset A2: "Freight Ziggurat", "Orbital Tether" (marked "current concept, not binding") | No | Not a GDD conflict, but art_asset needs updating. |
| Pointers called "readers" (round6) and "needles" | GDD: "pointer" | No | Terminology only. art_asset also says "needles". |

## 4. Suggested next concept rounds
1. Firmware chips: all 18, the socketed-on-slice state, and trigger FX.
2. Daemon sigils (24) with the combat row and tray.
3. Precision landing (Perfect / Good / Partial / Miss), together with the Class Core hooks.
4. Hub cores, Mk2, enemy hubs and the Hub Breach state, plus the inner-ring segment glyphs (with Anchor) on D4.
5. Exploits: the 3 kinds, the Site marker, and the boss effects.
6. Satellite mini-wheels and the Flip / Freeze / Breach FX.
7. Operative characters.
8. Grid Site markers, node types (with Compiler Rack), home variants and the asset structures.
9. The HQ room and the meta screens.

Before any art is reintegrated, the designer needs to decide the slice program names (§3, row 1) and the GDD 9.1 baseline conflict.
