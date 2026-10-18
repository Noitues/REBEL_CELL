# netrun_art test fixtures

Regenerate with `python -m netrun_art.tests.gen_fixtures` (from `tools/`), then run pytest.

- Placeholder entrance: regen when the landmark entries land. The HQ parity fixtures (`*_hq_poses.json`, `derive_hq`,
  `poses_hq` hashes) frame the first DECISION with `slots.set_entrance`, the ground centre of the base-tier face closest
  to the overview camera. Real anchors come from art-pass's `<corp>_landmark.py` through `slots.LANDMARK_ENTRIES`.
