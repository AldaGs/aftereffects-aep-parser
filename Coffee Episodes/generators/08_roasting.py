"""Generator for episode 8, "What Roasting Really Does" (scripts/08_roasting_script.md).

    python "Coffee Episodes/generators/08_roasting.py"      # writes ../json/08_roasting.json

Every scene hangs off one camera null (cam): content point q sits on screen at c with zoom z, and the master
push-in is cancelled inside the expression, so content coordinates are screen pixels and every match cut is
exact without handoff maths. No fades: cut_pass turns exits into cuts or pops.
"""
import math, random

from coffee_common import *  # noqa: F401,F403

C = (CX, CY)


def cam(D, states=None, name="Cam"):
    """states [(t, q, c, z)]: content point q on screen at c, zoom z; eased between states, master push-in cancelled."""
    states = states or [(0, C, C, 1)]
    t, q, c, z = states[0]
    e = f"var k = 1 + {HS - 1:.4f} * time / {D}; var qx = {q[0]}, qy = {q[1]}, cx = {c[0]}, cy = {c[1]}, lz = {math.log(z):.5f}; "
    for (t0, q0, c0, z0), (t1, q1, c1, z1) in zip(states, states[1:]):
        e += (f"if (time > {t0}) {{ {u_expr(t0, t1)}qx = {q0[0]} + ({q1[0] - q0[0]:.2f}) * u; qy = {q0[1]} + ({q1[1] - q0[1]:.2f}) * u; "
              f"cx = {c0[0]} + ({c1[0] - c0[0]:.2f}) * u; cy = {c0[1]} + ({c1[1] - c0[1]:.2f}) * u; "
              f"lz = {math.log(z0):.5f} + ({math.log(z1) - math.log(z0):.5f}) * u; }} ")
    pos = X(e + f"var z = Math.exp(lz); [{CX} + (cx - qx * z - {CX}) / k, {CY} + (cy - qy * z - {CY}) / k]")
    sc = X(e + "var s = Math.exp(lz) / k * 100; [s, s]")
    return null(name, [0, 0], 0, D, anchor=[0, 0], position=dict(pos, value=[0, 0]), scale=dict(sc, value=[100, 100]))


def finish(L, D, states=None):
    parent_all(L, "Cam")
    return L + [cam(D, states), bg(D)]


def tag(name, s, pos, t, t1, size=16, color=INK, just="center", **tr):
    return appear(caps(name, s, pos, t, t1, size=size, color=color, just=just, **tr), t)


def arrow(name, a, b, t, t1, col=INK, w=4):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    hd = [(b[0] - 16 * math.cos(ang - 0.5), b[1] - 16 * math.sin(ang - 0.5)), b, (b[0] - 16 * math.cos(ang + 0.5), b[1] - 16 * math.sin(ang + 0.5))]
    return shape(name, [G("A", path([a, b]), path(hd), trim(0, A(K(t, 0), K(t + 0.5, 100))), stroke(col, w))], [0, 0], t, t1)


# ---------------------------------------------------------------------
# molecules and small art
# ---------------------------------------------------------------------
def hexpath(r, x=0, y=0):
    return path([(x + r * math.cos(math.radians(60 * k + 30)), y + r * math.sin(math.radians(60 * k + 30))) for k in range(6)], True)


def honeycomb(r, w, h, lw):
    """Pointy-top hex grid with a cell centred on the origin, clipped to a w x h ellipse."""
    ps = []
    for j in range(-int(h / r), int(h / r) + 1):
        for i in range(-int(w / r), int(w / r) + 1):
            x, y = (i + (j % 2) * 0.5) * r * math.sqrt(3), j * r * 1.5
            if (x / (w / 2)) ** 2 + (y / (h / 2)) ** 2 < 0.8:
                ps.append(hexpath(r, x, y))
    return G("Cells", *ps, stroke(INK, lw))


def bean(name, pos, w, col, t0, t1, crease=True, cells_r=None, cells_t=None, gloss_t=None, **tr):
    h = w * 0.7
    items = []
    if gloss_t is not None:
        items.append(G("Gloss", ell([w * 0.22, h * 0.12], [-w * 0.18, -h * 0.26]), *[ell([w * 0.05, w * 0.05], [x * w, y * h]) for x, y in ((0.2, -0.2), (0.1, 0.25), (-0.25, 0.15))],
                       fill(WHITE, 70), tr={"opacity": fade_in(gloss_t)}))
    if crease:
        items.append(G("Crease", path([(-w * 0.38, 0), (w * 0.38, 0)], False, i=[(0, 0), (-w * 0.2, -h * 0.12)], o=[(w * 0.2, h * 0.12), (0, 0)]),
                       stroke(INK, max(2, w * 0.022), 55)))
    if cells_r:
        g = honeycomb(cells_r, w, h, max(0.1, w * 0.004) if cells_r < 10 else 2)
        if cells_t is not None:
            g["transform"] = {"opacity": fade_in(cells_t)}
        items.append(g)
    items.append(G("Body", ell([w, h]), stroke(INK, max(2, w * 0.008)), fill(col)))
    return shape(name, items, pos, t0, t1, **tr)


def sugar(name, pos, t0, t1, r=40, broken=None, **tr):
    """White hexagon. broken: time it falls apart (edges fly out, face cut)."""
    if broken is None:
        return shape(name, [G("Hex", hexpath(r), stroke(INK, max(2, r * 0.08)), fill(WHITE))], pos, t0, t1, **tr)
    vs = [(r * math.cos(math.radians(60 * k + 30)), r * math.sin(math.radians(60 * k + 30))) for k in range(7)]
    edges = []
    for k in range(6):
        a, b = vs[k], vs[k + 1]
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        edges.append(G(f"Edge {k + 1}", path([a, b]), stroke(INK, max(2, r * 0.08)),
                       tr={"position": A(K(broken, [0, 0]), K(broken + 0.7, [mx * 1.2, my * 1.2])), "rotation": A(K(broken, 0), K(broken + 0.7, 40 * (-1) ** k))}))
    return shape(name, edges + [G("Face", hexpath(r), fill(WHITE), tr={"opacity": A(K(broken, 100), K(broken + 0.1, 0))})], pos, t0, min(t1, broken + 0.9), **tr)


def amino(name, pos, t0, t1, col=INK, **tr):
    z = [(-50, 0), (-25, -16), (0, 0), (25, -16), (50, 0)]
    return shape(name, [G("Z", path(z), stroke(col, 5)), G("End", ell([16, 16], [58, 0]), fill(col))], pos, t0, t1, **tr)


def aroma(name, pos, t0, t1, s=100, col=INK, **tr):
    at = [(-22, 8), (0, -10), (22, 8), (0, 28)]
    items = [G(f"A{j + 1}", ell([14, 14], list(p)), stroke(col, 3), fill(WHITE)) for j, p in enumerate(at)]
    items.append(G("Bonds", path([at[0], at[1], at[2]]), path([at[1], at[3]]), stroke(col, 3)))
    return shape(name, items, pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)


def coil(name, pos, t0, t1, col=ROAST[3], s=100, drawn=False, **tr):
    pts = [((6 + 5 * a) * math.cos(a), (6 + 5 * a) * math.sin(a)) for a in [j * 0.35 for j in range(36)]]
    tm = [] if drawn else [trim(0, A(K(t0, 0), K(t0 + 0.8, 100)))]
    return shape(name, [G("Coil", path(pts), *tm, stroke(col, 7))], pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)


