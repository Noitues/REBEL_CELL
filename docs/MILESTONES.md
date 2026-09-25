# REBEL_CELL — Vertical Slice Milestones

Goal: prove the core loop is fun with one class (Breaker), one corporation (Solace) and a
10-Site City Grid before building more content. Work one milestone at a time. A milestone
is done only when **every** acceptance criterion passes and all tests are green headless.

Placeholder art is expected until M4 (see `STYLE_GUIDE.md` §7).

---

## M0 — Foundation
**Build**
- Project structure per `TECH_SPEC.md` §2; move provided schemas to `scripts/data/`.
- Install GUT 9.x; add one passing test per test folder.
- Autoloads: `SignalBus`, `ContentRegistry`, `RngService`, `SaveService` (skeleton),
  `RunManager` (skeleton).
- `content/config/campaign_config.tres` with every value from GDD §11 and the config
  groups in `CampaignConfigData`.
- `tools/validate_content.gd`: loads all content and prints every `validate()` error.
- Input map for GDD §9.5 bindings.

**Acceptance**
- [ ] `godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://tests -gexit` exits 0.
- [ ] `tools/schema_smoke_test.gd` and `tools/validate_content.gd` exit 0.
- [ ] `RngService` streams: same seed → same sequences; streams are independent (test).
- [ ] `ContentRegistry` resolves every content id; duplicate ids fail validation.

## M1 — Combat Core
**Build**
- `wheel_math`, state classes, `CombatResolver`, turn state machine, effect interpreter
  (effect types used by Appendix A), preview, rewind with checkpoints.
- Content: Breaker (wheel, Hub Core, starting deck), slice types, Collections Agent (with
  satellite), Compliance Officer (Hub resistance), Dosage Dispenser (DOSE).
- A functional (ugly is fine) combat scene: two wheels, hand, preview readouts, targeting,
  nudge, end turn, rewind, log.

**Acceptance**
- [ ] Wheel math matches GDD §2.3 for all 30 ticks, flipped and unflipped (table test).
- [ ] Precision tiers: offsets 0/±1/±2 → Perfect/Good/Partial; no Miss tier exists.
- [ ] Resistance absorbs nudges and spins tick-for-tick; Flip and Respin are blocked while
      resistance > 0; passive resistance restores each player turn; Hub Breach disables
      Hub resistance for one turn.
- [ ] Resolution order: defensive → offensive → statuses, simultaneous on both sides.
- [ ] Pointer rule and satellite bodyguard work; Pierce ignores satellites and block.
- [ ] Breaker Perfect hook resolves the slice twice; Inner Ring ×2/Pierce apply.
- [ ] CORRUPTED, OVERCLOCKED, ENCRYPTED behave per GDD §2.9.
- [ ] **Preview equals actual** for 500 random seeded turns.
- [ ] **Rewind** restores exactly and cannot cross a checkpoint; checkpoints survive
      save/load.
- [ ] **Determinism:** replaying a recorded fight from its seed gives an identical state
      hash.
- [ ] A full fight against each of the three enemies is playable in the scene.

## M2 — Netrun Loop
**Build**
- Map generator (TECH_SPEC §6), map scene, node types, Terminal events (5 placeholder
  events), Modem shop, rewards (cards 1-of-3, elite Firmware 1-of-2, Rack Daemon 1-of-3,
  asset drops), Heat per node, Server Rack banking, death and completion flow.
- Content: all Appendix A.2 cards, A.3 normal + elite enemies, A.4 Firmware & Daemons,
  A.5 assets.
- Run save/resume.

**Acceptance**
- [ ] 1,000 seeds generate valid maps (reachability + guarantees); same seed = same map.
- [ ] Banking: Schematics and assets bank on Rack capture; death loses only unbanked items;
      death adds 10 + tier Heat.
- [ ] Completion: Cycles convert 10:1; operative keeps deck/Firmware/Daemons; Rank +1.
- [ ] Every card, Firmware and Daemon in the slice has at least one unit test.
- [ ] Quit mid-run (including mid-combat) and resume to the identical state.
- [ ] A Tier 1 netrun is completable in roughly 12–18 minutes of play.

## M3 — Campaign & Raids
**Build**
- HQ scene (roster, recruit, station, spend), City Grid scene with the A.6 Grid, Site
  selection with rank gating, claiming and 3 node types (Relay, Firewall Relay,
  Safehouse), Heat meter with threshold events/modifiers, Armory, raid setup +
  projection + playout, node loss states, repair, Rank 1 Inner Ring, Exploits (3) with
  placeholder story beats, Renewal Engine boss with phases, win/loss flow.

**Acceptance**
- [ ] Threshold events fire once only; modifiers switch off when Heat drops below.
- [ ] Raid projection equals the real raid result (golden tests for 5 layouts).
- [ ] Disabled/Seized rules, cascade (50%), step cap and home-server loss per GDD §7.
- [ ] Deployed assets persist and can be repositioned; Armory cap 6 enforced.
- [ ] Beating the Renewal Engine with 3 Exploits wins the campaign; home integrity 0 loses
      it; profile records update.
