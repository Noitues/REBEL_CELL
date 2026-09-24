# REBEL_CELL — Gap Analysis and Horizontal Slice Plan

Date: 2026-09-24 · Basis: GDD v0.9, TECH_SPEC, STYLE_GUIDE, MILESTONES M0–M4 (all
accepted), the code (10,038 lines of GDScript, 264 tests) and the content tree (143 ids).

Target set by the designer: **a complete game — all bosses, operatives, story, dialog,
menus — that an average player spends about 100 hours on to reach full content.**

---

## 1. Where the project stands

| Layer | Built | Evidence |
|---|---|---|
| Combat core | Wheel math, resolver, effect language, preview, rewind, replay, statuses, Firmware, Daemons, boss phases, Exploit overrides | 30-tick table tests, 500-turn preview test, replay hash, 25 cards / 6 Firmware / 6 Daemons each tested |
| Netrun | Map generator, node contents, rewards, Modem, Terminals, banking, death/completion, mid-run raid interludes, save/resume | 1,000-seed map test, banking/death/completion tests, resume-identical tests |
| Campaign | City Grid state, claiming through Relays, 3 node types, repair, recruit, stationing, Heat thresholds, Armory, raids with exact projection, Exploits, story beats, win/loss, profile records | Golden raid layouts, campaign round-trip tests |
| Presentation | Three-worlds baseline, zine kit, wireframe wheels with glyphs, ghost preview, precision/Heat feedback, generated audio, accessibility settings, full keyboard combat | Layout, flash-limiter, glyph, keyboard and reduce-effects tests |
| Content | 1 class, 1 corporation with a 10-Site Grid, 9 enemies + 3 satellites + 1 boss, 25 cards, 6 Firmware, 6 Daemons, 3 assets, 3 threats, 5 events, 5 raids, 5 placeholder story paths | `content/` |

The loop is playable end to end: HQ → Grid → netrun (map, fights, shop, events, mini-boss)
→ back to HQ → raids → three Exploits → the Renewal Engine → win.

---

## 2. Gaps in the vertical slice

Systems the GDD specifies for the slice (or that the slice needs to feel complete) that
are missing, placeholder, or only data. Severity: **A** blocks the "complete game"
claim, **B** is a visible hole in play, **C** is polish. Size: S (≤1 day), M (2–4 days),
L (1–2 weeks), XL (more).

### 2.1 Combat rules

| Gap | GDD | Sev | Size | Notes |
|---|---|---|---|---|
| DEPLOY slices / `DEPLOY_DRONE` / drones docked on the player wheel | 2.6, 5.2 | A | M | Needed by Botnet; resolver reports "unsupported". Player-side satellites (bodyguards on your own wheel) are not modelled. |
| Enemy `ENEMY_RESISTANCE` modifier (Heat 50, ICE 7) not applied in combat | 4.3, 11.9 | A | S | `rule_modifier` exists; `create_combat` must add it to enemy resistance. |
| `BOSS_STRENGTH_PCT`, `BOSS_EXTRA_POINTER`, `STARTING_BUG_CARD`, `NO_FIRST_TURN_FREE_NUDGE` not applied | 11.9 | A | S | Data exists; wire through `NetrunSession` overrides. "Bug" card content missing. |
| MIGRATE phases are not telegraphed a turn early; orbit trail exists, migration flicker does not | 2.11, 9.2 | B | S | Add a "next layout" preview event + wheel view flicker. |
| `BossPhaseData.wheel_override` ignored | 2.11 | C | S | Only `hub_override` and spawns apply. |
| Satellite spawns with `ON_TURN_START` / `every_n` / `max_active` beyond combat start | schema | B | S | Only ON_COMBAT_START spawns. |
| `HeatGatedEffectData` (enemy behaviour above a Heat) never evaluated | schema, 4.3 | B | S | |
| Inner Ring segments Corrupt, Anchor, Accelerator, Echo (content) and the Rank 3 segment-swap flow | 6.4, 5.3 | A | M | Resolver supports retrigger/pierce/multiplier/triggered effects; `DOUBLE_NUDGE_CARDS` (Accelerator) is unimplemented. |
| Daemons Linked Bus, Stolen Intent, Twin Pointer, Botnet Seed | 6.2 | A | M | Rule-breakers → handler scripts; Twin Pointer needs a second player pointer + "max RAM halved". |
| Card slice picker and nudge-direction picker in the combat UI | 2.5, A.2 | A | S | Cleanse/Encrypt are refused in the scene (no slot pick); Fine Tune/Micro-Adjust always nudge +1. Core supports both. |
| Random-effect **odds** in the HUD (Respin, random targets) | 2.10 | B | M | Preview hides the DOSE slot but shows no probabilities. |
| Right-click **inspect** (bound, unused) and hover inspect for slices, statuses, Daemons | 9.5 | B | M | Codex-style tooltips. |
| Combat log filtering/animation pacing; resolve is instant | 5.6 | C | M | Events are logged; no tweened playback of the three passes. |