def sound(name, pos, t0, t1, s=100, rate=12):
    arcs = [arc((20 + 18 * j, -24 - 14 * j), (20 + 18 * j, 24 + 14 * j), -0.35) for j in range(3)]
    return shape(name, [G("Waves", *arcs, stroke(INK, 4))], pos, t0, t1,
                 scale=X(f"var p = {s} * (1 + 0.12 * Math.sin(time * {rate})); [p, p]"))


def gauge(name, pos, t0, t1, rot):
    return shape(name, [G("Needle", path([(0, 0), (0, -52)]), stroke(INK, 5), tr={"rotation": rot}),
                        G("Dial", path([(-60, 0), (60, 0)], False, i=[(0, 0), (0, -80)], o=[(0, -80), (0, 0)]), stroke(INK, 4))], pos, t0, t1, scale=grow(t0))


def cup(name, pos, t0, t1):
    return shape(name, [G("Handle", ell([22, 26], [34, -6]), stroke(INK, 4)),
                        G("Cup", path([(-30, -24), (30, -24), (22, 20), (-22, 20)], True), stroke(INK, 4), fill(WHITE))], pos, t0, t1, scale=grow(t0))


def clock(name, pos, t0, t1):
    return shape(name, [G("Hand", path([(0, 0), (0, -24)]), stroke(INK, 4), tr={"rotation": X(f"(time - {t0}) * 30")}),
                        G("Face", ell([64, 64]), stroke(INK, 4), fill(WHITE))], pos, t0, t1, scale=grow(t0))


# ---------------------------------------------------------------------
# the drum and the bag (S1, S8, S9, S10)
# ---------------------------------------------------------------------
DRUM, DR = (540, 560), 200
BAG = (1380, 560)
NOTES = "CARAMELO, CACAO"
NOTES_Y = 650


def drum(t0, t1, col=ROAST[3], pour_t=None, label_t=None):
    """Ink cut-away drum roaster at the left third; beans tumble inside. pour_t: sugar pours in and glazes the beans."""
    rnd = random.Random(8)
    out = []
    if pour_t is not None:
        for j in range(8):
            t = pour_t + j * 0.25
            x = DRUM[0] + rnd.uniform(-30, 30)
            out.append(sugar(f"Crystal {j + 1}", [x, 120], t, t + 0.9, r=12, position=A(KL(t, [x, 120]), KL(t + 0.9, [x, DRUM[1] + 60]))))
        g = pour_t + 2.4
        col = A(K(g, col), K(g + 1.0, INK))
    bs = []
    for j in range(14):
        a, r = rnd.uniform(0.15, 0.85) * math.pi, rnd.uniform(60, 160)
        p = [round(r * math.cos(a), 1), round(r * math.sin(a), 1)]
        bs.append(G(f"Bean {j + 1}", path([(-14, 0), (14, 0)]), stroke(INK, 2, 50), tr={"position": p, "rotation": rnd.uniform(0, 180)}))
        bs.append(G(f"Bean {j + 1} Body", ell([44, 30]), stroke(INK, 2), fill(col), tr={"position": p, "rotation": bs[-1]["transform"]["rotation"]}))
    out.append(shape("Drum Beans", [G("Tumble", *bs, tr={"rotation": X("time * 45")})], list(DRUM), t0, t1))
    out.append(shape("Drum", [G("Hopper", path([(-90, -290), (-36, -205), (36, -205), (90, -290)]), stroke(INK, 6)),
                              G("Legs", path([(-140, 140), (-170, 240)]), path([(140, 140), (170, 240)]), path([(-190, 240), (190, 240)]), stroke(INK, 6)),
                              G("Shell", ell([DR * 2, DR * 2]), stroke(INK, 6), fill(WHITE))], list(DRUM), t0, t1, scale=grow(t0)))
    if label_t is not None:
        out.insert(0, tag("Drum Label", "TOSTADO CON AZÚCAR · MÉXICO", [DRUM[0], 850], label_t, t1))
    return out


def bag(t0, t1, swipe_t=None, slide_t=None):
    x, y = BAG
    out = [text("Bag Name", "VERACRUZ", [x, 470], 42, INK, t0, t1, font=HEAD),
           caps("Bag Sub", "TUESTE MEDIO", [x, 512], t0, t1, size=16, color=INK),
           text("Bag Notes", NOTES, [x, NOTES_Y], 22, INK, t0, t1, font=LAB)]
    if swipe_t is not None:
        out.append(word_marker("Bag Swipe", NOTES, "CARAMELO", x, NOTES_Y, 22, swipe_t, t1, font=LAB))
    out.append(shape("Bag", [G("Crimp", rect([340, 34], [0, -243]), stroke(INK, 4)),
                             G("Body", rect([340, 520], None, 8), stroke(INK, 4), fill(KRAFT))], [x, y], t0, t1))
    if slide_t is not None:
        for l in out:
            p = l["transform"]["position"]
            l["transform"]["position"] = A(K(slide_t, [p[0] + 700, p[1]]), K(slide_t + 0.8, p))
    return out


# ---------------------------------------------------------------------
# the roast curve (S3, S5, S6, S7, S9)
# ---------------------------------------------------------------------
TS = [25, 60, 95, 120, 138, 150, 160, 170, 180, 188, 196, 206, 215, 222, 228]   # bean temperature at each minute
RAMP_T = [25, 160, 196, 215, 228]
DOT_W = 60
M_YELLOW, M_FC, M_DEV, M_SC = 6.0, 10.0, 12.0, 13.5


def T_at(m):
    i = min(int(m), len(TS) - 2)
    u = m - i
    p0, p1, p2, p3 = TS[max(i - 1, 0)], TS[i], TS[i + 1], TS[min(i + 2, len(TS) - 1)]
    return 0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


def cxy(m, T=None):
    return (240 + 100 * m, 860 - 2.6 * (T_at(m) if T is None else T))


SAMPLES = [cxy(j / 10) for j in range(141)]
_LEN = [0.0]
for a, b in zip(SAMPLES, SAMPLES[1:]):
    _LEN.append(_LEN[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))


def drawn(m):
    j = min(int(m * 10), 139)
    u = m * 10 - j
    return (_LEN[j] + (_LEN[j + 1] - _LEN[j]) * u) / _LEN[-1] * 100


def ramp(T):
    T = max(RAMP_T[0], min(RAMP_T[-1], T))
    j = max(i for i in range(4) if RAMP_T[i] <= T) if T < RAMP_T[-1] else 3
    u = (T - RAMP_T[j]) / (RAMP_T[j + 1] - RAMP_T[j])
    a, b = [int(ROAST[j][k:k + 2], 16) for k in (1, 3, 5)], [int(ROAST[j + 1][k:k + 2], 16) for k in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * u):02X}" for x, y in zip(a, b))


def ride(way, step=0.1):
    """[(t, m)] waypoints -> eased (t, m) samples."""
    out = []
    for (t0, m0), (t1, m1) in zip(way, way[1:]):
        n = max(1, int((t1 - t0) / step)) if m1 != m0 else 1
        for j in range(n):
            u = j / n
            out.append((t0 + (t1 - t0) * u, m0 + (m1 - m0) * u * u * (3 - 2 * u)))
    out.append(way[-1])
    return out


