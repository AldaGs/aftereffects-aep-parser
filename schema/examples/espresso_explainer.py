"""Generator for espresso_explainer.json, a 2:22 illustrated explainer (see espresso_explainer_script.md).

The authoring JSON is ~450 layers, so it is generated, not hand-written. Edit this file, then:

    python schema/examples/espresso_explainer.py            # writes espresso_explainer.json next to this file
    go run ./cmd/json2jsx -i schema/examples/espresso_explainer.json

Layout: palette + keyframe/shape/layer helpers, reusable art (cup, gauge, pipes, streams),
one function per scene (s1_hook ... s7_outro, type_scene + art_* for the machine types),
and build(), which assembles the scene precomps, wipes and grain into the master comp.
"""
import json, math, os, random, sys

W, H, FPS = 1920, 1080, 30
TITLE, SERIF, SERIF_I = "Georgia-Bold", "Georgia", "Georgia-Italic"
SANS_B, SANS = "Arial-BoldMT", "ArialMT"
INK, OW = "#24150E", 5
C = dict(
    paper="#F4E9D8", paper2="#E6D5BA", paperShade="#D7C3A3", sepia="#EADBC3",
    esp="#3B2418", esp2="#24130A", coffee="#6E4127", caramel="#C98A4B", crema="#E2AE6C", cremaLight="#F2D39C",
    teal="#3E8A8C", tealLight="#8CC7C2", water="#5BB5C9", waterLight="#C4ECF2", waterDeep="#2F7F95",
    red="#D9583B", redDark="#9E3A24", glow="#FF8A4C", mustard="#E3A72F", mustardDark="#B07D16",
    copper="#C27A45", copperDark="#8F5129", copperLight="#E3A27A", brass="#D4A64A",
    steel="#D3D8DB", steelMid="#9AA4A9", steelDark="#626C71", steelShadow="#454D52", handle="#2B211C",
    cream="#F4E9D8", muted="#BFAE98", pro="#6DBE7B", con="#E46F57",
    roast="#2A1B14", roast2="#3A261B", roast3="#4A3122",
)

# ---------- keyframes ----------
SNAP = {"inInfluence": 85, "outInfluence": 10, "inSpeed": 0, "outSpeed": 0}

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

def pop(t, s=100, d=0.5):
    return A(K(t, [0, 0]), K(t + d * 0.45, [s * 1.12, s * 1.12]), KS(t + d * 0.72, [s * 0.96, s * 0.96]), KS(t + d, [s, s]))

def slide(t, pos, dx=0, dy=40, d=0.6):
    return A(K(t, [pos[0] + dx, pos[1] + dy]), K(t + d, pos))

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

def smooth(pts, closed=False, k=1 / 6):
    """Catmull-Rom style bezier through points."""
    n = len(pts)
    ins, outs = [], []
    for j in range(n):
        if closed:
            a, b = pts[(j - 1) % n], pts[(j + 1) % n]
        else:
            a, b = pts[max(j - 1, 0)], pts[min(j + 1, n - 1)]
        tx, ty = (b[0] - a[0]) * k, (b[1] - a[1]) * k
        if not closed and (j == 0 or j == n - 1):
            tx, ty = tx / 2, ty / 2
        ins.append((-tx, -ty))
        outs.append((tx, ty))
    return path(pts, closed, ins, outs)

def fill(c, op=None):
    d = {"type": "fill", "color": c}
    if op is not None:
        d["opacity"] = op
    return d

def stroke(c, w, op=None, cap="round", join="round"):
    d = {"type": "stroke", "color": c, "strokeWidth": w, "lineCap": cap, "lineJoin": join}
    if op is not None:
        d["opacity"] = op
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

def obj(name, shp, col, ink=INK, w=OW, tr=None):
    """Illustrated object: fill with an ink outline on top."""
    shp = shp if isinstance(shp, list) else [shp]
    return G(name, *shp, stroke(ink, w), fill(col), tr=tr)

# ---------- layers ----------
def _tr(L, tr):
    for k, v in tr.items():
        if v is None:
            continue
        if k == "parent":
            L["parent"] = v
        elif k == "enabled":
            L["enabled"] = v
        elif k == "position" and isinstance(v, dict) and "expression" in v and "value" not in v and "keyframes" not in v:
            # keep the static position so `value` in the expression means something
            L["transform"][k] = dict(v, value=L["transform"]["position"])
        else:
            L["transform"][k] = v
    return L

def shape(name, groups, pos, t0, t1, **tr):
    L = {"name": name, "type": "shape", "in": round(t0, 3), "out": round(t1, 3), "shapes": groups, "transform": {"position": pos}}
    return _tr(L, tr)

def text(name, s, pos, size, color, t0, t1, font=SANS_B, just="center", tracking=0, leading=0, **tr):
    T = {"string": s, "font": font, "fontSize": size, "fillColor": color, "justification": just}
    if tracking:
        T["tracking"] = tracking
    if leading:
        T["leading"] = leading
    L = {"name": name, "type": "text", "in": round(t0, 3), "out": round(t1, 3), "text": T, "transform": {"position": pos}}
    return _tr(L, tr)

def null(name, pos, t0, t1, anchor=(0, 0), **tr):
    L = {"name": name, "type": "null", "in": round(t0, 3), "out": round(t1, 3),
         "transform": {"position": pos, "anchorPoint": list(anchor)}}
    return _tr(L, tr)

def appear(L, t, dx=0, dy=30, d=0.6):
    p = L["transform"]["position"]
    L["transform"]["position"] = slide(t, p, dx, dy, d)
    L["transform"]["opacity"] = fade_in(t, d * 0.6)
    return L

def parent_all(layers, parent, skip=()):
    for L in layers:
        if L["name"] not in skip and "parent" not in L and L["name"] != parent:
            L["parent"] = parent
    return layers

def bg(color, D, extra=()):
    return [shape("BG", [G("BG", rect([W + 400, H + 400]), fill(color))], [960, 540], 0, D)] + list(extra)

def particles(name, n, box, color, t0, t1, seed, size=(4, 9), speed=18, op=35):
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    Hh = y1 - y0
    gs = []
    for k in range(n):
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        s = rnd.uniform(*size)
        sp = speed * rnd.uniform(0.6, 1.4)
        a, ph = rnd.uniform(0.4, 1.1), rnd.uniform(0, 6.28)
        expr = (f"var y = {y:.0f} - time * {sp:.1f}; y = ((y - {y0}) % {Hh} + {Hh}) % {Hh} + {y0}; "
                f"[{x:.0f} + Math.sin(time * {a:.2f} + {ph:.2f}) * 16, y]")
        gs.append(G(f"P{k + 1}", ell([s, s]), fill(color, op), tr={"position": X(expr)}))
    return shape(name, gs, [0, 0], t0, t1, opacity=fade_in(t0, 1.0))

def steam(prefix, pos, t0, t1, parent=None, k=1.0, color=None, op=55, n=3):
    out = []
    color = color or C["cream"]
    offs = [(-0.32, 0.0), (0, 0.8), (0.32, 1.5)][:n] if n == 3 else [(0, 0.4)]
    for j, (dx, ph) in enumerate(offs):
        wisp = path([(0, 0), (0, -70 * k), (0, -150 * k)], False, i=[(0, 0), (-28 * k, 30 * k), (-28 * k, 30 * k)],
                    o=[(28 * k, -30 * k), (28 * k, -30 * k), (0, 0)])
        out.append(shape(f"{prefix} Steam {j + 1}", [
            G("Wisp", wisp, trim(X(f"Math.max(0, Math.min(100, (((time + {ph}) % 2.4) - 0.8) * 90))"),
                                 X(f"Math.min(100, ((time + {ph}) % 2.4) * 90)")), stroke(color, 9 * k, op))],
            [pos[0] + dx * 220 * k, pos[1]], t0, t1, parent=parent, opacity=fade_in(t0, 0.8)))
    return out

# ---------- reusable art ----------
def cup(prefix, cx, cy, k, t0, t1, scale=None, fill_t=None, steam_t=None, parent=None):
    """3/4-view demitasse on a saucer. (cx, cy) is the rim centre. Returns layers top->bottom.
    fill_t=(a, b): the espresso surface rises between a and b (else it starts full)."""
    s = lambda v: [v[0] * k, v[1] * k]
    body = path([s((-150, 0)), s((150, 0)), s((0, 178))], True,
                i=[s((0, 115)), s((0, 0)), s((108, 0))], o=[s((0, 0)), s((0, 115)), s((-108, 0))])
    shade = path([s((62, 0)), s((150, 0)), s((0, 178)), s((-20, 150))], True,
                 i=[s((-10, 50)), s((0, 0)), s((108, 0)), s((0, 0))], o=[s((0, 0)), s((0, 115)), s((-20, 0)), s((60, -40))])
    cup_l = shape(f"{prefix} Cup", [
        G("Opening", ell(s((268, 52))), stroke(INK, OW * min(1, k + 0.3)), fill(C["esp2"])),
        obj("Rim", ell(s((300, 72))), C["paper"], w=OW * min(1, k + 0.3)),
        G("Highlight", path([s((-120, 34)), s((-84, 118))], False, i=[(0, 0), s((-20, -30))], o=[s((0, 30)), (0, 0)]), stroke("#FFFFFF", 10 * k, 55)),
        G("Shade", shade, fill(C["paperShade"])),
        obj("Body", body, C["paper"], w=OW * min(1, k + 0.3)),
        G("Handle", ell(s((96, 86)), s((176, 62))), stroke(C["paper"], 20 * k), stroke(INK, 32 * k)),
        obj("Saucer Well", ell(s((300, 58)), s((0, 196))), C["paperShade"], w=OW * min(1, k + 0.3) * 0.7),
        obj("Saucer", ell(s((520, 118)), s((0, 200))), C["paper2"], w=OW * min(1, k + 0.3)),
        G("Shadow", ell(s((560, 130)), s((10, 214))), fill(INK, 35)),
    ], [cx, cy], t0, t1, scale=scale, parent=parent)
    surf_items = [
        G("Swirl", path([s((-60, -4)), s((10, -10)), s((70, 2))], False, i=[(0, 0), s((-30, 0)), s((-20, -6))], o=[s((20, -6)), s((30, 0)), (0, 0)]),
          stroke(C["cremaLight"], 6 * k, 80)),
        G("Crema", ell(s((236, 40)), s((0, -1))), fill(C["crema"])),
        G("Espresso", ell(s((262, 50))), fill(C["coffee"])),
    ]
    if fill_t:
        a, b = fill_t
        surf = shape(f"{prefix} Surface", surf_items, A(K(a, [cx, cy + 20 * k], None), KS(b, [cx, cy + 1 * k])), a, t1,
                     scale=A(K(a, [18, 18], None), KS(b, [100, 100])), parent=parent)
    else:
        surf = shape(f"{prefix} Surface", surf_items, [cx, cy + k], t0, t1, parent=parent)
    out = [surf, cup_l]
    if steam_t is not None:
        out = steam(prefix, [cx, cy - 40 * k], steam_t, t1, parent=parent, k=k) + out
    return out

