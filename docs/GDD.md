# REBEL_CELL — Game Design Document

**Genre:** Cyberpunk tactical dual-spinner deckbuilder with a network-defense campaign layer
**Engine:** Godot 4.7 · **Platform:** PC (mouse + keyboard, gamepad)
**Status:** v0.9 — consolidated handoff specification

All numbers are tuning placeholders unless marked **locked**. Numeric tuning lives in
`CampaignConfigData` and content `.tres` files, never in code (see `TECH_SPEC.md`).

### Changes since v0.8
30-tick wheel (was 24) · Miss precision tier removed · jitter replaced by spin resistance ·
Hubs, Inner Rings, satellites, multiple pointers added · three-layer progression (profile /
campaign / netrun) · City Grid campaign map · Heat redefined as a campaign meter · Ranks,
stationing, Armory · Exploit-based Central Server · economy, ICE difficulty, narrative, UX,
audio and visual baseline defined · vertical-slice content defined (Appendix A).
2026-10-05 (M14, DECISIONS 2026-10-05, ruling 4): §9 rewritten around ART_BIBLE v2: the visual baseline is the
cel-shaded low-poly city, CRT screens, vinyl stickers, grease pencil and light spill (9.1),
with the sticker / pencil layer rules and status overlays in 9.2 (ruling 10), DOWN as the
white bolt at every zoom in 9.3 (ruling 11) and "the city reacts" in 9.4.

---

## 1. Overview

### 1.1 Pitch
REBEL_CELL is a roguelite deckbuilder where every action resolves through spinning wheels.
You lead an unseen rebel cell fighting a biotech megacorp that bricks the life-critical
implants of anyone who misses a subscription payment. Operatives *jack in* to corporate
systems on netruns (single roguelike runs, about 15 minutes each), where combat is a
deterministic puzzle of reading, nudging, spinning and flipping wheels. Between runs you
expand your network across a digital city and defend it from corporate retaliation raids,
until you can breach the corporation's final server and plant the kill code.

### 1.2 Design Pillars
1. **Precision is the currency of skill.** Alignment on the wheel is the core mechanic.
   Cards, classes and Firmware expand the space around alignment. **Hubs grant passives,
   never actions; every action resolves through alignment.**
2. **Escalating, high-stakes campaign.** Difficulty ramps with tier and Heat. Death is
   permanent for the operative and pushes the campaign toward defeat.
3. **Three-layer progression.**
   - *Netrun:* power comes from in-run pickups and dies with the operative.
   - *Campaign:* Schematics buy defenses, network options and one-time boosts.
   - *Profile:* permanent unlocks (classes, corporations, etc.) carry across campaigns.
4. **System boundaries.** Wheel mechanics exist only in combat. Raids are deterministic
   graph auto-battles with a planning phase.

### 1.3 Structure
```
PROFILE (permanent): unlocks, ICE records
 └─ CAMPAIGN (one corporation): City Grid, network territory, Heat, Schematics, roster
     ├─ HQ: recruit, station, spend Schematics, pick a Site and an operative
     ├─ NETRUN (one operative, one Site, ~15 min): map → combats, events, shops, Server Racks
     │    └─ may be interrupted by a raid interlude
     └─ RAIDS: triggered by Heat thresholds and other events, mid-run or between runs
 Win: breach the final server with enough Exploits. Loss: home server integrity reaches 0.
```

---

## 2. Combat

### 2.1 Wheel Anatomy (locked)
- A wheel has **30 ticks** (12° each) and **6 slices** of **5 ticks**. Slice *i* is centred
  on tick 5*i* and spans ticks 5*i*−2 … 5*i*+2.
- **Pointer:** a fixed marker (top of the wheel by default). The tick under a pointer
  decides which slice resolves and how precisely.
- **Hub (center zone):** always-on passive for that wheel (2.8).
- **Inner Ring (optional):** 3 segments of 10 ticks, rotating independently. The outer
  slice sets the *action*; the inner segment sets a *modifier* (Section 6.4).
- **Satellites:** 2–3-slice mini-wheels (10 or 15 ticks per slice) docked on an enemy
  slice (2.7).
- Enemies may have several pointers, evenly spaced (15 or 10 ticks apart) unless a boss
  phase moves them.

### 2.2 Turn Flow
1. **Start of turn:** every wheel respins to a random tick (a *random event*; sets a
   rewind checkpoint). Enemy intents are now visible. Player draws to 5 cards, gains
   +4 RAM (max 12), and the free nudge refreshes. Block from last turn expires.
2. **Player phase:** play cards, use the free nudge (extra nudges cost 1 RAM each),
   inspect previews, rewind freely back to the last checkpoint.
3. **End turn:** all pointers resolve at once, in this order:
   1. Defensive slices on both sides (DEFRAG, SANDBOX, DETOUR, HOTFIX).
   2. Offensive slices on both sides (SHIM, OVERFLOW, TROJAN).
   3. Statuses and other effects (INFECT, CORRUPTED triggers, Daemon hooks).
4. Unplayed cards are discarded. When the draw pile is empty, shuffle the discard pile in.

### 2.3 Resolution Math (locked)
```
tick_under_pointer = (rotation + pointer_tick) mod 30      # a Flip rearranges the wheel, see below
slice_index        = round(tick / 5) mod 6
offset             = tick − 5 × round(tick / 5)        # −2 … +2
```
Flip mirrors the wheel across the horizontal axis: tick *t* → (2*p* + 15 − *t*) mod 30,
so the slice opposite the pointer arrives at the pointer and slice order reverses.

