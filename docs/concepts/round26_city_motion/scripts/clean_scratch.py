"""Remove this round's scratch folder (and only it) plus Python caches in scripts/."""
import os
import shutil
HERE = os.path.dirname(os.path.abspath(__file__))
for p in (os.path.join(os.path.dirname(HERE), 'scratch'), os.path.join(HERE, '__pycache__')):
    if os.path.isdir(p):
        shutil.rmtree(p)
        print('removed', p)
