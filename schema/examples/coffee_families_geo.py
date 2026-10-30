"""Builds coffee_families_geo.json, the simplified map outlines used by coffee_families.py.

    python schema/examples/coffee_families_geo.py <ne_110m_land.geojson> <mexico_states.geojson>

Sources (download them first):
  land:   https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_land.geojson (public domain)
  states: https://raw.githubusercontent.com/angelnmara/geojson/master/mexicoHigh.json

Output is lon/lat in degrees: {"land": [ring, ...], "mexico": {state: [ring, ...]}}. Rings are simplified with
Douglas-Peucker so the generated JSX stays small.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    n = (dx * dx + dy * dy) ** 0.5 or 1e-9
    best, idx = -1, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = abs(dy * x - dx * y + x1 * y0 - y1 * x0) / n
        if d > best:
            best, idx = d, i
    if best <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)


def ring(coords, eps):
    pts = [tuple(p[:2]) for p in coords]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    # split the closed ring in two so the endpoints of each half are far apart
    h = len(pts) // 2
    out = rdp(pts[:h + 1], eps)[:-1] + rdp(pts[h:] + [pts[0]], eps)[:-1]
    return [[round(x, 2), round(y, 2)] for x, y in out]


def polys(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [p[0] for p in geom["coordinates"]]


def main(land_path, mx_path):
    land = []
    for f in json.load(open(land_path, encoding="utf-8"))["features"]:
        for c in polys(f["geometry"]):
            lats = [p[1] for p in c]
            if max(lats) < -55 or min(lats) > 72:  # Antarctica, Arctic islands
                continue
            r = ring(c, 0.18)
            if len(r) >= 4:
                land.append(r)
    mexico = {}
    for f in json.load(open(mx_path, encoding="utf-8"))["features"]:
        rs = [ring(c, 0.035) for c in polys(f["geometry"])]
        mexico[f["properties"]["name"]] = [r for r in rs if len(r) >= 4]
    out = os.path.join(HERE, "coffee_families_geo.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"land": land, "mexico": mexico}, fh, ensure_ascii=False, separators=(",", ":"))
    print(out, sum(len(r) for r in land), "land points,", sum(len(r) for v in mexico.values() for r in v), "state points")


if __name__ == "__main__":
    main(*sys.argv[1:3])
