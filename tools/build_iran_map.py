"""Build seed/data/iran_provinces.json (SVG paths of the 31 provinces) from Natural Earth.

Usage:  python tools/build_iran_map.py ne_10m_admin_1_states_provinces.geojson
Source: https://github.com/nvkelso/natural-earth-vector (public domain)
Requires: shapely (dev only; not needed at runtime).
"""
import json
import math
import sys
from pathlib import Path

from shapely.geometry import shape
import warnings
warnings.filterwarnings('ignore')

SRC = sys.argv[1]
OUT = Path(__file__).resolve().parent.parent / "seed" / "data" / "iran_provinces.json"
WIDTH = 1000.0

# Lambert conformal conic (spherical) tuned for Iran
PHI1, PHI2, PHI0, LAM0 = map(math.radians, (30, 38, 32, 54))
N = math.log(math.cos(PHI1) / math.cos(PHI2)) / math.log(
    math.tan(math.pi / 4 + PHI2 / 2) / math.tan(math.pi / 4 + PHI1 / 2))
F = math.cos(PHI1) * math.tan(math.pi / 4 + PHI1 / 2) ** N / N
RHO0 = F / math.tan(math.pi / 4 + PHI0 / 2) ** N


def project(lon, lat):
    phi, lam = math.radians(lat), math.radians(lon)
    rho = F / math.tan(math.pi / 4 + phi / 2) ** N
    th = N * (lam - LAM0)
    return rho * math.sin(th), -(RHO0 - rho * math.cos(th))


def proj_geom(g):
    from shapely.ops import transform
    return transform(lambda x, y, z=None: project(x, y), g)


data = json.load(open(SRC))
feats = [f for f in data["features"] if f["properties"].get("admin") == "Iran"]
geoms = []
for f in feats:
    g = shape(f["geometry"])
    g = proj_geom(g)
    # drop tiny islands, keep big rings
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    polys = [p for p in polys if p.area > 1e-6]
    from shapely.geometry import MultiPolygon
    geoms.append((f, MultiPolygon(polys) if len(polys) > 1 else polys[0]))

minx = min(g.bounds[0] for _, g in geoms)
miny = min(g.bounds[1] for _, g in geoms)
maxx = max(g.bounds[2] for _, g in geoms)
maxy = max(g.bounds[3] for _, g in geoms)
scale = WIDTH / (maxx - minx)
H = (maxy - miny) * scale
pad = 12


def norm_pt(x, y):
    return (x - minx) * scale + pad, (y - miny) * scale + pad


def ring_d(coords):
    pts = [norm_pt(x, y) for x, y in coords]
    return "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts[:-1]) + "Z"


out = []
for f, g in geoms:
    g = g.simplify(0.35 / scale, preserve_topology=True)
    polys = list(g.geoms) if g.geom_type == "MultiPolygon" else [g]
    d = ""
    for p in polys:
        d += ring_d(list(p.exterior.coords))
        for hole in p.interiors:
            d += ring_d(list(hole.coords))
    rp = max(polys, key=lambda p: p.area).representative_point()
    cx, cy = norm_pt(rp.x, rp.y)
    props = f["properties"]
    out.append({
        "name": props["name_fa"].replace("استان ", "").strip(),
        "name_en": props["name"],
        "iso": props["iso_3166_2"] if props["name"] != "Alborz" else "IR-32",
        "path": d,
        "cx": round(cx, 1),
        "cy": round(cy, 1),
    })

# crowded north-west labels: nudge so they do not overlap
ADJUST = {"West Azarbaijan": (-4, 38), "East Azarbaijan": (18, 14), "Ardebil": (6, -6), "Bushehr": (-14, 6)}
for o in out:
    dx, dy = ADJUST.get(o["name_en"], (0, 0))
    o["cx"] = round(o["cx"] + dx, 1)
    o["cy"] = round(o["cy"] + dy, 1)

out.sort(key=lambda p: p["name_en"])
CITIES = {"ارومیه": (45.07, 37.55), "بیرجند": (59.22, 32.87), "شیراز": (52.58, 29.59), "سراب": (47.54, 37.94)}
cities = []
for name, (lon, lat) in CITIES.items():
    x, y = norm_pt(*project(lon, lat))
    cities.append({"name": name, "x": round(x, 1), "y": round(y, 1)})

result = {"cities": cities, "width": round(WIDTH + 2 * pad), "height": round(H + 2 * pad), "provinces": out}
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(result, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
print("provinces:", len(out), "size:", result["width"], result["height"], "bytes:", OUT.stat().st_size)
