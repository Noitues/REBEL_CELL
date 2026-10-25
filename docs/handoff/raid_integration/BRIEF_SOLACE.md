# Solace × raid grid: merge ideas brief (designer 2026-10-25)

**Designer ask:** "We will need ideas for how to merge the main ideas, things like Solace campaign having the campaign
infection timer mechanic, and how to adapt the solace campaign structure to be more like our raid grid."

**Context:**
- docs/design/raid_concepts/INTEGRATION_PLAN.md (commit e5ead05b) is the reintegration plan. Its biggest risk: the
  Solace City Grid is a star of about 10 spokes from HOME, so on real geometry the corp's beams may rarely overlap,
  and placement stops being a choice.
- The lab's raid board, a 4×3 grid of routes and streets between two HQs, scored 39/50. Its rules are in
  D:/rc_tmp/raid_design_lab/integration/LAB_AND_CITY_INVENTORY.md and docs/handoff/raid_lab_l8/L14_RULES.md.

**Main as of db350783 (2026-10-22):**
- Our branch is docs and tools/ only, and it merges with one doc conflict.
- Main's recent work is mostly look (the Solace "Bloom A Necrosis" visuals). The rules are unchanged since the
  merge-base.
- Read the game files from this worktree: its scripts/ and content/ equal the merge-base, and main changed only
  scripts/data/campaign_config_data.gd (2 lines) and scripts/ui/hq_scene.gd (a trim). Check DECISIONS.md entries
  dated 2026-10-19 to 2026-10-22 on main with `git show main:docs/DECISIONS.md`. The file is very large: grep it.

**Study before proposing:**
- **Solace infection and bloom:**
  - scripts/core/solace_raid_rules.gd;
  - scripts/core/bloom_rules.gd (bands DORMANT / CREEPING / CLOSE / CATCHING / CAUGHT);
  - scripts/state/bloom_state.gd;
  - netrun_session.gd bloom_* (the virus front trailing the operative, and Doses);
  - the bloom / infection config in campaign_config_data.gd;
  - DECISIONS S1 ("campaign figure that may diminish to zero") and every Bloom ruling.
- **The Solace campaign structure:**
  - content/corporations/solace.tres (the embedded city_grid: Sites, tiers T1–T3, links, locked_links,
    objectives, exploits);
  - solace_hq_graph.gd (the Genome Core);
  - exploit_building_graph.gd;
  - CampaignRules claim / launchable_sites / patrol / raids for Solace;
  - GDD sections 3, 4.1, 4.3, 7 and 11.7.

**Write docs/design/raid_concepts/SOLACE_MERGE_IDEAS.md** in US English, about 300–500 lines:
1. **How Solace works today**, in half a page: the infection timer, bloom, raids, the grid shape, win and lose.
   Include the exact numbers and paths.
2. **Three or four distinct merge concepts.** Each concept covers:
   - **The infection timer:** how it drives or replaces the lab's raid cadence, Heat bands and decay. For example,
     the bloom front as the corp's beams, infection as the DECAY clock, Doses as responses, wounds as infected cards.
   - **The grid structure:** how the Solace grid is reshaped toward the lab board, for example spokes regrouped into
     3 routes between HOME and the Genome Core, cross-links as streets, or tiers as columns. Include an ASCII sketch
     of the grid.
   - **One raid turn and one campaign arc**, walked through.
   - **What it keeps** from the lab's praised strengths (forecast, persistence chain, deck tie-in) and what it fixes
     from the lab's caps: raids that lock at PLAN, and responses that differ only in tier.
   - **Content and code changes,** with paths, and an estimate of size.
   - **Risks,** and a cheap measurement that could test the concept. The lab's Python oracle (tools/raid_concepts)
     can simulate; say what to measure and its gate.
3. **A comparison table** of the concepts against the vision fit: the seamless city, netruns as captures, the corp
   hacking back, the infection identity, build cost, and expected critic axes.
4. **A recommendation** with the reason, plus the designer decisions it needs, each with a default.

**Rules:**
- Do not edit GDD.md, DECISIONS.md, scripts/ or content/.
- Ideas must fit the GDD pillars, Solace first, at text 1.0 with mouse and keyboard.
- Flag anything that invents a new system as such.