### 2.2 Netrun

| Gap | GDD | Sev | Size | Notes |
|---|---|---|---|---|
| Routers dropping common Firmware | 6.3 | B | S | Only elites offer Firmware. |
| `CYCLE_PRICE_PCT` (ICE 4) not applied to Modem prices | 11.9 | A | S | `_price_scale()` is a stub. |
| `HEAT_OBJECTIVE_SITES`, `HEAT_GAIN_PCT`, `HEAT_SINK_PCT`, `DEATH_HEAT`, `EXPLOIT_HEAT`, `PURGE_THRESHOLD`, `REPAIR_COST_PCT`, `SEIZED_RAID_STRENGTH_PCT` not applied | 11.9 | A | M | The whole ICE ladder is data-only; applying each is small, together M. |
| One-time netrun boosts (10–20 Schematics) | 11.4 | B | S | Config exists, no purchase flow. |
| Compiler Rack bonus at run start, Vault Terminal +3 Schematics, Proxy Relay −1 Heat | 3.2 | A | M | Node types missing; `NetworkNodeData.passive_effects` never evaluated. |
| Netrun map as a wireframe graph (nodes/edges drawn) instead of button columns | 9.1 | B | M | Functional but not the visual baseline. |
| Terminal events: only 5 placeholders; no rescue-operative event; no DISPATCH clue chain | 4.2, 8.2, 8.6 | A | L | Writing + 30–60 events per corporation. |
| Retaliation raids for netrun objectives (Heat objective / Exploit Sites) | 4.4 | B | S | Only threshold and claim raids exist. |

### 2.3 Campaign, Grid and raids

| Gap | GDD | Sev | Size | Notes |
|---|---|---|---|---|
| ICE selection at campaign start, ICE progression rules, new-corporation offset, per-corp records → unlocks | 3.4, 11.9 | A | M | `ice_level` is always 0. |
| Profile unlocks: class unlock (80 Schematics), class alternatives, corporations, home-server variants, node types, skins | 3.4 | A | M | `ProfileUnlockData` exists; no flow. |
| Full City Grid (30–40 Sites, cross-links, more than one Heat objective, Reclaim targets) | 4.1 | A | L | Slice has 10. |
| Node upgrades (30 then 60) and the remaining node types | 11.4, 3.2 | A | M | |
| Threats that freeze or alter links before a raid | 7.1 | B | M | Flags exist on `ThreatData`; resolver ignores them. |
| Raid playout with speed controls (1×/2×/4×) and skip; threat paths animated on the Grid | 7.2, 9.3 | B | M | Playout is an instant log; paths are drawn statically. |
| Adjacency bonuses (`AdjacencyBonusData`) beyond the station-bonus Firewall rule | 3.2 | C | S | |
| Stationed operatives returning unharmed from Seized/Disabled nodes | 3.3 | B | S | Event is logged; the recall itself is not applied. |
| Home-server internal layout (variants with internal nodes) | 3.1 | C | M | Standard variant has no internal nodes. |
| Story raids, node-built raids (`triggers_raid` on Vault etc.) | 4.4 | B | S | Enum values exist; only HEAT_THRESHOLD and TERRITORY_CLAIM are used. |

### 2.4 Narrative, dialogue and voice

| Gap | GDD | Sev | Size | Notes |
|---|---|---|---|---|
| Six written Solace story paths (Hostile Takeover missing; all five are placeholders), bonus beats, finale scripts | 8.4 | A | L | |
| DISPATCH briefings per Site/raid/threshold; hidden AI clues across campaigns; voice drift | 8.2 | A | L | No DISPATCH text exists beyond one CRT line. |
| Operative barks, raid warnings (Corpo voice), pirate-radio DJ | 8.1, 8.6 | B | L | |
| Subtitles with speaker names (setting exists, no subtitle UI or line database) | 9.6 | A | M | |
| Codex (slices, statuses, cards, Firmware, Daemons, nodes, threats, lexicon) | 8.1 | B | M | |
| Voice acting (≈500 lines at launch) and localisation pipeline | 10 | A | XL | Text externalisation first (CSV/PO), then casting. |

