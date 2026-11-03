"""Generator for coffee_families.json, a 3:00 Vox-style explainer on the coffee species (see coffee_families_script.md).

    python schema/examples/coffee_families.py            # writes coffee_families.json next to this file
    go run ./cmd/json2jsx -i schema/examples/coffee_families.json

White background, flat cut-paper shapes, one colour per family, and only match cuts between scenes. Each scene
ends on a shape at the exact screen position/size where the next scene's first shape starts. The master comp
pushes every scene in by HS (3 %), so a handoff value at the end of a scene is mapped through inv()/HS.

Maps come from coffee_families_geo.json (see coffee_families_geo.py). A map is drawn in "map space"
(lon * K, -lat * K) and parented to a rig null whose anchor is the focus point, so zooms are a scale on the rig.

Timing: 24 fps. Scenes are written in design seconds; build() passes each one through retime(), which snaps keys to
frames and makes every in/out animation a whole number of 12-frame beats (0.5 s, 1 s, ...). build(durations)
re-times the scenes to other lengths (the voiceover cut, Coffee Episodes/generators/01_coffee_families_vo.py) the
same way, so nothing is time-stretched. check_timing() refuses a build that breaks the rule.

Episode 1 draws its cherry, cross-section, leaves, shrubs and beans with coffee_cherry(), coffee_section(),
coffee_leaf(), icon_shrub() and bean_items2(). Episodes 2-10 import this module and still use the older cherry(),
cherry_section(), leaf_path() and stroke icons, which are left unchanged.
"""
import json, math, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1920, 1080, 24
BEAT = 12  # frames: every in and out animation lasts a whole number of beats (see retime())
CX, CY = W / 2, H / 2
HEAD, SCI, LAB, BODY = "Chonburi-Regular", "Georgia-Italic", "Arial-BoldMT", "ArialMT"
INK, GREY, LINE, LAND, WHITE = "#161616", "#8C8C8C", "#E2E2E2", "#ECECEC", "#FFFFFF"
ARA, ROB, SMALL, MX, RUST, HL = "#D9432F", "#7A5440", "#6F8796", "#2F7D5A", "#E8892B", "#FFD84D"
ARA_DARK, SEED, SEED_LINE, PULP, STEM = "#8E2A1C", "#F1E1BE", "#C9A56E", "#F7CDBE", "#5B4A2E"
HS = 1.03  # master push-in per scene
GEO = json.load(open(os.path.join(HERE, "coffee_families_geo.json"), encoding="utf-8"))

# ---------- keyframes ----------
SNAP = {"inInfluence": 85, "outInfluence": 10, "inSpeed": 0, "outSpeed": 0}
EXIT = {"inInfluence": 10, "outInfluence": 70, "inSpeed": 0, "outSpeed": 0}  # starts slow, leaves at speed


def K(t, v, e=SNAP):
    d = {"time": round(t, 3), "value": v}
    if e:
        d["ease"] = e
    return d


def KS(t, v):
    return K(t, v, "easeInOut")


def KL(t, v):
    return K(t, v, None)


def A(*ks):
    return {"keyframes": list(ks)}


def X(expr):
    return {"expression": expr}


def fade_in(t, d=0.35):
    return A(K(t, 0), K(t + d, 100))


def fade_io(a, b, d=0.3):
    return A(K(a, 0), K(a + d, 100), K(b - d, 100), K(b, 0))


def grow(t, s=100, d=0.45):
    return A(K(t, [0, 0]), K(t + d, [s, s]))


def slide(t, pos, dx=0, dy=30, d=0.6):
    return A(K(t, [pos[0] + dx, pos[1] + dy]), K(t + d, pos))


def u_expr(t0, t1):
    """Eased 0..1 progress (cubic in-out) as an expression snippet."""
    return (f"var u = Math.min(1, Math.max(0, (time - {t0}) / {t1 - t0})); "
            f"u = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; ")


def zoom_scale(t0, t1, s0, s1):
    """Rig scale that zooms at a constant perceived speed (log interpolation)."""
    return X(u_expr(t0, t1) + f"var s = Math.exp({math.log(s0):.5f} * (1 - u) + {math.log(s1):.5f} * u) * 100; [s, s]")


def zoom_pos(t0, t1, a, b):
    return X(u_expr(t0, t1) + f"[{a[0]:.2f} + ({b[0] - a[0]:.2f}) * u, {a[1]:.2f} + ({b[1] - a[1]:.2f}) * u]")


def inv(p):
    """Scene-space point that lands on screen point p at the end of a scene (master push-in HS)."""
    return [round(CX + (p[0] - CX) / HS, 2), round(CY + (p[1] - CY) / HS, 2)]


def fwd(p):
    """Screen point of scene-space point p at the end of a scene."""
    return [round(CX + (p[0] - CX) * HS, 2), round(CY + (p[1] - CY) * HS, 2)]


# ---------- shape items ----------
def rect(size, pos=None, r=0):
    d = {"type": "rect", "size": size}
    if pos is not None:
        d["position"] = pos
    if r:
        d["roundness"] = r
    return d


def ell(size, pos=None):
    d = {"type": "ellipse", "size": size}
    if pos is not None:
        d["position"] = pos
    return d


def path(verts, closed=False, i=None, o=None):
    p = {"closed": closed, "vertices": [[round(a, 2), round(b, 2)] for a, b in verts]}
    if i:
        p["inTangents"] = [[round(a, 2), round(b, 2)] for a, b in i]
    if o:
        p["outTangents"] = [[round(a, 2), round(b, 2)] for a, b in o]
    return {"type": "path", "path": p}


def arc(a, b, bend):
    """Quadratic-looking arc from a to b; bend is the bulge as a fraction of the chord (sign = side)."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    c = (mx - dy * bend, my + dx * bend)
    return path([a, b], False, i=[(0, 0), ((c[0] - b[0]) * 2 / 3, (c[1] - b[1]) * 2 / 3)],
                o=[((c[0] - a[0]) * 2 / 3, (c[1] - a[1]) * 2 / 3), (0, 0)])


def fill(c, op=None):
    d = {"type": "fill", "color": c}
    if op is not None:
        d["opacity"] = op
    return d


def stroke(c, w, op=None, cap="round", join="round", dashes=None):
    """dashes: (dash, gap) or (dash, gap, offset); each a number or animated value."""
    d = {"type": "stroke", "color": c, "strokeWidth": w, "lineCap": cap, "lineJoin": join}
    if op is not None:
        d["opacity"] = op
    if dashes is not None:
        d["dashes"] = dict(zip(("dash", "gap", "offset"), dashes))
    return d


def trim(s=None, e=None, o=None):
    d = {"type": "trim"}
    for k, v in (("start", s), ("end", e), ("offset", o)):
        if v is not None:
            d[k] = v
    return d


def G(name, *items, tr=None):
    d = {"type": "group", "name": name, "items": list(items)}
    if tr:
        d["transform"] = tr
    return d


def paper(name, item, col, line=None, lw=4, sh=6, sh_op=9):
    """Cut-paper element: a face plus a hard offset shadow underneath."""
    face = [item] + ([stroke(line, lw)] if line else []) + [fill(col)]
    return [G(name, *face), G(name + " Shadow", item, fill("#000000", sh_op), tr={"position": [0, sh]})]


def leaf_path(L, wr=0.42):
    h, dx = L * wr * 0.66, L * 0.3
    return path([(-L / 2, 0), (L / 2, 0)], True, i=[(dx, h), (-dx, -h)], o=[(dx, -h), (-dx, h)])


def bean_items(name, w, h, col, crease, s_curve):
    if s_curve:
        c = path([(0, -h * 0.4), (0, h * 0.4)], False, i=[(0, 0), (-w * 0.25, -h * 0.2)], o=[(w * 0.25, h * 0.2), (0, 0)])
    else:
        c = path([(0, -h * 0.4), (0, h * 0.4)])
    return [G(name + " Crease", c, stroke(crease, max(3, w * 0.07))), *paper(name, ell([w, h]), col)]


# ---------- layers ----------
def _tr(L, tr):
    for k, v in tr.items():
        if v is None:
            continue
        if k in ("parent", "enabled", "trackMatte"):
            L[k] = v
        elif k == "position" and isinstance(v, dict) and "expression" in v and "value" not in v and "keyframes" not in v:
            L["transform"][k] = dict(v, value=L["transform"]["position"])
        else:
            L["transform"][k] = v
    return L


def shape(name, groups, pos, t0, t1, **tr):
    L = {"name": name, "type": "shape", "in": round(t0, 3), "out": round(t1, 3), "shapes": groups, "transform": {"position": pos}}
    return _tr(L, tr)


def text(name, s, pos, size, color, t0, t1, font=BODY, just="center", tracking=0, leading=0, **tr):
    T = {"string": s, "font": font, "fontSize": size, "fillColor": color, "justification": just}
    if tracking:
        T["tracking"] = tracking
    if leading:
        T["leading"] = leading
    L = {"name": name, "type": "text", "in": round(t0, 3), "out": round(t1, 3), "text": T, "transform": {"position": pos}}
    return _tr(L, tr)


def null(name, pos, t0, t1, anchor=None, **tr):
    L = {"name": name, "type": "null", "in": round(t0, 3), "out": round(t1, 3),
         "transform": {"position": pos, "anchorPoint": list(anchor if anchor is not None else pos)}}
    return _tr(L, tr)


def appear(L, t, dx=0, dy=24, d=0.55):
    p = L["transform"]["position"]
    L["transform"]["position"] = slide(t, p, dx, dy, d)
    L["transform"]["opacity"] = fade_in(t, d * 0.6)
    return L


def add_out(L, t, d=0.3):
    """Fade a layer out at t (keeps earlier opacity keys) and trim its out point."""
    tr = L["transform"]
    op = tr.get("opacity")
    if op is None or isinstance(op, (int, float)):
        v = 100 if op is None else op
        tr["opacity"] = A(K(t, v), K(t + d, 0))
    else:
        ks = op["keyframes"]
        ks[:] = [k for k in ks if k["time"] < t - 1e-6]
        last = ks[-1]["value"] if ks else 100
        ks += [K(t, last), K(t + d, 0)]
    L["out"] = round(min(L["out"], t + d), 3)
    return L


def parent_all(layers, parent):
    for L in layers:
        if "parent" not in L and L["name"] != parent:
            L["parent"] = parent
    return layers


def bg(D):
    return shape("BG", [G("BG", rect([W + 600, H + 600]), fill(WHITE))], [CX, CY], 0, D)


FONT_W = {HEAD: 0.62, SCI: 0.46, LAB: 0.68, BODY: 0.52}


def tw(s, size, font, tracking=0):
    return len(s) * size * (FONT_W[font] + tracking / 1000)


def marker(name, x0, y, w, t, t1, h=None, size=40, d=0.35, **tr):
    """Highlighter swipe from x0 rightwards, centred on the x-height of text with baseline y."""
    h = h or size * 0.62
    return shape(name, [G("Marker", rect([w, h], [w / 2, 0]), fill(HL))], [x0, y - size * 0.3], t, t1,
                 scale=A(K(t, [0, 100]), K(t + d, [100, 100])), **tr)


def wipe_text(name, s, pos, size, color, t, t1, font=HEAD, just="center", tracking=0, d=0.55, hl=False, parent=None):
    """Text revealed left-to-right by a hidden matte, optionally with a highlighter swipe behind it."""
    w = tw(s, size, font, tracking)
    x0 = pos[0] - (w / 2 if just == "center" else (w if just == "right" else 0))
    out = [shape(name + " Matte", [G("M", rect([w + 60, size * 1.6], [(w + 60) / 2, 0]), fill(WHITE))],
                 [x0 - 30, pos[1] - size * 0.32], t, t1, enabled=False, parent=parent,
                 scale=A(K(t, [0, 100]), K(t + d, [100, 100]))),
           text(name, s, pos, size, color, t, t1, font=font, just=just, tracking=tracking, parent=parent,
                trackMatte={"target": name + " Matte", "type": "Alpha"})]
    if hl:
        out.append(marker(name + " Marker", x0 - 12, pos[1], w + 24, t + d * 0.6, t1, size=size, parent=parent))
    return out


def caps(name, s, pos, t, t1, size=20, color=GREY, just="center", **tr):
    return text(name, s, pos, size, color, t, t1, font=LAB, just=just, tracking=140, **tr)


def leader(name, a, b, t, t1, col=INK, dot=True, **tr):
    items = [G("Line", path([a, b]), trim(0, A(K(t, 0), K(t + 0.4, 100))), stroke(col, 2.5))]
    if dot:
        items.insert(0, G("Dot", ell([10, 10], a), fill(col)))
    tr.setdefault("opacity", fade_in(t, 0.15))
    return shape(name, items, [0, 0], t, t1, **tr)


def lead(name, a, b, t, t1, col=INK):
    """Leader for episode 1: the dot pops, the line draws to the label; it leaves the way it came, with the label's fade."""
    out = t1 - 0.3
    dot = G("Dot", ell([10, 10], a), fill(col), tr={"anchorPoint": list(a), "position": list(a),
                                                     "scale": A(K(t, [0, 0]), K(t + 0.5, [100, 100]), K(out + 0.25, [100, 100]), K(out + 0.75, [0, 0]))})
    line = G("Line", path([a, b]), trim(A(K(out, 0), K(out + 0.5, 100)), A(K(t, 0), K(t + 0.5, 100))), stroke(col, 2.5))
    return shape(name, [dot, line], [0, 0], t, out + 0.75)


