# Zoom rules round 7 (O-16 highlight tone-down, motion pass: sign flicker)
Godot `D:/rc_art/godot_look_tide`, branch `art/netrun-zoom`, base 22979681. Autonomous overnight run; choices logged below. Numbers in `CityConfig` `zr_hl_*`, `zr_flick_*`.

## 1. City-view highlight (`highlight_before_after_crop.png`, `highlight_before.png`, `highlight_after.png`)
Choice: ground fill ONLY on the road cells of the segment (street lots), depth tested (new shader `city_zoom_hl_fill.gdshader`, own mesh) so buildings in front hide it; fill 0.35 -> 0.14 (`zr_hl_fill`, `zr_hl_fill_roads`); cyan outline and end squares unchanged (no depth test); light column thinner and brighter (`zr_hl_beam_px` 2.5 px half-width, `zr_hl_beam_k` 1.5). Captured with nr_zoom `--hl` (before: HEAD code, after: this). The pink pane is gone; the segment reads as a cyan frame with faint pink on the road lots. The column is faint at this scale; raise `zr_hl_beam_k` if wanted.

## 2. Sign flicker
- Pure maths `CityZoomFlicker.gain(sign id, letter, t, params)` (integer hash, no RNG stream), mirrored in `shaders/lib/zr_flicker.gdshaderinc`. A seeded share of signs (street 0.3, city 0.2) can flicker; per sign per slot at most ONE event: a dip (p 0.3, to 55 % light, 0.14 s street / 0.4 s city, to 70 %) or, rarely (p 0.1, street only), one letter drops to 15 % for 0.11 s. Slot 1.0 s street, 2.5 s city (min 0.5 s enforced) -> at most 2 dip starts in any second (test: under 3), never a strobe; the dips are smooth sin^2.
- Which signs: street = neon-frame fascia signs and tier signs (blade, panel, roof) of neon buildings, frame and letters (letters tagged per letter); city = wall screens, blade signs, roof logos, roof screens in `city_neon.gdshader` (sign id packed in UV2.y: unflagged quads keep UV2.y exactly).
- Off: `zr_flick_on` false; reduce motion when `zr_flick_reduce_off` (default true); reduce effects; frozen capture (`--freeze`). Then `fl_on` = 0 and the factor is exactly 1.0.
- Clock: `CityView3D.flicker_clock()` (node `CityZoomFlicker`), frame clock, `set_time(t)` for captures. nr_zoom: `--gif=N,fps,t0` (frames gif_NNN.png), `--flick-only` (with `--freeze`: only the flicker moves; used to prove effect), `--hl` as before.
- GIFs (640 px, 48 frames, 12 fps = 4 s, live scene, t 0-4 s): `street_band_flicker_4s_12fps.gif`, `city_band_flicker_4s_12fps.gif`. Honest note: at the street frame only about one neon sign (the right vertical blade) dips in these 4 s (2 events), the city band shows many small dips; the other motion in the GIFs is the existing rain / beams / window twinkle. The flicker-only frame diffs (`logs/flicker_only_*_framediff.txt`, frozen scene) show the dips alone.

## Checks (`logs/`)
- Street band frozen (`--freeze --layers=1 --stages=5`, no `--hl`) vs round 6 code: **0 differing pixels** (`street_frozen_vs_round6.txt`).
- City band zoom rules on vs off, frozen: **0** (`city_band_on_vs_off.txt`); rules-off frame after vs before code: **0** (`city_base_after_vs_before.txt`). (The round-6 baseline "layers" frame was overwritten by my highlight baseline, so the on-vs-off check is on the new code plus the base-vs-base check.)
- Tests (targeted only, no full suite): round-6 set (zoom layers/r2/rules/stage, neon kit, shaders, city3d model, city motion) + new `test_city_zoom_flicker.gd` (determinism, steady majority, flash-rate cap, city slower, dead letter, off switches, quad packing) + 1 highlight test: **145 tests, 0 failing, 8 pending** (`targeted_tests.log`).

## Gaps / slips
- Flicker maths in GDScript and GLSL are separate implementations (same integer ops); parity is not unit-tested, only seen in the captures.
- Flash-rate cap is per sign; many signs dipping at once are not rate-limited as a group (dips are shallow, 30-45 %).
- Slip: ran `python -` (heredoc) once by mistake; stopped it by task id, it did nothing. Tool `godot --headless --import` run once to register the new class.
- Perf not re-measured.