def tiger_stream(name, x, y0, y1, t_on, t_off, t1, w=9, parent=None):
    """Striped espresso stream from y0 to y1; thins out at t_off."""
    L = y1 - y0
    n = max(3, round(L / 24))
    h = L / n
    cols = [C["esp2"], C["coffee"], C["caramel"], C["coffee"]]
    gs = [G(f"Stripe {j + 1}", rect([w, h + 1], X(f"[0, ((time * 280 + {j * h:.2f}) % {L:.2f})]")), fill(cols[j % 4])) for j in range(n)]
    return shape(name, gs, [x, y0], t_on, t1, parent=parent,
                 scale=A(K(t_on, [100, 0]), K(t_on + 0.35, [100, 100]), KS(t_off, [100, 100]), KS(t_off + 0.5, [0, 100])))

def gauge(prefix, pos, t0, t1, needle, size=120, label=None, label_col=None, parent=None, ring=C["steel"]):
    r = size / 2
    out = [
        shape(prefix + " Needle", [
            obj("Hub", ell([size * 0.16, size * 0.16]), C["handle"], w=3),
            G("Needle", path([(0, 8), (0, -r * 0.74)]), stroke(C["red"], max(4, size * 0.045))),
        ], pos, t0, t1, rotation=needle, parent=parent),
        shape(prefix + " Dial", [
            G("Redline", ell([size * 0.78, size * 0.78]), trim(0, 25, 45), stroke(C["red"], size * 0.06, cap="butt")),
            G("Ticks", ell([size * 0.78, size * 0.78]), trim(0, 75, -135), stroke(C["steelDark"], size * 0.06, cap="butt")),
            G("Face", ell([size * 0.86, size * 0.86]), fill(C["paper"])),
            obj("Bezel", ell([size, size]), ring),
        ], pos, t0, t1, scale=pop(t0), parent=parent),
    ]
    if label:
        out.append(text(prefix + " Label", label, [pos[0], pos[1] + r + 38], 20, label_col or C["muted"], t0, t1, tracking=120,
                        parent=parent, opacity=fade_in(t0 + 0.2)))
    return out

BAR = lambda b: -135 + b / 12 * 270

def pipe_layers(prefix, pts, t0, t1, flow=None, pulse=True, w=20, col=None, water=None, parent=None):
    """Pipe base + optional water fill drawn on between flow=(a, b) + moving highlight."""
    water = water or C["water"]
    out = []
    if flow:
        a, b = flow
        if pulse:
            out.append(shape(f"{prefix} Pulse", [G("Pulse", path(pts), trim(0, 14, X("time * 230")), stroke(C["waterLight"], w * 0.3, 85))],
                             [0, 0], b, t1, opacity=fade_in(b, 0.3), parent=parent))
        out.append(shape(f"{prefix} Flow", [G("Flow", path(pts), trim(0, A(K(a, 0, "easeInOut"), K(b, 100, "easeInOut"))), stroke(water, w * 0.5))],
                         [0, 0], a, t1, parent=parent))
    out.append(shape(f"{prefix} Pipe", [G("Pipe", path(pts), stroke(col or C["steelDark"], w), stroke(INK, w + 8))], [0, 0], t0, t1,
                     opacity=fade_in(t0), parent=parent))
    return out

def zigzag(n, length, width, horizontal=False):
    pts = [(0, 0)]
    for j in range(n):
        d = (j + 0.5) / n * length
        s = width / 2 if j % 2 == 0 else -width / 2
        pts.append((s, d) if not horizontal else (-d, s))
    pts.append((0, length) if not horizontal else (-length, 0))
    return pts

def puff(name, pos, t0, t1, k=1.0, ph=0.0, col=None, parent=None, rise=110):
    """Cartoon steam cloud that loops: rises, grows and fades."""
    col = col or "#FFFFFF"
    cyc = 2.2
    return shape(name, [G("Cloud", ell([60 * k, 60 * k], [-28 * k, 6 * k]), ell([74 * k, 74 * k], [6 * k, -8 * k]), ell([54 * k, 54 * k], [34 * k, 10 * k]),
                         ell([90 * k, 40 * k], [2 * k, 18 * k]), fill(col))],
                 pos, t0, t1, parent=parent,
                 position=X(f"var u = ((time + {ph}) % {cyc}) / {cyc}; [value[0] + Math.sin(u * 6) * 10, value[1] - u * {rise}]"),
                 scale=X(f"var u = ((time + {ph}) % {cyc}) / {cyc}; var s = 40 + u * 80; [s, s]"),
                 opacity=X(f"var u = ((time + {ph}) % {cyc}) / {cyc}; Math.min(1, (time - {t0}) / 0.5) * (u < 0.2 ? u / 0.2 : 1 - (u - 0.2) / 0.8) * 70"))

def check_icon(pos, good, t, D, name, parent=None):
    marks = [path([(-6, 0), (-1, 6), (8, -6)])] if good else [path([(-6, -6), (6, 6)]), path([(-6, 6), (6, -6)])]
    items = [G("Mark", *marks, stroke("#FFFFFF", 4))]
    return shape(name, items + [G("Disk", ell([30, 30]), fill(C["pro"] if good else C["con"]))], pos, t, D, scale=pop(t), parent=parent)

def caption_bar(prefix, steps, D, y=985):
    """Lower-third captions: numbered disk + sentence, swapping per step."""
    L = []
    for k, (a, b, s) in enumerate(steps):
        last = k == len(steps) - 1
        op = A(K(a, 0), K(a + 0.3, 100)) if last else fade_io(a, b)
        L.append(text(f"{prefix} Caption {k + 1}", s, [600, y + 12], 34, C["cream"], a, b, just="left", font=SANS, opacity=op,
                      position=slide(a, [600, y + 12], dx=30, dy=0)))
        L.append(text(f"{prefix} Num {k + 1}", str(k + 1), [548, y + 13], 32, C["esp"], a, b, font=TITLE, opacity=op))
    L.append(shape(f"{prefix} Num Disk", [G("Disk", ell([58, 58]), fill(C["mustard"]))], [548, y], steps[0][0], D, scale=pop(steps[0][0])))
    L.append(shape(f"{prefix} Panel", [G("Panel", rect([1000, 96], [430, 0], 48), fill("#120B08", 70))], [520, y], steps[0][0], D,
                   scale=A(K(steps[0][0], [0, 100]), K(steps[0][0] + 0.5, [100, 100]))))
    return L

# =====================================================================
# SCENE 1 - HOOK (12 s)
# =====================================================================
def s1_hook(D):
    L = []
    pour_on, pour_off = 2.0, 7.4
    # title (second half)
    L.append(appear(text("Title Sub", "A story of heat, pressure and about 25 seconds", [960, 325], 34, C["muted"], 8.6, D, font=SERIF_I), 8.6, dy=20))
    L.append(text("Title", "How does an espresso\rmachine work?", [960, 150], 84, C["cream"], 8.0, D, font=TITLE, leading=92,
                  opacity=fade_in(8.0, 0.4), position=slide(8.0, [960, 150], dy=-40), scale=A(K(8.0, [92, 92]), K(8.7, [100, 100]))))
    # callouts
    def callout(name, big, small, anchor, label_pos, t, t_out, icon):
        out = []
        lx, ly = label_pos
        out.append(text(f"{name} Small", small, [lx, ly + 34], 22, C["muted"], t + 0.35, t_out, tracking=150, opacity=fade_io(t + 0.35, t_out)))
        out.append(text(f"{name} Big", big, [lx, ly], 66, C["cream"], t + 0.25, t_out, font=TITLE, opacity=fade_io(t + 0.25, t_out),
                        position=slide(t + 0.25, [lx, ly], dy=20)))
        for l in icon:
            l["transform"]["opacity"] = fade_io(t, t_out)
        out += icon
        ax, ay = anchor
        midx = lx + (120 if ax > lx else -120)
        out.append(shape(f"{name} Leader", [
            G("Dot", ell([14, 14], [ax, ay]), fill(C["mustard"])),
            G("Line", path([(midx, ly - 80), (ax, ay)]), trim(0, A(K(t, 0), K(t + 0.5, 100))), stroke(C["mustard"], 3)),
        ], [0, 0], t, t_out, opacity=fade_io(t, t_out)))
        return out
    L += callout("Pressure", "9 bar", "PRESSURE", (960, 238), (500, 470), 2.6, 7.9,
                 gauge("Pressure Gauge", [500, 330], 2.6, 7.9, A(K(2.8, BAR(0)), K(3.6, BAR(9))), size=110))
    therm = [
        shape("Temp Mercury", [G("Mercury", rect([14, 74], [0, -37]), fill(C["red"]))], [1430, 352], 3.4, 7.9,
              scale=A(K(3.6, [100, 6]), K(4.6, [100, 100])), opacity=fade_io(3.4, 7.9)),
        shape("Temp Thermometer", [obj("Bulb", ell([46, 46], [0, 44]), C["red"]), obj("Tube", rect([30, 118], [0, -18], 15), C["paper"])],
              [1430, 300], 3.4, 7.9, scale=pop(3.4), opacity=fade_io(3.4, 7.9)),
    ]
    L += callout("Temp", "93 °C", "WATER TEMPERATURE", (1060, 160), (1430, 470), 3.4, 7.9, therm)
    timer = [
        shape("Timer Hand", [G("Hand", path([(0, 0), (0, -38)]), stroke(C["cream"], 5))], [1430, 700], 4.2, 7.9,
              rotation=A(KL(pour_on, 0), KL(pour_off, 360)), opacity=fade_io(4.2, 7.9)),
        shape("Timer", [G("Progress", ell([96, 96]), trim(0, A(KL(pour_on, 0), KL(pour_off, 100))), stroke(C["mustard"], 9)),
                        G("Face", ell([96, 96]), stroke(C["roast3"], 9)), obj("Button", rect([20, 14], [0, -60], 4), C["steel"], w=3)],
              [1430, 700], 4.2, 7.9, scale=pop(4.2), opacity=fade_io(4.2, 7.9)),
    ]
    L += callout("Time", "25 s", "FROM FIRST DROP TO LAST", (1060, 640), (1430, 860), 4.2, 7.9, timer)

    # machine top: spouts + portafilter + group head (exit upward at 7.6)
    exit_t = 7.6
    def top(name, groups, pos, t_in, dx=0, dy=-260):
        return shape(name, groups, A(K(t_in, [pos[0] + dx, pos[1] + dy]), K(t_in + 0.7, pos), KS(exit_t, pos), KS(exit_t + 0.6, [pos[0], pos[1] - 420])), t_in, D)
    L.append(top("Portafilter", [
        obj("Spout L", path([(-38, 22), (-22, 22), (-26, 52), (-34, 52)], True), C["steelMid"], w=4),
        obj("Spout R", path([(22, 22), (38, 22), (34, 52), (26, 52)], True), C["steelMid"], w=4),
        G("Shine", path([(-100, -6), (60, -6)]), stroke("#FFFFFF", 6, 60)),
        obj("Basket", rect([240, 50], [0, 0], 14), C["steel"]),
        G("Handle Shine", path([(-330, -4), (-180, -4)]), stroke("#FFFFFF", 5, 30)),
        obj("Handle", rect([280, 40], [-250, 4], 20), C["handle"]),
    ], [960, 200], 0.8, dx=-700, dy=0))
    L.append(top("Group Head", [
        G("Shine", path([(-150, -40), (140, -40)]), stroke("#FFFFFF", 7, 55)),
        obj("Collar", rect([280, 36], [0, 34], 10), C["steelMid"]),
        obj("Block", rect([360, 150], [0, -50], 24), C["steel"]),
    ], [960, 130], 0.4))
    # streams
    # cup (streams sit between the espresso surface and the cup)
    L += cup("Hero", 960, 640, 1.0, 1.1, D, scale=A(K(1.1, [100, 0]), K(1.45, [100, 112]), KS(1.7, [100, 96]), KS(1.9, [100, 100])),
             fill_t=(pour_on + 0.3, pour_off), steam_t=7.6)
    L[-1]["transform"]["position"] = A(K(1.1, [960, 1300]), K(1.5, [960, 640]))
    L.insert(len(L) - 1, tiger_stream("Stream L", 930, 252, 652, pour_on, pour_off, D))
    L.insert(len(L) - 1, tiger_stream("Stream R", 990, 252, 652, pour_on, pour_off, D))
    # ambience
    L.append(particles("Dust", 26, (0, 0, 1920, 1080), C["cremaLight"], 0, D, 11, speed=14, op=18))
    L += bg(C["roast"], D, [
        shape("Spot", [G("Inner", ell([760, 760]), fill(C["roast3"], 60)), G("Outer", ell([1300, 1300]), fill(C["roast2"]))],
              [960, 640], 0, D, scale=A(K(0, [80, 80]), K(1.2, [100, 100])), opacity=fade_in(0, 1.0))])
    return L

