# Raid reintegration design brief (designer request 2026-10-25)

**Designer's target vision (verbatim intent):** "a seamless city we can zoom in and out of, where the city itself is
our hacking path where we decide the hack netruns to gain territory and find exploits against our target. The
corporation fights back by trying to hack back and eliminate us via raids. Netruns are the micro Slay the Spire runs
where we traverse the individual buildings toward our target server. We combat via spinners and cards, gaining
daemons and new slices, slotting firmware upgrades into slices, new cards, and such."

**Task:** write a design document on how the prototyped city raid (tools/raid_lab_city, L8–L17) folds back into the
whole game toward that vision. It is a design document only: no code changes.

## Inputs (verify what you rely on; line references are approximate)
- **D:/rc_tmp/raid_design_lab/integration/LAB_AND_CITY_INVENTORY.md:**
  - the lab's final rules (L14) and view (L17);
  - the best critic score, 39/50; P and C are at their ceiling, D and S are limited by the rules; R15–R17 are open;
  - the 3D city code inventory.
- **Game inventory (from a read-only explorer):**
  - **Campaign:**
    - The City Grid of Sites: scripts/data/city_grid_data.gd, scripts/data/site_data.gd,
      scripts/state/grid_state.gd, scripts/core/campaign_rules.gd, content/corporations/*.tres, and the
      content/city/city_A2.json layout.
    - Heat: scripts/core/heat_rules.gd, with thresholds 25/50/75/100 in campaign_config.tres.
    - Exploits: at least 3 to breach the Central Server (boss_overrides).
    - Operatives stationed on Sites.
    - Solace infection / bloom: solace_raid_rules.gd and bloom_rules.gd.
  - **The REAL raid today:** scripts/core/raid_resolver.gd.
    - A deterministic auto-battle where threats walk the grid.
    - Defense assets are placed at setup (content/assets, 8).
    - Threats (content/threats, 17) and raids (content/raids, 40), with waves scaled by Heat and a 30-step cap.
    - The projection is the same resolve().
    - Outcomes: DOWN / TAKEN / HOLDS / CELL HOLDS / BREACHED (raid_outcome.gd).
    - UI: scripts/ui/hq_scene.gd show_raid and show_raid_playout. GDD section 7.
  - **Raid concepts:**
    - docs/design/raid_concepts/RECOMMENDATION.md (2026-10-22) chose the MANHUNT sweep. The city lab grew out of
      it.
    - The labs in tools/ are not wired to scripts/core.
  - **Netruns:**
    - An abstract 7-layer node map: map_generator.gd, map_v2.gd, netrun_session.gd.
    - Building-scale graphs exist only for the Solace HQ (solace_hq_graph.gd), the Halcyon HQ and the Solace
      exploit buildings (exploit_building_graph.gd).
    - The netrun street view uses the same CityModel.
  - **City and netrun:**
    - They are separate scenes joined by a jack-in / jack-out dive (run_manager.gd go_to_netrun / go_to_hq).
    - city_lod.gd has NETRUN / RAID / GRID bands.
    - docs/art_review/HQ_REDESIGN/PROPOSAL.md: the HQ is the live 3D city at the RAID band, and zooming out reaches
      the GRID band.
    - Route map V3 is waiting on an art concept (DECISIONS 2026-10-15).
  - **Combat:**
    - combat_resolver.gd and wheel_state.gd: 30 ticks, variable slot sizes.
    - Content: 38 slices, 18 firmware, 24 daemons, 71 cards, plus rings.
    - Rewards come through netrun_scene.gd choose_reward.
    - Card upgrades and slice rearranging are MISSING. GDD v0.9 lags behind the content counts.
- **Also read:**
  - docs/GDD.md (the source of truth);
  - docs/TECH_SPEC.md;
  - docs/design/raid_concepts/RULE_BACKLOG.md, RECOMMENDATION.md and SCOREBOARD.md (L14–L17);
  - docs/handoff/raid_lab_l8/L14_RULES.md;
  - GDD section 7 compared with raid_resolver.gd.
- **Constraints:**
  - One corp at a time, Solace first.
  - Scope: text 1.0, mouse and keyboard.
  - The art-pass owns the look, except for the raid lab's own look.

## Output: docs/design/raid_concepts/INTEGRATION_PLAN.md (US English, about 400–700 lines)
1. **The loop in one picture.**
   - The zoom levels: city GRID, district RAID, building NETRUN, combat.
   - The decisions at each level.
   - How state flows between them: territory, exploits, Heat, deck, wounds, HOME integrity, operatives.
   - An ASCII diagram.
2. **A mapping table.** For every lab concept, give its place in the full game (what it replaces, merges with or
   extends, with paths) and a verdict of keep, adapt or drop, with the reason. The lab concepts are: districts,
   routes and streets; HQs; capture; sentries; the deck hand; wounds; sealed beams A and B; the hunter; responses;
   Heat bands; intensity; the between step; score; forecast and tiers.
   - Decide these explicitly:
     - CAPTURE becomes a netrun.
     - Is the dummy deck the real run deck or a raid sub-deck? Justify the choice.
     - Wounds become real curse cards.
     - Intensity becomes netrun choice and Heat.
     - How the lab's 4×3 grid maps onto real City Grid Sites.
     - Is raid_resolver.gd replaced, wrapped, or kept as the projection engine?
3. **GDD conflicts.** Name the exact GDD sections. Write each conflict as a proposed DECISIONS.md open question with
   a recommended default. Do not edit GDD.md or DECISIONS.md.
4. **Exists vs build.** With paths, split into reuse, port and new.
5. **A phased plan.**
   - Milestone-sized slices, each with acceptance criteria and tests.
   - The smallest playable vertical slice comes first, Solace only.
   - Keep the lab's oracle + golden + parity approach when porting into scripts/core: deterministic, RngService
     streams, no magic numbers, every rule tested.
   - Mark which slices suit the Batch API, agents, or Godot capture runs.
6. **Risks and open questions,** each with a recommended default. Cover at least:
   - the time split between raids and netruns;
   - R15–R17 once real cards exist;
   - seamless zoom tech;
   - save migration;
   - the branch base: this branch is about 71 commits ahead of main's merge-base.

Be concrete. Cite paths and GDD section names. Flag gaps instead of inventing systems.
