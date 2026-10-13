# Playtest feedback — ferrite · PB-010 · build 19ad76a3a10c260a760667a0d6dde27156508740 · session date not recorded

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** ferrite
- **Persona / focus / quirks:** Roguelite newcomer / Menus, navigation and information / never uses UNDO; right-clicks every new card or icon before using it
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard. Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 60 minutes (905 actions, 1 session; I quit with the in-game Quit and the campaign saved)
- **Campaign setup:** corporation Solace, ICE 0, home server Standard Home Server, starting roster Breaker ×2, campaign code RC1-solace-0-1-home_standard-breaker (shown on the pause menu)
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time). The tutorial was never finished either: the FIGHT WON screen showed no way forward, so I left through the pause menu. INCOMPLETE.
  - Netruns: 1 started, 0 completed. The first fight (Billing Daemon) was won, and the run failed in the second fight (Dosage Dispenser) with 1 operative death (Breaker 1, flatlined on turn 10, layer 2).
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: not encountered
  - Raids: not encountered
  - Final Heat: 11 · Home server integrity: 50/50 at the start; not checked at the end
- **Overall enjoyment (1–10):** 3 — the look is great, but I spent most of the hour hunting for rules the game never told me.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Lining up needles and nudging did not feel like skill to me. I was guessing, because ticks, nudge and the slice icons are never explained.
  - SEND IT vs the preview chips: the SEND IT hover preview was useful (for example "RAM -2", and the Dispenser's Shim hitting me from 12 to 9). I did not see a mismatch.
  - UNDO: never used it, by persona choice. It sits right beside SEND IT, which made me nervous. I cancelled card selections with right-click instead.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless: I never played Overdrive, because "becomes CORRUPTED" scared me. I could not judge its worth. Mirror Flip was often unaffordable at RAM 3.
- **Synergies & archetypes:** I only ran Breaker with a basic deck (Jolt, Brute Spin, Fine Tune, Overdrive, Mirror Flip, then Jam from loot). No strategy came together. I never found a heal card.
- **Card text & clarity:** No.
  - Mirror Flip is truncated to "Blocked while th…" on the card face.
  - "Nudge", "tick" and "CORRUPTED" are not defined in the tutorial.
  - Right-click inspect sometimes did nothing, while hover worked.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** the first netrun fight took about 10 turns (about 25 minutes, mostly spent reading). I can't judge the campaign length.
- **Netrun map & encounters:** the layer-2 route map was hard to read. The legend lists RACK and SHOP, but I could not tell which links lead to them. The route panel showed only "[1] Fight > Fight". I did not see a Rack, Shop or Elite node in my short run.
- **City Grid & HQ:** I only saw the Market (a Breaker recruit for 15 Schematics, and boosts at 10, 15 and 20). I held my 20 Schematics because "Cycles" was never explained.
- **Heat:** not encountered in a meaningful way. It ended at 11, and I could not tell what drives it.
- **Raids:** not encountered.
- **RNG & fairness (1–5):** 3 — I could not tell luck from my own ignorance. At 6 HP, one Jolt flatlined me.
- **Permadeath & meta-progression:** the failure box explained permadeath plainly, and I appreciated that. I did not get far enough to want another campaign.

## 4. UI, controls & audio

- **Information in combat:**
  - HP is easy to see.
  - Deck and discard labels are tiny and the DISCARD label is clipped.
  - The RAM readout confused me for about 20 minutes: a bar like 6/12 with a "(-3)" or "(-2)" beside it, and hatched pink segments.
  - The only RAM explanation was a tooltip on the bar: "pays for cards, respins and extra nudges". It says nothing about negative values.
  - The red "-3" tags on the HP bars were only explained by a tooltip after six turns.
  - The slice icons on the enemy wheel were too small to read.
- **Information outside combat:**
  - The Codex has 211–212 entries across 13–14 tabs, with no search. I never found NUDGE, tick or RAM defined.
  - The "(Esc)" hint on the pause menu exists, but Esc did nothing during the training sim.
  - The Field Kit tooltip is hidden behind the bottom bar.
- **Controls:**
  - The Q/E nudge arrows ignored about a dozen clicks in tutorial turns 5–6.
  - The aim arrow for Fine Tune jumped to the enemy ring, and I couldn't retarget it.
  - Several times the screen looked frozen, but the gear icon showed the game was responding.
  - Esc worked on the FIGHT WON screen but not in the sim.
- **Visual feedback:**
  - "1 LANDS HERE" and the dashed preview arcs were the clearest feedback.
  - The big radial wheel over the map after JACK IN was unlabelled.

## 5. Focus questions (Menus, navigation and information)

1. **Which piece of information did you look for and fail to find?** What a nudge is, what a tick is, what RAM is and what negative RAM means, and what CORRUPTED does. I also never found how to heal. All were absent from the Codex. NUDGE and tick, the Lexicon entries I hunted for, were nowhere in it, though the WEIGHT entry mentions nudges. Nudge was explained only in a tooltip on the Q arrow, about 16 minutes in. RAM was explained only by hovering the bar.
2. **Which screen took the most clicks to do something simple?** The Codex. A single word lookup cost 30+ steps of tab-hopping and scrolling through the Lexicon, which stalled near WEIGHT/MIRROR. A close second was the tutorial FIGHT WON screen: clicks, Enter, Space, Esc and the gear icon never revealed a Next button, and I had to Quit to Main Menu.
3. **Did hover and right-click inspect behave consistently?** No. Hover tooltips were reliable and carried most of the real explanations. Right-click inspect worked on some cards, but gave nothing on Jolt and Mirror Flip across about six tries, and nothing on the Q icon.

## 6. Open feedback

- **Favourite moment or build:** the dashed preview arc and the SEND IT preview. The pause-menu quit prompt, "Your campaign is saved", was also reassuring.
- **Biggest frustration / moment you wanted to quit:** the ~20 minutes on negative RAM, and the tutorial FIGHT WON dead end.
- **One thing to change or add right now:** add a short how-to-play page covering nudge, ticks, RAM and CORRUPTED. Put it in the tutorial and make it reachable from combat. Also add a search box to the Codex, and a visible Continue button on the tutorial result screen.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Tutorial FIGHT WON | 19.1m–20.6m | A visible Next/Continue | None; had to Quit to Main Menu | blocker | 0219.png |
| 2 | Tutorial sim, Q/E nudge arrows | 5.7m–9.4m | Click nudges the ring | Ignored about a dozen clicks | wrong | 0067.png |
| 3 | Tutorial sim, Esc | 11.0m | Opens pause | Nothing; gear icon worked | wrong | 0131.png |
| 4 | Combat, right-click inspect on Jolt/Mirror Flip | 28.2m–28.6m, 17.7m | Card inspect | No change | wrong | 0329.png |
| 5 | Combat, Mirror Flip text | 10.6m | Full text | Cut off at "Blocked while th…" | cosmetic | 0250.png |
| 6 | Combat, RAM readout | 30.0m–51.7m | Clear cost label | (-N) and hatched segments, unexplained | wrong | 0355.png |
| 7 | JACK IN transition | 21.4m | Clear transition | Large unlabelled ring covering the map | cosmetic | 0246.png |
| 8 | Market, Field Kit tooltip | 58.9m | Readable tooltip | Hidden behind the bottom bar | cosmetic | 0672.png |
| 9 | Route map L2 | 46.8m–49.5m | Visible links to RACK | Links not shown; only "Fight > Fight" listed | wrong | 0548.png |

**Confusion log:**
- 1.3m — tutorial sim — "Free nudge" — ~0.2m, resolved by a tooltip on the nudge marker.
- 2.4m–15.6m — tutorial sim — what nudge and CORRUPTED mean — ~13m, resolved only by the Q-arrow tooltip. CORRUPTED was explained later in the Codex.
- 23.0m–23.4m — combat — RAM "(-3)" — ~0.4m, resolved by hovering the RAM bar.
- 30.0m–40.2m — combat — negative RAM — never resolved; ~10m of hunting.
- 52.7m–53.3m — combat — red "-3" tags — resolved by a tooltip after six turns.
- 46.8m–49.5m — route map — where is RACK — never resolved.
- 54.2m–58.2m — Dispenser fight — no heal found, wheel icons unreadable — unresolved; died.
- 58.5m–60.0m — Market — what Cycles and the boosts do — unresolved.

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: ferrite
persona: PB-010
focus: menus-navigation-information
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 1
raids_survived: 0
playtime_min: 60
enjoyment: 3
rng_fairness: 3
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: Overdrive, Mirror Flip
bugs: 9
top_frustration: Core terms (nudge, RAM, negative RAM, ticks) never defined in the tutorial or Codex, plus the tutorial result screen dead end
top_change: Add a how-to-play page and a Codex search, and put a visible Continue button on the tutorial result screen
```