def curve(prefix, t0, t1, way, axes_t=None, dot_scale=None, cells_t=None):
    """Axes, the ink curve drawn up to the dot, and the bean-dot riding it. Returns layers top -> bottom."""
    s = ride(way)
    pos = A(*[KL(t, list(map(lambda v: round(v, 2), cxy(m)))) for t, m in s])
    col = A(*[KL(t, ramp(T_at(m))) for t, m in s])
    end = A(*[KL(t, round(drawn(m), 3)) for t, m in s])
    tr = {"scale": dot_scale} if dot_scale else {}
    out = [bean(f"{prefix}Dot", list(cxy(way[0][1])), DOT_W, col, t0, t1, crease=cells_t is None,
                cells_r=6 if cells_t is not None else None, cells_t=cells_t, position=pos, **tr),
           shape(f"{prefix}Curve", [G("C", path(SAMPLES), trim(0, end), stroke(INK, 5))], [0, 0], t0, t1)]
    at, lag = (axes_t, 0.3) if axes_t is not None else (t0, 0)
    tm = [trim(0, A(K(at, 0), K(at + 0.8, 100)))] if axes_t is not None else []
    out.append(shape(f"{prefix}Axes", [G("Y", path([(240, 860), (240, 210)]), *tm, stroke(INK, 3)),
                                       G("X", path([(240, 860), (1660, 860)]), *tm, stroke(INK, 3)),
                                       G("Ticks", *[path([(232, 860 - 2.6 * v), (240, 860 - 2.6 * v)]) for v in range(0, 251, 50)], stroke(INK, 3))],
                       [0, 0], at, t1))
    for v in range(0, 251, 50):
        out.append(caps(f"{prefix}Tick {v}", str(v), [222, 860 - 2.6 * v + 5], at + lag, t1, size=13, color=INK, just="right"))
    out.append(caps(f"{prefix}Y Title", "BEAN TEMPERATURE, °C", [240, 185], at + lag, t1, size=14, color=INK, just="left"))
    out.append(caps(f"{prefix}X Title", "TIME, 0 TO ≈ 14 MIN", [1660, 905], at + lag, t1, size=14, color=INK, just="right"))
    return out


# ---------------------------------------------------------------------
# the composition bar (S2, S7, S8)
# ---------------------------------------------------------------------
BX0, BW, BAR_Y, BH, WAT_Y = 240, 1440, 860, 56, 790
SEGS = [("CELL WALL", 50, SEED_LINE, 0), ("OIL", 15, KRAFT, 1), ("PROTEIN", 10, SEED, 0), ("SUGAR", 7, WHITE, 1),
        ("CHLOROGENIC ACIDS", 6, GREY2, 0), ("CAFFEINE", 1, CAF, 1), ("OTHER", 11, LINE, 2)]


def seg_x(k):
    return BX0 + BW * sum(p for _, p, _, _ in SEGS[:k]) / 100, BW * SEGS[k][1] / 100


def bar_layers(prefix, t, t1, grow_t=None, lift=None):
    """One layer per segment, drawn from its left edge. lift: {name: (t, dy)}."""
    out = []
    for k, (nm, p, col, _) in enumerate(SEGS):
        x0, w = seg_x(k)
        tr = {}
        if grow_t is not None:
            tr["scale"] = A(K(grow_t + k * 0.25, [0, 100]), K(grow_t + k * 0.25 + 0.3, [100, 100]))
        pos = [x0, BAR_Y]
        if lift and nm in lift:
            lt, dy = lift[nm]
            pos = A(K(lt, [x0, BAR_Y]), K(lt + 0.5, [x0, BAR_Y + dy]))
        out.append(shape(f"{prefix}Seg {nm}", [G("S", rect([w, BH], [w / 2, 0]), stroke(INK, 2), fill(col))], pos, t, t1, **tr))
    return out


def water_row(prefix, t, t1, frac=None):
    w = BW * 0.11
    sc = frac if frac is not None else A(K(t, [0, 100]), K(t + 0.5, [100, 100]))
    return [shape(f"{prefix}Water", [G("W", rect([w, 24], [w / 2, 0]), fill(WATER))], [BX0, WAT_Y], t, t1, scale=sc),
            shape(f"{prefix}Seed Outline", [G("O", rect([BW, 24], [BW / 2, 0]), stroke(INK, 2))], [BX0, WAT_Y], t, t1)]


# =====================================================================
# SCENE 1 - SUGAR IN THE DRUM (17 s)
# =====================================================================
def s1_drum(D):
    L = []
    b0, c0, g0 = 6.0, 12.0, 13.6
    L.append(tag("No Sugar", "NO SUGAR ADDED", [BAG[0], 170], b0 + 4.0, g0, size=16))
    L.append(shape("Cross", [G("X", path([(-26, -26), (26, 26)]), path([(26, -26), (-26, 26)]), stroke(ARA, 6))], [BAG[0] + 70, 230], b0 + 4.0, g0, scale=grow(b0 + 4.0)))
    L.append(shape("Bag Hex", [G("H", hexpath(36), stroke(INK, 3))], [BAG[0], 230], b0 + 3.6, g0, scale=grow(b0 + 3.6)))
    L.append(shape("Tick", [G("T", path([(-22, 0), (-6, 16), (24, -20)]), stroke(MX, 6))], [770, 240], b0 + 3.2, g0, scale=grow(b0 + 3.2)))
    L.append(sugar("Drum Hex", [700, 240], b0 + 3.0, g0, r=36, scale=grow(b0 + 3.0)))
    # C: a bean rolls out of the bag to centre and goes back along the ramp to the green seed
    L.append(bean("Bean", [BAG[0], 760], 520, A(K(g0 + 0.4, ROAST[3]), K(g0 + 1.0, ROAST[2]), K(g0 + 1.6, ROAST[1]), K(g0 + 2.4, ROAST[0])), c0, D,
                  position=A(K(c0, [BAG[0], 760]), K(g0, [CX, CY])), rotation=A(K(c0, -540), K(g0, 0)),
                  scale=A(K(c0, [11.5, 11.5]), K(g0, [11.5, 11.5]), K(g0 + 1.4, [100, 100]))))
    L += bag(b0, g0, swipe_t=b0 + 2.2, slide_t=b0)
    L += drum(0.2, g0, pour_t=1.4, label_t=4.8)
    for l in L:
        if l["out"] == g0:
            add_out(l, g0 - 0.3)
    return finish(L, D)


# =====================================================================
# SCENE 2 - WHAT'S IN A GREEN SEED (20 s)
# =====================================================================
START = cxy(0)


