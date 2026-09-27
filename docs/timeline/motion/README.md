# Motion frame strips

Frame strips for owner review (ANIMATION_HANDOFF 5-6): Movie Maker frames at 30 fps, each
labelled with its ms from the start of the motion; variants stacked top to bottom, their
values in each strip's title. The picked values are in `content/config/ui_motion.tres`
and logged in `docs/DECISIONS.md` ("Motion pass").

| Strip | Slice | Motion | Variants (top to bottom) | Picked | Captured with |
|---|---|---|---|---|---|
| `influence_spread.png` | ANIM-5 | Territory tint spreads from a newly claimed Site (HQ backdrop) | `influence_spread` 0.7 / 1.0 / 1.4 s | 1.0 s (the front reads, done inside a second) | hq `--demo-hq --demo-anim=influence_spread` |
| `raid_playout.png` | ANIM-5 | Threat travels the street route, turret trace, hit, damage number, HOLDS stamp | `raid_move` 0.35 / 0.5 / 0.7 s | 0.5 s | hq `--demo-raid --demo-anim=raid_playout` |
| `heat_pulse.png` | ANIM-5 | Heat crosses 25: distortion pulse, corporate wireframe creeps in from the edges, letters shake, band stamps | `heat_pulse` peak 0.85 / 0.5 / 0.3 | 0.5 (the UI keeps its shapes) | hq `--demo-hq --demo-anim=heat_pulse` |
| `jack_in.png` | ANIM-5 | Push into the JACK IN / deck CRT, dissolve to the wireframe city, scanlines roll, the net arrives | `jack_in` 0.6 / 0.8 / 0.9 s | 0.8 s (heavy, mid-range) | hq `--demo-grid --demo-anim=jack_in` |
| `route_pulse.png` | ANIM-5 | Netrun move: light pulse carries the marker along the link, new node pops, old one dims | `route_pulse` 0.3 / 0.4 / 0.6 s | 0.4 s | netrun `--demo-run --demo-anim=route_pulse` |
| `site_select.png` | ANIM-5 | Grid Site selected: roof outline draws on, ring eases in, camera leans and eases | `site_outline_draw` 0.25 / 0.4 / 0.6 s | 0.4 s | hq `--demo-grid --demo-anim=site_select` |
| `asset_drop.png` | ANIM-5 | Raid asset deployed: drops onto its node with a stamp ring (the map holds still) | one (`asset_drop` 0.25 s BOUNCE 24 px) | as is | hq `--demo-raid --demo-anim=asset_drop` |

Variants: add `--demo-tune=<id>:<duration>[:<amplitude>]` (a duplicate of the table; the
file never changes). Command: `godot --path . --resolution 1280x720 --write-movie
<dir>/f.png --fixed-fps 30 --quit-after N <scene> -- <flags>`; the log prints "anim5: <id>
starts on frame N" for `tools/design_lab/frame_strip.py --start`.
