# Character art briefs (art pass W5)

Painted-final briefs for every character family (ART_BIBLE §7.1, §7.2; STYLE_GUIDE 7). The game draws procedural stand-ins today (`PortraitArt`, `Polaroid`, `Hologram`); final art drops in without code changes (`ClassData.portrait`, `Polaroid.portrait`, `EnemyData.art`).

Pixel-art concepts (Q6: script-drawn, never shipped): `docs/art_review/W5/concepts/` (`tools/art_concepts/character_concepts.py`).

## Operatives: 1:1, 1024 px master, four expressions
| Class | Id | Accent | Brief |
|---|---|---|---|
| Breaker | `breaker` | #FF3DA8 | [class_breaker.md](class_breaker.md) |
| Wrecker | `wrecker` | #FF7A1A | [class_wrecker.md](class_wrecker.md) |
| Ghost | `ghost` | #9FE8FF | [class_ghost.md](class_ghost.md) |
| Phantom | `phantom` | #C8B6FF | [class_phantom.md](class_phantom.md) |
| Rigger | `rigger` | #FFD24D | [class_rigger.md](class_rigger.md) |
| Overclocker | `overclocker` | #FF4FD8 | [class_overclocker.md](class_overclocker.md) |
| Botnet | `botnet` | #7BE07B | [class_botnet.md](class_botnet.md) |
| Hivemind | `hivemind` | #B04DFF | [class_hivemind.md](class_hivemind.md) |

## Enemies (768 px busts) and bosses (1024 px holograms), per corporation
| Corp | Hue | Agents | Machines | Boss |
|---|---|---|---|---|
| Solace Biosystems | #3DFF8B | [agents](enemy_solace_agents.md) | [machines](enemy_solace_machines.md) | [Renewal Engine (Auto-Renew)](boss_renewal_engine.md) |
| Meridian Freight Systems | #FF8C1A | [agents](enemy_meridian_agents.md) | [machines](enemy_meridian_machines.md) | [The Manifest (Priority Routing)](boss_the_manifest.md) |
| Halcyon Civic | #8C7BFF | [agents](enemy_halcyon_agents.md) | [machines](enemy_halcyon_machines.md) | [The Civic Core (Emergency Powers)](boss_civic_core.md) |
| Orbital Commons | #7FA8FF | [agents](enemy_orbital_agents.md) | [machines](enemy_orbital_machines.md) | [The Commons Array (Station Keeping)](boss_commons_array.md) |
| REBEL_CELL (the handler AI) | #E8141E | [agents](enemy_rebel_cell_agents.md) | [machines](enemy_rebel_cell_machines.md) | [DISPATCH (Root Access)](boss_dispatch_core.md) |

## Shared rules
- Strong value contrast: figure near black, the accent or corp hue on the rim, eyes and props only.
- Every figure reads from its silhouette alone (tested for the procedural stand-ins: no two classes share a silhouette).
- Operatives: four expressions (neutral, hurt, triumphant, flatlined); per-operative variation (hair, visor, tint) stays inside the class accent.
- Enemies: the corp's hue **and** pattern, always together.
- No IP look-alikes (ART_BIBLE §1).

## Not covered here
- `botnet_drone`, `seed_drone`: the Cell's own summoned drones (no corporation); they take the summoning class's accent and belong with the Botnet brief's drone halo.
- `rc_template_elite`, `rc_template_elite_b` ("Mirror"): REBEL_CELL copies of an operative; they reuse the operative class portraits through the REBEL_CELL scan-glitch hologram, so they need no art of their own.