### 2.4 Precision Tiers (locked)
| Tier | Offset from slice centre | Output | Notes |
|---|---|---|---|
| Perfect | 0 | 1.0× | Triggers the class Perfect hook and Perfect-based effects |
| Good | ±1 | 1.0× | |
| WEAK | ±2 | 0.5× | (was Partial; DECISIONS 2026-10-05, names for M14, D8) |

There is **no miss tier**: every landing is within 2 ticks of some slice centre. A "miss"
means only the **NULL slice** resolving. Effects that mention it (Fault Tolerance,
Cold Exit, CORRUPTED) refer to the NULL slice.

### 2.5 Manipulation
| Action | Scope | Cost | Resistance |
|---|---|---|---|
| Nudge ±1 | One ring | 1st per turn free, then 1 RAM | Each tick is absorbed by 1 resistance |
| Spin N | Whole wheel (outer + inner) | Card | First R ticks absorbed; the rest move the wheel |
| Flip | Whole wheel | Card | **Blocked entirely** while resistance > 0 |
| Respin | Whole wheel, random | Card, or 4 RAM on your own wheel (11.3) | Blocked while resistance > 0; sets a checkpoint |
| Freeze | Whole wheel | Card | Target skips its next start-of-turn respin |

**Spin resistance (enemy ability).** Resistance R absorbs the first R ticks of player
manipulation. Sources: a **passive trait** (restores to full at the start of each player
turn) or the **Hub** (active while the Hub is; disabled by Hub Breach).

### 2.6 Slice Types
| Type | Default target | Effect |
|---|---|---|
| SHIM | Pointer target | Deal damage (DECISIONS 2026-10-05, names for M14, D2) |
| OVERFLOW | Pointer target | Deal high damage |
| DEFRAG | Self | Gain block (expires start of your next turn) |
| SANDBOX | Self | Gain shield (persists across turns, cap 15) (DECISIONS 2026-10-05, SANDBOX / TROJAN / NULL) |
| DETOUR | Self | Cancel the next incoming SHIM or OVERFLOW this turn |
| TROJAN | Self | Create a drone (Botnet) |
| HOTFIX | Self | Restore HP (enemy-facing) |
| INFECT | Pointer target | Apply a status (e.g. Solace DOSE applies CORRUPTED) |
| NULL | — | Nothing (unless modified) |

### 2.7 Targeting & Satellites
- **Pointer rule:** a Pointer attack hits whatever sits at **each** pointer of the target
  wheel. Against a 3-pointer boss, one SHIM lands three times. The rule applies both
  ways: enemy attacks hit whatever sits at your pointer.
- **Satellites** dock onto a slice of their host wheel and rotate with it. A Pointer
  attack aimed at a pointer whose slice has a docked satellite hits the satellite
  instead (bodyguard). **Pierce** ignores block and shield, not satellites (ruling
  2026-09-24, see DECISIONS.md).
- Satellites have their own mini-wheel and intent, resolve after their host, and can be
  nudged individually. Spinning or flipping the host carries docked satellites along.
- Other target rules: SELF, SWEEP (all enemies), CHOSEN (player picks; a few cards only).

### 2.8 Hubs
Player Hubs hold the operative's **Class Core** (passive + Perfect hook). Enemy Hubs hold
an enemy passive (resistance, per-turn healing, etc.). **Hub Breach** cards disable an
enemy Hub for one turn.

### 2.9 Statuses
| Status | Rule |
|---|---|
| CORRUPTED | When the slice resolves: 3 self-damage (+1 per MAJOR Heat threshold crossed) and −1 RAM. Lasts until cleansed or combat ends. Applies to enemies too. |
| OVERCLOCKED | 1.5× output on the slice's next trigger, then the slice becomes CORRUPTED. (Burner Firmware is permanent and adds Heat instead.) |
| ENCRYPTED | Absorbs the next status applied to that slice. |

### 2.10 Preview & Rewind (locked)
- Combat is deterministic between random events, so the HUD always shows what will
  resolve at every pointer: slice, offset, tier, ring segment, satellite guard, and the
  full outcome including damage after block. Hovering a card shows its result before
  playing it.
- Random effects (Respin, random targets) show odds instead of a single result.
- **Rewind:** unlimited undo within a turn, back to the most recent checkpoint. Every
  random outcome sets a checkpoint; the start-of-turn respin is the first. Checkpoints
  are saved, so quitting and reloading cannot reroll a random result. On screen the respin
  control reads **RESPIN** (never CHECKPOINT) and an undo blocked by a checkpoint shows on
  **UNDO** itself (DECISIONS 2026-10-05, names for M14, D12).

### 2.11 Boss Pointer Phases (experimental)
Bosses change pointers when HP crosses phase thresholds: **Multiply** (new pointers
appear), **Migrate** (pointers move; telegraphed one turn ahead), **Orbit** (pointers move
N ticks per turn; a trail shows future positions).

---

## 3. Profile, Campaign & Network Territory

### 3.1 Network Territory
- The campaign map is the **City Grid** (Section 4). Your network is your **home server**
  (its internal layout set by the chosen home-server variant) plus **claimed Sites** with
  remote nodes installed, joined by Grid links.
- Clearing a Site with a netrun uses it up and makes it claimable. Installing a node
  costs Schematics.
- Raids start from corporate Sites adjacent to your territory and travel along links.
  Unclaimed cleared Sites are neutral; raids can pass through them.

