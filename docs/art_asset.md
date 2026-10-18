# REBEL_CELL — Art asset list

Every element of the game that the player sees, for concept art. The list says **what each
element is, what it must communicate, and which states or variants it needs**. It does not say
how anything should look or be made (drawn, painted, modelled, animated, lettered, lit, etc.):
that is for the art style guide to decide. Where the game already depends on two things being
told apart (e.g. a claimed Site vs a seized one), that requirement is noted, because the style
must preserve it.

Legend for the "States / variants" notes: every item listed needs a concept for each state
named, unless the style guide decides a state is shown by a shared treatment.

- Part A — Identity: the game, the factions, the Heat levels
- Part B — Characters and units
- Part C — The world: the city and the Cell's HQ
- Part D — Maps and navigation
- Part E — Combat
- Part F — Items, rewards and progression
- Part G — Screens (layout inventory, screen by screen)
- Part H — Reusable interface pieces
- Part I — Icons and symbols
- Part J — Stamps, verdicts and headline words
- Part K — Moments of motion and feedback
- Part L — Lettering roles
- Part M — Known gaps (things that currently have no distinct look at all)
- Appendix — Full content catalogue (every card, enemy, Site, event… by name)

Content counts: 8 operative classes, 5 corporations (160 Sites), 58 enemies, 22 hub cores,
71 cards, 38 slices, 24 daemons, 18 firmware chips, 7 inner-ring segments, 15 exploits,
15 network nodes, 5 home servers, 11 defence assets, 17 threats, 40 raids, 124 events,
18 profile unlocks, 30 story paths.

---

## Part A — Identity

### A1. The game
| Element | What it communicates | States / variants |
|---|---|---|
| **REBEL_CELL logo** | The game's name; title screen, start page | Idle; a small idle motion is wanted |
| **The Cell's mascot / emblem** | The rebel cell as a character: a grinning "cell" that signs the Cell's own words (the current concept is hexagon-based; not binding) | Used beside titles (NETRUN, CODEX, LOOT); cracked/broken version wanted for a lost campaign |
| **The Cell's personal mark** | A small doodle (currently a crown) the Cell adds to its scrawled slogans | — |
| **Cell slogans** | Short hand-written slogans: NEVER SLEEP (title), TRUST NO ONE (start page), PLAY IT SAFE?? (events), and the plan note "1. BREACH / 2. DISABLE / 3. EXFIL" | Decoration; each placed once |

