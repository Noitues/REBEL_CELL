# Card illustration briefs (W4)

ART_BIBLE 7.3 and designer ruling Q1: about 30 **base illustrations**, one per effect
family, shared by the family's cards and tinted per card type; **unique art** for every
rare and class card. Every final is a two-colour risograph print (INK + CELL_PINK) at
768 x 512 (3:2). Until the finals land, `scripts/ui/kit/card_art.gd` (`CardArt`) draws a
procedural stand-in in the same style; a final drops in by setting the card's `art`
texture (`CardData.art`) with no code change.

- 35 family briefs (34 used by content, plus the `chip` fallback for Firmware and Daemon stickers).
- 12 unique-art briefs (rares and class cards), listed below by id.
- Pixel-art concepts, one per family: [`docs/art_review/W4/concepts/`](../../art_review/W4/concepts/contact_sheet.png)
  (script-drawn, Q6; never shipped).

Regenerate: `godot --headless --path . -s tools/art_concepts/dump_cards.gd`, then
`python tools/art_concepts/card_briefs.py` and `python tools/art_concepts/card_concepts.py`.

## Inks by card type
| Card type | Stock (window) | Key ink | Spot ink |
|---|---|---|---|
| WHEEL (paper) | `PAPER_ALT` #E9E4D6 | `INK` | `CELL_PINK` |
| SYSTEM (black) | `INK` #111111 | `PAPER` (light ink) | `CELL_PINK` |
| HACK (pink) | `STICKER_PINK` #F5AFCB | `INK` | `CELL_PINK` |

## Families
| Brief | Family | Base cards | Unique variations | Concept |
|---|---|---|---|---|
| [Spin](spin.md) | `spin` | 5 | – | [concept](../../art_review/W4/concepts/spin.png) |
| [Heavy spin](spin_heavy.md) | `spin_heavy` | 4 | – | [concept](../../art_review/W4/concepts/spin_heavy.png) |
| [Backspin](backspin.md) | `backspin` | 2 | – | [concept](../../art_review/W4/concepts/backspin.png) |
| [Gear mesh](gear.md) | `gear` | 1 | `torque_wrench` | [concept](../../art_review/W4/concepts/gear.png) |
| [Nudge](nudge.md) | `nudge` | 4 | – | [concept](../../art_review/W4/concepts/nudge.png) |
| [Jam](jam.md) | `jam` | 2 | `ghost_step` | [concept](../../art_review/W4/concepts/jam.png) |
| [Inner ring](inner_ring.md) | `inner_ring` | 4 | – | [concept](../../art_review/W4/concepts/inner_ring.png) |
| [Snap](snap.md) | `snap` | 3 | `hot_swap` | [concept](../../art_review/W4/concepts/snap.png) |
| [Flip](flip.md) | `flip` | 2 | – | [concept](../../art_review/W4/concepts/flip.png) |
| [Respin](respin.md) | `respin` | 1 | – | [concept](../../art_review/W4/concepts/respin.png) |
| [Freeze](freeze.md) | `freeze` | 2 | `blind_spot` | [concept](../../art_review/W4/concepts/freeze.png) |
| [Strip](strip.md) | `strip` | 2 | – | [concept](../../art_review/W4/concepts/strip.png) |
| [Breach](breach.md) | `breach` | 1 | `shatter`, `short_circuit` | [concept](../../art_review/W4/concepts/breach.png) |
| [Damage](damage.md) | `damage` | 1 | – | [concept](../../art_review/W4/concepts/damage.png) |
| [Arc](arc.md) | `arc` | 1 | – | [concept](../../art_review/W4/concepts/arc.png) |
| [Overload](overload.md) | `overload` | 1 | – | [concept](../../art_review/W4/concepts/overload.png) |
| [Block](block.md) | `block` | 2 | – | [concept](../../art_review/W4/concepts/block.png) |
| [Shield](shield.md) | `shield` | 1 | – | [concept](../../art_review/W4/concepts/shield.png) |
| [Evade](evade.md) | `evade` | 1 | – | [concept](../../art_review/W4/concepts/evade.png) |
| [Heal](heal.md) | `heal` | 1 | `stim_patch` | [concept](../../art_review/W4/concepts/heal.png) |
| [Cleanse](cleanse.md) | `cleanse` | 2 | – | [concept](../../art_review/W4/concepts/cleanse.png) |
| [Corrupt](corrupt.md) | `corrupt` | 2 | – | [concept](../../art_review/W4/concepts/corrupt.png) |
| [Overclock](overclock.md) | `overclock` | 1 | `overdrive` | [concept](../../art_review/W4/concepts/overclock.png) |
| [Encrypt](encrypt.md) | `encrypt` | 2 | – | [concept](../../art_review/W4/concepts/encrypt.png) |
| [Parasite](parasite.md) | `parasite` | 0 | `leech_worm`, `parasite_pulse` | [concept](../../art_review/W4/concepts/parasite.png) |
| [RAM](ram.md) | `ram` | 3 | – | [concept](../../art_review/W4/concepts/ram.png) |
| [Drain](drain.md) | `drain` | 1 | – | [concept](../../art_review/W4/concepts/drain.png) |
| [Draw](draw.md) | `draw` | 2 | – | [concept](../../art_review/W4/concepts/draw.png) |
| [Drone](drone.md) | `drone` | 0 | `spawn_drone` | [concept](../../art_review/W4/concepts/drone.png) |
| [Calibrate](calibrate.md) | `calibrate` | 2 | – | [concept](../../art_review/W4/concepts/calibrate.png) |
| [Ring lock](ring_lock.md) | `ring_lock` | 1 | – | [concept](../../art_review/W4/concepts/ring_lock.png) |
| [Steady hand](steady.md) | `steady` | 1 | – | [concept](../../art_review/W4/concepts/steady.png) |
| [Undock](undock.md) | `undock` | 1 | – | [concept](../../art_review/W4/concepts/undock.png) |
| [Amplify](amplify.md) | `amplify` | 0 | `overclock_nudges` | [concept](../../art_review/W4/concepts/amplify.png) |
| [Chip (fallback)](chip.md) | `chip` | 0 | – | [concept](../../art_review/W4/concepts/chip.png) |