def s2_seed(D):
    L = []
    b0, c0, d0 = 5.0, 11.0, 17.0
    lift = {"SUGAR": (c0, -26), "CHLOROGENIC ACIDS": (c0, -26)}
    labs = []
    for k, (nm, p, _, row) in enumerate(SEGS):
        x0, w = seg_x(k)
        t = b0 + 0.8 + k * 0.25
        s = f"{nm} ≈ {p} %"
        labs.append(caps(f"Label {nm}", s, [x0 + w / 2, 920 + row * 32], t, d0, size=13, color=INK))
        if nm in lift:
            labs.append(marker(f"Swipe {nm}", x0 + w / 2 - tw(s, 13, LAB, 140) / 2 - 8, 920 + row * 32, tw(s, 13, LAB, 140) + 16, c0 + 0.4, d0, size=13))
    px, pw = seg_x(2)
    labs.append(shape("Amino Part", [G("A", rect([pw * 0.3, BH], [pw * 0.15, 0]), fill(INK, 35))], [px + pw * 0.7, BAR_Y], c0 + 0.6, d0 + 0.6,
                      scale=A(K(d0, [100, 100]), K(d0 + 0.6, [0, 100]))))
    labs.append(tag("Amino Label", "FREE AMINO ACIDS", [px + pw * 0.85, BAR_Y - 50], c0 + 0.8, d0, size=13))
    labs.append(caps("Bar Title", "GREEN ARABICA, DRY WEIGHT", [BX0, 730], b0 + 0.8, d0, size=16, color=INK, just="left"))
    labs.append(src("Src Farah", "SOURCE: FARAH (2012); ILLY & VIANI (2005)", b0 + 0.8, d0))
    labs.append(caps("Water Label", "WATER ≈ 11 % OF THE SEED'S WEIGHT", [BX0 + BW * 0.11 + 20, WAT_Y + 6], c0 + 2.4, d0, size=13, color=INK, just="left"))
    for l in labs:
        add_out(l, d0)
    L += labs
    L += water_row("", c0 + 2.0, d0 + 0.3)
    bars = bar_layers("", b0 + 0.6, d0 + 0.6, grow_t=b0 + 0.6, lift=lift)
    for l in bars:
        l["transform"]["scale"]["keyframes"] += [K(d0, [100, 100]), K(d0 + 0.6, [0, 100])]
    L += bars
    L.append(bean("Seed Small", [CX, BAR_Y], 120, SEED, d0 + 0.6, D, scale=grow(d0 + 0.6),
                  position=A(K(d0 + 1.2, [CX, BAR_Y]), K(d0 + 2.2, list(START)))))
    L.append(bean("Seed", [CX, CY], 520, SEED, 0, b0 + 1.0, cells_r=26, cells_t=1.0,
                  position=A(K(b0, [CX, CY]), K(b0 + 1.0, [CX, BAR_Y])), scale=A(K(b0, [100, 100]), K(b0 + 1.0, [0, 0]))))
    L[-1]["shapes"][0]["transform"] = {"opacity": A(K(0.8, 100), K(1.0, 0))}   # the crease goes as the cells open
    return finish(L, D)


# =====================================================================
# SCENE 3 - THE CURVE, AND DRYING (21 s)
# =====================================================================
Z_CELL = 320 / 6


def s3_curve(D):
    L = []
    c0, p0 = 9.0, 17.6
    way = [(0, 0), (1.0, 0), (14.0, M_YELLOW), (D, M_YELLOW)]
    tm = lambda t: max(0, min(M_YELLOW, (t - 1.0) / 13.0 * M_YELLOW))
    for k, (s, m) in enumerate((("HAY", 4.0), ("BREAD", 5.6))):
        t = 1.0 + m / M_YELLOW * 13.0
        x, y = cxy(m)
        L.append(tag(f"Smell {s}", s, [x - 30, y - 70], t, p0, size=18))
    rnd = random.Random(3)
    for j in range(8):
        t = c0 + j * 0.6
        x, y = cxy(tm(t))
        dx = rnd.uniform(-30, 30)
        L.append(disc(f"Steam {j + 1}", A(K(t, [x, y]), K(t + 1.4, [x + dx, y - 140], None)), 14, GREY2, t, t + 1.4, sh=0))
    L.append(caps("Water Small Label", "WATER IN THE SEED", [1100, 680], c0, p0, size=13, color=INK, just="left"))
    L.append(shape("Water Small", [G("W", rect([300, 22], [150, 0]), fill(WATER))], [1100, 710], c0, p0, scale=A(K(c0, [100, 100]), K(14.0, [15, 100]))))
    L.append(shape("Water Small Outline", [G("O", rect([300, 22], [150, 0]), stroke(INK, 2))], [1100, 710], c0, p0))
    L.append(tag("Drum Temp", "DRUM ≈ 200–230 °C", [1600, 330], 4.4, p0, size=14))
    L.append(shape("Drum Icon", [G("Therm", rect([10, 70], [70, -10], 5), stroke(INK, 3), fill(ARA)),
                                 G("D", ell([110, 110]), path([(-40, 0), (40, 0)]), stroke(INK, 4), fill(WHITE))], [1580, 240], 4.0, p0, scale=grow(4.0)))
    L.append(src("Src Schenker", "SOURCE: SCHENKER (2000), ETH ZÜRICH", 1.0, p0))
    for l in L:
        add_out(l, min(l["out"], p0 - 0.3))
    cv = curve("", 0, D, way, axes_t=0.6, dot_scale=A(K(0, [200, 200]), K(1.0, [100, 100])), cells_t=p0 - 0.4)
    for l in cv[1:]:
        l["out"] = p0 + 0.2   # the curve's ink would swell to a bar in the push
    L += cv
    q = cxy(M_YELLOW)
    return finish(L, D, [(0, C, C, 1), (p0, C, C, 1), (D - 0.5, q, C, Z_CELL)])


# =====================================================================
# SCENE 4 - THE MAILLARD REACTION (39 s)
# =====================================================================
CELL_R = 320


def cell(name, t0, t1, col):
    return shape(name, [G("Wall", hexpath(CELL_R), stroke(INK, 6), fill(col))], [CX, CY], t0, t1, parent="Cell Rig")


COILS = [((830, 700), 1.6), ((990, 560), 2.0), ((1080, 360), 1.4)]


def coils(t0, t1, prefix="", drawn=False):
    return [coil(f"{prefix}Coil {j + 1}", list(p), t0 + (0 if drawn else j * 0.4), t1, col=ROAST[4], s=s * 100, drawn=drawn, parent="Cell Rig")
            for j, (p, s) in enumerate(COILS)]


