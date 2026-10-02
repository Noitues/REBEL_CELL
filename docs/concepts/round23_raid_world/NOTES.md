# Round 23: raid world (slow field under the units, repair on the locked node health)

Locked from round 22: vehicle icons v4, the close and far health views, the status pips, the Rigger beacon, and the slow field proposal.

## Files
| File | What |
|---|---|
| `bonus_slow_v3.gif` | The slow / freeze field is now a GROUND layer. It draws only where the street and sidewalk are visible (world z < 0.45 m from the position pass), so vehicles, buildings and the beacon stay on top. **Base:** slow blue dashed rings drift inward. **Levelled:** ice crystals grow inward along the street with a light-blue translucent fill. Only the frozen unit itself gets an ice skin and the frozen glyph, on the unit on purpose. |
| `bonus_repair_v3.gif` | Repair now uses the raid UI's locked node health read (`round21_raid_ui` node_health / `round22_raid_ui` node_status_key). The diamond's outline and icon stay static; the middle lit fill and track are the health. Repair makes that fill rise **south → north** (the reverse of the north → south drain). **Base (hovered):** the diegetic number and its 10-segment bar count up with the fill (6/20 → 20/20), with a cursor. **Levelled:** the adjacent CORE refills too. The liked field-repair effect is kept: rising "+" marks, vertical streaks and green sparks spiralling into the socket. The round 22 stacked-cell column is gone. |
| `contact_sheet.jpg`, `scripts/` | |

## Godot build notes
- **Slow field:**
  - A Decal (or a ground-plane shader on the street mesh) in the render order before the units, so the depth test hides it under vehicles.
  - Uniforms: radius, dash phase, inward ring phase, freeze 0..1.
  - The unit's ice skin is a separate overlay on the unit (shader param `frozen` on the vehicle material).
- **Repair:** drive the same `health` uniform as damage; the socket shader is unchanged (`netdecal21.health_pad` is the prototype).
  - Tween `health` upward over the repair beat (~0.7 s, smoothstep).
  - The hover Label counts the integer with the tween.
  - The '+' / streak / spark particles are a GPUParticles3D burst at the socket.

## Rebuild
1. `python scripts/emblems20.py`
2. `python scripts/run_blender21.py bonus_nh`
3. `python scripts/screens23.py`

Scripts were copied from round 22, plus the raid UI's `netdecal20.py` / `netdecal21.py` (health read), copied unedited from `round22_raid_ui/scripts`. Seeded throughout.
