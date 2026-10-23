# Raid target frames: concept art for the sweep raid (brief)

## Goal
Three bold concept frames that set the visual target (V) and the suspense moments (S) for the sweep raid, before
anything is built in Godot. The designer judged an earlier art pass underwhelming: lead with bold, finished-looking
art, not tweaks of the placeholder lab.

## The raid, in one paragraph
- The player's hacker cell is a 4×3 network: 6 asset nodes, each with a value, plus the HOME server with 3
  integrity. A corporation sweeps it with beams; Heat sets how many.
- Beam 1 is known. Beam 2 is sealed: one of 3 candidate lines, each marked by a shape (triangle, square, circle) and
  revealed only at launch.
- A hunter beam then turns down the column of the first node touched.
- The player's levers:
  - ghost: hide a node;
  - decoy: a node the beam stops on;
  - go dark: hide a node for its income;
  - after the reveal, a spoof: SKIP (beam 2 skips one node) or JAM (the hunter doesn't run).
- A hit asset goes DOWN (wrench); a second hit TAKES it. HOME at 0 loses the whole campaign.
- Read the lab captures for the content: `D:/rc_tmp/raid_design_lab/lab_l5/shots/` (planned leg 0) and `shots_jam/`.

## The three frames (1920×1080 each)
1. **PLAN.** The network before launch: assets with value, HOME, the known beam, the three sealed candidates as
   shaped ghost lines, levers placed (one ghost, one decoy, one dark node), and the Heat meter at the 50 notch.
2. **REVEAL.** The unseal moment: two candidates collapse and the real line ignites. The spoof window is open: SKIP
   and JAM shown as the player's two options, with a countdown or press cue.
3. **IMPACT.** The sweep landing: the hunter turning down a column, an asset going DOWN, HOME taking a hit, with the
   outcome stamp arriving.

## Look
- **Sources:** `docs/STYLE_GUIDE.md` §1 (Three Worlds: the raid lives in the netrun / cyberspace world), §2 (color
  tokens) and §5.3 (raid motion).
- **Colors:** threats are cobalt `#3D6BFF`; the player's cell and HOME are warm. Every frame must read in
  grayscale at thumbnail size.
- **Shared design:** the three frames share one camera and one board, so they read as a sequence.
- **Pipeline:** follow the existing Blender pipeline (`tools/art_pipeline/city/concept_r40/unified40.py` and
  `tools/art_gen/portraits/render_busts.py`), and use Blender headless:
  `"C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b -P <script> -- <args>`.
  - Use 2D compositing over the render (Python + Pillow) for UI glyphs and text.
  - Text is minimal and US English.
- **Benchmark:** the frames should hold their own next to Into the Breach, Invisible, Inc. and FTL screenshots
  (shipped-game visuals scored about 7–8 by the critic).

## Deliverables
- **Scripts:** `tools/raid_concepts/target/` (Blender scene script plus composite script). Re-runnable, seeded, and
  with no absolute paths except the Blender exe and D:/rc_tmp.
- **Renders:** under `D:/rc_tmp/raid_design_lab/target/`.
- **Committed frames:** `docs/design/raid_concepts/raid_target/` holds the three final PNGs, each ≤ 2 MB (JPEG-quality
  PNG or downscale if needed), plus a `README.md` that says what each frame shows and lists the palette.
- **Self-check:** before handing back, build a side-by-side sheet: each frame next to its lab capture.