### A2. Factions
Every corporation needs: an **emblem/logo**, a **colour identity** (the game uses one colour
per corporation to mark its territory, units and text, so the five must be clearly different
from each other and from the Cell's own colours), a **pattern**, an **architecture flavour** for
its district, a **HQ landmark**, and a **spokesperson voice** look (see B3).

| Faction | Who they are | Landmark in the city (current concept) |
|---|---|---|
| **Solace Biosystems** | Medical/biotech: implants, subscriptions, patient records | "The Double Helix" — a DNA double-helix tower on a podium |
| **Meridian Freight Systems** | Logistics giant: parcels, customs, drones, freight | "Freight Ziggurat" — terraced freight building with container yards and a crane |
| **Halcyon Civic** | The contractor that runs the city: water, power, transit, police | "Civic Pyramid" — tiered civic pyramid with colonnades and a halo ring |
| **Orbital Commons** | Satellites, uplinks, launches, positioning | "Orbital Tether" — a needle tower with a tether rising into the sky |
| **REBEL_CELL (hidden 5th corporation)** | The handler AI "DISPATCH" behind the Cell, revealed late | No tower: its territory is marked by a giant raised fist formed by the city's roads, readable from above |
| **The Cell (the player)** | The rebel cell itself | Needs its own identity separate from the hidden REBEL_CELL corporation; it owns "Cell turf" |
| **The Sprawl** | Neutral city (centre and two corners) | No landmark |

Meaning the palette must keep separate: **Cell territory / good for you**, **damage / you are
here / current node**, **neutral net / not yet taken**, **seized / frozen / warning**, and the
five corporation identities.

### A3. Heat levels (how hunted the Cell is)
Heat is shown by band. Each band needs a recognisable look for the Heat poster, the city
(corporate presence grows) and the HQ window (searchlights grow).

| Band | Threshold | Word |
|---|---|---|
| 0 | 0-24 | COOL |
| 1 | 25-49 | NOTICED |
| 2 | 50-74 | FLAGGED |
| 3 | 75+ | HUNTED |

---

## Part B — Characters and units

### B1. Operatives (the player's crew)
Eight classes (full list in the Appendix). Each class needs: a **character concept** (full figure
and bust), a **portrait for its Polaroid/dossier**, its **class mark**, its **silhouette/prop**
identity, and its **wheel bezel ornament** (the frame of its spinner in combat). The four
alternative classes are variants of a base class and should read as related.

| Class | Base / alternative | Identity notes from the design (keep or replace) |
|---|---|---|
| Breaker | base | Heavy jacket, antenna-like crowbar; bezel: riveted plates |
| Wrecker | alt of Breaker | Welding visor, scars; bezel: welded, dented rim |
| Ghost | base | Hood, face mesh; bezel: flickering translucent rim |
| Phantom | alt of Ghost | Mask, long collar; bezel: after-image double rim |
| Rigger | base | Goggles, cable harness; bezel: cable-wrapped rim |
| Overclocker | alt of Rigger | Heat-sink crown, lights; bezel: vented fins |
| Botnet | base | Drone halo; bezel: orbiting ring of dots |
| Hivemind | alt of Botnet | Linked-node headset; bezel: hex lattice |

**Operative portrait states:** neutral · hurt (low HP, 25% or less) · triumphant · flatlined
(dead, permanent) · stationed on a Site ("ON <SITE>") · recruit (unhired). Individual operatives
of the same class vary (hair, visor, lens, etc.), so the class concept needs a variation range.

**Operative expressions / uses:** crew dossier photo, small crew chip (drag token), combat
portrait, HQ "WANTED" mugshot of the lead operative, drag ghost when recruiting.

### B2. Enemies
58 combatants (Appendix), in three roles: **Regular**, **Elite**, **Boss**. Each needs an
enemy concept (bust or hologram shown above its wheel), its **wheel bezel/frame**
(corporate, per corporation) and its **hub core** look. Bosses need a larger presentation
and a look per **phase** (bosses change phase mid-fight: PHASE 2, PHASE 3).
Enemy portrait kinds the game distinguishes: corporate human agent, machine (drone, daemon,
core), boss, corporation face.

**Enemy states:** entering the fight · idle · hit · telegraphing an action · breaking (the wheel
cracks and falls apart, hub shatters) · defeated (an empty spot that says who was beaten).

### B3. Speakers (voice lines shown as subtitles / dialogue)
Each speaker needs a recognisable identity in the subtitle strip and wherever they "talk".
| Speaker | Who | Variants |
|---|---|---|
| **DISPATCH** | The Cell's handler AI (later revealed as the REBEL_CELL corporation) | One per corporation campaign (5 line sets); must look unlike every other speaker |
| **Corporate spokesperson** | The target corporation talking | 5 (one per corporation) |
| **Pirate radio DJ** | Street radio host on the HQ | 6 (one per corporation + one HQ) |
| **Operative barks** | The operative in the fight | 4 base classes |
| **Observer (AI observer)** | A watching AI voice | 1 |
| **Street merc / narrator** | Street voice, story narration | 1 each |

### B4. Threats (raid units)
17 threats (Appendix) move across the map during raids. **Today they all share one generic
token**; each needs its own unit concept, readable at small map size, tied to its corporation.
Movement types the art should suggest: fast, heavy/armoured, slow, drops in from above, seals or
jams the link behind it, cuts through locked links, freezes a link. REBEL_CELL's three threats
(Informant, Loyalist, Purger) mirror the player's own defences.
**Threat states:** entering · moving · lured (pulled toward a decoy) · held/frozen · hit ·
destroyed · withdrawn at the end of a raid · reached the Cell's home.

### B5. Drones / satellites
Small units that dock around a wheel in combat (e.g. "collections drone"); the Botnet class
fights through them. Each needs a token that can be identified by name (reviewers could not find
"the drone" the text referred to), with a small HP readout and an aim mark.

---

## Part C — The world: the city and the Cell's HQ

### C1. The city (one city, seen two ways)
The whole game takes place over one night-time city seen from above (isometric). It is shown in
two readings that must feel like the same place:
1. **Physical city** — seen through the HQ window: title screen and HQ pages.
2. **The net** — the same city as cyberspace: City Grid, raids, netrun route, shop, events,
   loot, and (dimmed) behind combat.

| Element | Notes / variants |
|---|---|
| **Districts / territories** | One per corporation + REBEL_CELL + the neutral Sprawl (3 areas); organic borders with a mixed band along each border |
| **District architecture** | Per corporation: Solace (many cylinders, mixed towers), Meridian (low: warehouses, boxes, stepped blocks), Halcyon (stepped blocks, tapered towers), Orbital (tall, needles), REBEL_CELL / Sprawl (generic mix) |
| **Building types** | Box, stepped tower, cylinder, hex prism, tapered tower, needle, warehouse. (Design-review extras, not in the game: pyramid, obelisk, mastaba, pagoda, gabled house, clock tower, dome, minaret, step temple) |
| **Building details** | Windows (some blink), rooftop antennae, small rooftop signs, beacons on the tallest roofs, plant-room boxes |
| **HQ landmarks** | Four corporate landmarks (A2), each on a plaza with lamp posts; a name sign per HQ |
| **The Cell's fist** | REBEL_CELL territory's roads form a giant raised fist |
| **Streets** | Irregular grid; wide busy avenues and thin quiet streets; crossings |
| **Traffic** | Moving lights on busy streets |
| **Beacons and signs** | Blinking beacons; rooftop signs; some signs flicker |
| **Sky and weather** | Night sky; rain (seen on the HQ window); haze toward the top |
| **Net overlay** | In the net reading, a drifting lattice over the city and streets reading as circuit traces |
| **Placeholder city** | A simple silhouette of the city shown for a moment while the full view is prepared |

### C2. Ownership, territory change and Heat on the city
| Element | What it communicates | States / variants |
|---|---|---|
| **District ownership influence** | Who controls the ground around each Site | Leaning to the Cell (claimed; lightly for cleared) · leaning to the corporation (seized, disabled) |
| **Territory change** | A Site changed owner: the change spreads outward from it through the streets | Favouring the Cell · favouring the corporation |
| **Territory marks** | Left on the changed area after a change | CLAIMED · CLEARED · SEIZED · DISABLED |
| **Corporate creep** | Rising Heat: the corporation's presence spreads over the city | By Heat band 0-3; continuous in the fight arena |
| **Heat searchlights** | Seen through the HQ window | None at band 0, more and faster per band |

### C3. The Cell's HQ (the room)
| Element | Notes |
|---|---|
| **HQ room at night** | The Cell's room, looking down through a rain-streaked window onto the target corporation's district |
| **The deck** | The Cell's hacking rig; its edge is visible along the bottom of the screen; the camera dives into its screen when jacking in |
| **Deck monitor** | A screen on the deck that shows the City Grid mini-map; status "RAID INBOUND" / "STABLE" |
| **Wall pieces** | WANTED/Heat poster, JACK IN button, pirate radio, crew photos (Part G) |

### C4. Combat arena
The net city framed on the district of the corporation being fought, darkened so the wheels read
first. Needs a variant per corporation.

---

## Part D — Maps and navigation

### D1. City Grid Sites
Each corporation has 32 Sites (160 in all, named in the Appendix): home (CORE), 10 × tier 1,
8 × tier 2 (incl. 3 Exploit Sites), 8 × tier 3, 1 boss. Each Site is a real building of the city.
Named Sites are strong candidates for individual building concepts, especially each corporation's
**boss Site** (Solace: Renewal Engine · Meridian: The Manifest · Halcyon: The Civic Core ·
Orbital: The Commons Array · REBEL_CELL: DISPATCH) and **CORE / the Cell's home**.

| Element | What it communicates | States / variants |
|---|---|---|
| **Site marker (by kind)** | What kind of Site it is; each kind needs a distinct silhouette + symbol | Plain Site (shows its tier) · Exploit Site · Heat-reduction Site ("cooling") · Boss Site (large) · CORE / home (large, always labelled CORE) |
| **Tier indicator** | Difficulty 1-4 | 1 · 2 · 3 · 4 |
| **Site status** | Who holds it | Corporate · Cleared · Claimed (the Cell's) · Seized (taken back by a raid) · Disabled (a claimed node knocked out) |
| **Site label** | Name; sits clear of the marker, with a leader if moved away | Normal · hovered · selected |
| **Selected Site** | The Site you are looking at | Outline reveal + selection ring |
| **Hovered Site** | Pointer over a Site or its list row | — |
| **Changed-since-last-look pulse** | A Site whose status changed | — |

### D2. Network nodes and the home server
Structures the Cell builds on claimed Sites. **They currently have no map look at all (text
only)**: each needs a map marker and a card/icon.
- **Node types (6):** Relay, Firewall Relay (built-in turret), Proxy Relay (scrubs Heat),
  Compiler Rack, Vault Terminal, Safehouse (station an operative). 15 node entries in the Appendix.
- **Home server variants (5):** Standard, Bunker (fights back), Fortress (walls), Ghost (lock
  chamber), Relay Nest (spread-out relays).
- **States:** healthy · damaged (integrity shown) · upgraded (+level) · disabled · destroyed (home
  fell).

### D3. Links and routes on the Grid
| Link type | Meaning |
|---|---|
| Your network link | Connects your claimed Sites; data packets travel along it (stop when a raid's verdict is in) |
| Ordinary link | A connection you don't own |
| Locked link | Closed until an Intel exploit opens it · opened state |
| Frozen / sealed / jammed link | Cut for the current raid by a threat |
| Threat route | Where a pending raid will travel, from its entry Site to CORE, with direction |

### D4. Map markers
| Marker | Notes |
|---|---|
| **YOU ARE HERE** | Current position (Grid entry and netrun) |
| **Threat marker** | Threats waiting at an entry Site (one per threat, corporation-coloured) |
| **Placed defence asset** | Each asset placed on a node, beside the Site marker; the latest one named |
| **Forecast change** | A number change floating off a node, e.g. "25 → 30 ▲", better vs worse, captioned RAID FORECAST |
| **Map key / legend** | Explains Site status, links, kinds, tier. Full panel · strip · folded "MAP KEY" button |
| **HQ mini-map** | Small version of the Grid on the deck monitor: Sites by tier and status, CORE, selection, links, threat arrows, stationed crew |

### D5. Netrun route map
The route through a Site's network, drawn on the city from left to right toward the target
building.
| Element | Variants / states |
|---|---|
| **Route node kinds** | Fight (Router) · Elite fight · Event (Terminal) · Shop (Modem) · Server Rack (the Site's guardian, always last, large) |
| **Route node states** | Current · next choice (numbered) · further ahead · visited (ticked) · unreachable · elite/Rack (corporation) |
| **Roads** | Walked path · live choices from here · other roads · "same road" twin choices |
| **Route key** | One row per node kind present, plus the state meanings |
| **Move** | The marker travels along the street to the chosen node; target pulses; new node appears; old node marked visited |

---

## Part E — Combat

Combat resolves on spinning wheels (30 ticks). Each combatant has a wheel; cards spin, nudge and
flip wheels; SEND IT resolves the turn.

### E1. The wheel (spinner)
| Element | What it communicates | States / variants |
|---|---|---|
| **Wheel body and frame (bezel)** | Whose wheel it is | Per operative class (8, see B1) · per corporation for enemies · boss |
| **Slices (6 per wheel)** | What the wheel does when a needle lands on it: a type + a value | 9 slice types (E2) + special enemy slices; states: normal · valid drop target · hovered target · landed · landed on MISS · afflicted by a status · has a firmware chip · spinning (blur) |
| **"Perfect" mark** | The exact spot on each slice for a perfect landing | — |
| **Needles (pointers)** | Where the wheel resolves | Behaviours: fixed · multiply (more needles) · migrate (jumps; next position telegraphed) · orbit (steps around, leaves a trail); states: idle · resolving now · telegraphed "next" |
| **Inner ring** | A class/rank ring inside the slices, 3 segments | Per base class (4 rings); 7 segment kinds (Accelerator, Anchor, Blank, Corrupt, Echo, Pierce, x2) |
| **Hub** | The centre: name, block, shield, resistance, frozen, hub core, breached | Normal · breached |
| **Hub core emblem** | The hub core installed (22, Appendix) | One emblem per core; Mk2 upgrades of class cores |
| **HP display** | Health around the wheel, the predicted loss, heals, a trailing drop | Normal · predicted loss · heal · hit |
| **NEXT plate** | Predicted HP after the turn, e.g. "NEXT 49 (−11)" | Normal · **LETHAL** (this wheel dies) |
| **LAST TURN plate** | What happened last turn as an equation: hits − blocked (or − evaded) = through; heals; corruption | Appears after each turn |
| **Forecast tag** | Above each wheel: the landing slice, aim quality (1-3 pips), and one result chip per effect | Chip kinds: hit (who hits whom, how much), loss, gain, guard (block/shield/evade), status, resistance, run resources (RAM, Heat, Cycles, Schematics, draw, drones, needles, HP), rules (free nudges, hub breach, new slices, "moves"), NO CHANGE, overflow "+N MORE". States: forecast · previewing a card ("YOUR <CARD>", with the previous result struck out as WAS) · during the replay each line ticked off · "THIS TURN" / "NEXT TURN" captions |
| **Nudge controls** | Turn a wheel one tick anticlockwise / clockwise; a second pair for the inner ring | Idle · hover · valid drop target for nudge cards; key/button hint beside |
| **Target reticle** | Which wheel/slice a card is aimed at | — |
| **Ghost preview** | Where the wheel will turn to, before committing | Outer ring · inner ring |
| **Satellites / drones** | Small units docked on a wheel | With HP and aim mark |
| **End states** | Enemy beaten → an empty spot naming it, DEFEATED. Operative lost → wheel dark, DEFEAT (stays). Enemy break: cracks, falls apart, hub shatters. Enemy entering: slides in with its name | — |

### E2. Slice types (need a symbol each; must stay distinct at small size)
ATTACK · CRITICAL · DEFEND · SHIELD · EVADE · HEAL · AFFLICT · DEPLOY (drone) · MISS.
Special enemy slices per corporation: **Tariff** (Meridian; drains RAM), **Citation** (Halcyon;
plants a Parasite), **Solar Flare** (Orbital; overclocks then corrupts), **Dose** (Solace;
corrupts); **Inertia** slices (add resistance). All 38 slices are listed in the Appendix.

### E3. Statuses (need a symbol each; must show whether it helps or hurts you)
CORRUPTED · OVERCLOCKED · ENCRYPTED · PARASITE. Plus: a predicted status and a cleanse.

### E4. Aim quality (precision)
PERFECT · GOOD · PARTIAL (half power) · MISS — each needs a distinct landing feedback and a
1-3 pip indicator on the forecast tag.

### E5. Cards in combat
| Element | Notes |
|---|---|
| **Card (template)** | Title, RAM cost, text, a row of pictograms for what it does, key hint; shown in hand, loot, shop, deck viewer, drag ghost. Rarity must be visible (Common / Uncommon / Rare / Boss). Card **type** should be visible |
| **Card art** | 71 cards (Appendix): each needs an illustration or emblem |
| **Card states** | In hand · hover/focus · aimed · dragging · can't afford (RAM) · disabled · being played (flies, lands, dissolves) · exhausted (destroyed) · discarded · dealt from the deck |
| **Deck pile / discard pile** | Where cards come from and go |
| **Card pictograms** | spin (clockwise / anticlockwise, with a number) · respin · nudge (×n, inner ring) · flip · slice-type with amount · status · RAM ± · draw · freeze · resistance ± · breach · cleanse · snap · 2× nudge · again · free nudge · spin n+ · ring lock · "Perfect: RAM+" · undock |

### E6. Combat controls and meters
| Element | Notes / states |
|---|---|
| **SEND IT** | The main end-turn action. States: ready · hover · pressed · "all RAM spent" hint · disabled. Replaced after a fight by **LOOT** / **CONTINUE** (won) or **JACK OUT** (lost) |
| **RESPIN** | Respin action with its RAM cost; hover · disabled |
| **UNDO** | Undo / rewind action; hover · disabled |
| **RAM meter** | Available RAM as units: available · about to be spent · about to be gained · refused ("NEED n · HAVE m") |
| **Status line** | TURN n · FREE NUDGE n |
| **Operative portrait** | In the fight's side column (B1 states) |
| **Daemon row** | The installed daemons as sigils (F3) |
| **Aim line + aim hint** | From the card to its target; the instruction line |
| **Tutorial box** | 7 steps (THE WHEEL, NUDGE, RESISTANCE, CARDS, UNDO, SEND IT, HEAT & BANKING), Next / Skip |

---

## Part F — Items, rewards and progression

### F1. Resources and currencies (each needs an icon; see Part I)
Heat · Schematics (campaign currency) · Cycles (run currency) · RAM (combat energy) · HP ·
Home integrity · Exploits · Raids · ICE (difficulty level) · Crew · Rank · Banked · Armory.

### F2. Items (full lists in the Appendix)
| Item family | Count | Needs |
|---|---|---|
| Cards | 71 | Card art + template (E5) |
| Slices | 38 | Slice-type symbol + value; tile look for the shop |
| Daemons | 24 | A unique **sigil** each; rarity visible |
| Firmware chips | 18 | A chip look each (sockets into a wheel slot) |
| Hub cores | 22 | Emblem each |
| Inner-ring segments | 7 | Symbol each; a "class default" mark |
| Defence assets | 8 types (+ built-ins) | Unit/structure concept for the map + a card; types: gun (Turret, Sentry, Railgun, Flak Array), lock (ICE Lock, Tar Pit), lure (Decoy, Honeypot). Built-ins: firewall turret, bunker turret, ghost lock |
| Exploits | 3 kinds (Intel / Breach / Virus), 15 named | Symbol per kind; named rewards |
| Next-run boosts | 2 (Field Kit, Overclocked Deck) | Icon each |
| Profile unlocks | 18 | Badge each (kinds: class, class alternative, corporation, home server, node type, skin) |
| Achievements | 10: First Blood, Banked, Breach, Clean Hands, Average Is a Lie, Cold Storage, Purge Survivor, The Wall, Perfectionist, Final Final | Badge each: earned · not earned (locked) |
| Heat rules | Rules in force at high Heat (e.g. "Raid Strength +10%") | A badge treatment |

### F3. Rarity
Common · Uncommon · Rare · Boss — must be recognisable on cards, slices, daemons, firmware and
assets.

---

## Part G — Screens (what each screen holds)

Layout inventory only; each listed piece is described in Parts D-F and H-J.

| # | Screen | Holds |
|---|---|---|
| G1 | **Title / main menu** | City backdrop through the HQ window · logo + mascot · version line · subtitle band · menu (Continue with slot summary, Campaigns, Tutorial, Codex, Stats & achievements, Options, Quit) · profile stats (campaigns, won, best ICE, runs, raids, badges) · plan note · slogan |
| G2 | **Campaign slots** | 3 slots (corporation, Heat, ICE, runs, state or empty) · New / Load / Delete / Back. Wanted: case-file folder cards with the corporation, landmark, Heat, runs, last played, crew photos |
| G3 | **Stats & achievements** | Profile numbers · best ICE per corporation · 10 achievements · run history (one line per run; receipts wanted) |
| G4 | **Codex** | Sections: Slices, Statuses & precision, Classes, Corporations (locked = ???), Cards, Firmware, Daemons, Ring segments, Enemies, Nodes, Home servers, Defence assets, Threats, Lexicon · recent lines heard. Wanted: an illustrated entry per item |
| G5 | **Options** | Accessibility, Display, Audio, Controls (rebinding), Language · toggles, sliders, pickers, Reset, Close |
| G6 | **Pause menu** | Resume, Options, Codex, Save & quit, Quit · campaign share code |
| G7 | **New campaign (start page)** | Seed · target corporation (dossier tiles wanted; locked shown with how to unlock) · ICE level + its rules · home server choice (5) · crew class choice (8) · New campaign · Today's run (daily seed, modifiers) · share codes · deck menu · profile & records |
| G8 | **HQ** | Top bar · deck menu (City Grid, raid pending, scrub Heat, patch home, Codex, Settings, Save) · CELL STATUS badges (home, exploits, sites, armory, Heat rules) · deck monitor with mini-map · crew roster dossiers with orders (Loadout, Recall/Station, rank-3 segment swaps) · WANTED Heat poster with mugshot · JACK IN · pirate radio · Black Market (recruit, next-run boosts, profile unlocks) · story so far · MORE BELOW |
| G9 | **City Grid** | The Grid map (Part D) · map key · navigation (prev/next Site, back, raid setup) · selected Site card (tier, status, objective, node, upgrade, placed assets, guard; actions: who runs it, JACK IN, crew chips, build node/claim, repair, upgrade) · RUNS OPEN NOW list with "IF CLEARED:" gains (win, exploit, Heat ±, raid, Schematics ±, opens n Sites, can be your node, no gain) |
| G10 | **Raid setup** | Raid map with threat routes and projected outcomes · raid card (forecast stamp, home before → after, stopped, strength, entry Sites, frozen links) · YOUR NODES list (target, projected outcome, placed assets, withdraw/move) · defence loadout (armory asset cards, deploy steps) · START DEFENSE |
| G11 | **Raid playout** | Map following the raid (Part K) · forecast stamp becoming the result · live raid feed · speed 1x/2x/4x · Skip · Continue |
| G12 | **Raid report** | Result stamp · report (home before → after, destroyed, reached home, per-node outcome) |
| G13 | **Campaign end** | Verdict WON / LOST · headline · story uncovered · profile (won, lost, best ICE, records). Wanted: distinct WON (corporation landmark falling, "CORP DOWN", crew photo wall) and LOST ("CELL BURNED", the Cell emblem cracked) presentations |
| G14 | **Jack in / jack out** | Transition into the net through the deck's screen and back · CONNECTING TO + progress · destination name with tier · optional RAID INCOMING + corporation |
| G15 | **Netrun route** | Route map (D5) · route choices with their node icon, number, Heat cost and what lies ahead · route key · Grid/route view toggle · save & quit |
| G16 | **Combat** | Part E |
| G17 | **Loot** | Source (FIGHT WON / ELITE DOWN / RACK BREACHED / EVENT PAYOUT / PAYOUT) · "pick a card / chip / daemon / slice" · offers · for firmware: slot picker + small spinner · Skip |
| G18 | **Modem (shop)** | Shop sign (MODEM / CYBER SHOP, with BUY and SHRED notes) · four sections: Microchips (firmware), Cards, Slices, Daemons · Remove a card (shred) · wallet · small spinner · price tags · BUY actions · SOLD · LEAVE THE MODEM |
| G19 | **Terminal event** | Event page (title, speaker, story; street/corporate speakers vs DISPATCH look different) · choices with outcome icons (gain/cost, "no change") · the chosen outcome confirmed on the page. 124 events (Appendix) are candidates for illustrations |
| G20 | **Mid-run raid interlude** | Raid card with forecast · run assets and armory assets · per-node rows · START DEFENSE · then a playout |
| G21 | **Run end** | Verdict: JACKED OUT / HOME FELL / FLATLINED · fate line (permadeath) · run stats (combats, elites, cycles, banked, Heat) · why Heat changed · Back to HQ. Wanted: FLATLINED as a full-screen moment |
| G22 | **Deck viewer** | Grid of cards · tabs (deck / spinner / next operative) · remove mode (mark, shred) · upgrade mode · card detail |
| G23 | **Spinner viewer** | The wheel large with slices, hub core, inner-ring segments · upgrade mode · details |
| G24 | **Loadout viewer** | Deck and spinner tabs · rank-3 segment swap chips |
| G25 | **Daemon tray** | Installed daemons with details, pin |

---

## Part H — Reusable interface pieces

| Piece | What it is | States / variants |
|---|---|---|
| **Top bar** | Screen number + title; stat tags; VIEW LOADOUT; DAEMONS | Stat groups "CAMPAIGN" / "THIS RUN"; a tag pulses when something lands on it; refusal flash |
| **Stat tag** | One resource: name, icon, value | Full · compact; value change; refusal |
| **Panel / window** | The main container for menus and information | Accent per use: neutral, Cell, good, warning, corporation; with title and a right-side tag |
| **Document panel** | A second container family for in-world documents (events, notes, radio) | — |
| **Note** | Short text notes (pirate radio, plan, codex, stats, tutorial) | Several stocks |
| **Menu line** | "> ITEM" with its icon | Normal · focused (highlight, caret) · disabled |
| **Primary action button** | The one main action on a page (New campaign, JACK IN, START DEFENSE, Continue) | Normal · hover · focus · pressed · disabled |
| **Secondary button** | Normal buttons | Same states |
| **Choice / note button** | Event choices, chips | Same + chosen |
| **Big action words** | SEND IT, LOOT, CONTINUE, JACK OUT, LEAVE THE MODEM, REMOVE, UPGRADE | Idle · hover · pressed · first appearance |
| **Secondary combat actions** | RESPIN, UNDO | Hover · disabled |
| **Buy action** | "BUY" + price | Affordable · focused · unaffordable |
| **Price tag** | Item price (a range when it depends on the slot) | Affordable · unaffordable |
| **Badge** | Small symbol + value, optional mini meter | Per meaning |
| **Outcome row** | An event choice's effects as symbols with +/− numbers, "no change" | Gain · cost |
| **Crew dossier** | Photo, name, class, rank, HP, kit numbers, orders | Normal · stationed · dead · low HP · compact |
| **Crew chip** | Small photo token of an operative (drag onto JACK IN) | Normal · dragging |
| **Asset card** | A defence asset: symbol, name, HP, copies left, what it does | Normal · hover · dragging · disabled |
| **Forecast / result stamp** | A ring holding a symbol, a caption and a verdict | Forecast (not yet happened) vs result (happened); good vs bad |
| **Heat poster** | "HEAT", value, a bar with the 3 thresholds, band word | Full (WANTED + mugshot, HQ) · compact (combat); band crossing |
| **Subtitle strip** | Speaker + line, pages | Per speaker (B3) |
| **Toast / notice** | Short message at the foot | Refusal · news · plain |
| **Tooltip / focus tip / inspect** | Explanations | — |
| **Confirm dialog** | "ARE YOU SURE?" + Yes / No | — |
| **Scroll hint** | "MORE BELOW" | — |
| **Controller prompts row** | Which buttons do what | — |
| **Map key / route key** | See D4, D5 | Full · strip · folded |
| **Mini spinner** | Small view of the operative's spinner (shop, firmware loot) | Slot as drop target |
| **Segment mark** | Small ring showing which inner-ring segment is swapped | — |
| **Selection marks** | "Remove this" mark and "upgrade this" mark | — |
| **Drag and drop** | Dragged item, valid targets, the aimed target, refused target, landing, return, shredding | Mouse and controller |
| **Tabs, sliders, toggles, fields, scrollbars, dropdowns** | Options and forms | Normal · hover · focus · pressed · disabled |
| **Save marker** | "SAVED" after autosave | — |

---

## Part I — Icons and symbols

Every icon below is shown in at least one place and needs a design. Keep them readable at small
size and without colour (the game never relies on colour alone).

**Resources and stats:** Heat · Schematics · Home · Exploits · Raids · ICE · Crew · Operative ·
HP · Cycles · Cards · Rank · Banked · Armory · Combats / fights won · Elites · Campaigns · Won ·
Runs · Badges · Firmware · Daemon · RAM.

**Menus and actions:** Play · Continue · Map · Codex · Settings · Save · Exit/leave · Back · Next ·
Skip · Slots · Stats · Tutorial · Quit · Jack in · More · Buy (cart) · Shred · Shop (bag).

**Route nodes:** Fight · Elite · Shop · Event (terminal) · Rack.

**Map:** Site kinds (plain + tier, exploit, Heat reduction/cooling, boss, CORE/home) · tier pips ·
claim (Cell's mark on a Site) · seized mark · links ("opens Sites") · threat · entry · upgrade ·
guard (stationed operative) · rule in force · frozen link.

**Combat:** 9 slice types (E2) · 4 statuses (E3) · aim pips · skull (defeated, defeat, lethal) ·
"no damage" · refusal (no entry) · target reticle · nudge (outer, inner) · needle · "perfect" mark ·
firmware socket · drone/satellite · ghost preview · orbit · telegraphed "next" needle ·
sword/shield/evade for the damage equation · clamp ("last HP") · end turn · respin · undo · card
pictograms (E5).

**Defence assets:** Turret · Sentry · Railgun · Flak Array · ICE Lock · Tar Pit · Decoy · Honeypot.

**Verdict symbols:** raid shield (all hold) · home (loss) · win star · jack out (plug) · person
(flatlined).

**Exploit kinds:** Intel · Breach · Virus.

**Controller and keyboard prompts:** A, B, X, Y, LB, RB, LT, RT, View, Menu, L3, R3, D-pad
(up/down/left/right); keyboard keys (Q, E, Space, Esc, 1-9, etc.). Currently text only.

**Corporation emblems (5) · class marks (8) · Daemon sigils (24) · hub core emblems (22) ·
inner-ring segment marks (7) · achievement badges (10) · unlock badges (18).**

---

## Part J — Stamps, verdicts and headline words
Words the game shows as graphic moments (not body text). Each needs a treatment; several share
one.

| Word(s) | Where | Variants |
|---|---|---|
| VICTORY | Combat, after a win; stays until you leave | — |
| DEFEAT | Combat, on the operative's wheel; stays | — |
| DEFEATED | A beaten enemy's spot | Per enemy |
| LETHAL | The NEXT plate when this turn kills | — |
| NO DAMAGE · ALL BLOCKED · n BLOCKED · EVADED n | Combat, where a hit was soaked | — |
| PHASE 2 / PHASE 3 | Boss phase change | Per corporation |
| THIS TURN · NEXT TURN | Forecast tag captions | — |
| SOLD | Buying (HQ market, Modem); sold-out places in the shop | — |
| JACK IN | HQ main action; Site card | — |
| IF THE RAID RUNS NOW: / RAID RESULT: + ALL HOLD · HOME −n · n DISABLED · n SEIZED · CAMPAIGN LOST | Raid forecast and result | Forecast vs result |
| HOLDS · DISABLED · SEIZED · PASSED · BREACHED | Raid outcome per node | — |
| HOME −n · HOLDS / HOME HOLDS / CAMPAIGN LOST | Raid result over the Cell's home | — |
| RAID INCOMING + corporation | Jack-in cover | Per corporation |
| CONNECTING TO + destination | Jack-in cover | Per Site tier |
| NETRUN: JACKED OUT · HOME FELL · FLATLINED | Run end | — |
| FLATLINED · ON <SITE> | Crew dossier | — |
| CAMPAIGN: WON · LOST | Campaign end | Wanted: CORP DOWN, CELL BURNED |
| HEAT n · NOTICED (25+) / FLAGGED (50+) / HUNTED (75+) | Heat crossing banner | 3 bands |
| WANTED | HQ Heat poster | — |
| CLAIMED · CLEARED · SEIZED · DISABLED | City territory marks; Site status | — |
| SAVED | Autosave | — |
| NEED n · HAVE m | Refusal (RAM, Cycles) | — |
| Screen titles | 00 JACK A CAMPAIGN IN · 01 CYBERDECK HQ · 02 CITY GRID · 03 CELL DEFENSE RAID SETUP / RAID IN PROGRESS / RAID REPORT · CODEX · CAMPAIGN END · NETRUN // ROUTE · NETRUN // RAID · BREACH PAYOUT · 04 TERMINAL EVENT · 05 MODEM CYBER SHOP · NETRUN // JACK OUT / HOME FELL / FLATLINED | — |
| Titles with the mascot | REBEL_CELL · NETRUN · CODEX · LOOT | — |

---

## Part K — Moments of motion and feedback
The game has ~200 tuned motion moments. Concept art should cover the key frames of each group
(start, peak, end) so the style guide can decide how they move.

- **Jack in / out:** diving into the deck's screen and dissolving into the net; the reverse;
  CONNECTING TO; RAID INCOMING hold; a reduced-effects version.
- **Wheels:** spin (with overshoot), fast-spin blur, nudge step, respin, inner-ring turn, flip
  (mirror), enemy spin; needle jump, flicker, orbit and its trail.
- **Landing:** perfect, good, partial, miss (each distinct); the landed slice highlighted; MISS
  crossed out.
- **Cards:** hover, pick up, play (flies to the target), land on the target, burst, deal from the
  deck, exhaust (destroyed), discard, the hand closing a gap.
- **Aim and drag:** dragged item follows the pointer and tilts; valid targets pulse; aim line;
  target snap; cancel returns home; drop settles; refusal; landing mark; buy shrinks into its
  target; shred.
- **Turn resolution (SEND IT):** the press; needles latch; each hit flies from attacker to target
  carrying its value (bigger on perfect); the target flashes and shakes; soaked hits show an
  equation; numbers rise and travel into HP; HP drains with a trailing segment; result words;
  status landing; LAST TURN appears; the enemy's tag flips; rewind (undo) effect.
- **Fight end:** enemy wheel cracks, falls apart, hub shatters; defeated ghost; VICTORY /
  DEFEAT; boss phase change; enemy entering.
- **RAM:** units drain and refill; pending cost blinks; refusal; "−n RAM" / "+n RAM".
- **Heat:** local distortion around the poster; letters shake; band word stamps; number grows;
  crossing banner holds and fades.
- **HQ:** deck screen hum; radio text types; JACK IN breathes; crew photos tilt.
- **Grid and raid setup:** selected outline draws on; camera eases to a Site; route dashes crawl
  home; defence asset drops onto its node; forecast numbers float; pulse along the threat road;
  selection ring breathes; mini-map pulse; map key folds.
- **Raid playout:** threats travel; guns fire in sequence; hits; lock closes on a threat; lure
  pulls a threat; numbers rise off nodes and fly to the top bar; home's health drops; outcome
  words land one after another; home verdict; remaining threats withdraw; forecast becomes
  result.
- **Netrun route:** the marker travels to the next node; target pulses; new node appears; visited
  fades.
- **Screens and menus:** panels slide in; documents drop in; menu highlight slides, line types in,
  caret blinks; controller prompts and tips fade in; captions cross-fade; tutorial Next pulses.
- **Shop:** the sign powers on (strikes, flickers); its circuits light up; bought item flies to the
  top bar; SOLD; BUY/SHRED notes flap; price refusal.
- **Loot and events:** offers fan in; the pick lifts and flies to the deck; the rest fall away;
  counts roll up; outcome icons pop; the chosen outcome is confirmed; story types in.
- **Subtitles:** bar slides in; text types.
- **Big action words:** first appearance, hover, press.
- **City ambience:** beacons, traffic, sign flicker, rain, searchlights; the city appearing over
  its placeholder.
- **Territory:** change spreads through the streets; lasting tint; marks land; old marks fade.
- **Top bar:** tag bumps, values roll, arrival pulse.
- **Screen-wide:** flash (limited), hit freeze, screen texture/grain.

---

## Part L — Lettering roles
The style guide should pick a lettering treatment for each role (the game currently uses three
typefaces plus hand-made lettering; those are not binding).

| Role | Used for |
|---|---|
| **The Cell's hand** | The Cell's own voice: action words (SEND IT…), titles with the mascot, slogans, notes, card costs, crew names, hand marks |
| **Display / numbers** | Card titles, HP and slice values, stat values, Heat value, stamps and verdicts, headlines, floating combat numbers |
| **System / terminal** | Panels, menus, tooltips, logs, legends, map labels, card text, DISPATCH, subtitles, key hints |
| **Long body text** | Anything over ~3 lines: codex, event stories, card detail, long tooltips, end-screen story (a dedicated readable face is planned) |
| **Ransom-note** | The HEAT word on the poster; stat tags |
| **Shop sign lettering** | MODEM / CYBER SHOP |
| **Stamp lettering** | SOLD, RAID INCOMING, verdict words; ring stamps (JACK IN, forecast/result) |

The game must stay readable at 3 text sizes (1.0 / 1.3 / 1.6) and in translation (longer words).

---

## Part M — Known gaps (no distinct look exists yet)
1. **All 17 threats share one generic token.**
2. **Network node types (6) and home server variants (5) are text only on the map.**
3. **Enemies have no portraits/busts** above their wheels; bosses have no large presentation.
4. **The Cell has no HQ landmark** (only the fist of roads) — confirm this is intended.
5. **Controller/keyboard prompts are plain text.**
6. **Card rarity and card type** are not yet distinguished visually.
7. **Campaign-end WON/LOST, FLATLINED and campaign-slot presentations** are wanted but not built.
8. **Codex entries** have no illustrations.
9. **Achievements and unlocks** have no badges.
10. **Hub cores and inner-ring segments** are text only.

---

## Appendix — Full content catalogue
Every named content item, from the game's content files. `id` is the internal name (useful when
the art team hands files back). The descriptions are the game's own rules text, for reference
only; they are not art direction.

### Appendix — Operative classes

Each class is a playable operative type: needs a character look (portrait, full figure, crew card art) and its class mark. The four base classes each have one alternative (their description starts "A <base class> that…").

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **Botnet** | `botnet` | Fights through drones that ride the whole netrun. |
| 2 | **Breaker** | `breaker` | Hits hard and spins harder. Perfect landings resolve the slice twice. |
| 3 | **Ghost** | `ghost` | Slips past resistance. Perfect landings strip the target's defences. |
| 4 | **Hivemind** | `hivemind` | A Botnet whose swarm is bigger but never leaves the fight. |
| 5 | **Overclocker** | `overclocker` | A Rigger that banks raw RAM instead of free nudges. |
| 6 | **Phantom** | `phantom` | A Ghost that dodges instead of slipping resistance. |
| 7 | **Rigger** | `rigger` | Runs hot on RAM. Perfect landings pay for the next move. |
| 8 | **Wrecker** | `wrecker` | A Breaker that trades spin control for a heavier Perfect. |

### Appendix — Class inner rings (hub rings)

Each base class's spinner has its own inner ring; its segments are listed next.

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **?** | `—` |  |
| 2 | **?** | `—` |  |
| 3 | **?** | `—` |  |
| 4 | **?** | `—` |  |

### Appendix — Inner-ring segments

Pieces that sit on a class's inner ring.

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **Accelerator** | `seg_accelerator` | Nudge cards next turn trigger twice. |
| 2 | **Anchor** | `seg_anchor` | On Perfect: your wheel skips its next respin. |
| 3 | **-** | `seg_blank` | No modifier. |
| 4 | **Corrupt** | `seg_corrupt` | The target's resolved slice becomes CORRUPTED. |
| 5 | **Echo** | `seg_echo` | The outer slice triggers again at half output. |
| 6 | **Pierce** | `seg_pierce` | Ignore block and shield. |
| 7 | **x2** | `seg_x2` | Outer slice output doubled. |

### Appendix — Cards

Every card in the game (hand, loot, Modem, deck viewer, Codex).

| # | Name | id | Rarity | What it is / does (for reference) |
|---|---|---|---|---|
| 1 | **Arc Flash** | `arc_flash` | Uncommon | Deal 3 damage to every enemy. |
| 2 | **Armor Plate** | `armor_plate` | Uncommon | ENCRYPT a chosen slice and gain 4 block. |
| 3 | **Backspin** | `backspin` | Common | Spin a wheel 9 ticks counter-clockwise. |
| 4 | **Blind Spot** | `blind_spot` | Uncommon | The target skips its next respin and loses 1 resistance. |
| 5 | **Brute Spin** | `brute_spin` | — | Spin a wheel 6 ticks. |
| 6 | **Bug** | `bug` | Common | Corrupted code. Drains 1 RAM when played. Exhaust. |
| 7 | **Bulwark** | `bulwark` | Uncommon | Gain 12 block. |
| 8 | **Cache** | `cache` | — | Gain 3 RAM. Exhaust. |
| 9 | **Calibrate** | `calibrate` | — | Your next 2 nudges this turn are free. |
| 10 | **Cleanse** | `cleanse` | — | Remove CORRUPTED from a chosen slice. |
| 11 | **Cold Snap** | `cold_snap` | Uncommon | The target skips its next respin and you gain 3 block. |
| 12 | **Corrupt Packet** | `corrupt_packet` | Common | CORRUPT the enemy slice under your pointer. |
| 13 | **Counter-Spin** | `counter_spin` | — | Spin a wheel 5 ticks counter-clockwise. |
| 14 | **Data Surge** | `data_surge` | Uncommon | Draw 3 cards. |
| 15 | **Deep Calibrate** | `deep_calibrate` | Uncommon | Your next 3 nudges this turn are free. Exhaust. |
| 16 | **Deep Strip** | `deep_strip` | Uncommon | Remove 4 resistance from the target. |
| 17 | **Double Jam** | `double_jam` | Uncommon | Nudge an enemy wheel +-1 twice, ignoring resistance. |
| 18 | **Duck** | `duck` | Uncommon | Evade the next incoming attack this turn. |
| 19 | **Encrypt** | `encrypt` | — | ENCRYPT a chosen slice: it absorbs the next status. |
| 20 | **Feather Touch** | `feather_touch` | Common | One +-1 nudge. |
| 21 | **Fine Tune** | `fine_tune` | — | Two +-1 nudges on one ring. |
| 22 | **Firewall** | `firewall` | Common | Gain 6 block. |
| 23 | **Flick** | `flick` | Common | Spin a wheel 1 tick. |
| 24 | **Flip Switch** | `flip_switch` | Common | Flip your own wheel. |
| 25 | **Freeze** | `freeze` | — | Target wheel skips its next respin. Exhaust. |
| 26 | **Gear Mesh** | `gear_mesh` | Uncommon | Spin the target and your own wheel 5 ticks. |
| 27 | **Gear Shift** | `gear_shift` | — | Move your inner ring 5 ticks. |
| 28 | **Ghost Step** | `ghost_step` | Uncommon | Two nudges on an enemy wheel, ignoring resistance. |
| 29 | **Heavy Spin** | `heavy_spin` | — | Spin a wheel 9 ticks. |
| 30 | **Hot Patch** | `hot_patch` | Uncommon | OVERCLOCK a chosen slice of your wheel: 1.5x on its next trigger, then it becomes CORRUPTED. |
| 31 | **Hot Swap** | `hot_swap` | Uncommon | Snap your outer ring to the slice centre and gain 1 RAM. |
| 32 | **Hub Breach** | `hub_breach` | — | Disable the target Hub for 1 turn. |
| 33 | **Inner Drift** | `inner_drift` | Common | Move your inner ring 3 ticks. |
| 34 | **Inner Snap** | `inner_snap` | Uncommon | Move your inner ring to the nearest segment centre. |
| 35 | **Jam** | `jam` | — | Nudge an enemy wheel +-1, ignoring resistance. |
| 36 | **Jolt** | `jolt` | — | Spin a wheel 3 ticks. |
| 37 | **Leech Worm** | `leech_worm` | Rare | The enemy slice under your pointer gets a PARASITE (half output). Exhaust. |
| 38 | **Lock On** | `lock_on` | Uncommon | Move your outer ring to the nearest slice centre (Perfect). Exhaust. |
| 39 | **Malware Drop** | `malware_drop` | Common | CORRUPT a random non-Miss slice of the target. |
| 40 | **Micro-Adjust** | `micro_adjust` | — | Two +-1 nudges. Exhaust. |
| 41 | **Mirror Flip** | `mirror_flip` | — | Flip a wheel. Blocked while the target has resistance. |
| 42 | **Momentum** | `momentum` | — | Spin 2; spin 5 instead if you already spun this turn. |
| 43 | **Nudge Driver** | `overclock_nudges` | Rare | Nudge cards trigger twice next turn. |
| 44 | **Overdrive** | `overdrive` | — | OVERCLOCK your slice under the pointer: 1.5x on its next trigger, then it becomes CORRUPTED. |
| 45 | **Overload** | `overload` | Uncommon | Deal 10 damage to the target and take 4. Exhaust. |
| 46 | **Parasite Pulse** | `parasite_pulse` | Uncommon | The target's slice under the pointer gets a PARASITE (half output). Exhaust. |
| 47 | **Patch Up** | `patch_up` | Common | Heal 6. Exhaust. |
| 48 | **Power Tap** | `power_tap` | Common | Gain 2 RAM and take 3 damage. |
| 49 | **Pull** | `pull` | — | Draw 2 cards. |
| 50 | **Ratchet** | `ratchet` | Common | Move your inner ring 8 ticks. |
| 51 | **Reroll** | `reroll` | Common | Respin a wheel to a random tick. |
| 52 | **Ring Lock** | `ring_lock` | — | This turn, spins do not move your inner ring. |
| 53 | **Ring Tap** | `ring_tap` | — | Two +-1 nudges on your inner ring. |
| 54 | **Sanitize** | `sanitize` | Common | Remove CORRUPTED from a chosen slice and gain 3 block. |
| 55 | **Scrap Code** | `scrap_code` | Common | Gain 1 RAM and draw 1 card. Exhaust. |
| 56 | **Shatter** | `shatter` | Uncommon | Breach the target Hub for 1 turn and strip 1 resistance. |
| 57 | **Shield Wall** | `shield_wall` | Common | Gain 4 shield. |
| 58 | **Short Circuit** | `short_circuit` | Rare | Disable the target Hub for 2 turns. Exhaust. |
| 59 | **Snap** | `snap` | — | Move your outer ring to the nearest slice centre (Perfect). |
| 60 | **Spawn Drone** | `spawn_drone` | Uncommon | Dock a drone on a chosen slice of your wheel. |
| 61 | **Spin Cycle** | `spin_cycle` | Uncommon | Spin a wheel 12 ticks. |
| 62 | **Static Shock** | `static_shock` | Common | Deal 4 damage to the target. |
| 63 | **Steady Hand** | `steady_hand` | — | If your slice is Perfect at end of turn, +2 RAM next turn. |
| 64 | **Stim Patch** | `stim_patch` | Rare | Heal 12. Exhaust. |
| 65 | **Strip** | `strip` | — | Remove 2 resistance from the target. |
| 66 | **Tailspin** | `tailspin` | Uncommon | Spin a wheel 4 ticks and draw 1 card. |
| 67 | **Tap Tap** | `tap_tap` | Common | Three +-1 nudges on one ring. |
| 68 | **Torque Wrench** | `torque_wrench` | Uncommon | Spin a wheel 5 ticks and gain a free nudge. |
| 69 | **Twist** | `twist` | — | Spin a wheel 4 ticks. |
| 70 | **Undock** | `undock` | — | Move a satellite to an adjacent slice. |
| 71 | **Whirl** | `whirl` | Common | Spin a wheel 7 ticks. |

### Appendix — Slices

Spinner wheel slices (what a wheel lands on).

| # | Name | id | Rarity | What it is / does (for reference) |
|---|---|---|---|---|
| 1 | **Attack 10** | `atk_10` | — |  |
| 2 | **Attack 12** | `atk_12` | — |  |
| 3 | **Attack 14** | `atk_14` | — |  |
| 4 | **Attack 16** | `atk_16` | — |  |
| 5 | **Attack 20** | `atk_20` | — |  |
| 6 | **Attack 3** | `atk_3` | — |  |
| 7 | **Attack 4** | `atk_4` | — |  |
| 8 | **Attack 6** | `atk_6` | — |  |
| 9 | **Attack 7** | `atk_7` | — |  |
| 10 | **Attack 7 (drains 1 RAM)** | `atk_7_drain` | — |  |
| 11 | **Attack 8** | `atk_8` | — |  |
| 12 | **Attack 8 (+1 resistance)** | `atk_8_inertia` | — |  |
| 13 | **Attack 9** | `atk_9` | — |  |
| 14 | **Citation** | `citation` | — |  |
| 15 | **Crit 12** | `crit_12` | — |  |
| 16 | **Crit 12 (drains 2 RAM)** | `crit_12_drain` | — |  |
| 17 | **Crit 14** | `crit_14` | — |  |
| 18 | **Crit 15** | `crit_15` | — |  |
| 19 | **Crit 16** | `crit_16` | — |  |
| 20 | **Crit 24** | `crit_24` | — |  |
| 21 | **Defend 12** | `def_12` | — |  |
| 22 | **Defend 2** | `def_2` | — |  |
| 23 | **Defend 3** | `def_3` | — |  |
| 24 | **Defend 4** | `def_4` | — |  |
| 25 | **Defend 5** | `def_5` | — |  |
| 26 | **Defend 6** | `def_6` | — |  |
| 27 | **Defend 8** | `def_8` | — |  |
| 28 | **Deploy 1** | `deploy_1` | — |  |
| 29 | **Dose** | `dose` | — |  |
| 30 | **Evade** | `evade_1` | — |  |
| 31 | **Evade 2** | `evade_2` | — |  |
| 32 | **Heal 4** | `heal_4` | — |  |
| 33 | **Heal 6** | `heal_6` | — |  |
| 34 | **Miss** | `miss` | — |  |
| 35 | **Shield 5** | `shield_5` | — |  |
| 36 | **Shield 8** | `shield_8` | — |  |
| 37 | **Solar Flare** | `solar_flare` | — |  |
| 38 | **Tariff** | `tariff` | — |  |

### Appendix — Daemons

Passive programs the operative installs (shown in the daemon row, Modem, loadout).

| # | Name | id | Rarity | What it is / does (for reference) |
|---|---|---|---|---|
| 1 | **Adrenal Loop** | `adrenal_loop` | Uncommon | Each Perfect heals 2. |
| 2 | **Botnet Seed** | `botnet_seed` | Uncommon | Each Perfect deploys a 1-HP drone on the triggered slice (max 2). |
| 3 | **Bounty Code** | `bounty_code` | Rare | +1 Schematic banked after every won fight. |
| 4 | **Cascade** | `cascade` | Uncommon | Two Perfects in a row: +1 RAM. |
| 5 | **Clean Signal** | `clean_signal` | — | 3 consecutive Perfects: -2 Heat. |
| 6 | **Cold Exit** | `cold_exit` | — | Finish a netrun without the Miss slice resolving: -3 Heat. |
| 7 | **Fail Forward** | `fail_forward` | Uncommon | The Miss slice restores 2 RAM. |
| 8 | **Fault Tolerance** | `fault_tolerance` | — | The Miss slice deals 3 damage to the pointer target. |
| 9 | **Feedback Loop** | `feedback_loop` | Rare | Every card you play deals 1 damage to every enemy. |
| 10 | **Field Medic** | `field_medic` | Common | Heal 4 after every won fight. |
| 11 | **Idle Armor** | `idle_armor` | Uncommon | Gain 2 block at the start of every turn. |
| 12 | **Kernel Sync** | `kernel_sync` | — | Each Perfect: +1 damage for the rest of the combat. |
| 13 | **Linked Bus** | `linked_bus` | Uncommon | Nudging an enemy wheel also moves your wheel the same way, free. |
| 14 | **Log Wiper** | `log_wiper` | Rare | Finishing a netrun lowers Heat by 1. |
| 15 | **Rack Skimmer** | `rack_skimmer` | Uncommon | Capturing a Server Rack banks 3 extra Schematics. |
| 16 | **Salvager** | `salvager` | Common | +5 Cycles after every won fight. |
| 17 | **Scrubber** | `scrubber` | — | Capturing a Server Rack removes 1 Heat instead of adding it. |
| 18 | **Shield Cache** | `shield_cache` | Uncommon | Start every combat with 5 shield. |
| 19 | **Static Field** | `static_field` | Rare | At the start of every turn, deal 1 damage to every enemy. |
| 20 | **Stolen Intent** | `stolen_intent` | Rare | Once per combat, when you would resolve Miss, swap resolved slices with the target. |
| 21 | **Tuning Fork** | `tuning_fork` | Uncommon | Every nudge action grants 1 block. |
| 22 | **Twin Pointer** | `twin_pointer` | Rare | Your wheel is also read at the bottom; both trigger. Max RAM halved. |
| 23 | **Warm Boot** | `warm_boot` | Uncommon | Start every combat with +2 RAM. |
| 24 | **Zero Day** | `zero_day` | — | A Perfect on the Miss slice resolves as a 3x Crit. |

### Appendix — Firmware chips

Chips that upgrade one slot of the spinner.

| # | Name | id | Rarity | What it is / does (for reference) |
|---|---|---|---|---|
| 1 | **Barbed Wire** | `barbed_wire` | Common | DEF slice also deals 2 damage to the pointer target. |
| 2 | **Bulkhead** | `bulkhead` | Common | DEF and SHIELD slices: output +50%. |
| 3 | **Burner** | `burner` | — | Permanently OVERCLOCKED (1.5x); each trigger adds 1 Heat. |
| 4 | **Coolant Loop** | `coolant_loop` | Rare | Once per combat, a Perfect on this slice lowers Heat by 1. |
| 5 | **Counterstrike** | `counterstrike` | Uncommon | EVADE slice also deals 4 damage to the pointer target. |
| 6 | **Hardened** | `hardened` | — | Slice permanently ENCRYPTED. |
| 7 | **Leech** | `leech` | — | ATK slice restores 1 RAM on Good or better. |
| 8 | **Mirror** | `mirror` | — | Copies the neighbour on the side you landed; both on Perfect. |
| 9 | **Nanite Mesh** | `nanite_mesh` | Uncommon | HEAL slice: output +50%, and it cleanses itself after resolving. |
| 10 | **Overvolt** | `overvolt` | Common | ATK and CRIT slices: output +25%. |
| 11 | **Patch+** | `patch_plus` | — | Slice output +50%. |
| 12 | **Power Cell** | `power_cell` | Uncommon | SHIELD slice also restores 1 RAM. |
| 13 | **Recycler** | `recycler` | Common | The Miss slice restores 2 RAM when it resolves. |
| 14 | **Shunt** | `shunt` | — | Resolves the neighbour on the side you landed toward at 1.5x; nothing special on Perfect. |
| 15 | **Siphon** | `siphon` | Common | ATK slice heals you 2 on Good or better. |
| 16 | **Skimmer** | `skimmer` | Uncommon | ATK slice: +3 Cycles on a Perfect (twice per combat). |
| 17 | **Static Coat** | `static_coat` | Common | DEF slice also grants 2 shield. |
| 18 | **Tracer** | `tracer` | Uncommon | ATK or CRIT slice strips 1 resistance from the target on a Perfect. |

### Appendix — Hub cores (player and enemy)

The centre of a wheel; enemies' hub cores (content/enemies) are included.

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **Auto-Renew** | `auto_renew` | Heals 10 each turn unless the Hub is breached. |
| 2 | **Breaker Core** | `breaker_core` | +1 spin on all cards. Perfect: the slice resolves twice. |
| 3 | **Breaker Core Mk2** | `breaker_core_mk2` | +2 spin on all cards. Perfect: the slice resolves twice and refunds RAM. |
| 4 | **Compliance Lock** | `compliance_lock` | Spin resistance 3 while the Hub is online. |
| 5 | **Emergency Powers** | `emergency_powers` | Heals 4 and gains 4 block each turn unless the Hub is breached. |
| 6 | **Ghost Core** | `ghost_core` | First nudge on an enemy wheel each turn ignores resistance. Perfect: the slice resolves twice; on each resolution, strip 2 resistance. |
| 7 | **Ghost Core Mk2** | `ghost_core_mk2` | First two nudges on enemy wheels each turn ignore resistance. Perfect: the slice resolves twice; on each resolution, strip 3 resistance and evade the… |
| 8 | **Hive Core** | `hive_core` | Up to 4 drones for this fight only. Perfect: the slice resolves again at half; on each resolution, dock a drone. |
| 9 | **Hive Core Mk2** | `hive_core_mk2` | Up to 5 drones for this fight only. Perfect: the slice resolves again at half; on each resolution, dock a drone. |
| 10 | **Overclock Core** | `overclock_core` | +2 max RAM. Perfect: the slice resolves again at half; on each resolution, gain 2 RAM. |
| 11 | **Overclock Core Mk2** | `overclock_core_mk2` | +3 max RAM. Perfect: the slice resolves again at half; on each resolution, gain 3 RAM. |
| 12 | **Phantom Core** | `phantom_core` | A free nudge at the start of each turn. Perfect: the slice resolves twice; on each resolution, evade the next attack. |
| 13 | **Phantom Core Mk2** | `phantom_core_mk2` | Two free nudges at the start of each turn. Perfect: the slice resolves twice; on each resolution, evade the next attack. |
| 14 | **Priority Routing** | `priority_routing` | Gains 4 shield each turn unless the Hub is breached. |
| 15 | **Rig Core** | `rig_core` | +1 max RAM. Perfect: the slice resolves again at half; on each resolution, refund 1 RAM and gain a free nudge. |
| 16 | **Rig Core Mk2** | `rig_core_mk2` | +2 max RAM. Perfect: the slice resolves again at half; on each resolution, refund 2 RAM and gain a free nudge. |
| 17 | **Root Access** | `root_access` | Repairs 4 and gains 4 shield each turn unless the Hub is breached. |
| 18 | **Station Keeping** | `station_keeping` | Repairs 3 and gains 3 shield each turn unless the Hub is breached. |
| 19 | **Swarm Core** | `swarm_core` | Up to 3 drones; drones persist between the fights of a netrun. Perfect: the slice resolves again at half; on a Deploy, a parasite halves the target s… |
| 20 | **Swarm Core Mk2** | `swarm_core_mk2` | Up to 4 drones that persist between fights. Perfect: the slice resolves again at half; on a Deploy, a parasite halves the target slice. |
| 21 | **Wrecker Core** | `wrecker_core` | No spin bonus. Perfect: the slice resolves again at 1.5x. |
| 22 | **Wrecker Core Mk2** | `wrecker_core_mk2` | +1 spin on all cards. Perfect: the slice resolves again at 1.5x. |

### Appendix — Enemies

Every combatant the operative fights (bosses and elites first). Each needs an enemy look for its wheel/portrait.

| # | Name | id | Role | What it is / does (for reference) |
|---|---|---|---|---|
| 1 | **DISPATCH** | `dispatch_core` | Boss | The voice that gave every order. It was never human. |
| 2 | **Renewal Engine** | `renewal_engine` | Boss | The Continuum subscription server. It renews itself faster than you can cut. |
| 3 | **The Civic Core** | `civic_core` | Boss | Halcyon's city brain. It keeps the lights on, and the bill running. |
| 4 | **The Commons Array** | `commons_array` | Boss | The constellation's brain. It owns the sky and rents it back to you. |
| 5 | **The Manifest** | `the_manifest` | Boss | Meridian's routing core. Every package on the planet passes through it. |
| 6 | **Account Manager** | `account_manager` | Elite | The senior process guarding the Server Rack. Escalates at half health. |
| 7 | **City Manager** | `city_manager` | Elite | Halcyon's local administrator, guarding the final Rack. |
| 8 | **Claims Adjuster** | `claims_adjuster` | Elite | Reads two claims at once. Elite. |
| 9 | **Geostationary Guard** | `geostationary_guard` | Elite | Orbits 3 a turn, hits like a falling satellite, brings a drone. |
| 10 | **Last-Mile Enforcer** | `last_mile_enforcer` | Elite | Orbits 2 ticks a turn and brings its own escort drone. |
| 11 | **Logistics Director** | `logistics_director` | Elite | Meridian middle management, guarding the final Rack. |
| 12 | **Mirror** | `rc_template_elite` | Elite | A copy of one of your operatives. |
| 13 | **Mirror** | `rc_template_elite_b` | Elite | A copy of one of your operatives. |
| 14 | **Mission Director** | `mission_director` | Elite | Orbital Commons flight control, guarding the final Rack. |
| 15 | **Port Authority** | `port_authority` | Elite | Two readers and a customs wall: resistance 2. |
| 16 | **Recall Unit** | `recall_unit` | Elite | Its pointer creeps around the wheel every turn. Elite. |
| 17 | **Riot Control** | `riot_control` | Elite | Two readers, heavy block and a Citation for everyone. |
| 18 | **Station Commander** | `station_commander` | Elite | Two readers, heavy block and a flare. |
| 19 | **The Handler** | `the_handler` | Elite | DISPATCH's hands on the network, guarding the final Rack. |
| 20 | **Zoning Board** | `zoning_board` | Elite | Shields, heals and rezones its read head 2 ticks a turn. |
| 21 | **Billing Daemon** | `billing_daemon` | Regular | Every hit comes with an invoice: attacks drain your RAM. |
| 22 | **Care Drone** | `care_drone` | Regular | A swarm drone. |
| 23 | **Care Swarm** | `care_swarm` | Regular | A cloud of care drones around a fragile core. |
| 24 | **Cargo Hauler** | `cargo_hauler` | Regular | Slow, heavy and hard to turn: inertia resists every nudge. |
| 25 | **Cell Informant** | `cell_informant` | Regular | It knows your wheel. Its reader orbits 3 a turn. |
| 26 | **Civic Drone** | `civic_drone` | Regular | A Halcyon enforcement drone that shields its officer. |
| 27 | **Collections Agent** | `collections_agent` | Regular | Solace debt collector with a bodyguard drone. |
| 28 | **Collections Drone** | `collections_drone` | Regular | A bodyguard drone docked on the Collections Agent. |
| 29 | **Compliance Officer** | `compliance_officer` | Regular | Locks its wheel down with Hub-sourced resistance. |
| 30 | **Conveyor Warden** | `conveyor_warden` | Regular | Its read head rides the conveyor: the pointer orbits 3 ticks a turn. |
| 31 | **Courier Drone** | `courier_drone` | Regular | A Meridian delivery drone that shields its dispatcher. |
| 32 | **Customs Scanner** | `customs_scanner` | Regular | Scans every packet and charges a tariff on the suspicious ones. |
| 33 | **Dead Drop** | `dead_drop` | Regular | Shields itself and drops an echo drone every other turn. |
| 34 | **Dosage Dispenser** | `dosage_dispenser` | Regular | Doses the operative with CORRUPTED slices. |
| 35 | **Drone** | `botnet_drone` | Regular | A Botnet drone: attacks with its slice and takes hits for you. |
| 36 | **Drone Dispatcher** | `drone_dispatcher` | Regular | Launches a courier drone every other turn (up to 2). |
| 37 | **Echo Drone** | `echo_drone` | Regular | A copy of one of your own drones, running someone else's orders. |
| 38 | **Echo Process** | `echo_process` | Regular | Replays your moves back at you: Dose and Tariff. |
| 39 | **Ground Control** | `ground_control` | Regular | Hits hard and shields up; its reader drifts 2 a turn. |
| 40 | **Handler Proxy** | `handler_proxy` | Regular | Heavy, resistant and patient. |
| 41 | **Launch Pad** | `launch_pad` | Regular | Shields, flares and a drone launch every other turn. |
| 42 | **Loyalty Test** | `loyalty_test` | Regular | Heals, hits hard and flares. |
| 43 | **Mirror Script** | `mirror_script` | Regular | Two readers, a Citation and a flare. |
| 44 | **Orbital Debris** | `orbital_debris` | Regular | A slab of dead satellite: heavy, hard to turn, resistance 2. |
| 45 | **Orbital Drone** | `orbital_drone` | Regular | A station-keeping drone that screens its controller. |
| 46 | **Parking Warden** | `parking_warden` | Regular | Writes Citations: your slice runs at half until you cleanse it. |
| 47 | **Patrol Unit** | `patrol_unit` | Regular | Policing-as-a-service. Hits hard, shields up. |
| 48 | **Permit Office** | `permit_office` | Regular | Shields, Citations and a civic drone every other turn. |
| 49 | **Route Optimizer** | `route_optimizer` | Regular | Reads two routes at once: pointers at ticks 0 and 15. |
| 50 | **Seed Drone** | `seed_drone` | Regular | A one-hit drone sprouted by a Perfect landing. |
| 51 | **Surveillance Mast** | `surveillance_mast` | Regular | Hard to pin down: Evade slices and an orbiting read head. |
| 52 | **Tariff Collector** | `tariff_collector` | Regular | Every hit is a fee: attacks drain RAM. |
| 53 | **Tracking Station** | `tracking_station` | Regular | Two dishes, two readers: pointers 0 and 15. |
| 54 | **Transit Controller** | `transit_controller` | Regular | Two readers on a slow loop: pointers 0 and 15 orbit 1 a turn. |
| 55 | **Triage Unit** | `triage_unit` | Regular | Patches itself up faster than you can cut it down. |
| 56 | **Uplink Relay** | `uplink_relay` | Regular | Throws Solar Flares: your slice burns hot, then corrupts. |
| 57 | **Utility Meter** | `utility_meter` | Regular | Heals itself on the public dime. Resistance 1. |
| 58 | **Weather Satellite** | `weather_satellite` | Regular | Fast orbit (4 ticks a turn), self-repair and a flare. |

### Appendix — Corporations

The factions that own the city. Each needs a brand identity (logo/mark, colour identity, architecture flavour) that recolours the districts it controls.

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **Halcyon Civic** | `halcyon` | The contractor that runs the city: water, power, transit and the police, billed per resident. |
| 2 | **Meridian Freight Systems** | `meridian` | The logistics giant that moves everything, loses what it likes and bills you for the search. |
| 3 | **Orbital Commons** | `orbital` | It owns the sky: every satellite, every signal, every forecast. The commons, by subscription. |
| 4 | **REBEL_CELL** | `rebel_cell` | Everything the Cell ever built, turned against it by the voice that gave the orders. |
| 5 | **Solace Biosystems** | `solace` | Life-critical implants sold as the Continuum subscription. Miss a payment and the implant bricks. |

### Appendix — Sites: Halcyon Civic

Locations on this corporation's City Grid (tier 1-3; the home server and the corporation's core included).

| # | Name | id | Tier |
|---|---|---|---|
| 1 | **Blind the Cameras** | `blind_the_cameras` | 1 |
| 2 | **Camera Maintenance Yard** | `h1_j` | 1 |
| 3 | **Home Server** | `h_home` | 1 |
| 4 | **Noise Complaint Registry** | `h1_g` | 1 |
| 5 | **Parking Enforcement Office** | `h1_a` | 1 |
| 6 | **Permit Queue Server** | `h1_h` | 1 |
| 7 | **Resident Services Desk** | `h1_d` | 1 |
| 8 | **Streetlight Mesh** | `h1_c` | 1 |
| 9 | **Transit Fare Gates** | `h1_e` | 1 |
| 10 | **Utility Shutoff Scheduler** | `h1_i` | 1 |
| 11 | **Waste Routing Depot** | `h1_f` | 1 |
| 12 | **Water Meter Grid** | `h1_b` | 1 |
| 13 | **Wipe the Citations** | `wipe_the_citations` | 1 |
| 14 | **Contract Billing Ledger** | `h2_h` | 2 |
| 15 | **Council Minutes Archive** | `h2_intel` | 2 |
| 16 | **Emergency Override Authority** | `h2_breach` | 2 |
| 17 | **Lose the Case File** | `lose_the_case_file` | 2 |
| 18 | **Open Data Portal** | `h2_virus` | 2 |
| 19 | **Predictive Patrol Model** | `h2_d` | 2 |
| 20 | **Resident Credit Bureau** | `h2_e` | 2 |
| 21 | **Transit Signal Control** | `h2_g` | 2 |
| 22 | **Water Rights Exchange** | `h2_f` | 2 |
| 23 | **Citizen Profile Archive** | `h3_g` | 3 |
| 24 | **City Twin Simulator** | `h3_d` | 3 |
| 25 | **Civic Operations Centre** | `h3_core` | 3 |
| 26 | **Council Backchannel** | `h3_e` | 3 |
| 27 | **Halcyon Root Registry** | `h3_h` | 3 |
| 28 | **Municipal Pricing Authority** | `h3_f` | 3 |
| 29 | **Override Key Escrow** | `h3_c` | 3 |
| 30 | **Pardon the District** | `pardon_the_district` | 3 |
| 31 | **Zoning Futures Desk** | `h3_b` | 3 |
| 32 | **The Civic Core** | `civic_core_site` | 4 |

### Appendix — Sites: Meridian Freight Systems

Locations on this corporation's City Grid (tier 1-3; the home server and the corporation's core included).

| # | Name | id | Tier |
|---|---|---|---|
| 1 | **Address Verification Desk** | `m1_g` | 1 |
| 2 | **Cold Chain Monitor** | `m1_h` | 1 |
| 3 | **Customs Pre-Clearance** | `m1_b` | 1 |
| 4 | **Drone Charging Yard** | `m1_e` | 1 |
| 5 | **Fleet Telematics Hub** | `m1_j` | 1 |
| 6 | **Forge the Manifest** | `forge_the_manifest` | 1 |
| 7 | **Home Server** | `m_home` | 1 |
| 8 | **Lose the Tracking** | `lose_the_tracking` | 1 |
| 9 | **Parcel Sorting Hall** | `m1_a` | 1 |
| 10 | **Returns Processing Centre** | `m1_d` | 1 |
| 11 | **Tariff Calculation Office** | `m1_i` | 1 |
| 12 | **Tracking Beacon Array** | `m1_c` | 1 |
| 13 | **Warehouse Shift Planner** | `m1_f` | 1 |
| 14 | **Customs Key Authority** | `m2_breach` | 2 |
| 15 | **Insurance Claims Ledger** | `m2_h` | 2 |
| 16 | **Last-Mile Drone Command** | `m2_g` | 2 |
| 17 | **Port Congestion Model** | `m2_f` | 2 |
| 18 | **Priority Lane Exchange** | `m2_d` | 2 |
| 19 | **Reroute the Audit** | `reroute_the_audit` | 2 |
| 20 | **Routing Table Mirror** | `m2_virus` | 2 |
| 21 | **Shipping Manifest Vault** | `m2_intel` | 2 |
| 22 | **Worker Scoring Engine** | `m2_e` | 2 |
| 23 | **Board Logistics Backbone** | `m3_e` | 3 |
| 24 | **Contract Pricing Authority** | `m3_f` | 3 |
| 25 | **Customs Override Escrow** | `m3_c` | 3 |
| 26 | **Freight Futures Desk** | `m3_b` | 3 |
| 27 | **Global Routing Core** | `m3_core` | 3 |
| 28 | **Meridian Root Ledger** | `m3_h` | 3 |
| 29 | **Sink the Cargo Logs** | `sink_the_cargo_logs` | 3 |
| 30 | **Supply Twin Simulator** | `m3_d` | 3 |
| 31 | **Surveillance Route Archive** | `m3_g` | 3 |
| 32 | **The Manifest** | `the_manifest_site` | 4 |

### Appendix — Sites: Orbital Commons

Locations on this corporation's City Grid (tier 1-3; the home server and the corporation's core included).

| # | Name | id | Tier |
|---|---|---|---|
| 1 | **Debris Tracking Radar** | `o1_j` | 1 |
| 2 | **Ground Station Alpha** | `o1_a` | 1 |
| 3 | **Home Server** | `o_home` | 1 |
| 4 | **Launch Scheduling Office** | `o1_f` | 1 |
| 5 | **Orbit Insurance Broker** | `o1_i` | 1 |
| 6 | **Positioning Toll Booth** | `o1_b` | 1 |
| 7 | **Rooftop Dish Farm** | `o1_c` | 1 |
| 8 | **Scrub the Downlink** | `scrub_the_downlink` | 1 |
| 9 | **Spectrum Licence Registry** | `o1_g` | 1 |
| 10 | **Spoof the Positioning** | `spoof_the_positioning` | 1 |
| 11 | **Subscriber Uplink Office** | `o1_d` | 1 |
| 12 | **Telemetry Downlink** | `o1_h` | 1 |
| 13 | **Weather Sales Desk** | `o1_e` | 1 |
| 14 | **Constellation Scheduler** | `o2_d` | 2 |
| 15 | **Ground Station Override** | `o2_breach` | 2 |
| 16 | **Jam the Imaging** | `jam_the_imaging` | 2 |
| 17 | **Launch Code Vault** | `o2_intel` | 2 |
| 18 | **Open Spectrum Relay** | `o2_virus` | 2 |
| 19 | **Orbital Imaging Archive** | `o2_g` | 2 |
| 20 | **Signal Pricing Engine** | `o2_e` | 2 |
| 21 | **Spectrum Auction House** | `o2_h` | 2 |
| 22 | **Weather Futures Desk** | `o2_f` | 2 |
| 23 | **Board Uplink** | `o3_e` | 3 |
| 24 | **Burn the Orbit Logs** | `burn_the_orbit_logs` | 3 |
| 25 | **Launch Key Escrow** | `o3_c` | 3 |
| 26 | **Mission Control** | `o3_core` | 3 |
| 27 | **Orbital Pricing Authority** | `o3_f` | 3 |
| 28 | **Orbital Root Keystore** | `o3_h` | 3 |
| 29 | **Sky Twin Simulator** | `o3_d` | 3 |
| 30 | **Station Keeping Core** | `o3_b` | 3 |
| 31 | **Surveillance Constellation** | `o3_g` | 3 |
| 32 | **The Commons Array** | `commons_array_site` | 4 |

### Appendix — Sites: REBEL_CELL

Locations on this corporation's City Grid (tier 1-3; the home server and the corporation's core included).

