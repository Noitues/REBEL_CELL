import importlib
for m in ('skimage', 'cv2', 'scipy', 'numpy', 'PIL'):
    try:
        mod = importlib.import_module(m)
        print(m, getattr(mod, '__version__', '?'))
    except Exception as e:
        print(m, 'missing', type(e).__name__)