def disc(name, pos, d, col, t0, t1, icon=(), line=None, sh=5, **tr):
    face = paper("Disc", ell([d, d]), col, line=line, lw=5, sh=sh) if sh else [G("Disc", ell([d, d]), *([stroke(line, 5)] if line else []), fill(col))]
    return shape(name, list(icon) + face, pos, t0, t1, **tr)


def ticks(name, n, per_row, col, pos, t0, t1, w=4, h=16, gx=9, gy=24, right=False, **tr):
    gs = []
    for j in range(n):
        r, c = divmod(j, per_row)
        x = -c * gx if right else c * gx
        gs.append(rect([w, h], [x, r * gy]))
    return shape(name, [G("Ticks", *gs, fill(col))], pos, t0, t1, **tr)


# ---------- maps ----------
def map_pt(lonlat, k):
    return [round(lonlat[0] * k, 2), round(-lonlat[1] * k, 2)]


def screen(lonlat, k, center, o):
    """Screen point for a map framed with lon/lat `center` at screen `o`, k px per degree."""
    return [o[0] + (lonlat[0] - center[0]) * k, o[1] - (lonlat[1] - center[1]) * k]


def land_layer(name, k, t0, t1, col=LAND, bbox=None, **tr):
    items = []
    for r in GEO["land"]:
        if bbox:
            lo, la = [p[0] for p in r], [p[1] for p in r]
            if max(lo) < bbox[0] or min(lo) > bbox[2] or max(la) < bbox[1] or min(la) > bbox[3]:
                continue
        items.append(path([map_pt(p, k) for p in r], True))
    return shape(name, [G("Land", *items, fill(col))], [0, 0], t0, t1, **tr)


def in_land(lon, lat):
    hit = False
    for r in GEO["land"]:
        n = len(r)
        for i in range(n):
            (x1, y1), (x2, y2) = r[i], r[(i + 1) % n]
            if (y1 > lat) != (y2 > lat) and lon < (x2 - x1) * (lat - y1) / (y2 - y1) + x1:
                hit = not hit
    return hit


def state_centroid(name):
    pts = [p for r in GEO["mexico"][name] for p in r]
    return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]


# ---------- art ----------
CHERRY_D = 220


def cherry(prefix, t0, t1, rig, body_scale=None, show=0.0, leaf_t=None, detail_t=None):
    """Coffee cherry centred on its rig: body, highlight, navel, stem and leaf. Returns layers top -> bottom."""
    lt = leaf_t if leaf_t is not None else show
    dt = detail_t if detail_t is not None else show
    leaf = shape(f"{prefix} Leaf", [
        G("Vein", path([(-90, 0), (80, 0)]), stroke(WHITE, 4, 70)),
        *paper("Leaf", leaf_path(200), MX, sh=5)], [CX + 18, CY - 170], t0, t1, parent=rig,
        anchorPoint=[-100, 0], rotation=-28, scale=grow(lt, 100, 0.6))
    stem = shape(f"{prefix} Stem", [G("Stem", path([(0, -100), (18, -172)], False, i=[(0, 0), (-4, 24)], o=[(4, -24), (0, 0)]),
                                      trim(0, A(K(lt - 0.25, 0), K(lt + 0.15, 100))), stroke(STEM, 9))],
                 [CX, CY], t0, t1, parent=rig)
    body = shape(f"{prefix} Body", [
        G("Highlight", ell([54, 30], [-52, -58]), fill(WHITE, 45), tr={"rotation": -35, "opacity": fade_in(dt, 0.4)}),
        G("Navel", ell([24, 14], [0, 92]), stroke(ARA_DARK, 4), tr={"opacity": fade_in(dt, 0.4)}),
        *paper("Skin", ell([CHERRY_D, CHERRY_D]), ARA, sh=7)], [CX, CY], t0, t1, parent=rig, scale=body_scale)
    return [leaf, stem, body]


def cherry_section(prefix, t_open, t_close, t1, rig, thread_t=None):
    """Cross-section revealed by an iris inside the cherry: pulp and two seeds with flat sides facing."""
    def seed(name, side):
        s = 1 if side > 0 else -1
        # D-shaped seed: flat side towards the centre line
        v = [(s * 6, -72), (s * 6, 72)]
        p = path(v, True, i=[(s * 70, 0), (0, 0)], o=[(0, 0), (s * 70, 0)])
        return [G(name + " Groove", path([(s * 22, -40), (s * 22, 40)]), stroke(SEED_LINE, 3, 70)), G(name, p, stroke(SEED_LINE, 3), fill(SEED))]
    items = []
    if thread_t is not None:
        thr = path([(28, -50), (44, -18), (30, 14), (46, 48)], False, i=[(0, 0), (-8, -12), (8, -12), (-8, -12)], o=[(8, 12), (-8, 12), (8, 12), (0, 0)])
        items.append(G("Robusta Thread", thr, trim(0, A(K(thread_t, 0), K(thread_t + 0.9, 100))), stroke(ROB, 5)))
    items += seed("Seed R", 1) + seed("Seed L", -1)
    items.append(G("Pulp", ell([CHERRY_D - 26, CHERRY_D - 26]), fill(PULP)))
    sc = A(K(t_open, [0, 0]), K(t_open + 0.6, [100, 100]))
    if t_close is not None:
        sc["keyframes"] += [K(t_close, [100, 100]), K(t_close + 0.5, [0, 0])]
    return shape(f"{prefix} Section", items, [CX, CY], t_open, t1, parent=rig, scale=sc)


def icon_plant(col, tall=True, cherries=False):
    top = -30 if tall else -12
    items = [path([(0, 26), (0, top)])]
    ys = [16, 2, -12, -24] if tall else [16, 4, -6]
    for j, y in enumerate(ys):
        w = 16 if tall else 20
        items += [path([(0, y), (-w, y - 9)]), path([(0, y), (w, y - 9)])]
    out = [G("Plant", *items, stroke(col, 5))]
    if cherries:
        out.insert(0, G("Cherries", ell([10, 10], [-9, -2]), ell([10, 10], [9, 10]), ell([10, 10], [-9, 18]), fill(col)))
    return out


def icon_feather(col):
    vane = path([(0, -30), (0, 26)], True, i=[(0, 0), (-16, 20)], o=[(16, 18), (0, 0)])
    return [G("Spine", path([(-4, 34), (2, -30)]), stroke(col, 4)), G("Vane", vane, stroke(col, 4))]


def icon_big_bean(col):
    c = path([(0, -18), (0, 18)], False, i=[(0, 0), (-8, -8)], o=[(8, 8), (0, 0)])
    return [G("Crease", c, stroke(col, 4)), G("Bean", ell([40, 54]), stroke(col, 5))]


def icon_leaf(col, L=56):
    return [G("Vein", path([(-L * 0.42, 0), (L * 0.4, 0)]), stroke(WHITE, max(2, L * 0.02), 70)), G("Leaf", leaf_path(L), fill(col))]


# ---------- episode 1 art (v2): drawn shapes instead of circles and lenses ----------
# Episodes 2-10 still use cherry(), cherry_section(), leaf_path() and the stroke icons above.
def _rot(p, deg, o=(0, 0)):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return (o[0] + p[0] * c - p[1] * s, o[1] + p[0] * s + p[1] * c)


def smooth(pts, closed=True, corners=()):
    """Bezier path through pts (Catmull-Rom tangents). Indices in `corners` get sharp vertices."""
    n = len(pts)
    ins, outs = [], []
    for j in range(n):
        if j in corners or (not closed and j in (0, n - 1)):
            ins.append((0, 0))
            outs.append((0, 0))
            continue
        a, b = pts[j - 1], pts[(j + 1) % n]
        tx, ty = (b[0] - a[0]) / 6, (b[1] - a[1]) / 6
        ins.append((-tx, -ty))
        outs.append((tx, ty))
    return path(pts, closed, i=ins, o=outs)


CH_W, CH_H, CH_ROT = 200, 240, -8  # cherry: an ellipsoid a fifth longer than wide, hanging slightly off vertical


def egg_pts(w, h, e=0.06, n=24, rot=0, o=(0, 0)):
    """Closed egg outline, top first, clockwise. e > 0 widens the top (stem end) and narrows the bottom."""
    out = []
    for j in range(n):
        th = 2 * math.pi * j / n
        s, c = math.sin(th), math.cos(th)
        flat = 1 - 0.05 * max(0.0, -c) ** 6  # the navel end is a little flattened
        out.append(_rot((w / 2 * s * (1 + e * c), -h / 2 * c * flat), rot, o))
    return out


def egg(w, h, e=0.06, rot=0, o=(0, 0)):
    return smooth(egg_pts(w, h, e, rot=rot, o=o))


def crescent(pts, j0, j1, width, inset=0.0):
    """Sliver hugging the outline pts from index j0 to j1 (wrapping), widest in the middle."""
    n = len(pts)
    idx = [(j0 + k) % n for k in range(((j1 - j0) % n) + 1)]
    outer, inner = [], []
    for k, j in enumerate(idx):
        x, y = pts[j]
        r = math.hypot(x, y) or 1
        u = k / (len(idx) - 1)
        x, y = x * (1 - inset / r), y * (1 - inset / r)
        w = width * math.sin(math.pi * u) ** 0.8
        outer.append((x, y))
        inner.append((x - x / r * w, y - y / r * w))
    pts2 = outer + inner[::-1][1:-1]
    return smooth(pts2, True, corners=(0, len(outer) - 1))


def leaf_pts(L, wr=0.36, bend=0.035, side=1.0):
    """Coffee leaf along +x, base at -L/2: wedge base, widest just below the middle, a drip tip, wavy edges."""
    prof = [(0.05, 0.22), (0.16, 0.62), (0.3, 0.9), (0.45, 1.0), (0.6, 0.94), (0.73, 0.76), (0.84, 0.5), (0.92, 0.24), (0.97, 0.08)]
    hw = L * wr / 2

    def P(u, v):  # u along the leaf 0..1, v across in half-widths
        return (-L / 2 + u * L, v * hw - bend * L * math.sin(math.pi * u))

    def width(u):  # half-width profile (0..1) at u, linear between the samples
        pr = [(0.0, 0.0)] + prof + [(1.0, 0.0)]
        for (u0, w0), (u1, w1) in zip(pr, pr[1:]):
            if u0 <= u <= u1:
                return w0 + (w1 - w0) * (u - u0) / (u1 - u0)
        return 0.0

    up = [P(u, -w * (1 + 0.035 * (-1) ** j)) for j, (u, w) in enumerate(prof)]
    lo = [P(u, w * side * (1 + 0.035 * (-1) ** (j + 1))) for j, (u, w) in enumerate(prof)]
    return [P(0, 0)] + up + [P(1, 0)] + lo[::-1], P, width


def coffee_leaf(L, col, sh=5, veins=True, petiole=True):
    """Leaf items (top -> bottom): veins, midrib, face, shadow. Base at (-L/2, 0), tip at (L/2, 0)."""
    pts, P, width = leaf_pts(L)
    face = smooth(pts, True, corners=(0, 10))
    w = max(0.6, L * 0.007)
    items = []
    if veins:
        vs = []
        for j, u in enumerate((0.16, 0.27, 0.38, 0.49, 0.6, 0.71, 0.81)):
            for sgn in (-1, 1):  # side veins run forward and curve towards the tip
                vs.append(smooth([P(u, 0), P(u + 0.06, sgn * 0.45 * width(u + 0.06)), P(u + 0.13, sgn * 0.78 * width(u + 0.13))], False))
        items.append(G("Veins", *vs, stroke(WHITE, w, 38)))
        items.append(G("Midrib", smooth([P(u, 0) for u in (0.0, 0.25, 0.5, 0.75, 0.93)], False), stroke(WHITE, w * 1.6, 60)))
    if petiole:
        items.append(G("Petiole", path([P(-0.07, 0), P(0.02, 0)]), stroke(STEM, max(1.5, L * 0.03))))
    items.append(G("Leaf", face, fill(col)))
    if sh:
        items.append(G("Leaf Shadow", face, fill("#000000", 9), tr={"position": [0, sh]}))
    return items


def leaf_outline(L):
    pts, _, _ = leaf_pts(L)
    return smooth(pts, True, corners=(0, 10))


def _leaf_at(L, base, deg, side=1.0):
    """Small filled leaf path for icons, base at `base`, pointing at `deg` (0 = right, clockwise)."""
    pts, _, _ = leaf_pts(L, wr=0.42, bend=0.0, side=side)
    return smooth([_rot((x + L / 2, y), deg, base) for x, y in pts], True, corners=(0, 10))