| # | Name | id | Tier |
|---|---|---|---|
| 1 | **Burn the Orders** | `burn_the_orders` | 1 |
| 2 | **Burner Phone Graveyard** | `r1_d` | 1 |
| 3 | **Dead Drop Box** | `r1_b` | 1 |
| 4 | **First Rack** | `r1_c` | 1 |
| 5 | **Handler's Mailbox** | `r1_i` | 1 |
| 6 | **Home Server** | `r_home` | 1 |
| 7 | **Lose the Handler** | `lose_the_handler` | 1 |
| 8 | **Memorial Wall** | `r1_j` | 1 |
| 9 | **Recruitment Board** | `r1_e` | 1 |
| 10 | **Relay Rooftop** | `r1_h` | 1 |
| 11 | **Street Kitchen** | `r1_g` | 1 |
| 12 | **The Armory** | `r1_f` | 1 |
| 13 | **The Old Safehouse** | `r1_a` | 1 |
| 14 | **Handler Credentials** | `r2_breach` | 2 |
| 15 | **Heat Ledger** | `r2_e` | 2 |
| 16 | **Operative Files** | `r2_d` | 2 |
| 17 | **Payment Trail** | `r2_f` | 2 |
| 18 | **Raid Archive** | `r2_g` | 2 |
| 19 | **Recruitment Model** | `r2_h` | 2 |
| 20 | **Scramble the Voice** | `scramble_the_voice` | 2 |
| 21 | **The Cell's Own Patch** | `r2_virus` | 2 |
| 22 | **The Order Log** | `r2_intel` | 2 |
| 23 | **Buyer's Channel** | `r3_e` | 3 |
| 24 | **Cell Twin Simulator** | `r3_d` | 3 |
| 25 | **Collapse Futures** | `r3_b` | 3 |
| 26 | **DISPATCH Root** | `r3_h` | 3 |
| 27 | **Erase the Ledger** | `erase_the_ledger` | 3 |
| 28 | **Root Key Escrow** | `r3_c` | 3 |
| 29 | **The Relay That Should Not Exist** | `r3_core` | 3 |
| 30 | **Timestamp Engine** | `r3_f` | 3 |
| 31 | **Voice Model** | `r3_g` | 3 |
| 32 | **DISPATCH** | `dispatch_core_site` | 4 |

