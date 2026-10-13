# Playtest feedback — quietcarrier · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · session date not recorded

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** quietcarrier
- **Persona / focus / quirks:** Explorer / completionist; Pacing and session length; takes every card reward offered
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 95 wall-clock minutes (903 actions, 744 steps, 1 session; I quit in-game when time ran out)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard, starting roster Breaker, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time. The time box ended at ~95 min, so the outcome is INCOMPLETE. I used the in-game Quit.)
  - Netruns: 6 started, 0 completed (no site was ever cleared), 5 operative deaths. Breaker 1 died on fight 4 (a 112 HP Claims Adjuster), Breaker 2 on fight 2 (Recall Unit, turn 30), Breaker 3 on the L3 Elite Claims Adjuster, Breaker 4 on fight 3 (Compliance Officer, at 6 HP), and Breaker 5 on the L6 Elite Claims Adjuster. The sixth netrun was still going when I quit, with fight 1 won.
  - Highest Site tier reached: T1 · Exploits held: 0 · Sites claimed at the end: 0
  - Raids: 2 played out and the Cell held both times (Core 50→40, then 40→27). Nodes lost: not encountered.
  - Final Heat: 70 (Flagged) · Home server integrity: 27/50
- **Overall enjoyment (1–10):** 4 — the wheel idea is neat, but fights ran very long, my operatives kept dying, and I lost nearly half an hour to map navigation.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Lining up the needle and nudging did feel like a skill once I understood it. The previews were readable. The early fights (Billing Daemon, Collections Agent) were fine. Against resistance-heavy enemies (Triage Unit, Recall Unit, Compliance Officer with resist 4) I couldn't find a way to make progress, so fights turned into 10–30 turn slogs.
  - SEND IT never gave a different result from the preview chips as far as I could tell.
  - Undo behaved as the tutorial said. The Fine Tune aim kept going stale, though: I undid it repeatedly and the RAM readout still showed -1.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen. Patch+ (+50% slice output) was the only Firmware I took that did something clear.
  - Useless / never worth picking: Mirror Flip, which was blocked by enemy resistance most of the time and cost me a lot of time. Fine Tune also felt weak, because a ±1 nudge rarely changed anything.
- **Synergies & archetypes:** I only ran the Breaker. I took every card offered (Nudge Driver, Sanitize, Inner Snap, Data Surge, Flick, Firewall, Snap, Gear Mesh) but never felt a strategy form. It stayed a pile, and I mostly traded blows with whatever was in hand.
- **Card text & clarity:** No. Card descriptions are clipped ("OVERCLOCK your slice under th…", "Blocked while th…"). Fine Tune reads "Two +-1 nudges on on ring." Nudge cards go onto the round Q/E nudge buttons, not onto the wheels. I clicked wheels for about 10 minutes before I understood that. Mirror Flip's "Blocked" tooltip doesn't say why it's blocked.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** netrun too long, because single fights took 10–30 turns, and a netrun that dies at fight 2–3 lasted ~5–25 min. The whole campaign I couldn't judge, since I got through no sites in 95 min; at this pace it looks too long.
- **Netrun map & encounters:** I saw Fights, Elites, a Terminal event (Wellness Kiosk, Locked Ward, Patient Records), a Mainframe shop, and a Rack that I never reached. Events were my favourite part. Costs show as chips, which I liked. One "free" event option (Copy the index) led into a surprise fight. The route often funnelled me into an Elite at low HP with no healing, with no alternative path.
- **City Grid & HQ:** Site choices were hard to make meaningful because I couldn't find a reachable site. Almost every site was locked behind a chain, and I probed locked nodes for roughly 25+ min in total. Reachable sites are marked only by a small orange ring, and the Map Key was collapsed and empty on first open. The reachable sites were off-screen near my marker until I panned with the minimap. I recruited free Breakers at the Market after wipes, which was a good safety net. I spent no Schematics, because I never had enough: Heat Scrub costs 25 and I had 5.
- **Heat:** I could see the number climb (25→70), but I couldn't predict it or manage it. I didn't understand what thresholds did beyond the "Mainframe loses an item" note.
- **Raids:** Setup and playout were understandable and quick (about 20 s). With 0–1 crew and an empty armory there was nothing to defend with, so the outcome felt predetermined. The banner said "RAID IN PROGRESS" while the feed said "Raid over".
- **RNG & fairness (1–5):** 3 — no single cheat moment. What got me was going into Elites at 14–19 HP with no healing and no alternative route.
- **Permadeath & meta-progression:** Deaths felt partly earned (my 10-minute loop in fight 3 cost me HP, and entering fights at 6–19 HP) and partly forced by the map. Free recruits make it painless, so I would start another run. I saw no profile unlocks in this session.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and enemy previews are readable. The RAM readout often showed a stray "(-1)" or "-2" mid-aim, and in two fights it stayed there across several turns. Slice icons, chips like "(3)" and the "FREE NUDGE" label are unexplained. The "AT LARGE" stamp hides max HP on the route-map dossier.
- **Information outside combat:** I looked for the reachable-site marker, the Map Key contents, and a way to revive crew. The Map Key is too hidden. Many tooltips say "orange ring" and "JACK IN", but neither is visible from where you are.
- **Controls:** Q/E nudge buttons did nothing visible on several clicks, and event option clicks twice showed no change until I pressed key 1. Clicking Breaker 5's card in the Crew tab did nothing across ~7 clicks. A misclick opened Abandon Campaign, and its CANCEL ignored the mouse; keyboard closed it. Continue on the loot sheet was blocked by a Firmware "does not fit an OVERFLOW slice" toast until I picked a different slot.
- **Visual feedback:** The FLATLINED stamp and the DELETED stickers are fun. Overlapping stickers garble the "DELETED" text, and the "LOOT" sticker covers the PROCEED label.

