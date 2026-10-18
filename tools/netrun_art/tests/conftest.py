import os
import sys

# Put tools/ on the path so `import netrun_art` works from any cwd.
_TOOLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