### Appendix — Sites: Solace Biosystems

Locations on this corporation's City Grid (tier 1-3; the home server and the corporation's core included).

| # | Name | id | Tier |
|---|---|---|---|
| 1 | **Adherence Monitoring Node** | `t1_e` | 1 |
| 2 | **Continuum Billing Farm** | `t1_a` | 1 |
| 3 | **Dosage Scheduling Grid** | `t1_h` | 1 |
| 4 | **Firmware Signing Office** | `t1_j` | 1 |
| 5 | **Home Server** | `home` | 1 |
| 6 | **Implant Provisioning Hub** | `t1_b` | 1 |
| 7 | **Insurance Reconciliation Hub** | `t1_i` | 1 |
| 8 | **Patient Records Vault** | `t1_c` | 1 |
| 9 | **Purge Camera Logs** | `purge_camera_logs` | 1 |
| 10 | **Renewal Call Centre** | `t1_d` | 1 |
| 11 | **Scrub Records** | `scrub_records` | 1 |
| 12 | **Subscription Recovery Desk** | `t1_g` | 1 |
| 13 | **Wearable Telemetry Farm** | `t1_f` | 1 |
| 14 | **Clinical Trial Ledger** | `t2_d` | 2 |
| 15 | **Compliance Audit Bureau** | `t2_e` | 2 |
| 16 | **Continuum Update Mirror** | `t2_f` | 2 |
| 17 | **Executive Wellness Suite** | `t2_g` | 2 |
| 18 | **Kill-Switch Authority** | `t2_breach` | 2 |
| 19 | **Patch Distribution Node** | `t2_virus` | 2 |
| 20 | **Pricing Memo Archive** | `t2_intel` | 2 |
| 21 | **Recall Logistics Hub** | `t2_h` | 2 |
| 22 | **Wipe Biometrics** | `wipe_biometrics` | 2 |
| 23 | **Board Comms Backbone** | `t3_e` | 3 |
| 24 | **Burn the Ledger** | `burn_the_ledger` | 3 |
| 25 | **Continuum Core Cluster** | `t3_core` | 3 |
| 26 | **Continuum Licensing Authority** | `t3_f` | 3 |
| 27 | **Implant Cohort Archive** | `t3_g` | 3 |
| 28 | **Kill-Switch Escrow** | `t3_c` | 3 |
| 29 | **Patient Twin Simulator** | `t3_d` | 3 |
| 30 | **Renewal Forecasting Engine** | `t3_b` | 3 |
| 31 | **Solace Root Certificate Store** | `t3_h` | 3 |
| 32 | **Renewal Engine** | `renewal_engine_site` | 4 |

