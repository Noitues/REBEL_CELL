# netrun_art test fixtures

Regenerate with `python -m netrun_art.tests.gen_fixtures` (from `tools/`), then run pytest.

- Entrances: the HQ parity fixtures (`*_hq_poses.json`, `derive_hq`, `poses_hq` hashes) frame the first DECISION with
  `slots.set_entrance`. `slots.LANDMARK_ENTRIES` now holds all 7 corps, Aurelian included (art-pass 6d214ce9, plates
  63be54f6); a corp without an entry falls back to the ground centre of the base-tier face closest to the overview camera.
- Occlusion (2026-10-18): DECISION records (`decision`, `fixtures[].decision`) aim the occlusion cone at every route room in
  frame (`occlusion.rooms_in_frame`, twin of art-pass `occ_check.in_frame_rooms`), not only the current room and options.
  Regenerated with this change: all 24 `expected/<seed>_{street,hq}_poses.json` (seeds 101-112) and `hashes.json`.
