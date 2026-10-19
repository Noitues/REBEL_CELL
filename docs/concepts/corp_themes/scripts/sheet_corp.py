"""Contact sheet for one corp: python sheet_corp.py halcyon G_scan,G_spotted,... [accent r,g,b]"""
import sys
import theme_lib as T
corp, names = sys.argv[1], sys.argv[2].split(",")
acc = tuple(int(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 else (200, 200, 210)
print(T.sheet(corp, names, accent=acc))