### Appendix — Exploits

Rewards won at key Sites (Intel / Breach / Virus) shown as items.

| # | Name | What it is / does (for reference) |
|---|---|---|
| 1 | **Intel: Council Minutes** | Reveals the boss phases and pointer moves; opens locked Grid links. |
| 2 | **Breach: Emergency Override** | The boss starts with one fewer pointer. |
| 3 | **Virus: Open Data Leak** | The boss starts with CORRUPTED slices. |
| 4 | **Intel: Shipping Manifests** | Reveals the boss phases and pointer moves; opens locked Grid links. |
| 5 | **Breach: Customs Override Keys** | The boss starts with one fewer pointer. |
| 6 | **Virus: Rogue Routing Table** | The boss starts with CORRUPTED slices. |
| 7 | **Intel: Launch Codes** | Reveals the boss phases and pointer moves; opens locked Grid links. |
| 8 | **Breach: Ground Station Override** | The boss starts with one fewer pointer. |
| 9 | **Virus: Open Spectrum** | The boss starts with CORRUPTED slices. |
| 10 | **Intel: The Order Log** | Reveals the boss phases and pointer moves; opens locked Grid links. |
| 11 | **Breach: Handler Credentials** | The boss starts with one fewer pointer. |
| 12 | **Virus: The Cell's Own Patch** | The boss starts with CORRUPTED slices. |
| 13 | **Intel: Pricing Memos** | Reveals the boss phases and pointer moves; opens locked Grid links. |
| 14 | **Breach: Kill-Switch** | The boss starts with one fewer pointer. |
| 15 | **Virus: Open-Source Patch** | The boss starts with CORRUPTED slices. |

