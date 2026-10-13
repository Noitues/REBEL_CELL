# Playtest feedback — saltlamp · PB-012 · build 19ad76a3a10c260a760667a0d6dde27156508740 · date not shown

> Written by a Claude playtester that played the game only through the screen, the mouse and
> the keyboard (docs/process/05_CLAUDE_PLAYTESTER.md). Every claim below comes from what was on
> screen; screenshot paths and actions.log times back the specific ones. "Not encountered"
> means exactly that.

## 1. General & session info

- **Playtester handle:** saltlamp
- **Persona / focus / quirks:** Casual evening player / Cards, Firmware and Daemons / Sticks with the same operative class (Breaker all campaign); never uses UNDO (broken once, in desperation, at 16.1m).
- **Platform & hardware:** PC, Windows 10 (the studio PC), 1280×720 window, mouse + keyboard.
  Audio off (the run is muted), drag-and-drop not available (cards played by click → target).
- **Build:** main @ 19ad76a3a10c260a760667a0d6dde27156508740
- **Total playtime:** 22 minutes (179 actions, 136 steps; quit via the pause menu mid-fight so the game saved)
- **Campaign setup:** corporation not shown in my notes (the HQ map showed Continuum Billing Farm as the site), ICE not shown, home server variant not shown, starting roster Breaker (Breaker 1, then Breaker 2), campaign code not shown
- **How far did you get?**
  - [ ] Stopped in the tutorial / before the first netrun (why)
  - [ ] Campaign **lost**
  - [ ] Campaign **won**
  - [x] Campaign **abandoned** / could not continue (why: out of time). INCOMPLETE. Breaker 2 was mid-fight on T1 versus a Collections Agent, turn 7, me 16/60, enemy 22/40.
  - Netruns: 2 started, 0 completed, 1 operative death (Server Rack, layer 4)
  - Highest Site tier reached: T1 · Exploits held: not encountered · Sites claimed at the end: not shown
  - Raids: not encountered
  - Final Heat: 11 · Home server integrity: not shown
- **Overall enjoyment (1–10):** 4 — I liked the moments when the wheel lined up, but a forced Rack at 11 HP felt unfair.

## 2. Core gameplay & deckbuilding

- **Wheel combat:**
  - It felt like skill in places. A Respin to land the 12 slice and Jolt to shift off the 6s worked. The aiming rules stayed a bit cryptic to me, and I mostly went by feel.
  - I did not notice SEND IT differing from the preview chips. The preview felt trustworthy.
  - UNDO: I only used it once, when I was desperate at 0 RAM, and I lost anyway. Otherwise not used.
- **Card balance & utility:**
  - Overpowered / automatic picks: Patch+ (taken twice) was a safe pick for the OVFL 12 slice because my damage comes from there. Respin felt like a lifesaver against the healer.
  - Useless / never worth picking: Brute Spin felt useless on a wheel with 6 slices, since it is a full lap. Inner-ring cards looked dead on my wheels. The -1 RAM chip was never explained to me.
- **Synergies & archetypes:** No build really came together. I took Jam, Reroll and Freeze, and none of them clicked into a plan. The deck felt like a small pile of wheel tweaks. The 12 slice was my one reliable source of damage.
- **Card text & clarity:** No. The card description text on the loot cards is tiny and thin. The terms Overflow, RAM, Free Nudge and the slot abbreviations (OVFL, SHIM, DFRG) are unexplained.

## 3. Roguelite loop & campaign progression

- **Pacing & length:** Netrun 1 was about 17 minutes including the tutorial fight. Netrun 2 was cut off by the time limit. Campaign length is not judged.
- **Netrun map & encounters:** Each layer offered only one node. I never got a shop, event or elite, so there was no real route choice. Layer 4 forced a Rack at 11/60 HP, and Grid View showed no alternative either.
- **City Grid & HQ:** Barely seen. I jacked in straight away at HQ with Heat 11 and Schematics 20.
- **Heat:** Heat went to 11 after the death. I could not tell how it would be managed.
- **Raids:** Not encountered.
- **RNG & fairness (1–5):** 4. I went in at 23/60 HP, won a healer fight at a cost of 34 HP, and then had no way to heal before the 112 HP Rack.
- **Permadeath & meta-progression:** The loss did not feel earned, because the route gave me no way out. I did restart with Breaker 2 straight away.