def s4_maillard(D):
    L = []
    a0, b0, c0, d0, e0, r0 = 1.0, 8.0, 15.0, 25.0, 31.0, 37.2
    head = [("SUGAR + AMINO ACID", a0 + 2.2, b0), ("REARRANGES", b0 + 0.4, b0 + 3.4), ("FRAGMENTS", b0 + 3.6, c0), ("STRECKER DEGRADATION", c0 + 0.6, d0),
            ("MELANOIDINS = THE BROWN", d0 + 0.6, e0)]
    for k, (s, t, t1) in enumerate(head):
        L.append(tag(f"Head {k + 1}", s, [CX, 170], t, t1, size=20))
    L.append(tag("Toast", "THE SAME REACTION BROWNS TOAST", [CX, 930], a0 + 3.5, b0, size=16))
    # A: sugar meets amino acid
    st_a = [sugar("Sugar A", [780, 420], a0, e0, r=44, scale=grow(a0), parent="Cell Rig"),
            amino("Amino A", [780, 640], a0, e0, position=A(K(a0 + 0.6, [780, 640]), K(a0 + 2.2, [780, 500])), parent="Cell Rig")]
    # B: the pair refolds into a chain, then shatters
    chain = [(-60, 0), (-30, -20), (0, 0), (30, -20), (60, 0), (90, -20)]
    st_b = [shape("Chain", [G("C", path(chain), stroke(INK, 5)), G("Atoms", *[ell([14, 14], list(p)) for p in chain], stroke(INK, 3), fill(WHITE))],
                  [930, 400], b0 + 0.4, b0 + 3.4, scale=grow(b0 + 0.4), parent="Cell Rig")]
    frags = [(900, 560), (1010, 620), (930, 700), (1040, 500)]
    for j, p in enumerate(frags):
        st_b.append(shape(f"Fragment {j + 1}", [G("F", path([(-18, 0), (0, -12), (18, 0)]), stroke(INK, 5))], [960, 420], b0 + 3.4, e0,
                          position=A(K(b0 + 3.4, [960, 420]), K(b0 + 4.4, list(p))), parent="Cell Rig"))
    # C: Strecker - fragments tear the ends off fresh amino acids, which fly off as smells
    st_c = [amino("Amino C1", [1110, 560], c0 + 0.6, e0, scale=A(K(c0 + 0.6, [0, 0]), K(c0 + 1.0, [70, 70])), parent="Cell Rig"),
            amino("Amino C2", [1110, 690], c0 + 1.0, e0, scale=A(K(c0 + 1.0, [0, 0]), K(c0 + 1.4, [70, 70])), parent="Cell Rig")]
    smells = [("MALT", "3-METHYLBUTANAL", (1110, 560), (1480, 330), c0 + 2.0), ("COOKED POTATO", "METHIONAL", (1110, 690), (1480, 470), c0 + 3.6)]
    for j, (s, chem, a, b, t) in enumerate(smells):
        L.append(aroma(f"Smell {j + 1}", list(b), t, e0, position=A(K(t, list(a)), K(t + 1.2, list(b)))))
        L.append(tag(f"Smell {j + 1} Label", s, [b[0] + 50, b[1] - 4], t + 1.2, e0, size=16, just="left"))
        L.append(caps(f"Smell {j + 1} Chem", chem, [b[0] + 50, b[1] + 22], t + 1.4, e0, size=12, color=INK, just="left"))
    L.append(src("Src Grosch", "SOURCE: GROSCH (2001); FLAMENT (2002)", c0 + 2.0, D))
    st_c.append(shape("Pyrazines", [G("R1", hexpath(22, -22, 0), hexpath(22, 22, 0), stroke(INK, 3), fill(WHITE))], [1100, 790], c0 + 6.0, e0,
                      scale=grow(c0 + 6.0), parent="Cell Rig"))
    L.append(leader("Pyrazine Leader", (1150, 790), (1460, 640), c0 + 6.2, e0))
    L.append(tag("Pyrazine Label", "PYRAZINES · ROASTED NUTS", [1480, 630], c0 + 6.4, e0, size=16, just="left"))
    # D: the brown; a small bean moves along the ramp
    L.append(bean("Ramp Bean", [380, 760], 140, A(K(d0, ROAST[1]), K(d0 + 2.5, ROAST[2]), K(d0 + 5.0, ROAST[3])), d0 + 0.4, e0, scale=grow(d0 + 0.4)))
    L.append(tag("Ramp Label", "THE BEAN", [380, 850], d0 + 0.8, e0, size=14))
    for l in L:
        add_out(l, min(l["out"], e0))
    prods = st_a + st_b + st_c
    dim(st_a, b0)
    dim(st_b, c0)
    dim(st_c, d0)
    for l in prods:
        add_out(l, e0)
    L += prods
    # E: the smell cloud above the shrunken cell
    rnd = random.Random(1000)
    pts = []
    while len(pts) < 1000:
        x, y = rnd.uniform(-450, 450), rnd.uniform(-250, 250)
        if (x / 450) ** 2 + (y / 250) ** 2 < 1:
            pts.append((round(x, 1), round(y, 1)))
    cl0, grey_t = e0 + 1.0, e0 + 3.6
    sink = dict(position=A(K(r0, [CX, 400]), K(r0 + 0.6, [CX, 850])), scale=A(K(cl0, [0, 0]), K(cl0 + 0.5, [100, 100]), K(r0, [100, 100]), K(r0 + 0.6, [0, 0])))
    keep = pts[:30]
    hl = keep[7]
    L.append(tag("Cloud Count", "ABOUT 1,000 AROMA COMPOUNDS IDENTIFIED", [CX, 110], cl0 + 0.6, r0, size=18))
    L.append(tag("Cloud Few", "A FEW DOZEN CARRY THE SMELL", [CX, 700], grey_t + 0.4, r0, size=18))
    L.append(caps("FFT Label", "2-FURFURYLTHIOL", [CX + hl[0] + 24, 400 + hl[1] + 5], grey_t + 1.4, r0, size=14, color=INK, just="left"))
    L.append(marker("FFT Swipe", CX + hl[0] + 16, 400 + hl[1] + 5, tw("2-FURFURYLTHIOL", 14, LAB, 140) + 16, grey_t + 1.2, r0, size=14))
    L.append(shape("Cloud Keep", [G("K", *[ell([12, 12], list(p)) for p in keep], fill(INK))], [CX, 400], cl0, r0 + 0.6, **dict(sink)))
    L.append(shape("Cloud", [G("D", *[ell([7, 7], list(p)) for p in pts[30:]], fill(A(K(grey_t, INK), K(grey_t + 0.6, GREY2))))], [CX, 400], cl0, r0 + 0.6,
                   **dict(position=A(*sink["position"]["keyframes"]), scale=A(*sink["scale"]["keyframes"]))))
    for j in range(2):
        L.append(aroma(f"Escape {j + 1}", [CX, 400], e0 + 0.2, cl0, position=A(K(e0 + 0.2, [CX - 60 + 120 * j, 850]), K(cl0, [CX, 400]))))
    L.append(src("Src Flament", "SOURCE: FLAMENT (2002); GROSCH (2001)", cl0, r0))
    L += coils(d0 + 0.4, D)
    L.append(cell("Cell", 0, D, A(K(d0, ROAST[1]), K(d0 + 3.0, ROAST[3]))))
    sur = []
    for j in range(-2, 3):
        for i in range(-3, 4):
            x, y = (i + (j % 2) * 0.5) * CELL_R * math.sqrt(3), j * CELL_R * 1.5
            if (i, j) != (0, 0):
                sur.append(hexpath(CELL_R, x, y))
    L.append(shape("Surround", [G("Cells", *sur, stroke(INK, 6)), G("Y", rect([W + 200, H + 200]), fill(ROAST[1]))], [CX, CY], 0, 0.8))
    L.append(null("Cell Rig", [CX, CY], 0, D, scale=A(K(e0, [100, 100]), K(e0 + 0.8, [40, 40]), K(r0 + 0.4, [40, 40]), K(r0 + 1.4, [100, 100])),
                  position=A(K(e0, [CX, CY]), K(e0 + 0.8, [CX, 850]), K(r0 + 0.4, [CX, 850]), K(r0 + 1.4, [CX, CY]))))
    return finish(L, D)


