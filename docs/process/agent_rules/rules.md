# Area: rules (deterministic core, state, resolvers, save, content)

Owns: `scripts/core/`, `scripts/state/`, `scripts/data/` (minimal; every schema change gets a
`tools/schema_smoke_checks.gd` check and a DECISIONS entry), `content/`, the rule tests
(`test_wheel_math`, `test_preview`, `test_rewind`, `test_replay`, `test_rng_service`,
`test_raid_resolver`, `test_map_generator`, `test_save_service`, `test_cards`, `test_heat_*`).
Reference: GDD (source of truth), TECH_SPEC 4–8, DECISIONS "Locked design decisions" and the
designer rulings by date (grep).
Rules specific here: no Node, scene, autoload or `SignalBus` reference in core; every input that can
vary is a parameter; RNG streams by name from `RngService`; every rule change comes with a test
that shows preview == result and that a seeded replay still matches; ties by content id then node
id; a number that tunes behaviour goes in `content/config/campaign_config.tres` with a
`CampaignConfigData` field, never inline. Save compatibility is not required (ruling 2026-10-05)
but say in the report when a save format changes.
Mechanics the GDD lacks are not built: log them under "Open questions for the designer".