## 4. UI, controls & audio

- **Information in combat:** The preview chips and incoming damage were readable. The turn-by-turn RAM chip (-1) was a mystery. The Triage Unit's healing was clear once I looked.
- **Information outside combat:** The route map is dense and busy. Node types are tiny and hard to tell apart, and nothing says what to click. The dossier card's "AT LARGE" stamp covers the max HP. The purple "D 0" badge is unlabelled.
- **Controls:** Fine overall. The loot screen left me unsure whether picking a card confirms it or I still need Continue.
- **Visual feedback:** The victory screen has a LOOT sticker over the PROCEED label, and two DELETED stamps overlap. Hits were readable, but I did not find them impactful.

## 5. Focus questions (Cards, Firmware and Daemons)

1. **Card reward offers and picks:**
   - Fight 1: Nudge Driver / Jam / Leech Worm. I took Jam.
   - Fight 2: Sanitize / Reroll / Inner Drift. I took Reroll.
   - Fight 3: Inner Snap / Gear Shift / Freeze. I took Freeze.
   - Firmware offers: Patch+ vs Shunt (took Patch+) and Patch+ vs Bulkhead (took Patch+).
   - No card rewards were seen on Breaker 2's run before time ran out. No Daemons were offered to me. The Billing Daemon was only an enemy.
2. **Most changing pickup:** Respin (the 4 RAM wheel reroll) and Patch+. Respin got me the 12 slice that turned the Triage Unit fight, and Patch+ made that slice hit harder.
3. **Class strength:** I only played Breaker, so I cannot compare. It felt weak once I was low on HP and short of healing.

## 6. Open feedback

- **Favourite moment or build:** Respinning onto the 12 slice against the Triage Unit and watching the -12 chip finally beat its heal.
- **Biggest frustration / moment you wanted to quit:** At 11/60 HP the map offered only the Rack. I lost Breaker 1 there on turn 1.
- **One thing to change or add right now:** Give a heal or a safe alternative node before a Rack when HP is low. Also make the loot card text and node types bigger and clearer.

## 7. Bugs and confusion log

| # | Where | Steps (actions.log time) | Expected | Saw | Severity | Shot |
|---|---|---|---|---|---|---|
| 1 | Victory screen | after fight, 4.4m | A clear PROCEED/LOOT button | LOOT sticker covers PROCEED; DELETED stamps overlap | cosmetic | 0033.png |
| 2 | Dossier card on map | 6.1m, 12.6m | Max HP visible | AT LARGE stamp hides the max HP | cosmetic | 0083.png |
| 3 | Route map L4 | 12.6m–14.6m | A choice of nodes | Only the Rack offered at 11/60 HP, also in Grid View | wrong | 0089.png |
| 4 | Loot screen | 4.5m | Clear confirm flow | Unclear whether picking confirms; tiny card text | cosmetic | 0034.png |

**Confusion log:**
- 8.3m — Triage Unit fight — the -1 RAM chip — stayed unexplained for the rest of the fight.
- 14.1m — route map — looking for another node — not resolved; Rack forced.
- 4.5m — loot sheet — whether picking auto-confirms — I clicked and it worked out.

## 8. Summary

```
SUMMARY
handle: saltlamp
persona: PB-012
focus: cards-firmware-daemons
build: 19ad76a3a10c260a760667a0d6dde27156508740
outcome: INCOMPLETE
netruns_completed: 0
operative_deaths: 1
raids_survived: 0
playtime_min: 22
enjoyment: 4
rng_fairness: 4
netrun_length: too long
campaign_length: just right
text_clear: no
op_picks: Patch+, Respin
weak_picks: Brute Spin, Freeze
bugs: 4
top_frustration: Forced Rack at 11/60 HP with no alternative route or heal killed Breaker 1.
top_change: Offer a heal or a safe node before a Rack when HP is low, and enlarge loot card text and map node icons.
```