# =====================================================================
# SCENE 5 - FIRST CRACK (26 s)
# =====================================================================
def s5_crack(D):
    L = []
    k0, b0, c0 = 9.5, 12.0, 19.0
    rnd = random.Random(5)
    cellv = []
    cellv.append(tag("Steam Label", "STEAM + CO₂", [1340, 780], 3.0, b0, size=16, just="left"))
    cellv.append(tag("Pressure Label", "PRESSURE", [1620, 300], 1.4, b0, size=14))
    cellv.append(gauge("Gauge", [1620, 250], 1.0, b0, A(K(1.0, -80), K(k0, 70), K(k0 + 0.3, -20))))
    cellv.append(tag("Crack Label", "CRACK", [1520, 548], k0 + 0.1, b0, size=24, just="left"))
    cellv.append(sound("Crack Waves", [1420, 540], k0 + 0.1, b0))
    jag = [(-280, -150), (-170, -60), (-120, -110), (-20, 0), (50, -40), (130, 70), (180, 30), (280, 160)]
    cellv.append(shape("Crack", [G("C", path(jag), trim(0, A(K(k0, 0), K(k0 + 0.25, 100))), stroke(INK, 7))], [CX, CY], k0, b0, parent="Cell Rig"))
    for j in range(40):
        a, r = rnd.uniform(0, 2 * math.pi), math.sqrt(rnd.random()) * 240
        t = 1.0 + j * 0.2
        cellv.append(disc(f"Gas {j + 1}", [round(CX + r * math.cos(a), 1), round(CY + r * math.sin(a), 1)], 16, GREY2 if j % 2 else WHITE, t, b0, sh=0,
                          line=GREY if j % 2 == 0 else None, parent="Cell Rig", scale=grow(t, 100, 0.2)))
        cellv[-1]["transform"]["position"] = X(f"var w = 3 + time * 0.8; [value[0] + Math.sin(time * w + {j}) * 6, value[1] + Math.cos(time * w * 1.3 + {j}) * 6]")
        cellv[-1]["transform"]["position"]["value"] = [round(CX + r * math.cos(a), 1), round(CY + r * math.sin(a), 1)]
    cellv += coils(0, b0, drawn=True)
    cellv.append(cell("Cell", 0, b0, ROAST[3]))
    for l in cellv:
        l["out"] = min(l["out"], b0)
    L += cellv
    L.append(null("Cell Rig", [CX, CY], 0, b0, scale=A(K(3.0, [100, 100]), K(k0, [110, 110]))))
    # B: the whole bean, split along its crease, against a ghost of the green bean
    bv = [tag("Swell Label", "≈ 1.5 × THE VOLUME OF THE GREEN BEAN", [CX, 880], b0 + 1.2, c0, size=18),
          src("Src Swell", "SOURCE: SCHENKER (2000); ILLY & VIANI (2005)", b0 + 1.0, c0),
          shape("Split", [G("S", path([(-260, 0), (260, 0)], False, i=[(0, 0), (-140, -44)], o=[(140, 44), (0, 0)]), stroke(WHITE, 16))], [CX, CY], b0, c0),
          bean("Roasted", [CX, CY], 620, ROAST[2], b0, c0, crease=False),
          caps("Ghost Label", "GREEN", [CX - 300, 300], b0 + 1.6, c0, size=14, color=GREY, just="right"),
          shape("Ghost", [G("G", ell([540, 378]), stroke(GREY, 3, dashes=(14, 10)))], [CX - 60, CY - 40], b0 + 1.4, c0)]
    L += bv
    # C: back out to the curve
    L.append(tag("FC Label", "FIRST CRACK ≈ 196 °C", [cxy(M_FC)[0] - 30, cxy(M_FC)[1] - 60], c0 + 2.2, D, size=16, just="right"))
    L.append(caps("Band Label", "190–205 °C", [260, cxy(0, 205)[1] - 10], c0 + 2.4, D, size=13, color=GREY, just="left"))
    cv = curve("", c0, D, [(c0, M_FC), (D, M_FC)])
    for l in cv[1:]:
        l["in"] = c0 + 1.2
    L += cv
    y0, y1 = cxy(0, 205)[1], cxy(0, 190)[1]
    L.append(shape("FC Band", [G("B", rect([1420, y1 - y0], [950, (y0 + y1) / 2]), fill(LINE))], [0, 0], c0 + 2.0, D))
    d = cxy(M_FC)
    return finish(L, D, [(0, C, C, 1), (b0 - 0.01, C, C, 1), (b0, C, C, 1.5), (b0 + 1.6, C, C, 1), (c0 - 0.01, C, C, 1), (c0, d, C, 6), (c0 + 2.0, d, d, 1)])


# =====================================================================
# SCENE 6 - DEVELOPMENT (29 s)
# =====================================================================
def s6_develop(D):
    L = []
    m0, c0, k0, x0 = 1.0, 15.0, 21.0, 26.0
    way = [(0, M_FC), (m0, M_FC), (c0, 11.5), (k0, 11.5), (k0 + 3.0, M_DEV), (D, M_DEV)]
    # carried over from S5's last frame
    L.append(caps("FC Label", "FIRST CRACK ≈ 196 °C", [cxy(M_FC)[0] - 30, cxy(M_FC)[1] - 60], 0, m0 + 0.4, size=16, color=INK, just="right"))
    L.append(caps("Band Label", "190–205 °C", [260, cxy(0, 205)[1] - 10], 0, m0 + 0.4, size=13, color=GREY, just="left"))
    y0, y1 = cxy(0, 205)[1], cxy(0, 190)[1]
    band_fc = shape("FC Band", [G("B", rect([1420, y1 - y0], [950, (y0 + y1) / 2]), fill(LINE))], [0, 0], 0, m0 + 0.4)
    # A: the development band grows behind the dot
    xs = ride(way)
    dev = A(*[KL(t, [max(0.01, (cxy(m)[0] - cxy(M_FC)[0]) / 200 * 100), 100]) for t, m in xs])
    L.append(caps("Dev Label", "DEVELOPMENT", [cxy(M_FC)[0] + 8, 840], m0 + 1.0, x0, size=13, color=INK, just="left"))
    L.append(caps("Clock Label", "SINCE FIRST CRACK", [1560, 820], m0 + 1.2, x0, size=12, color=INK))
    L.append(clock("Clock", [1560, 760], m0 + 1.0, x0))
    # B: a chlorogenic acid splits
    t_split = 7.0
    L.append(tag("CGA Label", "CHLOROGENIC ACID", [530, 140], 3.4, t_split, size=16))
    L.append(shape("CGA Bond", [G("B", path([(-38, 0), (38, 0)]), stroke(INK, 4))], [530, 200], 3.0, t_split, scale=grow(3.0)))
    for j, (nm, x) in enumerate((("QUINIC ACID", 400), ("CAFFEIC ACID", 660))):
        L.append(shape(f"Ring {j + 1}", [G("R", hexpath(36), stroke(INK, 4), fill(WHITE))], [470 + 120 * j, 200], 3.0, x0,
                       position=A(K(t_split, [470 + 120 * j, 200]), K(t_split + 0.8, [x, 290])), scale=grow(3.0)))
        L.append(tag(f"Ring {j + 1} Label", nm, [x, 360], t_split + 0.8, x0, size=14))
    L.append(tag("Lactones", "→ LACTONES · BITTER", [660, 392], t_split + 3.0, x0, size=14))
    L.append(tag("Phenylindanes", "→ PHENYLINDANES · HARSHER", [660, 422], t_split + 5.5, x0, size=14))
    # C: how much is left at each stop
    bars = [("GREEN", 100, 880), ("MEDIUM ≈ ⅓", 35, 1020), ("DARKER ≈ 1 IN 10", 12, 1160)]
    L.append(tag("Bars Title", "CHLOROGENIC ACIDS LEFT", [1020, 560], c0, x0, size=14))
    for j, (nm, p, x) in enumerate(bars):
        h = 200 * p / 100
        t = c0 + 0.4 + j * 0.6
        L.append(caps(f"Bar {j + 1} Label", nm, [x, 830], t, x0, size=11, color=INK))
        L.append(shape(f"Bar {j + 1}", [G("B", rect([70, h], [0, -h / 2]), stroke(INK, 2), fill(GREY2))], [x, 800], t, x0, scale=A(K(t, [100, 0]), K(t + 0.4, [100, 100]))))
    L.append(src("Src Jezek", "SOURCE: JEŽEK ET AL., POTRAVINARSTVO (2019)", c0, x0))
    # D: two stopping points
    for j, (s, m, just, dx) in enumerate((("EARLY STOP: TASTES MORE OF THE FARM", M_FC, "right", -50), ("LATE STOP: TASTES MORE OF THE ROAST", M_DEV, "left", 50))):
        x, y = cxy(m)
        t = k0 + j * 0.8
        L.append(tag(f"Stop {j + 1}", s, [x + dx, y - 96], t + 0.3, x0, size=13, just=just))
        L.append(cup(f"Cup {j + 1}", [x, y - 100], t, x0))
    for l in L:
        add_out(l, min(l["out"], x0))
    L += curve("", 0, D, way)
    L.append(band_fc)
    L.append(shape("Dev Band", [G("B", rect([200, 650], [100, 535 - 860]), fill(LINE))], [cxy(M_FC)[0], 860], m0, x0, scale=dev))
    add_out(L[-1], x0)
    return finish(L, D)


