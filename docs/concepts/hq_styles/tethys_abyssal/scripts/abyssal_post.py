"""AAA-2 post (the base post_city.aaa, unchanged) for an abyssal render.
python abyssal_post.py <stem> <out.png> [target_median]     stem = <outdir>/t_over_aaa
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.normpath(os.path.join(HERE, "..", "..", "..", "route_map_graph", "hq_tethys", "scripts"))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(BASE, "city_base"))
import post_city as PC  # noqa: E402

if __name__ == "__main__":
    tg = float(sys.argv[3]) if len(sys.argv) > 3 else 0.16
    PC.aaa(sys.argv[1], sys.argv[2], target=tg)