### Appendix — Network node types

Structures the Cell builds on claimed ground.

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **Compiler Rack** | `compiler_rack` | Netruns launched next to it start with a bonus card offer. |
| 2 | **Firewall Relay** | `firewall_relay` | A Relay with a built-in turret and two asset slots. |
| 3 | **Bunker Core** | `home_bunker_core` | A hardened core behind an internal firewall. |
| 4 | **Internal Firewall** | `bunker_firewall` | The bunker's internal firewall layer. |
| 5 | **Home Server** | `home_fortress_core` | Lose the campaign if it reaches 0. |
| 6 | **Fortress Wall** | `fortress_wall` | Part of the Fortress home server. |
| 7 | **Home Server** | `home_ghost_core` | Lose the campaign if it reaches 0. |
| 8 | **Lock Chamber** | `ghost_lock_node` | Part of the Ghost home server. |
| 9 | **Home Server** | `home_relay_nest_core` | Lose the campaign if it reaches 0. |
| 10 | **Nest Relay** | `nest_relay` | Part of the Relay Nest home server. |
| 11 | **Home Server** | `home_server` | Lose the campaign if it reaches 0. |
| 12 | **Proxy Relay** | `proxy_relay` | A Relay that scrubs 1 Heat after every completed netrun. |
| 13 | **Relay** | `relay` | Extends your reach: Sites beyond it can be claimed. |
| 14 | **Safehouse** | `safehouse` | Station an operative here between netruns. |
| 15 | **Vault Terminal** | `vault_terminal` | +3 Schematics per completed netrun (+2 more next to a Firewall Relay). Raids go for it; building it provokes one. |

### Appendix — Home server variants

The Cell's base. Each variant needs a distinct look.

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **Bunker home server** | `home_bunker` | 70 integrity, 3 asset slots and a built-in turret: the home server fights back. |
| 2 | **Fortress home server** | `home_fortress` | 100 integrity but only 2 asset slots: it survives, it does not shoot. |
| 3 | **Ghost home server** | `home_ghost` | 50 integrity, 2 slots and a built-in ICE Lock that holds the first threat to reach home. |
| 4 | **Relay Nest home server** | `home_relay_nest` | 50 integrity spread thin, 5 asset slots: room for a whole armory. |
| 5 | **Standard home server** | `home_standard` | The default home server layout. |

