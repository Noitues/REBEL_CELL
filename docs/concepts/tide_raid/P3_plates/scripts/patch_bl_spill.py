s = open('p1_bl.py').read()
s = s.replace("        cy.samples = SPEC.get('spill_samples', 128)\n    dump(p)", "        cy.samples = min(SPEC.get('spill_samples', 128), 48)\n        scene.render.resolution_percentage = 50     # P2: the spill is low-frequency light; half-res + 48 spp, upscaled on load\n    dump(p)\n    scene.render.resolution_percentage = 100")
s = s.replace("    buf = np.empty(RES[0] * RES[1] * 4, np.float32)\n    img.pixels.foreach_get(buf)\n    arr = buf.reshape(RES[1], RES[0], 4)[::-1].astype(np.float16)",
              "    iw, ih = img.size\n    buf = np.empty(iw * ih * 4, np.float32)\n    img.pixels.foreach_get(buf)\n    arr = buf.reshape(ih, iw, 4)[::-1]\n    if (iw, ih) != (RES[0], RES[1]):\n        from scipy import ndimage as ndi\n        arr = np.stack([ndi.zoom(arr[..., c], (RES[1] / ih, RES[0] / iw), order=1) for c in range(4)], -1)\n    arr = arr.astype(np.float16)")
open('p1_bl.py', 'w').write(s)
print('ok')