def icon_shrub(col, tall=True, cherries=False):
    """Coffee shrub: one stem with opposite leaf pairs spreading almost flat, cherries in the leaf axils. Fits ~64 px."""
    if tall:
        top, nodes = -34, [(20, 22, 4), (6, 20, -2), (-8, 17, -8), (-21, 12, -16)]
    else:
        top, nodes = -14, [(20, 24, 6), (7, 23, 0), (-5, 18, -8)]
    leaves = []
    for y, L, a in nodes:
        leaves += [_leaf_at(L, (2, y), a), _leaf_at(L, (-2, y), 180 - a)]
    leaves.append(_leaf_at(11, (0, top + 6), -90))
    out = [G("Stem", path([(0, 30), (0, top + 4)]), stroke(col, 4)), G("Leaves", *leaves, fill(col))]
    if cherries:
        bs = [egg(7, 9, o=(x, y + 6)) for y, _, _ in nodes[:-1] for x in (-5, 5)]
        out.insert(0, G("Cherries", *bs, stroke(WHITE, 1.5), fill(ARA_DARK)))
    return out


def icon_feather2(col):
    vane = smooth([(0, -32), (12, -16), (13, 6), (5, 24), (0, 30), (-7, 20), (-11, 0), (-8, -18)], True, corners=(0, 4))
    barbs = [path([(0, y), (sx * 10, y - 7)]) for y, sx in ((-14, 1), (-2, 1), (10, 1), (-8, -1), (4, -1), (16, -1))]
    return [G("Barbs", *barbs, stroke(WHITE, 2)), G("Spine", path([(-2, 38), (0, -30)]), stroke(col, 4)), G("Vane", vane, fill(col))]


def bean_items2(name, w, h, col, crease, s_curve):
    """Green-coffee bean, flat side up: an egg outline with the centre cut (S-shaped for arabica)."""
    if s_curve:
        c = smooth([(0, -h * 0.4), (w * 0.08, -h * 0.15), (-w * 0.08, h * 0.15), (0, h * 0.4)], False)
    else:
        c = path([(0, -h * 0.4), (0, h * 0.4)])
    body = egg(w, h, e=0.1)
    return [G(name + " Crease", c, stroke(crease, max(3, w * 0.07))),
            G(name, body, fill(col)), G(name + " Shadow", body, fill("#000000", 9), tr={"position": [0, 6]})]


def icon_big_bean2(col):
    c = smooth([(0, -18), (4, -6), (-4, 6), (0, 18)], False)
    return [G("Crease", c, stroke(col, 4)), G("Bean", egg(40, 54, e=0.1), stroke(col, 5))]


def icon_fruit2():
    """Three cherries on short stalks (excelsa card)."""
    bs = [egg(19, 23, rot=r, o=o) for o, r in (((-11, 8), 18), ((11, 8), -18), ((0, -6), 0))]
    return [G("Fruit", *bs, fill(WHITE)), G("Stalks", path([(-8, -2), (0, -22)]), path([(8, -2), (0, -22)]), path([(0, -18), (0, -26)]), stroke(WHITE, 3))]


# cherry-on-a-branch geometry, in rig space (cherry centre at the origin)
CH_PTS = egg_pts(CH_W, CH_H)
NODE = (-26, -184)
SIB = {"pos": (-114, -84), "rot": 18, "w": 144, "h": 172}
TWIG = [(-260, -158), (-140, -176), NODE, (90, -196), (196, -204)]
# the end-of-scene disc: the egg squashes to a circle of CHERRY_D, rotated upright
MORPH_SCALE = [100 * (CHERRY_D - 6) / CH_W, 100 * (CHERRY_D - 6) / CH_H]


def coffee_cherry(prefix, t0, t1, rig, grow_t=None, morph_in=None, morph_out=None, branch_t=0.0, detail_t=0.0, flutter=True):
    """Coffee cherry hanging from a twig, with a smaller cherry behind it and a pair of opposite leaves.

    grow_t: body grows from nothing; morph_in / morph_out: (t0, t1) the plain disc of CHERRY_D turns into the
    cherry, or back. Returns layers top -> bottom: front leaf, body, twig and stalks, back cherry, back leaf.
    """
    pos = [CX, CY]
    top = _rot((0, -CH_H / 2 + 4), CH_ROT)

    def at(p):
        return [CX + p[0], CY + p[1]]

    # body: details sit inside the rotated egg group, so the morph squashes and turns them together
    det_op = A(K(detail_t, 0), K(detail_t + 0.5, 100))
    shade = G("Shade", crescent(CH_PTS, 2, 13, 30), fill(ARA_DARK, 30), tr={"opacity": det_op})
    hi = G("Highlight", crescent(CH_PTS, 18, 22, 13, inset=16), fill(WHITE, 45), tr={"opacity": det_op})
    navel = G("Navel", ell([10, 7], [0, CH_H / 2 - 15]), fill(ARA_DARK), ell([34, 15], [0, CH_H / 2 - 15]), stroke(ARA_DARK, 4),
              tr={"opacity": det_op})
    grp_rot, grp_sc, disc_sc, sh_pos = CH_ROT, [100, 100], None, [0, 7]
    if morph_out:
        a, b = morph_out
        for g in (shade, hi, navel):
            g["transform"]["opacity"] = A(K(detail_t, 0), K(detail_t + 0.5, 100), K(a - 0.3, 100), K(a + 0.2, 0))
        grp_rot = A(K(a, CH_ROT), K(b, 0))
        grp_sc = A(K(a, [100, 100]), K(b, MORPH_SCALE))
        disc_sc = A(K(a, [80, 80]), K(b, [100, 100]))
        sh_pos = A(K(a, [0, 7]), K(b, [0, 0]))
    if morph_in:
        a, b = morph_in
        grp_rot = A(K(a, 0), K(b, CH_ROT))
        grp_sc = A(K(a, MORPH_SCALE), K(b, [100, 100]))
        disc_sc = A(K(a, [100, 100]), K(b, [80, 80]))
        sh_pos = A(K(a, [0, 0]), K(b, [0, 7]))
    skin = smooth(CH_PTS)
    items = [G("Cherry", navel, hi, shade, G("Skin", skin, fill(ARA)), tr={"rotation": grp_rot, "scale": grp_sc})]
    if disc_sc:
        items.append(G("Disc", ell([CHERRY_D, CHERRY_D]), fill(ARA), tr={"scale": disc_sc}))
    items.append(G("Skin Shadow", skin, fill("#000000", 9), tr={"position": sh_pos, "rotation": grp_rot, "scale": grp_sc}))
    sc = A(K(grow_t, [0, 0]), K(grow_t + 0.5, [100, 100])) if grow_t is not None else None
    body = shape(f"{prefix} Body", items, pos, t0, t1, parent=rig, scale=sc)

    # twig, the hero's stalk and the back cherry's stalk; the twig draws out from the node both ways
    bt = branch_t
    twig = shape(f"{prefix} Twig", [
        G("Stalk", smooth([top, (top[0] - 4, (top[1] + NODE[1]) / 2), NODE], False), trim(0, A(K(bt + 0.25, 0), K(bt + 0.75, 100))), stroke(STEM, 10)),
        G("Back Stalk", smooth([_rot((0, -SIB["h"] / 2 + 4), SIB["rot"], SIB["pos"]), (-60, -178), NODE], False),
          trim(0, A(K(bt + 0.25, 0), K(bt + 0.75, 100))), stroke(STEM, 8)),
        G("Node", ell([22, 18], NODE), fill(STEM), tr={"anchorPoint": list(NODE), "position": list(NODE), "scale": grow(bt + 0.25, 100, 0.5)}),
        G("Twig", smooth(TWIG, False), trim(A(K(bt, 47), K(bt + 0.5, 0)), A(K(bt, 47), K(bt + 0.5, 100))), stroke(STEM, 12))],
        pos, t0, t1, parent=rig)

    sib_pts = egg_pts(SIB["w"], SIB["h"])
    sib = shape(f"{prefix} Back Cherry", [
        G("Shade", crescent(sib_pts, 3, 12, 22), fill("#000000", 12)),
        G("Skin", smooth(sib_pts), fill(ARA_DARK))], at(SIB["pos"]), t0, t1, parent=rig, rotation=SIB["rot"],
        scale=A(K(bt + 0.5, [0, 0]), K(bt + 1.0, [100, 100])))

    def leaf(name, L, deg, t, phase):
        rot = {"keyframes": [K(t, deg - 50), K(t + 0.5, deg)]}
        if flutter:  # a slow sway from the base, as if in a draught
            rot["expression"] = f"value + 1.4 * Math.sin((time + {phase}) * 2 * Math.PI / 3.5)"
        return shape(name, coffee_leaf(L, MX, sh=5), at(NODE), t0, t1, parent=rig, anchorPoint=[-L / 2 - L * 0.07, 0],
                     rotation=rot, scale=A(K(t, [0, 0]), K(t + 0.5, [100, 100])))

    front = leaf(f"{prefix} Leaf", 220, -34, bt + 0.5, 0.0)
    back = leaf(f"{prefix} Back Leaf", 170, 206, bt + 0.75, 1.3)
    return [front, body, twig, sib, back]


def coffee_section(prefix, t_open, t_close, t1, rig, thread_t=None):
    """Lengthwise cut through the cherry, opened by an iris: skin rim, pulp, mucilage, parchment, two seeds flat sides together."""
    def seed(name, s):
        sd = smooth([(s * 5, -74), (s * 36, -66), (s * 60, -30), (s * 64, 8), (s * 52, 48), (s * 28, 72), (s * 5, 76)], True, corners=(0, 6))
        pa = smooth([(s * 2, -84), (s * 40, -76), (s * 70, -34), (s * 74, 10), (s * 60, 56), (s * 30, 82), (s * 2, 86)], True, corners=(0, 6))
        groove = smooth([(s * 9, -54), (s * 17, -20), (s * 18, 16), (s * 10, 52)], False)  # the furrow, just inside the flat face
        return [G(name + " Groove", groove, stroke(SEED_LINE, 3, 80)),
                G(name, sd, stroke(SEED_LINE, 3), fill(SEED)),
                G(name + " Parchment", pa, stroke("#E6D3AE", 2), fill("#FFF8EA"))]
    items = []
    if thread_t is not None:
        thr = smooth([(28, -50), (44, -18), (30, 14), (46, 48)], False)
        items.append(G("Robusta Thread", thr, trim(0, A(K(thread_t, 0), K(thread_t + 1.0, 100))), stroke(ROB, 5)))
    items += seed("Seed R", 1) + seed("Seed L", -1)
    items.append(G("Mucilage", egg(176, 206, e=0.04), fill("#FBE3D8")))
    items.append(G("Pulp", smooth([(x * 0.9, y * 0.91) for x, y in CH_PTS]), fill(PULP)))
    sc = A(K(t_open, [0, 0]), K(t_open + 0.5, [100, 100]))
    if t_close is not None:
        sc["keyframes"] += [K(t_close, [100, 100]), K(t_close + 0.5, [0, 0])]
    return shape(f"{prefix} Section", items, [CX, CY], t_open, t1, parent=rig, rotation=CH_ROT, scale=sc)


# =====================================================================
# SCENE 1 - THE SEED (10 s)
# =====================================================================
def s1_seed(D):
    L = []
    rig = "Cherry Rig"
    # labels
    L += [caps("Label Cherry", "COFFEE CHERRY", [1260, 372], 1.6, 6.4, color=INK, just="left", opacity=fade_io(1.6, 6.4)),
          lead("Leader Cherry", (1040, 500), (1240, 380), 1.4, 6.4)]
    L += [caps("Label Seeds", "2 SEEDS", [660, 652], 3.9, 6.4, color=INK, just="right", opacity=fade_io(3.9, 6.4)),
          caps("Label Seeds Sub", "THE COFFEE BEANS", [660, 682], 4.1, 6.4, size=16, just="right", opacity=fade_io(4.1, 6.4)),
          lead("Leader Seeds", (918, 566), (680, 640), 3.7, 6.4)]
    L.append(coffee_section("S1", 3.0, 6.6, D, rig))
    # exit: the leaves and the back cherry drop, the twig pulls back into the stalk, the stalk into the cherry,
    # and the cherry squashes upright into the plain red disc that scene 2 zooms out of
    parts = coffee_cherry("S1", 0, D, rig, grow_t=0.25, morph_out=(7.9, 8.4), branch_t=0.0, detail_t=0.75)
    leaf, body, twig, sib, back = parts
    for l, t, dx, rot in ((leaf, 7.0, 140, 70), (back, 7.15, -120, -60), (sib, 7.3, -30, 25)):
        p0 = l["transform"]["position"]
        l["transform"]["position"] = A(K(t, p0, EXIT), K(t + 1.0, [p0[0] + dx, p0[1] + 900], EXIT))
        r = l["transform"].get("rotation")
        r0 = r if isinstance(r, (int, float)) else r["keyframes"][-1]["value"]
        fall = [K(t, r0, EXIT), K(t + 1.0, r0 + rot, EXIT)]
        if isinstance(r, dict):
            r["keyframes"] += fall
        else:
            l["transform"]["rotation"] = A(*fall)
        l["out"] = t + 1.0
    tw_ = twig["shapes"]
    tw_[3]["items"][1].update(start=A(K(0, 47), K(0.5, 0), K(7.3, 0), K(7.8, 47)), end=A(K(0, 47), K(0.5, 100), K(7.3, 100), K(7.8, 47)))
    tw_[2]["transform"]["scale"] = A(K(0.25, [0, 0]), K(0.75, [100, 100]), K(7.4, [100, 100]), K(7.9, [0, 0]))
    tw_[1]["items"][1]["end"] = A(K(0.25, 0), K(0.75, 100), K(7.3, 100), K(7.8, 0))
    tw_[0]["items"][1]["end"] = A(K(0.25, 0), K(0.75, 100), K(7.4, 100), K(7.9, 0))  # the stalk retracts into the cherry
    twig["out"] = 7.9
    body["transform"]["scale"] = A(K(0.25, [0, 0]), K(0.75, [100, 100]), K(8.4, [100, 100]), KL(D, [100 / HS, 100 / HS]))
    L += parts
    L.append(null(rig, [CX, CY], 0, D))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 2 - THE GENUS (13 s)
