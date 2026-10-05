# Group 4 — Screens: ART-9 shop / rewards / events / dialogue / portraits, ART-10 menus / title / settings / HQ, ART-11 campaign end (M14)

Started 2026-10-05 in parallel with Groups 1–3 (designer: "start any group you can in parallel"; DECISIONS
"groups in parallel, fast checks only, done within days"). Every agent reads `process/agent_common_rules.txt`
first. Source of truth: `docs/ART_BIBLE.md` §1.2 (media and their jobs), §2, §4.10–4.13, §5–6; references in
`docs/art_reference/{shop_events,portraits,menus,campaign_end}/` (README maps each to its lock); plan §4.2.
Generator scripts: `art-concepts-r43:docs/concepts/<round>/scripts/`.

**Goal: each screen looks like its reference.** Visual impact first; capture windowed next to the reference,
iterate. Fast checks + own scripts only (no full suite, no audit until after ART-12).

**Foundations landing in parallel:** 1A palette v2 / faces / theme types (TerminalPanel, TerminalButton,
HoloPanel, PaperPanel, live-number LabelSettings), 1B materials (CRT, vinyl sticker with peel/slap/dissolve,
grease pencil, light spill, holo, corp paper, binary bits), 1C glyph atlas. Build behind one seam each; the
orchestrator messages you when each lands → `git merge main` → switch. F's kit behaviour (states, focus
brackets, PadGlyph, modal API + GlassScrim, UiWrap, PaperInk) is on main already.

