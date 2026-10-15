"""Encode a PNG sequence to H.264 mp4 with Blender's built-in FFmpeg (VSE, CPU only, no GPU lock needed).

blender -b --factory-startup -P encode_mp4.py -- <frames_dir> <out.mp4> <n_frames> [fps]
Frames are f_0000.png .. f_<n-1>.png.
"""
import os
import sys

import bpy

argv = sys.argv[sys.argv.index("--") + 1:]
src, out, n = argv[0], argv[1], int(argv[2])
fps = int(argv[3]) if len(argv) > 3 else 24

sc = bpy.context.scene
sc.render.fps = fps
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = 100
sc.frame_start, sc.frame_end = 1, n
if not sc.sequence_editor:
    sc.sequence_editor_create()
ed = sc.sequence_editor
coll = ed.strips if hasattr(ed, "strips") else ed.sequences
first = os.path.join(src, "f_0000.png")
strip = coll.new_image("seq", first, 1, 1)
for f in range(1, n):
    strip.elements.append("f_%04d.png" % f)
strip.frame_final_duration = n
ims = sc.render.image_settings
try:
    ims.media_type = "VIDEO"
except Exception:
    pass
ims.file_format = "FFMPEG"
ff = sc.render.ffmpeg
ff.format = "MPEG4"
ff.codec = "H264"
try:
    ff.constant_rate_factor = "HIGH"
except Exception:
    pass
ff.ffmpeg_preset = "GOOD"
sc.render.filepath = out
sc.render.use_sequencer = True
bpy.ops.render.render(animation=True)
print("ENCODED", out)
