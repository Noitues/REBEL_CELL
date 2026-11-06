"""Peek into final/checks.json: list top-level keys and the structure of a path.
Usage: python cj_peek.py <json> [dotted.path] [maxlen]"""
import sys, json

def main():
    d = json.load(open(sys.argv[1], encoding='utf-8'))
    path = sys.argv[2] if len(sys.argv) > 2 else ''
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    cur = d
    if path:
        for k in path.split('.'):
            cur = cur[int(k)] if isinstance(cur, list) else cur[k]
    if isinstance(cur, dict):
        for k, v in cur.items():
            s = json.dumps(v)
            print(f'{k}: ({type(v).__name__}, {len(s)} ch) {s[:200]}')
    else:
        print(json.dumps(cur, indent=1)[:n])

if __name__ == '__main__':
    main()
