"""Shared helpers for the Coffee Episodes generators.

Re-exports episode 1's helpers, palette and maps (schema/examples/coffee_families.py) and adds what episodes 2+
share: season colours, multi-segment camera moves, source lines, documents, and the project build/write step.
"""
import json, math, os, random, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "schema", "examples"))
from coffee_families import *  # noqa: F401,F403
from coffee_families import zero_tangents

FPS = 30  # episodes 2-10 (STYLE_GUIDE.md); episode 1 is 24 fps

JSON_DIR = os.path.join(_HERE, "..", "json")

# season palette (STYLE_GUIDE.md)
TEA, WATER, CAF = "#8DB33A", "#4FB3C8", "#3B73B9"
CIN, GREY2, TEALEAF, OXID, KRAFT = "#B5763E", "#C9C9C9", "#3A3A2E", "#5B4A2E", "#D9BE93"
ROAST = ["#F1E1BE", "#E3C77A", "#B9814A", "#6B4226", "#2B1D16"]


def _ease(t0, t1):
    return (f"var u = Math.min(1, Math.max(0, (time - {t0}) / {t1 - t0})); "
            f"u = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; ")


def zmulti(s0, segs):
    """Rig scale over several zoom segments [(t0, t1, s1)], log-interpolated."""
    e, prev = f"var s = {math.log(s0):.5f}; ", s0
    for t0, t1, s1 in segs:
        e += f"if (time > {t0}) {{ {_ease(t0, t1)}s = {math.log(prev):.5f} * (1 - u) + {math.log(s1):.5f} * u; }} "
        prev = s1
    return X(e + "var k = Math.exp(s) * 100; [k, k]")


def pmulti(p0, segs):
    e, prev = f"var x = {p0[0]:.2f}, y = {p0[1]:.2f}; ", p0
    for t0, t1, p in segs:
        e += (f"if (time > {t0}) {{ {_ease(t0, t1)}x = {prev[0]:.2f} + ({p[0] - prev[0]:.2f}) * u; "
              f"y = {prev[1]:.2f} + ({p[1] - prev[1]:.2f}) * u; }} ")
        prev = p
    return X(e + "[x, y]")


def src(name, s, t, t1):
    return caps(name, s, [90, 1040], t, t1, size=14, just="left", opacity=fade_in(t))


def fade_all(layers, t, d=0.4, keep=()):
    for j, l in enumerate(layers):
        if l["type"] != "null" and l["name"] not in keep and l["out"] > t:
            add_out(l, t + (j % 5) * 0.03, d)
    return layers


def dim(layers, t, to=28, d=0.4):
    """Grey a group back (opacity to `to`) from t, keeping earlier opacity keys."""
    for l in layers:
        if l["type"] == "null" or l["in"] >= t:
            continue
        op = l["transform"].get("opacity")
        ks = [k for k in op["keyframes"] if k["time"] < t] if isinstance(op, dict) else []
        last = ks[-1]["value"] if ks else (op if isinstance(op, (int, float)) else 100)
        l["transform"]["opacity"] = A(*ks, K(t, last), K(t + d, to))
    return layers


def grey_leaf(name, L, pos, t0, t1, **tr):
    return shape(name, [G("Vein", path([(-L * 0.4, 0), (L * 0.38, 0)]), stroke(INK, max(1.5, L * 0.012))),
                        G("Leaf", leaf_path(L), stroke(INK, max(2, L * 0.015)), fill(LAND))], pos, t0, t1, **tr)


def doc(name, lines, pos, size, t, t1, hl_line=None, credit=None):
    """Flat recreation of a printed page: outlined sheet, text lines, a highlighter swipe on one line."""
    w, h = size
    x, y = pos
    out = []
    for j, (s, sz, font) in enumerate(lines):
        ly = y - h / 2 + 70 + j * sz * 1.5
        out.append(text(f"{name} L{j + 1}", s, [x, ly], sz, INK, t + 0.2, t1, font=font, opacity=fade_in(t + 0.2)))
        if j == hl_line:
            ww = tw(s, sz, font) + 20
            out.append(marker(f"{name} Swipe", x - ww / 2, ly, ww, t + 0.9, t1, size=sz))
    out.append(shape(name, paper("Sheet", rect([w, h], None, 4), WHITE, line="#D0D0D0", lw=2, sh=6, sh_op=6), [x, y], t, t1,
                     scale=grow(t, 100, 0.4)))
    if credit:
        out.append(src(f"{name} Credit", credit, t + 0.4, t1))
    return out


def sacks(name, n, col, x, base, t, t1, w=56, h=26):
    gs = [G(f"Sack {j + 1}", rect([w, h], [0, -j * (h + 4) - h / 2], 9), fill(col), tr={"opacity": fade_in(t + j * 0.06, 0.15)})
          for j in range(n)]
    return shape(name, gs, [x, base], t, t1)


def word_marker(name, line, word, center, y, size, t, t1, font=HEAD):
    """Highlighter swipe under one word of a centred line."""
    i = line.index(word)
    x0 = center - tw(line, size, font) / 2 + tw(line[:i], size, font)
    return marker(name, x0 - 10, y, tw(word, size, font) + 20, t, t1, size=size)