# =====================================================================
# SCENE 2 - WHY PRESSURE (13 s)
# =====================================================================
def s2_pressure(D):
    L = []
    cam = "Cam S2"
    tamp, water_t, slam = 2.6, 4.6, 8.0
    # grains packed in basket bed: local coords y in [-200, 0], layer at bed bottom
    rnd = random.Random(4)
    grains = []
    cols = [C["coffee"], C["esp"], "#8A5434", C["coffee"]]
    rows = 7
    for r in range(rows):
        y = -14 - r * 27
        half = 268 - (0 if r > 0 else 0)
        nx = 20
        for c in range(nx):
            x = -half + (c + (0.5 if r % 2 else 0)) * (2 * half / nx) + rnd.uniform(-4, 4)
            if abs(x) > 270:
                continue
            s = rnd.uniform(24, 32)
            t = 0.4 + r * 0.16 + rnd.uniform(0, 0.25)
            grains.append(G(f"G{r}-{c}", ell([s, s * rnd.uniform(0.82, 1.0)]), stroke(INK, 2.5), fill(rnd.choice(cols)),
                            tr={"position": [round(x, 1), round(y + rnd.uniform(-3, 3), 1)],
                                "scale": A(K(t, [0, 0]), K(t + 0.25, [112, 112]), KS(t + 0.4, [100, 100]))}))
    grains.reverse()
    bed_scale = A(K(tamp, [100, 100], "easeInOut"), K(tamp + 0.25, [100, 80]), KS(tamp + 0.45, [100, 82]))
    # water channels through the puck (drawn at slam)
    chans = []
    rnd2 = random.Random(9)
    for j in range(9):
        x = -240 + j * 60 + rnd2.uniform(-10, 10)
        pts = [(x, -200)] + [(x + rnd2.uniform(-16, 16), -200 + q * 40) for q in range(1, 5)] + [(x + rnd2.uniform(-6, 6), 0)]
        a = slam + 0.35 + j * 0.07
        chans.append(G(f"Channel {j + 1}", smooth(pts), trim(0, A(K(a, 0, "easeInOut"), K(a + 1.0, 100, "easeInOut"))),
                       stroke(A(K(a + 0.3, C["water"]), K(a + 1.6, C["caramel"])), 7)))
    L.append(shape("Channels", chans, [960, 760], slam, D, scale=bed_scale, parent=cam))
    L.append(shape("Grains", grains, [960, 760], 0.3, D, scale=bed_scale, parent=cam))
    # water pool on the puck
    L.append(shape("Water Pool", [G("Shine", path([(-200, -78), (120, -78)]), stroke(C["waterLight"], 6, 70)),
                                  G("Pool", rect([546, 96], [0, -48], 6), fill(C["water"], 90))],
                   [960, 600], water_t, D, parent=cam,
                   scale=A(K(water_t, [100, 0]), K(water_t + 0.7, [100, 100]), KS(slam + 0.2, [100, 100]), K(slam + 1.8, [100, 6]))))
    L.append(shape("Pour In", [G("Water", rect([16, 440], [0, 220]), fill(C["water"]))], [960, 120], water_t - 0.2, D, parent=cam,
                   scale=A(K(water_t - 0.2, [100, 0]), K(water_t + 0.15, [100, 100]), KS(water_t + 0.7, [100, 100]), KS(water_t + 1.2, [0, 100]))))
    # slow drip (gravity only) vs. espresso flow after slam
    L.append(shape("Slow Drip", [G("Drop", path([(0, -12), (9, 4), (0, 12), (-9, 4)], True, i=[(0, 0), (0, -6), (6, 0), (0, 6)], o=[(0, 0), (0, 6), (-6, 0), (0, -6)]),
                                   fill(C["coffee"]))], [960, 800], 5.6, slam, parent=cam,
                   position=X("var u = (time % 1.6) / 1.6; [960, 800 + u * u * 260]"), opacity=X("var u = (time % 1.6) / 1.6; u < 0.8 ? 100 : (1 - u) * 500")))
    L.append(tiger_stream("Espresso Out", 960, 798, 1200, slam + 1.3, D + 1, D, w=16, parent=cam))
    for j, x in enumerate([920, 1004, 945, 985]):
        L.append(shape(f"Crema Bubble {j + 1}", [G("B", ell([10, 10]), stroke(C["cremaLight"], 2.5))], [x, 830], slam + 1.6, D, parent=cam,
                       position=X(f"var u = ((time + {j * 0.37}) % 1.5) / 1.5; [{x} + Math.sin(time * 5 + {j}) * 6, 830 + u * 240]"), opacity=fade_in(slam + 1.6)))
    # tamper (in then out) and piston (slam)
    L.append(shape("Tamper", [
        G("Shine", path([(-20, -200), (-20, -60)]), stroke("#FFFFFF", 6, 45)),
        obj("Knob", ell([120, 90], [0, -220]), C["handle"]),
        obj("Shaft", rect([60, 170], [0, -110], 12), C["steelMid"]),
        obj("Base", rect([540, 46], [0, 0], 10), C["steel"]),
    ], A(K(1.6, [960, -150]), K(tamp, [960, 537]), KS(tamp + 0.45, [960, 573]), K(tamp + 1.2, [960, -250])), 1.6, tamp + 1.3, parent=cam))
    L.append(shape("Piston", [
        G("Shine", path([(-230, -150), (210, -150)]), stroke("#FFFFFF", 8, 50)),
        obj("Rod", rect([110, 300], [0, -330], 10), C["steelMid"]),
        obj("Head", rect([536, 200], [0, -100], 24), C["steel"]),
    ], A(K(slam - 0.5, [960, -320]), K(slam, [960, 500]), KS(slam + 0.25, [960, 492]), K(slam + 1.8, [960, 590])), slam - 0.5, D, parent=cam))
    chev = [G(f"Chevron {j}", path([(-40, -16), (0, 16), (40, -16)]), stroke(C["esp"], 12),
              tr={"position": X(f"[0, -60 + ((time * 70 + {j * 40}) % 120)]"), "opacity": X(f"var u = ((time * 70 + {j * 40}) % 120) / 120; Math.sin(u * Math.PI) * 100")})
            for j in range(3)]
    L.append(shape("Piston Arrows", chev, [960, 380], slam, D, parent="Piston"))
    L[-1]["transform"]["position"] = [0, -120]
    L.append(text("Piston Label", "9 BAR", [0, -20], 56, C["esp"], slam, D, font=TITLE, parent="Piston"))
    # basket (cross-section)
    basket = path([(-305, -260), (-292, 40), (-260, 70), (260, 70), (292, 40), (305, -260)], False)
    L.append(shape("Basket", [G("Holes", *[path([(x, 62), (x, 78)]) for x in range(-220, 221, 40)], stroke(C["roast"], 8, cap="butt")),
                              G("Wall", basket, stroke(C["steel"], 22), stroke(INK, 32))], [960, 700], 0.1, D, parent=cam, scale=pop(0.1)))
    # labels
    L.append(appear(text("Label Fine", "FINELY GROUND, TIGHTLY PACKED", [960, 960], 24, C["tealLight"], 1.6, tamp + 1.6, tracking=180,
                         opacity=fade_io(1.6, water_t)), 1.6))
    L[-1]["transform"]["opacity"] = fade_io(1.6, water_t + 0.2)
    L.append(text("Gravity Tag", "Gravity alone: barely a trickle", [1370, 520], 34, C["cream"], 5.4, slam, font=SERIF_I, just="left", opacity=fade_io(5.4, slam)))
    L.append(text("Crema Tag", "Oils + CO₂ + fine solids = crema", [1300, 900], 34, C["cream"], slam + 2.2, D, font=SERIF_I, just="left",
                  opacity=fade_in(slam + 2.2), position=slide(slam + 2.2, [1300, 900], dx=40, dy=0)))
    L.append(shape("Crema Tag Line", [G("L", path([(1290, 890), (1010, 900)]), trim(0, A(K(slam + 2.0, 0), K(slam + 2.5, 100))), stroke(C["cremaLight"], 3)),
                                      G("Dot", ell([12, 12], [1010, 900]), fill(C["cremaLight"]))], [0, 0], slam + 2.0, D))
    L.append(text("Headline", "Why pressure?", [960, 120], 64, C["cream"], 0.2, D, font=TITLE, opacity=fade_io(0.2, slam - 0.3),
                  position=slide(0.2, [960, 120], dy=30)))
    L.insert(0, null(cam, [960, 540], 0, D, anchor=(960, 540),
                     position=A(K(0, [960, 540], None), KS(slam - 0.01, [960, 540]), KL(slam, [960, 552]), KL(slam + 0.06, [960, 532]),
                                KL(slam + 0.12, [960, 546]), KL(slam + 0.2, [960, 538]), KS(slam + 0.3, [960, 540])),
                     scale=A(KS(0, [100, 100]), KS(D, [106, 106]))))
    L.append(particles("Specks", 30, (0, 0, 1920, 1080), C["tealLight"], 0, D, 21, op=14))
    L += bg("#173A3E", D, [shape("Halo", [G("H", ell([1100, 1100]), fill("#1E474C"))], [960, 600], 0, D, scale=pop(0, 100, 0.8))])
    return L