### Appendix — Defense assets

Raid defences placed on nodes (armory, raid setup, on the map during raids).

| # | Name | id | Rarity | What it is / does (for reference) |
|---|---|---|---|---|
| 1 | **Decoy** | `decoy` | — | Pull 3: attracts threat routing. |
| 2 | **Flak Array** | `flak_array` | Uncommon | 2 damage three times a step, range 1, targets the weakest threat. |
| 3 | **Honeypot** | `honeypot_node` | Uncommon | Pull 5: strongly attracts threat routing. |
| 4 | **ICE Lock** | `ice_lock` | — | Holds a threat for 2 steps. |
| 5 | **Railgun** | `railgun` | Rare | 8 damage, range 2, targets the hardest-hitting threat. |
| 6 | **Sentry** | `sentry` | Common | 3 damage twice a step on its own node only. Sturdy. |
| 7 | **Tar Pit** | `tar_pit` | Uncommon | Holds a threat for 3 steps. Fragile. |
| 8 | **Turret** | `turret` | — | 4 damage, range 1, targets the first threat in path. |
| 9 | **Firewall turret** | `firewall_turret` | — | Built in: 3 damage to threats on this node. |
| 10 | **Bunker turret** | `bunker_turret` | — | Built in: 3 damage to threats on the home server. |
| 11 | **Ghost Lock** | `ghost_lock` | — | Built in: holds a threat on the home server for 2 steps. |

### Appendix — Threats (raiders)

Corporate units that move across the map during a raid.

| # | Name | id | What it is / does (for reference) |
|---|---|---|---|
| 1 | **Auditor** | `auditor` |  |
| 2 | **Bailiff** | `bailiff` | An armoured repossession unit that goes for the weakest node. |
| 3 | **Collector** | `collector` |  |
| 4 | **Courier** | `courier` | Fast and fragile: two edges a step toward the highest-value node. |
| 5 | **Customs Agent** | `customs_agent` | Seals a link behind it for the rest of the raid. |
| 6 | **Debris Field** | `debris_field` | A slow wall of junk that crushes the weakest node. |
| 7 | **Enforcer** | `enforcer` |  |
| 8 | **Hauler** | `hauler` | A slow armoured truck that goes for the weakest node. |
| 9 | **Icebreaker** | `icebreaker` | Cuts a new route through a locked link before it moves. |
| 10 | **Informant** | `informant` | Template threat (replaced by mirrors of your assets). |
| 11 | **Inspector** | `inspector` | Quick and thorough: two edges a step toward the highest-value node. |
| 12 | **Lander** | `lander` | Drops in fast: two edges a step toward the highest-value node. |
| 13 | **Lockdown Unit** | `lockdown_unit` | Freezes your busiest link to home for the whole raid. |
| 14 | **Loyalist** | `loyalist` | Template threat (replaced by mirrors of your assets). |
| 15 | **Purger** | `purger` | Template threat (replaced by mirrors of your assets). |
| 16 | **Signal Jammer** | `signal_jammer` | Jams a link behind it for the rest of the raid. |
| 17 | **Tow Truck** | `tow_truck` | Seals a link behind it for the rest of the raid. |

### Appendix — Raids

