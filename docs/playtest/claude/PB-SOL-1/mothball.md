# Playtest feedback — mothball · PB-SOL-1 · build 52626bcd24d785a8dd7c75b213a52ea639892935 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** mothball
- **Persona / focus / quirks:** Returning after a bad first try (novice) / Raids and cell defense / Quits to title and uses Continue once per session; avoids Elite Routers unless forced. I used Continue several times, not once.
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 52626bcd24d785a8dd7c75b213a52ea639892935
- **Total playtime:** 61 minutes wall-clock (866 actions, several sessions: I quit to title and used Continue a few times, and the game was restarted by the harness after it was closed or crashed around 53.8m, 54.7m, 55.6m, 56.1m and 60.3m)
- **Campaign setup:** corporation Solace Biosystems, ICE 0, home server Standard Home, starting roster Breaker, campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time. INCOMPLETE at run 1, with only the fifth Breaker left and Heat 50.)
  - Netruns: 4 started, 0 completed, 4 operative deaths (Breaker 1 in a Clinic Gate fight vs Collections Agent; Breaker 2 in a T1 Site fight vs Collections Agent, a mutual kill; Breaker 3 in an Elite Claims Adjuster fight; Breaker 4 in a fight vs Billing Daemon). Router/Elite Router/Rack layer numbers were not shown.
  - Highest Site tier reached: T1 · Exploits held: 0/3 · Sites claimed at the end: 0
  - Raids: 1 survived (CELL HOLDS), 0 nodes lost (DOWN 0 / TAKEN 0). A second Collections raid was intercepted at Heat 50 and I never played it out.
  - Final Heat: 50 (Flagged) · Home server integrity: 40/50
- **Overall enjoyment (1–10):** 3 — I could play by the preview numbers but never learned to read the wheels, and four permadeaths in an hour felt like punishment.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - Did lining up the needle and nudging/spinning wheels feel like skill? No. I played almost everything off the preview numbers and never understood the wheels or the "free nudge". I never saw a Perfect land (perfects=0 in every fight).
  - Did SEND IT ever give a different result from the preview chips? Yes, once. On the T1 Site fight, turn 11, the preview said Agent 7 → 0, but the Agent stayed at 7/40 with Guard 6 (0287.png). Most other turns matched, e.g. turn 7 on the same fight (0278.png).
  - Did UNDO / rewind behave as expected? Mostly. Undo rolled back my guessed nudges, and "Nothing to undo" appeared when it should. I also pressed Esc by accident and opened the pause menu.
- **Card balance & utility:**
  - Overpowered / automatic picks: none seen.
  - Useless / never worth picking: Fine Tune and Jolt targeting never registered for me in several fights, so they felt useless. That is a clarity problem, not necessarily a balance one.
- **Synergies & archetypes:** No strategy came together. The deck felt like a random pile, and I took Jam, Data Surge and Tailspin for readability, not synergy.
- **Card text & clarity:** No. Confusing items: "Free Nudge", Jolt's "NEED 1" badge, Fine Tune's "glowing target" prompt, the 1/0 markers on the wheels, the WEAK/PERFECT tags, and the Q/E arrows. Hover tooltips explain things, but a novice would not know to hover.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Netruns ran about 4–6 minutes for the early fights and 10–15 turns for the longer ones. The whole campaign is not judged, since I got through only 4 netruns in the hour.
- **Netrun map & encounters:** Route choices were readable at first. Later I was forced into an Elite fight at 19/60 HP because it was the only lit option. Grid view was unreadable and its buttons barely responded.
- **City Grid & HQ:** Site choices were not meaningful to me because of the lock chain (T2 behind T1, Heat sink behind T2). Hiring a rookie was never findable in the CREW tab. A "FIRE" stamp that I thought I saw on the Breaker card was not there when I zoomed in.
- **Heat:** I could not predict it. T1 jumped Heat 11 → 22, and flatlining added +11 each time. The Heat 25 and 50 raids followed. The thresholds were not obviously unfair, but the escalation felt like piling on.
- **Raids:** The setup screen and projection were readable. Stationing was a blocker (see section 5).
- **RNG & fairness (1–5):** 4 — the mutual kill on the T1 Site fight (Agent DELETED and Breaker BRICKED on the same turn) counted as DEFEAT with no explanation.
- **Permadeath & meta-progression:** Losing the first operative did not feel earned, because the wheels were never taught. The failure screens spell out permadeath clearly. I did not feel pulled to restart.

## 4. UI, controls & audio

- **Information in combat:** HP, RAM and the projected HP changes were easy to see. The wheel markers, "LANDS HERE" and the 1/0 numbers were not explained.
- **Information outside combat:** The map is very busy. I wanted a plain Heat cost per node, and what the flame, key and lock icons mean. The tooltip said T1 was "not reachable until a linked Site is cleared", yet it was the only node I could take.
- **Controls:**
  - Jack In needed many clicks on the first run (0059–0063) and again later (0312–0317, 0510–0513). Enter finally worked at 48.8m.
  - LOOT needed three tries.
  - The loot card frames stayed blank for several waits until I clicked.
  - Clicks on glowing targets (Fine Tune, Jolt) were often ignored.
  - My own map marker and the node at 240,350 ignored clicks.
  - The Quit confirm ignored clicks, Enter and the A key for roughly 6 minutes, and only Esc backed out.
  - The game was closed or restarted by the harness several times around then.