def _cut_opacity(op):
    """Turn every fade to/from 0 into a hold (a cut). Returns [(t0, t1, 'in'|'out')] for the scale pops."""
    ks = op["keyframes"]
    ev = []
    vals = [k["value"] for k in ks]
    for j, (a, b) in enumerate(zip(ks, ks[1:])):
        if vals[j] == 0 and vals[j + 1] != 0:
            ev.append((a["time"], b["time"], "in"))
            a["value"] = b["value"]
            a["interp"] = "hold"
            a.pop("ease", None)
        elif vals[j + 1] == 0 and vals[j] != 0:
            ev.append((a["time"], b["time"], "out"))
            a["interp"] = "hold"
            a.pop("ease", None)
    for k in ks:
        if k["value"] == 0:  # an invisible stretch must not ramp into the next key
            k["interp"] = "hold"
            k.pop("ease", None)
    return ev


def _pop(tr, ev, key="scale"):
    base = tr.get(key, [100, 100])
    if isinstance(base, dict) or not ev:
        return
    ks = []
    for t0, t1, kind in ev:
        z = [0, 0]
        ks += [K(t0, z), K(t1, base)] if kind == "in" else [K(t0, base), K(t1, z)]
    ks.sort(key=lambda k: k["time"])
    tr[key] = {"keyframes": ks}


def _extent(items):
    """Largest distance from the layer origin reached by any path vertex or item position."""
    m = 0
    for it in items:
        if it.get("type") == "group":
            m = max(m, _extent(it.get("items", [])))
            p = (it.get("transform") or {}).get("position")
            if isinstance(p, list):
                m = max(m, abs(p[0]), abs(p[1]))
        elif it.get("type") == "path":
            for x, y in it["path"]["vertices"]:
                m = max(m, abs(x), abs(y))
        else:
            p, s = it.get("position"), it.get("size")
            for v in (p, s):
                if isinstance(v, list):
                    m = max(m, abs(v[0]), abs(v[1]))
    return m


def cut_pass(proj):
    """Channel rule: nothing fades in or out. Appearing/disappearing is a cut, plus a scale pop where the scale is free.
    Partial opacity (greyed-back groups) stays animated."""
    def walk(items):
        for it in items:
            if it.get("type") != "group":
                continue
            tr = it.get("transform") or {}
            op = tr.get("opacity")
            if isinstance(op, dict) and "keyframes" in op:
                _pop(tr, _cut_opacity(op))
            walk(it.get("items", []))
    for c in proj["compositions"]:
        for l in c["layers"]:
            if l["type"] in ("null", "precomp", "adjustment"):
                continue
            tr = l.get("transform", {})
            op = tr.get("opacity")
            if isinstance(op, dict) and "keyframes" in op:
                ev = _cut_opacity(op)
                if l.get("enabled") is not False and _extent(l.get("shapes", [])) < 700:  # maps, routes and pipes drawn in comp space only cut
                    _pop(tr, ev)
            walk(l.get("shapes", []))


def build_project(scenes, master_name, aep_name):
    comps, main = [], []
    t = 0.0
    for cname, d, fn in scenes:
        layers = fn(d)
        names = [l["name"] for l in layers]
        assert len(names) == len(set(names)), (cname, [n for n in names if names.count(n) > 1])
        missing = [(l["name"], l["parent"]) for l in layers if l.get("parent") and l["parent"] not in names]
        assert not missing, (cname, "parent not found", missing)
        mattes = [(l["name"], l["trackMatte"]["target"]) for l in layers if l.get("trackMatte") and l["trackMatte"]["target"] not in names]
        assert not mattes, (cname, "matte not found", mattes)
        bad = [l["name"] for l in layers if not l["out"] > l["in"]]
        assert not bad, (cname, "out <= in", bad)
        comps.append({"name": cname, "width": W, "height": H, "fps": FPS, "duration": d, "backgroundColor": WHITE, "layers": layers})
        main.insert(0, {"name": cname, "type": "precomp", "source": cname, "startTime": t, "in": t, "out": t + d,
                        "transform": {"scale": A(KL(t, [100, 100]), KL(t + d, [HS * 100, HS * 100]))}})
        t += d
    grain = {"name": "Paper Grain", "type": "adjustment", "in": 0, "out": t,
             "effects": [{"matchName": "ADBE Noise", "props": {"ADBE Noise-0001": 2.0}}]}
    master = {"name": master_name, "width": W, "height": H, "fps": FPS, "duration": t, "backgroundColor": WHITE, "layers": [grain] + main}
    proj = {"$schema": "../../schema/motion.schema.json", "file": aep_name, "expressionEngine": "javascript-1.0",
            "bitDepth": "8 bpc", "compositions": [master] + comps}
    cut_pass(proj)
    zero_tangents(proj)
    return proj


def write(scenes, master_name, stem):
    proj = build_project(scenes, master_name, stem + ".aep")
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(JSON_DIR, stem + ".json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(proj, f, indent=1, ensure_ascii=False)
    t = 0
    for c, d, _ in scenes:
        print(f"{int(t // 60)}:{t % 60:04.1f}  {c}")
        t += d
    print("total", t, "s,", sum(len(c["layers"]) for c in proj["compositions"]), "layers")


def truck(name, pos, t0, t1, s=100, col=INK, **tr):
    """Coyote pickup, side view, facing right (ep. 9, ep. 10)."""
    items = [G("Wheels", ell([30, 30], [-38, 22]), ell([30, 30], [40, 22]), stroke(col, 4), fill(WHITE)),
             G("Cab", path([(10, 6), (10, -30), (40, -30), (62, -6), (62, 6)], True), stroke(col, 4), fill(WHITE)),
             G("Bed", rect([80, 30], [-30, -9]), stroke(col, 4), fill(WHITE))]
    return shape(name, items, pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)