# =====================================================================
# SCENE 3 - HISTORY (18 s), camera pans along a timeline
# =====================================================================
def s3_history(D):
    L = []
    cam = "Cam S3"
    xs = [960, 1960, 2960, 3960]
    arrive = [0.2, 4.9, 9.3, 13.7]
    line_y = 800
    pal = dict(fillA=C["copper"], fillB=C["brass"], metal="#C9C3B6", paper=C["sepia"])
    # camera: pan to each stop
    keys = [K(0, [960, 540], "easeInOut")]
    for j in range(1, 4):
        keys.append(KS(arrive[j] - 0.9, [960 - (xs[j - 1] - 960), 540]))
        keys.append(KS(arrive[j], [960 - (xs[j] - 960), 540]))
    L.append(null(cam, [960, 540], 0, D, anchor=(960, 540), position=A(*keys), scale=A(KS(0, [100, 100]), KS(D, [103, 103]))))
    # timeline
    tl_keys = [K(0, 0, "easeInOut"), KS(1.0, 18)] + [KS(arrive[j], 18 + 24 * j) for j in range(1, 4)]
    L.append(shape("Timeline", [G("Line", path([(360, line_y), (4560, line_y)]), trim(0, A(*tl_keys)), stroke(INK, 6))], [0, 0], 0, D, parent=cam))
    facts = [
        ("1884", "Turin: Angelo Moriondo patents a steam\rmachine that brews coffee in bulk."),
        ("1905", "Milan: Bezzera & Pavoni's 'Ideale' serves single cups,\rbut steam only reaches about 1.5 bar."),
        ("1948", "Achille Gaggia's spring lever hits 9 bar.\rThe golden foam on top, crema, is born."),
        ("1961", "The Faema E61 swaps muscle for an electric pump:\rthe blueprint for modern machines."),
    ]
    for j, (yr, desc) in enumerate(facts):
        x, t = xs[j], arrive[j] + 0.3
        L.append(text(f"Desc {yr}", desc, [x, 960], 30, INK, t + 0.5, D, font=SERIF_I, leading=38, parent=cam, opacity=fade_in(t + 0.5)))
        L.append(text(f"Year {yr}", yr, [x, 900], 76, C["redDark"], t + 0.25, D, font=TITLE, parent=cam, opacity=fade_in(t + 0.25),
                      position=slide(t + 0.25, [x, 900], dy=25)))
        L.append(shape(f"Marker {yr}", [obj("Dot", ell([34, 34]), C["mustard"]), G("Ring", ell([60, 60]), stroke(INK, 3, 60))], [x, line_y], t, D,
                       scale=pop(t), parent=cam))
        L.append(shape(f"Ground {yr}", [G("G", ell([420, 40]), fill(INK, 15))], [x, 768], t, D, scale=pop(t), parent=cam))
    # 1884: bulk steam brewer
    x, t = xs[0], arrive[0] + 0.5
    L += [puff(f"1884 Puff {j}", [x - 60 + j * 30, 400], t + 0.6, D, k=0.9, ph=j * 0.7, parent=cam) for j in range(3)]
    L.append(shape("1884 Machine", [
        obj("Tap", path([(170, 690), (215, 690), (215, 715)]), C["brass"]),
        obj("Cup", path([(190, 725), (240, 725), (232, 762), (198, 762)], True), C["paper"], w=4),
        obj("Gauge", ell([60, 60], [-60, 560]), C["paper"], w=4),
        G("Needle", path([(-60, 560), (-48, 540)]), stroke(C["red"], 4)),
        G("Pipe", path([(40, 500), (100, 500), (100, 560)]), stroke(C["brass"], 16), stroke(INK, 24)),
        G("Bands", path([(-160, 620), (40, 620)]), path([(-160, 700), (40, 700)]), stroke(C["copperDark"], 8, cap="butt")),
        obj("Dome", ell([220, 110], [-60, 450]), C["copperLight"]),
        obj("Boiler", rect([220, 300], [-60, 610], 26), pal["fillA"]),
        obj("Chamber Lid", ell([130, 40], [110, 560]), C["copperLight"]),
        obj("Chamber", rect([130, 190], [110, 665], 18), pal["fillB"]),
        obj("Legs", [rect([30, 26], [-140, 768], 4), rect([30, 26], [20, 768], 4), rect([30, 26], [150, 768], 4)], C["handle"]),
    ], slide(t, [x, 0], dy=60), t, D, parent=cam, opacity=fade_in(t, 0.2)))
    # 1905: tall Ideale with eagle
    x, t = xs[1], arrive[1] + 0.3
    L += [puff(f"1905 Puff {j}", [x + (-90 if j else 90), 610], t + 0.6, D, k=0.7, ph=j * 1.1, parent=cam) for j in range(2)]
    L.append(shape("1905 Machine", [
        obj("Eagle Wing L", path([(0, 285), (-70, 250), (-40, 295)], True), C["brass"], w=4),
        obj("Eagle Wing R", path([(0, 285), (70, 250), (40, 295)], True), C["brass"], w=4),
        obj("Eagle", ell([36, 44], [0, 292]), C["brass"], w=4),
        obj("Finial", rect([16, 40], [0, 330], 4), C["brass"], w=4),
        obj("Dome", path([(-100, 400), (100, 400), (0, 330)], True, i=[(0, 0), (0, 0), (60, 0)], o=[(0, 0), (0, -50), (-60, 0)]), C["copperLight"]),
        obj("Group L", rect([90, 40], [-140, 620], 8), pal["metal"], w=4),
        obj("Group R", rect([90, 40], [140, 620], 8), pal["metal"], w=4),
        G("Handle L", path([(-150, 650), (-230, 700)]), stroke(C["handle"], 14), stroke(INK, 22)),
        G("Handle R", path([(150, 650), (230, 700)]), stroke(C["handle"], 14), stroke(INK, 22)),
        G("Bands", path([(-100, 460), (100, 460)]), path([(-100, 540), (100, 540)]), path([(-100, 700), (100, 700)]), stroke(C["copperDark"], 8, cap="butt")),
        obj("Plaque", rect([90, 50], [0, 600], 8), C["brass"], w=4),
        obj("Column", rect([200, 380], [0, 590], 14), pal["fillA"]),
        obj("Base", rect([260, 34], [0, 772], 10), C["handle"]),
    ], slide(t, [x, 0], dy=60), t, D, parent=cam, opacity=fade_in(t, 0.2)))
    L += gauge("1905 Gauge", [x + 210, 430], t + 0.6, D, A(K(t + 0.8, BAR(0)), K(t + 1.6, BAR(1.5))), size=90, label="1.5 BAR", label_col=INK, parent=cam)
    # 1948: spring lever, lever pulls down and returns
    x, t = xs[2], arrive[2] + 0.3
    L.append(shape("1948 Lever", [G("Knob", ell([46, 46], [200, 0]), fill(C["handle"])), G("Arm", path([(0, 0), (200, 0)]), stroke(pal["metal"], 16), stroke(INK, 24))],
                   [x + 40, 420], t, D, parent=cam, opacity=fade_in(t, 0.2),
                   rotation=A(K(t, -55), K(t + 1.2, -55), K(t + 1.8, 25), KS(t + 2.2, 25), KS(t + 3.6, -55))))
    L.append(shape("1948 Machine", [
        obj("Pivot", ell([30, 30], [40, 420]), C["steelMid"], w=4),
        obj("Bell", path([(-60, 400), (60, 400), (80, 590), (-80, 590)], True), pal["metal"]),
        obj("Cap", ell([130, 40], [0, 400]), C["steel"]),
        obj("Portafilter", rect([150, 34], [0, 610], 8), C["steelMid"], w=4),
        G("PF Handle", path([(-70, 610), (-190, 640)]), stroke(C["handle"], 14), stroke(INK, 22)),
        obj("Body", rect([300, 120], [0, 712], 16), C["redDark"]),
        G("Trim", path([(-150, 690), (150, 690)]), stroke(pal["metal"], 8, cap="butt")),
    ], slide(t, [x, 0], dy=60), t, D, parent=cam, opacity=fade_in(t, 0.2)))
    L += cup("1948", x + 260, 690, 0.32, t + 0.6, D, scale=pop(t + 0.6), parent=cam)
    for j, (dx, dy) in enumerate([(-50, -70), (40, -95), (70, -40)]):
        L.append(shape(f"1948 Sparkle {j + 1}", [G("S", path([(0, -16), (4, -4), (16, 0), (4, 4), (0, 16), (-4, 4), (-16, 0), (-4, -4)], True), fill(C["mustard"]))],
                       [x + 260 + dx, 690 + dy], t + 2.2 + j * 0.2, D, parent=cam,
                       scale=X(f"var s = 70 + Math.sin(time * 5 + {j}) * 30; [s, s]"), rotation=X(f"time * 40 + {j * 20}"), opacity=fade_in(t + 2.2 + j * 0.2)))
    L.append(text("1948 Crema", "crema!", [x + 260, 600], 30, C["redDark"], t + 2.4, D, font=SERIF_I, parent=cam, opacity=fade_in(t + 2.4)))
    # 1961: E61
    x, t = xs[3], arrive[3] + 0.3
    L.append(shape("1961 Machine", [
        obj("Bolt", path([(250, 380), (215, 450), (245, 450), (220, 520), (290, 430), (258, 430), (285, 380)], True), C["mustard"], w=4),
        G("Lever", path([(40, 525), (95, 490)]), stroke(C["handle"], 12), stroke(INK, 20)),
        obj("Mushroom", path([(-70, 560), (70, 560), (0, 510)], True, i=[(0, 0), (0, 0), (50, 0)], o=[(0, 0), (0, -40), (-50, 0)]), pal["metal"]),
        obj("Neck", rect([90, 50], [0, 585], 8), pal["metal"]),
        obj("Portafilter", rect([130, 30], [0, 625], 8), C["steelMid"], w=4),
        G("PF Handle", path([(-60, 625), (-180, 640)]), stroke(C["handle"], 14), stroke(INK, 22)),
        obj("Gauge", ell([56, 56], [150, 600]), C["paper"], w=4),
        G("Needle", path([(150, 600), (165, 585)]), stroke(C["red"], 4)),
        G("Rails", path([(-200, 470), (200, 470)]), stroke(pal["metal"], 8)),
        obj("Body", rect([440, 260], [0, 630], 22), C["red"]),
        obj("Feet", [rect([40, 20], [-180, 768], 4), rect([40, 20], [180, 768], 4)], C["handle"]),
    ], slide(t, [x, 0], dy=60), t, D, parent=cam, opacity=fade_in(t, 0.2)))
    L.append(text("1961 Pump", "ELECTRIC PUMP", [x + 255, 360], 20, INK, t + 0.8, D, tracking=150, parent=cam, opacity=fade_in(t + 0.8)))
    # header (fixed)
    L.insert(0, appear(text("Header", "A SHORT HISTORY OF PRESSURE", [960, 110], 26, C["redDark"], 0.2, D, tracking=250), 0.2))
    L.append(particles("Paper Specks", 40, (0, 0, 1920, 1080), INK, 0, D, 5, size=(2, 5), speed=6, op=12))
    L += bg(C["sepia"], D)
    return L