# =====================================================================
K2, C2, O2 = 10.5, (54, 3), (CX, 560)
ETH, CON = (36.0, 7.5), (18.0, 1.0)
S2_DOT, S2_GROW = 16, 190


def s2_genus(D):
    L = []
    rig = "Map Rig"
    eth_scr = screen(ETH, K2, C2, O2)
    zs = (0.25, 2.4)
    # text block over the South Atlantic
    L += wipe_text("Genus Name", "Coffea", [150, 690], 70, INK, 2.8, D, font=SCI, just="left", hl=True)
    L.append(appear(text("Species Count", "120+", [150, 840], 120, INK, 3.4, D, font=HEAD, just="left"), 3.4))
    L.append(appear(caps("Species Label", "WILD SPECIES", [154, 886], 3.6, D, size=22, just="left"), 3.6))
    # region labels
    for j, (s, ll) in enumerate([("AFRICA", (20, 12)), ("MADAGASCAR", (47, -27)), ("ASIA", (100, 25))]):
        p = screen(ll, K2, C2, O2)
        L.append(caps(f"Region {s}", s, [p[0], p[1]], 4.6 + j * 0.6, D, size=18, opacity=A(K(4.6 + j * 0.6, 0), K(5.0 + j * 0.6, 100), K(8.0, 100), K(8.4, 35))))
    # species labels on the two dots
    a_s, r_s = eth_scr, screen(CON, K2, C2, O2)
    L.append(appear(text("Label Arabica", "C. arabica", [a_s[0] + 30, a_s[1] - 26], 30, ARA, 9.2, D, font=SCI, just="left"), 9.2, dx=-10, dy=0))
    L.append(appear(text("Label Canephora", "C. canephora", [r_s[0] - 30, r_s[1] + 10], 30, ROB, 9.5, D, font=SCI, just="right"), 9.5, dx=10, dy=0))
    for L_ in L[-2:]:
        add_out(L_, D - 0.6)
    # the two highlighted dots (parented, so the zoom carries the cherry down to dot size)
    L.append(disc("Arabica Dot", map_pt(ETH, K2), S2_DOT, ARA, 0, D, parent=rig, sh=0,
                  scale=A(K(8.6, [100, 100]), K(9.2, [S2_GROW, S2_GROW]))))
    L.append(disc("Robusta Dot", map_pt(CON, K2), S2_DOT, ROB, 8.6, D, parent=rig, sh=0, scale=grow(8.6, S2_GROW, 0.6)))
    # 120+ species dots on land in the tropics (Africa, Madagascar, Asia)
    rnd = random.Random(7)
    regions = [((-13, 4, 12, 11), 18), ((9, -6, 30, 6), 20), ((28, -11, 41, 11), 22), ((43.5, -25, 50, -12), 34),
               ((73, 7, 80, 16), 8), ((96, -6, 122, 16), 14), ((55, -21.5, 58, -19.8), 4)]
    gs, n = [], 0
    for (x0, y0, x1, y1), cnt in regions:
        k = 0
        while k < cnt:
            lon, lat = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
            if cnt > 4 and not in_land(lon, lat):
                continue
            t = 2.6 + rnd.uniform(0, 3.4)
            gs.append(G(f"Sp{n + 1}", ell([9, 9]), fill(INK), tr={"position": map_pt((lon, lat), K2), "scale": grow(t, 100, 0.3)}))
            k += 1
            n += 1
    L.append(shape("Species Dots", gs, [0, 0], 2.6, D, parent=rig, opacity=A(K(8.2, 55), K(8.7, 14))))
    L.append(land_layer("Land", K2, 0, D, bbox=(-30, -40, 150, 50), parent=rig, opacity=fade_in(0.4, 1.4)))
    L.append(null(rig, [CX, CY], 0, D, anchor=map_pt(ETH, K2),
                  scale=zoom_scale(zs[0], zs[1], CHERRY_D / S2_DOT, 1.0), position=zoom_pos(zs[0], zs[1], (CX, CY), eth_scr)))
    L.append(bg(D))
    return L


S2_HANDOFF = {"ara": fwd(screen(ETH, K2, C2, O2)), "rob": fwd(screen(CON, K2, C2, O2)), "d": S2_DOT * S2_GROW / 100 * HS}

# =====================================================================
# SCENE 3 - ARABICA vs ROBUSTA (25 s)
# =====================================================================
BAR_Y, BAR_H = 600, 72
SEG = {"ara": (240, 1100), "rob": (1106, 1652), "oth": (1658, 1686)}


def s3_species(D):
    L = []
    HD = 130
    hx = {"rob": 560, "ara": 1360}
    hy = 170
    t_out = 17.2
    rows_t = [2.2, 4.6, 6.8, 9.6, 12.0]
    ry = [420, 525, 630, 735, 840]
    names = ["ALTITUDE", "CAFFEINE", "FLAVOR", "BEAN", "CHROMOSOMES"]
    tmp = []
    # header names
    for key, nm, sci, col in (("rob", "Robusta", "Coffea canephora", ROB), ("ara", "Arabica", "Coffea arabica", ARA)):
        x = hx[key]
        t = 1.0 if key == "rob" else 1.3
        tmp.append(appear(text(f"Name {nm}", nm, [x, 300], 52, col, t, D, font=HEAD), t))
        tmp.append(appear(text(f"Sci {nm}", sci, [x, 340], 28, GREY, t + 0.15, D, font=SCI), t + 0.15))
    # row pills on the divider
    for j, (y, nm, t) in enumerate(zip(ry, names, rows_t)):
        tmp.append(caps(f"Row {j + 1} Label", nm, [CX, y + 7], t, D, size=18, opacity=fade_in(t)))
        tmp.append(shape(f"Row {j + 1} Pill", [G("Pill", rect([tw(nm, 18, LAB, 140) + 34, 34], None, 17), fill(WHITE))], [CX, y], t, D, opacity=fade_in(t)))
    # 1 altitude
    y, t = ry[0], rows_t[0]
    for key, x, frac, val, col, just, tx in (("rob", 790, 0.18, "0–800 m", ROB, "right", 710), ("ara", 1130, 0.78, "900–2,000 m", ARA, "left", 1210)):
        mx = x - 55 + 55 * frac
        my = y + 35 - 70 * frac
        tt = t + (0.15 if key == "rob" else 0.4)
        tmp.append(shape(f"Altitude {key}", [G("Marker", ell([16, 16], [mx - x, my - y]), fill(col)),
                                              *paper("Mountain", path([(-55, 35), (0, -35), (55, 35)], True), "#D9D9D9", sh=4)],
                         [x, y], tt, D, scale=grow(tt)))
        tmp.append(appear(text(f"Altitude {key} Value", val, [tx, y + 12], 34, INK, tt + 0.15, D, font=HEAD, just=just), tt + 0.15, dy=0, dx=-20 if just == "left" else 20))
    # 2 caffeine bars from the divider outwards
    y, t = ry[1], rows_t[1]
    for key, x, ln, val, col, sgn in (("rob", 860, 245, "2.2–2.7 %", ROB, -1), ("ara", 1060, 135, "1.2–1.5 %", ARA, 1)):
        tt = t + (0.15 if key == "rob" else 0.4)
        tmp.append(shape(f"Caffeine {key}", [G("Bar", rect([ln, 24], [sgn * ln / 2, 0], 4), fill(col))], [x, y], tt, D,
                         scale=A(K(tt, [0, 100]), K(tt + 0.6, [100, 100]))))
        tmp.append(appear(text(f"Caffeine {key} Value", val, [x + sgn * (ln + 22), y + 12], 34, INK, tt + 0.4, D, font=HEAD,
                               just="left" if sgn > 0 else "right"), tt + 0.4, dy=0, dx=-20 * sgn))
    # 3 flavour chips
    y, t = ry[2], rows_t[2]
    for key, words, col, sgn in (("rob", ["BITTER", "EARTHY"], ROB, -1), ("ara", ["SWEET", "BRIGHT", "AROMATIC"], ARA, 1)):
        x = 860 if sgn < 0 else 1060
        for j, wd in enumerate(words):
            wpx = tw(wd, 18, LAB, 140) + 40
            cx = x + sgn * wpx / 2
            tt = t + (0.15 if key == "rob" else 0.4) + j * 0.12
            tmp.append(caps(f"Chip {key} {j + 1}", wd, [cx, y + 7], tt, D, size=18, color=col, opacity=fade_in(tt)))
            tmp.append(shape(f"Chip {key} {j + 1} Pill", [G("Pill", rect([wpx, 44], None, 22), stroke(col, 3))], [cx, y], tt, D, scale=grow(tt, 100, 0.35)))
            x += sgn * (wpx + 16)
    # 4 bean shape
    y, t = ry[3], rows_t[3]
    tmp.append(shape("Bean rob", bean_items2("Bean", 70, 64, ROB, "#3E2A20", False), [800, y], t + 0.15, D, scale=grow(t + 0.15), rotation=-12))
    tmp.append(shape("Bean ara", bean_items2("Bean", 56, 82, ARA, ARA_DARK, True), [1120, y], t + 0.4, D, scale=grow(t + 0.4), rotation=12))
    tmp.append(appear(text("Bean rob Note", "round, straight crease", [740, y + 8], 24, GREY, t + 0.3, D, just="right"), t + 0.3, dy=0, dx=20))
    tmp.append(appear(text("Bean ara Note", "oval, S-shaped crease", [1180, y + 8], 24, GREY, t + 0.55, D, just="left"), t + 0.55, dy=0, dx=-20))
    # 5 chromosomes
    y, t = ry[4], rows_t[4]
    tmp.append(ticks("Chromo rob", 22, 22, ROB, [856, y - 8], t + 0.15, D, right=True, opacity=fade_in(t + 0.15),
                     scale=A(K(t + 0.15, [0, 100]), K(t + 0.75, [100, 100]))))
    tmp.append(ticks("Chromo ara", 44, 44, ARA, [1064, y - 8], t + 0.4, D, opacity=fade_in(t + 0.4),
                     scale=A(K(t + 0.4, [0, 100]), K(t + 1.0, [100, 100]))))
    tmp.append(appear(text("Chromo rob Value", "22", [642, y + 12], 34, INK, t + 0.6, D, font=HEAD, just="right"), t + 0.6, dy=0, dx=20))
    tmp.append(appear(text("Chromo ara Value", "44", [1478, y + 12], 34, INK, t + 0.9, D, font=HEAD, just="left"), t + 0.9, dy=0, dx=-20))
    # column focus tints and divider
    tmp.append(shape("Divider", [G("Line", path([(CX, 120), (CX, 900)]), trim(0, A(K(0.8, 0), K(1.8, 100))), stroke(LINE, 3))], [0, 0], 0.8, D))
    tmp.append(shape("Tint ara", [G("Tint", rect([760, 860], None, 24), fill(ARA, 5))], [1360, 520], 9.8, D, opacity=fade_in(9.8, 0.6)))
    tmp.append(shape("Tint rob", [G("Tint", rect([760, 860], None, 24), fill(ROB, 5))], [560, 520], 1.6, 9.9, opacity=fade_io(1.6, 9.9, 0.5)))
    for j, l in enumerate(tmp):
        if l["out"] > t_out:
            add_out(l, t_out + (j % 6) * 0.05)
    # header discs morph into the production bar (rect with roundness = circle)
    morph = (17.8, 18.9)
    for key, col, nm, t in (("rob", ROB, "Robusta", 0.0), ("ara", ARA, "Arabica", 0.0)):
        x0, x1 = SEG[key]
        start = S2_HANDOFF[key]
        s0 = S2_HANDOFF["d"] / HD * 100
        L.append(shape(f"{nm} Head", [G("Face", rect(A(K(morph[0], [HD, HD]), K(morph[1], [x1 - x0, BAR_H])), None,
                                                     A(K(morph[0], HD / 2), K(morph[1], 0))), fill(col))],
                       A(K(0, start), K(1.1, [hx[key], hy]), K(morph[0], [hx[key], hy]), K(morph[1], [(x0 + x1) / 2, BAR_Y])), 0, D,
                       scale=A(K(0, [s0, s0]), K(1.1, [100, 100]))))
    # others sliver and labels
    ox0, ox1 = SEG["oth"]
    L.append(shape("Others Bar", [G("Face", rect([ox1 - ox0, BAR_H], [(ox1 - ox0) / 2, 0]), fill(SMALL))], [ox0, BAR_Y], 19.0, D,
                   scale=A(K(19.0, [0, 100]), K(19.4, [100, 100]))))
    L += wipe_text("Prod Title", "World coffee production", [240, 400], 44, INK, 18.6, D, just="left")
    L.append(appear(caps("Prod ara Small", "ARABICA", [240, 470], 19.3, D, color=ARA, just="left"), 19.3))
    L.append(appear(text("Prod ara Big", "≈ 60 %", [240, 540], 56, INK, 19.4, D, font=HEAD, just="left"), 19.4))
    L.append(appear(caps("Prod rob Small", "ROBUSTA", [1106, 470], 21.2, D, color=ROB, just="left"), 21.2))
    L.append(appear(text("Prod rob Big", "≈ 38 %", [1106, 540], 56, INK, 21.3, D, font=HEAD, just="left"), 21.3))
    L.append(leader("Others Leader", (1672, BAR_Y + 48), (1672, 700), 22.6, D, col=SMALL, dot=False))
    L.append(appear(caps("Prod oth Small", "OTHER SPECIES", [1686, 740], 22.8, D, color=SMALL, just="right"), 22.8))
    L.append(appear(text("Prod oth Big", "< 2 %", [1686, 800], 44, INK, 22.9, D, font=HEAD, just="right"), 22.9))
    L += tmp
    L.append(bg(D))
    return L


