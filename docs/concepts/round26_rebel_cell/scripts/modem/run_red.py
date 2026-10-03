"""Round 26: render the locked F1B tenement facade (round 12) at night with the betrayed red MODEM sign.
python run_red.py -> ../../site_modem_red_night.png (+ scratch/modem/*)
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
R26 = os.path.normpath(os.path.join(HERE, "..", ".."))
SC = os.path.join(R26, "scratch", "modem")
BL = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"
os.makedirs(SC, exist_ok=True)
subprocess.run([sys.executable, os.path.join(HERE, "red_sign.py")], check=True)
env = dict(os.environ, MF_VAR="b", MF_PCT="100", MF_SAMPLES="48", MF_SIGN=os.path.join(SC, "sign_red.png"),
           MF_SPILL="#ff1622", MF_SPILL2="#ff5a2a", MF_ACCENT="#ff2a3a", MF_SIGN_K="1.9")
base = os.path.join(SC, "f1_night")
with open(os.path.join(SC, "log_modem.txt"), "w") as log:
    subprocess.run([BL, "-b", "--factory-startup", "--python", os.path.join(HERE, "scene.py"), "--", "f1", "night", base],
                   stdout=log, stderr=subprocess.STDOUT, env=env)
subprocess.run([sys.executable, os.path.join(HERE, "post.py"), base, "night", os.path.join(SC, "f1_night.png")], check=True, env=env)
shutil.copy(os.path.join(SC, "f1_night.png"), os.path.join(R26, "site_modem_red_night.png"))
print("wrote site_modem_red_night.png")