# =====================================================================
# SCENE 4 - INSIDE THE MACHINE (24 s), camera follows the water
# =====================================================================
def s4_inside(D):
    L = []
    cam = "Cam S4"
    steps = [(1.8, 5.4, "Water is pulled from the tank"),
             (5.4, 9.4, "The pump squeezes it to about 9 bar"),
             (9.4, 13.4, "The boiler heats it to about 93 °C"),
             (13.4, 17.4, "Hot, pressurised water floods the coffee puck"),
             (17.4, D, "Espresso pours out, crowned with crema")]
    shots = [(0.0, (960, 560), 1.0), (1.8, (320, 600), 1.6), (5.4, (660, 720), 1.7), (7.4, (1000, 330), 1.7),
             (9.4, (1000, 520), 1.45), (13.4, (1470, 500), 1.6), (17.4, (1470, 730), 1.5), (21.4, (960, 525), 0.92)]
    def campos(c, z):
        return [round(960 - z * (c[0] - 960), 1), round(540 - z * (c[1] - 540), 1)]
    pk, sk = [], []
    for j, (t, c, z) in enumerate(shots):
        t_arr = t + (1.0 if j else 0)
        if j:
            pk.append(KS(t, campos(shots[j - 1][1], shots[j - 1][2])))
            sk.append(KS(t, [shots[j - 1][2] * 100] * 2))
        pk.append(KS(t_arr, campos(c, z)))
        sk.append(KS(t_arr, [z * 100] * 2))
    L.append(null(cam, [960, 540], 0, D, anchor=(960, 540), position=A(*pk), scale=A(*sk)))
    L += caption_bar("Inside", steps, D)
    L.append(text("Header", "INSIDE THE MACHINE", [80, 92], 24, C["tealLight"], 0.2, D, just="left", tracking=250,
                  opacity=A(K(0.2, 0), K(0.6, 100), K(1.6, 100), K(2.0, 0), K(22.2, 0), K(22.6, 100))))
    L.append(text("Outro Line", "About 25 seconds, start to finish.", [960, 150], 52, C["cream"], 22.2, D, font=TITLE, opacity=fade_in(22.2),
                  position=slide(22.2, [960, 150], dy=-20)))

    P = dict(parent=cam)
    # --- cup + streams
    L += cup("Shot", 1470, 790, 0.5, 1.4, D, scale=pop(1.4, 100), fill_t=(17.8, 21.2), steam_t=21.0, parent=cam)
    L.insert(len(L) - 1, tiger_stream("Stream L", 1452, 582, 800, 17.5, 21.0, D, w=7, parent=cam))
    L.insert(len(L) - 1, tiger_stream("Stream R", 1488, 582, 800, 17.5, 21.0, D, w=7, parent=cam))
    # --- group head, puck
    drops = [G(f"Drop {j}", path([(0, -8), (6, 2), (0, 8), (-6, 2)], True, i=[(0, 0), (0, -4), (4, 0), (0, 4)], o=[(0, 0), (0, 4), (-4, 0), (0, -4)]),
               fill(C["water"]), tr={"position": X(f"[{-80 + j * 32}, 10 + ((time * 120 + {j * 13}) % 34)]")}) for j in range(6)]
    L.append(shape("Shower", drops, [1470, 486], 13.9, 17.6, opacity=fade_io(13.9, 17.6), **P))
    L.append(shape("Puck", [obj("Puck", rect([180, 32], None, 8), A(K(14.2, C["coffee"]), K(15.6, C["esp2"])), w=4)], [1470, 520], 1.6, D, scale=pop(1.6), **P))
    L.append(shape("Portafilter", [
        obj("Spout L", path([(-30, 30), (-14, 30), (-18, 60), (-26, 60)], True), C["steelMid"], w=4),
        obj("Spout R", path([(14, 30), (30, 30), (26, 60), (18, 60)], True), C["steelMid"], w=4),
        obj("Basket", path([(-120, -22), (120, -22), (104, 30), (-104, 30)], True), C["steel"]),
        G("Handle Shine", path([(270, -4), (130, -4)]), stroke("#FFFFFF", 5, 30)),
        obj("Handle", rect([210, 36], [230, 4], 18), C["handle"]),
    ], [1470, 528], 1.6, D, scale=pop(1.6), **P))
    L.append(shape("Group Head", [
        obj("Shower Screen", rect([210, 12], [0, 44]), C["steelDark"], w=3),
        G("Shine", path([(-110, -24), (100, -24)]), stroke("#FFFFFF", 7, 55)),
        obj("Block", rect([280, 100], None, 18), C["steel"]),
    ], [1470, 440], 1.6, D, scale=pop(1.6), **P))
    L.append(text("Label Group", "GROUP HEAD", [1470, 355], 22, C["tealLight"], 1.8, D, tracking=150, opacity=fade_in(1.8), **P))
    # --- boiler
    for j, (bx, ph) in enumerate([(-90, 0), (-30, 50), (30, 20), (90, 80), (0, 110)]):
        L.append(shape(f"Bubble {j + 1}", [G("B", ell([18, 18]), stroke(C["waterLight"], 3))], [1000 + bx, 640], 10.4, D,
                       position=X(f"[value[0] + Math.sin(time * 4 + {j}) * 6, 640 - ((time * 90 + {ph}) % 190)]"), opacity=fade_in(10.4), **P))
    L.append(shape("Heating Coil", [
        G("Glow", path([(-120, 0), (-90, -20), (-60, 20), (-30, -20), (0, 20), (30, -20), (60, 20), (90, -20), (120, 0)]),
          stroke(C["glow"], 22, A(K(9.8, 0), K(10.8, 45)))),
        G("Coil", path([(-120, 0), (-90, -20), (-60, 20), (-30, -20), (0, 20), (30, -20), (60, 20), (90, -20), (120, 0)]),
          stroke(A(K(9.8, C["steelMid"]), K(10.8, C["red"])), 9), stroke(INK, 15)),
    ], [1000, 640], 1.1, D, scale=pop(1.1), **P))
    L.append(shape("Boiler Water", [
        G("Shine", path([(-110, -100), (60, -100)]), stroke(C["waterLight"], 6, 60)),
        G("Water", rect([258, 220], None, 30), fill(A(K(10.0, C["water"]), K(12.4, C["red"])), 80)),
    ], [1000, 560], 1.1, D, scale=pop(1.1), **P))
    L.append(shape("Boiler", [
        G("Window", rect([262, 240], [0, 30], 34), fill("#1A2326")),
        G("Rivets", *[ell([10, 10], [x, -140]) for x in range(-120, 121, 40)], fill(C["copperDark"])),
        G("Shine", path([(-140, -80), (-140, 100)]), stroke(C["copperLight"], 10, 70)),
        obj("Shell", rect([320, 330], None, 56), C["copper"]),
    ], [1000, 525], 1.1, D, scale=pop(1.1), **P))
    L.append(text("Label Boiler", "BOILER", [1000, 735], 22, C["tealLight"], 1.3, D, tracking=150, opacity=fade_in(1.3), **P))
    L.append(text("Temp Readout", "93 °C", [1190, 380], 46, C["glow"], 11.6, D, font=TITLE, just="left", opacity=fade_in(11.6),
                  position=slide(11.6, [1190, 380], dx=-20, dy=0), **P))
    # --- gauge
    L += gauge("Gauge", [1000, 252], 1.2, D, A(K(7.6, BAR(0)), K(8.6, BAR(9.6)), KS(9.0, BAR(9))), size=126, parent=cam)
    L.append(text("Gauge Readout", "9 bar", [1080, 268], 46, C["mustard"], 8.4, D, font=TITLE, just="left", opacity=fade_in(8.4), **P))
    # --- pump
    L.append(shape("Pump Rotor", [obj("Hub", ell([32, 32]), C["steelMid"], w=3),
                                  G("Vanes", rect([118, 18], None, 9), rect([18, 118], None, 9), fill(C["steelDark"]))],
                   [640, 770], 0.8, D, scale=pop(0.8), rotation=X("time < 5.6 ? 0 : (time - 5.6) * 540"), **P))
    L.append(shape("Pump", [G("Window", ell([132, 132]), fill("#1A2326")), obj("Body", ell([170, 170]), C["steel"]),
                            obj("Motor", rect([120, 90], [0, 90], 16), C["steelDark"])], [640, 770], 0.8, D, scale=pop(0.8), **P))
    L.append(text("Label Pump", "PUMP", [520, 870], 22, C["tealLight"], 1.0, D, tracking=150, opacity=fade_in(1.0), **P))
    # --- tank
    L.append(shape("Tank Water", [G("Shine", path([(-80, -290), (60, -290)]), stroke(C["waterLight"], 6, 70)),
                                  G("Water", rect([196, 300], [0, -150], 14), fill(C["water"], 85))],
                   [280, 740], 0.5, D, scale=A(K(0.5, [100, 0]), K(1.2, [100, 100]), KS(3.2, [100, 100]), KS(21, [100, 74])), **P))
    L.append(shape("Tank", [G("Glare", path([(-80, -150), (-80, 120)]), stroke("#FFFFFF", 8, 25)),
                            obj("Lid", rect([240, 30], [0, -195], 10), C["steelMid"]),
                            obj("Shell", rect([220, 380], None, 26), "#2B4A52")], [280, 560], 0.5, D, scale=pop(0.5), **P))
    L.append(text("Label Tank", "WATER TANK", [280, 800], 22, C["tealLight"], 0.7, D, tracking=150, opacity=fade_in(0.7), **P))
    # --- pipes (under components)
    L += pipe_layers("P1", [(390, 700), (470, 700), (470, 770), (555, 770)], 0.4, D, flow=(2.4, 4.4), parent=cam)
    L += pipe_layers("P2", [(725, 770), (790, 770), (790, 600), (840, 600)], 0.4, D, flow=(6.0, 7.4), parent=cam)
    L += pipe_layers("P3", [(1160, 440), (1330, 440)], 0.4, D, flow=(13.6, 14.4), parent=cam, water=C["red"])
    L += pipe_layers("P4", [(1000, 315), (1000, 360)], 0.4, D, parent=cam)
    # blueprint grid + bg
    grid = [path([(x, -400), (x, 1500)]) for x in range(-480, 2400, 80)] + [path([(-500, y), (2400, y)]) for y in range(-400, 1500, 80)]
    L.append(shape("Grid", [G("Grid", *grid, stroke("#25393E", 2, cap="butt"))], [0, 0], 0, D, opacity=fade_in(0, 0.8), parent=cam))
    L += bg("#1C2B2F", D)
    return L

# =====================================================================
# MACHINE TYPES - art in local coords (parented to an "Art" null)
# =====================================================================
def art_lever(D, P):
    L = []
    pull, hold, rel, end = 1.6, 2.6, 3.3, 8.3
    py = A(K(0.6, [0, -40]), K(pull, [0, -40]), K(hold, [0, -230]), KS(rel, [0, -230]), K(end, [0, -40]))
    L += gauge("Lever Gauge", [-230, -170], 0.8, D, A(KL(rel, BAR(0)), K(rel + 0.3, BAR(9.2)), KS(end, BAR(6)), K(end + 0.4, BAR(0))), size=104,
               label="PRESSURE", parent=P)
    L.append(shape("Lever Arm", [obj("Knob", ell([58, 58], [235, 0]), C["handle"]),
                                 G("Shine", path([(20, -4), (200, -4)]), stroke("#FFFFFF", 4, 45)),
                                 G("Arm", path([(0, 0), (230, 0)]), stroke(C["steel"], 18), stroke(INK, 28)),
                                 obj("Pivot", ell([38, 38]), C["steelMid"])],
                   [60, -300], 0.6, D, parent=P, rotation=A(K(0.6, -32), K(pull, -32), K(hold, 34), KS(rel, 34), K(end, -32))))
    L.append(shape("Spring", [G("Spring", path(zigzag(9, 225, 72)), stroke(C["mustard"], 7), stroke(INK, 12))], [0, -285], 0.6, D, parent=P,
                   scale=A(K(0.6, [100, 100]), K(pull, [100, 100]), K(hold, [100, 20]), KS(rel, [100, 20]), K(end, [100, 100]))))
    L.append(shape("Piston", [obj("Piston", rect([104, 30], None, 8), C["steel"], w=4)], py, 0.6, D, parent=P))
    L.append(shape("Chamber Water", [G("Water", rect([104, 190], [0, -95]), fill(C["water"], 85))], [0, -5], 0.6, D, parent=P,
                   scale=A(K(0.6, [100, 4]), K(pull, [100, 4]), K(hold, [100, 100]), KS(rel, [100, 100]), K(end, [100, 4]))))
    L.append(shape("Housing", [G("Glare", path([(-40, -120), (-40, 110)]), stroke("#FFFFFF", 6, 25)),
                               obj("Cap", rect([150, 26], [0, -150], 8), C["steelMid"]),
                               G("Glass", rect([124, 290], None, 12), stroke(C["steel"], 7), fill("#1B2124", 90))], [0, -135], 0.6, D, scale=pop(0.6), parent=P))
    L += cup("Lever", 0, 235, 0.42, 0.9, D, scale=pop(0.9), fill_t=(rel + 0.5, end), parent=P)
    L.insert(len(L) - 1, tiger_stream("Lever Stream", 0, 140, 240, rel + 0.2, end - 0.2, D, w=8, parent=P))
    L.append(shape("Portafilter", [obj("Spout", path([(-10, 18), (10, 18), (7, 40), (-7, 40)], True), C["steelMid"], w=4),
                                   obj("Basket", path([(-90, -20), (90, -20), (76, 22), (-76, 22)], True), C["steel"]),
                                   obj("Handle", rect([190, 30], [-175, 2], 15), C["handle"])], [0, 100], 0.8, D, scale=pop(0.8), parent=P))
    L.append(shape("Group", [G("Shine", path([(-70, -30), (60, -30)]), stroke("#FFFFFF", 6, 55)), obj("Group", path([(-80, -50), (80, -50), (95, 55), (-95, 55)], True), C["steel"])],
                   [0, 30], 0.6, D, scale=pop(0.6), parent=P))
    L.append(shape("Frame", [obj("Base", rect([400, 44], [0, 355], 16), C["steelShadow"]),
                             obj("Post", rect([56, 600], [130, 60], 14), C["steelDark"])], [0, 0], 0.5, D, scale=pop(0.5), parent=P))
    return L, (rel, end)

