# REBEL_CELL — Gap Analysis and Horizontal Slice Plan

Target set by the designer: **a complete game — all bosses, operatives, story, dialog,
menus — that an average player spends about 100 hours on to reach full content.**

The designer's process (2026-09-24): fix every vertical-slice gap, rerun this analysis,
repeat until the vertical section comes up clean; then run the same loop over the
horizontal slices. Every decision is made by the implementer and logged in
`DECISIONS.md`. This file is rewritten on each pass; the pass log keeps history.

## Pass log

| Pass | Date | Vertical gaps found | Result |
|---|---|---|---|
| 1 | 2026-09-24 | 48 across combat, netrun, campaign, narrative, menus, art | Fixed in vertical batches 1–4 (commits 3295d43 … 102f1e0) |
| 2 | 2026-09-24 | 5 (V1–V5) plus 4 found by the balance simulation (home repair, raid frequency, patrol soft-lock, one-shot tier damage) and 1 display bug | Fixed in vertical batch 5 |
| 3 | 2026-09-24 | **0** | Vertical slice clean. Horizontal loop starts (§4). |
| H1 | 2026-09-24 | 16 after M6-M12 (Solace-only win text, speaker, music, DJ, ICE picker and records; codex spoilers; rescue; untested cores and home servers; built-in ICE Locks ignored in raids; stale docs) | Fixed in horizontal batch H1 |
| H2 | 2026-09-24 | 11 (5 P1: raid names and warning keys per corporation, event speakers, shared text naming Solace, untested H1 rules; 6 P2) | Fixed in horizontal batch H2 |
| H3 | 2026-09-24 | 6 (lost-raid names, REBEL_CELL elite pool leak, pad-only focus, untested config numbers, stale doc, Mirror numbers in code) | Fixed in horizontal batch H3 |
| H4 | 2026-09-24 | 6 (focus lost after a card play, Tab swallowed by focus, modals without focus, ICE unreachable by pad, auto-focus preview, docs/tests) | Fixed in horizontal batch H4 |
| H5 | 2026-09-24 | 4 (keyboard actions replaced the End Turn preview, dialogs dropped focus, Esc in the code field, input-level tests) | Fixed in horizontal batch H5 |
| H6 | 2026-09-24 | 6 (reward, Modem, corporation picker and lower Grid rows unreachable by D-pad; dead reward hotkeys; SEND IT left; assist label numbers) | Fixed in horizontal batch H6 |
| H7 | 2026-09-24 | 3 + tests (title Options sections, reference notes unscrollable by pad, netrun combat linked too early) | Fixed in horizontal batch H7 |
| H8 | 2026-09-24 | 1 + docs/test (reference notes still not pad-scrollable; H7 claim corrected) | Fixed in horizontal batch H8 |
| H9 | 2026-09-24 | 1 + doc (HQ panels ran off the 1280 screen once many unlocks and classes existed; stale test count) | Fixed in horizontal batch H9 |
| H10 | 2026-09-24 | 1 + follow-up (mid-run raid screen ran off the 1280 screen; netrun combat entry left focus on Settings) | Fixed in horizontal batch H10 |
| H11 | 2026-09-24 | 10 (stationed operatives could run and dead ones kept posts, empty-roster stall, text-scale overflow, Heat previews unscaled, home repair ignored ICE 13, boosts skipped special runs, relay shared only the Breaker bonus, magic numbers, stale TECH_SPEC, stale counts) | Fixed in horizontal batch H11 |
| H12 | 2026-09-24 | 7 (profile per slot, final Rack rewards unclaimable, patrol Seized mid-run re-extracted its Exploit, raid setup / end / title overflow, Daemon and raid magic numbers, Twin Pointer Miss and Cold Exit, Racks stat estimated) | Fixed in horizontal batch H12 |

### Pass 3 (vertical) — clean

Re-checked every GDD section against the code and the simulator after batch 5:
every rule has a code path and a test (355 tests), every screen follows the three-worlds
rule, the Grid and netrun maps are interactive, and a bot completes ICE 0 and ICE 5
campaigns within GDD 11.8 pacing (see DECISIONS.md, batch 5). What remains outside code
is listed under "Out of reach for code" in §2 and needs people (art, music, voice,
translation, a human performance run and playtests).

---

## 1. Where the project stands (horizontal pass 1, after M12)

| Layer | Built |
|---|---|
| Combat | Full effect language, preview, rewind, replay, statuses incl. PARASITE, Firmware, Daemons, ring segments, drones, boss phases, ICE/Heat modifiers, freeze cooldown, assist free nudges |
| Classes | Breaker, Ghost, Rigger, Botnet + Wrecker, Phantom, Overclocker, Hivemind; cores and Mk2 cores, rings, two exclusives each, station bonuses, barks, unlocks |
| Corporations | Solace, Meridian, Halcyon, Orbital (32 Sites, 6 enemies, 2 elites, mini-boss, phased boss, 3 Exploits, 6 story paths, own raids, voice, colour, raid music) and REBEL_CELL built from the profile |
| Campaign | Corporation and class selection, per-corporation ICE ladders and records, 7 node types, 5 home servers, raids with station bonuses and built-in holds, assist mode, share codes, daily run |
| Content | 60 shared cards, 18 Firmware, 24 Daemons, 8 assets, 12 shop slices, events: Solace 40, others 28 rollable each |
| Tooling | Balance simulator per class and corporation drafting by measured value; content generators in `tools/content_gen/` |

