# Decision Log

Append new entries at the top of the relevant section. Never delete entries; mark them
superseded instead.

## Locked design decisions (v0.9)
- Wheel is 30 ticks / 6 slices / 5 ticks per slice (was 24). Enables a true centre tick.
- No Miss precision tier; "Miss" means the Miss slice only.
- Enemy jitter replaced by spin resistance (passive trait or Hub-sourced). Flip and
  Respin are blocked while resistance > 0.
- Flip mirrors the wheel across the horizontal axis (opposite slice to the pointer).
- Triggering: every pointer triggers its slice on End Turn. Pointer attacks hit every
  pointer of the target wheel. Satellites act as bodyguards.
- Resolution order: defensive → offensive → statuses, simultaneous.
- Three-layer progression: netrun / campaign / profile. Class unlocks are profile-level.
- Rank (runs survived) replaces veterans/Trace: wheel upgrades, netrun tier access,
  station bonus scaling. Survivors keep everything; difficulty scales to match.
- Heat is one campaign meter. Threshold events fire once; modifiers apply while at/above.
- City Grid is one shared map for netruns, territory and raids; cleared Sites are used up
  and become claimable.
- Armory (cap 6) + persistent deployed assets resolves the audit's persistence question.
- Mainframe gate: minimum 3 Exploits (Intel, Breach, Virus); extras weaken the boss.
- Story paths: 5–6 per corporation, hidden and random; beats unlock in Exploit order.
- REBEL_CELL (the handler AI) is the final unlock corporation at ICE 10 on all others.
- ICE difficulty: 20 cumulative levels, ICE 5 is the average-player tuning target.
- Visual baseline: three worlds (cyberdeck / wireframe / zine), Cell colour hot pink.
- Full voice acting; fully solvable combat preview; rewind with checkpoints at random
  events.

## Implementation decisions
_(Claude Code: add entries here as you make them.)_

### 2026-09-25 — Horizontal pass 17 fixes (GAP_ANALYSIS H17)
- **The pause menu blocks the mouse**: a full-screen backdrop (`MOUSE_FILTER_STOP`, dim)
  sits behind it, so clicking SEND IT, a map node or an HQ button behind the menu does
  nothing (H15 blocked keys and pad only).
- **A Shunt resolution is the landing everywhere**: its slice's CORRUPTED bite and
  OVERCLOCKED burn-out apply, Stolen Intent fires on a shunted Miss, and the operative's
  drones follow the slot that actually resolves (GDD 5.2).
- **A copy resolves the neighbour's slice and temporary status only**: not its Firmware
  and not the permanent status that Firmware grants (Burner's Overclock without its Heat).
- **Rebinding refuses 1-9, Enter and Esc and any key another action holds**
  (`Settings.bind_error`); the button says why and keeps waiting for another key.
- Balance after H17: Breaker ICE 5 3/8 in 48.1 runs (was 4/8 in 42.8).

### 2026-09-25 — Horizontal pass 16 fixes (GAP_ANALYSIS H16)
- **A landing is the pointer's slice, or what a Shunt resolves instead**
  (`CombatResolver.is_landing`). A Mirror copy of a neighbour is not a landing: Daemons
  don't fire on it (a Mirror Perfect used to fire Kernel Sync, Clean Signal, Botnet Seed
  three times), and a copied Miss doesn't resolve the Miss for Cold Exit, Zero Day or the
  consecutive-Perfect count. The copies still resolve the slice and the Hub (H17: not the
  neighbour's Firmware or the permanent status it grants).
- **A MULTIPLY or MIGRATE phase stops an earlier orbit**: Commons Array's 33% readers
  "lock on" as its phase line says.
- **Rebinding captures every key** in `_input` (arrow keys, Tab), before focus navigation.
- **The combat pause menu is on its own CanvasLayer**, centred on the viewport, so the
  netrun scroll can't clip it.
- **Esc in the pause-menu Codex returns to the menu** (as Esc in Options does).
- Balance after H16: Breaker ICE 5 4/8 in 42.8 runs (was 5/8 in 36.4; the bot's Mirror
  Firmware had been tripling its Daemons). See the pacing open question.

### 2026-09-25 — Horizontal pass 15 fixes (GAP_ANALYSIS H15)
- **Daemons fire once per landing.** A Perfect resolves two or three times (every Hub
  Core retriggers, Echo adds one), and each extra resolution used to fire the Daemons
  again: Clean Signal gave -4 Heat for "-2", Zero Day was a 6x Crit for "3x", Kernel Sync
  +2 for "+1". Now the slice, its Firmware, segment and Hub repeat with every resolution
  (the M1/M6 rulings stand) and Daemon listeners fire once after the resolutions. The Hub
  Core texts now say "on each resolution" for their hook effects.
- **Nothing acts behind the pause menu**: while it is open it swallows unhandled keys and
  pad buttons (Space, 1-9, Q/E, LB/RB, Tab), in combat, on the map and at HQ.
- **The pause menu is 760x520** and its Options panel reports its content's size, so the
  menu's scroll reaches Close, Reset and every rebind button at text scale 1.6.
- **Intel's phase reveal shows the real layouts** (`CombatResolver.phase_layout`: Breach
  removal and the ICE extra pointer), plus the orbit speed of an ORBIT phase.
- **Firmware per-combat limits: one counter per Firmware id, the limit times the copies
  socketed.** H14 keyed it by slot, and a Flip moves Firmware between slots, which gave
  fresh charges (Skimmer fired four times). Two copies still have two charges each.
- **Repair shows its price** (`CampaignRules.repair_cost`, ICE 13 included).
- **The End Turn preview shows odds only for random status picks** (DOSE); a fixed slot
  (Overclock burnout, a Perfect Parasite, the Corrupt segment) says which slot.
- **Config**: `achievement_ice_low` 5 and `achievement_ice_high` 10; the Rack tier index
  is bounded by the Rack tables. TECH_SPEC 8 lists the quit and window-close saves.
- **Balance after H15** (Daemons no longer doubled): Breaker ICE 5 5/8 in 36.4 runs;
  Ghost ICE 0 6/8 in 27.1; Botnet ICE 0 8/8 in 22.1; Rigger ICE 0 5/8 in 36.5 (was 7/8 in
  19.8: it leaned on doubled Daemons). Kept on the harder side; see the open question.

### 2026-09-24 — Horizontal pass 14 fixes (GAP_ANALYSIS H14)
- **Boss phases keep their layout and ICE extras**: an ORBIT phase that lists pointers
  sets them before orbiting (Commons Array 66%: two readers; Civic Core 33%: two). The ICE
  16-20 extra pointer and the ICE / Heat bonus resistance are stored at setup and re-added
  after every MULTIPLY / MIGRATE layout and wheel swap.
- **Heat-gated effects can ride attacks only** (`HeatGatedEffectData.offensive_slices_only`,
  schema change): Compliance Officer's Audit drains RAM on its Attack and Crit slices only.