## Unique art (rares and class cards)
| Brief | Name | Rarity | Class | Family |
|---|---|---|---|---|
| [`blind_spot`](unique/blind_spot.md) | Blind Spot | UNCOMMON | ghost | freeze |
| [`ghost_step`](unique/ghost_step.md) | Ghost Step | UNCOMMON | ghost | jam |
| [`hot_swap`](unique/hot_swap.md) | Hot Swap | UNCOMMON | rigger | snap |
| [`leech_worm`](unique/leech_worm.md) | Leech Worm | RARE | – | parasite |
| [`overclock_nudges`](unique/overclock_nudges.md) | Nudge Driver | RARE | – | amplify |
| [`overdrive`](unique/overdrive.md) | Overdrive | COMMON | breaker | overclock |
| [`parasite_pulse`](unique/parasite_pulse.md) | Parasite Pulse | UNCOMMON | botnet | parasite |
| [`shatter`](unique/shatter.md) | Shatter | UNCOMMON | breaker | breach |
| [`short_circuit`](unique/short_circuit.md) | Short Circuit | RARE | – | breach |
| [`spawn_drone`](unique/spawn_drone.md) | Spawn Drone | UNCOMMON | botnet | drone |
| [`stim_patch`](unique/stim_patch.md) | Stim Patch | RARE | – | heal |
| [`torque_wrench`](unique/torque_wrench.md) | Torque Wrench | UNCOMMON | rigger | gear |

## Delivery
- 768 x 512 PNG, sRGB, named `<family>_<type>.png` for bases (`spin_paper.png`) and
  `<card_id>.png` for unique art, into `assets/art/cards/`; the importer sets each card's
  `art`. The window crops the centre about 1.17:1 on hand cards and shows the whole 3:2
  in the card detail.
