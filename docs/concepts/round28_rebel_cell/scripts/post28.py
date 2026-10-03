"""Round 28: finish canyon renders with the darker canyon grade (backdrop28.MODE["canyon"]).
python post28.py <tag> [--street] [--rain N] [--size W,H]   -> ../scratch/backdrops/<tag>_night.png"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import backdrop28 as B

if __name__ == "__main__":
    a = sys.argv[1:]
    tag = a[0]
    street = "--street" in a
    rain = int(a[a.index("--rain") + 1]) if "--rain" in a else None
    size = tuple(int(v) for v in a[a.index("--size") + 1].split(",")) if "--size" in a else None
    B.finish(tag, "night", rain_seed=rain, street=street, size=size, M=B.MODE["canyon"])