S3_SLIVER = {"pos": fwd(((SEG["oth"][0] + SEG["oth"][1]) / 2, BAR_Y)), "size": [(SEG["oth"][1] - SEG["oth"][0]) * HS, BAR_H * HS]}

# =====================================================================
# SCENE 4 - THE SMALLER SPECIES (22 s)
# =====================================================================
S5_EUG, S5_ROB, S5_D = (660, 330), (1260, 330), 130


def s4_others(D):
    L = []
    RAIL_Y, CARD_Y, CW, CH, DD = 590, 590, 380, 560, 120
    xs = [330, 750, 1170, 1590]
    t_cards = [2.6, 5.4, 8.4, 13.2]
    t_exit = 19.6
    cards = [
        ("Liberica", "Coffea liberica", "WEST AFRICA", "A towering tree with\rbig, smoky beans", "Grows up to 17 m tall", "tree"),
        ("Excelsa", "C. liberica var. dewevrei", "CENTRAL AFRICA · SE ASIA", "Tart and fruity,\rgrown in Southeast Asia", "Reclassified as liberica, 2006", "fruit"),
        ("Stenophylla", "Coffea stenophylla", "SIERRA LEONE", "Tastes like arabica,\rhandles the heat", "Rediscovered in 2018", "therm"),
        ("Eugenioides", "Coffea eugenioides", "EAST AFRICAN HIGHLANDS", "Mild, low in caffeine.", "", "tree2"),
    ]

    def icon(kind):
        if kind == "tree":
            return [G("Canopy", ell([54, 46], [0, -10]), fill(WHITE)), G("Trunk", path([(0, 30), (0, 6)]), stroke(WHITE, 8, cap="butt"))]
        if kind == "fruit":
            return icon_fruit2()
        if kind == "therm":
            return [G("Bulb", ell([22, 22], [0, 20]), fill(WHITE)), G("Tube", rect([12, 46], [0, -8], 6), stroke(WHITE, 4)),
                    G("Mercury", rect([5, 26], [0, 2]), fill(WHITE))]
        return [G("Nodes", ell([16, 16], [-16, -16]), ell([16, 16], [16, -16]), ell([20, 20], [0, 22]), fill(WHITE)),
                G("Links", path([(-16, -16), (-16, 2), (16, 2), (16, -16)]), path([(0, 2), (0, 22)]), stroke(WHITE, 4))]

    # sliver -> rail
    rail = shape("Rail", [G("Face", rect(A(K(0, S3_SLIVER["size"]), K(1.1, [1640, 4]))), fill(SMALL))],
                 A(K(0, S3_SLIVER["pos"]), K(1.1, [CX, RAIL_Y])), 0, D, opacity=A(K(t_exit, 100), K(t_exit + 0.4, 0)))
    rail["out"] = t_exit + 0.4
    eug_disc = None
    for j, ((nm, sci, origin, trait, note, kind), x, t) in enumerate(zip(cards, xs, t_cards)):
        rig = f"Card {j + 1} Rig"
        cl = []
        drop = 1.0 + j * 0.12
        dot_scale = A(K(drop, [0, 0]), K(drop + 0.35, [20, 20]), K(t, [20, 20]), K(t + 0.5, [100, 100]))
        dot_pos = A(K(t, [x, RAIL_Y]), K(t + 0.5, [x, CARD_Y - CH / 2]))
        ic = [G("Icon", *icon(kind), tr={"opacity": A(K(t + 0.35, 0), K(t + 0.6, 100))})]
        d = disc(f"Card {j + 1} Disc", dot_pos, DD, SMALL, drop, D, icon=ic, scale=dot_scale, parent=rig, sh=4)
        tc = t + 0.35
        cl.append(appear(text(f"Card {j + 1} Name", nm, [x, 450], 42, INK, tc, D, font=HEAD, parent=rig), tc))
        cl.append(appear(text(f"Card {j + 1} Sci", sci, [x, 492], 24, GREY, tc + 0.1, D, font=SCI, parent=rig), tc + 0.1))
        cl.append(appear(caps(f"Card {j + 1} Origin", origin, [x, 540], tc + 0.2, D, size=15, color=SMALL, parent=rig), tc + 0.2))
        cl.append(shape(f"Card {j + 1} Rule", [G("Rule", path([(-120, 0), (120, 0)]), stroke(LINE, 2))], [x, 572], tc + 0.2, D, parent=rig,
                        scale=A(K(tc + 0.2, [0, 100]), K(tc + 0.6, [100, 100]))))
        cl.append(appear(text(f"Card {j + 1} Trait", trait, [x, 624], 25, INK, tc + 0.35, D, leading=34, parent=rig), tc + 0.35))
        if note:
            cl.append(appear(text(f"Card {j + 1} Note", note, [x, 740], 20, GREY, tc + 0.6, D, font=SCI, parent=rig), tc + 0.6))
        else:  # eugenioides: the reveal
            cl += wipe_text(f"Card {j + 1} Mother", "Arabica's mother", [x, 700], 34, INK, 16.2, D, hl=True, parent=rig)
        card = shape(f"Card {j + 1}", paper("Card", rect([CW, CH], None, 18), WHITE, line="#EAEAEA", lw=2, sh=8, sh_op=7),
                     [x, CARD_Y], t, D, parent=rig, scale=A(K(t, [0, 0]), K(t + 0.5, [100, 100])))
        if j < 3:
            L += [d] + cl + [card]
            L.append(null(rig, [x, CARD_Y], 0, D, position=A(K(t_exit + j * 0.1, [x, CARD_Y]), K(t_exit + 0.7 + j * 0.1, [x - 1700, CARD_Y]))))
        else:
            for c in cl:
                add_out(c, t_exit, 0.25)
            card["transform"]["scale"]["keyframes"] += [K(t_exit + 0.1, [100, 100]), K(t_exit + 0.6, [0, 0])]
            card["out"] = t_exit + 0.6
            end_s = S5_D / HS / DD * 100
            d["transform"]["position"]["keyframes"] += [K(t_exit + 0.3, [x, CARD_Y - CH / 2]), K(t_exit + 1.3, inv(S5_EUG))]
            d["transform"]["scale"]["keyframes"] += [K(t_exit + 0.3, [100, 100]), K(t_exit + 1.3, [end_s, end_s])]
            d["shapes"][0]["transform"]["opacity"]["keyframes"] += [K(t_exit + 0.2, 100), K(t_exit + 0.6, 0)]
            L += [d] + cl + [card]
            L.append(null(rig, [x, CARD_Y], 0, D))
    L.append(wipe_text("Others Title", "The smaller species", [CX, 150], 50, INK, 1.3, D)[1])
    L[-1].pop("trackMatte")
    L[-1]["transform"]["opacity"] = A(K(1.3, 0), K(1.7, 100), K(t_cards[0], 100), K(t_cards[0] + 0.4, 0))
    L[-1]["out"] = t_cards[0] + 0.4
    L.append(rail)
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 5 - WHERE ARABICA COMES FROM (17 s)
# =====================================================================
K5, C5, O5 = 36, (41, 11), (CX, CY)
MOCHA = (43.25, 13.32)
S5_DOT = 26


def s5_origin(D):
    L = []
    AR, AD = (CX, 640), 160
    t_map = 10.0
    tmp = []
    # parents
    tmp.append(appear(text("Eug Sci", "Coffea eugenioides", [560, 322], 34, INK, 0.3, D, font=SCI, just="right"), 0.3, dx=20, dy=0))
    tmp.append(appear(caps("Eug Tag", "MOTHER", [560, 280], 0.5, D, size=16, color=SMALL, just="right"), 0.5, dx=20, dy=0))
    tmp.append(appear(text("Rob Sci", "Coffea canephora", [1360, 322], 34, INK, 1.1, D, font=SCI, just="left"), 1.1, dx=-20, dy=0))
    tmp.append(appear(caps("Rob Tag", "FATHER · ROBUSTA", [1360, 280], 1.3, D, size=16, color=ROB, just="left"), 1.3, dx=-20, dy=0))
    tmp.append(appear(caps("Eug Count", "22 CHROMOSOMES", [560, 450], 1.6, D, size=15, just="right"), 1.6))
    tmp.append(appear(caps("Rob Count", "22 CHROMOSOMES", [1360, 450], 1.8, D, size=15, just="left"), 1.8))
    tmp.append(disc("Rob Disc", A(K(0.3, [2150, S5_ROB[1]]), K(1.1, list(S5_ROB))), S5_D, ROB, 0, D))
    tmp.append(disc("Eug Disc", list(S5_EUG), S5_D, SMALL, 0, D))
    # connectors
    for key, x, col in (("Eug", S5_EUG[0], SMALL), ("Rob", S5_ROB[0], ROB)):
        tmp.append(shape(f"{key} Link", [G("Link", path([(x, S5_EUG[1] + S5_D / 2 + 8), (x, 520), (CX, 520)]),
                                           trim(0, A(K(1.8, 0), K(2.8, 100))), stroke(col, 5))], [0, 0], 1.8, D))
    tmp.append(shape("Child Link", [G("Link", path([(CX, 520), (CX, AR[1] - AD / 2 - 8)]), trim(0, A(K(2.7, 0), K(3.0, 100))), stroke(INK, 5))], [0, 0], 2.7, D))
    # chromosome ticks merge into arabica (eugenioides rows 1-2, canephora rows 3-4)
    blk = (1080, 590)
    tmp.append(ticks("Eug Ticks", 22, 11, SMALL, [461, 366], 1.5, D, opacity=fade_in(1.5),
                     position=A(K(6.8, [461, 366]), K(7.8, list(blk)))))
    tmp.append(ticks("Rob Ticks", 22, 11, ROB, [1360, 366], 1.7, D, opacity=fade_in(1.7),
                     position=A(K(7.0, [1360, 366]), K(8.0, [blk[0], blk[1] + 48]))))
    tmp.append(appear(caps("Ara Count", "44 CHROMOSOMES", [blk[0], 690], 8.0, D, size=15, just="left"), 8.0))
    tmp.append(appear(caps("Genomes", "TWO GENOMES, ONE SPECIES", [CX, 860], 8.2, D, size=18, color=INK), 8.2))
    tmp += wipe_text("Ara Sci", "Coffea arabica", [CX, 800], 46, ARA, 3.4, D, font=SCI)
    # self-pollination loop
    loop = [G("Arrow", path([(-12, -6), (0, 6), (12, -6)]), stroke(INK, 4), tr={"position": [0, -AD / 2 - 26], "opacity": fade_in(9.6, 0.2)}),
            G("Loop", ell([AD + 52, AD + 52]), trim(0, A(K(8.8, 0), K(9.8, 92)), 0), stroke(INK, 4))]
    tmp.append(shape("Self Loop", loop, list(AR), 8.8, D, rotation=8))
    tmp.append(appear(caps("Self Label", "SELF-POLLINATING", [AR[0] - 130, AR[1] + 6], 9.2, D, size=16, color=INK, just="right"), 9.2, dx=20, dy=0))
    for j, l in enumerate(tmp):
        add_out(l, t_map + (j % 5) * 0.04, 0.35)
    # arabica: pops, then shrinks onto Ethiopia and travels to Mocha
    eth = screen(ETH, K5, C5, O5)
    moc = screen(MOCHA, K5, C5, O5)
    end_s = S5_DOT / HS / AD * 100
    L.append(disc("Arabica", A(K(t_map + 0.2, list(AR)), K(t_map + 1.4, eth), K(12.4, eth), K(14.2, inv(moc))), AD, ARA, 3.0, D,
                  scale=A(K(3.0, [0, 0]), K(3.45, [100, 100]), K(t_map + 0.2, [100, 100]), K(t_map + 1.4, [S5_DOT / AD * 100] * 2), K(12.4, [S5_DOT / AD * 100] * 2), K(14.2, [end_s, end_s]))))
    L.append(shape("Trail", [G("Trail", path([eth, inv(moc)]), trim(0, A(K(12.4, 0), K(14.2, 100))), stroke(ARA, 4))], [0, 0], 12.4, D))
    # map labels
    for j, (s, ll, t, col) in enumerate([("ETHIOPIA", (35.0, 4.6), 11.3, INK), ("RED SEA", (38.3, 18.2), 12.2, GREY), ("YEMEN", (46.5, 15.8), 12.8, INK)]):
        p = screen(ll, K5, C5, O5)
        L.append(appear(caps(f"Map {s}", s, p, t, D, size=22, color=col), t))
    L.append(appear(caps("Mocha Label", "MOCHA · 1400s", [moc[0] + 40, moc[1] + 46], 14.3, D, size=18, color=ARA, just="left"), 14.3))
    L.append(land_layer("Land", K5, t_map, D, bbox=(15, -10, 70, 35), opacity=fade_in(t_map + 0.3, 1.0),
                        position=[O5[0] - C5[0] * K5, O5[1] + C5[1] * K5]))
    L += tmp
    L.append(bg(D))
    return L