Tests: 480 passing at H12; schema smoke test and content validation green.

---

## 2. Gaps in the vertical slice (pass 2)

| # | Gap | Sev | Notes |
|---|---|---|---|
| V1 | `CampaignRules.launch_error` and `RunManager.launch_error` gate Rank with the default class, not the operative's class | A (latent bug) | Wrong the moment a second class exists. |
| V2 | Clicking a Site on the Grid view does nothing (`site_clicked` has no listener) | B | The text list works; the map should select and act. |
| V3 | Netrun reward, event, shop and end panels are plain button lists | B | STYLE_GUIDE: "anything the Cell touches gets zined"; cards should be stickers everywhere. |
| V4 | No automated check of GDD 11.8 pacing (runs to win, Heat peak) | B | Needed before balance can be discussed; a seeded bot campaign is enough. |
| V5 | `MILESTONES.md` stops at M4; the vertical-fix work has no acceptance record | C | Add M5 "Vertical completion". |

**Out of reach for code (needs people; tracked, not counted as open):** final art
(portraits, holograms, Grid buildings, zine textures), composed music and recorded SFX,
voice recording, translations into other languages, the 1080p mid-range PC performance
run (the fps counter is in place), human playtests.

---

## 3. What "100 hours to full content" implies (decided)

GDD 11.8: average campaign ≈ 6 h 35 m, fast ≈ 2 h 15 m.

| Lever | Decision (DECISIONS.md) |
|---|---|
| Corporations | 4 + REBEL_CELL: Solace Biosystems, Meridian Freight Systems, Halcyon Civic, Orbital Commons |
| ICE progression | A win at ICE *n* unlocks up to *n + 3* on that corporation; any corporation starts at global best − 5; fresh profiles pick 0–3 |
| Classes | Breaker, Ghost, Rigger, Botnet + one alternative each |
| Content per corporation | 30–40 Sites, 6 normal + 2 elite + 1 mini-boss + 1 boss, 3 Exploits, 6 story paths, ~30 rollable events (own + shared; Solace has 40), 8 raid templates, own voice sets |
| Pools | ~60 shared cards + 2 exclusives per class, ~18 Firmware, ~24 Daemons, ~8 assets |

≈ 19 campaigns to full content ≈ 120 h average / 45 h fast.

---

## 4. Horizontal slices, prioritised

P0 = systems the finished game needs; P1 = content volume for 100 hours; P2 = polish.

### P0
1. ~~**Recruitment by class** and the class unlock purchase (80 Schematics); the roster
   chooses among unlocked classes.~~ Done in M6.
2. ~~**Botnet drones persisting between combats** in a run (Hub passive).~~ Done in M6.
3. ~~**Corporation selection** at campaign start (profile-unlocked corporations).~~ Done in M8.
4. ~~**Balance simulation** grows into a tuning tool (per ICE, per class, per corporation).~~
   Done: `class=<id>` (M6), `corp=<id>` (M8), measured drafting (M7).

### P1
5. ~~**Classes**: Ghost, Rigger, Botnet (wheels, Hub Cores + Mk2, rings, exclusive cards,
   station bonuses, barks), then four alternatives.~~ Done in M6.
6. ~~**Pools**: shared cards to ~60, Firmware to ~18, Daemons to ~24, assets to ~8, shop
   slices to ~12.~~ Done in M7.
7. ~~**Solace depth**: events to ~40.~~ Done in M7.
8. ~~**Meridian Freight Systems** (done in M8), **Halcyon Civic** (done in M9), **Orbital Commons**~~ (done in M10): grid, enemy
   family, mini-boss, boss with phases, Exploits, threats, raids, story paths, events,
   voice sets, music context, corporation colour.
9. ~~**REBEL_CELL**: generator from the profile, own ICE ladder, DISPATCH reveal, finale,
   "final final".~~ Done in M11.
10. ~~**More home-server variants**~~ (done in M12) and skins (deferred to art, M13).

### P2
11. ~~Controller support.~~ 12. ~~Daily seed / challenge runs and replay sharing.~~
13. ~~Assist options~~ (done in M12: extra free nudge and HP; previews are always on). 14. Art, audio, voice and translation integration
as assets arrive.

---

## 5. Milestones after M4

| Milestone | Scope |
|---|---|
| M5 Vertical completion | Passes 1–2 (§2) |
| M6 Class roster | P0 1–2, P1 5 |
| M7 Pools and Solace depth | P1 6–7 |
| M8–M10 Corporations 2–4 | P0 3, P1 8 |
| M11 REBEL_CELL | P1 9 |
| M12 Polish and reach | P1 10, P2 |
| M13 Art/audio/voice integration, M14 balance and release | Needs people |