### 3.2 Remote Node Types
| Node | Effect | Integrity |
|---|---|---|
| Home Server | Lose the campaign if it reaches 0 | 50 |
| Relay | Lets you claim Sites beyond it | 15 |
| Firewall Relay | Built-in turret (3 dmg, own node); asset slots | 30 |
| Compiler Rack | Netruns launched next to it start with a bonus card or Firmware | 15 |
| Vault Terminal | +3 Schematics per completed netrun; raids prioritise it | 20 |
| Proxy Relay | −1 Heat per completed netrun | 15 |
| Safehouse | Station slot for an operative | 20 |

Adjacency example: a Firewall Relay next to a Safehouse shares the stationed operative's
bonus.

### 3.3 Node Loss States
The raid words are the rules words (DECISIONS 2026-10-05, ruling 6.2): **DOWN** (was Disabled), **TAKEN** (was
Seized); a node that survives **HOLDS**, a raid the Cell survives ends **CELL HOLDS**, and the
home server falling is **BREACHED**.

| State | Cause | Recovery |
|---|---|---|
| DOWN | Integrity reaches 0 | Repair for 50% of install cost; no bonus until repaired |
| TAKEN | A threat is on the node when the raid ends, or a DOWN node is hit again | Site returns to the corporation. A Reclaim netrun (single combat, tiny rewards) makes it claimable again; the node must be reinstalled. A TAKEN Site next to your territory becomes a raid entry point. |

A stationed operative on a TAKEN or DOWN node returns to the reserves unharmed.
The home server can be patched at HQ for 1 Schematic per integrity point (2026-09-24).
Cleared and claimed Sites can be **patrolled**: a full netrun for loot, Heat and Rank with no
objective (2026-09-24, prevents a soft-lock when every Site is used up).

### 3.4 Profile Layer
Permanent unlocks: classes (80 Schematics, spent from the current campaign), class
alternatives (same deck + different core, or the reverse), corporations, home-server
variants, new node types, skins, ICE levels.
**ICE records:** highest ICE cleared overall and per corporation. Each corporation's ICE
ladder unlocks separately; a new corporation may start at (global best − 5).

---

## 4. City Grid, Netruns & Heat

### 4.1 City Grid (campaign map)
- 30–40 **Sites** per corporation. Each netrun targets one Site; cleared Sites are used up.
- **Tier chains:** each T1 Site opens exactly one T2, each T2 its T3, etc.
- Each T2 Site holds at most one Exploit; each Exploit type sits at a different Site.
- **Cross-links** between Sites start locked; Intel Exploits or objectives open them.
  Opened links are routes for raids too.
- **Heat objective Sites** reduce Heat (e.g. *Scrub Records: wipe your personal data from
  their memory banks, −5 Heat*).
- Minimum winning path (locked target): T1→T2 three times, then T3, then the boss =
  **8 runs**, Heat ≈ 70 before the boss.

### 4.2 Netrun Map
- **7 layers**, 2–4 nodes each, branching paths.
- **Server Racks** at layer 4 (optional, one node among others) and layer 7 (the single
  final node). Capturing a Rack banks its Schematics immediately (and banks Armory assets).
- On T2+ targets, the final Rack holds the Site's Exploit.
- Node types:

| Node | Content | Heat |
|---|---|---|
| Router | Standard combat | 0 |
| Elite Router | Elite combat | +1 |
| Terminal | Event (Section 8.7 voices) | 0 |
| Mainframe | Shop (Cycles) (DECISIONS 2026-10-05, ruling 6.5) | 0 |
| Server Rack | Elite-strength combat + banking | per 11.5 table |

- Guarantees: layer 1 all Routers; at least one Mainframe in layers 3–5; about 1 Elite per
  layer in layers 3–6; Terminals ≈ 25% of remaining nodes.
- Pacing: about 5 combats of roughly 2 minutes plus events ≈ 15 minutes.
- **Death:** the operative is permanently lost with everything unbanked (Cycles, cards,
  Firmware, Daemons, unbanked assets). Campaign gains 10 + tier Heat.
- **Completion:** survivors return to HQ at full HP, keeping deck, Firmware and Daemons;
  unspent Cycles convert to Schematics at 10:1; Rank increases.

### 4.3 Heat
- One campaign-wide meter, 0–100.
- **Thresholds:** MINOR every 10, MAJOR at 25/50/75, PURGE at 100.
- **Bands** (DECISIONS 2026-10-05, "five Heat bands"): COOL 0–24, NOTICED 25–49, FLAGGED 50–74,
  HUNTED 75–99, PURGE 100.
- **Bands** (DECISIONS 2026-10-05, "five Heat bands"): COOL 0–24, NOTICED 25–49, FLAGGED 50–74,
  HUNTED 75–99, PURGE 100.
  - **Events** (raids, complications) fire the *first time* a threshold is crossed, never
    again.
  - **Modifiers** apply only *while* Heat is at or above the threshold.

| Threshold | One-time event | Ongoing modifier (while ≥) |
|---|---|---|
| Minor (each 10) | Netrun complication (e.g. shop stock −1, extra elite) | — |
| 25 (Major) | Raid | Elites more frequent |
| 50 (Major) | Raid | All enemies +1 resistance |
| 75 (Major) | Raid | Raid strength +25% |
| 100 (Purge) | Largest raid of the campaign | — |

### 4.4 Raid Triggers & Timing
Raids trigger from Heat thresholds, claiming Sites next to corporate ones, building
certain nodes, story events, and retaliation for netrun objectives (an Exploit extracted at
Heat 50 or more; Heat objectives never provoke one, 2026-09-24). They can happen
mid-netrun (an interlude between map nodes) or between netruns. **Raid rewards are set by
the trigger; raid strength scales with current Heat**, so low-Heat raids are profitable.