# =====================================================================
# SCENE 7 - SECOND CRACK (20 s)
# =====================================================================
def s7_second(D):
    L = []
    b0 = 8.5
    x, y = cxy(M_SC)
    cv = [tag("SC Label", "SECOND CRACK ≈ 225 °C", [x - 40, y - 60], 4.0, b0, size=16, just="right"),
          sound("SC Waves", [x + 40, y], 4.0, b0, s=60, rate=20),
          caps("Oil Label", "OIL ON THE SURFACE", [600, 400], 5.8, b0, size=14, color=INK),
          bean("Glossy", [600, 270], 260, A(K(3.0, ROAST[3]), K(4.0, ROAST[4])), 2.8, b0, gloss_t=5.4, scale=grow(2.8))]
    cv += curve("", 0, b0, [(0, M_DEV), (1.0, M_DEV), (4.0, M_SC), (b0, M_SC)])
    for l in cv:
        l["out"] = min(l["out"], b0)
    L += cv
    # B: the S2 bars return and lose a sixth of the weight
    w11 = BW * 0.11
    sx, sw = BX0 + BW * 0.94, BW * 0.06
    rnd = random.Random(7)
    lab = [tag("Water Loss", "WATER ≈ 11 % → ≈ 1–2 %", [BX0 + w11 + 20, WAT_Y + 6], b0 + 1.4, D - 1.5, size=13, just="left"),
           tag("Gas Label", "CO₂, STEAM FROM REACTIONS AND SMELLS", [BX0 + BW, 680], b0 + 4.4, D - 1.5, size=13, just="right"),
           tag("Total", "≈ 1/6 OF THE WEIGHT GONE", [BX0 + BW * 11 / 12, 735], b0 + 6.0, D - 1.5, size=16),
           shape("Bracket", [G("B", path([(BX0 + BW * 5 / 6, 772), (BX0 + BW * 5 / 6, 762), (BX0 + BW, 762), (BX0 + BW, 772)]), stroke(INK, 3))], [0, 0], b0 + 5.8, D - 1.5),
           src("Src Weight", "SOURCE: ILLY & VIANI (2005)", b0 + 1.0, D - 1.5)]
    for l in lab:
        add_out(l, D - 1.5)
    L += lab
    for j in range(16):
        t = b0 + 4.0 + j * 0.05
        p = [sx + rnd.uniform(0, sw), BAR_Y + rnd.uniform(-20, 20)]
        L.append(disc(f"Gas {j + 1}", A(K(t, p), K(t + 1.6, [p[0] + rnd.uniform(-40, 40), p[1] - 200 - rnd.uniform(0, 60)], None)), 12, GREY2, t, t + 1.6, sh=0))
    L.append(shape("Slice", [G("S", rect([sw, BH], [sw / 2, 0]), stroke(INK, 2), fill(LINE))], [sx, BAR_Y], b0, b0 + 4.0))
    L.append(shape("Slice Ghost", [G("G", rect([sw, BH], [sw / 2, 0]), stroke(GREY, 2, dashes=(8, 6)))], [sx, BAR_Y], b0 + 4.0, D))
    L.append(shape("Water Ghost", [G("G", rect([w11, 24], [w11 / 2, 0]), stroke(GREY, 2, dashes=(8, 6)))], [BX0, WAT_Y], b0 + 1.0, D))
    bars = bar_layers("", b0, D)
    oth = [l for l in bars if l["name"] == "Seg OTHER"][0]
    oth["shapes"][0]["items"][0]["size"] = [BW * 0.05, BH]
    oth["shapes"][0]["items"][0]["position"] = [BW * 0.025, 0]
    L += bars
    L += water_row("", b0, D, frac=A(K(b0 + 1.2, [100, 100]), K(b0 + 3.0, [14, 100])))
    for l in bars + L[-2:]:
        appear(l, b0, dy=40)
    return finish(L, D)


# =====================================================================
# SCENE 8 - WHERE THE SUGAR WENT (25 s)
# =====================================================================
def s8_sugar(D):
    L = []
    z0, z1, b0, c0, x0 = 0.4, 2.6, 9.0, 17.0, 22.0
    sx, sw = seg_x(3)
    sug = (sx + sw / 2, BAR_Y)
    # A: green vs medium roast
    base = 800
    L.append(tag("Gone", "≈ 96–98 % GONE", [560, base - 60], z1 + 2.0, x0, size=16))
    L.append(marker("Gone Swipe", 560 - tw("≈ 96–98 % GONE", 16, LAB, 140) / 2 - 8, base - 60, tw("≈ 96–98 % GONE", 16, LAB, 140) + 16, z1 + 2.6, x0, size=16))
    L.append(caps("Chart Title", "SUGAR, % OF DRY WEIGHT", [200, 300], z1 + 0.2, x0, size=14, color=INK, just="left"))
    L.append(caps("Green Label", "GREEN ≈ 7 %", [330, base + 34], z1 + 0.2, x0, size=13, color=INK))
    L.append(caps("Medium Label", "MEDIUM ROAST", [560, base + 34], z1 + 0.8, x0, size=13, color=INK))
    L.append(shape("Medium Bar", [G("B", rect([120, 4], [0, -2]), fill(INK))], [560, base], z1 + 0.8, x0, scale=grow(z1 + 0.8)))
    L.append(shape("Green Bar", [G("B", rect([120, 420], [0, -210]), stroke(INK, 3), fill(WHITE))], [330, base], z1, x0))
    L.append(shape("Baseline", [G("B", path([(200, base), (680, base)]), stroke(INK, 3))], [0, 0], z1, x0))
    L.append(src("Src Jezek", "SOURCE: JEŽEK ET AL., POTRAVINARSTVO (2019)", z1 + 0.4, x0))
    # B: where it went
    L.append(arrow("Arrow Colour", (410, 420), (800, 330), b0, x0))
    L.append(arrow("Arrow Caramel", (410, 520), (800, 690), b0 + 0.6, x0))
    L.append(coil("Melanoidin", [880, 320], b0 + 0.5, x0, s=180))
    L.append(tag("Colour", "COLOUR", [880, 210], b0 + 1.0, x0, size=16))
    L.append(sugar("Breaking", [880, 700], b0 + 1.0, x0, r=50, broken=b0 + 3.0, scale=grow(b0 + 1.0)))
    L.append(tag("Caramelisation", "CARAMELISATION, ABOVE ≈ 170 °C", [880, 800], b0 + 1.4, x0, size=14))
    L.append(tag("Furaneol", "FURANEOL · SMELLS OF CARAMEL", [880, 832], b0 + 3.8, x0, size=14))
    # C: the smell settles on the bag
    nx = BAG[0] - tw(NOTES, 22, LAB) / 2 + tw("CARAMELO", 22, LAB) / 2
    for j in range(3):
        t = b0 + 3.2 + j * 0.3
        a, m = [880 - 40 + 40 * j, 700], [880 - 60 + 60 * j, 580]
        L.append(aroma(f"Caramel {j + 1}", m, t, c0 + 3.0, s=80, position=A(K(t, a), K(t + 1.0, m), K(c0 + 1.2, m), K(c0 + 3.0, [nx - 50 + 50 * j, NOTES_Y - 50]))))
    for l in L:
        add_out(l, min(l["out"], x0))
    L += bag(c0, D, swipe_t=c0 + 3.2, slide_t=c0)
    # the bars from S7, pushed into the sugar segment
    pre = bar_layers("", 0, z1)
    oth = [l for l in pre if l["name"] == "Seg OTHER"][0]
    oth["shapes"][0]["items"][0]["size"] = [BW * 0.05, BH]
    oth["shapes"][0]["items"][0]["position"] = [BW * 0.025, 0]
    L += pre
    L += water_row("", 0, z1, frac=[14, 100])
    return finish(L, D, [(0, C, C, 1), (z0, C, C, 1), (z1 - 0.01, sug, C, 7.5), (z1, C, C, 1)])