- [ ] Campaign save/load round-trip is exact.

## M4 — Look, Feel & Accessibility
**Build**
- Three-worlds visual baseline per `STYLE_GUIDE.md`: cyberdeck HQ, wireframe Grid and
  arena (glow shader, grid floor), zine UI kit (cards, HUD, notes, stamps), jack-in
  transition, precision feedback, Heat feedback, ratchet/tick audio and placeholder
  music by context, accessibility settings.

**Acceptance**
- [ ] Combat, Grid and HQ screens match the approved mockups' layout and style rules.
- [ ] Reduce-effects toggle disables scanlines, flicker and chromatic effects everywhere.
- [ ] Flash limiter: never more than 3 flashes per second (automated check on the event
      stream).
- [ ] Every slice type and status is distinguishable without colour.
- [ ] Full keyboard play is possible for combat.
- [ ] 60 fps at 1080p on a mid-range PC.

---

## M5 — Vertical Completion (added 2026-09-24)

The designer asked for every vertical-slice gap to be fixed and the project analysis rerun
until clean (`GAP_ANALYSIS.md`, pass log). Decisions are the implementer's, logged in
`DECISIONS.md`.

**Acceptance**
- [x] Every `RuleModifierType` in the ICE ladder and the Heat thresholds changes play, each
      with a test (combat, netrun, campaign, raids).
- [x] Every effect type and slice type resolves (no "not implemented" path is reachable).
- [x] All seven node types, node upgrades, Profile unlocks, a second home-server variant,
      netrun boosts, and every raid trigger source exist and are tested.
- [x] The combat UI plays every card in the pool from the keyboard (slice and direction
      pickers, respin, inspect, odds for random effects).
- [x] Solace has 30-40 Sites, six written story paths, DISPATCH briefings for every Site,
      subtitles, a codex and a text export for translation.
- [x] Title, save slots, pause, options (display, audio, key rebinding, language),
      tutorial, achievements, CI and export presets.
- [x] A seeded bot campaign wins at ICE 0 and ICE 5 within ±20% of GDD 11.8 pacing
      (`tools/simulate_campaign.gd`).
- [x] Tests, schema smoke test and content validation green.

## M6 — Class Roster (added 2026-09-24, horizontal loop)

Ghost, Rigger and Botnet from GDD 5.2 plus one alternative per class (GDD 3.4), with
recruitment gated by Profile unlocks. Decisions are the implementer's, logged in
`DECISIONS.md`.

**Acceptance**
- [x] Ghost, Rigger and Botnet: wheel, Hub Core and Mk2, Rank 1 ring, Rank 3 options,
      starting deck, two exclusive cards, station bonus and barks.
- [x] Four alternatives (Wrecker, Phantom, Overclocker, Hivemind): same deck, new core.
- [x] Recruitment by class; class unlocks (80 Schematics, alternatives 60); the new
      campaign picks the starting crew's class.
- [x] Botnet drones persist between the fights of a netrun and survive save/load.
- [x] PARASITE status; station hold, regen and turrets in raids.
- [x] A seeded bot campaign wins at ICE 0 with every class (`tools/simulate_campaign.gd
      -- 8 0 class=<id>`).
- [x] Tests, schema smoke test and content validation green.

## M7 — Pools and Solace Depth (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Shared cards 60, Firmware 18, Daemons 24, defense assets 8, shop slices 12.
- [x] Solace netruns can roll 40 Terminal events; every choice resolves.
- [x] Every shared card plays with preview == result; new Firmware, Daemon hooks and
      assets are tested.
- [x] Seeded bot campaigns still win at ICE 0 and ICE 5.
- [x] Tests, schema smoke test and content validation green.

## M8 — Corporation Selection and Meridian Freight Systems (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Corporations are Profile unlocks; the new-campaign panel picks the target and its ICE
      ladder; a locked corporation cannot be started.
- [x] Meridian Freight Systems: 32-Site Grid, 6 enemies, 2 elites, mini-boss, phased boss,
      3 Exploits, threats and 8 raids, 6 story paths, 20 events, DISPATCH briefings and
      corporate voice, colour.
- [x] Heat-threshold raids resolve to the corporation's own raid.
- [x] Seeded bot campaigns against Meridian win at ICE 0 (every base class) and ICE 5.
- [x] Tests, schema smoke test and content validation green.

## M9 — Halcyon Civic (added 2026-09-24, horizontal loop)

**Acceptance**
- [x] Halcyon Civic: 32-Site Grid, 6 enemies, 2 elites, mini-boss, phased boss, Exploits,
      threats and 8 raids, 6 story paths, 20 events, briefings, corporate voice, colour.
- [x] Citations (PARASITE on your wheel) and the Civic Core hub are tested.
- [x] Seeded bot campaigns against Halcyon win at ICE 0 and ICE 5.
- [x] Tests, schema smoke test and content validation green.