- **Mirror elites run their own Daemons**: enemy hubs fire ON_COMBAT_START effects (Shield
  Cache), and enemy Perfect hooks need no streak (the consecutive-Perfect counter is the
  operative's; an enemy hook with consecutive_required > 1 never fires).
- **Rig Core's free nudge arrives**: free nudges earned while resolving are banked in
  `CombatState.free_nudges_next_turn` and added at the next start of turn.
- **Ghost Core covers card nudges**: the first N nudges on enemy wheels each turn, from an
  action or a card, ignore resistance (one shared counter).
- **Firmware per-combat limits count per slot**: two Coolant Loops have two charges.
- **Text fixed to match the rules**: Nanite Mesh "cleanses itself after resolving"; Snap
  "your outer ring"; Locked Ward rescues "another runner"; The Old Crew "Open the cells"
  (no rescue); the Armory sabotage no longer claims weaker raids; Returns Desk result.
- **Terminal Firmware that fits no slice is refused** (button disabled, reason shown);
  zero-Cycle filler effects no longer print "+0 Cycles".
- **Modals trap focus** (`UiFocus.trap`): confirm dialogs (Yes and No reach each other)
  and the pause menu, its Options and Codex. The pause menu scrolls vertically and wraps.
- **Text scale 1.6 fits**: the netrun and HQ status bars wrap, the standalone combat top
  row flows and hides the dev fight picker in the Tutorial, and the tutorial note starts
  at the top and scrolls by pad.
- **Achievement thresholds from config** (`achievement_racks` 10, `achievement_raids` 20,
  `achievement_perfects` 500); Purge Survivor tracks the top Heat threshold.
- **Closing the window saves** (`NOTIFICATION_WM_CLOSE_REQUEST`), so a fight resumes where
  it was; a resumed run's outcome is recorded in history and stats.
- Balance after H14: Breaker ICE 5 5/8 in 31.6 runs, Ghost ICE 0 7/8 in 24.0, Rigger ICE 0
  7/8 in 19.8.

### 2026-09-24 — Horizontal pass 13 fixes (GAP_ANALYSIS H13)
- **Cards move the ring they name**: a NUDGE effect with ring_scope INNER (Ring Tap,
  Ratchet, Inner Drift, Gear Shift) always moves the inner ring. An outer-ring nudge card
  (Fine Tune's "one ring", Jam, Tap Tap) follows the ring toggle, and falls back to the
  outer ring on a wheel without an inner one instead of spending the card for nothing.
  Snap's text now says it snaps the outer ring (Inner Snap does the inner one).
- **Resistance changed while the turn resolves lasts**: a change made during RESOLVE
  (Ghost Core strip on a Perfect, Tracer, an enemy's own +resistance slice) carries into
  the next turn's restore (`CombatantState.resistance_carry`), then full resistance
  returns a turn later. Changes made in the player phase (the Strip card) work as before.
- **A kill outside resolution ends the fight**: after a card play and after start-of-turn
  effects, deaths are settled and the outcome checked (Static Shock and friends no longer
  leave a 0-HP enemy standing).
- **Terminal choices show their real costs**: the button text uses the choice's data
  (Cycles, HP, Heat as it will apply at the current ICE, rewards) in place of the
  hand-written summary. A choice is refused, and its button disabled, when it costs
  Cycles you don't have, would flatline the operative, or grants a Daemon already
  installed. Returns Desk's "Return a Bug" (it never took a Bug) became "Trade in store
  credit".
- **Rack Heat labels include Scrubber's override**.
- **The tutorial sits over the log strip** (right column, never on a wheel), is part of
  the layout check, and names the bound keys; the combat buttons do too.
- **Momentum**: Spin `amount` (2), or amount x multiplier (5) after a spin, from the card.
- **Width tests restore the text scale in after_each**, so a failed run can't leave the
  player's settings at 1.6. Netrun panels wrap like HQ panels (`UiWrap.fit`).

### 2026-09-24 — Horizontal pass 12 fixes (GAP_ANALYSIS H12)
- **One profile for every campaign slot** (GDD 3.4, TECH_SPEC 8): slots 1-3 and the default
  slot share `profile.json`; deleting a slot's campaign keeps it. Test slots (`gut_` prefix)
  keep a private profile. A per-slot profile from before H12 is read when the shared one
  is missing.
- **The final Rack's rewards are claimable**: its card (and any Firmware) offer now waits
  in the REWARD phase and the run completes once it is resolved. **The final Rack offers
  no Daemon**; the layer-4 Rack is the Rack Daemon source. With a Daemon at both Racks the
  bot carried 12-13 Daemons into the boss and won ICE 5 in 8.8 runs (GDD 11.8: about 24).
  Raising elite and boss HP x1.3 and output x1.25 barely changed that (9.5 runs). Without
  the final Daemon: ICE 0 7/8 won in 31 runs, ICE 5 5/8 in 32.9 (H11: 4/8 in 30.1), on the
  harder side of the target (the "when in doubt, stronger" rule).
- **A patrol stays a patrol**: `RunState.patrol` is set at launch, so a raid Seizing the
  Site mid-run doesn't turn the completion into a clear. An Exploit already held is never
  extracted again (no second copy, Heat or story beat).
- **Long labels wrap on every HQ and title panel** (`UiWrap.fit`): labels stacked in a
  column wrap, and any row label or button wider than 560 px wraps at 560. Title slot rows
  are flow rows. Tested at text scale 1.0 and 1.6.
- **Tuning moved to content and config**: `DaemonData.amount` (schema change) holds Cold
  Exit 3, Scrubber 1, Kernel Sync 1, Zero Day 3 and Botnet Seed 2. Config gains
  `raid_wave_interval` 5, `raid_heat_scaling_step` 10, `dispatch_drift_mid` 3 and
  `dispatch_drift_late` 6.
- **Any player read head resolving the Miss spoils Cold Exit**, Twin Pointer's second
  one included. The consecutive-Perfect count stays on the first pointer.
- **Racks captured are counted** (`RunState.racks_captured`), no longer estimated from
  banked Schematics.

### 2026-09-24 — Horizontal pass 11 fixes (GAP_ANALYSIS H11)
- **Stationed operatives leave their post to run** (GDD 5.4, "instead of running"):
  launching a stationed operative recalls it (the launch picker says "leaves <site>"), and
  a death frees the post.
- **An empty roster can always recruit**: with no living operative a rookie costs
  `emergency_rookie_cost` (0), so the campaign can't stall with no operative and fewer
  than 15 Schematics.
- **Heat labels show the applied Heat**: map nodes, Scrub Heat and Heat-objective Sites
  use `HeatRules.scaled_delta` (ICE gain and sink modifiers included). A Daemon override
  of Rack Heat still applies only on capture.
- **ICE 13 raises home repairs** as well as node repairs (REPAIR_COST_PCT).
- **HQ boosts apply to the final breach and Reclaim runs** (Cycles, run-only cards, max
  RAM), and are spent there.
- **A Firewall Relay shares every station bonus** (GDD 3.2): hold, regen and turrets from
  an adjacent stationed operative, the best of each, as well as the Breaker damage bonus.
  This supersedes the M3 Breaker-only ruling.
- **Config**: `ice_base_cap` 3, `ice_unlock_step` 3, top ICE from the ladder
  (`max_ice_level()`), Modem stock `shop_card_stock` 3, `shop_firmware_stock` 2,
  `shop_daemon_stock` 1; Steady Hand's +2 RAM is the card effect's amount.
- **Large text scales wrap**: the combat controls row is a flow row, Grid Site labels
  wrap; widths are tested at `TEXT_SCALE_MAX`.

### 2026-09-24 — Horizontal pass 10 fix (GAP_ANALYSIS H10)
- **Netrun screens fit 1280**: the mid-run raid row wraps (HFlowContainer) and the netrun
  panel host scrolls vertically (horizontal scrolling disabled, follows focus), matching the
  H9 HQ rule.
- **Entering a fight focuses the hand**: the netrun scene calls `CombatScene.focus_hand()`
  (first playable card, else SEND IT) instead of linking or focusing the combat panel generically.

### 2026-09-24 — Horizontal pass 9 fix (GAP_ANALYSIS H9)
- **HQ panels fit the 1280 screen**: button rows (start panel, actions, boosts, unlocks,
  roster, Site rows, raid rows, codex tabs) are HFlowContainers that wrap; the HQ scroll
  area never scrolls sideways; long profile/unlock/record lines word-wrap. A test opens the
  start panel, HQ, codex and Grid with everything unlocked and all eight classes recruited
  and checks every panel is at most 1280 px wide.

### 2026-09-24 — Horizontal pass 7 fixes (GAP_ANALYSIS H7)
- **Settings sections relink**: `show_section` relinks the panel after swapping controls,
  `link_layout` clears old neighbour paths first, and sliders count as linkable, so every
  Options section (title and pause) is D-pad complete.
- **Reference notes are readable by pad**: codex, stats, run history and lines-heard notes
  start at the top, stop auto-following, and take focus (`ZineNote.make_reference`). H8: a
  focused note handles ui_up/ui_down itself (a RichTextLabel only scrolls on keyboard
  arrows), a quarter page per press, and passes focus on at the top or bottom edge.
- **Netrun combat** links its own hand; the netrun panel no longer links it before the
  fight pickers are hidden.

### 2026-09-24 — Horizontal pass 6 fixes (GAP_ANALYSIS H6)
- **Every panel is D-pad complete**: `UiFocus.link_layout` groups a panel's focusable
  controls into rows (a horizontal container is a row, a lone control is its own row),
  chains left/right within rows and up/down to the same column of the next row; SpinBox
  text fields are skipped (their -/+ buttons are used). HQ, title and netrun panels link on
  open, so reward and Modem stickers, the corporation picker and every Grid row are
  reachable; the Grid list scrolls to follow focus. Left from SEND IT returns to the hand.
- **Reward stickers** no longer show number-key hints that do nothing.
- **Assist label** reads its numbers from the config.
- `tests/unit/test_pad_reachability.gd` walks focus neighbours from the starting focus and
  asserts every usable control is reached (start panel, Grid, rewards, Modem, combat).

### 2026-09-24 — Horizontal pass 5 fixes (GAP_ANALYSIS H5)
- **Card previews follow navigation only**: a card shows its preview when the player moves
  focus onto it (D-pad, arrows, Shift+Tab); nudges, card keys and the automatic refocus
  after a refresh keep the End Turn preview the tutorial points at.
- **D-pad walks the hand**: explicit left/right neighbours between cards (tilted stickers
  confused Godot's geometric search), the last card leads to SEND IT.
- **Confirm dialogs give focus back** to whatever opened them.
- **Esc leaves the share-code field** instead of being swallowed.
- Tests drive real key events through the viewport (E, Right, Esc).

### 2026-09-24 — Horizontal pass 4 fixes (GAP_ANALYSIS H4)
- **Focus survives card plays**: a control queued for deletion no longer counts as focused,
  so the rebuilt hand takes focus; with no playable card, focus falls back to the controls
  row (SEND IT). Card previews follow focus only after keyboard or pad input (auto-focus at
  fight start keeps the End Turn preview).
- **Tab is Cycle target again**: Tab is removed from `ui_focus_next` (like Space from
  `ui_accept`); Shift+Tab still moves focus back.
- **Modals take focus**: the pause menu focuses its first button and gives focus back on
  close, the settings panel focuses itself, confirm dialogs focus "No".
- **Start panel for pads**: ICE -/+ and seed +1 buttons (SpinBoxes ignore the D-pad).

### 2026-09-24 — Horizontal pass 3 fixes (GAP_ANALYSIS H3)
- **Lost-raid Heat** names the next raid for the corporation: `CampaignRules.fight_raid`
  renames its own events (HQ, netrun interlude and simulator paths all go through it).
- **REBEL_CELL elite pool** = this campaign's Mirrors only (`corporation.elites`), sorted;
  netrun pools are rebuilt once the corporation is set. Before, Mirrors from earlier builds
  in the session leaked in and a resume in a fresh session could play differently.
- **Pad-only play**: every panel focuses its first usable button (`UiFocus`), the combat
  hand refocuses when focus is lost (H4: also after a card play frees the old hand), pad
  inspect inspects the focused control. Pad
  layout reworked: LB/RB nudge, Y target, X end turn, Back rewind, L3 inspect, R3 respin,
  Start options; the D-pad, A and B drive focus (`UI_PAD_BINDS`), so the combat pickers and
  cards are reached as on-screen buttons. Space no longer presses the focused button (it is
  End Turn). Confirm on real hardware.
- **More Mirror numbers in the config**: `mirror_resistance`, `mirror_deploy_base`,
  `mirror_threat_min_integrity`, `mirror_threat_min_damage`, `mirror_decoy_speed`; the
  designer's tuning knob is `config.mirror_output_factor`.

### 2026-09-24 — Horizontal pass 2 fixes (GAP_ANALYSIS H2)
- **Raid names per corporation**: `CampaignRules.name_pending_raids` rewrites HeatRules'
  "Raid incoming" text with the corporation's own raid (HQ report, netrun Heat, run end).
- **Raid warning keys**: mid-run interludes carry the queued (shared) raid id, so the
  corporation's specific warning plays on both screens.
- **Event speakers** carry their corporation (label and colour); "lines heard" too.
- **Held at home = no damage while held**; the damage lands on the step the hold ends.
- **Boss launch message**: with enough Exploits it now says the boss needs a cleared or
  claimed Site next to it (it used to repeat "needs 3 Exploits (3 held)").
- **Share codes** encode the campaign's starting class (`CampaignState.start_class_id`), so
  the code stays valid after that operative dies.
- **ICE records** skip a locked REBEL_CELL (no spoiler) and hint "something opens at ICE
  10 everywhere"; the stats screen shows records per corporation and assisted wins; run
  history names corporations.
- **No magic numbers**: Heat bands come from the config's MAJOR thresholds
  (`major_heat_levels()`); Mirror factors and the "final final" ICE moved to the config
  (`mirror_output_factor`, `mirror_threat_integrity`, `mirror_threat_damage_bonus`,
  `final_final_ice`; code keeps the same defaults for tools).
- **Colours**: Halcyon #8C7BFF (was too close to Solace), Orbital #DDE3FF (was too close to
  resist_gold); every corporation colour is in STYLE_GUIDE. Dead `CLASS_COLORS` removed.
- **Shared text**: the Medbay and DISPATCH ping events and two Breaker barks no longer name
  Solace.
- **Unlock matching by id** (bug found by the full suite): after a REBEL_CELL campaign the
  built corporation replaces the template in the lookup, and `unlock_for` compared objects,
  so REBEL_CELL looked open to everyone for the rest of the session. Unlocks now also match
  by content id.

### 2026-09-24 — Horizontal pass 1 fixes (GAP_ANALYSIS H1)
- **Corporation-aware everywhere**: the win text and end screen name the corporation's own
  boss; corporate subtitle lines carry the corporation's short name ("MERIDIAN") and colour
  (`Dialogue.speaker_name`); the boss-phase flash and the Heat poster use the corporation
  colour; the HQ pirate radio has DJ sets per corporation (generic lines kept apart).
- **Music per corporation**: `AudioDirector.CORP_CONTEXTS` maps generic contexts to a
  corporation's (Solace/Meridian/Halcyon/Orbital raids get their own loop; REBEL_CELL plays
  its slowed lo-fi at HQ and on the Grid). New code-generated loops for the three raids.
- **ICE records**: HQ and end screen list the best ICE for every corporation and the
  road to REBEL_CELL (n/4 cleared at ICE 10). The Target list is ordered open first, then
  by unlock price, REBEL_CELL last, and the ICE box starts from the first entry's cap.
- **Codex**: enemies appear once met (`RunManager.record_seen`, profile stat
  `use_seen:<id>`); REBEL_CELL shows as "???" until reached; new Classes, Corporations and
  Home servers sections; AFFLICT and PARASITE text generic; lexicon adds Tariff, Citation,
  Solar Flare, Inertia, Mirror.
- **Rescue**: every corporation has a rescue event; a rescued operative is one of the
  classes already on the roster (seeded draw, never bypasses class unlocks).
- **Built-in ICE Locks hold threats** (bug): raid holds only looked at deployed assets;
  built-in node and home assets now hold too, and a threat held at the home server does
  not damage it while held (the home defences keep firing). This makes the Ghost home work.
- **Raid warnings** use the queued (shared) raid id on both screens, so corporation lines
  play. **DISPATCH speaks its boss line** when a boss run starts.
- **Assisted wins** count in `stats.assisted_wins`, not `campaigns_won` (no "Breach").
- **Share codes for REBEL_CELL** are marked local on the HQ radio (it is built from your
  own profile; another player's code builds from theirs).
- **Breaker's second exclusive**: Shatter (breach the Hub 1 turn, strip 1 resistance),
  shared with the Wrecker; every class now has two exclusives.
- **Events per corporation**: target lowered to about 30 rollable (own + shared): the new
  corporations have 21 of their own plus 7 shared; Solace keeps 40. Writers can add more.
- Tests for Overclocker and Mk2 cores, home servers in raids, Mirror threat routing,
  REBEL_CELL resume mid-netrun, and every corporation's events in its own campaign.

### 2026-09-24 — M12 Polish and reach (GAP_ANALYSIS P1 10, P2 11-13)
- **Home-server variants 2 -> 5** (Profile unlocks, `tools/content_gen/gen_home.py`): Relay
  Nest (50 integrity spread over two nodes, 5 asset slots; 50 Schematics), Ghost (50
  integrity, 2 slots, built-in ICE Lock holding a threat 2 steps; 60), Fortress (100
  integrity, 2 slots, no gun; 80).
- **Skins deferred to art integration (M13)**: with placeholder art a skin would only be a
  palette swap; UnlockKind.SKIN stays for when portraits and card art arrive.
- **Controller support** (P2 11): `Settings.CONTROLLER_BINDS` adds a pad button to every
  combat action at startup (shoulders nudge, Y target, X end turn, Back rewind, B nudge
  wheel, D-pad toggles, stick clicks inspect/respin, Start options). Menus use Godot's pad
  ui_* bindings. Rebinding a key keeps the pad button. No pad rebinding UI yet.
- **Share codes and the daily run** (P2 12): `CampaignCode` encodes seed, corporation, ICE,
  home and class as RC1-<corp>-<ice>-<seed>-<home>-<class>; the core is deterministic, so a
  code replays the same campaign. HQ start panel: Daily run (seed YYYYMMDD from the system
  date, read in the UI only) and Start from code; the HQ radio shows the running code.
  Locked parts of a code fall back like the start panel.
- **Assist mode** (P2 13): an Accessibility option; campaigns started with it get
  `config.assist_free_nudges` (1) extra free nudges a turn and `config.assist_hp_multiplier`
  (1.25) operative HP, saved on the campaign. Assisted wins count as wins but set no ICE
  records and earn no campaign achievements; the HQ shows ASSIST. "Preview-only" from the
  GDD list is already how the game plays (every action previews before it commits).

### 2026-09-24 — M11 REBEL_CELL (GAP_ANALYSIS P1 9, GDD 8.5)
- **Built from the profile.** `ProfileState` now counts usage (stats `use_class:`,
  `use_daemon:`, `use_node:`, `use_asset:`) at the end of every run: the operative's class
  and Daemons, and the node types and assets standing on the Grid.
  `RebelCellBuilder.snapshot` takes the top 2 classes, 3 Daemons, 3 node types and 3
  assets (ties by id; starter fallbacks when empty). `RebelCellBuilder.build` deep-copies
  the template (never touches the loaded Resource) and:
  - replaces the elites with **Mirrors** of your classes: your wheel, each slice swapped
    for the closest plain slice of its type at 1.5x output (Deploy becomes Attack), one
    pointer, resistance 1, and a hub running the combat effects of your data Daemons
    (custom-handler Daemons cannot be copied);
  - prefixes Site names with your node types;
  - rebuilds every raid with **Mirror** threats made from your assets (1.5x integrity,
    +2 damage; turrets hunt the weakest node, ICE Locks freeze links, decoys run fast at
    the highest-value node).
- **Rebuilt on resume**: the campaign saves its snapshot (`CampaignState.generated`), so the
  enemy does not change when the profile moves on. The built corporation is registered in
  the lookup (`RunManager.build_generated`).
- **Unlock**: free, and opens by itself once every other corporation is cleared at ICE 10
  (`requires_all_corporations_at_ice = config.rebel_cell_unlock_ice`); free unlocks are
  not shown in the HQ buy row. Own ICE ladder (per-corporation caps already existed).
- **Static template** (`tools/content_gen/gen_rebel_cell.py`): normal enemies using every
  corporation's signature affliction (Dose, Tariff, Citation, Solar Flare); mini-boss The
  Handler; boss **DISPATCH** (460 HP; Root Access hub repairs 4 and shields 4 unless
  breached). Six reveal paths (The Handler, Every Collapse, The Buyer, Your Own Hands, The
  Founders, Final Final): DISPATCH is the rogue AI and the buyer behind every collapse.
  DISPATCH briefs the Cell as the enemy. Template elites have no corporation id so pools
  never draw them. Colour #FF2A6D.
- **"Final final"** achievement: REBEL_CELL and every other corporation at ICE 20
  (`Achievements.check` now takes the corporation list).
- **Balance** (8 seeds; the simulator builds REBEL_CELL from a profile that played the
  simulated class with the starter assets): first pass the Mirrors used two pointers and
  2x slices and killed rookies (Breaker 2/8); now one pointer and the closest 1.5x slice.
  Final: Breaker ICE 0 5/8 (27.5 runs), ICE 5 4/8, ICE 10 1/8; Rigger ICE 0 6/8; Botnet
  ICE 0 8/8. The hardest corporation by design.

### 2026-09-24 — M10 Orbital Commons (GAP_ANALYSIS P1 8)
- **Orbital Commons** (GDD 8.4 names): privatised orbital infrastructure (satellite
  internet, positioning, weather). Mechanical identity: **Solar Flares** (new AFFLICT slice:
  OVERCLOCK a random non-Miss player slice: 1.5x on its next trigger, then CORRUPTED, a
  double-edged status), fast orbits and heavy debris. Enemies Uplink Relay, Orbital Debris,
  Tracking Station, Weather Satellite (orbit 4), Ground Control, Launch Pad; elites Station
  Commander and Geostationary Guard; mini-boss Mission Director; boss **The Commons Array**
  (420 HP; Station Keeping hub repairs 3 and shields 3 a turn unless breached; 66% two
  pointers orbiting 4; 33% three pointers, Crit wheel, drones). Threats Lander, Debris
  Field, Signal Jammer; eight raids. Exploits: Launch Codes, Ground Station Override, Open
  Spectrum. Six story paths: The Enclosure, Blackout Weather, Positioning Tax, Final
  Transmission (DISPATCH clues; foreshadows REBEL_CELL, the satellite that names itself),
  Dead Satellites, The Commons. Twenty events, briefings, voice, colour gold #FFE14F.
  Unlock 160 Schematics.
- **Balance** (8 seeds): first pass easy (Breaker ICE 5 7/8 in 14.5 runs); as the fourth
  corporation it was strengthened: elites +10% HP, boss 380 -> 420. Final: Breaker ICE 0
  7/8 (14.3 runs), ICE 5 8/8 (18.4), Ghost ICE 5 8/8 (14.1), Botnet ICE 0 8/8 (13.3),
  Rigger ICE 0 8/8 (17.6).

### 2026-09-24 — M9 Halcyon Civic (GAP_ANALYSIS P1 8)
- **Halcyon Civic** (GDD 8.4 names): smart-city services contractor. Mechanical identity:
  **Citations** (new AFFLICT slice: PARASITE on a random non-Miss player slice, half output
  until cleansed), healing and shielding enemies, evasive surveillance masts. Enemies
  Parking Warden, Utility Meter, Transit Controller, Surveillance Mast, Patrol Unit, Permit
  Office; elites Riot Control and Zoning Board; mini-boss City Manager; boss **The Civic
  Core** (360 HP; Emergency Powers hub heals 4 and blocks 4 a turn unless breached; 66%
  three pointers; 33% orbit, Crit wheel, civic drones). Threats Inspector, Bailiff, Tow
  Truck; eight raids replacing the shared threshold raids. Exploits: Council Minutes,
  Emergency Override, Open Data Leak. Six story paths: Water Rights, Predictive Policing,
  Transit Blackout, The Census (DISPATCH clues), Orbital Uplink (foreshadows Orbital
  Commons), Smart Meters. Twenty events, briefings for every Site, corporate voice, colour
  mint #4FFFB0. Unlock 140 Schematics.
- **Shared generator**: `tools/content_gen/gen_corp_lib.py` builds a whole corporation from
  a spec dict; the M6-M9 generators now live in `tools/content_gen/` (README there).
- **Balance** (8 seeds): first pass the Civic Core killed Breakers (25 boss deaths at ICE 5,
  4/8 won); HP 400 -> 360 and heal 5 -> 4. Final: Breaker ICE 0 7/8 (19.0 runs), ICE 5
  6/8 (15.8), Rigger 7/8 (17.9), Ghost ICE 5 8/8 (10.3), Botnet 8/8 (11.9 before the boss
  change).

### 2026-09-24 — M8 Corporation selection and Meridian Freight Systems (GAP_ANALYSIS P0 3, P1 8)
- **Corporation selection** (P0 3): corporations with a `ProfileUnlockData` (kind
  CORPORATION) need it; the rest (Solace) are always open. `CampaignRules.available_
  corporations` / `corporation_available`; `RunManager.new_campaign` falls back to Solace
  for a locked one. The HQ start panel has a Target picker; the ICE spin box follows the
  chosen corporation's own ladder (GDD 3.4). The start button reads "New campaign".
- **Meridian unlock**: 120 Schematics (implementer's call; classes are 80). Buying it at HQ
  works like the other Profile unlocks.
- **Per-corporation raids** (schema): `RaidData.corporation_id` and `replaces`. The
  Heat-threshold raids live in the shared config; a corporation's raid with `replaces =
  raid_heat_25` stands in for it in that corporation's campaigns. Pending raids now carry
  the campaign's corporation id; old saves without it keep the shared raid. Claim, node,
  story and retaliation raids already came from `CorporationData.raids`.
- **Meridian Freight Systems** (GDD 8.4 names): logistics megacorp. 32-Site Grid mirroring
  Solace's shape (ten T1, eight T2 with the three Exploits, eight T3, four Heat objectives,
  The Manifest at T4). Site ids are global content ids, so Meridian's are prefixed (m_home,
  m1_a..). Enemy family: Customs Scanner, Cargo Hauler (resistance 2), Conveyor Warden
  (orbit 3), Route Optimizer (two pointers), Drone Dispatcher (courier drones), Tariff
  Collector (RAM drain); elites Port Authority and Last-Mile Enforcer; mini-boss Logistics
  Director; boss The Manifest (400 HP, Priority Routing hub: +4 shield a turn unless
  breached; 66% two pointers; 33% orbit, a Crit wheel and courier drones). New slices
  Tariff (AFFLICT: drains 3 RAM) and Attack 8 +1 resistance (Inertia). Threats Courier,
  Hauler, Customs Agent; eight raids. Exploits: Shipping Manifests, Customs Override Keys,
  Rogue Routing Table (same effects as Solace's three). Six story paths: Lost Cargo, The
  Night Shift, Customs Hold, Ghost Freight (DISPATCH clues), Civic Contract (foreshadows
  Halcyon Civic), Last Mile. Twenty Meridian events; DISPATCH briefings for every Site and
  a Meridian corporate voice for raids. Corporation colour amber #FF8C1A.
- **Tuning** (8 seeds, `tools/simulate_campaign.gd -- 8 <ice> class=<id> corp=meridian`):
  first pass Meridian was easier than Solace (Rigger won in 9.6 runs) and the boss stalled
  (95 fights at the turn cap: shield regen outpaced damage at low HP). Normal enemies +20%
  HP and +2 attack, elites +15% HP and +2 attack, Tariff drains 3, boss 400 HP but 4
  shield a turn (was 6). Final:

  | Class | ICE | Won | Mean runs | Stalls |
  |---|---|---|---|---|
  | Breaker | 0 | 7/8 | 18.4 | 40 |
  | Breaker | 5 | 7/8 | 16.8 | 49 |
  | Ghost | 0 | 8/8 | 10.6 | 12 |
  | Botnet | 0 | 8/8 | 13.3 | 3 |
  | Rigger | 0 | 7/8 | 22.6 | 68 |

- Dev shortcuts: `--demo-start` (the start panel) and `--demo-corp=<id>` with the HQ demo
  flags (campaign-only, bypasses Profile unlocks).

### 2026-09-24 — M7 Pools and Solace depth (GAP_ANALYSIS P1 6–7)
- **Only existing effect types.** Every new card, Firmware, Daemon, asset and event is data
  on the M1–M6 effect set; no new mechanics. Numbers are placeholders.
- **Shared cards 22 → 60** (38 new): rotation (Whirl, Backspin, Flick, Spin Cycle, Gear
  Mesh, Inner Drift, Ratchet, Tailspin), precision (Tap Tap, Feather Touch, Inner Snap,
  Lock On, Deep Calibrate, Nudge Driver), enemy control (Deep Strip, Short Circuit, Double
  Jam, Cold Snap, Corrupt Packet, Malware Drop, Leech Worm, Flip Switch, Reroll), defence
  (Firewall, Bulwark, Shield Wall, Duck, Patch Up, Sanitize, Armor Plate, Stim Patch) and
  utility (Hot Patch, Power Tap, Data Surge, Scrap Code, Static Shock, Overload, Arc
  Flash). Direct-damage cards stay small (the wheel is the damage engine, GDD pillar).
- **Firmware 6 → 18**: Overvolt, Bulkhead, Siphon, Static Coat, Barbed Wire, Tracer,
  Coolant Loop, Skimmer, Counterstrike, Nanite Mesh, Power Cell, Recycler. Heat and Cycle
  Firmware have per-combat limits.
- **Daemons 10 → 24**: Warm Boot, Shield Cache, Idle Armor, Adrenal Loop, Fail Forward,
  Feedback Loop, Tuning Fork, Static Field, Cascade, Salvager, Field Medic, Bounty Code,
  Rack Skimmer, Log Wiper.
- **Run-level Daemon hooks apply their data effects.** `NetrunSession._apply_hook_effects`
  applies Heat, Cycles, banked Schematics and healing for ON_COMBAT_END (now fired after a
  won fight), ON_SERVER_RACK_CAPTURE and ON_NETRUN_COMPLETE hooks. Before, only custom
  handlers and netrun-complete Heat worked.
- **Defense assets 3 → 8**: Railgun, Flak Array, Sentry, Tar Pit, Honeypot, using the
  existing targeting modes (highest damage, lowest integrity) and range 0 (own node).
- **Shop slices 7 → 12**: Atk 10, Crit 16, Heal 6, and new Shield 8 and Evade 2 (GDD 11.2's
  examples). Heal 6 gives the Nanite Mesh Firmware a slice to live on.
- **Events 19 → 40**: 21 written events. Nineteen are Solace-only; two (Rival Crew, Ghost
  Market) are corporation-neutral so later corporations share them. Every choice resolves
  (test), rewards include the new cards, Firmware, Daemons and assets.
- **Balance** after the pools (8 seeds, `tools/simulate_campaign.gd`):

  | Class | ICE | Won | Mean runs | Deaths |
  |---|---|---|---|---|
  | Breaker | 0 | 8/8 | 14.8 | 1.8 |
  | Breaker | 5 | 7/8 | 26.4 | 3.5 |
  | Wrecker | 0 | 8/8 | 14.6 | 1.8 |
  | Ghost | 0 | 8/8 | 22.6 | 1.6 |
  | Phantom | 0 | 8/8 | 23.6 | 1.5 |
  | Rigger | 0 | 8/8 | 20.3 | 1.9 |
  | Overclocker | 0 | 8/8 | 20.3 | 1.9 |
  | Botnet | 0 | 8/8 | 20.6 | 3.0 |
  | Hivemind | 0 | 7/8 | 18.0 | 0.8 |

- **Why the bot changed.** With 3x the pools the bot's "take option 0" policy stopped
  finding what beats Solace, and its campaigns fell to 2-5 wins in 8. A ranking run
  (every Daemon and card against the T4 boss, 12 seeds each) showed what matters:
  anti-corruption cards (Sanitize 9/12, Hot Patch 8, Cleanse and Armor Plate 7; the boss's
  Dose corrupts your wheel), Adrenal Loop 11/12, Kernel Sync 9, Zero Day 7, and the Heat
  sinks (Clean Signal alone removed 116 Heat per M6 campaign). `CampaignSimulator` now
  drafts cards, Firmware and Daemons by those measured values, skips self-damage and
  random cards, and spends surplus Schematics on Heat scrubs (keeping two recruits in
  reserve). It logs deaths and stalls with the enemy, and the boss loadout.
- **Enemies strengthened** ("when in doubt, up elite and boss strength"): the smarter bot
  finished campaigns in 12-16 runs. Elites +25% HP (Claims Adjuster 90 -> 112, Recall Unit
  85 -> 106, Account Manager 120 -> 150), Renewal Engine 300 -> 360 HP, and enemy damage per
  tier 1.2 -> 1.3. ICE 5 now matches GDD 11.8 pacing (26 runs vs 24); ICE 0 is the easier
  entry. GDD A.3 is annotated.
- **Ghost ring back to Pierce / x2 / Echo.** Against the boss Pierce did not help (the stall
  is damage against the heal, not block): Pierce / Echo / blank won 4/12 boss fights,
  Pierce / x2 / Echo 9/12.
- **Hive Core keeps the half retrigger** (like the Swarm Core) with 4 drones (Mk2 5) that
  do not persist; without it the Hivemind stalled against the boss.
- **Feedback Loop fixed**: it hit "the target", which is you when the card targets your own
  wheel; it now hits every enemy.

### 2026-09-24 — M6 Class roster: Ghost, Rigger, Botnet and four alternatives (GAP_ANALYSIS P0 1–2, P1 5)
- **Recruitment by class** (P0 1): `CampaignRules.available_classes` / `class_available`
  read the Profile unlocks; the Breaker is always available. HQ shows one Recruit button
  per available class and a "Crew:" picker on the new-campaign panel;
  `RunManager.new_campaign` falls back to the Breaker for a locked class.
- **Unlock costs**: base classes 80 Schematics (GDD 3.4), alternatives 60 (implementer's
  call: a variation is worth less than a new class). Alternatives do not require their
  base class to be unlocked first.
- **Botnet drones persist** (P0 2): `HubCoreData.drones_persist`; living drones are saved
  on `RunState.drones` after a victory and re-docked (with their HP) at the next fight of
  the run through the "drones" combat override.
- **New hub fields**: `max_ram_bonus` (Rigger) and `free_resistance_nudges` (Ghost: the
  first N nudges on an enemy wheel each turn ignore resistance, event "ghost_nudge").
- **PARASITE** is a new `RC.Status` (value 4): the slice resolves at
  `config.parasite_multiplier` (0.5) until cleansed. The Swarm Core hook plants it on the
  target's slice under the matching pointer after a Perfect on a DEPLOY slice.
- **Station bonuses** (GDD 5.2) from the class's `station_bonus` effect type:
  FREEZE = hold (Ghost: a threat entering the node is held once, 1 step), HEAL = regen
  (Rigger: +5 integrity after each wave and at raid end), DEPLOY_DRONE = free turrets
  (Botnet: `config.station_deploy_asset`, the Turret, for this raid). Rank scales each by
  `station_bonus_multiplier`, counts rounded.
- **Freeze cooldown** (found by the class simulation): a wheel that skipped its respin
  because it was frozen cannot be frozen again until it has respun
  (`WheelState.respin_skipped`, event "freeze_blocked"). Without it an Anchor segment
  landing a Perfect on a non-damage slice locked the wheel forever: a stalemate.
- **Every class needs burst** (found by the simulation): the Renewal Engine heals 10 a turn
  and only the Breaker could outpace it (its Perfect resolves the slice twice). GDD 5.2 is
  extended, not replaced: the Ghost Perfect also resolves the slice twice; the Rigger and
  Botnet Perfects also resolve it again at half (Botnet on any slice). Hook effects fire
  once per resolution (the existing Breaker Mk2 rule), so a retriggered Botnet Deploy
  plants its Parasite twice and a Rigger Perfect refunds twice.
- **Wheels are interleaved** so neighbouring slices differ and a one-tick miss does not
  land on the same slice type. Values are placeholders tuned by simulation:
  Ghost Atk 14, Def 6, Atk 14, Evade, Def 6, Miss; Rigger Atk 16, Def 6, Atk 14,
  Shield 5, Def 6, Miss; Botnet Atk 16, Deploy, Atk 16, Deploy, Def 8, Miss.
- **Rank 1 rings**: Ghost Pierce / Echo / blank; Rigger Accelerator / x2 / Echo; Botnet
  Echo / Corrupt / x2. Rank 3 swap options are the remaining segments. The Anchor moved out
  of the Ghost's default ring into its options.
- **Exclusive cards** (two each): Ghost Step, Blind Spot; Torque Wrench, Hot Swap; Spawn
  Drone, Parasite Pulse. **Mk2 cores** at Rank 2 for every class. Barks for every class.
- **Alternatives** (GDD 3.4, "same deck + different core"): `ClassData.alternative_of`;
  `pool_class_id()` makes an alternative draw its base class's exclusive cards and speak
  its barks.
  - *Wrecker* (Breaker): no spin bonus; Perfect resolves again at 1.5x.
  - *Phantom* (Ghost): a free nudge at each turn start; Perfect evades and resolves twice.
  - *Overclocker* (Rigger): +2 max RAM; Perfect gains 2 RAM and resolves again at half.
  - *Hivemind* (Botnet): up to 5 drones that do not persist; Perfect docks a drone and
    resolves again at half.
- **Balance** (`tools/simulate_campaign.gd -- 8 0 class=<id>`, ICE 0, greedy bot):

  | Class | Won | Mean runs | Deaths |
  |---|---|---|---|
  | Breaker | 8/8 | 25.9 | 4.9 |
  | Wrecker | 8/8 | 25.8 | 5.3 |
  | Ghost | 7/8 | 25.5 | 4.4 |
  | Phantom | 7/8 | 23.5 | 2.9 |
  | Rigger | 8/8 | 15.4 | 1.8 |
  | Overclocker | same as Rigger (see below) | | |
  | Botnet | 8/8 | 19.1 | 3.0 |
  | Hivemind | 8/8 | 24.0 | 3.8 |

  The bot never spends free nudges or RAM above what its hand costs, so the Rigger and
  the Overclocker play identically in simulation (every seed matched). Their difference
  (free nudges vs banked RAM) only shows with a human. Single slice values swing the
  results a lot (Rigger Atk 14/14 took 36 runs, 16/16 takes 15), so 8 seeds is a coarse
  tool.

- Dev shortcuts: `--demo-classes` (HQ roster with every class) and `--demo-class=<id>`
  (netrun) bypass Profile unlocks in the demo save slot only.
- The simulator logs which enemy a stuck fight was against.

### 2026-09-24 — Vertical-slice fixes, batch 5: gap analysis pass 2 and the balance simulation
- **Rank gating uses the operative's own class** (V1): `RunManager.launch_error` passes the
  operative's ClassData; `CampaignRules.launch_error` refuses a mismatched class instead of
  silently gating with the wrong Rank table.
- **Grid map clicks select a Site** (V2): the Site's row (status and every action) is
  listed first under "SELECTED >" and the Site gets a cell_acid ring on the map.
- **Netrun panels are zined** (V3): rewards and Modem stock are zine stickers (cards show
  RAM cost, stock shows the Cycle price in the cost circle, Firmware/Daemon offers show
  none), street/corporate events sit on a ZinePanel, DISPATCH events on a clean dark strip
  (never zined), the run end is a stamp plus a torn note.
- **Balance simulation** (V4): `CombatBot` plays greedily from the End Turn preview (the
  information a player has) and never plays random-outcome cards; `CampaignSimulator`
  plays whole campaigns with fixed policies; `tools/simulate_campaign.gd -- <seeds> <ice>
  [verbose]` prints pacing. A campaign takes 3-25 s. The first runs found four real
  problems, fixed as below; the numbers after the fixes (8 seeds each):

  | | GDD 11.8 | ICE 0 | ICE 5 |
  |---|---|---|---|
  | bot wins | — | 8/8 | 6/8 |
  | runs | ≈ 24 (fast 8) | 25.9 (fastest 9) | 21.0 |
  | raids | ≈ 7 (fast 3) | 5.3 | 6.1 |
  | Heat peak | 85-90 at ICE 5 | 78 | 84 |
  | hours | 6 h 35 m | 6.9 | 5.8 |

- **Home server patch** (found by the sim: home damage was permanent while Schematics
  piled up): HQ "Patch home" restores integrity at `home_repair_cost_per_point` (1)
  Schematics per point; partial patches buy what the Schematics allow. GDD 3.3 annotated.
- **Retaliation raids narrowed** (found by the sim: 8 raids in 8 runs): only Exploit
  extraction at Heat ≥ `retaliation_min_heat` (50) provokes one; Heat objectives never do
  (they are sinks). Supersedes the batch 2a rule. GDD 4.4 annotated.
- **Patrol runs** (found by the sim: a soft-lock when every Site is used up and no
  operative has Rank 3): any cleared or claimed Site except home and the boss can be run
  again as a full netrun with normal loot, Heat and Rank but no objective; completion leaves
  the Grid unchanged (node passives still apply). Launch kind "patrol"; the Grid lists them.
- **Enemy damage scales separately from HP** (found by the sim: every Rank 3 Breaker died to
  the T4 Renewal Engine, whose Crit at 1.6^3 hit for 98 against 60 HP): HP keeps
  `enemy_scale_per_tier` 1.6; slice outputs use `enemy_damage_scale_per_tier`, tuned to
  **1.2** by simulation (1.6: 2/8 wins and 41 runs; 1.35: 3/8; 1.2: 8/8 at 26 runs). The
  designer's ruling stands: both scales hit normal enemies, mini-bosses and the boss.
  `CombatantState.hp_scale` lets satellites inherit the host's HP scale. GDD 11.6 annotated.
- **The bot skips Burner Firmware** (Heat per trigger); a player weighs that cost too.
- **M5 "Vertical completion"** is recorded in MILESTONES.md with its acceptance list.
- **Schema changes**: `CampaignConfigData.home_repair_cost_per_point / retaliation_min_heat /
  enemy_damage_scale_per_tier`, `CombatantState.hp_scale`. Smoke test batch 5 extended.

### 2026-09-24 — Vertical-slice fixes, batch 4: menus, platform and onboarding (GAP_ANALYSIS §2.5)
- **Title scene** (`scenes/menu/title_scene.tscn`) is the main scene: Continue (the most
  recently saved numbered slot), Campaigns (three slots with corporation / Heat / ICE /
  runs / state, New / Load / Delete with a confirm), Tutorial, Codex, Stats &
  achievements (profile numbers, achievement list, the last 20 runs), Options, Quit
  (confirm). Saves carry `saved_at`; `SaveService.list_campaign_slots()` scans the save
  directory; test and demo slots are never offered.
- **Pause menu** (`PauseMenu`) replaces the bare accessibility popup on Esc in every
  scene: Resume, Options (the full `SettingsPanel` inline), Codex, Save & quit to title,
  Quit to desktop (confirm). The scene variable keeps its `_settings_panel` name so the
  keyboard test still checks it toggles.
- **Options** in five sections: Accessibility (unchanged), Display (windowed /
  fullscreen / borderless, resolution presets, v-sync, fps counter), Audio (master, music,
  SFX), Controls (rebind the twelve combat/menu actions by pressing a key; card keys stay
  1-9; Escape cancels; Reset restores the project defaults; bindings persist in
  `Settings.keybinds` and are applied to the InputMap at start-up), Language (locales
  with a loaded translation). Display changes are no-ops headless.
- **Autosave indicator**: Fx shows a marker "SAVED" that fades whenever SignalBus reports
  a completed save; **fps counter** in cell_acid top-right when enabled.
- **Tutorial** (`TutorialOverlay`): seven zine steps over the first fight (wheel, precision,
  resistance, cards & preview, rewind, End Turn, Heat & banking); steps with a trigger
  advance on the matching engine event (nudge, card, rewind, turn_start), the rest on
  Next; Skip or Finish sets `Settings.tutorial_done`. Starts automatically on a new
  profile's first fight (never headless) and from the title's Tutorial button
  (`RunManager.pending_tutorial` → the combat scene).
- **Achievements** (`Achievements.DEFS`, evaluated in `sync_profile_with_campaign`): First
  Blood, Banked (10 Racks), Breach, Clean Hands, Average Is a Lie (ICE 5), Cold Storage
  (ICE 10), Purge Survivor, The Wall (20 raids), Perfectionist (500 Perfects), Final Final
  (defined, unreachable until REBEL_CELL). The narrator announces new ones through
  Dialogue. `ProfileState.stats` (perfects, racks, cycles, runs per tier) and
  `run_history` (20 entries) feed the stats screen.
- **CI and export**: `.github/workflows/ci.yml` runs import, GUT, the schema smoke test,
  content validation and checks that `assets/text/strings.csv` is current, then exports
  Windows and Linux builds as artifacts (Godot 4.7.2 via setup-godot). `export_presets.cfg`
  (Windows, Linux, macOS; no credentials) is committed, so it left `.gitignore`.
  `application/config/version` is 0.9.0 and the title shows it.
- **Controller support** stays out of the vertical slice (GDD 9.5: PC mouse + keyboard);
  it remains a P2 horizontal item.
- **Performance**: TECH_SPEC's 1080p target still needs a human run; the fps counter is
  the tool for it. The core stays under 1 ms per turn in the automated check.

### 2026-09-24 — Vertical-slice fixes, batch 3: narrative, dialogue, subtitles, codex, text export (GAP_ANALYSIS §2.4)
- **Line database** (`LineSetData` of `VoiceLineData`): lines are keyed by moment
  (`site:<id>`, `raid:<id>`, `threshold:<heat>`, `boss/win/loss`, `run_start/complete/died`,
  `rack`, `bark:<trigger>`, `dj`) and carry a `drift_stage` and `dispatch_clue`. The
  **Dialogue** autoload picks a line deterministically (hash of key + salt, ties by text)
  and never uses global RNG; **DISPATCH drift** (GDD 8.2) is a profile stage: 0 for the
  first two campaigns started, 1 from the third, 2 from the sixth; a higher stage replaces
  the human line and those lines are the clues (impossible timestamps, evenly spaced
  breaths, "the projection allowed for it").
- **Subtitle bar** (GDD 9.6): bottom-centre CanvasLayer; speaker name; DISPATCH and Corpo
  on a dark strip in amber/corporate colour (clean system text, STYLE_GUIDE 3), everyone
  else on paper. Honours `Settings.subtitles`; `line_spoken` fires regardless for voice-over
  later; `history` feeds the codex's "lines heard". Queue of six, timed by text length.
- **Content**: 55 DISPATCH lines (a briefing for all 32 Solace Sites, boss/win/loss with
  drift variants, threshold lines, run lines), 8 Solace Collections raid warnings, 14
  Breaker barks (perfect, miss, hurt, victory, defeat, deploy, jack_in, boss; at most one
  per trigger per turn, never in headless/reduce-effects), 8 pirate-radio DJ lines at HQ
  (two carry stage-1/2 clues). Barks are per class (`LineSetData.class_id`), so each new
  class ships its own set.
- **Six written Solace story paths** replace the placeholders: Recall Notice, Clinical
  Trial, Terms of Service, The Cure, Ghost Patient (every beat a DISPATCH clue; beat II
  triggers the STORY raid; foreshadows `dispatch`) and Hostile Takeover (foreshadows
  `meridian`). Each has a premise, 3 beats in Exploit order, 2 bonus beats and a finale.
- **Corporations 2–4 named** (open question from the gap analysis, my call): **Meridian
  Freight Systems** (autonomous logistics; threats are fleet drones; Exploits: manifests,
  routing keys, fleet firmware), **Halcyon Civic** (municipal surveillance contractor;
  threats are wardens; Exploits: camera keys, warrant authority, the civic ledger) and
  **Orbital Commons** (satellite data commons gone private; threats are uplink hunters;
  Exploits: ephemeris, ground-station keys, the commons charter). Hostile Takeover points
  at Meridian. Horizontal work builds them.
- **Codex** (GDD 8.1): an HQ/start-screen panel built from `Codex.entries()` (slices,
  statuses and precision, cards, Firmware, Daemons, ring segments, enemies, nodes, assets,
  threats, lexicon) plus the last six lines heard.
- **Text externalisation** (GDD 10): `TextDb.key_for(res, field)` gives every content string
  a stable key (`CardData.jolt.description`); `tools/export_text.gd` writes
  `assets/text/strings.csv` (`keys,en`, 389 strings) keeping any locale columns already
  there; Godot's CSV importer produces the `.translation` files; `TextDb.t(res, field)`
  returns the loaded translation or the content text, so untranslated builds never show
  keys. `Settings.language` sets the locale. UI strings go through `TextDb.ui(key,
  fallback)` as they are touched. Voice recording stays out of scope for code (the
  `audio_path` field on lines is the hook).
- **Schema changes**: `VoiceLineData`, `LineSetData` (new), `Settings.language`, the
  `Dialogue` autoload (after Fx).

### 2026-09-24 — Vertical-slice fixes, batch 2b: Solace at size, events, map and raid presentation
- **Solace City Grid is 32 Sites** (GDD 4.1: 30-40), generated by a script and checked in:
  home → ten T1 Sites (all touch home, so the opening offers ten runs); eight T1 open one
  T2 each (Intel, Breach, Virus among them), every T2 opens a T3, every plain T3 reaches
  the Renewal Engine (minimum path stays T1 → T2 → T3 → boss); four Heat objectives
  (Scrub Records −5 off t1_a, Purge Camera Logs −5 off t1_i, Wipe Biometrics −8 at T2 off
  t1_j, Burn the Ledger −8 at T3 off t2_e, so ICE 2 switches off Wipe Biometrics first);
  eleven locked cross-links opened by the Intel Exploit or an Icebreaker. Slice ids
  (`t1_a`, `t2_intel`, `t3_core`, `scrub_records`, `renewal_engine_site`) are unchanged so
  saves and tests carry over. GDD A.6 is now historical.
- **Terminal events: 19** (5 placeholders kept + 14 written): corporate memos (Continuum
  pricing, clause 44, the silent recall), street-merc trades, an auditor on break, the
  dosage cabinet, a honeypot, a Daemon broker and a Burner vendor, the Patient 0000-0000
  ghost record, **a rescue** (Locked Ward: 12 HP or 60 Cycles for a runner of a roster class) and the
  **DISPATCH clue chain** (Early Reply at T1, Escrow Receipt at T2, Voice Note at T3, all
  `dispatch_clue` + `foreshadows = dispatch`). Events honour `min_tier` (the pool filters
  on the run's tier). Original slang only (leash, subbie, bricked, ghosting).
- **Netrun map as a wireframe graph** (`NetrunMapView`): layers left to right, glyph per
  node type, current node cell_pink, reachable nodes cell_acid with a glow, visited nodes
  dimmed, Heat cost labelled; click a reachable node or press 1-9.
- **Raid playout** (`RaidPlayoutPanel`, GDD 7.2/9.3): the precomputed events are grouped
  by step (setup = link freezes/openings), shown at 0.9 s per step with 1×/2×/4× and Skip;
  threat markers move on the `GridMapView` (corporate dots + names), frozen links draw in
  resist_gold. Instant (straight to the summary) when headless or under reduce-effects,
  so the integration tests and the accessibility toggle both skip the wait. HQ and the
  mid-run interlude share the panel.
- **HQ screens**: start panel picks the ICE level (0..cap, with the cumulative ladder text)
  and the home-server variant; HQ sells next-run boosts and Profile unlocks and offers
  Rank 3 segment swaps per operative; the Grid lists every installable node type (locked
  ones disabled), an Upgrade button with its cost, switched-off objectives and ICE.
- Dense grids (> 16 Sites) draw smaller blocks with "T<n> <glyph>" labels.

### 2026-09-24 — Vertical-slice fixes, batch 2a: netrun and campaign rules (GAP_ANALYSIS §2.2-2.3)
- **Every remaining `RuleModifierType` is applied**: `HEAT_GAIN_PCT` scales positive Heat
  deltas and `HEAT_SINK_PCT` negative ones inside `HeatRules.add_heat` (a non-zero delta
  never rounds to zero); `PURGE_THRESHOLD` (ICE 17, value 90) makes the PURGE threshold
  fire at 90 (recorded as 100 in `thresholds_fired`); `HEAT_OBJECTIVE_SITES` (ICE 2, −1)
  switches off that many Heat-objective Sites at campaign start, the last by id
  (`CampaignState.disabled_objectives`, read through `CampaignRules.site_objective`);
  `DEATH_HEAT` and `EXPLOIT_HEAT` add to the base amounts before gain scaling;
  `CYCLE_PRICE_PCT` scales every Modem price including removals and overwrites;
  `REPAIR_COST_PCT` scales repairs; `SEIZED_RAID_STRENGTH_PCT` adds to raid strength when
  any entry Site is Seized; `RAID_EXTRA_WAVE` repeats the raid's last wave 5 steps later.
  Modifiers stack multiplicatively with ICE 1's gain (a death at ICE 8 is (10 + tier + 5)
  × 1.1), which is how a cumulative ladder should feel.
- **Node types complete** (GDD 3.2): Compiler Rack (a run launched next to an active one
  starts in the REWARD phase with one 1-of-3 card offer per adjacent Rack), Vault Terminal
  (+3 Schematics per completed run via `passive_effects`, +2 more next to a Firewall Relay
  via `adjacency_bonuses`, raid_priority 2, building it queues the NODE_BUILT raid) and
  Proxy Relay (−1 Heat per completed run; counts as a Relay for reach). Passives and
  adjacency bonuses with trigger ON_NETRUN_COMPLETE are evaluated in
  `CampaignRules.on_run_completed` for active nodes in id order; Disabled nodes give
  nothing. The three new nodes are **Profile unlocks** (30 Schematics each,
  `content/unlocks/`); `claim_error` refuses a locked node when a profile is passed.
- **Node upgrades** (GDD 11.4): `upgrade_node` costs `node_upgrade_costs[level]` (30, 60);
  each level adds `node_upgrade_integrity_pct` (50%) of the base integrity and
  `node_upgrade_asset_slots` (1) slots (`GridState` site `upgrade_level`). Home is not
  upgradable this way (variants cover it).
- **Home-server variants** (GDD 3.1): internal nodes fold into the home server's capacity
  (integrity, asset slots, built-in defenses in `GridState.home_asset_slots /
  home_built_in`) rather than becoming Grid sites; the Bunker variant (40 + 30 integrity,
  1 + 2 slots, built-in turret) is a 40-Schematic Profile unlock. `RunManager.new_campaign`
  takes the ICE level and the variant.
- **Netrun boosts** (GDD 11.4): `NetrunBoostData` (cycles, run-only cards, max RAM bonus)
  listed in `config.netrun_boosts`; bought at HQ into `CampaignState.pending_boosts`, all
  consumed by the next run (`RunState.temp_cards` leave the deck on completion). Warm
  Cache 10 (+40 Cycles), Overclocked Deck 15 (two Jolts), Field Kit 20 (+2 max RAM).
- **Routers drop common Firmware** with `router_firmware_chance` (0.35), 1-of-2 from
  Firmware of rarity COMMON; elites keep 1-of-2 of any rarity.
- **Raid triggers** (GDD 4.4): RETALIATION raids follow every Exploit and Heat-objective
  run and enter from the Site just cleared; STORY raids fire from beats marked
  `StoryBeatData.triggers_raid` (Ghost Patient II); NODE_BUILT raids from nodes with
  `triggers_raid` (Vault Terminal), falling back to the claim raid when a corporation has
  no such template. Solace gained three raid templates and two threats: **Icebreaker**
  (`alters_edges`: opens the first locked link, by id, touching its entry; the route
  stays open) and **Lockdown Unit** (`freezes_edges`: freezes the link between home and
  the neighbour holding the most deployed assets for that raid only; nothing routes or
  shoots across a frozen link). Both resolve in setup so the projection shows them.
- **Stationed operatives** return unharmed from Disabled nodes too (cascade included).
- **Rank counts full netruns only**: Reclaim runs (one fight) no longer raise Rank; the
  breach ends the campaign. `runs_completed` still counts them.
- **ICE progression** (GDD 3.4): `ProfileState.ice_cap_for` = max(3, best on that
  corporation + 3, global best − `new_corp_ice_offset`), capped at 20. A fresh profile
  chooses ICE 0–3.
- **Schema changes**: `NetrunBoostData` (new), `CampaignConfigData.netrun_boosts /
  node_upgrade_integrity_pct / node_upgrade_asset_slots / router_firmware_chance /
  router_firmware_choices`, `StoryBeatData.triggers_raid`, `GridState.home_asset_slots /
  home_built_in / frozen_links / upgrade_level`, `CampaignState.pending_boosts /
  disabled_objectives / home_variant_id`, `RunState.temp_cards`. Smoke test batch 5.

### 2026-09-24 — Vertical-slice fixes, batch 1: combat rules (GAP_ANALYSIS §2.1)
Designer instruction: "make calls on every decision". Every call below is logged here
and annotated in the GDD where it changes a rule.
- **ICE/Heat combat modifiers are applied through `NetrunSession.rule_overrides()`**:
  `ENEMY_RESISTANCE` adds passive resistance to every non-satellite enemy (satellites are
  nudged individually and stay at 0); `BOSS_STRENGTH_PCT` multiplies HP and output of the
  final boss **and mini-bosses** (the designer's "up the boss numbers"); `BOSS_EXTRA_POINTER`
  adds pointers to the final boss only, evenly spaced (offsets 15, 10, 20, 5, 25 from
  pointer 0, first free wins) and survives phase changes via the trim/add rules;
  `NO_FIRST_TURN_FREE_NUDGE` zeroes the free nudge on turn 1 only; `STARTING_BUG_CARD`
  puts N **Bug** cards (0 RAM, drains 1 RAM, exhaust, `CardData.offered = false` so it is
  never a reward or Modem stock) into the working deck at run start — a Modem removal
  is the counterplay, and the roster copy only inherits them on completion.
- **HeatGatedEffectData is live**: an enemy's `heat_effects` join its listeners while the
  Heat at combat start (`CombatState.campaign_heat`) is at or above `min_heat`. Content:
  Compliance Officer at Heat 50+ drains 1 RAM per attack ("Audit"); Account Manager at
  Heat 75+ heals 5 per turn ("Retainer").
- **Satellite spawns**: `ON_TURN_START` spawns count every start of turn (turn 1
  included), fire every `every_n`, and only while fewer than `max_active` satellites of
  that template are alive on the host.
- **MIGRATE is telegraphed**: entering a MIGRATE phase stores the layout in
  `WheelState.pending_pointer_ticks` (event `boss_migrate_telegraph`); the pointers move at
  that wheel's next start of turn (event `boss_migrate`). The view draws the pending
  pointers dashed in cell_acid with a "next" tag and flickers the current ones. Account
  Manager gained a 25% MIGRATE phase (pointers 5 and 20).
- **`BossPhaseData.wheel_override`** swaps slices, Firmware, statuses (reset) and passive
  resistance; rotation, pointers and pending migrations are kept; the override's hub
  applies unless `hub_override` is set. The Renewal Engine's ORBIT phase now swaps its
  second Atk 14 for a Crit 24.
- **Player drones (GDD 5.2)** live in `CombatState.drones` as satellites with
  `is_player = true`, host `player`. A DEPLOY slice docks the Hub's `drone` template
  (new `HubCoreData.drone`) on the Deploy slice itself or the next free slice clockwise,
  up to `max_drones`; `DEPLOY_DRONE` effects may pick the slice (`slice_pick`). A drone
  resolves only in a turn where the slice it docks on resolves (any player pointer), at
  full output, against the player's target; enemy attacks aimed at a guarded slice hit
  the drone (same bodyguard rule as enemy satellites). Drones respin with the wheel, do
  not get Kernel Sync or Daemon listeners, and die like satellites (deaths of combatants
  spawned mid-resolve are reported the same turn). Drones persisting between combats
  (Botnet passive) is left to the Botnet class work.
- **Rule-breaking Daemons**: Linked Bus echoes nudge *actions* (not nudge cards) on
  enemy wheels to your wheel, free, ignoring resistance; Stolen Intent fires automatically
  once per combat when your first pointer would resolve Miss and the target's first
  pointer would not, swapping the two slices (own tiers kept) through the new
  `ON_RESOLVE` trigger that hands handlers the collected resolutions; Twin Pointer adds a
  pointer 15 ticks from yours at combat start (`ON_COMBAT_START` Daemon hooks now run in
  `begin_combat`) and halves max RAM rounding up (`CombatState.max_ram`, 12 → 6); Botnet
  Seed docks a 1-HP `seed_drone` on the Perfect slice, max 2 seed drones alive.
- **Ring segments** Corrupt (ON_SLICE_TRIGGER → CORRUPTED on the target's slice under the
  matching pointer, clamped to its last pointer), Anchor (ON_PERFECT → FREEZE own wheel),
  Accelerator (ON_SLICE_TRIGGER → `DOUBLE_NUDGE_CARDS`: nudge cards resolve twice next
  turn, `CombatState.double_nudge_cards[_next]`), Echo (RETRIGGER ×0.5) are data. **Rank 3
  swap flow**: `RankRewardData.ring_segment_options` (Breaker: all four),
  `OperativeState.ring_segment_ids`, `CampaignRules.swap_ring_segment()` (free, any time
  between runs, empty id restores the default), passed to combat as the
  `ring_segment_ids` override.
- **RAM Respin action** (GDD 2.5 lists Respin as a card, 11.3 prices it at 4 RAM; the card
  pool has none): `CombatAction.RESPIN` respins your own wheel for `respin_ram_cost`, is a
  random event (checkpoint) and previews exactly. Key X.
- **Combat UI**: chosen-slice picker (F cycles, auto = none) and card direction picker (D)
  feed `CombatAction.slot_index` / `direction`; random effects (Respin, random slice picks)
  show **odds** as the slice-type mix of the wheel instead of the roll; right-click
  **inspect** describes the slice, Firmware, status and guard under the cursor (or the
  hub/segments at the centre) via the new `Codex` helper, in the left-column note that
  otherwise lists the installed Daemons; revealed boss phases (Intel) print on the enemy
  wheel; the log strip plays the three passes with a 0.35 s beat between them (instant
  under headless or reduce-effects; the wheels always show the final state at once).
- **Schema changes** (rule 8): `CardData.offered`, `HubCoreData.drone`,
  `RC.Trigger.ON_RESOLVE` (appended), `CombatAction.Type.RESPIN` (appended),
  `WheelState.pending_pointer_ticks`, `CombatState.drones/max_ram/campaign_heat/
  double_nudge_cards[_next]`, `OperativeState.ring_segment_ids`. Smoke test batch 4.
- **Timeline captures** (`docs/timeline/`): the designer asked for screen captures per
  system over time; each batch adds dated frames.

### 2026-09-24 — M4 Look, Feel & Accessibility
- **No approved mockups are in the repo** (STYLE_GUIDE points at a private canvas), so the
  screens follow the style guide's component rules literally: three worlds per screen,
  colour tokens in `Palette`, the three fonts, zine kit elements by name (Polaroid,
  ransom-note Heat, marker RAM tally, torn-paper log strip, SEND IT stamp, card stickers,
  graffiti tag, wanted poster, pirate radio, JACK IN, THE PLAN sidebar). Automated
  layout rules: zine elements never intersect a wheel's disc; player wheel `cell_pink`,
  enemy wheels `corp_*`; each screen shows its world background.
- **Fonts** (Permanent Marker — Apache 2.0, Anton and Share Tech Mono — OFL 1.1) are
  vendored from github.com/google/fonts with their licences in `assets/fonts/`.
- **Effects architecture:** one `Fx` autoload (CanvasLayer) owns the scanline / flicker /
  chromatic overlay (all three are shader uniforms), the Heat distortion pulse, screen
  flashes and the jack-in / jack-out transition. `Settings.reduce_effects` hides the
  overlay, zeroes the distortion, freezes background animation and skips freeze frames and
  stutter shakes. The glow and paper shaders are static and stay on.
- **Flash limiter** is a pure sliding-window class (`FlashLimiter`, 3 per rolling second)
  used by `Fx.flash()` and by the automated event-stream check, which maps the flash-worthy
  combat event types (Perfect retrigger, boss phase, Heat threshold, combat end, Zero Day)
  onto a timeline and asserts no one-second window holds more than three.
- **Without-colour readability:** a distinct glyph per slice type (▲ ✦ ■ ◇ ⬢ ⬡ ✚ ◈ ✕) and
  per status (☠ ⚡ ⌗) plus text tags; the Miss slice has a dashed outline; resistance is
  labelled, not only gold.
- **Keyboard play:** 1–9 play cards, Q/E nudge, W nudge wheel toggle, R ring toggle, T card
  target toggle, Tab target, Space end turn, Z / Ctrl+Z rewind, Esc settings; cards and the
  stamp are focusable.
- **Placeholder audio is generated in code** (`AudioDirector`): ratchet ticks, spins as
  decelerating click runs, flip clack, latch/click/stutter/static precision feedback, and
  4-second loops per music context with a Heat layer for combat. Real assets swap in behind
  the same API.
- **Performance:** fps at 1080p cannot be measured headless; the core budget is enforced
  by test (< 1 ms per resolved turn including state duplication) and every effect is a
  cheap 2D shader or `_draw` call that reduce-effects can disable.

### 2026-09-24 — M3 Campaign & Raids
- **Grid runtime state** (`GridState`) records per Site: status (corporate / cleared /
  claimed / Seized), installed node id, integrity, condition (OK / Disabled), deployed
  assets and the stationed operative; plus home integrity and Intel-opened links. Layout
  stays in `CityGridData`. `NetworkNodeData` gained an `id` so nodes are content ids.
- **Heat thresholds** (`HeatRules`): events fire on upward crossings not yet in
  `thresholds_fired`; the MAJOR/PURGE raid goes to `pending_raids`, MINOR complications to
  `pending_complications` (consumed by the next netrun: shop stock −1, elite +25%).
  Modifiers are read live (`CampaignState.rule_modifier`), so they switch off by
  themselves below the threshold. ICE levels ≤ `ice_level` stack with them.
- **Raids resolve at HQ** (between runs). Threshold raids reached mid-run wait in the
  queue until the operative returns; the "mid-run interlude" of GDD §4.4 is deferred
  (open question). Setup projection and playout are the same pure `RaidResolver.resolve`
  on copies, so projection always equals the result.
- **Raid step rules** (TECH_SPEC §7 filled in): threats spawn wave *k* at step 1 + 5*k*
  at the entry Sites (corporate or Seized Sites adjacent to the territory; the boss Site
  as a last resort). Movement follows shortest paths (ties by Site id) toward the routing
  target: home, the highest-value node (`raid_priority`, then install cost) or the weakest
  node; a Decoy overrides the target. Entering a live claimed node (or home) ends the
  step's advance; Disabled and unclaimed Sites are passed through. A threat camps on its
  target node until it falls. ICE Locks hold each threat once per lock. Assets and
  built-in defenses fire per node in Site-id order (FIRST_IN_PATH = nearest to home,
  ties by content id then threat id). Node damage: 0 → Disabled, `floor(excess ×
  cascade_ratio)` to each adjacent claimed node (no chaining); a threat ending a step on a
  Disabled node Seizes it; a Seized Site loses its node, assets and station; damage at
  home reduces integrity, 0 = campaign lost; a threat that reaches home is done. Step cap
  30 then Seizes every node still occupied. Win = every threat destroyed → RaidData
  reward; otherwise +5 Heat. RAID_STRENGTH_PCT scales threat integrity and damage.
- **Claiming** needs a cleared Site adjacent to home or to a live Relay/Firewall Relay
  ("Relay lets you claim Sites beyond it"), costs the node's install cost, and provokes a
  TERRITORY_CLAIM raid when the Site touches a corporate or Seized Site (GDD §4.4).
- **Node slots** (content): Relay 1 asset slot, Firewall Relay 2 (+ built-in 3-damage
  turret), Safehouse 1 (+1 station slot), home 2. Station bonuses are recorded but not
  yet applied in raids (open question on scaling).
- **Special runs:** the final breach and Reclaim runs are one-node `NetrunSession`s
  (`kind` boss / reclaim) so save/resume and the netrun scene work unchanged. Reclaim pays
  the 10–20 "Combat" Cycles and offers nothing else.
- **Boss phases** (`CombatResolver._check_boss_phases`) enter after deaths each turn;
  MULTIPLY/MIGRATE set the pointer layout, ORBIT sets `pointer_orbit`, phase spawns dock,
  hub overrides swap the Hub. Breach removes pointers in every layout but never below one;
  Virus corrupts two random non-Miss boss slices at the start; Intel only flags
  `reveal_phases` for the HUD.
- **Story:** one path is picked at campaign start from the corporation's weighted list
  using the `events` stream of the campaign seed; each Exploit reveals the next beat; the
  finale is shown on the win. Solace ships five placeholder paths of 3 beats + finale.
- **Profile** (`ProfileState`, `profile.json`): campaigns started/won/lost, runs completed,
  operatives lost, raids won/lost, best ICE overall and per corporation.
- **State dictionaries are JSON-normalised on `to_dict()`** (`RunState`, `CampaignState`)
  so a saved-and-reloaded state hashes identically (ints become floats either way).
- **Breaker Rank 2/3 rewards** exist only for tier gating (T3 / T4); the Rank 2 Hub
  upgrade and Rank 3 segment options are content for later (CONTENT_SLICES.md).
- **Scenes:** the HQ scene is the main scene (start → HQ → City Grid → launch → netrun
  scene → back to HQ; raids from HQ). RunManager owns profile, campaign, corporation and
  run; scene switching can be disabled for tests.

### 2026-09-24 — M2 Netrun Loop
- **Run randomness** comes from the run's own `RngStreams` (pure core class; `RngService`
  now wraps it) seeded from a run seed drawn from the campaign `map` stream: `map` builds
  the map, `combat` picks enemies and seeds each fight, `rewards` rolls Cycles, asset drops,
  offers and shop stock, `events` picks Terminal events. Stream states are saved with the
  run, so a resumed run continues identically.
- **Map generator** follows TECH_SPEC §6 with non-crossing edges built as monotone chains
  (each node 1–2 forward edges; every next-layer node covered; provably reachable both
  ways). New config: `map_modem_layers` (3–5), `map_elite_layers` (3–6),
  `map_elites_per_layer` (1), `map_terminal_ratio` (0.25). Elite Heat (+1) is charged on
  entering the node; Server Rack Heat is charged on *capture* (11.5 says "capture", and
  Scrubber needs to replace it).
- **Cycles per node:** Router 15–25 (`cycles_router_range`), Elite Router and Server Rack
  30–40 (`cycles_elite_range`); "Combat 10–20" is reserved for non-node fights (Reclaim,
  events). Rewards scale ×1.7^(tier−1); enemy HP and slice outputs ×1.6^(tier−1) via
  `CombatantState.output_scale`.
- **Rewards:** every won fight offers 1-of-3 cards from the shared pool plus the class's
  exclusives (no duplicate within an offer; skip allowed); elite Routers add 1-of-2
  Firmware (the player picks the socket; must fit the slice type); Server Racks add 1-of-3
  Daemons not yet owned, bank `rack_schematics_by_tier` and any unbanked assets. Asset drop
  chance 0.4 per fight from the A.5 assets; assets are unbanked until a Rack.
- **Modem stock:** 3 cards, 2 Firmware, 1 Daemon (prices rolled in the §11.2 ranges), card
  removal at 50 (+25 per removal), slice overwrite 100 (150 for the Miss slot). The
  overwrite options are the distinct non-Miss slices already on the operative's wheel
  (open question: a real slice catalogue).
- **Enemy pools** are derived from content, not a CorporationData (arrives with the City
  Grid in M3): EnemyData with `corporation_id == "solace"`, 6-slice wheel, not boss;
  `is_elite` splits normal/elite. Terminal events: `TerminalEventData` with matching or
  empty corporation, weighted pick.
- **Operative state** (`OperativeState`) carries the current wheel layout (slice ids +
  Firmware sockets), deck, Daemons, HP and Rank; a run works on a copy written back to the
  roster only on completion (death: permadeath, the roster entry is marked dead).
- **Daemon hooks.** Data-driven Daemons are plain listeners in TECH_SPEC order after the
  Hub. Rule-breakers use `custom_handler` scripts with
  `handle(context, state, rng) -> Array[Dictionary]`; combat handlers get every trigger with
  `context.trigger`, run-level handlers get ON_SERVER_RACK_CAPTURE / ON_NETRUN_COMPLETE with
  the RunState. Kernel Sync's +1 applies from the *next* attack after the Perfect.
  Zero Day = 3 × the wheel's best Crit output (else best Attack) at the pointer target.
- **Custom card effects** (`EffectType.CUSTOM` + handler): Ring Lock, Momentum, Calibrate,
  Steady Hand, Undock. Per-combat markers live in `CombatState.flags` / `ring_locked` /
  `ram_bonus_next_turn` / `damage_bonus` so they save, preview and replay like everything
  else.
- **Firmware neighbour rules** add derived resolutions before the passes: Mirror copies the
  neighbour on the landed side (both on Perfect) at the landing's tier; Shunt resolves that
  neighbour instead at ×1.5 and does nothing special on Perfect. Positive offset = landed
  clockwise = neighbour slot +1.
- **Billing Daemon** drains RAM through DRAIN_RAM slice effects (`atk_7_drain`,
  `crit_12_drain`); **Recall Unit** orbit is a new `WheelData.pointer_orbit_per_turn` (+2,
  applied from turn 2 on); **Care Swarm** drones dock on random free slots.
- **Save file:** one JSON per campaign slot (`user://saves/campaign_<slot>.json`) holding
  the campaign, the run (with its live combat session, checkpoint and streams) and the
  campaign RNG. Autosave on entering a node, after each combat, after every reward/event/
  shop step and on quit. A combat's `setup` is JSON-normalised on creation so a resumed
  session hashes identically.
- **Scenes:** the netrun scene is the main scene (start screen → map → embedded combat →
  reward/event/shop → summary). The combat scene keeps its standalone picker for M1-style
  testing (`auto_start`).

### 2026-09-24 — M1 Combat Core
- **Designer rulings applied (from the M0 review):** Godot pin moved to **4.7** (GUT
  9.7.1); elite frequency placeholder 25% confirmed; `BOSS_PHASE_EARLY` dropped in favour
  of a new `RuleModifierType.BOSS_STRENGTH_PCT` (boss HP and damage +25% at ICE 9; the
  old enum value stays so stored numbers keep meaning; GDD §11.9 "bosses change pointers
  earlier" is superseded); minor Heat complications alternate shop stock −1 (10/30/60/80)
  and elite frequency +25% (20/40/70/90); RAM cap is **12** as GDD §2.2/§5.2 already state,
  carried by `ClassData.max_ram` (`ram_regen_per_turn` removed from the config so RAM has
  one source of truth).
- **Flip math.** GDD §2.3's code block and TECH_SPEC §5.1 both say
  `tick = (rotation + pointer + 15 if flipped) mod 30`; the prose ("mirrors… slice order
  reverses") would be `pointer + 15 − rotation`. The code block is implemented; the
  discrepancy is logged as an open question.
- **State references content by id.** `WheelState` stores slice / Firmware / Hub / ring
  segment ids and resolves them through a `ContentLookup` handed to the resolver, so the
  core never touches the ContentRegistry autoload and tests can inject in-memory content.
- **One status per slice.** ENCRYPTED absorbs the next status and clears; OVERCLOCKED
  becomes CORRUPTED after its trigger; permanent Firmware statuses (Hardened, Burner) come
  from the Firmware, not the status slot. CORRUPTED self-damage ignores block/shield and is
  applied in the status pass for every corrupted slice that resolved this turn.
- **Simultaneity.** All pointers are collected before any pass; a combatant reduced to 0 HP
  still resolves the rest of the turn; deaths and the outcome apply after the status pass.
  A dead host takes its satellites with it.
- **Pointer rule.** Every attack instance hits once per pointer of the target wheel; the
  bodyguard check uses the target's slice under *that* pointer. Pierce ignores satellites
  and block but not shield (shield is a separate resource; open question).
- **Retrigger.** RETRIGGER effects (Breaker Perfect hook, Echo) are counted before the
  slice resolves; each extra instance repeats the base action and the slice's listeners.
- **Output rounding:** `roundi(base × multipliers)` (Partial 0.5, Overclock 1.5, ring ×2).
- **Breaker "+1 spin on all cards"** is data: a PASSIVE-trigger SPIN effect on the Hub
  Core; the interpreter adds its amount to every SPIN a card performs.
- **Slice selection for slice-level effects** is a new `EffectData.slice_pick`
  (UNDER_POINTER / RANDOM_NON_MISS / CHOSEN). DOSE = RANDOM_NON_MISS, never an
  already-corrupted slice. Convention: a NUDGE effect with `multiplier 0.0` ignores
  resistance (Jam). Fine Tune's ring and direction come from the action.
- **Enemy targeting:** enemies and satellites always attack the operative; the operative's
  pointer attacks and cards aim at `CombatState.target_id` (Tab / target list), which may
  be a satellite.
- **Checkpoints are detected, not declared:** `CombatSession.apply()` compares the RNG
  state before and after; any action that consumed RNG (End Turn respins, DOSE's random
  slice, Respin, a reshuffle on draw) becomes the new checkpoint. Rewind restores the
  checkpoint and replays the rest. Preview clones the RNG, so the preview of a random
  effect is exact in the engine; the scene deliberately shows DOSE as "random non-Miss
  slice" rather than the exact slot (GDD §2.10 says random effects show odds).
- **Respin** adds `2×30 + rand(0..29)` ticks so views can animate direction and distance;
  the inner ring respins independently; a Respin clears `flipped`.
- **Hub Breach** removes the hub's resistance from the pool at once and disables hub
  passives; the breach counter decrements at the next start of turn (one full turn).
- **Combat scene starts the Breaker at Rank 1** (ring installed) so every M1 mechanic is
  visible; the rank-0 path is covered by tests.
- **Breaker slice values** are placeholders (Crit 12 / Atk 6 / Def 5, matching the schema
  smoke test) because GDD §5.2 lists types only.

### 2026-09-24 — M0 Foundation
- **Engine used for verification: Godot 4.7.2** (only 4.6.2 / 4.7.x are installed on the
  dev machine). M0 kept the 4.3 pin; _superseded in M1_: the designer moved the pin to 4.7,
  so `*.uid` sidecars are now committed.
- **GUT 9.4.0** was vendored in M0; _superseded in M1_ by GUT 9.7.1 (the Godot 4.7 tag).
  `.gutconfig.json` enables `include_subdirs` so `-gdir=res://tests` picks up `unit/`,
  `integration/` and the non-test `helpers/`.
- **Fresh clone needs one import** before the `-s` tools work:
  `godot --headless --path . --import` builds the global script-class cache.
- **`-s` tool scripts compile before autoloads exist.** `tools/validate_content.gd`
  preloads `content_registry.gd`, so the registry looks SignalBus up by node path instead
  of naming the singleton. Other autoloads may name singletons directly.
- **ContentRegistry:** ids are collected from every `.tres/.res` under `res://content`
  *and* from resources nested inside them (Hub Cores, cards, slices…). The same instance
  reached twice is fine; two different instances with the same id is a duplicate and fails
  validation. Files are visited in sorted path order (rule 7: no dictionary-order ties).
  `validate()` runs every resource's `validate()` and prefixes problems with class + id.
- **RngService:** stream seed = `hash([campaign_seed, stream_name])` (TECH_SPEC §4). Save
  representation stores seeds and states as decimal strings because JSON round-trips
  integers exactly only up to 2^53 and `RandomNumberGenerator.state` is 64-bit.
- **SaveService skeleton:** every file gets a top-level `"version"`; `migrate()` walks a
  table of `from_version -> Callable` steps. JSON numbers come back as floats, so loaders
  must `int()` what they read; 64-bit values travel as strings (see RngService).
- **CampaignConfigData schema additions** so every GDD §11 number lives in
  `content/config/campaign_config.tres` (rule 5): `exploit_heat`; Cycle reward ranges
  (`cycles_combat_range`, `cycles_elite_range`, `cycles_router_range`); new group
  **Shop** (card/firmware/daemon price ranges, card removal price + increment, slice and
  Miss-slice overwrite prices); new group **Schematic costs** (rookie, node base, node
  upgrade costs, netrun boost range, Heat purchase amount/cost/increment, class unlock);
  Combat `ram_regen_per_turn` and `respin_ram_cost`. Ranges use `Vector2i(min, max)`.
  `validate()` checks min ≤ max and non-empty upgrade costs. Smoke test batch 3 covers it.
- **Heat thresholds in data (GDD §4.3):** MINOR at 10/20/30/40/60/70/80/90, MAJOR at
  25/50/75, PURGE at 100. MAJOR ongoing modifiers: 25 → ELITE_FREQUENCY_PCT, 50 →
  ENEMY_RESISTANCE +1, 75 → RAID_STRENGTH_PCT +25. MINOR one-time complications alternate
  the two examples the GDD gives (shop stock −1 / extra elite). `event_raid` stays null
  until M3 authors RaidData.
- **ICE ladder in data (GDD §11.9):** one change per level, in the order the GDD lists them
  within each band (ICE 1 = Heat gain +10% … ICE 6 = Heat sinks −15%, matching the schema
  README example). Bands 6–10, 11–15 and 16–20 list four changes each, so levels 10, 15 and
  20 carry no modifier and are marked "Reserved" in their description.
- **Input map (GDD §9.5):** actions `nudge_left` (Q), `nudge_right` (E), `cycle_target`
  (Tab), `end_turn` (Space), `rewind` (Z and Ctrl+Z), `inspect` (right mouse). Physical
  keycodes, so layouts other than QWERTY keep the key positions.
- **Display:** 1280×720 viewport, `canvas_items` stretch, `keep` aspect (TECH_SPEC §10).

## Open questions for the designer

- **Pacing after H15/H16.** With Daemons firing once per landing the bot's Breaker needs
  about 43 runs at ICE 5 (4/8 won), 48 after H17 (3/8), against the GDD 11.8 average of 24. Should enemies
  come down, or Daemons / rewards go up, now that the multi-fire bugs are gone?
- **Rigger at ICE 0 (H15).** With Daemons firing once per Perfect the bot's Rigger wins
  5/8 at ICE 0 in about 36 runs (other classes 6-8/8). Should the Rigger's hub or deck
  get a buff, or is ICE 0 meant to be this hard for it?
- **Final Rack Daemon (H12).** The final Rack offers a card, not a Daemon (a Daemon at
  both Racks made campaigns about three times faster). Should the final Rack get something
  else, such as a rare Daemon on T4 only or an extra Schematics payout? ICE 0 now runs about
  31 runs: is that too long for the entry level?
_(Claude Code: add questions here instead of guessing on design.)_

### From M11, REBEL_CELL (2026-09-24) — decided by the implementer, confirm in playtest
- **REBEL_CELL is hard** (Breaker bot 4/8 at ICE 5, 1/8 at ICE 10). It opens only after
  ICE 10 everywhere, so a human arrives experienced; raise or lower the Mirror factor
  (`config.mirror_output_factor`) after playtests.
- **Custom-handler Daemons** (Kernel Sync, Zero Day...) are not mirrored: their code runs
  on the player's side only.
- **Music** (resolved in H1): each corporation now selects its own contexts.

### From M9, Halcyon Civic (2026-09-24) — decided by the implementer, confirm in playtest
- **Ghost is strongest against the new corporations** (about 10 runs vs 20 for the others);
  Pierce / x2 / Echo plus a full retrigger. Revisit in the horizontal analysis.
- **Halcyon unlock** 140 Schematics (Meridian 120).

### From M8, corporations (2026-09-24) — decided by the implementer, confirm in playtest
- **Meridian vs Solace difficulty**: the bot finds Meridian's ICE 0 about as hard as
  Solace's; as the second corporation it could be harder. The ICE ladder already starts a
  new corporation at (best - 5), which may be enough.
- **Meridian unlock price** 120 Schematics, or should it unlock by beating Solace?
- **Boss stalls**: the bot still reaches the turn cap against The Manifest (Hub Breach and
  Pierce are the counters; the bot does not time them). A soft enrage is an option.
- **Music**: Meridian has no raid music context of its own yet (Solace has solace_raid).

### From M7, pools and Solace depth (2026-09-24) — decided by the implementer, confirm in playtest
- **Solace's key counter is anti-corruption** (Cleanse, Encrypt, Sanitize, Hot Patch). In a
  60-card pool it is offered less often; consider a guaranteed Cleanse-type card in the
  first Modem of a Solace campaign if human players struggle with the boss.
- **Boss stalls**: lower-damage builds still reach the 60-turn cap against the Renewal
  Engine now and then (the bot rarely times Hub Breach). A human can respin or breach; a
  hard turn limit or an enrage is an option if playtests show stalls.
- **Enemy numbers raised** (elites +25% HP, boss 360 HP, damage 1.3 per tier) because the
  smarter bot won too quickly. GDD A.3 still shows the original values with an annotation.

### From M6, the class roster (2026-09-24) — decided by the implementer, confirm in playtest
- **Perfect hooks now carry burst for every class** (Ghost resolves twice; Rigger and
  Botnet again at half). GDD 5.2 listed only the utility part of those hooks. Without the
  burst no class but the Breaker beat the Renewal Engine.
- **Rigger is the fastest class in simulation** (15 runs vs about 25). Trim its Atk 16
  slices if human play agrees.
- **Hook effects repeat per resolution** (inherited from Breaker Mk2): a Rigger Perfect
  refunds RAM twice, a Botnet Perfect Deploy plants two Parasites.
- **Alternatives cost 60** and need no base-class unlock.
- **Freeze cooldown**: a wheel cannot be frozen on consecutive turns.

### From the vertical-completion loop (2026-09-24) — decided by the implementer, confirm in playtest
- **Enemy damage per tier 1.2 instead of 1.6** (HP stays 1.6). Chosen by simulation so a
  greedy bot wins every ICE 0 campaign in about 26 runs; a human with rewind should do
  better. Raise it if playtests find T3/T4 too soft.
- **Patrol runs** exist to prevent a soft-lock; they also let cautious players farm Rank at
  a Heat cost. Cap patrols per campaign if that feels cheap.
- **Late-campaign Schematics surplus**: the bot ends campaigns with 300-700 unspent. Class
  unlocks and more node/boost content (horizontal) are the planned sinks.

### From M1 (2026-09-24) — resolved by the designer on 2026-09-24
- **Flip** is a true mirror, implemented as a rearrangement: slot i's slice (with its
  status and Firmware) moves to slot −i mod n on both rings, docked satellites move with
  their slice, and the rotation is remapped (`r' = −r − 15`) so the tick under the top
  pointer becomes `15 − t` as GDD §2.3 states. Orientation stays clockwise, so nudges and
  spins need no special case; flipping twice restores the wheel. The `flipped` flag is gone
  from WheelState and the GDD code block no longer carries a `+15` term.
- **Breaker slice numbers** Crit 12 / Atk 6 / Def 5 confirmed.
- **Pierce ignores block and shield, not satellites** (GDD §2.7 and §6.4 updated). The
  bodyguard rule applies to piercing hits; the drone takes them.
- **Corrupted self-damage** straight to HP confirmed.
- **DOSE preview** stays hidden from the player (the engine still predicts it exactly).

### From M3 (2026-09-24) — resolved by the designer on 2026-09-24
- **Tier scaling hits everything**, including the final boss (T4 ×4.1) and the new
  **mini-bosses**: every netrun's final Server Rack is guarded by a corporation mini-boss
  (`EnemyData.is_mini_boss`, may have phases). Solace: *Account Manager* (120 HP, Atk 10,
  Def 8, Crit 16, Dose, Shield 5, Miss; resistance 1; at 50% multiplies to two pointers).
  Playtest risk noted: a T4 Renewal Engine Crit is 98 damage against 60 HP operatives.
- **Mid-run raid interludes** are in: whenever a run would return to the map with a raid
  queued, `RunState.Phase.RAID` opens the setup inside the netrun scene (projection, the
  run's own assets and the Armory both deployable, playout). Losing the home server there
  ends the run as ABORTED. Runs that launch with a raid already queued fight it first.
- **Station bonus scaling** (made up): the class `station_bonus` is a DEAL_DAMAGE effect
  whose `multiplier` is the asset damage factor (Breaker 1.5); Rank scales the bonus part
  by `RankRewardData.station_bonus_multiplier` = 1.25 / 1.5 / 2.0 at Ranks 1 / 2 / 3, so a
  Rank 3 Breaker doubles asset damage. It applies to the stationed node and to adjacent
  Firewall Relays.
- **Raid movement details** confirmed as a starting point.
- **Breaker Core Mk2** (Rank 2 Hub upgrade, made up): +2 spin on all cards; Perfect
  resolves the slice twice and refunds 1 RAM per resolution. Operatives fight with the
  highest hub upgrade their Rank has earned (`OperativeState.hub_id`).

### From M2 (2026-09-24) — resolved by the designer on 2026-09-24
- **Shop slice catalogue:** `CampaignConfigData.shop_slices` (Atk 6/8, Crit 12, Def 5/8,
  Shield 5, Evade) with `shop_slice_choices = 3` per Modem; new slices go in the catalogue
  rather than repeating the wheel. Tracked as a horizontal slice in
  `docs/CONTENT_SLICES.md` (new running list: vertical first, horizontal later).
- **Cycles ranges:** implementer's call stands (Router nodes 15–25, elites/Racks 30–40,
  10–20 reserved for non-node fights). Revisit in human playtest.
- **Elite frequency:** node combat type is always known before entering. ELITE_FREQUENCY_PCT
  adds a fraction of an elite per band layer at map generation; when the fraction reaches a
  whole node, one more Router in that layer is flipped to elite (never in place, never after
  the map is shown; each layer keeps a non-elite route). Elite Terminals are a horizontal
  backlog item.
- **Rescued operatives** become a free fresh rookie in the roster (as implemented).

### From M0 (2026-09-24) — resolved by the designer on 2026-09-24
- Godot version → 4.7 pin, GUT 9.7.1. "More elites" → 25% confirmed. ICE 9 → boss
  strength (+25% HP/damage) instead of BOSS_PHASE_EARLY. Minor Heat complications →
  alternate shop stock −1 / elite +25% (implementer's call). RAM cap → 12 (GDD §2.2).
- Still open: **ICE levels 10, 15 and 20** have no listed change; `REPAIR_COST_PCT = 25`
  (ICE 13) and `SEIZED_RAID_STRENGTH_PCT = 25` (ICE 14) are placeholders ("when in doubt,
  up elite and boss numbers" applied); MAJOR-threshold RaidData arrives in M3.