---

## 5. Operatives

### 5.1 Model
An operative has a class, a 6-slice wheel, a Hub Core, a starting deck, HP and RAM.
Permadeath. HP carries between fights within a netrun; survivors heal fully at HQ.

### 5.2 Classes
| Class | HP | Wheel | Hub Core passive | Perfect hook | Station bonus |
|---|---|---|---|---|---|
| **Breaker** (slice) | 60 | Overflow, Shim, Shim, Shim, Defrag, Null | +1 spin on all cards | Slice resolves twice | Node's assets +50% damage |
| Ghost | 50 | Shim, Shim, Defrag, Defrag, Detour, Null | First nudge each turn ignores resistance | Strip 2 resistance from target | Threats entering node delayed 1 step |
| Rigger | 55 | Shim, Shim, Defrag, Defrag, Sandbox, Null | +1 max RAM | Refund 1 RAM + 1 free nudge | Node regains integrity after each wave |
| Botnet | 45 | Shim, Shim, Defrag, Trojan, Trojan, Null | Up to 3 drones; drones persist between combats in a run | Perfect Trojan docks a Parasite drone on an enemy slice (halves its output) | Node gains one free asset per raid |

*M6 balance ruling (2026-09-24, DECISIONS.md):* every class needs burst to outpace the
Renewal Engine's heal, so the Ghost hook also resolves the slice twice, and the Rigger and
Botnet hooks also resolve it again at half (Botnet on any slice; Trojan Perfects still plant
the Parasite). Wheels are interleaved so adjacent slices differ; exact slice values live in
`content/classes/`.

RAM: start each combat with 6, +4 per turn, carry-over, max 12. All classes share a card
pool; each class adds 1–2 exclusive cards.

**Botnet drones:** TROJAN creates a drone (5 HP, mini-wheel Shim 3 / Defrag 3) docked on
your wheel: on the TROJAN slice itself, else the next free slice clockwise (ruling
2026-09-24; DEPLOY_DRONE card effects may pick the slice). When that slice triggers, the
drone triggers too. Enemy Pointer attacks hit a drone on your resolved slice before you.
The Hub sets the drone template and cap (`max_drones`).

### 5.3 Rank
Rank = netruns survived.
| Rank | Wheel upgrade | Netrun tier access |
|---|---|---|
| 0 Rookie | Base wheel | T1 |
| 1 | Class Inner Ring installed | T2 |
| 2 | Upgraded Hub Core | T3 |
| 3 | Inner Ring segment swap options | T4 |

Station bonuses scale with rank. Netrun tier difficulty scales to match what veterans
carry (they keep everything).

### 5.4 Stationing & Roster
Between netruns a surviving operative can be stationed on a node (Safehouse slot) instead
of running; recall any time between runs. Campaign start: **2 rookies** of unlocked
classes, **20 Schematics**, standard home server. Recruit rookies at HQ (15 Schematics) or
rescue them at Terminal events.

---

## 6. Firmware, Daemons & Inner Rings

**Rule:** Firmware changes what its slice does. Inner Ring segments change wheel state or
modify the outer slice. Daemons are run-wide rules. Rule-breaking Daemons are expected.

### 6.1 Firmware (one socket per slice)
| Firmware | Effect |
|---|---|
| Patch+ | Slice output +50% |
| Hardened | Slice permanently ENCRYPTED |
| Burner | Permanently OVERCLOCKED (1.5×); each trigger +1 Heat |
| Leech | SHIM slice restores 1 RAM on Good or better |
| Mirror | Copies the clockwise neighbour when landing clockwise of centre, the counter-clockwise neighbour when landing counter-clockwise, **both** on Perfect |
| Shunt | Resolves the neighbour on the side you landed toward at 1.5×; nothing on Perfect |

### 6.2 Daemons
| Daemon | Effect |
|---|---|
| Clean Signal | 3 consecutive Perfects: −2 Heat |
| Cold Exit | Finish a netrun without the NULL slice resolving: −3 Heat |
| Scrubber | Capturing a Server Rack removes 1 Heat instead of adding it |
| Fault Tolerance | NULL slice deals 3 damage to the pointer target |
| Kernel Sync | Each Perfect: +1 damage for the rest of the combat |
| Zero Day | A Perfect on the NULL slice resolves as a 3× OVERFLOW |
| Linked Bus | Nudging an enemy wheel (nudge actions, not cards) also moves your wheel the same way, free |
| Stolen Intent | Once per combat, when you would resolve NULL and the target would not, swap resolved slices (automatic; ruling 2026-09-24) |
| Twin Pointer | Your wheel is also read at the bottom; both trigger. Max RAM halved. |
| Botnet Seed | Each Perfect deploys a 1-HP drone on the triggered slice (max 2) |

### 6.3 Acquisition
Routers: common Firmware · Terminals: events offering Firmware, Daemons or rescued
operatives · Mainframes: everything, for Cycles · Server Racks: rare Daemons + Schematics.