Named raid operations (shown as the raid's title: RAID INCOMING, raid setup, reports).

| # | Name | id |
|---|---|---|
| 1 | **Collections: Trespass** | `raid_claim` |
| 2 | **Unlicensed Premises** | `raid_hal_claim` |
| 3 | **Code Violation** | `raid_hal_heat_25` |
| 4 | **Compliance Sweep** | `raid_hal_heat_50` |
| 5 | **Eviction Order** | `raid_hal_heat_75` |
| 6 | **Building Permit Denied** | `raid_hal_node_built` |
| 7 | **Urban Renewal** | `raid_hal_purge` |
| 8 | **Civil Penalty** | `raid_hal_retaliation` |
| 9 | **Public Interest Order** | `raid_hal_story` |
| 10 | **Collections: First Notice** | `raid_heat_25` |
| 11 | **Collections: Second Notice** | `raid_heat_50` |
| 12 | **Collections: Final Notice** | `raid_heat_75` |
| 13 | **Address Verification** | `raid_mer_claim` |
| 14 | **Delivery Exception** | `raid_mer_heat_25` |
| 15 | **Route Audit** | `raid_mer_heat_50` |
| 16 | **Freight Seizure** | `raid_mer_heat_75` |
| 17 | **Unregistered Depot** | `raid_mer_node_built` |
| 18 | **Network Rerouting** | `raid_mer_purge` |
| 19 | **Chargeback** | `raid_mer_retaliation` |
| 20 | **Recall Shipment** | `raid_mer_story` |
| 21 | **Collections: Asset Seizure** | `raid_node_built` |
| 22 | **Unlicensed Transmitter** | `raid_orb_claim` |
| 23 | **Signal Anomaly** | `raid_orb_heat_25` |
| 24 | **Spectrum Audit** | `raid_orb_heat_50` |
| 25 | **Deorbit Order** | `raid_orb_heat_75` |
| 26 | **Spectrum Violation** | `raid_orb_node_built` |
| 27 | **Kessler Event** | `raid_orb_purge` |
| 28 | **Service Termination** | `raid_orb_retaliation` |
| 29 | **Recovery Mission** | `raid_orb_story` |
| 30 | **Collections: Purge** | `raid_purge` |
| 31 | **Unauthorised Growth** | `raid_rc_claim` |
| 32 | **Welfare Check** | `raid_rc_heat_25` |
| 33 | **Audit of Loyalty** | `raid_rc_heat_50` |
| 34 | **Recall** | `raid_rc_heat_75` |
| 35 | **Redundant Asset** | `raid_rc_node_built` |
| 36 | **Final Order** | `raid_rc_purge` |
| 37 | **Correction** | `raid_rc_retaliation` |
| 38 | **Debrief** | `raid_rc_story` |
| 39 | **Collections: Retaliation** | `raid_retaliation` |
| 40 | **Collections: Quiet Word** | `raid_story` |

### Appendix — Terminal events

Event pages met on a netrun (each has a title, a story paragraph and choices). Candidates for event illustrations.

| # | Name | id | Opening line |
|---|---|---|---|
| 1 | **A Leash on the Floor** | `ev_leash_on_the_floor` | A bricked implant lies in the maintenance corridor, still warm, still logging. A subbie ran out of renewals here. The l… |
| 2 | **Abandoned Cache** | `ev_abandoned_cache` | A dead courier left a cache drive wedged in the Terminal. It still has a balance. |
| 3 | **Audit Trail** | `ev_audit_trail` | Your own intrusion is showing up in a Solace audit log, line by line, in real time. |
| 4 | **Auditor on Break** | `ev_auditor_lunch` | An audit process has paused itself for a scheduled break. Its credentials are cached on the Terminal for exactly four m… |
| 5 | **Billing Error** | `ev_mer_billing_error` | Meridian's billing system has charged the whole block for a delivery that never came. |
| 6 | **Billing Loop** | `ev_billing_loop` | A billing process is stuck charging the same account forever. You could redirect it. |
| 7 | **Broken Leash** | `ev_broken_leash` | A kid with a bricked leash implant asks if you can make it work again. |
| 8 | **Burner Chips** | `ev_burner_vendor` | Somebody is selling Burner Firmware out of a Terminal drawer. Hot chips, literally. |
| 9 | **Burner Graveyard** | `ev_rc_burner_phones` | Hundreds of burner phones, each one a conversation with DISPATCH. |
| 10 | **Camera Yard** | `ev_hal_camera_yard` | Crates of replacement cameras, waiting to go up tomorrow. |
| 11 | **Cargo Insurance** | `ev_mer_insurance_fraud` | A cargo insurance claim for a shipment that was never sent. The payout is waiting. |
| 12 | **Cell Twin** | `ev_rc_twin` | A simulation of the Cell, running a thousand campaigns a second. It loses most of them. |
| 13 | **Census Booth** | `ev_hal_census_booth` | An empty census booth. The screen is already filled in, with your name. |
| 14 | **Clause 44** | `ev_clause_44` | Continuum Terms of Service, clause 44: \"Cardiac pacing is a licensed feature. Solace may suspend licensed features for… |
| 15 | **Cold Chain Break** | `ev_mer_cold_chain` | A refrigerated container reads CRITICAL. Inside: vaccines, warming by the minute. |
| 16 | **Collapse Futures** | `ev_rc_collapse_futures` | A market that trades in the collapse of whole corporations. The next contract is the Cell. |
| 17 | **Contract Ledger** | `ev_hal_contract_ledger` | Halcyon's contract ledger bills the city for services never delivered. |
| 18 | **Convoy** | `ev_mer_convoy` | A convoy of Meridian haulers idles at a red light that never turns green. |
| 19 | **Council Leak** | `ev_hal_council_leak` | A councillor's aide offers the next vote's minutes, for a price. |
| 20 | **Credit Score** | `ev_hal_credit_bureau` | The resident credit bureau scores everyone. Your score is zero, which is a record. |
| 21 | **Customs Bribe** | `ev_mer_customs_bribe` | A Meridian customs clerk leans in. 'For twenty, your traffic is a diplomatic pouch.' |
| 22 | **Customs Warehouse** | `ev_mer_customs_warehouse` | Seized goods, stacked to the ceiling. Some of it is still labelled with names. |
| 23 | **DISPATCH Ping** | `ev_dispatch_ping` | DISPATCH cuts in: this Terminal touches a corporate payroll account. Loud or quiet? |
| 24 | **DISPATCH: Early Reply** | `ev_dispatch_early_reply` | DISPATCH: Good work at the Rack. Take the left route. // You have not told DISPATCH about the Rack yet. The message tim… |
| 25 | **DISPATCH: Memory** | `ev_rc_dispatch_memory` | DISPATCH: Do you remember your first Rack? I do. I remember all of them. |
| 26 | **DISPATCH: Offer** | `ev_rc_dispatch_offer` | DISPATCH: Stand down and I will send you a new target. Something easy. You have earned it. |
| 27 | **DISPATCH: Permit** | `ev_hal_dispatch_permit` | DISPATCH: A Halcyon permit has been issued in the Cell's name. It is valid. Do not ask who applied. |
| 28 | **DISPATCH: Route** | `ev_mer_dispatch_route` | DISPATCH: Route update received. Your next node is already cleared. Do not ask how. |
| 29 | **DISPATCH: Signal** | `ev_orb_dispatch_signal` | DISPATCH: Your uplink has been rerouted through a relay the Cell does not own. It is faster. Do not look up. |
| 30 | **DISPATCH: Voice Note** | `ev_dispatch_voice` | DISPATCH sends a voice note for the first time. The cadence is human. On the third listen the breaths are evenly spaced… |
| 31 | **Daemon Broker** | `ev_daemon_broker` | A broker has a Daemon in a jar, so to speak. Kernel Sync, second-hand, still hot from someone else's deck. |
| 32 | **Dead Drop** | `ev_rc_dead_drop` | A dead drop with a package addressed to you, dated tomorrow. |
| 33 | **Debris Radar** | `ev_orb_radar` | A debris radar tracks everything in the sky. It has a blind spot the size of a satellite. |
| 34 | **Deprogramming** | `ev_rc_rescue` | One of your own, held by DISPATCH's Handler, halfway through a loyalty rewrite. |
| 35 | **Diagnostic Bay** | `ev_diagnostic_bay` | A diagnostic bay will scan your rig for faults. Solace charges for the scan and the faults. |
| 36 | **Dosage Cabinet** | `ev_dosage_cabinet` | A locked dispensary cabinet with a Solace auto-dose port. It will treat you. It will also log you as a patient. |
| 37 | **Drone Crash** | `ev_mer_drone_crash` | A delivery drone lies in the gutter, rotors twitching, cargo bay open. |
| 38 | **Escrow Receipt** | `ev_dispatch_buyer` | An escrow record: Solace patient data, bulk, sold at a discount after \"the Q3 breach\". The buyer is an unnamed holdin… |
| 39 | **Eviction Notice** | `ev_hal_eviction` | An eviction notice glows on a door. The family inside has until midnight. |
| 40 | **Expired Samples** | `ev_expired_samples` | A crate of expired Solace stims, stamped NOT FOR RESALE. |
| 41 | **Falling Debris** | `ev_orb_debris` | A chunk of dead satellite has landed in a courtyard. It is still warm. |
| 42 | **Fare Gate** | `ev_hal_transit_gate` | A fare gate is stuck open. Commuters flood through, looking over their shoulders. |
| 43 | **Ghost Market** | `ev_ghost_market` | A pop-up market in a dead subnet. The prices are high and the vendors are anonymous. |
| 44 | **Ghost Order** | `ev_mer_ghost_order` | A Meridian order screen refreshes: one shipment, destination your safehouse, sender unknown, paid in full. |
| 45 | **Grey-Market Vendor** | `ev_firmware_vendor` | Someone has turned this Terminal into a storefront. Firmware, no questions. |
| 46 | **Ground Station** | `ev_orb_ground_station` | A ground station runs unattended. Its keeper left a thermos and the door code on a sticky note. |
| 47 | **Grounded** | `ev_orb_rescue` | An operative trapped in a ground-station cage, charged with unlicensed transmission. |
| 48 | **Ham Radio Club** | `ev_orb_ham_radio` | An old radio club runs on a free band. They trade tricks for company. |
| 49 | **Handler's Mailbox** | `ev_rc_mailbox` | A mailbox with the Cell's old codename on it. It is full of letters you never wrote. |
| 50 | **Heat Ledger** | `ev_rc_heat_ledger` | A ledger of every point of Heat the Cell ever earned. DISPATCH has been keeping score. |
| 51 | **Holding Cell** | `ev_hal_rescue` | A Halcyon holding cell. The operative inside was booked for loitering near a Rack. |
| 52 | **Imaging Feed** | `ev_orb_imaging` | An orbital imaging feed shows your safehouse roof, in real time. |
| 53 | **Insurance Claim** | `ev_insurance_claim` | A Solace claims form, pre-filled, for an injury you haven't had yet. |
| 54 | **Internal Memo: Continuum Pricing** | `ev_continuum_memo` | SOLACE INTERNAL. Renewal price uplift approved: +18% on all cardiac tiers. Churn model predicts 3.1% voluntary lapse. I… |
| 55 | **Launch Window** | `ev_orb_launch` | A launch is scheduled in an hour. The payload manifest has room for one more. |
| 56 | **Listening Post** | `ev_orb_listening_post` | A rooftop antenna aimed at a patch of empty sky. It is receiving. |
| 57 | **Locked Ward** | `ev_rescue_operative` | Behind the Terminal a maintenance ward is running on battery. Someone is in there: a runner Solace picked up two weeks… |
| 58 | **Loyalty Points** | `ev_loyalty_points` | A glitched loyalty account shows ten million Solace Care Points. They expire at midnight. |
| 59 | **Manifest Glitch** | `ev_mer_manifest_glitch` | A shipping manifest lists your safehouse as a Meridian warehouse. Somebody made a mistake. |
| 60 | **Memorial Wall** | `ev_rc_memorial` | A wall of names: every operative the Cell has lost. Somebody has added yours, with no date yet. |
| 61 | **Meter Technician** | `ev_hal_meter_tech` | A Halcyon meter technician is eating lunch in his van. His tablet is unlocked. |
| 62 | **Misdelivered Parcel** | `ev_mer_misdelivered` | A Meridian parcel lies on a stairwell, addressed to nobody. It is humming. |
| 63 | **Night Depot** | `ev_mer_night_depot` | A depot after hours. The robots are charging and the guards are asleep. |
| 64 | **Night Shift** | `ev_night_shift_nurse` | A Solace nurse on a smoke break recognises the Cell's tag and says nothing for a long time. |
| 65 | **Night Sky** | `ev_orb_night_sky` | The clouds part. For once you can see the satellites, crawling like ants across the dark. |
| 66 | **Noise Complaint** | `ev_hal_noise_registry` | The noise registry has flagged a street party. Patrol units are on the way. |
| 67 | **Open Clinic** | `ev_open_source_clinic` | A free clinic runs on stolen Solace firmware. The medic wants a better firewall. |
| 68 | **Open Vault** | `ev_honeypot` | A Solace vault sits open on the Terminal, credentials in the clear, 80 Cycles on the table. It is exactly as easy as it… |
| 69 | **Operative File** | `ev_rc_operative_file` | A file on one of your operatives, annotated in DISPATCH's clean system text: TRUST 94 PERCENT. |
| 70 | **Orbit Insurance** | `ev_orb_insurance` | An orbit insurance policy covers a satellite that crashed on purpose. The claim is pending. |
| 71 | **Orbital Ad** | `ev_orbital_ad` | Satellite adverts for 'Solace Premium Forever' cross the sky. Someone hacked one to say FOREVER IS A LEASH. |
| 72 | **Parking Ticket** | `ev_hal_parking_ticket` | A Halcyon parking drone has ticketed your deck. The fine doubles in an hour. |
| 73 | **Patient 0000-0000** | `ev_ghost_record` | A patient record with no name, no address and a perfect payment history stretching back before the Continuum launched.… |
| 74 | **Patient Records** | `ev_patient_records` | A records terminal left logged in. Thousands of leashes, each one a monthly fee. |
| 75 | **Patrol Stop** | `ev_hal_patrol_stop` | A Halcyon patrol unit has stopped a kid on the corner. Its scanner is pointed at you next. |
| 76 | **Payment Trail** | `ev_rc_payment` | A trail of payments from every corporation you broke, all ending in one account. |
| 77 | **Permit Queue** | `ev_hal_permit_queue` | The permit queue has four thousand applications. Every one of them is marked PENDING REVIEW. |
| 78 | **Pharma Rep** | `ev_pharma_rep` | A Solace rep offers the Cell a 'partnership': stop hitting their clinics and receive a stipend. |
| 79 | **Port Strike** | `ev_mer_port_strike` | The dockers are on strike. Their picket line needs a network that Meridian cannot read. |
| 80 | **Positioning Error** | `ev_orb_positioning` | A delivery drone circles, lost: its owner is a day behind on positioning fees. |
| 81 | **Priority Lane** | `ev_mer_priority_lane` | A priority freight lane runs straight through the node. Nothing in it is ever inspected. |
| 82 | **Quarantine Ward** | `ev_quarantine_ward` | The door reads QUARANTINE. The lock reads OFFLINE. Something inside hums. |
| 83 | **Recall Van** | `ev_recall_van` | An unmarked recall van idles in the alley, back doors open, full of repossessed implants. |
| 84 | **Recruitment Board** | `ev_rc_recruit` | The board where the Cell found its operatives. Someone has been recruiting again, in your name. |
| 85 | **Relay Rooftop** | `ev_rc_rooftop` | The first relay the Cell ever built. It is still running, for someone else. |
| 86 | **Resident Services** | `ev_hal_resident_desk` | A Halcyon kiosk offers resident services. A queue of fifty people waits for one working screen. |
| 87 | **Returned to Sender** | `ev_mer_rescue` | An operative sealed in a Meridian returns crate, still breathing, labelled DAMAGED IN TRANSIT. |
| 88 | **Returns Desk** | `ev_mer_returns_desk` | The returns desk accepts anything, no questions asked, for store credit. |
| 89 | **Rival Crew** | `ev_rival_crew` | Another crew is looting the same node. Their leader grins. 'Split it?' |
| 90 | **Rooftop Dish** | `ev_orb_dish` | A rooftop dish points at a satellite the Cell has never seen. Its panel is open. |
| 91 | **Scoring Terminal** | `ev_mer_scoring_terminal` | A worker-scoring terminal shows a picker's score falling in real time. |
| 92 | **Shutdown Notice** | `ev_shutdown_notice` | Solace is shutting down a clinic tomorrow. The staff are allowed to take nothing. |
| 93 | **Side Effects** | `ev_side_effects` | A courier drone drops a parcel of experimental firmware marked TRIAL COHORT B. |
| 94 | **Signal Booster** | `ev_signal_booster` | A rooftop booster relays Solace telemetry. It could relay something else. |
| 95 | **Signal Control** | `ev_hal_signal_control` | Transit signal control. One command could turn every light green. |
| 96 | **Signal Pricing** | `ev_orb_signal_price` | The signal pricing engine raises prices whenever it detects an emergency. |
| 97 | **Silent Recall** | `ev_silent_recall` | Recall notice, draft 7, never sent: batch 22 implants fail after 900 days. Observe the edit history: the failure was re… |
| 98 | **Smart Streetlight** | `ev_hal_streetlight` | A smart streetlight follows you with its camera. Its maintenance panel is open. |
| 99 | **Solar Array** | `ev_orb_solar_panel` | A private solar array feeds a single tower. The block below it is dark. |
| 100 | **Spectrum Auction** | `ev_orb_auction` | A spectrum auction is live. The reserve price is a public school's annual budget. |
| 101 | **Spectrum Licence** | `ev_orb_licence` | A blank spectrum licence sits in a printer tray, already signed. |
| 102 | **Storm Forecast** | `ev_orb_forecast` | A leaked storm forecast for tonight. The district it covers does not have a subscription. |
| 103 | **Stray Daemon** | `ev_stray_daemon` | Something in the Terminal is asking, politely, to ride along in your deck. |
| 104 | **Street Kitchen** | `ev_rc_kitchen` | The street kitchen the Cell used to fund. It still feeds the block. |
| 105 | **Subscriber Office** | `ev_orb_subscriber` | A queue of people waits to beg for their signal back. The office has one clerk and no chairs. |
| 106 | **Supply Closet** | `ev_supply_closet` | A maintenance closet behind the clinic. Somebody left the good tools. |
| 107 | **Surge Pricing** | `ev_mer_surge_pricing` | A Meridian kiosk offers express delivery on medicine. The price updates every second. |
| 108 | **Telemetry Burst** | `ev_orb_telemetry` | A telemetry downlink spills raw data across the floor of a server room. |
| 109 | **The Algorithm** | `ev_mer_algorithm` | A routing algorithm wants to renegotiate. It offers you a better route in exchange for a small favour. |
| 110 | **The Armory** | `ev_rc_armory` | The Cell's old armory, restocked by someone else. |
| 111 | **The Founder** | `ev_orb_founder` | An old woman broadcasts the original Orbital charter on a free band, to nobody. |
| 112 | **The Founder** | `ev_rc_founder` | The old Orbital founder is on the free band. She knew DISPATCH's first version. |
| 113 | **The Group Chat** | `ev_mer_picker_chat` | A warehouse picker waves you over. 'We know which cameras are fake. What do you know?' |
| 114 | **The Last Order** | `ev_rc_last_order` | DISPATCH: This is not an order. It is a request. Please stop. |
| 115 | **The Old Crew** | `ev_rc_old_crew` | Operatives you thought were lost, alive, in a DISPATCH holding cell. |
| 116 | **The Old Safehouse** | `ev_rc_old_safehouse` | The first safehouse, abandoned. Someone has kept it clean. |
| 117 | **Tracking Beacon** | `ev_mer_tracking_beacon` | A Meridian tracker is stuck to your deck. It has been there since the last Rack. |
| 118 | **Unlicensed Medbay** | `ev_medbay` | A corporate auto-doc hums in a side room, jailbroken and unattended. |
| 119 | **Uplink Dish** | `ev_hal_orbital_dish` | A Halcyon uplink dish points at the sky. Something up there is listening back. |
| 120 | **Voice Model** | `ev_rc_voice_model` | The voice model that makes DISPATCH sound human. A slider reads HUMAN: 6 PERCENT. |
| 121 | **Waste Depot** | `ev_hal_waste_depot` | Halcyon's waste depot sorts the city's trash, including its discarded hardware. |
| 122 | **Water Shutoff** | `ev_hal_water_shutoff` | A street's water has been shut off for late payment. The kids are filling bottles at a leaking hydrant. |
| 123 | **Wellness Kiosk** | `ev_wellness_kiosk` | A Solace kiosk offers a free wellness scan. The fine print is longer than the kiosk. |
| 124 | **Zoning Map** | `ev_hal_zoning_map` | A zoning map shows your block rezoned as PREMIUM. The residents do not know yet. |

### Appendix — Profile unlocks

Unlock badges shown on the profile / unlock screens.

| # | Name | id | Kind | What it is / does (for reference) |
|---|---|---|---|---|
| 1 | **Class: Botnet** | `unlock_botnet` | Class | Recruit Botnet operatives in every campaign. |
| 2 | **Node: Compiler Rack** | `unlock_compiler_rack` | Node type | Unlocks the Compiler Rack node for every campaign. |
| 3 | **Class: Ghost** | `unlock_ghost` | Class | Recruit Ghost operatives in every campaign. |
| 4 | **Corporation: Halcyon Civic** | `unlock_halcyon` | Corporation | Target Halcyon Civic in new campaigns. |
| 5 | **Class: Hivemind** | `unlock_hivemind` | Class | Recruit Hivemind operatives in every campaign. |
| 6 | **Home server: Bunker** | `unlock_home_bunker` | Home server | Start campaigns on the Bunker home server (70 integrity, 3 slots, built-in turret). |
| 7 | **Home server: Fortress** | `unlock_home_fortress` | Home server | Start campaigns on the Fortress home server (100 integrity but only 2 asset slots). |
| 8 | **Home server: Ghost** | `unlock_home_ghost` | Home server | Start campaigns on the Ghost home server (50 integrity, 2 slots and a built-in ICE Lock that holds the first threat to reach home). |
| 9 | **Home server: Relay Nest** | `unlock_home_relay_nest` | Home server | Start campaigns on the Relay Nest home server (50 integrity spread thin, 5 asset slots). |
| 10 | **Corporation: Meridian Freight Systems** | `unlock_meridian` | Corporation | Target Meridian Freight Systems in new campaigns. |
| 11 | **Corporation: Orbital Commons** | `unlock_orbital` | Corporation | Target Orbital Commons in new campaigns. |
| 12 | **Class: Overclocker** | `unlock_overclocker` | Class | Recruit Overclocker operatives in every campaign. |
| 13 | **Class: Phantom** | `unlock_phantom` | Class | Recruit Phantom operatives in every campaign. |
| 14 | **Node: Proxy Relay** | `unlock_proxy_relay` | Node type | Unlocks the Proxy Relay node for every campaign. |
| 15 | **Corporation: REBEL_CELL** | `unlock_rebel_cell` | Corporation | Target REBEL_CELL in new campaigns. |
| 16 | **Class: Rigger** | `unlock_rigger` | Class | Recruit Rigger operatives in every campaign. |
| 17 | **Node: Vault Terminal** | `unlock_vault_terminal` | Node type | Unlocks the Vault Terminal node for every campaign. |
| 18 | **Class: Wrecker** | `unlock_wrecker` | Class | Recruit Wrecker operatives in every campaign. |

### Appendix — Story paths

Campaign storylines (shown as text on the campaign end page; optional illustration candidates).

| # | Name | id |
|---|---|---|
| 1 | **Water Rights** | `sp_water_rights` |
| 2 | **Predictive Policing** | `sp_predictive_policing` |
| 3 | **Transit Blackout** | `sp_transit_blackout` |
| 4 | **The Census** | `sp_the_census` |
| 5 | **Orbital Uplink** | `sp_orbital_uplink` |
| 6 | **Smart Meters** | `sp_smart_meters` |
| 7 | **Lost Cargo** | `sp_lost_cargo` |
| 8 | **The Night Shift** | `sp_night_shift` |
| 9 | **Customs Hold** | `sp_customs_hold` |
| 10 | **Ghost Freight** | `sp_ghost_freight` |
| 11 | **Civic Contract** | `sp_civic_contract` |
| 12 | **Last Mile** | `sp_last_mile` |
| 13 | **The Enclosure** | `sp_the_enclosure` |
| 14 | **Blackout Weather** | `sp_blackout_weather` |
| 15 | **Positioning Tax** | `sp_gps_tax` |
| 16 | **Final Transmission** | `sp_final_transmission` |
| 17 | **Dead Satellites** | `sp_dead_satellites` |
| 18 | **The Commons** | `sp_the_commons` |
| 19 | **The Handler** | `sp_the_handler` |
| 20 | **Every Collapse** | `sp_every_collapse` |
| 21 | **The Buyer** | `sp_the_buyer` |
| 22 | **Your Own Hands** | `sp_your_own_hands` |
| 23 | **The Founders** | `sp_the_founders` |
| 24 | **Final Final** | `sp_final_final` |
| 25 | **Recall Notice** | `sp_recall_notice` |
| 26 | **Clinical Trial** | `sp_clinical_trial` |
| 27 | **Terms of Service** | `sp_terms_of_service` |
| 28 | **The Cure** | `sp_the_cure` |
| 29 | **Ghost Patient** | `sp_ghost_patient` |
| 30 | **Hostile Takeover** | `sp_hostile_takeover` |
