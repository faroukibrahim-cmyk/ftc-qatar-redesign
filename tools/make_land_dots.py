"""Precompute the globe's land dots from world-atlas land-110m.json (TopoJSON).

Writes src/data/land-dots.json: a flat [lat, lon, lat, lon, ...] list of points on a
Fibonacci sphere that fall on land, so the browser needs no TopoJSON decoder.
"""
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
topo = json.loads((ROOT / "src/vendor/land-110m.json").read_text())
sx, sy = topo["transform"]["scale"]; tx, ty = topo["transform"]["translate"]

arcs = []
for arc in topo["arcs"]:
    x = y = 0; pts = []
    for dx, dy in arc:
        x += dx; y += dy
        pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)

def ring(idx):
    out = []
    for i in idx:
        a = arcs[i] if i >= 0 else arcs[~i][::-1]
        out.extend(a if not out else a[1:])
    return out

polys = []
def collect(g):
    if g["type"] == "GeometryCollection":
        for x in g["geometries"]: collect(x)
    elif g["type"] == "Polygon": polys.append([ring(r) for r in g["arcs"]])
    elif g["type"] == "MultiPolygon":
        for p in g["arcs"]: polys.append([ring(r) for r in p])
for obj in topo["objects"].values(): collect(obj)

def bbox(r):
    xs = [p[0] for p in r]; ys = [p[1] for p in r]
    return min(xs), min(ys), max(xs), max(ys)
polys = [(bbox(p[0]), p) for p in polys]

def inside(r, x, y):
    c = False; j = len(r) - 1
    for i in range(len(r)):
        xi, yi = r[i]; xj, yj = r[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi: c = not c
        j = i
    return c

def on_land(lon, lat):
    for (x0, y0, x1, y1), p in polys:
        if x0 <= lon <= x1 and y0 <= lat <= y1 and inside(p[0], lon, lat) and not any(inside(h, lon, lat) for h in p[1:]):
            return True
    return False

N = 16000; golden = math.pi * (3 - math.sqrt(5)); out = []
for i in range(N):
    y = 1 - (i / (N - 1)) * 2; r = math.sqrt(1 - y * y); th = golden * i
    lat = math.degrees(math.asin(y)); lon = math.degrees(math.atan2(math.sin(th) * r, math.cos(th) * r))
    if lat > -60 and on_land(lon, lat): out += [round(lat, 2), round(lon, 2)]
(ROOT / "src/data").mkdir(exist_ok=True)
(ROOT / "src/data/land-dots.json").write_text(json.dumps(out, separators=(",", ":")))
print(len(out) // 2, "land dots")
