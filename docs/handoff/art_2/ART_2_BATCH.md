# Group 2 — Combat: ART-2 wheel stack, ART-3 cards and FX, ART-4 HUD (M14 — Art direction v2)

Started 2026-10-05 in parallel with Group 1 (DECISIONS "Designer ruling: groups in parallel, fast checks
only, done within days"). Every agent reads `process/agent_common_rules.txt` first. Source of truth:
`docs/ART_BIBLE.md` §3 (Combat) and §5–6, `docs/art_reference/{wheel,cards_fx,hud}/` (README maps each image
to its lock), plan §4.2 ART-2/3/4. Generator scripts: `art-concepts-r43:docs/concepts/<round>/scripts/`.

**Goal: the fight looks like `docs/art_reference/hud/round41_wheel_stack/combat_typical_v4.*` and
`combat_worst_case_v4.*`** (bible §3.1). Visual impact first; capture windowed next to the references and
iterate. Checks: fast checks + own scripts only (no full suite, no audit until after ART-12).

**Foundations are landing in parallel** (Group 1): 1A palette v2 / faces / theme types, 1B material kit
(CRT panel, vinyl sticker with peel/slap/dissolve, grease pencil, light spill, holo, corp paper, binary bits
emitter, toon/ink), 1C glyph atlas + id → glyph table, 1D city render spike. Until each lands, build on
main and keep the seam small (one place that picks the material / glyph / token), so switching is a small
edit; the orchestrator messages you when each lands, then `git merge main` and switch.

**Rules that must survive** (tests exist for all): preview == result (GDD 2.10); ANIM motion behaviour
(MotionSkip one press, reduce effects = end state, headless never waits, entries in `ui_motion.tres` +
REQUIRED_IDS + lab demo; art restyles motion, never drops an entry); Signal Up / Call Down; tokens only (D's
static lint fails on new literal colours/sizes); layouts at 1.0 / 1.6 / 2.0.

**Presentation rulings built on plan defaults, pending designer confirmation** (plan §3.1):
D15 HUD v4 result chips replace the forecast tags and NEXT plates (the chip **is** the preview; GDD 2.10
must still hold; preview == result tests move to the chip); D16 every card-caused effect stems from the
card's slap and dissolve on the target wheel, never from the hand; D17 boss fight backdrop = the corp HQ,
regular fights at the target Site, fight won → the building's lights turn Cell colours.
Mechanics not approved (G1–G16) are **not** built: FROZEN / LOCKED / BURNING / EMPOWERED states, tiers
beyond I, parasite ring, gates, new slice types stay out.

## Areas (parallel)

### 2A — Wheel stack (ART-2 core; bible §3.2–3.8, §3.10, §3.16, §3.19, §6.2)
Owns `scripts/ui/wheel_view.gd` and new `scripts/ui/wheel/**`, `shaders/wheel/**`.
Refs: `wheel/round13_wheel_details/*` (D4 "Lens & rail"), `wheel/round15_slice_system/*`,
`round16_slice_system/*`, `round17_slice_system/*`, `round34_slice_names/*`, `round17_corp_wheels/*`,
`round18_corp_wheels/*`, `round38–40_hub_inner_ring/*`, `cards_fx/round39_landing_exploits/*`.
1. D4 "Lens & rail" frame for every wheel with phase pips; bezel, telemetry ring, rail, blades, elite
   collar, crests per §3.2.
2. Family C "Screens & Data" slices: CRT screens with white glyphs (1C atlas), program names, value read
   block counter-rotated (§3.4–3.6); tier I rendering only (§3.7).
3. State overlays for the existing statuses only (§3.8, ruling 10: overlay is the status, corner badge only
   for ×N / multiplier tags).
4. Hub cores, Mk2 and enemy hubs, the breach lockdown waterline, the player defeat drain (§3.3).
5. Inner ring bezel and textures extending into the slices, current segments only (§3.10).
6. Corp skins for all five kits and boss phase treatments (§2.4, §3.16).
7. Precision landings Perfect / Good / WEAK (§3.19).
- Accept: worst-case clutter fixture legible at 1.0 and 1.6 (and 2.0); preview == result; wheel draw time
  within budget (windowed profile); captures vs `combat_typical_v4` / `combat_worst_case_v4` and each corp kit.

### 2B — Wheel attachments and the arena (ART-2 rest; bible §3.9, §3.11, §3.13, §3.14, §3.17, §3.21)
Owns new `scripts/ui/wheel/attach/**` (satellites, firmware socket, Daemon rack, preview overlay) and the
combat backdrop node; hooks into `wheel_view.gd` / `combat_scene.gd` are the smallest possible and agreed
through 2A / 2D's seams (report them).
Refs: `wheel/round40_satellites/*`, `round41_wheel_stack/*`, `round34_firmware_daemons/*`,
`round11_combat_target/*`, `city/round31_meridian_combat/*`, `city/round26_hq_targets/*`,
`city/round34_rebel_cell/*`.
1. Satellites as mini-wheels with the blended dock and collapsed drones that bloom on hover; round 41
   z-order and conflict rules (§3.11, §3.21).
2. Firmware socketed die at the hub side (§3.9); Daemon rack CRT plate (§3.13).
3. Animated card-play preview: ghost blades, ghost drones, no trace arrows (§3.17), fed by the same
   forecast code path (preview == result).
4. Combat backdrop (§3.14, D17): the target building close-up, day (cooler) / night; the HQ for bosses;
   Meridian facing the boom; the REBEL_CELL canyon; wheel areas softened ~55 %. Until ART-5's city lands,
   use stills/bakes made from the concept generator scripts (Blender headless allowed) per corp; fight
   won → the building's lights turn Cell colours.
- Accept: worst-case fixture with satellites legible; preview overlay == forecast; captures per corp.

### 2C — Cards and FX (ART-3; bible §3.18, §3.20, §3.15, §5.3–5.4, §6.3)
Owns `scripts/ui/kit/combat_fx_layer.gd`, card views (`card_view` / hand), new `scripts/ui/fx/**` FX.
Refs: `cards_fx/round19_combat_fx/*` (card_play_v2, dissolve_A_bitstream), `round18–23_combat_fx/*`,
`cards_fx/binary_damage/*`, `round17_corp_wheels/*`.
1. Sticker cards: peel, slap, dissolve A bit-stream; the hover preview (§3.18).
2. Binary damage shards (hit and crit) on 1B's bits emitter, routed round the rim (§3.20).
3. The locked effect set (§3.20): block / shield walls; heal; drone deploy / attack / destroyed v3; enemy
   defeated v2; corrupt apply v4 / tick v3; evade v4; phase change v3; respin; nudge and resistance; RAM
   gain from the TURN banner; temporary word stickers dissolving into bits; Daemon sigils, rack and trigger;
   firmware trigger.
4. Heat on the combat screen, five bands, H1 "the city reacts" (§3.15; PURGE = HUNTED's look for now).
5. Carry-over: combat `hit_shake` 3 px is above T2's 2 px limit — fix to the tier.
- Accept: every FX has a `ui_motion.tres` entry, a lab demo and its reduce-effects end state; flash limiter
  (≤ 3/s) test; the D16 origin rule tested; captures vs the reference GIF strips.

### 2D — HUD (ART-4; bible §3.1, §1.3, §4.13 kit parts)
Owns `scripts/ui/combat_scene.gd` HUD parts, `kit/hud_*`, `ram_bar.gd`, toasts / tooltips / buttons /
dialog kit restyle (behaviour from F's port stays).
Refs: `hud/round41_wheel_stack/*`, `hud/round22_combat_fx/send_it_sticker.jpg`,
`menus/round33_ui_chrome/abandon_dialog.jpg`, `ui_kit.jpg`.
1. Combat HUD v4 (§3.1): nudges above the wheels; CELL-9 // CLASS sticker over RAM; boss keys A / D
   (check bindings); **result chips** beside each HP in the D15 format with the breakdown tooltip; SEND IT
   pink vinyl sticker over `EXECUTE`; RESPIN / UNDO terminal chips, undo block on UNDO (D12).
2. Map HUD and top bar on the v2 kit.
3. Toasts, tooltips, buttons (yellow CANCEL), the modal and dialog kit (abandon dialog: both buttons
   stickers).
- Accept: GDD 2.10 holds — chip == resolve for all enemies × seeds (re-use the H23/H24 sweeps, moved to the
  chip); pad reachability; fits at 2.0; captures vs `combat_typical_v4` and the abandon dialog.

## File-ownership matrix
| Path | Owner |
|---|---|
| wheel_view.gd, scripts/ui/wheel/** (except attach/), shaders/wheel/** | 2A |
| scripts/ui/wheel/attach/**, combat backdrop | 2B |
| combat_fx_layer.gd, card views, scripts/ui/fx/** | 2C |
| combat_scene.gd (HUD + layout), hud kit, ram_bar.gd, toast/tooltip/dialog restyle | 2D |
| palette / theme / fonts, shaders/kit/**, materials, glyph atlas, city spike | Group 1 (read-only; smallest edits reported) |
| scripts/ui/kit/* behaviour (focus, PadGlyph, modals, UiWrap) | F (ART-0) until merged |
| ui_motion.tres, REQUIRED_IDS, lab DEMOS, test_manifest.json, strings.csv, DECISIONS | everyone (union) |

## Group 2 acceptance
- [ ] 2A, 2B, 2C, 2D merged one at a time after fast checks green, pushed.
- [ ] The fight matches `combat_typical_v4` / `combat_worst_case_v4` (side-by-side in `docs/art_review/ART-2/`).
- [ ] Preview == result (chip == resolve) for all enemies × seeds; every FX entry + demo + reduce-effects end state.
- [ ] Timeline `19_art2` with a README row.
- [ ] Designer review (non-blocking).