S5_MOCHA = fwd(screen(MOCHA, K5, C5, O5))

# =====================================================================
# SCENE 6 - TYPICA AND BOURBON (19 s)
# =====================================================================
K6, C6, O6 = 7.9, (7.5, 13), (CX, 560)
PLACES = {"india": (75.7, 13.3), "java": (110.4, -7.4), "ams": (4.9, 52.4), "paris": (2.35, 48.85), "mart": (-61.0, 14.6),
          "reunion": (55.5, -21.1), "brazil": (-47.0, -15.0), "eafrica": (37.0, -1.5), "ver": (-96.13, 19.2)}


def s6_routes(D):
    L = []
    rig = "Map Rig"
    P = {k: screen(v, K6, C6, O6) for k, v in PLACES.items()}
    moc = screen(MOCHA, K6, C6, O6)
    zs = (0.2, 2.6)
    TY, BO = ARA, ARA_DARK

    def leg(name, a, b, bend, t0, t1, col):
        return shape(name, [G("Leg", arc(a, b, bend), trim(0, A(K(t0, 0, "easeInOut"), K(t1, 100, "easeInOut"))), stroke(col, 4))], [0, 0], t0, D)

    def stop(name, p, label, t, col, dx=14, dy=-14, just="left"):
        return [caps(f"{name} Label", label, [p[0] + dx, p[1] + dy], t + 0.1, D, size=16, color=INK, just=just, opacity=fade_in(t + 0.1)),
                disc(f"{name} Dot", p, 12, col, t, D, sh=0, scale=grow(t))]

    ty = [("india", moc, P["india"], -0.25, 3.8, 4.7, "INDIA 1670", 14, -14, "left"),
          ("java", P["india"], P["java"], -0.3, 4.8, 5.6, "JAVA 1696", 14, 26, "left"),
          ("ams", P["java"], P["ams"], 0.25, 5.9, 7.0, "AMSTERDAM 1706", 14, -14, "left"),
          ("paris", P["ams"], P["paris"], 0.4, 7.1, 7.5, "PARIS 1714", -16, 22, "right"),
          ("mart", P["paris"], P["mart"], 0.18, 7.7, 8.9, "MARTINIQUE c. 1720", 0, 34, "center")]
    for k, a, b, bend, t0, t1, lab, dx, dy, just in ty:
        L += stop(f"Stop {k}", b, lab, t1, TY, dx, dy, just)
        L.append(leg(f"Typica {k}", a, b, bend, t0, t1, TY))
    bo = [("reunion", moc, P["reunion"], -0.3, 10.0, 11.0, "RÉUNION 1715", 16, 6, "left"),
          ("brazil", P["reunion"], P["brazil"], -0.22, 12.4, 13.7, "BRAZIL 1860", -16, 26, "right"),
          ("eafrica", P["reunion"], P["eafrica"], 0.3, 13.8, 14.5, "EAST AFRICA 1890s", -16, -12, "right")]
    for k, a, b, bend, t0, t1, lab, dx, dy, just in bo:
        L += stop(f"Stop {k}", b, lab, t1, BO, dx, dy, just)
        L.append(leg(f"Bourbon {k}", a, b, bend, t0, t1, BO))
    # last Typica branch: Caribbean -> Veracruz
    L.append(disc("Veracruz Dot", P["ver"], 16, ARA, 17.9, D, sh=0, scale=A(K(17.9, [0, 0]), K(18.3, [100, 100]), KL(D, [100 / HS, 100 / HS]))))
    L.append(leg("Typica ver", P["mart"], P["ver"], 0.2, 16.6, 17.9, TY))
    # line labels
    L.append(appear(caps("Typica Label", "TYPICA", [moc[0] + 70, moc[1] - 36], 3.3, D, size=22, color=TY, just="left"), 3.3))
    L.append(appear(caps("Bourbon Label", "BOURBON", [moc[0] + 46, moc[1] + 64], 9.6, D, size=22, color=BO, just="left"), 9.6))
    L += wipe_text("Routes Title", "Two lines", [90, 130], 56, INK, 2.6, D, just="left")
    L.append(appear(text("Note 1", "Nearly all arabica descends from these two lines:", [90, 960], 26, GREY, 15.0, D, just="left"), 15.0))
    L += wipe_text("Note 2", "very little genetic diversity", [90, 1012], 38, INK, 15.6, D, just="left", hl=True)
    # Mocha dot (screen space; follows the rig's focus point)
    L.append(disc("Mocha Dot", S5_MOCHA, S5_DOT, ARA, 0, D, sh=0, position=zoom_pos(zs[0], zs[1], S5_MOCHA, moc),
                  scale=A(K(zs[0], [100, 100]), K(zs[1], [70, 70]))))
    L.append(land_layer("Land", 36, 0, D, parent=rig))
    L.append(null(rig, S5_MOCHA, 0, D, anchor=map_pt(MOCHA, 36), scale=zoom_scale(zs[0], zs[1], HS, K6 / 36),
                  position=zoom_pos(zs[0], zs[1], S5_MOCHA, moc)))
    L.append(bg(D))
    return L


S6_VER = fwd(screen(PLACES["ver"], K6, C6, O6))

# =====================================================================
# SCENE 7 - MEXICO (13 s)
# =====================================================================
K7, C7, O7 = 40, (-101.5, 23.5), (1010, 560)
COFFEE_STATES = [("Chiapas", 4.6), ("Veracruz", 5.5), ("Puebla", 6.6), ("Oaxaca", 7.5)]
MINOR_STATES = ["Guerrero", "Hidalgo", "San Luis Potosí", "Nayarit"]
S7_ROW = [(840, 540), (920, 540), (1000, 540), (1080, 540)]


def s7_mexico(D):
    L = []
    rig = "Map Rig"
    ver = PLACES["ver"]
    ver_final = screen(ver, K7, C7, O7)
    zs = (0.3, 2.6)
    s0 = K6 * HS / K7
    # state dots lift into a row at the end (handoff to the family tree)
    lift = (11.4, 12.4)
    for j, (st, t) in enumerate(COFFEE_STATES):
        c = screen(state_centroid(st), K7, C7, O7)
        L.append(disc(f"Dot {st}", c, 20, MX, t + 0.3, D, sh=0, scale=A(K(t + 0.3, [0, 0]), K(t + 0.6, [100, 100]), K(lift[1], [100, 100]), KL(D, [100 / HS, 100 / HS])),
                      position=A(K(lift[0] + j * 0.08, c), K(lift[1] + j * 0.08, inv(S7_ROW[j])))))
    # labels
    lab = {"Chiapas": ((1440, 880), "left"), "Veracruz": ((1300, 640), "left"), "Puebla": ((1030, 668), "right"), "Oaxaca": ((1150, 950), "center")}
    for st, t in COFFEE_STATES:
        p, just = lab[st]
        L.append(appear(caps(f"Label {st}", st.upper(), p, t + 0.2, D, size=22, color=MX, just=just), t + 0.2))
    L.append(appear(caps("Veracruz Year", "LATE 1700s", [1300, 668], 2.6, D, size=16, color=GREY, just="left"), 2.6))
    L += wipe_text("Mexico Title", "Mexico", [110, 820], 64, INK, 2.8, D, just="left")
    L.append(appear(text("Stat", "Most of it is arabica,", [110, 880], 30, INK, 9.8, D, just="left"), 9.8))
    L.append(appear(text("Stat 2", "grown in the mountains", [110, 920], 30, INK, 10.1, D, just="left"), 10.1))
    for l in L:
        if l["name"].startswith(("Label", "Veracruz Year", "Mexico Title", "Stat")):
            add_out(l, lift[0] - 0.2, 0.4)
    # Veracruz arrival dot (screen space; follows the rig's focus point)
    L.append(disc("Veracruz Dot", S6_VER, 16, ARA, 0, lift[0], sh=0, position=zoom_pos(zs[0], zs[1], S6_VER, ver_final),
                  opacity=A(K(5.3, 100), K(5.6, 0))))
    # states: coffee states fill green over the grey map
    items_hi, items_lo, items_all = [], [], []
    for st, rings in GEO["mexico"].items():
        ps = [path([map_pt(p, K7) for p in r], True) for r in rings]
        items_all += ps
    for st, t in COFFEE_STATES:
        L.append(shape(f"State {st}", [G(st, *[path([map_pt(p, K7) for p in r], True) for r in GEO["mexico"][st]], fill(MX))], [0, 0], t, D,
                       parent=rig, opacity=A(K(t, 0), K(t + 0.5, 100), K(lift[0], 100), K(lift[0] + 0.5, 35))))
    L.append(shape("Minor States", [G("Minor", *[path([map_pt(p, K7) for p in r], True) for st in MINOR_STATES for r in GEO["mexico"][st]], fill(MX))],
                   [0, 0], 8.3, D, parent=rig, opacity=A(K(8.3, 0), K(8.8, 30), K(lift[0], 30), K(lift[0] + 0.5, 12))))
    L.append(shape("States", [G("Borders", *items_all, stroke(WHITE, 2)), G("Fill", *items_all, fill(LAND))], [0, 0], 0, D, parent=rig))
    L.append(land_layer("Land", K7, 0, D, parent=rig))
    L.append(null(rig, S6_VER, 0, D, anchor=map_pt(ver, K7), scale=zoom_scale(zs[0], zs[1], s0, 1.0), position=zoom_pos(zs[0], zs[1], S6_VER, ver_final)))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 8 - MEXICO'S ARABICA FAMILY TREE (29 s)
# =====================================================================
ROOTS = {"Typica": (440, 170), "Bourbon": (1560, 170)}
MUNDO, CATUAI, GARNICA = (1010, 470), (1140, 800), (1430, 800)
LEAF_ICON, LEAF_SCREEN, LEAF_ROT = 52, 440, -30