def art_vibe(D, P):
    L = []
    on = 1.5
    osc = f"time > {on} ? Math.sin(time * Math.PI * 2 * 5) * 26 : 0"
    for j, ph in enumerate([0, 47, 93]):
        L.append(shape(f"Out Pulse {j + 1}", [obj("Drop", rect([30, 14], None, 7), C["water"], w=3)], [240, -40], on, D, parent=P,
                       position=X(f"[240 + ((time * 260 + {ph}) % 140), -40]")))
        L.append(shape(f"In Pulse {j + 1}", [obj("Drop", rect([30, 14], None, 7), C["water"], w=3)], [-380, -40], on, D, parent=P,
                       position=X(f"[-380 + ((time * 260 + {ph}) % 130), -40]")))
    arcs = [G(f"Arc {j}", path([(-30 - j * 22, 0), (0, -26 - j * 16), (30 + j * 22, 0)], False, i=[(0, 0), (-25 - j * 12, 0), (0, 0)], o=[(0, 0), (25 + j * 12, 0), (0, 0)]),
              stroke(C["mustard"], 6, X(f"time < {on} ? 0 : 50 + Math.sin(time * 30 + {j}) * 50"))) for j in range(3)]
    L.append(shape("Buzz Arcs", arcs, [-20, -150], 0.8, D, parent=P))
    L.append(text("Buzz", "BZZZ", [-20, -225], 30, C["mustard"], on, D, tracking=250, parent=P, opacity=X(f"time < {on} ? 0 : (Math.sin(time * 40) > 0 ? 100 : 40)")))
    L.append(shape("Return Spring", [G("Spring", path(zigzag(8, 165, 54, True)), stroke(C["cream"], 5), stroke(INK, 10))], [220, -40], 0.8, D, parent=P,
                   scale=X(f"[100 - ({osc}) / 165 * 100, 100]")))
    L.append(shape("Vibe Piston", [obj("Rod", rect([70, 20], [-105, 0], 6), C["steelMid"], w=4),
                                   G("Shine", path([(-55, -20), (50, -20)]), stroke("#FFFFFF", 5, 60)),
                                   obj("Piston", rect([140, 72], None, 12), C["steel"])], [-20, -40], 0.8, D, parent=P, position=X(f"[-20 + ({osc}), -40]")))
    for side, yy in [("Top", -112), ("Bottom", 32)]:
        L.append(shape(f"Coil {side}", [G("Windings", *[path([(dx, -14), (dx, 14)]) for dx in range(-90, 91, 15)], stroke(C["copperDark"], 4, cap="butt")),
                                        obj("Coil", rect([214, 30], None, 6), C["copper"])], [-30, yy], 0.7, D, scale=pop(0.7), parent=P))
    L.append(shape("Pump Tube", [G("Glare", path([(-200, -40), (200, -40)]), stroke("#FFFFFF", 5, 22)),
                                 G("Tube", rect([460, 130], None, 24), stroke(C["steel"], 7), fill("#1B2124", 90))], [0, -40], 0.6, D, scale=pop(0.6), parent=P))
    L += pipe_layers("Vibe Pipes", [(-385, -40), (-232, -40)], 0.6, D, parent=P) + pipe_layers("Vibe Out", [(232, -40), (385, -40)], 0.6, D, parent=P)
    L.append(text("Coil Label", "ELECTROMAGNET", [-30, 98], 20, C["muted"], 1.0, D, tracking=150, parent=P, opacity=fade_in(1.0)))
    L += gauge("Vibe Gauge", [0, 220], 1.0, D, X(f"time < {on} ? -135 : {BAR(9.6)} + Math.sin(time * 37) * 9"), size=104, label="PULSING PRESSURE", parent=P)
    return L, (on, 9.0)

def art_rotary(D, P):
    L = []
    on = 1.2
    spin = f"time < {on} ? 0 : (time - {on}) * 300"
    L.append(shape("Rotor", [obj("Hub", ell([40, 40]), C["steelDark"], w=4),
                             obj("Disc", ell([150, 150]), C["steel"]),
                             G("Vanes", rect([16, 212], None, 5), rect([212, 16], None, 5), stroke(INK, 3), fill(C["cream"]))],
                   [72, -40], 0.8, D, scale=pop(0.8), rotation=X(spin), parent=P))
    L.append(shape("Housing", [G("Water", ell([250, 250]), fill(C["waterDeep"])), obj("Ring", ell([290, 290]), C["steel"])], [95, -40], 0.6, D, scale=pop(0.6), parent=P))
    L.append(shape("Motor Fan", [G("Blades", rect([130, 18], None, 9), rect([18, 130], None, 9), fill(C["steelMid"]))], [-255, -40], 0.8, D,
                   scale=pop(0.8), rotation=X(spin), parent=P))
    L.append(shape("Shaft", [obj("Shaft", rect([110, 26], None, 6), C["steelMid"], w=4)], [-95, -40], 0.6, D, scale=pop(0.6), parent=P))
    L.append(shape("Motor", [obj("Face", ell([150, 150]), "#1B2124"),
                             G("Fins", *[path([(-110, y), (-90, y)]) for y in range(-70, 71, 20)], *[path([(90, y), (110, y)]) for y in range(-70, 71, 20)], stroke(INK, 6)),
                             obj("Body", rect([220, 200], None, 26), C["steelDark"])], [-255, -40], 0.6, D, scale=pop(0.6), parent=P))
    L += pipe_layers("Inlet", [(95, 230), (95, 108)], 0.6, D, flow=(on, on + 0.6), parent=P)
    L += pipe_layers("Outlet", [(95, -188), (95, -280), (330, -280)], 0.6, D, flow=(on + 0.4, on + 1.2), parent=P)
    L.append(text("Motor Label", "ELECTRIC MOTOR", [-255, 110], 20, C["muted"], 1.0, D, tracking=150, parent=P, opacity=fade_in(1.0)))
    L.append(text("Vane Label", "SPINNING VANES", [95, 270], 20, C["muted"], 1.0, D, tracking=150, parent=P, opacity=fade_in(1.0)))
    L += gauge("Rotary Gauge", [310, -40], 1.0, D, A(K(on, BAR(0)), K(on + 1.0, BAR(9))), size=104, label="STEADY 9 BAR", parent=P)
    return L, (on, 9.0)

def art_super(D, P):
    L = []
    press, g_on, g_off, pour = 1.1, 1.4, 4.4, 4.7
    for j, ph in enumerate([0, 0.33, 0.66]):
        L.append(shape(f"Falling Bean {j + 1}", [obj("Bean", ell([22, 30]), C["coffee"], w=3)], [0, -240], g_on, g_off, parent=P,
                       position=X(f"[{(j - 1) * 22}, -240 + ((time + {ph}) % 1) * 70]"), rotation=X(f"time * 200 + {j * 60}")))
    for j, ph in enumerate([0, 0.25, 0.5, 0.75]):
        L.append(shape(f"Grounds {j + 1}", [G("Dots", ell([8, 8], [-10, 0]), ell([8, 8], [12, 6]), ell([8, 8], [0, 12]), fill(C["caramel"]))],
                       [0, -110], g_on + 0.3, g_off, parent=P, position=X(f"[0, -112 + ((time + {ph}) % 1) * 40]")))
    teeth = [(round(math.cos(a) * r, 1), round(math.sin(a) * r, 1)) for q in range(16) for a, r in [(q / 16 * 2 * math.pi, 52 if q % 2 == 0 else 40)]]
    L.append(shape("Burr", [obj("Burr", path(teeth, True), C["steel"], w=4), obj("Hub", ell([24, 24]), C["steelDark"], w=3)], [0, -145], 0.8, D, scale=pop(0.8), parent=P,
                   rotation=X(f"time < {g_on} ? 0 : (time < {g_off} ? (time - {g_on}) * 500 : {(g_off - g_on) * 500})")))
    L.append(shape("Brew Unit", [obj("Brew", rect([140, 30], None, 8), C["esp"], w=4)], [0, -58], 0.8, D, scale=pop(0.8), parent=P))
    L.append(shape("Grinder Window", [G("Window", rect([280, 200], None, 22), fill("#1B2124"))], [0, -130], 0.7, D, scale=pop(0.7), parent=P))
    L.append(shape("Button Ring", [G("Ring", ell([60, 60]), stroke(C["mustard"], 4))], [0, 70], press, press + 0.8, parent=P,
                   scale=A(K(press, [100, 100]), K(press + 0.8, [230, 230])), opacity=A(K(press, 100), K(press + 0.8, 0))))
    L.append(shape("Button", [obj("Button", ell([54, 54]), C["mustard"], w=4)], [0, 70], 0.9, D, parent=P,
                   scale=A(K(0.9, [0, 0]), K(1.0, [100, 100]), K(press, [100, 100]), K(press + 0.1, [76, 76]), KS(press + 0.3, [100, 100]))))
    L.append(text("Display Text", "ESPRESSO", [0, 19], 20, C["water"], 0.9, D, tracking=150, parent=P, opacity=fade_in(0.9)))
    L.append(shape("Display", [obj("Display", rect([190, 46], None, 10), "#0F1A22", w=4)], [0, 11], 0.8, D, scale=pop(0.8), parent=P))
    L += cup("Super", 0, 250, 0.36, 0.9, D, scale=pop(0.9), fill_t=(pour + 0.3, 8.4), parent=P)
    L.insert(len(L) - 1, tiger_stream("Super Stream L", -12, 160, 255, pour, 8.2, D, w=6, parent=P))
    L.insert(len(L) - 1, tiger_stream("Super Stream R", 12, 160, 255, pour, 8.2, D, w=6, parent=P))
    L.append(shape("Spout", [obj("Spout", rect([74, 28], None, 8), C["steel"], w=4)], [0, 146], 0.8, D, scale=pop(0.8), parent=P))
    L.append(shape("Cup Bay", [G("Bay", rect([270, 200], None, 22), fill("#1B2124"))], [0, 225], 0.7, D, scale=pop(0.7), parent=P))
    L.append(shape("Hopper Beans", [G("Beans", *[ell([24, 32], [dx, dy]) for dx, dy in [(-50, 10), (-20, 18), (12, 8), (44, 16), (-34, -14), (0, -10), (30, -16)]],
                                      stroke(INK, 3), fill(C["coffee"]))], [0, -295], 0.8, D, scale=pop(0.8), parent=P))
    L.append(shape("Hopper", [obj("Lid", rect([250, 20], [0, -58], 8), C["steelDark"]),
                              obj("Hopper", path([(-115, -50), (115, -50), (70, 45), (-70, 45)], True), "#4A3A30")], [0, -290], 0.6, D, scale=pop(0.6), parent=P))
    L.append(shape("Machine Body", [G("Shine", path([(-170, -200), (-170, 250)]), stroke("#FFFFFF", 8, 18)),
                                    obj("Body", rect([410, 590], None, 44), C["steelDark"])], [0, 40], 0.5, D, scale=pop(0.5), parent=P))
    return L, (pour - 0.3, 8.4)