### 2.5 Menus, platform and meta

| Gap | Sev | Size | Notes |
|---|---|---|---|
| Title/main menu, pause menu, quit/confirm dialogs | A | M | The game boots straight into HQ. |
| Options: display (fullscreen, resolution, vsync), audio buses, key rebinding, language | A | M | Only accessibility exists. |
| Save slots (multiple campaigns), delete/confirm, autosave indicator | B | S | One slot ("current"). |
| Tutorial / onboarding (first netrun guided, wheel reading, resistance, rewind) | A | L | Nothing teaches the wheel. |
| Achievements (e.g. "final final"), stats screen, run history | C | M | |
| Controller support (optional per GDD: PC mouse + keyboard) | C | M | |
| Export presets, CI running the three checks on every push, versioning | A | S | Tests exist; no pipeline. |
| Performance validation at 1080p on a mid-range PC (M4 item left unverified) | B | S | Needs a human run; add an in-game fps counter. |

### 2.6 Art and audio

| Gap | Sev | Size |
|---|---|---|
| Portraits (4 classes × glitch variants), enemy holograms, corporation logos | A | L |
| Wheel art pass (final wireframe/glow, slice icons), zine textures (paper, tape, stamps, stickers), HUD skinning | A | L |
| City Grid isometric building set, netrun map tiles, raid threat sprites | B | L |
| Jack-in/jack-out cinematic polish; Heat pulse art; wanted posters/searchlights | C | M |
| Music: 7 contexts + Heat layers, composed; SFX: ratchet family, precision set, UI | A | L |
| Voice recording (see 2.4) | A | XL |

---

## 3. What "100 hours to full content" implies

GDD §11.8 pacing: netrun ≈ 15 min, raid ≈ 5 min; an **average campaign ≈ 6 h 35 m**
(24 runs, ~7 raids), a fast one ≈ 2 h 15 m.

- 100 h at the average pace ≈ **15 campaigns**; at the fast pace ≈ 45.
- "Full content" = every corporation cleared, every class unlocked and played, REBEL_CELL
  unlocked (ICE 10 on every other corporation) and beaten.

Proposed shape (needs a designer ruling):

| Lever | Proposal | Why |
|---|---|---|
| Corporations | **4 corporations + REBEL_CELL** | 5 distinct campaigns ≈ 33 h once through. |
| ICE progression | Winning at ICE *n* unlocks up to *n + 3* on that corporation; new corporations start at (global best − 5) as the GDD says | Reaching ICE 10 on four corporations takes ~4 wins each = 16 campaigns; with the first pass and a REBEL_CELL climb that is ≈ 19 campaigns ≈ 120 h average / 45 h fast. One ICE per win would need ~40 campaigns (260 h). |
| Classes | 4 classes + 4 alternatives, unlocked with Schematics | Each class changes the wheel and deck enough to make a second pass on a corporation feel new. |
| Content per corporation | 30–40 Sites, 6 normal + 2 elite + 1 mini-boss + 1 boss (+ satellites), 3 Exploits, 5–6 story paths, ~40 Terminal events, 6–8 raid templates, own music and threat set | Matches GDD 4.1, 8.4 and the slice ratios. |
| Card pool | ~60 shared cards + 2 exclusives per class/alternative (~76) | Slice has 25; three-way choices need ~4× the pool to stop repeating within a run. |
| Firmware / Daemons | ~18 Firmware, ~24 Daemons (10 listed in the GDD) | Rack and Modem offers need depth to avoid repeats across 24 runs. |
| Defense | 7 node types (all in §3.2), ~8 assets, ~6 threats per corporation | |

---

## 4. Horizontal slices (missing content and systems), prioritised

P0 = required for a "complete game" at all; P1 = required for the 100-hour target;
P2 = polish and reach. Sizes as in §2.

### P0 — complete the systems the GDD already promises

1. **ICE ladder applied end to end** — every `RuleModifierType` wired (combat, netrun,
   campaign, raids), ICE picker at campaign start, progression/unlock rule, records. (M)
2. **All seven node types + node upgrades**, `passive_effects` and adjacency evaluation,
   Vault raid priority. (M)
3. **Inner Ring segment set** (Corrupt, Anchor, Accelerator, Echo) + Rank 3 swap flow. (M)
4. **Remaining Daemons** (Linked Bus, Stolen Intent, Twin Pointer, Botnet Seed) and a
   deeper Daemon/Firmware pool. (M)
