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

### Pass 3 (vertical) — clean

Re-checked every GDD section against the code and the simulator after batch 5:
every rule has a code path and a test (355 tests), every screen follows the three-worlds
rule, the Grid and netrun maps are interactive, and a bot completes ICE 0 and ICE 5
campaigns within GDD 11.8 pacing (see DECISIONS.md, batch 5). What remains outside code
is listed under "Out of reach for code" in §2 and needs people (art, music, voice,
translation, a human performance run and playtests).

---

## 1. Where the project stands (pass 2)

| Layer | Built |
|---|---|
| Combat | Wheel math, resolver, full effect language (no unsupported effect or slice type left), preview, rewind, replay, statuses, Firmware, 10 Daemons, 7 ring segments + Rank 3 swap, player drones, boss phases incl. telegraphed MIGRATE and wheel overrides, every ICE/Heat combat modifier, RAM respin |
| Netrun | Map generator, wireframe map view, rewards incl. Router Firmware, Modem with ICE prices, 19 Terminal events with tier gating, rescue and DISPATCH chain, boosts, Compiler Rack bonus, raid interludes |
| Campaign | 32-Site Solace Grid, 7 node types + upgrades, Profile unlocks, Bunker home variant, ICE picker and progression, every raid trigger source, freezing/altering threats, raid playout with speed/skip, recall from Disabled/Seized |
| Narrative | Six written story paths, 55 DISPATCH lines with voice drift, raid warnings, barks, DJ, subtitle bar, codex, text export pipeline |
| Menus/platform | Title, three save slots, pause menu, five-section options with rebinding, tutorial, achievements, stats, fps counter, autosave marker, CI + export presets |
| Content | 1 class, 1 corporation (32 Sites), 12 enemies + 3 satellites + 2 drones, 26 cards, 6 Firmware, 10 Daemons, 3 assets, 5 threats, 8 raids, 19 events, 4 line sets |

Tests: 346 passing; schema smoke test and content validation green.

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
| Content per corporation | 30–40 Sites, 6 normal + 2 elite + 1 mini-boss + 1 boss, 3 Exploits, 6 story paths, ~40 events, 8 raid templates, own voice sets |
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
4. **Balance simulation** grows into a tuning tool (per ICE, per class). Per class done in M6
   (`class=<id>`); per corporation arrives with corporation selection.

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
