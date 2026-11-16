# Glyph / unit-picture baseline (designer ruling 8, 2026-11-16)

"We made a pass at this a long time ago, lets use those as a baseline and then discuss any new or ones that need
changes." The old pass = round 17 LOCKED glyphs, round 21-22 class beacons / colours and v4 unit icons, round 38-39
portrait busts. What Campaign B needs = the classes, units, devices and weapons in `content/b/` and the raid look
(`content/config/raid_look.tres`, `scripts/ui/raid/look/`) at port-campaign-b d44936b37. Solace only (no other corp's
icon is listed or shown).

- `baseline_sheet.jpg`: KEEP, no review needed.
- `review_sheet.jpg`: NEW / CHANGE / CONFIRM, for the designer (one line why each).
- `src/make_sheets.py`: `python src/make_sheets.py [game checkout]` rebuilds both from the shipped assets and the set 8 draft.

## KEEP (old pass, used as is)
| Need | Asset | Source |
|---|---|---|
| Corp unit, fast / flying / heavy / special (Solace) | `assets/raid/icons/solace_<type>_<status>_hp<n>.png` | round 22 v4 icons (bible 4.8; designer ruling 2, 2026-11-15) |
| Unit status rings: held (frozen), slowed; health drain | same set, `frozen` / `slowed`, hp000-100 | round 22 |
| Core / Safehouse health | `picto_hp` | round 17 LOCKED |
| Holds (route held at a wall) | `placeholder_shield` | round 17 LOCKED |
| Reroll, undo, shop locked, resolving, Heat | `picto_again`, `picto_spin_ccw`, `state_locked`, `picto_spin`, `placeholder_burn` | round 17 LOCKED |
| Device BARRICADE | `picto_block` | round 17 LOCKED |
| Device MINE | `placeholder_bomb` | round 17 LOCKED |

## REVIEW (new or changed)
| # | Need | Now | Status | Why |
|---|---|---|---|---|
| 1 | Class GUNNER: glyph / beacon | `picto_target` / Breaker beacon | CHANGE | beacon is the Breaker's emblem (crowbar) baked pink; Gunner's sticker is orange |
| 1 | Class HACKER | `placeholder_key` / Ghost beacon | CHANGE (small) | Ghost's emblem, cyan vs Hacker blue |
| 1 | Class FIXER | `placeholder_vault` / Rigger beacon | CONFIRM | colours match; vault is art's pick (never ruled) |
| 1 | Class SAPPER | `placeholder_bomb` / Wrecker beacon | CHANGE | glyph = MINE's and BOMBARD's; beacon orange vs Sapper violet |
| 2 | Pinned operative mark | none (station in red pencil text) | NEW, empty | ruling 6 names the state "pinned"; nothing marks it |
| 3 | 10 unit kinds | 4 v4 type icons (art's map) | CONFIRM / CHANGE | Trooper, Riot, Sniper, Heavy share one icon; Mortar / Wrecker, Bike / Flanker, Drone / EMP Drone share |
| 4 | Device SENTRY | `raid_sentry` | NEW (draft) | set 7 proposal, in game, never reviewed |
| 4 | Devices TAR, SHOCK fence, GATE | no glyph; set 8 badge marks in `raid_v3/src/raid_d.py` | NEW (draft) | v42 devices; TAR and SHOCK weak at 1:1 (set 8 notes) |
| 4 | Devices BEACON, DECOY, Repair DRONE, LURE, Relay MAST | none | NEW, empty | in content/b/device; no glyph anywhere |
| 5 | Weapons SMG, RAIL, SHOTGUN, JAMMER | `raid_smg` etc. | NEW (draft) | set 7 proposals, in game, never reviewed |
| 5 | 21 other weapons | abbreviation on the gear tag | NEW, empty | BARRIER .. WIRE (content/b/weapon) |
| 6 | Raid strip / order: kills, leak, place, EVACUATE, Tab | `raid_kills` .. `raid_tab` | NEW (draft) | set 7 proposals, in game |
| 7 | Chain tokens HELD / BOMBARD / BLOCK / SNIPE | shield / bomb / block / rail | CHANGE | three reuse a device or weapon glyph |
| 8 | Class pictures (class pick, HQ roster, recruit) | none (text) | NEW | old-pass busts are the 8 netrun classes in their colours; reuse the mapped four re-tinted, or none? |

## Not in Campaign B screens (listed so nothing is missed)
- Portrait busts / prints (`assets/portraits/`), raid asset cards (`assets/raid/cards/`), the route operative token,
  the other four netrun-class beacons: used by the netrun / HQ (A) screens only.
- Unit roles (`content/b/role/`, 10): `raid_look.tres` `role_glyphs` is empty and no B screen draws a role mark.
- Fight statuses (`content/b/status/`, 25): outside this pass (the fight's Deface look).
- Other corporations' unit icons ship in `assets/raid/icons/` but are never shown (`unit_corp = solace`).
