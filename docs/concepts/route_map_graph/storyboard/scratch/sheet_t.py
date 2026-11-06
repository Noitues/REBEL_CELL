import sys
from PIL import Image
S = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass\docs\concepts\route_map_graph\storyboard\scratch\\"
ims = [Image.open(S + n).convert("RGB").resize((960, 540)) for n in sys.argv[1:]]
out = Image.new("RGB", (1920, 540 * ((len(ims) + 1) // 2)))
for k, im in enumerate(ims):
    out.paste(im, ((k % 2) * 960, (k // 2) * 540))
out.save(S + "sheet.jpg", quality=88)