### 6.4 Inner Ring Segments
Each class starts its standard ring at Rank 1 (Breaker: ×2 / Pierce / —). At Rank 3 the
player may swap segments from: ×2, Pierce (ignore block + shield), Corrupt (apply
CORRUPTED to the target's resolved slice), Anchor (on Perfect, skip next respin),
Accelerator (nudge cards next turn trigger twice), Echo (outer slice triggers again at
0.5×). Precision tiers are measured on the outer ring only.

---

## 7. Cell Defense (Raids)

### 7.1 Setup Phase (~4 minutes)
Threat vectors are revealed along Grid links from corporate Sites. The player places and
repositions defense assets on claimed nodes. Some threats freeze or alter links before
the raid. Each node shows the **exact projected outcome** if the raid ran now (HOLDS /
DOWN / TAKEN (DECISIONS 2026-10-05, ruling 6.2)), because resolution is deterministic.

### 7.2 Resolution (30–60 s playout; 1×/2×/4× and skip)
Each step:
1. Threats move along links (edges_per_step), following their routing rule.
2. ICE Locks hold threats on their node.
3. Assets fire (range in hops, targeting priority); built-in node defenses fire.
4. Threats damage the node they're on. A node at 0 goes **DOWN**; 50% of excess
   damage spreads to adjacent claimed nodes.

The raid ends when every threat is destroyed or has reached home, or after **30 steps**.
Threats still on a node at the end leave it **TAKEN**. Damage reaching the home server reduces
its integrity; **0 = BREACHED, campaign lost**. A survived raid ends **CELL HOLDS**; the summary shows DOWN/TAKEN nodes, repair costs
and new entry points.

### 7.3 Armory & Persistence (locked)
- Assets collected during a netrun bank to the **Armory** (max 6) on Server Rack capture
  or run completion. Unbanked assets are lost on death.
- Deployed assets **persist** on their node until destroyed and can be repositioned in any
  raid's setup.
- Between-run raids use the Armory plus built-in node defenses. Mid-run raids can also use
  the assets the current run carries.

---

## 8. World & Narrative

### 8.1 Tone Map
| Tone | Where | Voice |
|---|---|---|
| Tech-Noir | City, Cell, operatives, narration | Street Merc (operatives) |
| Anarchic Punk | Combat, Terminal events, deals gone wrong | — |
| Transhumanist Dread | The overarching story, implants, the AI twist | AI Observer |
| — | Corporate messages, raid warnings, data dumps | Corpo |

Original slang lexicon (living list): *leash* (subscription implant), *subbie* (corp word
for customer; street insult), *bricked* (implant shut off for non-payment), *ghosting*
(running without leaving traces). Do not borrow slang from existing cyberpunk IP.

### 8.2 The Cell & DISPATCH
The player is the Cell's unseen leader. Orders come through **DISPATCH**, an encrypted
handler everyone assumes is human. DISPATCH is a rogue AI using the Cell to destroy its
competitors. Hidden clues across campaigns: replies before messages are sent, impossible
timestamps, stolen data mentioning a buyer who profits from every collapse, and a voice
that slowly shifts from human to machine. DISPATCH text is always a clean CRT terminal
feed (red accent, ART_BIBLE v2 §1.2), never a sticker or pencil (DECISIONS 2026-10-05, DISPATCH text ruling).

### 8.3 First Corporation: Solace Biosystems (placeholder name)
Software for life-critical implants, sold as the **Continuum** subscription; prices just
rose; missed payments get implants bricked. Enemies are medical security software
(self-healing, "dosages", resistance called Compliance Lock). Raids are **Collections**.
Exploits: Intel (pricing memos), Breach (disable the kill-switch), Virus (open-source
patch that frees implants). Final server: the **Renewal Engine**.

### 8.4 Story Beat Paths (locked structure)
Each corporation has 5–6 hidden story paths; one is chosen at random at campaign start.
Beats reveal **in the order Exploits are collected**; extra Exploits unlock bonus beats;
the final boss delivers the finale. Solace paths: Recall Notice, Clinical Trial, Terms of
Service, The Cure, Ghost Patient (foreshadows DISPATCH), Hostile Takeover (foreshadows the
next corporation, Meridian Freight Systems; corporation names per DECISIONS.md 2026-09-24:
Meridian Freight Systems, Halcyon Civic, Orbital Commons). A beat may trigger a story raid.

### 8.4b Meridian Freight Systems (M8, DECISIONS.md 2026-09-24)
Logistics: automated freight, tariffs, tracking, last-mile drones. Enemies lean on
**WEIGHT** (spin resistance; was Inertia, D4), **PRIORITY** (RAM drain; its OVERFLOW shows as **AIRMAIL**; DECISIONS
2026-10-05, names for M14, D3), Conveyors (orbiting pointers) and courier
drones. Exploits: Intel (shipping manifests), Breach (customs override keys), Virus (rogue
routing table). Final server: **The Manifest**, which shields itself every turn unless its
Hub, the **Customs Seal** (was Priority Routing; DECISIONS 2026-10-05, ruling 6.1), is breached.

### 8.4c Halcyon Civic (M9, DECISIONS.md 2026-09-24)
Smart-city services: water, power, transit, policing-as-a-service. Enemies issue
**Citations** (PARASITE on your slice), heal and shield each other. Exploits: Intel
(council minutes), Breach (emergency override), Virus (open data leak). Final server:
**The Civic Core**, which heals and blocks every turn unless its Hub is breached.

### 8.4d Orbital Commons (M10, DECISIONS.md 2026-09-24)
Privatised orbit: satellite internet, positioning, weather. Enemies throw **Solar Flares**
(OVERCLOCK your slice: stronger once, then CORRUPTED) and orbit fast. Exploits: Intel
(launch codes), Breach (ground station override), Virus (open spectrum). Final server:
**The Commons Array**, which repairs and shields every turn unless its Hub is breached.

### 8.5 REBEL_CELL (final unlock corporation)
Unlocked by clearing every other corporation at ICE 10; has its own ICE 0–20 ladder.
Built from the player's profile: its Grid uses your most-used node types, its elites use
your classes' wheels, Hub Cores and Daemons, its raids use your asset types. "Final final"
achievement: REBEL_CELL at ICE 20 after all others at ICE 20.
*M11 ruling (2026-09-24, DECISIONS.md):* Mirror elites use your wheel at about 1.5x slice
output with one pointer and a hub running your data Daemons; the final boss is DISPATCH.

### 8.6 Delivery
Exploit beats and the finale (fully voiced), Terminal events, DISPATCH briefings, operative
barks, and an optional pirate-radio DJ at HQ.

---

## 9. UX & Visual Direction

### 9.1 Visual Baseline: the City, the Cell's Screens, Stickers and Pencil (locked)
*Rewritten around ART_BIBLE v2 (`docs/ART_BIBLE.md`) per DECISIONS 2026-10-05, ruling 4 ("Designer rulings:
art reintegration, pause point 0"); it supersedes the three-worlds baseline of v0.9. Reference
images: `docs/art_reference/`.*

| Medium | Job | Look |
|---|---|---|
| **Cel-shaded low-poly city** | The world: one city model for the City Grid, raids and netrun transit; HQs, Sites, combat backdrops | Gritty triangulated low-poly, three hard toon bands, wobbly **ink lines**; rain and haze at night |
| **CRT screens** | The Cell's own systems: slices, menus, resources, tooltips, forecasts, the dialogue feed | Navy glass with a cyan edge, scanlines, terminal type; **white glyphs** on the slice screens |
| **Vinyl stickers** | **Everything that never changes**: cards, buttons and verbs (SEND IT), titles, name plates, node-type stickers, result stamps | Die-cut vinyl with an ink keyline; peel, slap and dissolve |
| **Grease pencil** | **Plans** and annotations that are true to the rules | Opaque wax; **yellow = our routes and plans**, **red = threats** and losses; solid = what will happen, dashed = what-if; writes on, wipes off |
| **Light spill** | Glowing things light the city | Signs, screens and lights spill onto walls and streets |

Supporting media, each with one job (ART_BIBLE v2 §1.2): corp paper for intercepted corporate
documents, decrypted holo for hacked intel, binary bits for digital transitions and damage, bare
numerals for live values. Values that change never sit on a sticker. Cell colour: **hot pink**;
lime marks what the Cell owns. Details and tokens: ART_BIBLE v2 (visual source of truth from
M14); motion and interaction rules: `STYLE_GUIDE.md` §5.

### 9.2 Combat Readability
Always-on outcome preview per pointer; ghost preview on card hover; explicit targeting
(outer ring / inner ring / enemy wheel / satellite); per-pointer intent labels; migrating
pointers flicker a turn early; orbiting pointers show a trail. Layer rules (DECISIONS 2026-10-05, ruling 4,
ART_BIBLE v2 §1.2, §3.21): stickers and HUD controls stay clear of the wheels and their extras,
and each slice's value is always drawn on top of its overlays; **no UI ever covers grease
pencil**. A status is shown by its overlay on the slice: the overlay is the status; a small flat
corner badge appears only to carry a ×N stack tab or a ×1.5 / ×0.5 multiplier tag (DECISIONS 2026-10-05, ruling 10).

### 9.3 Raids & Grid
Threat paths drawn on links in red grease pencil, the Cell's plans in yellow (solid = will
happen, dashed = what-if); exact projected outcomes per node during setup; playout speed
controls and skip; post-raid summary. **DOWN** is shown the same way at every zoom, on the Grid
and in the raid view: a white bolt over a greyed marker (DECISIONS 2026-10-05, ruling 11; the raid words per
ruling 6.2, 3.3).

### 9.4 Heat Feedback
Heat bands follow thresholds (25/50/75), not arbitrary ranges. Distortion **pulses** on
threshold events rather than staying on. **The city reacts** (DECISIONS 2026-10-05, ruling 4, ART_BIBLE v2
§3.15, §4.3): Heat shows in the world, never as a HUD tint: alarm beacons, then searchlights,
then police lights behind the combat wheels as the bands rise; calm lights on the map nodes Heat
has made harder. A full-screen screen glitch exists only as an **Options extra, off by default**.

### 9.5 Input (PC)
Hover for previews, right-click to inspect, full keyboard support (e.g. Q/E nudge, Tab
cycle target, Space end turn, Z/Ctrl+Z rewind).

### 9.6 Accessibility
Reduce-effects toggle (scanline roll, flicker, chromatic aberration; static CRT scanlines may
stay, ART_BIBLE v2 §5.4 per DECISIONS 2026-10-05, ruling 4); flash limiter capped at
3 flashes/second, on by default; never colour alone (every slice has a glyph); text
scaling; subtitles with speaker names.

---

## 10. Audio

- **Mechanical ratchet:** every tick clicks; spins produce a decelerating run of clicks,
  nudges a single click, flips a mechanical clack. Players can hear wheel position.
- **Precision feedback:** Perfect = latch + wheel-local inversion + 2-frame freeze; Good =
  clean click; WEAK = stutter; NULL slice = static burst.
- **Music by context:** HQ/Grid lo-fi; netrun traversal dark ambient/synthwave; combat
  synthwave with layers added at Heat thresholds; raids industrial; bosses industrial
  synthwave; Solace raids corporate hold music; REBEL_CELL your HQ lo-fi slowed and wrong.
- **Voice:** full voice acting. Launch estimate ≈ 500 lines (1 corporation, 4 classes);
  ≈ +270 per corporation; each localisation is a full re-record. DISPATCH: human actor
  with processing increasing across campaigns.

---

## 11. Economy & Balancing

### 11.1 Resources
| Resource | Scope | Earned | Spent |
|---|---|---|---|
| Cycles | Netrun | Combat 10–20, elite 30–40, Router 15–25, events | Any in-run purchase |
| RAM | Combat | +4/turn | Extra nudges, cards, respins |
| Core Schematics | Campaign | Server Racks, raid wins, Cycle conversion (10:1) | Nodes, repairs, recruits, boosts, Heat reduction, profile unlocks |
| Heat | Campaign | See 11.5 | Reduced by sinks |

### 11.2 Shop Prices (Cycles)
Card 50–75 · Firmware 75–150 · Daemon 150–250 · card removal 50 (+25 each time) ·
slice overwrite 100 (NULL slice 150).

### 11.3 RAM Costs
Cards 0–3 · first nudge free, extras 1 · respin 4.

### 11.4 Schematics
| Tier | Per Server Rack | Raid win |
|---|---|---|
| 1 | 10 | 8 |
| 2 | 17 | 12 |
| 3 | 29 | 18 |
| 4 | 50 | 25 |

Costs: rookie 15 · basic node 20 · node upgrade 30 then 60 · repair 50% of install ·
one-time netrun boost 10–20 · −5 Heat 25 (+10 per purchase) · class unlock 80 (profile).

### 11.5 Heat Sources & Sinks
| Source | Heat |
|---|---|
| Server Rack capture | T1 +2, T2 +3, T3 +5, T4 +8 |
| Exploit extracted | +10 |
| Elite node | +1 |
| Operative death | +10 + tier |
| Burner trigger | +1 |
| Lost raid | +5 |

Sinks: Clean Signal −2 · Cold Exit −3 · Scrubber · Heat objective Sites (≈ −5 to −8) ·
Proxy Relay −1/run · purchase −5.
Targets: solo 5-run speed path crosses 50 before the boss; average ICE 5 campaign peaks
around 85–90 (current numbers need ≈ 40–45 Heat trimmed at ICE 5 — tune in playtest).

### 11.6 Scaling
Enemy HP per tier: base × 1.6^(tier−1); enemy damage (slice output) per tier: base ×
1.2^(tier−1) (split 2026-09-24 after simulation, see DECISIONS.md). Rewards: base ×
1.7^(tier−1).

### 11.7 Central Server: Exploits
The boss Site is the corporation's **Central Server** (DECISIONS 2026-10-05, names for M14, D5):
The Genome Core (Solace), The Master Manifest (Meridian), The Panopticon (Halcyon), Launch Control
(Orbital); REBEL_CELL's stays DISPATCH (8.5 names none).
Minimum **3 Exploits** to attempt the breach. Each extra Exploit weakens the boss further.
| Exploit | Effect on the final breach |
|---|---|
| Intel | Reveals boss phases and pointer moves; opens locked Grid links |
| Breach | Boss starts with one fewer pointer |
| Virus | Boss starts with CORRUPTED slices |

### 11.8 Pacing Targets
Netrun ≈ 15 min · raid ≈ 5 min · fast campaign 8 runs ≈ 2 h 15 m · average ≈ 24 runs ≈
6 h 35 m · ≈ 3 raids (fast) to ≈ 7 raids (average).

### 11.9 ICE Difficulty (20 cumulative levels; ICE 5 = average-player tuning target)
| ICE | Adds |
|---|---|
| 1–5 | Heat gain +10%, one fewer Heat objective Site, more elites, Cycle prices +10%, raid strength +15% |
| 6–10 | Heat sinks −15%, enemies +1 resistance, deaths +5 Heat, bosses change pointers earlier |
| 11–15 | Starting Bug card (0 RAM, drains 1 RAM, exhaust; a Mainframe can remove it), no free nudge on turn 1, repairs cost more, TAKEN Sites spawn stronger raids |
| 16–20 | Exploits +5 Heat, Purge at 90, final boss +1 pointer, raids gain a second wave |

---

## 12. Technical Architecture (summary)
Godot 4.7, GDScript. Deterministic pure-logic core (RefCounted classes) wrapped by Nodes
that follow **Signal Up, Call Down**. Content as `Resource` `.tres` files (41 schema
classes in `scripts/data/`); runtime state in separate state objects; seeded RNG streams;
JSON saves. Full detail: `TECH_SPEC.md`.

## 13. Open Items / Deferred
- ~~Full card pool beyond the slice set; Ghost, Rigger, Botnet content~~ (M6-M7, 2026-09-24).
- ~~Additional corporations and their story paths; REBEL_CELL generator~~ (M8-M11).
- Complete ICE 1–20 level list (bands defined above).
- Final Heat tuning (11.5) and HP/damage tuning — playtest.
- Story path scripts, voice casting, localisation plan.

---

## Appendix A — Vertical Slice Content

### A.1 Breaker Starting Deck (10)
| Card | Count | Effect | RAM |
|---|---|---|---|
| Jolt | 4 | Spin 3 (+1 Breaker = 4) | 1 |
| Brute Spin | 2 | Spin 6 (+1 = 7) | 2 |
| Fine Tune | 2 | Two ±1 nudges on one ring | 1 |
| Mirror Flip | 1 | Flip target wheel | 3 |
| Overdrive (Breaker only) | 1 | OVERCLOCK your slice under the pointer | 1 |

Breaker Rank 1 ring: ×2 / Pierce / —.

### A.2 Shared Card Pool (20)
| # | Card | Group | Effect | RAM |
|---|---|---|---|---|
| 1 | Twist | Rotation | Spin 4 | 1 |
| 2 | Heavy Spin | Rotation | Spin 9 | 2 |
| 3 | Counter-Spin | Rotation | Spin −5 | 1 |
| 4 | Ring Lock | Rotation | This turn, spins don't move your inner ring | 0 |
| 5 | Momentum | Rotation | Spin 2; spin 5 instead if you already spun this turn | 1 |
| 6 | Gear Shift | Rotation | Move your inner ring 5 ticks | 1 |
| 7 | Snap | Precision | Move a ring to the nearest slice centre (Perfect) | 2 |
| 8 | Micro-Adjust | Precision | Two ±1 nudges. Exhaust. | 0 |
| 9 | Calibrate | Precision | Your next 2 nudges this turn are free | 1 |
| 10 | Ring Tap | Precision | Two ±1 nudges on your inner ring | 1 |
| 11 | Steady Hand | Precision | If your slice is Perfect at end of turn, +2 RAM next turn | 1 |
| 12 | Strip | Enemy control | Remove 2 resistance | 1 |
| 13 | Hub Breach | Enemy control | Disable target Hub for 1 turn | 2 |
| 14 | Undock | Enemy control | Move a satellite to an adjacent slice | 1 |
| 15 | Freeze | Enemy control | Target wheel skips its next respin. Exhaust. | 3 |
| 16 | Jam | Enemy control | Nudge an enemy wheel ±1, ignoring resistance | 2 |
| 17 | Cache | Utility | Gain 3 RAM. Exhaust. | 0 |
| 18 | Pull | Utility | Draw 2 | 1 |
| 19 | Cleanse | Utility | Remove CORRUPTED from a slice | 1 |
| 20 | Encrypt | Utility | ENCRYPT a slice | 1 |

### A.3 Solace Enemies (Tier 1 base values; scale per 11.6)
| Enemy | HP | Wheel (6 slices) | Special |
|---|---|---|---|
| Collections Agent | 40 | Shim 8, Shim 8, Defrag 6, Dose, Overflow 14, Null | Satellite drone (5 HP; Shim 3 / Defrag 3) docked on slice 1 at combat start |
| Triage Unit | 45 | Defrag 8, Hotfix 6, Shim 6, Hotfix 6, Defrag 8, Null | — |
| Compliance Officer | 50 | Shim 7, Shim 7, Defrag 6, Overflow 12, Shim 7, Null | Hub: Compliance Lock, resistance 3 |
| Dosage Dispenser | 38 | Dose, Shim 6, Dose, Defrag 5, Shim 6, Null | — |
| Billing Daemon | 42 | Shim 7, Shim 7, Defrag 6, Overflow 12, Shim 7, Null | Attacks drain 1 RAM (Overflow drains 2) |
| Care Swarm | 25 | Defrag 4, Hotfix 4, Defrag 4, Hotfix 4, Shim 4, Null | 3 satellites (4 HP; Shim 3, Shim 3, Defrag 2) |
| **Elite:** Claims Adjuster | 90 | Shim 10, Defrag 8, Overflow 16, Shim 10, Dose, Null | 2 pointers (ticks 0, 15) |
| **Elite:** Recall Unit | 85 | Shim 9, Shim 9, Defrag 8, Overflow 15, Sandbox 5, Null | Pointer orbits +2 ticks/turn; passive resistance 1 |
| **Boss:** Renewal Engine | 300 | Shim 14, Shim 14, Defrag 12, Dose, Overflow 24, Null | Hub *Auto-Renew*: heal 10/turn unless Hub-Breached. 66%: Multiply to 2 pointers (0, 15). 33%: pointers Orbit 3/turn and spawn 2 drones. |

Dose = INFECT slice applying CORRUPTED to a random non-NULL player slice. Solace wheels show
HOTFIX as **GROWTH** (DECISIONS 2026-10-05, names for M14, D4).

*M7 balance ruling (2026-09-24, DECISIONS.md):* elites +25% HP (Claims Adjuster 112, Recall
Unit 106, Account Manager 150) and the Renewal Engine 360 HP; enemy damage scales 1.3 per
tier. The table keeps the original values for reference.

### A.4 Slice Firmware & Daemons
Firmware: Patch+, Hardened, Burner, Leech, Mirror, Shunt.
Daemons: Clean Signal, Cold Exit, Scrubber, Fault Tolerance, Kernel Sync, Zero Day.

### A.5 Defense Assets & Threats
| Asset | Integrity | Effect |
|---|---|---|
| Turret | 10 | 4 dmg, range 1, targets first in path |
| ICE Lock | 8 | Holds a threat 2 steps |
| Decoy | 12 | Pull 3 (attracts threat routing) |

| Threat | Integrity | Damage | Speed | Routing |
|---|---|---|---|---|
| Collector | 12 | 5 | 1 | Shortest to home |
| Auditor | 8 | 3 | 2 | Highest-value node |
| Enforcer | 25 | 9 | 1 | Weakest node |

### A.6 Slice City Grid (10 Sites) — superseded 2026-09-24
The M3 slice used 10 Sites. Solace now ships its full 32-Site Grid (see DECISIONS.md,
batch 2b): ten T1, eight T2 (three Exploits), eight T3, four Heat objectives, the boss.
The breach still requires 3 Exploits.
