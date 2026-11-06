"""Render the 6 motion tests (normal + reduce-motion): python render.py <name|all> [normal|reduce] [--jobs N] [--frames-only]
Outputs tests/<name>_<variant>.mp4 (1280x720, 30 fps), .gif (640 px, 30 fps), tests/<name>_<variant>_sheet.png and tests/metrics_<name>.json.
Frames are cached in D:/rc_scratch/tide_concepts/p2m_work/frames (delete a frame file to re-render it)."""
import sys, os, time, json, subprocess
sys.dont_write_bytecode = True
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P2_motion/'
TD = OUT + 'tests/'
FR = 'D:/rc_scratch/tide_concepts/p2m_work/frames/'
FFMPEG = 'D:/rc_scratch/tide_concepts/venv_vid/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
XFADE = 9
NOLOOP = {'jack'}
os.makedirs(TD, exist_ok=True)
os.makedirs(FR, exist_ok=True)


def fpath(name, variant, f):
    return FR + '%s_%s_%03d.png' % (name, variant, f)


def work(args):
    name, variant, f = args
    p = fpath(name, variant, f)
    if os.path.exists(p):
        return f
    import scenes2 as S2
    fn, n = S2.TESTS[name]
    a = fn(f, reduce=(variant == 'reduce'), mode='test')
    Image.fromarray(a).save(p + '.tmp.png')
    os.replace(p + '.tmp.png', p)
    return f


def load_frames(name, variant, n):
    return [np.asarray(Image.open(fpath(name, variant, f)).convert('RGB')) for f in range(n)]


def write_video(frames, mp4):
    cmd = [FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1280x720', '-r', '30', '-i', '-',
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', '-movflags', '+faststart', mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()


def write_gif(mp4, gif):
    cmd = [FFMPEG, '-y', '-loglevel', 'error', '-i', mp4, '-vf',
           'fps=30,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle',
           '-loop', '0', gif]
    subprocess.run(cmd, check=True)


def metrics(frames):
    small = [f[::2, ::2] for f in frames]
    lum = [float((f.astype(np.float32) * np.array([.2126, .7152, .0722], np.float32)).sum(-1).mean()) / 255 for f in small]
    d = np.abs(np.diff(lum))
    big = []
    for a, b in zip(small[:-1], small[1:]):
        big.append(float((np.abs(a.astype(np.int16) - b.astype(np.int16)).max(-1) > 64).mean()))
    sh = []
    for a, b in zip(small[:-1], small[1:]):
        la = a[::2, ::2].astype(np.float32).mean(-1)
        lb = b[::2, ::2].astype(np.float32).mean(-1)
        best = (1e18, 0, 0)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                e_ = float(np.abs(np.roll(la, (dy, dx), (0, 1))[8:-8, 8:-8] - lb[8:-8, 8:-8]).mean())
                if e_ < best[0]:
                    best = (e_, dy, dx)
        sh.append(max(abs(best[1]), abs(best[2])) * 4)
    # general-flash proxy: frames whose mean luminance jumps by more than 10 % of full scale, and the max in any 1 s window
    jumps = [i for i, v in enumerate(d) if v > .10]
    per_s = 0
    for i in range(len(d)):
        per_s = max(per_s, sum(1 for j in jumps if i <= j < i + 30))
    return dict(frames=len(frames), seconds=round(len(frames) / 30.0, 2), max_dlum=round(float(d.max()), 4), mean_dlum=round(float(d.mean()), 4),
                max_big_frac=round(max(big), 4), frames_big_gt1pct=int(sum(1 for b in big if b > .01)), max_shift_px=int(max(sh)),
                lum_jumps_gt10pct=len(jumps), max_lum_jumps_per_s=per_s)


def sheet(frames, path, k=12):
    n = len(frames)
    idx = [int(i * (n - 1) / (k - 1)) for i in range(k)]
    tw, th = 427, 240
    im = Image.new('RGB', (tw * 6, th * 2), (8, 6, 20))
    d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18) if os.path.exists('C:/Windows/Fonts/consola.ttf') else ImageFont.load_default()
    for i, j in enumerate(idx):
        t = Image.fromarray(frames[j]).resize((tw, th), Image.LANCZOS)
        im.paste(t, ((i % 6) * tw, (i // 6) * th))
        d.text(((i % 6) * tw + 8, (i // 6) * th + 6), 'f%03d' % j, font=fnt, fill=(255, 238, 58))
    im.save(path)


def finish(name, variant, n, loop):
    fr = load_frames(name, variant, n)
    m = metrics(fr)
    arr = [f.astype(np.float32) for f in fr]
    if loop:
        first = arr[0]
        for k in range(XFADE):
            j = n - XFADE + k
            tt = (k + 1) / float(XFADE)
            arr[j] = arr[j] * (1 - tt) + first * tt
    u8 = [np.clip(a + .5, 0, 255).astype(np.uint8) for a in arr]
    mp4 = TD + '%s_%s.mp4' % (name, variant)
    write_video(u8, mp4)
    write_gif(mp4, TD + '%s_%s.gif' % (name, variant))
    sheet(fr, TD + '%s_%s_sheet.png' % (name, variant))
    p = TD + 'metrics_%s.json' % name
    old = json.load(open(p)) if os.path.exists(p) else {}
    old[variant] = m
    json.dump(old, open(p, 'w'), indent=1)
    print(name, variant, m, flush=True)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    jobs = 5
    if '--jobs' in sys.argv:
        jobs = int(sys.argv[sys.argv.index('--jobs') + 1])
        args = [a for a in args if a != str(jobs)]
    import scenes2 as S2
    names = list(S2.TESTS) if args[0] == 'all' else [args[0]]
    variants = args[1:] or ['normal', 'reduce']
    tasks = []
    for nm in names:
        n = S2.TESTS[nm][1]
        for v in variants:
            tasks += [(nm, v, f) for f in range(n)]
    t0 = time.time()
    with Pool(jobs) as pool:
        for i, _ in enumerate(pool.imap_unordered(work, tasks, chunksize=2)):
            if i % 25 == 0:
                print('frames', i, '/', len(tasks), round(time.time() - t0), 's', flush=True)
    if '--frames-only' not in sys.argv:
        for nm in names:
            for v in variants:
                finish(nm, v, S2.TESTS[nm][1], loop=nm not in NOLOOP)
    print('done', round(time.time() - t0), 's')