- **Visual feedback:** Previews and result screens were clear, with the HP numbers reading well. I got no sense of impact because no Perfect ever landed. A result screen said DEFEAT while the enemy showed DELETED, which contradicted itself.

## 5. Focus questions (Raids and cell defense)

1. Did the projected outcome in setup match the result? — Yes, but only for an undefended raid. Setup said Home Server 50 → 40, HOLDS, and the playout gave 50 → 40, CELL HOLDS, DOWN 0 / TAKEN 0, Heat 34 → 39 (0487/0489). I never stationed anyone, so I could not test the projection with defense in place.
2. Did you understand why a node went DOWN or TAKEN? — Not encountered. No node went DOWN or TAKEN, and I never found out what those outcomes look like.
3. Did raids feel like a puzzle you could solve, or a tax? — A tax. I could not station Breaker 4 after about 30 tries across the card, the CREW and DEFENSE tabs, and the nodes. The confirm dialog said "Station an operative on a node at HQ first", but no click ever registered, so I played the raid with nobody. The second raid at Heat 50 had one Breaker and projected INTERCEPTED (Home 40 → 27 holds), and I never played it out.

## 6. Open feedback

- **Favourite moment or build:** The failure and result screens tell you plainly what you lost. The save held every time I used Continue (Heat 11, 34 and 50 all came back correctly).
- **Biggest frustration / moment you wanted to quit:** Turn 5 of the T1 Site fight, where I burned many steps on Fine Tune and Jolt targeting that ignored my clicks. The raid stationing dead end and the stuck Quit confirm were close behind.
- **One thing to change or add right now:** Teach Free Nudge and the targeting step in plain text on screen, and make stationing in raid setup actually work and be visible.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Raid setup | 42.3m–46.1m, about 30 clicks | Clicking Breaker 4 stations her on a node | Nothing registered, crew stayed 0, and the dialog said to station first | blocker | 0465.png |
| 2 | Campaign map, Jack In | 5.0m–5.3m, 29.4m–29.9m, 48.3m–48.8m | Jack In responds to the first click | Needed many clicks, and Enter finally worked | wrong | 0063.png |
| 3 | Combat targeting | 19.9m–24.0m, 30.4m–30.9m | Clicking the glowing target stages the card | Clicks ignored on Fine Tune and Jolt targets | wrong | 0225.png |
| 4 | Fight result | 27.8m, 52.0m | A clear winner | Both sides at 0 HP, the screen said DEFEAT while the enemy showed DELETED | wrong | 0540.png |
| 5 | Combat preview | 26.8m | Agent 7 → 0 as previewed | Agent stayed at 7/40 with Guard 6 | wrong | 0287.png |
| 6 | Loot screen | 34.6m–34.9m | Cards visible on the pick screen | Blank card frames until I clicked | wrong | 0368.png |
| 7 | Loot button | 7.5m | LOOT opens on the first click | Needed three tries | wrong | 0087.png |
| 8 | Campaign map | 14.3m–15.0m | The node and my marker take clicks | Both ignored clicks for about six steps | wrong | 0167.png |
| 9 | Quit confirm | 54.2m–60.2m | QUIT [A] quits | Ignored clicks, A and Enter. Only Esc backed out. The game restarted several times. | blocker | 0562.png |
| 10 | Route map | 34.4m–36.4m | Grid view and Confirm respond | Buttons barely responded, and Confirm stayed greyed until the node was clicked | wrong | 0380.png |
| 11 | Node info card | 35.4m | A real Cache description | Reads "Cache: placeholder text" | cosmetic | 0374.png |
| 12 | Loot toast | 35.1m | Deck count consistent | The toast said 11 while the deck button said 12 | cosmetic | not shown |
| 13 | Raid playout | 46.2m | The banner updates when the raid ends | The feed said "Raid over" while the banner still said RAID IN PROGRESS | cosmetic | 0487.png |

**Confusion log**
- 1.6m–4.4m — training sim — free nudge and wheel tags — the whole sim, never resolved
- 14.0m–16.2m — campaign map — which node to take, and the lock chain — about 2 minutes, resolved by clicking the CLEAR FIRST node
- 28.5m–29.9m — HQ crew tab — where to hire a rookie — never found; Jack In eventually worked with the lone Breaker
- 35.4m–36.4m — route map — only the Elite lit — forced into it
- 38.2m–40.2m — Elite fight turn 1 — Jolt NEED 1 — never understood; escalated, got no reply, died on turn 2
- 42.3m–46.1m — raid setup — how to station — never resolved
- 52.4m–52.9m — CREW tab — hire a rookie — no button visible

## 8. Summary (machine-read by tools/playtest/aggregate.py — keep the keys, one line each)

```
SUMMARY
handle: mothball
persona: PB-SOL-1
focus: raids
build: 52626bcd24d785a8dd7c75b213a52ea639892935
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 4
raids_survived: 1
playtime_min: 61
enjoyment: 3
rng_fairness: 4
netrun_length: too long
campaign_length: too long
text_clear: no
op_picks: none
weak_picks: Fine Tune, Jolt
bugs: 13
top_frustration: Free Nudge and targeting never explained, and raid stationing would not register, so permadeath and raids felt like an unreadable tax
top_change: Explain Free Nudge and card targeting in plain on-screen text and make stationing in raid setup work
```