def art_capsule(D, P):
    L = []
    drop, close, flow = 0.9, 2.0, 3.0
    L.append(shape("Lid", [obj("Lid", rect([250, 30], [125, 0], 12), C["steel"])], [-125, -275], 0.6, D, parent=P,
                   rotation=A(K(0.6, -55), K(close - 0.5, -55), K(close, 0))))
    L.append(shape("Pierce Flash", [G("Flash", ell([90, 90]), stroke(C["mustard"], 5))], [0, -180], close, close + 0.6, parent=P,
                   scale=A(K(close, [40, 40]), K(close + 0.6, [190, 190])), opacity=A(K(close, 100), K(close + 0.6, 0))))
    L.append(shape("Capsule", [obj("Foil", rect([116, 14], [0, -30], 5), C["steel"], w=4),
                               G("Shine", path([(-30, -18), (-20, 18)]), stroke("#FFFFFF", 5, 50)),
                               obj("Cup", path([(-50, -26), (50, -26), (30, 30), (-30, 30)], True), C["red"])],
                   A(K(drop, [0, -480]), K(drop + 0.7, [0, -180])), drop, D, opacity=fade_in(drop, 0.2), parent=P))
    L.append(shape("Brew Chamber", [G("Chamber", rect([164, 116], None, 14), fill("#1B2124"))], [0, -170], 0.5, D, scale=pop(0.5), parent=P))
    feed = [(240, -180), (240, -310), (60, -310), (60, -292)]
    L += pipe_layers("Feed", feed, 0.5, D, flow=(flow, flow + 0.8), parent=P, water=C["red"], w=18)
    L.append(shape("Tank Water", [G("Water", rect([80, 300], [0, -150], 10), fill(C["water"], 80))], [240, 160], 0.5, D, parent=P,
                   scale=A(K(flow, [100, 100]), K(D, [100, 84]))))
    L.append(shape("Tank", [G("Glare", path([(-24, -140), (-24, 140)]), stroke("#FFFFFF", 6, 25)),
                            obj("Tank", rect([104, 344], None, 18), "#2B4A52")], [240, -5], 0.5, D, scale=pop(0.5), parent=P))
    L += cup("Capsule", 0, 235, 0.38, 0.9, D, scale=pop(0.9), fill_t=(flow + 1.2, 8.4), parent=P)
    L.insert(len(L) - 1, tiger_stream("Capsule Stream", 0, -80, 238, flow + 0.9, 8.2, D, w=9, parent=P))
    L.append(shape("Machine", [obj("Spout", rect([54, 32], [0, 85], 8), C["steelDark"], w=4),
                               G("Shine", path([(-120, -60), (100, -60)]), stroke("#FFFFFF", 7, 25)),
                               obj("Head", rect([310, 190], None, 34), C["steelShadow"]),
                               obj("Base", rect([320, 44], [0, 490], 14), C["handle"]),
                               obj("Column", rect([116, 520], [-97, 250], 22), C["steelShadow"])], [0, -180], 0.4, D, scale=pop(0.4), parent=P))
    L.append(text("Capsule Label", "SEALED CAPSULE", [-190, -330], 20, C["muted"], drop, D, tracking=150, parent=P, opacity=fade_in(drop)))
    return L, (flow, 8.4)

CURVES = {
    "lever": [(0, 0), (30, -128), (120, -122), (250, -104), (380, -90), (460, -84)],
    "vibe": [(0, 0), (40, -122)] + [(60 + q * 20, -128 + (9 if q % 2 else -9)) for q in range(21)],
    "rotary": [(0, 0), (40, -118), (70, -120), (460, -120)],
    "super": [(0, 0), (20, -36), (110, -38), (150, -118), (190, -120), (460, -120)],
    "capsule": [(0, 0), (30, -132)] + [(60 + q * 25, -136 + (4 if q % 2 else -4)) for q in range(17)],
}

TYPES = [
    dict(key="lever", comp="S5a_Lever", name="Lever", src="YOUR ARM OR A SPRING", bg="#3A1F1A", stage="#4E2B23",
         desc="Pull the lever down and a spring is loaded.\rLet go, and the spring presses the shot.",
         pros=["Silent and hands-on", "Gentle, falling pressure"], cons=["Takes practice", "Slower to work with"],
         found="classic cafe levers and manual home machines", art=art_lever),
    dict(key="vibe", comp="S5b_Vibratory", name="Vibratory pump", src="AN ELECTROMAGNET", bg="#173A3E", stage="#1F4C51",
         desc="A magnet snaps a tiny piston back and forth\r50-60 times a second, pushing water in pulses.",
         pros=["Compact and affordable", "Heats up fast"], cons=["Buzzy", "Pressure wobbles"],
         found="most home espresso machines", art=art_vibe),
    dict(key="rotary", comp="S5c_Rotary", name="Rotary pump", src="AN ELECTRIC MOTOR", bg="#1D2A3F", stage="#283A55",
         desc="A motor spins a vaned disc inside an off-centre\rchamber, sweeping water through smoothly.",
         pros=["Quiet, steady 9 bar", "Can plumb into mains water"], cons=["Bigger and pricier", "More to maintain"],
         found="cafes and high-end home setups", art=art_rotary),
    dict(key="super", comp="S5d_SuperAuto", name="Super-automatic", src="A BUILT-IN PUMP", bg="#2E2238", stage="#3F3050",
         desc="One button grinds, doses, tamps and brews,\rthen dumps the used puck for you.",
         pros=["One-touch convenience", "Very consistent"], cons=["Less control over taste", "Complex to repair"],
         found="offices and busy kitchens", art=art_super),
    dict(key="capsule", comp="S5e_Capsule", name="Capsule", src="A SMALL VIBRATORY PUMP", bg="#2F3320", stage="#41472C",
         desc="A sealed capsule of ground coffee is pierced\rand hot water is pumped straight through it.",
         pros=["Fast and mess-free", "Cheap machine"], cons=["Costly per cup", "Capsule waste"],
         found="kitchens that want coffee in seconds", art=art_capsule),
]

