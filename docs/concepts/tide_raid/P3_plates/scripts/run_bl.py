"""run blender headless under the shared GPU lock: python run_bl.py <spec.json> <log> [--nolock]"""
import subprocess, sys, time
sys.path.insert(0, 'D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts')
import gpu_lock as GL
BL = 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe'
spec, logf = sys.argv[1], sys.argv[2]
nolock = '--nolock' in sys.argv
SC = 'D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts/p1_bl.py'
with open(logf, 'a') as lf:
    if not nolock:
        GL.acquire('tide_p3 ' + spec, poll=30, log=lambda *a: (lf.write(' '.join(map(str, a)) + '\n'), lf.flush()))
    try:
        r = subprocess.run([BL, '-b', '--factory-startup', '--python', SC, '--', spec], stdout=lf, stderr=subprocess.STDOUT)
        lf.write('exit %d\n' % r.returncode)
    finally:
        if not nolock:
            GL.release(log=lambda *a: lf.write(' '.join(map(str, a)) + '\n'))