## 5. Focus questions (Pacing and session length)

1. **Which part of the loop felt too long? Too short?** Too long:
   - The tutorial sim took ~4 min (turn 14) and dragged after the enemy was nearly dead.
   - Many fights: Recall Unit took 30 turns (~7 min), Triage Unit 15 turns, and Compliance Officer 12+ turns.
   - HQ site-finding took roughly 25–30 min of the 95.
   - Too short: raids (~20 s) and events.
2. **Which animation or transition did you most want to skip?** The per-turn free-nudge phase and the resolve each turn, repeated over 10–30 turn fights. The tutorial's drawn-out ending was a close second.
3. **Would you start another netrun right now? Why or why not?** Yes, tentatively. Free recruits make restarting cheap, and I want to see the Rack and T2 sites. But I'd dread another 15-turn fight against a resist enemy.

## 6. Open feedback

- **Favourite moment or build:** Terminal events with costs shown as chips, and the clean early fights, where the preview chips told me exactly what would happen.
- **Biggest frustration / moment you wanted to quit:** The ~10-minute fight 3 loop (Mirror Flip and Fine Tune against resistance), and later the HQ map hunt for an enterable site.
- **One thing to change or add right now:** Mark reachable sites clearly (an always-visible orange ring and an auto-pan or "next site" button), and cap fight length or make resistance enemies breakable.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Combat RAM readout | 6.4m, 8.9m, 10.2m, 17.3m, 51.4m–53.2m | RAM shows a non-negative value | Stray "(-1)" / "-2" beside RAM, persisting for several turns | wrong | 0050.png |
| 2 | Loot sheet Firmware | 43.7m, 82.6m | Continue works | Toast "does not fit a OVERFLOW slice" blocked Continue until I chose another slot | wrong | 0665.png |
| 3 | Event options | 18.9m, 87.5m | Click selects option | No change on click; key 1 worked | wrong | 0152.png |
| 4 | Crew tab, Breaker 5 card | 57.6m | Click opens or selects the card | No change after 6–7 clicks | wrong | 0452.png |
| 5 | Abandon campaign confirm | 58.0m–58.2m | CANCEL closes the dialog | Mouse clicks ignored; closed via keyboard | wrong | 0459.png |
| 6 | Q/E nudge buttons | 41.5m–42.3m | Visible effect on click | No visible effect | wrong | 0334.png |
| 7 | Patient Records event | 87.6m | "Free" option (Copy the index) is free | Led straight into a combat | wrong | 0697.png |
| 8 | Raid playout banner | 27.8m | Banner matches state | "RAID IN PROGRESS" while the feed says "Raid over" | cosmetic | 0220.png |
| 9 | Map Key | 39.2m | Shows the legend on open | Empty at first open; needed a header click | cosmetic | 0319.png |

**Confusion log:**
- 11.1m — combat — Mirror Flip and Fine Tune "blocked"; I didn't know nudge cards go onto the Q/E buttons — ~10 min, resolved when I noticed the buttons.
- 28.5m–76.7m — HQ city map — couldn't find a reachable site — ~25+ min across many tries, resolved by opening the Map Key and panning the minimap to my marker.
- 41.2m–42.4m — combat — Q/E showed no visible effect — ~1.5 min, resolved by sending the turn.
- 55.4m — HQ — all crew flatlined, no visible recruit button — ~0.5 min, resolved in the Market (free recruit).
- 57.6m — HQ Crew tab — Breaker 5 card unresponsive — ~1 min, resolved by using the map instead.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: quietcarrier
persona: PB-010
focus: pacing
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 5
raids_survived: 2
playtime_min: 95
enjoyment: 4
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: Patch+
weak_picks: Mirror Flip, Fine Tune
bugs: 9
top_frustration: Fights of 10-30 turns against resistance enemies, plus ~25 min lost hunting for a reachable site on the HQ map
top_change: Make reachable sites obvious on the HQ map and shorten or unblock resistance-heavy fights
```