# NA-21 parity inventory (GDScript twins of the netrun-art Python oracle)

Python is the oracle (`tools/netrun_art/`). Twins live in `scripts/netrun_art/`, tuning numbers in `content/config/netrun_art.tres`
(`NetrunArtConfigData`, generated from the Python constants by `python -m netrun_art.gen_twin_config`, run from `tools/`).
Fixtures: `tools/netrun_art/tests/fixtures/` — `inputs/<seed>.json` (exact doubles as `"~hex"` strings), `expected/<seed>_{street,hq}_{derive,poses}.json`,
`expected/<seed>_street_dress.json`, `hashes.json`. Seeds 101-112, street and HQ. Regenerate with `python -m netrun_art.tests.gen_fixtures` then
`python -m netrun_art.tests.gen_inputs` (HQ entrances use the art-pass LANDMARK_ENTRIES, provisional except Meridian).
Parity tests: `tests/netrun_art/test_na21_parity.gd` (derive, poses, occlusion, dress reader, reader negatives),
`tests/netrun_art/test_na21_camera_pixels.gd` (Godot `frustum_offset` vs `shift_x/shift_y`).

| Twin (GDScript) | Python source | Public functions | Constants / config | Fixture file |
|---|---|---|---|---|
| `NetrunArtUnits` | `units.py` | kit, r4, smoothstep01, vector helpers | `units` (floor_bu, kit_storey, k_fit) | (used by all) |
| `NetrunPose` | `rig.py` `Pose` | make, dir, loc, proj, to_json, from_json, mix | `rig` (sensor_mm, ref_w, ref_h) | `*_poses.json` pose blocks |
| `NetrunCameraRig` | `rig.py` | frame_points, bbox_px, street_overview, street_decision, street_hover, hq_page_camera, hq_page_pose, dive_pose, dive_distance, ease fns | `rig` (t_step 0.9, t_zoom 1.0, ...), `look_bias_sign` +1, `dive`, `hq_page` | `*_street_poses.json` (overview, decision, fixtures, dive) |
| `NetrunHqOrbit` | `hq/orbit.py` | hq_decision, hq_hover, hq_overview, overview_yaw, face_index, visible_room | `hq_rig` | `*_hq_poses.json` |
| `OcclusionHelper` | `occlusion.py` | occlusion_params, occlusion_state, building_boxes, occlusion_block, rail_* | `occlusion` | `occlusion` blocks in both poses files |
| `RevealTiers` | `lod.py` + spec 5.2b | band, weights, zoom_dive, zoom_detail, lod_block, tier_weight, visible_tier | `lod`, `reveal` | `lod`, `lod_weights` in poses |
| `NetrunSection` | `section.py` | zcut, look_w, section_params, section_block | `section` | `section` blocks (HQ poses) |
| `NetrunArtLayout` | `layout.py` (not `apply_layout_rules`) | merged_buildings, border_links, link_legs, route_on_streets, leg_axis | `layout` | via `*_street_derive.json` |
| `NetrunStreetDeriver` | `derive/street.py` | derive_street, frontage, assign, room_boxes, link_paths | `street_rules` | `*_street_derive.json` |
| `NetrunHqSlots` | `hq/slots.py` | derive_hq, plan_compound, place_slots, set_entrance, link_paths | `slot_params`, `landmark_entries` | `*_hq_derive.json` |
| `NetrunArtDeriver` | `derive/__init__.py` | game_partial, derive_street, derive_hq, poses, derive_text | VERSION 2 | both derive files |
| `NetrunPoseBuilder` | `poses.py` | build_poses, successors, fixture_walks | VERSION 1 | `*_poses.json` |
| `NetrunFrustum` | (new) AD 5 | frustum_size, frustum_offset, camera_transform, apply | `frustum_tolerance` | pixel parity test |
| `DressReader` | `dress.py` (reader only) | read_text, read_file, check_derive, is_room_kind | palette ids, room kinds (AD 19) | `*_street_dress.json` |

Not ported (input arrives already laid out and zoned; NA-11 / NA-12 own them): `layout.apply_layout_rules`, `zoning.py`, `dress.dress_street` (the writer).
Serializer: one hand-written canonical writer, `NetrunArtExport.canonical` (its `float_str` now rounds half up first, spec 12.8 rule 1).