**Must survive:** the shop and event sweeps (affordability, outcome rows == deltas); preview == result;
MotionSkip one press; reduce effects = end state; headless never waits; motion in `ui_motion.tres` +
REQUIRED_IDS + lab demo (restyle, never drop); tokens only (D's static lint); layouts at 1.0/1.6/2.0; pad
reachability; Signal Up / Call Down. **No unapproved mechanics** (G1–G16): shop pricing stays the current
rules (no top-3 discount, G14), removal stays the current action (the recycle bin is its look only if it
maps 1:1 onto the current removal; otherwise keep the current removal with v2 styling and say so).

## Areas (parallel)

### 4A — MAINFRAME shop, rewards, events (ART-9; bible §4.10, §4.11)
Owns the Mainframe shop, loot / reward and event views (`netrun_scene.gd` shop/loot/event parts,
`kit/mainframe_sign.gd`, related kit views). Refs: `shop_events/round12_modem_facade/f1b_*` (F1 Tenement
facade, pinker spill, no dangling cables), `round33_mainframe_sign/*` (sign v4 + sequences NO→MoRE→MAN,
I AM→AI, I AM→NO→MAN), `round34_firmware_daemons/shop_v5.jpg` (layout v5, FIRMWARE / Daemon shelves),
`round33_shop/*` (offscreen slice wheel, recycle bin), `round31_reward_event/*`, `round32_shop_reward/*`.
1. Shop: facade backdrop (baked from the generator scripts per day / night / rain), sign v4 with its
   sequences, layout v5, the offscreen slice wheel with price tags (current flat price), FIRMWARE / Daemon
   shelves, a more colourful LEAVE sticker.
2. Rewards: peel from the loot sheet (`reward_reveal`).
3. Events as drawn (`event_screen`, `event_screen_memo`): corp memo on corp paper where the speaker is a corp.
- Accept: shop and event sweeps hold; captures vs each reference.

### 4B — Dialogue and portraits (ART-9; bible §4.11, §4.12; DISPATCH ruling)
Owns `dialogue.gd`, `subtitle_strip.gd`, portrait views / portrait art. Refs: `shop_events/round31_reward_event/
dialogue.jpg`, `portraits/round38_portraits/*` (states, contexts), `round39_portraits/portraits_classes_v2.jpg`.
1. Dialogue: cel bust on a CRT feed; DISPATCH is voice-only, a clean red CRT terminal feed, never a sticker
   or pencil (DECISIONS "DISPATCH text").
2. Operative portraits v2 for all eight classes with states (idle, hurt, dead-eyes …) and contexts (feed,
   dossier "print", combat) and rookie variants; pre-rendered bust sets from the generator scripts (Blender
   headless allowed; keep assets game-sized) or SubViewport assembly; one feed shader (`mode`, `tint`,
   `split`, `tear`, `noise`, `fps_hold`).
- Accept: every class × state renders; subtitles keep their ANIM behaviour (typing, paging, skip); captures.

### 4C — Menus, title, settings, HQ screen (ART-10; bible §4.13, §1.2)
Owns `title`/main menu, `settings_panel.gd` (look; C's behaviour stays), `pause_menu.gd`, codex, stats,
achievements, campaign slots, new-campaign picker, `hq_scene.gd` look. Refs: `menus/round33_ui_chrome/
title_screen.jpg`, `title_screen_alt_simulate.jpg`, `abandon_dialog.jpg`, `ui_kit.jpg`, `typography.jpg`,
`menus/round31_ui_chrome/settings_menu.jpg`.
1. Title option A with the verbs BREACH / DISABLE / OVERTHROW and **SIMULATE** for the tutorial (D10 —
   pending designer confirmation, built on its default); the abandon dialog (both buttons stickers).
2. Options on the v2 kit incl. `heat_glitch` and (when Group 3 lands it) always-show nodes; carry-over: the
   pad focus scale on full-width Options rows (UiFocus.META_NO_SCALE or narrower rows); panels adopt
   FitScroll.
3. Codex, stats, achievements, pause, campaign slots, new-campaign picker on the v2 kit; corp paper in
   Courier Prime where a screen shows a corp document.
4. The HQ screen restyled on the v2 kit (CRT terminals over the city; operative dossier as corp paper).
   The concept rounds dropped the HQ room (G13, pending re-evaluation after M14): keep every current HQ
   action reachable, restyled — no action removed.
- Accept: captures vs references; pad reachability; fits at 2.0.

### 4D — Campaign lost, dossier, run end (ART-11; bible §4.8 campaign lost / summary)
Owns campaign end / run end stages. Refs: `campaign_end/round20_raid_world/campaign_lost.jpg`,
`round21_raid_world/campaign_dossier.jpg`, `raid/round23_raid_ui/interactions_gifs/26_home_breached.frames.jpg`.
1. Campaign lost = option A, ransomware lock: the winning corp's house style and verb (PROCESSED,
   RECLAIMED, TREATED, DE-ORBITED, OVERWRITTEN), every node padlocked, a countdown to the wipe, the Cell's
   stickers curl and drop off; BREACHED as the cause (ruling 6.2).
2. Campaign summary = the corp's audit dossier (manila folder, typed AUDIT REPORT, CASE CLOSED, personnel
   sheet DECEASED / AT LARGE, polaroids, auditor post-its); campaign won in the same language.
3. Run end FLATLINED / JACKED OUT / HOME FELL restyled.
- Accept: each end state captured vs reference; motion entries + reduce-effects end states.

## File-ownership matrix
| Path | Owner |
|---|---|
| shop / loot / event parts of netrun_scene.gd, mainframe_sign.gd | 4A |
| dialogue.gd, subtitle_strip.gd, portraits | 4B |
| title, settings_panel look, pause, codex, stats, achievements, slots, picker, hq_scene.gd look | 4C |
| campaign end / run end stages | 4D |
| netrun route / map parts of netrun_scene.gd | Group 3 (3B) |
| combat_scene.gd, wheel_view.gd, combat FX | Group 2 |
| palette / theme / fonts, shaders/kit, materials, glyphs | Group 1 (read-only; smallest edits reported) |
| ui_motion.tres, REQUIRED_IDS, lab DEMOS, test_manifest.json, strings.csv, DECISIONS | everyone (union) |

## Group 4 acceptance
- [ ] 4A–4D merged one at a time after fast checks green, pushed.
- [ ] Each screen side by side with its reference in `docs/art_review/ART-4grp/<area>/`.
- [ ] Sweeps hold (shop, event, preview); every motion entry + demo + reduce-effects end state.
- [ ] Timeline row with a README row. Designer review (non-blocking).