def type_scene(n, T, D=10.0):
    L = []
    P = "Art"
    x0 = 1030
    t = 0.3
    L.append(text("Number", f"0{n}", [x0 + 34, 262], 30, C["esp"], t + 0.1, D, font=TITLE, opacity=fade_in(t + 0.1)))
    L.append(shape("Number Disk", [G("D", ell([72, 72]), fill(C["mustard"]))], [x0 + 34, 252], t, D, scale=pop(t)))
    L.append(appear(text("Name", T["name"], [x0 + 96, 280], 76, C["cream"], t + 0.15, D, font=TITLE, just="left"), t + 0.15, dx=50, dy=0))
    label = "POWERED BY  " + T["src"]
    pw = len(label) * 15.2 + 48
    L.append(appear(text("Source", label, [x0 + 24, 359], 20, C["mustard"], t + 0.35, D, just="left", tracking=150), t + 0.35, dx=40, dy=0))
    L.append(shape("Source Pill", [G("Pill", rect([pw, 44], [pw / 2, 0], 22), stroke(C["mustard"], 2.5), fill(C["mustard"], 12))],
                   [x0, 352], t + 0.3, D, scale=A(K(t + 0.3, [0, 100]), K(t + 0.8, [100, 100]))))
    L.append(appear(text("Description", T["desc"], [x0, 445], 30, C["cream"], t + 0.6, D, just="left", font=SANS, leading=42), t + 0.6, dx=40, dy=0))
    # pressure chart
    ox, oy = x0 + 70, 740
    art_layers, (s0, s1) = T["art"](D, P)
    pts = CURVES[T["key"]]
    L.append(text("Chart Title", "PRESSURE DURING THE SHOT", [x0, 566], 18, C["muted"], 1.0, D, just="left", tracking=200, opacity=fade_in(1.0)))
    L.append(text("Chart 9", "9 bar", [ox - 14, oy - 114], 20, C["muted"], 1.1, D, just="right", font=SANS, opacity=fade_in(1.1)))
    L.append(text("Chart Time", "time", [ox + 470, oy + 30], 20, C["muted"], 1.1, D, just="right", font=SANS_B, opacity=fade_in(1.1)))
    L.append(shape("Chart", [
        G("Curve", smooth(pts), trim(0, A(K(s0, 0, "easeInOut"), K(s1, 100, "easeInOut"))), stroke(C["mustard"], 6)),
        G("Ref", path([(0, -120), (470, -120)]), stroke(C["cream"], 2, 25, cap="butt")),
        G("Axes", path([(0, -160), (0, 0), (480, 0)]), trim(0, A(K(1.0, 0), K(1.6, 100))), stroke(C["cream"], 3, 55)),
    ], [ox, oy], 1.0, D))
    # pros / cons
    rows = [(T["pros"][0], True, 0), (T["cons"][0], False, 1), (T["pros"][1], True, 0), (T["cons"][1], False, 1)]
    for j, (s, good, col) in enumerate(rows):
        tt = 1.6 + j * 0.2
        x, y = x0 + col * 420, 832 + (j // 2) * 50
        L.append(appear(text(f"Point {j + 1}", s, [x + 30, y + 9], 26, C["cream"], tt, D, just="left", font=SANS), tt, dx=30, dy=0))
        L.append(check_icon([x + 6, y], good, tt, D, f"Icon {j + 1}"))
    L.append(appear(text("Found In", "Found in " + T["found"], [x0, 965], 22, C["muted"], 2.6, D, just="left", font=SERIF_I), 2.6, dx=30, dy=0))
    # art + stage
    L.append(null(P, [540, 560], 0, D))
    if T["key"] == "vibe":
        L[-1]["transform"]["position"] = {"value": [540, 560],
                                          "expression": "var a = time > 1.5 ? 1 : 0; [value[0] + Math.sin(time * 95) * 2.5 * a, value[1] + Math.cos(time * 83) * 2 * a]"}
    L += art_layers
    L.append(shape("Stage Ring", [G("Ring", ell([760, 760]), trim(0, 72, X("time * 25")), stroke(C["cream"], 3, 25))], [540, 560], 0.2, D,
                   scale=pop(0.2, 100, 0.8)))
    L.append(shape("Stage", [G("Stage", ell([680, 680]), fill(T["stage"]))], [540, 560], 0.0, D, scale=pop(0.0, 100, 0.7)))
    L.append(particles("Specks", 24, (0, 0, 1920, 1080), C["cream"], 0, D, 30 + n, op=10))
    L += bg(T["bg"], D)
    return L

# ---------- icons (one layer each) ----------
def icon(key, name, pos, t0, t1, **tr):
    g = {
        "lever": [obj("Knob", ell([30, 30], [86, -96]), C["handle"], w=4), G("Arm", path([(20, -64), (86, -96)]), stroke(C["steel"], 12), stroke(INK, 20)),
                  obj("Housing", rect([50, 100], [0, -24], 8), C["steel"], w=4), obj("Group", rect([80, 34], [0, 44], 8), C["steelMid"], w=4),
                  obj("Base", rect([130, 16], [0, 96], 6), C["steelDark"], w=4)],
        "vibe": [G("Spring", path(zigzag(5, 50, 26, True)), stroke(C["cream"], 4)), obj("Coil", rect([70, 70], [-24, 0], 8), C["copper"], w=4),
                 obj("Tube", rect([160, 50], None, 14), C["steelDark"], w=4)],
        "rotary": [G("Vanes", rect([10, 110], None, 4), rect([110, 10], None, 4), fill(C["cream"])), obj("Disc", ell([80, 80], [-8, 0]), C["steel"], w=4),
                   obj("Housing", ell([130, 130]), C["waterDeep"], w=5)],
        "super": [obj("Hopper", path([(-46, -100), (46, -100), (30, -66), (-30, -66)], True), C["coffee"], w=4), obj("Button", ell([20, 20], [0, -12]), C["mustard"], w=3),
                  obj("Bay", rect([80, 54], [0, 40], 10), "#1B2124", w=4), obj("Body", rect([130, 170], [0, 2], 20), C["steelDark"], w=5)],
        "capsule": [obj("Foil", rect([118, 16], [0, -40], 6), C["steel"], w=4), obj("Cup", path([(-54, -34), (54, -34), (32, 40), (-32, 40)], True), C["red"], w=5)],
    }[key]
    return shape(name, g, pos, t0, t1, **tr)

ORDER = ["lever", "vibe", "rotary", "super", "capsule"]
NAMES = {"lever": "LEVER", "vibe": "VIBRATORY", "rotary": "ROTARY", "super": "SUPER-AUTO", "capsule": "CAPSULE"}

def s5_intro(D):
    L = [appear(text("Intro Title", "Same goal, five ways to get there", [960, 300], 64, C["cream"], 0.2, D, font=TITLE), 0.2)]
    for j, k in enumerate(ORDER):
        x, t = 360 + j * 300, 0.7 + j * 0.15
        L.append(text(f"Intro Label {j + 1}", NAMES[k], [x, 720], 22, C["muted"], t + 0.3, D, tracking=150, opacity=fade_in(t + 0.3)))
        L.append(icon(k, f"Intro Icon {j + 1}", [x, 560], t, D, scale=pop(t),
                      rotation=X(f"Math.sin(time * 2 + {j}) * 3")))
        L.append(shape(f"Intro Disk {j + 1}", [G("D", ell([220, 220]), fill(C["roast3"]))], [x, 560], t - 0.1, D, scale=pop(t - 0.1)))
    L.append(particles("Specks", 24, (0, 0, 1920, 1080), C["cremaLight"], 0, D, 77, op=14))
    L += bg(C["roast"], D, [shape("Spot", [G("O", ell([1600, 900]), fill(C["roast2"]))], [960, 560], 0, D, scale=pop(0, 100, 0.8))])
    return L

# =====================================================================
# SCENE 6 - CONTROL vs CONVENIENCE MAP (11 s)
# =====================================================================
def s6_map(D):
    L = []
    ox, oy, ex, ey = 300, 900, 1720, 230
    L.append(appear(text("Map Title", "Every machine trades convenience for control", [960, 130], 54, INK, 0.2, D, font=TITLE), 0.2))
    L.append(text("Axis X", "HANDS-ON CONTROL", [ex, oy + 60], 24, C["redDark"], 1.0, D, just="right", tracking=200, opacity=fade_in(1.0)))
    L.append(text("Axis Y", "CONVENIENCE", [ox - 30, ey - 28], 24, C["redDark"], 1.0, D, just="left", tracking=200, opacity=fade_in(1.0)))
    L.append(shape("Axes", [
        G("Arrow X", path([(ex - 18, oy - 12), (ex, oy), (ex - 18, oy + 12)]), stroke(INK, 5), tr={"opacity": fade_in(1.2, 0.2)}),
        G("Arrow Y", path([(ox - 12, ey + 18), (ox, ey), (ox + 12, ey + 18)]), stroke(INK, 5), tr={"opacity": fade_in(1.0, 0.2)}),
        G("Axes", path([(ox, ey), (ox, oy), (ex, oy)]), trim(0, A(K(0.5, 0), K(1.3, 100))), stroke(INK, 5)),
    ], [0, 0], 0.5, D))
    band = (shape("Trade-off", [G("Band", path([(420, 330), (1600, 790)]), trim(0, A(K(1.4, 0), K(2.4, 100))), stroke(C["mustard"], 70, 30))],
                   [0, 0], 1.4, D))
    spots = {"capsule": (500, 330), "super": (760, 400), "vibe": (1020, 560), "rotary": (1290, 650), "lever": (1550, 750)}
    for j, k in enumerate(["capsule", "super", "vibe", "rotary", "lever"]):
        x, y = spots[k]
        t = 2.4 + j * 0.45
        L.append(text(f"Map Label {k}", NAMES[k], [x, y + 112], 22, INK, t + 0.3, D, tracking=150, opacity=fade_in(t + 0.3)))
        L.append(icon(k, f"Map Icon {k}", [x, y], t, D, scale=pop(t, 80), rotation=X(f"Math.sin(time * 2 + {j}) * 3")))
        L.append(shape(f"Map Disk {k}", [G("D", ell([180, 180]), fill(C["paper2"])), G("R", ell([180, 180]), stroke(INK, 4))], [x, y], t - 0.1, D, scale=pop(t - 0.1, 80)))
    L.append(band)
    L.append(particles("Paper Specks", 40, (0, 0, 1920, 1080), INK, 0, D, 8, size=(2, 5), speed=6, op=12))
    L += bg(C["sepia"], D)
    return L

# =====================================================================
# SCENE 7 - OUTRO (9 s)
# =====================================================================
def s7_outro(D):
    L = [
        appear(text("Outro Small", "Enjoy your next espresso.", [960, 290], 34, C["muted"], 3.2, D, font=SERIF_I), 3.2),
        appear(text("Outro Title", "Different machines.\rThe same tiny miracle.", [960, 120], 70, C["cream"], 2.4, D, font=TITLE, leading=82), 2.4),
    ]
    for j, (big, small, (x, y)) in enumerate([("9 bar", "PRESSURE", (620, 870)), ("93 °C", "WATER", (960, 900)), ("25 s", "TIME", (1300, 870))]):
        t = 0.8 + j * 0.3
        L.append(text(f"Badge {j + 1} Small", small, [0, 32], 18, C["esp"], t + 0.2, D, tracking=150, opacity=fade_in(t + 0.2), parent=f"Badge {j + 1}"))
        L.append(text(f"Badge {j + 1} Big", big, [0, 8], 40, C["esp"], t + 0.2, D, font=TITLE, opacity=fade_in(t + 0.2), parent=f"Badge {j + 1}"))
        L.append(shape(f"Badge {j + 1}", [G("B", ell([170, 170]), fill(C["mustard"])), G("R", ell([186, 186]), stroke(C["mustard"], 3, 50))],
                       [x, y], t, D, scale=pop(t), position=X(f"[value[0], value[1] + Math.sin(time * 1.6 + {j}) * 8]")))
    L += cup("Outro", 960, 560, 0.8, 0.2, D, scale=pop(0.2), steam_t=0.6)
    L.append(particles("Dust", 26, (0, 0, 1920, 1080), C["cremaLight"], 0, D, 13, speed=14, op=16))
    L += bg(C["roast"], D, [shape("Spot", [G("Inner", ell([760, 760]), fill(C["roast3"], 60)), G("Outer", ell([1300, 1300]), fill(C["roast2"]))],
                                  [960, 640], 0, D, scale=pop(0, 100, 0.8))])
    return L

# =====================================================================
# MAIN
# =====================================================================
def band_wipe(name, b, col, lag):
    verts = [(-1900, -700), (2200, -700), (1900, 700), (-2200, 700)]
    t0, t1 = b - 0.6 + lag, b + 0.6 + lag
    return shape(name, [G("Band", path(verts, True), fill(col))], A(K(t0, [-2200, 540], "easeInOut"), K(t1, [4120, 540], "easeInOut")), t0, t1)

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

def build():
    scenes = [("S1_Hook", 12.0, s1_hook), ("S2_WhyPressure", 13.0, s2_pressure), ("S3_History", 18.0, s3_history),
              ("S4_Inside", 25.0, s4_inside), ("S5_TypesIntro", 4.5, s5_intro)]
    for n, T in enumerate(TYPES):
        scenes.append((T["comp"], 10.0, lambda D, n=n, T=T: type_scene(n + 1, T, D)))
    scenes += [("S6_Map", 11.0, s6_map), ("S7_Outro", 9.0, s7_outro)]
    comps, main, wipes = [], [], []
    t = 0.0
    for idx, (cname, d, fn) in enumerate(scenes):
        layers = fn(d)
        names = [l["name"] for l in layers]
        assert len(names) == len(set(names)), (cname, [n for n in names if names.count(n) > 1])
        missing = [(l["name"], l["parent"]) for l in layers if l.get("parent") and l["parent"] not in names]
        assert not missing, (cname, "parent not found", missing)
        comps.append({"name": cname, "width": W, "height": H, "fps": FPS, "duration": d, "backgroundColor": "#000000", "layers": layers})
        L = {"name": cname, "type": "precomp", "source": cname, "startTime": t, "in": t, "out": t + d,
             "transform": {"scale": A(KS(t, [100, 100]), KS(t + d, [103, 103]))}}
        if idx == len(scenes) - 1:
            L["transform"]["opacity"] = A(K(t + d - 1.2, 100), K(t + d, 0))
        main.insert(0, L)
        if idx:
            wipes += [band_wipe(f"Wipe {idx} A", t, C["mustard"], -0.08), band_wipe(f"Wipe {idx} B", t, C["cream"], 0.08)]
        t += d
    total = t
    grain = {"name": "Film Grain", "type": "adjustment", "in": 0, "out": total,
             "effects": [{"matchName": "ADBE Noise", "props": {"ADBE Noise-0001": 3.5}}]}
    main_comp = {"name": "Espresso_Explainer", "width": W, "height": H, "fps": FPS, "duration": total, "backgroundColor": "#000000",
                 "layers": [grain] + wipes[::-1] + main}
    return {"$schema": "../motion.schema.json", "file": "espresso_explainer.aep", "expressionEngine": "javascript-1.0",
            "bitDepth": "8 bpc", "compositions": [main_comp] + comps}, scenes

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "espresso_explainer.json")
    proj, scenes = build()
    zero_tangents(proj)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(proj, f, indent=1, ensure_ascii=False)
    t = 0
    for c, d, _ in scenes:
        print(f"{t:6.1f}  {c}")
        t += d
    print("total", t)