def s8_tree(D):
    L = []
    cam = "Cam"
    RD, ND = 130, 100
    LINK = "#9A9A9A"
    z0, z1 = 25.9, 27.8
    zoom = LEAF_SCREEN / (LEAF_ICON * HS)
    keep = {"Node Garnica"}

    def link(name, pts, t, d=0.5):
        return shape(name, [G("Link", path(pts), trim(0, A(K(t, 0), K(t + d, 100))), stroke(LINK, 3))], [0, 0], t, D)

    def node(nm, pos, t, icon, trait, line=ARA, tag=None):
        out = []
        x, y = pos
        out.append(appear(text(f"Name {nm}", nm, [x, y + ND / 2 + 44], 30, INK, t + 0.2, D, font=HEAD), t + 0.2))
        out.append(appear(text(f"Trait {nm}", trait, [x, y + ND / 2 + 76], 20, GREY, t + 0.35, D, leading=25), t + 0.35))
        if tag:
            w = tw(tag, 15, LAB, 140) + 30
            out.append(caps(f"Tag {nm}", tag, [x, y + ND / 2 + 147], t + 0.6, D, size=15, color=WHITE, opacity=fade_in(t + 0.6)))
            out.append(shape(f"Tag {nm} Pill", [G("Pill", rect([w, 32], None, 16), fill(MX))], [x, y + ND / 2 + 141], t + 0.5, D, scale=grow(t + 0.5)))
        ic = [G("Icon", *icon, tr={"opacity": A(K(t + 0.2, 0), K(t + 0.45, 100))})]
        out.append(disc(f"Node {nm}", list(pos), ND, WHITE, t, D, icon=ic, line=line, scale=grow(t)))
        return out

    # roots: two of the four state dots grow into Typica and Bourbon, two merge into them
    targets = [ROOTS["Typica"], ROOTS["Typica"], ROOTS["Bourbon"], ROOTS["Bourbon"]]
    s0 = 20 / RD * 100
    for j, (p0, tgt) in enumerate(zip(S7_ROW, targets)):
        pos = A(K(0.1 + 0.05 * j, list(p0)), K(1.2 + 0.05 * j, list(tgt)))
        if j in (0, 3):  # grows into the root; green turns arabica red
            green = [G("Green", ell([RD, RD]), fill(MX), tr={"opacity": A(K(0.8, 100), K(1.4, 0))})]
            L.append(disc(f"Root {'Typica' if j == 0 else 'Bourbon'}", list(tgt), RD, ARA, 0, D, icon=green, position=pos,
                          scale=A(K(0.1 + 0.05 * j, [s0, s0]), K(1.2 + 0.05 * j, [100, 100]))))
        else:  # merges into the root
            L.append(disc(f"Root Dot {j + 1}", list(tgt), 20, MX, 0, 1.4, sh=0, position=pos, opacity=A(K(1.0, 100), K(1.3, 0))))
    L.insert(0, appear(text("Root Typica Name", "Typica", [ROOTS["Typica"][0] - RD / 2 - 24, 186], 46, INK, 1.4, D, font=HEAD, just="right"), 1.4, dx=20, dy=0))
    L.insert(0, appear(text("Root Bourbon Name", "Bourbon", [ROOTS["Bourbon"][0] + RD / 2 + 24, 186], 46, INK, 1.7, D, font=HEAD, just="left"), 1.7, dx=-20, dy=0))
    L += wipe_text("Tree Title", "Mexico's arabica family tree", [CX, 92], 40, INK, 1.2, D)
    # Typica's children
    tx, ty = ROOTS["Typica"]
    kids = [("Criollo", 170, 2.8, icon_shrub(ARA, True), "Typica on old farms.\rTall, low yield"),
            ("Pluma Hidalgo", 440, 6.5, icon_feather2(ARA), "Typica selection\rfrom Oaxaca"),
            ("Maragogype", 720, 9.5, icon_big_bean2(ARA), "Typica mutation,\rgiant beans")]
    L.append(link("Link Typica Bus", [(tx, ty + RD / 2 + 6), (tx, 350)], 2.4, 0.3))
    for nm, x, t, ic, tr_ in kids:
        L.append(link(f"Link {nm}", [(tx, 350), (x, 350), (x, 470 - ND / 2 - 6)], t - 0.4, 0.45))
        L += node(nm, (x, 470), t, ic, tr_)
    # Bourbon -> Caturra
    bx, by = ROOTS["Bourbon"]
    L.append(link("Link Caturra", [(bx, by + RD / 2 + 6), (bx, 470 - ND / 2 - 6)], 12.3, 0.4))
    L += node("Caturra", (bx, 470), 12.6, icon_shrub(ARA, False), "Bourbon mutation.\rDwarf, dense planting")
    # Typica x Bourbon -> Mundo Novo
    cross = [G("Cross", path([(-9, -9), (9, 9)]), path([(-9, 9), (9, -9)]), stroke(INK, 4)), *paper("Badge", ell([34, 34]), WHITE, line=INK, lw=3, sh=3)]
    L.append(shape("Cross 1", cross, [MUNDO[0], ty], 16.6, D, scale=grow(16.6)))
    L.append(link("Link Cross 1", [(tx + RD / 2 + 6, ty), (bx - RD / 2 - 6, ty)], 16.2, 0.5))
    L.append(link("Link Mundo Novo", [(MUNDO[0], ty + 20), (MUNDO[0], 470 - ND / 2 - 6)], 16.8, 0.4))
    L += node("Mundo Novo", MUNDO, 17.1, icon_shrub(ARA, True, True), "Typica × Bourbon.\rTall, productive")
    # Mundo Novo x Caturra -> Catuai, Garnica
    mx = (MUNDO[0] + bx) / 2
    L.append(link("Link Cross 2", [(MUNDO[0] + ND / 2 + 6, 470), (bx - ND / 2 - 6, 470)], 20.4, 0.5))
    L.append(shape("Cross 2", cross, [mx, 470], 20.7, D, scale=grow(20.7)))
    L.append(link("Link Cross 2 Bus", [(mx, 490), (mx, 680)], 20.9, 0.3))
    L.append(link("Link Catuai", [(mx, 680), (CATUAI[0], 680), (CATUAI[0], 800 - ND / 2 - 6)], 21.2, 0.4))
    L.append(link("Link Garnica", [(mx, 680), (GARNICA[0], 680), (GARNICA[0], 800 - ND / 2 - 6)], 23.2, 0.4))
    L += node("Catuaí", CATUAI, 21.5, icon_shrub(ARA, False, True), "Mundo Novo × Caturra.\rCompact, high yield")
    L += node("Garnica", GARNICA, 23.6, [G("Leaf Icon", *coffee_leaf(LEAF_ICON, MX, sh=1, petiole=False), tr={"rotation": LEAF_ROT})], "Mundo Novo × Caturra", line=MX, tag="BRED IN MEXICO")
    # final push into Garnica's leaf: everything else fades
    for l in L:
        if l["name"] not in keep:
            add_out(l, z0, 0.5)
    g = next(l for l in L if l["name"] == "Node Garnica")
    for grp in g["shapes"][1:]:
        grp.setdefault("transform", {})["opacity"] = A(K(z0, 100), K(z0 + 0.5, 0))
    parent_all(L, cam)
    L.append(null(cam, list(GARNICA), 0, D, scale=zoom_scale(z0, z1, 1.0, zoom), position=zoom_pos(z0, z1, GARNICA, (CX, CY))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 9 - LA ROYA AND THE RESCUE (23 s)
# =====================================================================
ORO = (1330, 480)


def s9_roya(D):
    L = []
    rig = "Leaf Rig"
    t_clear = 10.8
    LF = LEAF_SCREEN
    tmp = []
    # leaf + rust spots (matted to the leaf)
    rnd = random.Random(12)
    spots = []
    for j in range(34):
        while True:
            x, y = rnd.uniform(-0.45, 0.45) * LF, rnd.uniform(-0.17, 0.17) * LF
            if (x / (0.46 * LF)) ** 2 + (y / (0.17 * LF)) ** 2 < 1:
                break
        s = rnd.uniform(12, 46)
        t = 1.0 + (abs(x) / LF) * 4 + rnd.uniform(0, 1.6)
        spots.append(G(f"Spot {j + 1}", ell([s * 0.4, s * 0.4]), fill("#A9561A"), ell([s, s]), fill(RUST),
                       tr={"position": [x, y], "scale": grow(t, 100, 0.8)}))
    tmp.append(shape("Rust", spots, [CX, CY], 1.0, D, parent=rig, rotation=LEAF_ROT, trackMatte={"target": "Leaf Matte", "type": "Alpha"}))
    tmp.append(shape("Leaf Matte", [G("M", leaf_outline(LF), fill(WHITE))], [CX, CY], 0, D, parent=rig, rotation=LEAF_ROT, enabled=False))
    tmp.append(shape("Leaf Wilt", [G("W", leaf_outline(LF), fill("#9C9372"))], [CX, CY], 3.5, D, parent=rig, rotation=LEAF_ROT, opacity=A(K(3.5, 0), K(6.5, 55))))
    tmp.append(shape("Leaf", coffee_leaf(LF, MX, sh=8, petiole=False), [CX, CY], 0, D, parent=rig, rotation=LEAF_ROT))
    tmp.append(null(rig, [CX, CY], 0, D, position=A(K(6.6, [CX, CY]), K(7.4, [560, 600])), scale=A(K(6.6, [100, 100]), K(7.4, [72, 72]))))
    # date and name
    tmp.append(appear(text("Year", "2012", [130, 230], 110, INK, 2.6, D, font=HEAD, just="left"), 2.6))
    tmp += wipe_text("Roya Sci", "Hemileia vastatrix", [134, 296], 36, INK, 3.2, D, font=SCI, just="left")
    tmp.append(appear(caps("Roya Name", "LA ROYA · COFFEE LEAF RUST", [134, 340], 3.6, D, size=20, color=RUST, just="left"), 3.6))
    # harvest chart
    base = 800
    for j, (lab, h, t, col) in enumerate([("2012", 380, 7.6, MX), ("2016", 190, 8.4, "#9C9372")]):
        x = 1220 + j * 300
        tmp.append(shape(f"Bar {lab}", [G("Bar", rect([170, h], [0, -h / 2], 6), fill(col))], [x, base], t, D, scale=A(K(t, [100, 0]), K(t + 0.6, [100, 100]))))
        tmp.append(appear(caps(f"Bar {lab} Label", lab, [x, base + 40], t, D, size=20, color=INK), t))
    tmp.append(shape("Chart Base", [G("Base", path([(1080, base), (1680, base)]), stroke(INK, 3))], [0, 0], 7.4, D, scale=A(K(7.4, [0, 100]), K(7.9, [100, 100])),
                     anchorPoint=[1380, base], position=[1380, base]))
    tmp.append(appear(caps("Chart Title", "MEXICO'S COFFEE HARVEST", [1370, 330], 7.4, D, size=20), 7.4))
    tmp.append(appear(text("Chart Drop", "≈ half", [1520, 560], 56, RUST, 9.0, D, font=HEAD), 9.0))
    for j, l in enumerate(tmp):
        if l["type"] != "null":
            add_out(l, t_clear + (j % 4) * 0.05, 0.35)
    # the rescue tree
    z0, z1 = 21.5, 22.7
    zoom = 220 / (HS * 90)
    cam = "Cam"
    tree = []
    LINKC = "#9A9A9A"

    def half(name, pos, d, t):
        r = d / 2
        k = 0.5523 * r
        left = path([(0, -r), (0, r)], True, i=[(0, 0), (-k, 0)], o=[(-k, 0), (0, 0)])
        left = path([(0, -r), (-r, 0), (0, r)], True, i=[(0, 0), (0, -k), (-k, 0)], o=[(-k, 0), (0, k), (0, 0)])
        right = path([(0, -r), (r, 0), (0, r)], True, i=[(0, 0), (0, -k), (k, 0)], o=[(k, 0), (0, k), (0, 0)])
        return shape(name, [G("Ara Half", left, fill(ARA)), G("Rob Half", right, fill(ROB)), G("Shadow", ell([d, d]), fill("#000000", 9), tr={"position": [0, 5]})],
                     list(pos), t, D, scale=grow(t))

    def dbl(name, pts, t, d=0.6):
        """Arabica (red) and robusta (brown) lines side by side: the robusta genes travel down the tree."""
        offs = [(-3, ARA), (3, ROB)]
        out = []
        for o, col in offs:
            p2 = [(x + o, y + o) for x, y in pts]
            out.append(shape(f"{name} {col}", [G("Link", path(p2), trim(0, A(K(t, 0), K(t + d, 100))), stroke(col, 4))], [0, 0], t, D))
        return out

    ar, rb, tm = (230, 300), (230, 680), (560, 490)
    tree.append(disc("Arabica Parent", list(ar), 80, ARA, 12.6, D, scale=grow(12.6)))
    tree.append(disc("Robusta Parent", list(rb), 80, ROB, 12.9, D, scale=grow(12.9)))
    tree.append(appear(caps("Arabica Parent Label", "ARABICA", [ar[0], ar[1] + 78], 12.8, D, size=18, color=ARA), 12.8))
    tree.append(appear(caps("Robusta Parent Label", "ROBUSTA", [rb[0], rb[1] + 78], 13.1, D, size=18, color=ROB), 13.1))
    tree.append(shape("Link Ara Timor", [G("L", path([(ar[0] + 46, ar[1]), (400, ar[1]), (400, tm[1] - 20), (tm[0] - 62, tm[1] - 20)]), trim(0, A(K(13.4, 0), K(14.1, 100))), stroke(ARA, 4))], [0, 0], 13.4, D))
    tree.append(shape("Link Rob Timor", [G("L", path([(rb[0] + 46, rb[1]), (400, rb[1]), (400, tm[1] + 20), (tm[0] - 62, tm[1] + 20)]), trim(0, A(K(13.4, 0), K(14.1, 100))), stroke(ROB, 4))], [0, 0], 13.4, D))
    tree.append(half("Timor Hybrid", tm, 110, 14.1))
    tree.append(appear(text("Timor Name", "Timor Hybrid", [tm[0], tm[1] + 98], 34, INK, 14.4, D, font=HEAD), 14.4))
    tree.append(appear(text("Timor Note", "natural cross, Timor, 1927", [tm[0], tm[1] + 130], 20, GREY, 14.6, D, font=SCI), 14.6))
    groups = [("Catimor", (930, 300), 16.4, "Caturra × Timor Hybrid"), ("Sarchimor", (930, 680), 17.0, "Villa Sarchí × Timor Hybrid")]
    for nm, p, t, note in groups:
        tree += dbl(f"Link {nm}", [(tm[0] + 62, tm[1]), (720, tm[1]), (720, p[1]), (p[0] - 52, p[1])], t - 0.6)
        tree.append(half(nm, p, 90, t))
        tree.append(appear(text(f"{nm} Name", nm, [p[0], p[1] - 70], 34, INK, t + 0.2, D, font=HEAD), t + 0.2))
        tree.append(appear(text(f"{nm} Note", note, [p[0], p[1] + 82], 20, GREY, t + 0.35, D, font=SCI), t + 0.35))
    vars_ = [("Costa Rica 95", (1330, 220), 18.9, (930, 300), None), ("Oro Azteca", ORO, 19.6, (930, 300), "BRED IN MEXICO"),
             ("Marsellesa", (1330, 760), 20.3, (930, 680), None)]
    for nm, p, t, src, tag in vars_:
        tree += dbl(f"Link {nm}", [(src[0] + 50, src[1]), (1150, src[1]), (1150, p[1]), (p[0] - 50, p[1])], t - 0.5, 0.5)
        tree.append(disc(f"Var {nm}", list(p), 90, ARA, t, D, sh=3, scale=grow(t)))
        tree.append(appear(text(f"{nm} Name", nm, [p[0] + 72, p[1] + 12], 36, INK, t + 0.15, D, font=HEAD, just="left"), t + 0.15, dx=-20, dy=0))
        if tag:
            w = tw(tag, 15, LAB, 140) + 30
            tree.append(caps(f"{nm} Tag", tag, [p[0] + 72 + w / 2, p[1] + 58], t + 0.4, D, size=15, color=WHITE, opacity=fade_in(t + 0.4)))
            tree.append(shape(f"{nm} Tag Pill", [G("Pill", rect([w, 32], None, 16), fill(MX))], [p[0] + 72 + w / 2, p[1] + 52], t + 0.3, D, scale=grow(t + 0.3)))
    tree.append(appear(caps("Resistant", "RUST-RESISTANT", [1150, 110], 19.0, D, size=20, color=RUST), 19.0))
    for l in tree:
        if l["name"] != "Var Oro Azteca":
            add_out(l, z0, 0.4)
    parent_all(tree, cam)
    tree.append(null(cam, list(ORO), 0, D, scale=zoom_scale(z0, z1, 1.0, zoom), position=zoom_pos(z0, z1, ORO, (CX, CY))))
    L = tree + tmp
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 10 - CLOSE (9 s)
# =====================================================================
def s10_close(D):
    L = []
    rig = "Cherry Rig"
    L += wipe_text("End Title", "The Coffee Family Tree", [CX, 790], 84, INK, 6.4, D, hl=True)
    L.append(appear(text("End Sub", "From Ethiopia to Mexico, one seed at a time", [CX, 860], 32, GREY, 7.0, D, font=SCI), 7.0))
    L.append(caps("Label Robusta", "A LITTLE ROBUSTA", [1180, 452], 4.7, D, color=ROB, just="left", opacity=fade_io(4.7, 6.2)))
    L.append(lead("Leader Robusta", (1000, 520), (1160, 460), 4.5, 6.2, col=ROB))
    L.append(coffee_section("S10", 1.6, None, D, rig, thread_t=3.8))
    # Oro Azteca's disc turns back into a cherry, and the twig and leaves grow around it
    L += coffee_cherry("S10", 0, D, rig, morph_in=(0.0, 0.5), branch_t=0.25, detail_t=0.5)
    L.append(null(rig, [CX, CY], 0, D, position=A(K(6.0, [CX, CY]), K(7.0, [CX, 400])), scale=A(K(6.0, [100, 100]), K(7.0, [72, 72]))))
    L.append(bg(D))
    return L


# =====================================================================
# MAIN
# =====================================================================
SCENES = [("S1_Seed", 10.0, s1_seed), ("S2_Genus", 13.0, s2_genus), ("S3_TwoSpecies", 25.0, s3_species),
          ("S4_Others", 22.0, s4_others), ("S5_Origin", 17.0, s5_origin), ("S6_Routes", 19.0, s6_routes),
          ("S7_Mexico", 13.0, s7_mexico), ("S8_Varieties", 29.0, s8_tree), ("S9_Roya", 23.0, s9_roya), ("S10_Close", 9.0, s10_close)]


def zero_tangents(proj):
    """Linear spatial paths: AE's default auto-bezier makes holds between position keys drift in loops."""
    def fix(prop):
        if isinstance(prop, dict):
            for k in prop.get("keyframes", []):
                if isinstance(k["value"], list) and len(k["value"]) == 2:
                    k["inTangent"], k["outTangent"] = [0, 0], [0, 0]

    def walk_shapes(items):
        for it in items:
            if it.get("type") == "group":
                fix((it.get("transform") or {}).get("position"))
                walk_shapes(it.get("items", []))

    for c in proj["compositions"]:
        for l in c["layers"]:
            tr = l.get("transform", {})
            fix(tr.get("position"))
            fix(tr.get("anchorPoint"))
            walk_shapes(l.get("shapes", []))


# ---------- timing: 24 fps, in/out animations in whole 12-frame beats ----------
EPS = 1e-6
_UEXPR = re.compile(r"\(time - ([-0-9.e]+)\) / ([-0-9.e]+)\)")


def frames(t):
    return round(t * FPS)


def beats(d):
    """Duration d (s) rounded to a whole number of beats, at least one."""
    return max(1, round(d * FPS / BEAT)) * BEAT / FPS


def _same(a, b):
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) < 1e-6
    return a == b


def _is_zero(v):
    return all(abs(x) < 1e-6 for x in v) if isinstance(v, list) else isinstance(v, (int, float)) and abs(v) < 1e-6


def _ease_side(k, **kw):
    e = k.get("ease")
    if e is None or isinstance(e, str):
        return  # linear or preset keys keep their ease
    k["ease"] = dict(e, **kw)


def retime(layers, D, Dn):
    """Map a scene designed at D seconds onto Dn seconds at FPS.

    Start times scale by Dn / D and snap to frames; every animated segment (two keys with different values) is
    re-timed to a whole number of 12-frame beats from its start. A segment that ends on the scene's last frame
    (the handoff to the next scene) keeps that end and moves its start instead. Holds absorb the difference.
    Segments that go to zero (fade-outs, scale-outs, retracting trims) get the EXIT ease: slow start, fast leave.
    """
    f = Dn / D
    T = lambda t: Dn if abs(t - D) < EPS else frames(t * f) / FPS

    def keys(ks, tmap):
        def mv(a, b):
            return not _same(a["value"], b["value"]) and a.get("interp") != "hold"

        # a drift into the cut right after an animation: hold first, so both keep whole beats
        copies = set()
        for j in range(len(ks) - 1, 1, -1):
            if abs(ks[j]["time"] - D) < EPS and mv(ks[j - 1], ks[j]) and mv(ks[j - 2], ks[j - 1]):
                ks.insert(j, dict(ks[j - 1]))
                copies.add(j + 1)
        old = [k["time"] for k in ks]
        new = []
        for j, k in enumerate(ks):
            if j == 0:
                new.append(T(old[0]))
                continue
            moving = mv(ks[j - 1], k)
            if moving:
                d = beats((old[j] - old[j - 1]) * f)
                if abs(old[j] - D) < EPS:
                    if j > 1:
                        d = min(d, (Dn - new[j - 2] - 1 / FPS) // (BEAT / FPS) * BEAT / FPS)
                    if d < BEAT / FPS - EPS:  # no room for a whole beat: land on the final value instead of drifting
                        ks[j - 1]["value"] = k["value"]
                        if j in copies:
                            ks[j - 2]["value"] = k["value"]
                        new.append(max(T(old[j]), new[j - 1] + 1 / FPS))
                        continue
                    new[j - 1] = Dn - d
                    new.append(Dn)
                else:
                    new.append(new[j - 1] + d)
                if _is_zero(k["value"]) and not _is_zero(ks[j - 1]["value"]):
                    _ease_side(ks[j - 1], outInfluence=70, outSpeed=0)
                    _ease_side(k, inInfluence=10, inSpeed=0)
            else:
                new.append(max(T(old[j]), new[j - 1] + 1 / FPS))
        for k, o, n in zip(ks, old, new):
            k["time"] = round(n, 6)
            tmap.setdefault(round(o, 3), []).append(n)

    def expr(e):
        return _UEXPR.sub(lambda m: f"(time - {T(float(m.group(1))):.6f}) / {beats(float(m.group(2)) * f):.6f})", e)

    def walk(o, tmap):
        if isinstance(o, dict):
            if isinstance(o.get("keyframes"), list) and o["keyframes"]:
                keys(o["keyframes"], tmap)
            if isinstance(o.get("expression"), str):
                o["expression"] = expr(o["expression"])
            for k, v in o.items():
                if k not in ("keyframes", "expression"):
                    walk(v, tmap)
        elif isinstance(o, list):
            for v in o:
                walk(v, tmap)

    for l in layers:
        tmap = {}
        walk(l.get("transform", {}), tmap)
        walk(l.get("shapes", []), tmap)
        t_in, t_out = l["in"], l["out"]
        l["in"] = T(t_in)
        if abs(t_out - D) < EPS:
            l["out"] = Dn
        else:
            l["out"] = min(Dn, max(tmap.get(round(t_out, 3), [T(t_out)])))
        l["out"] = round(max(l["out"], l["in"] + 1 / FPS), 6)
        l["in"] = round(l["in"], 6)
    return layers


def check_timing(proj):
    """Every key on a whole frame, every animated segment a whole number of beats, nothing animating past the cut."""
    bad = []

    def chk(o, where, D):
        if isinstance(o, dict):
            ks = o.get("keyframes")
            if isinstance(ks, list):
                for k in ks:
                    if abs(k["time"] * FPS - round(k["time"] * FPS)) > 1e-3:
                        bad.append((where, "off-frame key", k["time"]))
                for a, b in zip(ks, ks[1:]):
                    if round((b["time"] - a["time"]) * FPS) < 1:
                        bad.append((where, "keys less than a frame apart", a["time"]))
                    if not _same(a["value"], b["value"]) and a.get("interp") != "hold":
                        n = round((b["time"] - a["time"]) * FPS)
                        if n % BEAT:
                            bad.append((where, f"{n} frames", a["time"]))
                        if b["time"] > D + EPS:
                            bad.append((where, "past the cut", b["time"]))
            for m in _UEXPR.finditer(o.get("expression") or ""):
                if round(float(m.group(2)) * FPS) % BEAT:
                    bad.append((where, "expression ramp", m.group(0)))
            for k, v in o.items():
                if k != "keyframes":
                    chk(v, where, D)
        elif isinstance(o, list):
            for v in o:
                chk(v, where, D)

    for c in proj["compositions"][1:]:
        for l in c["layers"]:
            chk(l, f'{c["name"]}/{l["name"]}', c["duration"])
            for t in (l["in"], l["out"]):
                if abs(t * FPS - round(t * FPS)) > 1e-3:
                    bad.append((f'{c["name"]}/{l["name"]}', "off-frame in/out", t))
    return bad


def build(durations=None, aep="coffee_families.aep", schema="../motion.schema.json"):
    """durations: one length (s) per scene, e.g. measured from the voiceover; default is the designed timing."""
    comps, main = [], []
    t = 0.0
    durations = durations or [d for _, d, _ in SCENES]
    for (cname, d, fn), dn in zip(SCENES, durations):
        dn = frames(dn) / FPS
        layers = retime(fn(d), d, dn)
        names = [l["name"] for l in layers]
        assert len(names) == len(set(names)), (cname, [n for n in names if names.count(n) > 1])
        missing = [(l["name"], l["parent"]) for l in layers if l.get("parent") and l["parent"] not in names]
        assert not missing, (cname, "parent not found", missing)
        mattes = [(l["name"], l["trackMatte"]["target"]) for l in layers if l.get("trackMatte") and l["trackMatte"]["target"] not in names]
        assert not mattes, (cname, "matte not found", mattes)
        bad = [l["name"] for l in layers if not l["out"] > l["in"]]
        assert not bad, (cname, "out <= in", bad)
        comps.append({"name": cname, "width": W, "height": H, "fps": FPS, "duration": dn, "backgroundColor": WHITE, "layers": layers})
        # the master's 3 % push-in runs the length of the scene; it is a drift, not an in/out animation
        main.insert(0, {"name": cname, "type": "precomp", "source": cname, "startTime": round(t, 6), "in": round(t, 6), "out": round(t + dn, 6),
                        "transform": {"scale": A(KL(t, [100, 100]), KL(t + dn, [HS * 100, HS * 100]))}})
        t = frames(t + dn) / FPS
    for l in main:
        l["transform"]["scale"]["keyframes"][0]["time"] = l["in"]
        l["transform"]["scale"]["keyframes"][1]["time"] = l["out"]
    grain = {"name": "Paper Grain", "type": "adjustment", "in": 0, "out": t,
             "effects": [{"matchName": "ADBE Noise", "props": {"ADBE Noise-0001": 2.0}}]}
    master = {"name": "Coffee_Families", "width": W, "height": H, "fps": FPS, "duration": t, "backgroundColor": WHITE,
              "layers": [grain] + main}
    proj = {"$schema": schema, "file": aep, "expressionEngine": "javascript-1.0",
            "bitDepth": "8 bpc", "compositions": [master] + comps}
    zero_tangents(proj)
    bad = check_timing(proj)
    assert not bad, "\n".join(map(str, bad[:40])) + f"\n... {len(bad)} timing problems"
    return proj


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "coffee_families.json")
    proj = build()
    with open(out, "w", encoding="utf-8") as f:
        json.dump(proj, f, indent=1, ensure_ascii=False)
    t = 0
    for c in proj["compositions"][1:]:
        print(f"{int(t // 60)}:{t % 60:04.1f}  {c['name']}")
        t += c["duration"]
    print("total", t, "s at", FPS, "fps,", sum(len(c["layers"]) for c in proj["compositions"]), "layers")