# =====================================================================
# SCENE 9 - ROASTED WITH SUGAR (30 s)
# =====================================================================
NORM = [("NMX-F-173-SCFI-2020", 22, LAB), ("CAFÉ TOSTADO", 16, LAB), ("", 12, BODY), ("Especificaciones y métodos de prueba para el", 18, BODY),
        ("café tostado mezclado con azúcar caramelizada", 18, BODY), ("en grano o molido.", 18, BODY)]


def s9_mexico(D):
    L = []
    n0, n1, b0, c0, d0 = 6.0, 13.6, 14.0, 20.0, 26.0
    L += doc("Norm", NORM, [CX, 540], (520, 520), n0, n1, hl_line=4, credit="NMX-F-173-SCFI-2020, MÉXICO")
    for l in L:
        p = l["transform"]["position"]
        if isinstance(p, list) and not l["name"].endswith("Credit"):
            l["transform"]["position"] = A(K(n0, [p[0], p[1] + 700]), K(n0 + 0.7, p), K(n1 - 0.7, p), K(n1, [p[0], p[1] + 900]))
    # B: outside in vs inside out
    diag = [tag("Outside", "OUTSIDE IN", [CX, 470], b0 + 0.6, c0 + 0.6, size=16),
            tag("Inside", "INSIDE OUT", [CX, 820], b0 + 1.6, c0 + 0.6, size=16),
            shape("Wrap", [G("W", arc((CX + 70, 290), (CX - 110, 330), 0.5), trim(0, A(K(b0 + 0.6, 0), K(b0 + 1.2, 100))), stroke(INK, 4))], [0, 0], b0 + 0.6, c0 + 0.6),
            sugar("Hex Out", [CX + 100, 300], b0 + 0.3, c0 + 0.6, r=30, scale=grow(b0 + 0.3)),
            bean("Bean Out", [CX, 370], 200, ROAST[3], b0, c0 + 0.6, scale=grow(b0)),
            aroma("Inside Smell", [CX + 40, 650], b0 + 3.0, c0 + 0.6, s=70, position=A(K(b0 + 3.0, [CX, 720]), K(b0 + 4.0, [CX + 40, 640]))),
            sugar("Hex In", [CX, 720], b0 + 1.3, c0 + 0.6, r=26, broken=b0 + 2.8, scale=grow(b0 + 1.3)),
            bean("Bean In", [CX, 720], 200, ROAST[2], b0 + 1.0, c0 + 0.6, crease=False, scale=grow(b0 + 1.0))]
    # C: Profeco's 33 coffees
    strip = [tag("Strip Title", "COFFEES TESTED BY PROFECO, 2025", [CX, 880], c0 + 1.0, d0, size=16),
             tag("Strip Count", "4 OF 33: SUGAR BLENDS", [CX, 1000], c0 + 2.4, d0, size=16),
             src("Src Profeco", "SOURCE: PROFECO, REVISTA DEL CONSUMIDOR, JUNE 2025 (VIA EXPANSIÓN)", c0 + 1.0, d0)]
    for j in range(33):
        x = BX0 + 22 + j * 43
        black = j in (4, 12, 21, 28)
        t = c0 + 1.2 + j * 0.03
        strip.append(shape(f"Pack {j + 1}", [G("P", rect([28, 40], None, 3), stroke(INK, 2), fill(A(K(c0 + 2.2, WHITE), K(c0 + 2.6, INK)) if black else WHITE))],
                           [x, 935], t, d0, scale=grow(t, 100, 0.2)))
    for l in strip:
        add_out(l, d0)
    # D: the bag's own curve stops just after first crack
    mini = [((x - 240) * 0.22 + 1230, (y - 210) * 0.22 + 100) for x, y in SAMPLES[:105]]
    ex, ey = mini[-1]
    stopper = [caps("Stop Early", "STOP EARLY", [ex + 24, ey + 5], d0 + 2.0, D - 0.6, size=14, color=INK, just="left"),
               marker("Stop Swipe", ex + 16, ey + 5, tw("STOP EARLY", 14, LAB, 140) + 16, d0 + 2.2, D - 0.6, size=14),
               disc("Mini Dot", [ex, ey], 16, ROAST[2], d0 + 1.8, D - 0.6, sh=0, scale=grow(d0 + 1.8)),
               shape("Mini Curve", [G("C", path(mini), trim(0, A(K(d0 + 0.4, 0), K(d0 + 1.8, 100))), stroke(INK, 3))], [0, 0], d0 + 0.4, D - 0.6)]
    L = stopper + strip + diag + L
    L += bag(0, D)
    dr = drum(0, D, pour_t=1.4)
    dim(dr + diag, c0)
    for l in dr:
        op = l["transform"]["opacity"]
        op["keyframes"] += [K(d0, 28), K(d0 + 0.4, 100)]
    for l in diag:
        add_out(l, min(l["out"], d0))
    L += dr
    return finish(L, D)


# =====================================================================
# SCENE 10 - CLOSE (19 s)
# =====================================================================
def s10_close(D):
    L = []
    a0, s0, e0 = 1.5, 4.5, 11.0
    L += wipe_text("End Title", "What Roasting Really Does", [CX, 975], 64, INK, e0 + 0.4, D)
    L.append(word_marker("End Swipe", "What Roasting Really Does", "Roasting", CX, 975, 64, e0 + 1.2, D))
    L.append(tag("Added", "ADDED", [DRUM[0] + 150, 170], a0 + 0.6, D, size=18, just="left"))
    L.append(arrow("Added Arrow", (DRUM[0] + 130, 160), (DRUM[0] + 40, 230), a0 + 0.4, D))
    L.append(sugar("Drop", [DRUM[0], 330], a0, a0 + 1.1, r=32, position=A(K(a0, [DRUM[0], 100]), K(a0 + 1.0, [DRUM[0], 330]))))
    L.append(tag("Spent", "SPENT", [BAG[0], 150], s0 + 1.6, D, size=18))
    L.append(aroma("Spent Smell", [BAG[0] - 60, 210], s0 + 1.2, D, position=A(K(s0 + 1.2, [BAG[0], 240]), K(s0 + 2.0, [BAG[0] - 60, 210]))))
    L.append(coil("Spent Coil", [BAG[0] + 60, 230], s0 + 1.3, D, s=80))
    L.append(sugar("Spent Hex", [BAG[0], 240], s0, D, r=32, broken=s0 + 1.1, scale=grow(s0)))
    L += bag(0, D)
    L += drum(0, D, col=INK)
    return finish(L, D)


SCENES = [("S1_Drum", 17.0, s1_drum), ("S2_Seed", 20.0, s2_seed), ("S3_Curve", 21.0, s3_curve), ("S4_Maillard", 39.0, s4_maillard),
          ("S5_FirstCrack", 26.0, s5_crack), ("S6_Develop", 29.0, s6_develop), ("S7_SecondCrack", 20.0, s7_second), ("S8_Sugar", 25.0, s8_sugar),
          ("S9_Mexico", 30.0, s9_mexico), ("S10_Close", 19.0, s10_close)]

if __name__ == "__main__":
    write(SCENES, "Roasting", "08_roasting")
