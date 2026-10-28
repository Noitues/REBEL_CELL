s = open('p2_post.py').read()
s = s.replace("        im.crop(bx).resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 50, 2)).save(OUT + 'crops2x/%s_hot2x.png' % key)",
"""        f4 = OUT + 'plates4k/%s.png' % key
        if os.path.exists(f4):
            Image.open(f4).convert('RGB').crop(tuple(v * 2 for v in bx)).save(OUT + 'crops2x/%s_hot2x.png' % key)     # TRUE 2x: rendered at 3840x2160, not upscaled
        else:
            im.crop(bx).resize((1920, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.2, 50, 2)).save(OUT + 'crops2x/%s_hot2x.png' % key)""")
open('p2_post.py', 'w').write(s)