5. **Player-side drones / DEPLOY** for Botnet. (M)
6. **Combat UI completeness**: slice picker, direction picker, odds display, inspect
   tooltips, migration telegraph, pass-by-pass playback. (M)
7. **Menus and platform**: title, pause, options (display/audio/keys/language), save
   slots, confirms, CI + export presets. (M)
8. **Tutorial / onboarding**. (L)
9. **Subtitles + line database + text externalisation** (prerequisite for dialogue and
   localisation). (M)
10. **Raid playout controls and animated threat paths**; freezing/altering threats;
    stationed-operative recall; story/built raids. (M)

### P1 — content volume for 100 hours

11. **Classes**: Ghost, Rigger, Botnet with wheels, Hub Cores (+Rank 2 upgrades), rings,
    exclusive cards, station bonuses; then the four alternatives. (L)
12. **Solace, full size**: 30–40 Sites, cross-links, several Heat objectives, remaining
    enemies/elites, all six story paths written, ~40 events, DISPATCH briefings, raids. (L)
13. **Corporations 2, 3 and 4** — each a new enemy family, boss with phases, Exploit
    flavour, threats, raids, music context, story paths, events. (XL each)
14. **REBEL_CELL**: the profile-driven generator (grid from most-used node types, elites
    from your classes' wheels/Hubs/Daemons, raids from your assets), own ICE ladder,
    DISPATCH reveal and finale; "final final" achievement. (XL)
15. **Card pool to ~60 shared + exclusives**; Firmware to ~18; Daemons to ~24; assets to
    ~8; shop slice catalogue to ~12. (L)
16. **Home-server variants and internal nodes**; skins. (M)
17. **DISPATCH arc**: clue seeding across campaigns, timestamp anomalies, voice drift. (M
    writing + S code)

### P2 — polish, reach and retention

18. Final art passes (portraits, wheels, zine textures, Grid buildings, cinematics). (XL)
19. Composed music + SFX library replacing the generated placeholders. (L)
20. Voice acting and localisation (each language a full re-record). (XL)
21. Achievements, stats/history, daily seeds or challenge runs, run sharing (seed +
    replay is already deterministic). (M)
22. Controller support. (M)
23. Difficulty accessibility: assist options beyond effects (e.g. preview-only mode,
    extra rewind). (S)

---

## 5. Suggested milestone order after M4

| Milestone | Scope | Acceptance sketch |
|---|---|---|
| M5 Systems completion | P0 items 1–6, 10 | Every RuleModifierType has a test; all node types buildable; Botnet drones fight; segment swap at Rank 3; combat UI can play every card in the pool without a mouse. |
| M6 Menus, platform, onboarding | P0 items 7–9 | Title → options → new/continue; CI green on push; export runs on a clean PC; a new player finishes the tutorial run; every line of text is externalised and subtitled. |
| M7 Classes | 11 | Four classes each complete a Solace campaign in tests; alternatives unlockable. |
| M8 Solace complete | 12, 15 (first half), 17 | 30+ Sites validate; six written paths; 40 events; DISPATCH briefings for every Site. |
| M9–M11 Corporations 2–4 | 13, 15 (rest), 16 | Same acceptance as M8 per corporation; ICE 10 reachable on each. |
| M12 REBEL_CELL and finale | 14, 17 | Generator builds a valid Grid/enemy set from any profile; finale plays; "final final" recorded. |
| M13 Art and audio production | 18–20 | Style-guide compliance on every screen with final assets; VO integrated with subtitles. |
| M14 Balance and release | 21–23 + playtest passes | GDD 11.8 pacing hit within ±20% on ICE 5; 100-hour path validated by telemetry from playtests. |

---

## 6. Open questions raised by this analysis

- Confirm the **ICE progression rule** (unlock *n + 3* per win) and the **4 + 1
  corporation** count; both set the content budget.
- Should **Reclaim** and **Heat objective** netruns also count toward Rank?
- **Twin Pointer** and player-side drones change the pointer rule for the operative; do
  enemy attacks hit every player pointer too (yes by the GDD's symmetric wording)?
- The GDD leaves **corporations 2–4 unnamed**; their enemy families, Exploit flavours and
  raid themes are needed before M9.
- **Voice budget**: ≈500 lines at launch, +270 per corporation, ×languages; decide the
  languages early because each is a full re-record.
