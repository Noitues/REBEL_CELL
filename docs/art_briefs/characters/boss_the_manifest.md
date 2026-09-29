# The Manifest (Priority Routing) — boss hologram brief

**Family:** boss of Meridian Freight Systems (ART_BIBLE §7.2, §6.1). **Content id:** `the_manifest`.
**Deliverable:** a large hologram, 1:1, **1024 px master** (it shows at about 40% of the screen height, ~288 px at 720p, ~432 px at 1080p), plus a 768 px bust crop for the enemy portrait slot. Stand-in: `Hologram` (Mode.BOSS) / `PortraitArt` Kind.BOSS.
**Concept:** `docs/art_review/W5/concepts/boss_the_manifest.png`; review: `docs/art_review/W5/bosses.png`, `boss_hologram.png`, `boss_intro_strip.png`.

## Staging
- It stands **behind** the boss wheel (120% size, W3), dimmed (`Hologram.BOSS_DIM` 0.5) so the wheel, its slice values and the HP arc stay readable. W3 places it; it never covers slice values.
- Figure: head and shoulders rising above the wheel, a crown of antenna spikes, a halo ring filled with the corp pattern (**shipping-container stripes at 45°**), the corp hue **#FF8C1A** (`Palette.CORP_MERIDIAN`).
- One landmark motif per boss (container crane) worked into the crown or the chest so the five bosses read apart in greyscale.

## Hologram treatment (the view adds these; paint the clean figure)
- Translucent body, bright edges, scanlines drifting one pitch per 4 s (T0, `hologram_idle`), a projector cone and base disc.
- W6's `crt_overlay` (roll band, static scanlines). Under reduce effects everything is static.

## Intro sting (W3's name slam + this hologram)
- `Hologram.play_intro()`: the figure projects up from its base with a bright scan edge (T4, `hologram_intro`, 1.4 s). Under reduce effects it is a 0.4 s cross-fade (`hologram_intro_fade`).
- Paint an alpha-clean figure so the reveal can wipe it bottom to top.

## Do / don't
- Do keep the eyes the brightest point (they are the "look at you" beat of the intro).
- Don't paint a background: the net arena shows through.
- Don't use a full-screen flash; the reveal is the moment.
