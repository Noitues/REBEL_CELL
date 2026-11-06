"""Render the 4 motion tests (normal + reduce-motion): python tests.py <daemon|lock|home|bloom> [normal|reduce]
Outputs tests/<name>_<variant>.mp4 (960x540, 30 fps), .gif (640x360, 15 fps) and tests/<name>_sheet.png, tests/metrics_<name>.txt."""
import sys, os, time, subprocess, json
from stage import *
import beats_b as B
import beats_c as C

TD = OUTDIR + 'tests/'
os.makedirs(TD, exist_ok=True)
FR = WORKD + 'frames/'
os.makedirs(FR, exist_ok=True)


def sharp(im):
    return im.filter(ImageFilter.UnsharpMask(1.2, 40, 2))


TESTS = {
    # name: (fn, box, total frames normal, total frames reduce, kwargs normal, kwargs reduce)
    'daemon': dict(fn=B.b_daemon, box=(330, 300, 1290, 840), n=(120, 80)),
    'lock': dict(fn=B.b_lock, box=(1090, 380, 1690, 718), n=(105, 105)),
    'home': dict(fn=B.b_home, box=(0, 420, 960, 960), n=(105, 105)),
    'bloom': dict(fn=C.b_bloom, box=(150, 300, 1110, 840), n=(105, 105)),
}
XFADE = 9


def render(name, variant):
    t = TESTS[name]
    reduce = variant == 'reduce'
    n = t['n'][1 if reduce else 0]
    box = t['box']
    ims = []
    kw = {'reduce': reduce}
    if name == 'home':
        kw['f_imp'] = 36
    for f in range(n):
        p = FR + '%s_%s%s_%03d.png' % (name, variant, {'home_normal': 'b', 'daemon_normal': 'b'}.get(name + '_' + variant, ''), f)
        if os.path.exists(p):
            im = Image.open(p).convert('RGB')
        else:
            t0 = time.time()
            a = t['fn'](f, **kw)
            im = crop_scale(a, box, (960, 540))
            if box[2] - box[0] != 960:
                im = sharp(im)
            im.save(p)
            if f % 10 == 0:
                print(name, variant, f, round(time.time() - t0, 1), flush=True)
        ims.append(im)
    # loop: cross-fade the tail into frame 0 so the GIF/MP4 loops without a pop
    arr = [np.asarray(i, np.float32) for i in ims]
    first = arr[0]
    for k in range(XFADE):
        j = n - XFADE + k
        tt = (k + 1) / float(XFADE)
        arr[j] = arr[j] * (1 - tt) + first * tt
    return [np.clip(a + .5, 0, 255).astype(np.uint8) for a in arr], arr


def write_video(frames, mp4):
    cmd = [FFMPEG, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '960x540', '-r', '30', '-i', '-',
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', '-movflags', '+faststart', mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()


def write_gif(mp4, gif):
    cmd = [FFMPEG, '-y', '-loglevel', 'error', '-i', mp4, '-vf',
           'fps=15,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=5',
           '-loop', '0', gif]
    subprocess.run(cmd, check=True)


def metrics(frames):
    lum = [float((f.astype(np.float32) * np.array([.2126, .7152, .0722], np.float32)).sum(-1).mean()) / 255 for f in frames]
    d = np.abs(np.diff(lum))
    # per-frame fraction of pixels that changed by more than 25% of full scale (a flash / strobe proxy)
    big = []
    for a, b in zip(frames[:-1], frames[1:]):
        big.append(float((np.abs(a.astype(np.int16) - b.astype(np.int16)).max(-1) > 64).mean()))
    # shake proxy: best integer shift (<=6 px) between consecutive frames, by cross-correlation of luminance rows/cols
    sh = []
    for a, b in zip(frames[:-1], frames[1:]):
        la = a[::2, ::2].astype(np.float32).mean(-1)
        lb = b[::2, ::2].astype(np.float32).mean(-1)
        best = (1e18, 0, 0)
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                e_ = float(np.abs(np.roll(la, (dy, dx), (0, 1))[8:-8, 8:-8] - lb[8:-8, 8:-8]).mean())
                if e_ < best[0]:
                    best = (e_, dy, dx)
        sh.append(max(abs(best[1]), abs(best[2])) * 2)
    return dict(max_dlum=round(float(d.max()), 4), mean_dlum=round(float(d.mean()), 4), max_big_frac=round(max(big), 4),
                frames_big_gt1pct=int(sum(1 for b in big if b > .01)), max_shift_px=int(max(sh)))


if __name__ == '__main__':
    name = sys.argv[1]
    variants = sys.argv[2:] or ['normal', 'reduce']
    res = {}
    for v in variants:
        u8, _ = render(name, v)
        mp4 = TD + '%s_%s.mp4' % (name, v)
        write_video(u8, mp4)
        write_gif(mp4, TD + '%s_%s.gif' % (name, v))
        res[v] = dict(frames=len(u8), seconds=round(len(u8) / 30.0, 2), **metrics(u8))
        print(name, v, res[v], flush=True)
        # contact sheet row
        k = 10
        idx = [int(i * (len(u8) - 1) / (k - 1)) for i in range(k)]
        sh = Image.new('RGB', (320 * 5, 180 * 2))
        for i, j in enumerate(idx):
            sh.paste(Image.fromarray(u8[j]).resize((320, 180), Image.LANCZOS), ((i % 5) * 320, (i // 5) * 180))
        sh.save(TD + '%s_%s_sheet.png' % (name, v))
    p = TD + 'metrics_%s.json' % name
    old = json.load(open(p)) if os.path.exists(p) else {}
    old.update(res)
    json.dump(old, open(p, 'w'), indent=1)
