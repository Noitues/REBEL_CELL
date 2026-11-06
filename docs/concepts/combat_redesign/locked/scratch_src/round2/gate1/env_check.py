"""gate1: which optional libs exist."""
for m in ('skimage', 'scipy', 'numpy', 'PIL', 'cv2'):
    try:
        mod = __import__(m)
        print(m, getattr(mod, '__version__', '?'))
    except Exception as e:
        print(m, 'MISSING', e)
