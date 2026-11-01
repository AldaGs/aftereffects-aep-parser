"""Generator for episode 4, "The Shade Forest in Your Cup" (scripts/04_shade_forest_script.md).

    python "Coffee Episodes/generators/04_shade_forest.py"      # writes ../json/04_shade_forest.json

Rigs are nulls with anchor [0, 0]: content point c lands on screen at P + c * s. A handoff (P, s) at the start of
scene N+1 is written as (inv(P), s / HS) at the end of scene N (handoff()). The transect (S2-S3) and the farm
cross-section (S4-S6, S10) are each one drawing in content coordinates, reused across scenes.
No fades: cut_pass turns every exit into a cut or a pop.
"""
import math, random

from coffee_common import *  # noqa: F401,F403

SAGE = "#8FA88A"
CHIAPAS_LL = (-92.4, 15.6)
GREAT_LAKES = (-84.0, 45.0)


def handoff(P, s):
    return inv(P), s / HS


def rig(name, D, keys, t0=0):
    """keys: [(t, P, s)] -> rig null (anchor [0, 0])."""
    return null(name, [0, 0], t0, D, anchor=[0, 0], position=A(*[K(t, list(P)) for t, P, s in keys]),
                scale=A(*[K(t, [s * 100, s * 100]) for t, P, s in keys]))


# ---------------------------------------------------------------------
# art
# ---------------------------------------------------------------------
def crown(name, w, h, pos, t0, t1, ground=None, col=SAGE, kind="native", **tr):
    """Side-view tree: three lumps and a trunk down to `ground` (content y)."""
    if kind == "timber":
        lumps = [ell([w, h], [0, 0])]
    elif kind == "banana":
        lumps = [path([(0, 0), (s * w * 0.5, -h * 0.3 + k * 20)], False, i=[(0, 0), (-s * 30, -30)], o=[(s * 30, -30), (0, 0)])
                 for s in (-1, 1) for k in range(2)]
        items = [G("Fronds", *lumps, stroke(col, 14))]
        if ground is not None:
            items.append(G("Trunk", path([(0, 0), (0, ground - pos[1])]), stroke(STEM, 8)))
        return shape(name, items, pos, t0, t1, **tr)
    else:
        lumps = [ell([w * 0.6, h * 0.8], [-w * 0.2, h * 0.05]), ell([w * 0.6, h * 0.8], [w * 0.2, h * 0.05]), ell([w * 0.55, h * 0.75], [0, -h * 0.15])]
    items = [G("Crown", *lumps, fill(col))]
    if kind == "orange":
        items.insert(0, G("Fruit", *[ell([18, 18], [dx, dy]) for dx, dy in ((-40, 10), (20, -20), (50, 20), (-10, 30))], stroke(INK, 3), fill(WHITE)))
    if ground is not None:
        items.append(G("Trunk", path([(0, h * 0.2), (0, ground - pos[1])]), stroke(STEM, max(4, w * 0.03))))
    return shape(name, items, pos, t0, t1, **tr)


def shrub(name, pos, t0, t1, s=100, col=MX, outline=False, cherries=0, **tr):
    """Side-view coffee shrub, 200 px tall at s=100, base at pos."""
    leaves = []
    for k, (x, y, r) in enumerate(((-34, -60, -30), (34, -80, 30), (-38, -120, -35), (36, -140, 35), (-26, -170, -40), (24, -184, 40), (0, -200, 90))):
        leaves.append(G(f"Leaf {k + 1}", leaf_path(64), *([stroke(INK, 3)] if outline else []), fill(col), tr={"position": [x, y], "rotation": r}))
    items = []
    if cherries:
        items.append(G("Cherries", *[ell([16, 16], [(-1) ** k * 14, -70 - k * 22]) for k in range(cherries)], fill(ARA)))
    items += leaves + [G("Stem", path([(0, 0), (0, -196)]), stroke(STEM, 6))]
    return shape(name, items, pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)


def bird(k, pos, outline=False):
    p = path([(-16, 0), (-26, -8), (-26, 6)], True)
    st = [stroke(INK, 2)] if outline else []
    return G(f"Bird {k}", ell([28, 16], [0, 0]), ell([12, 12], [14, -8]), p, *st, *([] if outline else [fill(INK)]),
             tr={"position": list(pos)})


def bag(name, pos, t0, t1, **tr):
    st = [G("Bird", ell([22, 12], [0, 6]), ell([9, 9], [10, 1]), fill(INK)), G("Stamp", ell([90, 90], [0, 0]), stroke(INK, 3), fill(WHITE))]
    body = [G("Fold", path([(-130, -130), (130, -130)]), stroke(INK, 3)), G("Bag", rect([260, 340], None, 10), stroke(INK, 4), fill(WHITE))]
    return shape(name, [G("Seal", *st, tr={"position": [0, 30]})] + body, pos, t0, t1, **tr)


def arrow(name, a, b, t, t1, col=INK, w=4):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    hd = [(b[0] - 18 * math.cos(ang - 0.5), b[1] - 18 * math.sin(ang - 0.5)), b, (b[0] - 18 * math.cos(ang + 0.5), b[1] - 18 * math.sin(ang + 0.5))]
    return shape(name, [G("A", path([a, b]), path(hd), trim(0, A(K(t, 0), K(t + 0.5, 100))), stroke(col, w))], [0, 0], t, t1)


def tag(name, s, pos, t, t1, size=16, color=INK, just="center", **tr):
    return appear(caps(name, s, pos, t, t1, size=size, color=color, just=just, **tr), t)


# =====================================================================
# THE TRANSECT (S1 end, S2, S3): ground at y = TG, five zones of 1,920 px
# =====================================================================
TG, ZW = 820, 1920
MAIN = (CX, 330, 500, 300)
INGA_T = 6720
ZONES = ["RUSTIC", "TRADITIONAL POLYCULTURE", "COMMERCIAL POLYCULTURE", "SHADED MONOCULTURE", "SUN"]


def transect(prefix, t0, t1, rg, only_main=False, pop=None, grey_t=None):
    """The whole slope. only_main: just the S1/S2 crown and shrub. pop: time the other rustic crowns pop on."""
    col = A(K(grey_t, MX), K(grey_t + 0.3, GREY2)) if grey_t is not None else MX
    out = [shrub(f"{prefix}Shrub", [CX - 40, TG], t0, t1, s=130, col=col, outline=grey_t is not None, parent=rg)]
    out.append(crown(f"{prefix}Main Crown", MAIN[2], MAIN[3], [MAIN[0], MAIN[1]], t0, t1, ground=TG, parent=rg))
    if only_main:
        return out
    rnd = random.Random(3)
    trees = [(380, 260, 460, 280, "native"), (1560, 240, 520, 300, "native")]
    trees += [(2200, 300, 420, 240, "native"), (2650, 640, 200, 130, "orange"), (3000, 560, 220, 200, "banana"), (3400, 280, 400, 230, "native")]
    trees += [(4100, 360, 130, 300, "timber"), (4450, 620, 200, 130, "orange"), (4800, 340, 140, 320, "timber"), (5150, 560, 220, 200, "banana"),
              (5500, 360, 130, 300, "timber")]
    trees += [(x, 380, 380, 220, "inga") for x in (6240, 6720, 7200)]
    for k, (x, y, w, h, kind) in enumerate(trees):
        tt = pop if (pop is not None and x < ZW) else t0
        sc = grow(tt, 100, 0.5) if (pop is not None and x < ZW) else [100, 100]
        out.append(crown(f"{prefix}Tree {k + 1}", w, h, [x, y], tt, t1, ground=TG, kind="native" if kind == "inga" else kind, parent=rg, scale=sc))
    xs = list(range(ZW + 120, 4 * ZW, 240)) + list(range(4 * ZW + 60, 5 * ZW, 130))
    gs = []
    for k, x in enumerate(xs):
        gs.append(G(f"S{k}", *[G(f"L{j}", leaf_path(56), fill(MX), tr={"position": [(-1) ** j * 26, -50 - j * 30], "rotation": (-1) ** j * 35}) for j in range(5)],
                    G("Stem", path([(0, 0), (0, -170)]), stroke(STEM, 6)), tr={"position": [x, TG]}))
    out.append(shape(f"{prefix}Rows", gs, [0, 0], t0, t1, parent=rg))
    rays = [path([(4 * ZW + 100 + k * 220, TG - 900), (4 * ZW + 40 + k * 220, TG - 260)]) for k in range(9)]
    out.append(shape(f"{prefix}Sun Rays", [G("R", *rays, stroke(GREY2, 6))], [0, 0], t0, t1, parent=rg))
    out.append(shape(f"{prefix}Ground", [G("G", path([(-600, TG), (5 * ZW + 600, TG)]), stroke(GREY2, 5))], [0, 0], t0, t1, parent=rg))
    return out


# =====================================================================
# THE FARM CROSS-SECTION (S4-S6, S10): ground at y = FG
# =====================================================================
FG = 640
FARM_CROWNS = [(160, 300, 260, 150), (420, 200, 380, 220), (580, 120, 300, 150), (640, 330, 220, 130), (820, 250, 280, 160),
               (1000, 200, 380, 220), (1120, 110, 300, 150), (1190, 320, 230, 140), (1370, 230, 300, 170), (1560, 190, 380, 220),
               (1740, 320, 240, 140)]
INGA = (1000, 200)
V_TOP = ((-96, 96), 1.1)
V_ROOT = ((-96, -390), 1.1)
V_FULL = ((60, 300), 0.55)
SHRUB_X = list(range(120, 1820, 150))


def farm(prefix, t0, t1, rg, crowns=True):
    out = []
    if crowns:
        for k, (x, y, w, h) in enumerate(FARM_CROWNS):
            out.append(crown(f"{prefix}Crown {k + 1}", w, h, [x, y], t0, t1, ground=FG, parent=rg))
    gs = []
    for k, x in enumerate(SHRUB_X):
        gs.append(G(f"S{k}", *[G(f"L{j}", leaf_path(40), fill(MX), tr={"position": [(-1) ** j * 18, -30 - j * 18], "rotation": (-1) ** j * 35}) for j in range(5)],
                    G("C", ell([10, 10], [8, -50]), ell([10, 10], [-8, -70]), fill(ARA)),
                    G("Stem", path([(0, 0), (0, -110)]), stroke(STEM, 4)), tr={"position": [x, FG]}))
    out.append(shape(f"{prefix}Coffee", gs, [0, 0], t0, t1, parent=rg))
    lit = [G(f"L{k}", leaf_path(30), fill(SAGE), tr={"position": [30 + k * 38, FG + 8], "rotation": (k * 37) % 50 - 25}) for k in range(49)]
    out.append(shape(f"{prefix}Litter", lit, [0, 0], t0, t1, parent=rg))
    rnd = random.Random(7)
    roots = []
    for x, y, w, h in FARM_CROWNS:
        for j in range(3):
            ex = x + rnd.uniform(-120, 120)
            roots.append(path([(x, FG + 10), (x + (ex - x) * 0.4, FG + 120), (ex, FG + rnd.uniform(200, 280))]))
    out.append(shape(f"{prefix}Roots", [G("R", *roots, stroke(GREY2, 4))], [0, 0], t0, t1, parent=rg))
    out.append(shape(f"{prefix}Ground", [G("G", path([(-400, FG), (2400, FG)]), stroke(INK, 4))], [0, 0], t0, t1, parent=rg))
    return out


# =====================================================================
# SCENE 1 - TREETOPS (16 s)
# =====================================================================
def aerial(prefix, t0, t1, rg, pop=True):
    rnd = random.Random(1)
    pts = [(CX, CY, 150)]
    while len(pts) < 40:
        x, y = rnd.uniform(-450, 450), rnd.uniform(-225, 225)
        if (x / 450) ** 2 + (y / 225) ** 2 < 1 and all(math.hypot(CX + x - a, CY + y - b) > 70 for a, b, _ in pts):
            pts.append((CX + x, CY + y, rnd.uniform(90, 150)))
    gs = [G(f"C{k}", ell([d, d], [x, y]), stroke(WHITE, 4), fill(SAGE),
            tr={"anchorPoint": [x, y], "position": [x, y], "scale": grow(t0 + 0.2 + k * 0.04)} if pop else None) for k, (x, y, d) in enumerate(pts)]
    out = [shape(f"{prefix}Crowns", gs[1:], [0, 0], t0, t1, parent=rg),
           shape(f"{prefix}Centre Crown", [gs[0]], [0, 0], t0, t1, parent=rg),
           shape(f"{prefix}Ridge", [G("R", path([(380, 300), (700, 250), (1000, 270), (1300, 230), (1560, 280)]),
                                      *([trim(0, A(K(t0, 0), K(t0 + 1.2, 100)))] if pop else []), stroke(INK, 3))], [0, 0], t0, t1, parent=rg)]
    return out, pts


def s1_aerial(D):
    L = []
    ar = "Aerial Rig"
    sr = "Side Rig"
    z0, z1 = 9.0, 12.6
    s = MAIN[2] / 150
    L.append(tag("Place", "CHIAPAS, A COFFEE FARM", [CX, 860], 1.6, z0))
    al, _ = aerial("", 0, z1, ar)
    L += al
    L.append(rig(ar, z1, [(0, (0, 0), 1), (z0, (0, 0), 1), (z1, (CX - CX * s, MAIN[1] - CY * s), s)]))
    L += transect("", z1, D, sr, only_main=True)
    L[-2]["transform"]["scale"] = A(K(z1, [0, 0]), K(z1 + 0.6, [130, 130]))
    P, sc = handoff((0, 0), 1)
    L.append(rig(sr, D, [(z1, (0, 0), 1), (D, P, sc)], t0=z1))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 2 - A FOREST PLANT (21 s)
# =====================================================================
def s2_understory(D):
    L = []
    rg = "Transect Rig"
    b0 = 9.4
    L.append(shape("Ruler", [G("R", path([(160, TG), (160, 240)]), *[path([(150, y), (170, y)]) for y in (TG, TG - 260, 240)], trim(0, A(K(2.0, 0), K(2.8, 100))),
                             stroke(INK, 3))], [0, 0], 2.0, D))
    L.append(tag("Ruler Shrub", "SHRUB", [190, TG - 254], 2.6, D, size=14, just="left"))
    L.append(tag("Ruler Tree", "CANOPY ≈ 3× HIGHER", [190, 250], 2.8, D, size=14, just="left"))
    k = 2.2
    eth = (38.5, 7.5)
    o = (520, 960)
    inset = land_layer("Inset", k, 3.4, b0, bbox=(-20, -40, 60, 40), position=[o[0] - eth[0] * k, o[1] + eth[1] * k], scale=grow(3.4))
    inset["transform"]["anchorPoint"] = map_pt(eth, k)
    inset["transform"]["position"] = list(o)
    L.append(disc("Ethiopia", list(o), 16, ARA, 3.4, b0, sh=0))
    L.append(tag("Wild", "WILD ARABICA, UNDER THE FOREST CANOPY", [o[0] + 60, o[1] + 6], 3.8, b0, size=14, just="left"))
    L.append(inset)
    L.append(shape("Timeline", [G("T", path([(300, 1010), (1620, 1010)]), trim(0, A(K(b0, 0), K(b0 + 1.0, 100))), stroke(INK, 3))], [0, 0], b0, D))
    L.append(disc("Forest Icon", [300, 1010], 34, SAGE, b0, D, sh=0, scale=grow(b0)))
    L.append(tag("Forest Label", "FOREST: WHERE IT STARTED", [330, 990], b0 + 0.3, D, size=13, just="left"))
    L.append(shape("Sun Icon", [G("Rays", *[path([(14 * math.cos(a * math.pi / 4), 14 * math.sin(a * math.pi / 4)),
                                                  (24 * math.cos(a * math.pi / 4), 24 * math.sin(a * math.pi / 4))]) for a in range(8)], stroke(GREY, 3)),
                                G("Sun", ell([20, 20]), fill(GREY))], [1620, 1010], b0 + 1.4, D, scale=grow(b0 + 1.4)))
    L.append(tag("Sun Label", "SUN COFFEE, 1970s ON", [1590, 990], b0 + 1.6, D, size=13, just="right"))
    L.append(src("Src Forest", "SOURCE: PERFECTO ET AL. 1996", b0 + 1.0, D))
    for l in L:
        add_out(l, D - 0.8)
    L += transect("", 0, D, rg, pop=0.9, grey_t=0.3)
    P, sc = handoff((0, 0), 1)
    L.append(rig(rg, D, [(0, (0, 0), 1), (D, P, sc)]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 3 - ONE SLOPE, FIVE FARMS (29 s)
# =====================================================================
TS = 0.35


def s3_transect(D):
    L = []
    rg = "Transect Rig"
    p0 = (80, 640 - TG * TS)
    tk0, tk1, z0 = 8.0, 20.0, 22.0
    p1 = (CX - INGA_T * TS, p0[1])
    sI = 418 / 380
    Q = (1004 - INGA_T * sI, 316 - 380 * sI)
    P, sc = handoff(Q, sI)
    L += doc("Paper", [("Biodiversity conservation", 20, HEAD), ("in traditional coffee systems", 18, BODY), ("of Mexico", 18, BODY)],
             (400, 880), (460, 250), 2.6, 7.4, hl_line=0, credit="MOGUEL & TOLEDO 1999")
    for l in L:
        if l["name"] != "Paper Credit":
            p = l["transform"]["position"]
            p0v = p["keyframes"][-1]["value"] if isinstance(p, dict) else p
            l["transform"]["position"] = A(K(2.6, [p0v[0] - 800, p0v[1]]), K(3.2, p0v), K(6.8, p0v), K(7.4, [p0v[0] - 800, p0v[1]]))
    for k, nm in enumerate(ZONES):
        t = tk0 + (tk1 - tk0) * k / 4 - 0.6 if k else 3.2
        L.append(tag(f"Zone {k + 1}", nm, [k * ZW + 140, TG + 70], t, z0, size=44, just="left", parent=rg))
    seg = [G("Solid", rect([3300, 40], [1650, 0]), fill(MX))]
    for j in range(6):
        seg.append(G(f"Soft {j}", rect([120, 40], [3300 + 60 + j * 120, 0]), fill(MX, 85 - j * 14)))
    L.append(shape("Share Bar", seg, [0, TG + 170], 4.2, z0, parent=rg, scale=A(K(4.2, [0, 100]), K(5.2, [100, 100]))))
    L.append(tag("Share Label", "≈ 2/3 OF MEXICO'S COFFEE LAND", [40, TG + 270], 4.8, z0, size=44, just="left", parent=rg))
    L.append(src("Src Transect", "SOURCE: MOGUEL & TOLEDO 1999", 2.6, z0))
    for l in L:
        if l["out"] > z0:
            add_out(l, z0)
    L += transect("", 0, D, rg)
    L.append(rig(rg, D, [(0, (0, 0), 1), (2.4, p0, TS), (tk0, p0, TS), (tk1, p1, TS), (z0, p1, TS), (D - 0.4, P, sc)]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 4 - THE HOTTEST HOURS (32 s)
# =====================================================================
def trace(name, amp, y, x0, x1, t, t1, col, w=4):
    pts = [(x0 + (x1 - x0) * j / 48, y - amp * math.sin(2 * math.pi * j / 48)) for j in range(49)]
    return shape(name, [G("T", path(pts), trim(0, A(K(t, 0), K(t + 1.4, 100))), stroke(col, w))], [0, 0], t, t1)


def s4_hot(D):
    L = []
    cam = "Cam"
    b0, c0 = 8.0, 26.0
    rays = [path([(200 + k * 190, -400), (260 + k * 190, 80 if k % 3 else 520)]) for k in range(9)]
    L.append(shape("Rays", [G("R", *rays, trim(0, A(K(1.0, 0), K(2.4, 100))), stroke(GREY2, 6))], [0, 0], 1.0, c0, parent=cam))
    # B: the overlay
    ov = [shape("Panel", [G("P", rect([1640, 380], None, 12), stroke(INK, 3), fill(WHITE))], [CX, 850], b0, c0, scale=A(K(b0, [100, 0]), K(b0 + 0.4, [100, 100])))]
    ov.append(tag("Pin", "SOCONUSCO, CHIAPAS", [260, 720], b0 + 0.4, c0))
    for k, (s, h) in enumerate((("10–30 % SHADE", 20), ("35–65 % SHADE", 50), ("60–80 % SHADE", 70))):
        y = 790 + k * 70
        ov.append(shape(f"Station {k + 1}", [G("Shade", rect([h * 2, 12], [h - 70, -40]), fill(SAGE)), G("Mast", path([(0, 0), (0, -30)]), rect([22, 14], [0, -30]), stroke(INK, 3))],
                        [220, y + 20], b0 + 0.6 + k * 0.3, c0, scale=grow(b0 + 0.6 + k * 0.3)))
        ov.append(caps(f"Station Label {k + 1}", s, [270, y + 8], b0 + 0.7 + k * 0.3, c0, size=13, color=INK, just="left"))
    x0, x1, ym = 720, 1660, 850
    ov.append(shape("Chart Axes", [G("A", path([(x0, 700), (x0, 1000), (x1, 1000)]), stroke(INK, 3))], [0, 0], b0 + 1.4, c0))
    ov.append(caps("Chart X", "24 HOURS →", [x1, 1030], b0 + 1.4, c0, size=13, color=INK, just="right"))
    ov.append(caps("Chart Y", "TEMPERATURE SPREAD", [x0 + 10, 690], b0 + 1.4, c0, size=13, color=INK, just="left"))
    ov.append(shape("Average", [G("A", path([(x0, ym), (x1, ym)]), stroke(INK, 3, dashes=(14, 10)))], [0, 0], b0 + 2.0, c0))
    ov.append(caps("Average Label", "AVERAGE: CLOSE", [x1 - 10, ym - 14], b0 + 2.2, c0, size=13, color=INK, just="right"))
    for k, (amp, col, t) in enumerate(((120, INK, b0 + 3.0), (70, GREY, b0 + 6.0), (24, SAGE, b0 + 9.0))):
        ov.append(trace(f"Trace {k + 1}", amp, ym, x0, x1, t, c0, col, w=5 if k == 2 else 4))
    ov.append(tag("Wide", "LIGHT SHADE: WIDEST SWING", [x0 + 260, 712], b0 + 3.6, c0, size=13))
    ov.append(tag("Level", "HEAVY SHADE: STAYS LEVEL", [x1 - 240, 712], b0 + 9.6, c0, size=13, color=SAGE))
    ov.append(src("Src Lin", "SOURCE: LIN 2007, AGRICULTURAL AND FOREST METEOROLOGY", b0, c0))
    L += [l for l in ov if l["type"] == "text"] + [l for l in ov if l["type"] != "text" and l["name"] != "Panel"] + [ov[0]]
    for l in L:
        if l["out"] > c0:
            add_out(l, c0)
    L += farm("", 0, D, cam)
    P, sc = handoff(*V_TOP)
    L.append(rig(cam, D, [(0, V_TOP[0], V_TOP[1]), (c0, V_TOP[0], V_TOP[1]), (D, P, sc)]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 5 - FREE NITROGEN (27 s)
# =====================================================================
def to_screen(c, view):
    (P, s) = view
    return [P[0] + c[0] * s, P[1] + c[1] * s]


def s5_nitrogen(D):
    L = []
    cam = "Cam"
    a0, b0 = 4.2, 15.0
    rnd = random.Random(5)
    nod = [(INGA[0] + rnd.uniform(-110, 110), FG + rnd.uniform(110, 230)) for _ in range(10)]
    L.append(shape("Nodules", [G(f"N{k}", ell([18, 18], list(p)), stroke(INK, 2), fill(PULP), tr={"anchorPoint": list(p), "position": list(p), "scale": grow(a0 + k * 0.1)})
                               for k, p in enumerate(nod)], [0, 0], a0, D, parent=cam))
    air = [(nod[k][0] + rnd.choice((-1, 1)) * 60, nod[k][1] - 40) for k in range(4)]
    for k, (a, b) in enumerate(zip(air, nod)):
        L.append(arrow(f"N2 Arrow {k + 1}", to_screen(a, V_ROOT), to_screen(b, V_ROOT), a0 + 1.4 + k * 0.2, b0))
    L.append(tag("N2", "N₂ → NITROGEN THE TREE CAN USE", [CX, 120], a0 + 1.6, b0, size=18))
    L.append(text("Inga Name", "Chalahuite (Inga spp.)", [1480, 720], 34, INK, a0 + 2.6, b0, font=SCI))
    L.append(tag("Inga Rate", "≈ 35–40 KG N / HECTARE / YEAR", [1480, 770], a0 + 3.0, b0, size=16))
    L.append(sacks("Urea", 2, GREY2, 1480, 920, a0 + 4.4, b0, w=120, h=50))
    L.append(tag("Urea Label", "≈ 2 SACKS OF UREA", [1480, 960], a0 + 4.6, b0, size=16))
    L.append(src("Src Inga", "SOURCE: INSTITUTO DE ECOLOGÍA, XALAPA", a0 + 2.6, b0))
    for l in L:
        if l["out"] > b0:
            add_out(l, b0)
    # B: leaves drift down onto the litter, rain lands on it
    lit_y = to_screen((0, FG), V_ROOT)[1]
    for k in range(6):
        x = 300 + k * 260
        t = b0 + 0.4 + k * 0.35
        L.append(shape(f"Falling Leaf {k + 1}", [G("L", leaf_path(34), fill(SAGE))], A(K(t, [x, -60]), K(t + 2.2, [x + 40, lit_y - 6])), t, D,
                       rotation=A(K(t, -60), K(t + 2.2, 15))))
    rain = [G(f"R{k}", path([(0, 0), (0, 24)]), stroke(WATER, 4),
              tr={"position": X(f"[{rnd.uniform(100, 1820):.0f}, (time * 700 + {rnd.uniform(0, 400):.0f}) % ({lit_y:.0f} + 40) - 40]")}) for k in range(24)]
    L.append(shape("Rain", rain, [0, 0], b0 + 3.0, D))
    L.append(tag("Rain Label", "RAIN LANDS ON LITTER, NOT BARE SOIL", [CX, 120], b0 + 3.6, D, size=18))
    L += farm("", 0, D, cam)
    P, sc = handoff(*V_ROOT)
    L.append(rig(cam, D, [(0, V_TOP[0], V_TOP[1]), (1.0, V_TOP[0], V_TOP[1]), (a0, V_ROOT[0], V_ROOT[1]), (D - 1.0, V_ROOT[0], V_ROOT[1]), (D, P, sc)]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 6 - WHAT THE BIRD CHECKS (42 s)
# =====================================================================
K6, P67 = 7.0, (760, 700)


def s6_birds(D):
    L = []
    cam = "Cam"
    t_up, c1, c2, c3, c4 = 3.0, 4.4, 7.4, 10.4, 13.4
    b0, s0, d0 = 17.0, 25.0, 33.0
    L.append(bag("Bag", A(K(c1 - 0.8, [2200, 520]), K(c1, [1680, 520]), K(b0, [1680, 520]), K(b0 + 0.6, [2300, 520])), c1 - 0.8, b0 + 0.6))
    conds = []
    conds.append(shape("Height Ruler", [G("R", path([(1250, FG), (1250, 80)]), path([(1236, 80), (1264, 80)]), trim(0, A(K(c1, 0), K(c1 + 0.6, 100))), stroke(INK, 4))],
                       [0, 0], c1, s0, parent=cam))
    conds.append(caps("Height Label", "≥ 12 M", [1270, 160], c1 + 0.4, s0, size=30, color=INK, just="left", parent=cam))
    conds.append(shape("Cover", [G("C", rect([1500, 40], [960, FG - 20]), stroke(INK, 4, dashes=(18, 12)))], [0, 0], c2, s0, parent=cam,
                       scale=A(K(c2, [0, 100]), K(c2 + 0.6, [100, 100])), anchorPoint=[210, 0], position=[210, 0]))
    conds.append(caps("Cover Label", "≥ 40 % COVER", [210, FG - 60], c2 + 0.4, s0, size=30, color=INK, just="left", parent=cam))
    tags = []
    for k, (x, y, w, h) in enumerate(FARM_CROWNS):
        t = c3 + k * 0.12
        tags.append(G(f"T{k + 1}", ell([34, 34], [x, y - h * 0.45]), stroke(INK, 2), fill(WHITE), tr={"anchorPoint": [x, y - h * 0.45], "position": [x, y - h * 0.45],
                                                                                                    "scale": grow(t, 100, 0.25)}))
    conds.append(shape("Species Tags", tags, [0, 0], c3, s0, parent=cam))
    conds.append(caps("Species Label", "≥ 11 TREE SPECIES", [CX, 60], c3 + 1.4, s0, size=20, color=INK))
    conds.append(shape("Organic Stamp", [G("S", rect([300, 70], None, 8), stroke(INK, 4))], to_screen((960, FG + 70), V_TOP), c4, s0, scale=grow(c4)))
    conds.append(caps("Organic Label", "ORGANIC FIRST", [to_screen((960, FG + 70), V_TOP)[0], to_screen((960, FG + 70), V_TOP)[1] + 8], c4, s0, size=20, color=INK))
    for j, t in enumerate((c2, c3, c4)):
        dim([l for l in conds[: 2 * (j + 1)] if l["name"] not in ("Species Tags",)], t, 28)
    L += conds
    L.append(src("Src Norms", "SOURCE: SMITHSONIAN BIRD FRIENDLY NORMS", c1, b0))
    # B: birds on the branches and a count
    rnd = random.Random(6)
    spots = []
    for x, y, w, h in FARM_CROWNS:
        for j in range(3):
            spots.append((x + rnd.uniform(-w * 0.35, w * 0.35), y - h * 0.3 + rnd.uniform(-20, 30)))
    rnd.shuffle(spots)
    solid = [bird(k, p) for k, p in enumerate(spots[:22])]
    for k, g in enumerate(solid):
        g["transform"]["opacity"] = A(K(b0 + 0.6 + k * 0.08, 0), K(b0 + 0.7 + k * 0.08, 100))
    migr = [bird(k, p, outline=True) for k, p in enumerate(spots[22:30])]
    for k, g in enumerate(migr):
        g["transform"]["opacity"] = A(K(b0 + 1.6 + k * 0.1, 0), K(b0 + 1.7 + k * 0.1, 100))
    L.append(shape("Migrants", migr, [0, 0], b0 + 1.6, d0, parent=cam))
    L.append(shape("Birds", solid, [0, 0], b0 + 0.6, d0, parent=cam))
    L += wipe_text("Count", "150+ species", [CX, 120], 60, INK, b0 + 2.4, d0, hl=True)
    L.append(src("Src Birds", "SOURCE: SMITHSONIAN MIGRATORY BIRD CENTER", b0, s0))
    # C: the sun half
    gy = to_screen((0, FG), V_TOP)[1]
    L.insert(0, shape("Sun Half", [G("Split", path([(0, -60), (0, gy - 4)]), stroke(INK, 4)), G("V", rect([CX + 40, gy + 60], [CX / 2 + 20, (gy - 60) / 2]), fill(WHITE))],
                      [CX, 0], s0, d0, scale=A(K(s0, [0, 100]), K(s0 + 0.7, [100, 100])), anchorPoint=[0, 0]))
    few = [bird(k, (1200 + k * 160, gy - 130 - (k % 2) * 20)) for k in range(4)]
    L.insert(0, shape("Sun Birds", few, [0, 0], s0 + 0.8, d0))
    L.insert(0, tag("Sun Label", "SUN FARMS: FEWER BIRDS, FOREST SPECIES FIRST TO GO", [1440, 300], s0 + 1.0, d0, size=16))
    cnt = [l for l in L if l["name"].startswith("Count")]
    L = cnt + [l for l in L if l not in cnt]
    L.append(src("Src Sun", "SOURCE: GREENBERG ET AL. 1997; PHILPOTT ET AL. 2008", s0, d0))
    for l in L:
        if l["out"] > d0:
            add_out(l, d0)
    # D: the world map, a migrant's route north and back to the farm dot (6->7 handoff)
    o = inv(P67)
    k = K6 / HS
    ws = lambda ll: screen(ll, k, CHIAPAS_LL, o)
    land = land_layer("World", k, d0, D, bbox=(-130, 0, -55, 60))
    land["transform"]["position"] = [o[0] - CHIAPAS_LL[0] * k, o[1] + CHIAPAS_LL[1] * k]
    gl = ws(GREAT_LAKES)
    L.append(disc("Farm Dot", o, 22 / HS, MX, d0, D, sh=0))
    L.append(shape("Route", [G("R", arc(o, gl, -0.25), arc(gl, o, -0.25), trim(0, A(K(d0 + 0.6, 0), K(d0 + 4.0, 100))), stroke(INK, 3))], [0, 0], d0 + 0.6, D))
    L.append(shape("Migrant", [bird("M", [0, 0], outline=True)], A(K(d0 + 0.6, list(o)), K(d0 + 2.3, gl), K(d0 + 4.0, list(o))), d0 + 0.6, d0 + 4.0,
                                     scale=[160, 160]))
    L.append(tag("Lakes", "GREAT LAKES", [gl[0], gl[1] - 30], d0 + 2.0, D, size=14))
    L.append(land)
    L += farm("", 0, d0, cam)
    L.append(rig(cam, d0, [(0, V_ROOT[0], V_ROOT[1]), (0.5, V_ROOT[0], V_ROOT[1]), (t_up, V_TOP[0], V_TOP[1])]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 7 - NITROGEN NOBODY BUYS (29 s)
# =====================================================================
KM = 45
SACK_W, SACK_H = 160, 56
SUN_BAR = (760, 900)


def mex_map(name, t0, t1, rg, organic_t=None, land_out=None):
    """Land, states and the two organic states at KM px/deg, in content coordinates (map_pt)."""
    st = [path([map_pt(p, KM) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    land = []
    for r in GEO["land"]:
        lo, la = [p[0] for p in r], [p[1] for p in r]
        if max(lo) < -130 or min(lo) > -55 or max(la) < 0 or min(la) > 60:
            continue
        land.append(path([map_pt(p, KM) for p in r], True))
    out = []
    if organic_t is not None:
        for j, s in enumerate(("Chiapas", "Oaxaca")):
            out.append(shape(f"{name} {s}", [G(s, *[path([map_pt(p, KM) for p in r], True) for r in GEO["mexico"][s]], fill(MX))], [0, 0],
                             organic_t + j * 0.3, t1, parent=rg))
    out.append(shape(name, [G("Borders", *st, stroke(WHITE, 3)), G("States", *st, fill(LAND))], [0, 0], t0, t1, parent=rg))
    out.append(shape(f"{name} World", [G("Land", *land, fill(LAND))], [0, 0], t0, land_out, parent=rg))
    return out


def s7_organic(D):
    L = []
    rg = "Map Rig"
    a1, b0, c0, e0 = 3.0, 9.0, 17.0, 25.0
    cp = map_pt(CHIAPAS_LL, KM)
    s_a = K6 / KM
    P0 = (P67[0] - cp[0] * s_a, P67[1] - cp[1] * s_a)
    mx = map_pt((-99, 21), KM)
    P1 = (CX - mx[0], CY - mx[1])
    P2 = (P1[0] - 520, P1[1])
    L.append(disc("Farm Dot", A(K(0, list(P67)), K(a1, [P1[0] + cp[0], P1[1] + cp[1]]), K(b0, [P1[0] + cp[0], P1[1] + cp[1]]), K(b0 + 0.8, [P2[0] + cp[0], P2[1] + cp[1]])),
                  22, MX, 0, D, sh=0))
    rnd = random.Random(7)
    trees = []
    for j in range(16):
        ll = (rnd.uniform(-97.5, -91.5), rnd.uniform(15.5, 18.0))
        p = map_pt(ll, KM)
        t = a1 + 1.4 + j * 0.06
        trees.append(G(f"T{j}", ell([16, 16], p), fill(SAGE), tr={"anchorPoint": p, "position": p, "scale": grow(t, 100, 0.25)}))
    L.append(shape("Tree Icons", trees, [0, 0], a1 + 1.4, D, parent=rg))
    L += mex_map("Mexico", 0, D, rg, organic_t=a1 + 0.4, land_out=a1 + 0.6)
    L.append(rig(rg, D, [(0, P0, s_a), (a1, P1, 1), (b0, P1, 1), (b0 + 0.8, P2, 1)]))
    # B: the organic bar chart
    bx, py = 1000, 4
    bars = [("ETHIOPIA", 183, GREY2, 330), ("PERU", 169, GREY2, 430), ("MEXICO", 83, MX, 530)]
    L.append(tag("Bars Title", "CERTIFIED ORGANIC COFFEE LAND, 2021", [bx, 260], b0 + 0.6, D, just="left"))
    for k, (nm, v, col, y) in enumerate(bars):
        t = b0 + 1.0 + k * 0.4
        L.append(shape(f"Bar {nm}", [G("B", rect([v * py, 50], [v * py / 2, 0]), fill(col))], [bx, y], t, D, scale=A(K(t, [0, 100]), K(t + 0.6, [100, 100]))))
        L.append(caps(f"Bar {nm} Label", f"{nm} ≈ {v},000 HA", [bx + v * py + 16, y + 6], t + 0.4, D, size=14, color=INK, just="left"))
    cdmx = [(-120, -40), (-60, -95), (40, -100), (120, -50), (130, 40), (60, 100), (-40, 95), (-110, 50)]
    L.append(shape("CDMX", [G("C", path(cdmx, True), stroke(INK, 3, dashes=(10, 8)))], [bx + 140, 720], b0 + 3.0, D, scale=grow(b0 + 3.0)))
    L.append(tag("CDMX Label", "MEXICO'S ORGANIC COFFEE LAND ≈ HALF THE AREA OF MEXICO CITY (OUTLINE)", [bx, 850], b0 + 3.4, D, size=13, just="left"))
    L.append(src("Src Organic", "SOURCE: FIBL 2021 DATA, VIA AGRARIA.PE", b0 + 0.6, D))
    # C: no synthetic sack; nitrogen from the nodules and compost; the coffee sacks stack up
    L.append(shape("Fert Sack", [G("X", path([(-40, -50), (40, 50)]), path([(40, -50), (-40, 50)]), stroke(INK, 6),
                                   tr={"opacity": A(K(c0 + 1.2, 0), K(c0 + 1.3, 100))}),
                                 G("S", rect([90, 120], None, 14), stroke(INK, 3), fill(GREY2))],
                   A(K(c0, [2100, 960]), K(c0 + 1.0, [1500, 960])), c0, e0))
    L.append(caps("Fert Label", "SYNTHETIC N", [1500, 1050], c0 + 1.0, e0, size=13, color=INK))
    L.append(disc("Nodule Inset", [1180, 980], 70, PULP, c0 + 1.6, e0, line=INK, sh=0, scale=grow(c0 + 1.6)))
    L.append(arrow("Nodule Arrow", (1180, 940), (bx + 120, 560), c0 + 2.0, e0, col=MX))
    L.append(shape("Pulp", [G("P", ell([110, 50]), fill(ARA_DARK))], [1780, 760], c0 + 2.6, e0, scale=grow(c0 + 2.6)))
    L.append(caps("Pulp Label", "COMPOST", [1780, 810], c0 + 2.8, e0, size=13, color=INK))
    L.append(arrow("Pulp Arrow", (1720, 740), (bx + 340, 560), c0 + 3.0, e0, col=MX))
    for l in L:
        if l["out"] > e0 and l["name"] not in ("Farm Dot", rg) and l.get("parent") != rg:
            add_out(l, e0)
    for l in L:
        if l.get("parent") == rg or l["name"] == "Farm Dot":
            add_out(l, e0)
    stk = sacks("Coffee Sacks", 10, KRAFT, 0, 0, c0 + 4.0, D, w=SACK_W, h=SACK_H)
    s1 = 30
    stk["transform"]["position"] = A(K(c0 + 4.0, [bx + 83 * py + 300, 600]), K(e0 + 0.4, [bx + 83 * py + 300, 600]), K(D - 0.4, inv(SUN_BAR)))
    stk["transform"]["scale"] = A(K(e0 + 0.4, [s1, s1]), K(D - 0.4, [100 / HS, 100 / HS]))
    L.insert(0, stk)
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 8 - THE PRICE OF SHADE (23 s, the turn)
# =====================================================================
SHADE_BAR = (1160, 900)
STEP = SACK_H + 4


def s8_yield(D):
    L = []
    b0, z0 = 9.0, 15.4
    L.append(sacks("Sun Bar", 10, KRAFT, SUN_BAR[0], SUN_BAR[1], 0, z0, w=SACK_W, h=SACK_H))
    sh = sacks("Shade Bar", 8, KRAFT, SHADE_BAR[0], SHADE_BAR[1], 1.0, z0, w=SACK_W, h=SACK_H)
    L.append(sh)
    top = SHADE_BAR[1] - 8.2 * STEP
    L.append(shape("Shade Fifth", [G("S", rect([SACK_W, 0.2 * STEP - 4], [0, -(8 * STEP) - (0.2 * STEP - 4) / 2]), fill(KRAFT))], list(SHADE_BAR), 1.6, z0))
    gap = [G(f"G{j}", rect([SACK_W, SACK_H], [0, -(8.2 * STEP) - j * STEP - SACK_H / 2 - 2], 9), stroke(GREY, 3, dashes=(10, 8))) for j in range(2)]
    gap.append(G("Box", rect([SACK_W + 30, 1.8 * STEP + 8], [0, -(9.1 * STEP)]), stroke(GREY2, 3), fill(LAND, 50)))
    L.append(shape("Gap", gap, list(SHADE_BAR), 2.6, z0, scale=grow(2.6)))
    L.append(tag("Sun Label", "FULL SUN · 100", [SUN_BAR[0], SUN_BAR[1] + 50], 0.6, z0))
    L.append(tag("Shade Label", "≈ 45 % SHADE · 82", [SHADE_BAR[0], SHADE_BAR[1] + 50], 1.4, z0))
    L.append(text("Minus", "−18 %", [SHADE_BAR[0] + 200, top - 50], 56, INK, 3.4, z0, font=HEAD, scale=grow(3.4)))
    L.append(src("Src Vaast", "SOURCE: VAAST ET AL. 2006, COSTA RICA", 1.0, z0))
    L.append(tag("Bigger", "BIGGER BEANS, BETTER CUP", [SHADE_BAR[0] + 120, top + 120], b0, z0, just="left"))
    L.append(tag("Kilo", "COFFEE IS SOLD BY THE KILO", [SHADE_BAR[0] + 120, top - 150], b0 + 1.6, z0, just="left"))
    for l in L:
        add_out(l, z0)
    # the top edge of the shade bar becomes the leaf's midrib (8->9 handoff)
    mid = 630
    L.insert(0, shape("Top Edge", [G("E", path([(-SACK_W / 2, 0), (SACK_W / 2, 0)]), stroke(INK, 5))], A(K(z0 - 0.6, [SHADE_BAR[0], top]), K(D - 0.4, inv((CX, CY)))),
                      z0 - 0.6, D, scale=A(K(z0 - 0.6, [100, 100]), K(D - 0.4, [mid / SACK_W * 100 / HS, 100]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 9 - SHADE AND ROYA (27 s)
# =====================================================================
LEAF9 = 800


def s9_roya(D):
    L = []
    lr = "Leaf Rig"
    a1, b0, c0, d0 = 2.0, 9.0, 17.0, 23.4
    rnd = random.Random(9)
    beads = [G(f"W{k}", ell([16, 12], [rnd.uniform(-300, 300), rnd.uniform(20, 110)]), fill(WATER),
               tr={"opacity": A(K(a1 + 0.6 + k * 0.05, 0), K(a1 + 0.7 + k * 0.05, 100), K(c0, 100), K(c0 + 0.6, 30))}) for k in range(22)]
    spots = []
    for k in range(9):
        p = [rnd.uniform(-260, 260), rnd.uniform(-90, 90)]
        spots.append(G(f"R{k}", ell([34, 34], p), fill(RUST),
                       tr={"anchorPoint": p, "position": p, "scale": A(K(b0 + 1.2 + k * 0.1, [0, 0]), K(b0 + 2.6 + k * 0.1, [100, 100]), K(13.6, [100, 100]),
                                                                       K(14.6, [55, 55]), K(c0 + 1.6, [55, 55]), K(c0 + 3.2, [0, 0]))}))
    L.append(shape("Rust", spots, [CX, CY], b0 + 1.2, d0, parent=lr))
    L.append(shape("Film", beads, [CX, CY], a1 + 0.6, d0, parent=lr))
    L.append(shape("Leaf", [G("Mid", path([(-LEAF9 * 0.4, 0), (LEAF9 * 0.38, 0)]), stroke(INK, 5)), G("L", leaf_path(LEAF9), stroke(INK, 4), fill(MX))], [CX, CY], 0, D,
                   parent=lr, scale=A(K(0.2, [100, 0]), K(1.2, [100, 100]))))
    L.append(tag("Land", "LAND IN WATER", [CX, 780], a1 + 0.8, b0, size=18))
    L.append(crown("Crown", 520, 200, [CX, 150], a1 + 2.4, d0, scale=grow(a1 + 2.4)))
    L.append(shape("Clock", [G("Hand", path([(0, 0), (0, -24)]), stroke(INK, 4), tr={"rotation": X("time * 200")}), G("Face", ell([64, 64]), stroke(INK, 4), fill(WHITE))],
                   [1600, 300], a1 + 3.0, b0))
    L.append(tag("Wet", "UNDER THE TREE, THE FILM STAYS LONGER", [1600, 370], a1 + 3.4, b0, size=13))
    # B: two arrows on one MORE SHADE axis
    ay_ = 960
    L.append(tag("Axis", "MORE SHADE", [CX, ay_ + 10], b0, c0, size=16))
    L.append(arrow("To Rust", (CX - 120, ay_), (CX - 700, ay_), b0 + 0.6, c0, col=RUST, w=5))
    L.append(arrow("To Less", (CX + 120, ay_), (CX + 700, ay_), b0 + 3.6, c0, col=INK, w=5))
    L.append(tag("More Rust", "WETTER LEAF: MORE RUST", [CX - 700, ay_ - 30], b0 + 1.0, c0, size=15, color=RUST, just="left"))
    L.append(tag("Less Rust", "FEWER CHERRIES: LESS RUST", [CX + 700, ay_ - 30], b0 + 4.0, c0, size=15, just="right"))
    L.append(shape("Cherries", [G(f"C{k}", ell([30, 30], [-200 + k * 80, 0]), fill(ARA),
                                  tr={"opacity": A(K(13.6, 100), K(13.7, 0))} if k % 3 else None) for k in range(6)], [CX, 740], b0 + 3.6, c0, scale=grow(b0 + 3.6)))
    L.append(src("Src Lopez", "SOURCE: LÓPEZ-BRAVO, AVELINO ET AL. 2012", b0, c0))
    # C: layered crowns
    for k, (x, y, w) in enumerate(((CX - 420, 180, 360), (CX + 430, 190, 380), (CX - 150, 110, 300), (CX + 200, 100, 320))):
        t = c0 + 0.4 + (0 if k < 2 else 1.4) + (k % 2) * 0.2
        L.append(crown(f"Layer {k + 1}", w, 150, [x, y], t, d0, scale=grow(t)))
    L.append(tag("Layers", "CHIAPAS: MORE LAYERS OF TREES, LESS RUST", [CX, 960], c0 + 2.4, d0, size=16))
    L.append(src("Src Soto", "SOURCE: SOTO-PINTO ET AL. 2002", c0, d0))
    for l in L:
        if l["out"] > d0 and l.get("parent") != lr:
            add_out(l, d0)
    # D: the leaf shrinks into the coffee layer (9->10 handoff)
    tgt = to_screen((SHRUB_X[6], FG - 60), V_FULL)
    L.append(null(lr, [CX, CY], 0, D, position=A(K(d0, [CX, CY]), K(D - 0.4, inv(tgt))), scale=A(K(d0, [100, 100]), K(D - 0.4, [40 * 0.55 / LEAF9 * 100 / HS] * 2))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 10 - THE LEDGER (22 s)
# =====================================================================
def s10_ledger(D):
    L = []
    cam = "Cam"
    a0, b0, z0 = 1.0, 11.0, 17.0
    beam = "Beam"
    bx, by = 1560, 560
    tilt = A(K(a0 + 4.0, 0), K(a0 + 5.6, -6))
    L.append(caps("Work Col", "WORK THE TREES DO", [bx - 180, by - 280], a0, z0, size=14, color=INK, parent=beam))
    L.append(caps("Cost Col", "WHAT IT COSTS", [bx + 200, by - 280], a0, z0, size=14, color=INK, parent=beam))
    items = [("Trace", (520, 330), (bx - 180, by - 200)), ("Urea", (620, 700), (bx - 180, by - 120)), ("Litter", (700, 660), (bx - 180, by - 40))]
    t = a0 + 0.6
    for nm, src_p, dst in items:
        if nm == "Trace":
            g = [G("T", path([(-60 + j * 5, -10 * math.sin(j / 24 * 2 * math.pi) * 0.4) for j in range(25)]), stroke(SAGE, 5))]
            lab = "STEADIER HOURS"
        elif nm == "Urea":
            g = [G("S", rect([50, 24], [-30, 0], 8), rect([50, 24], [30, 0], 8), fill(GREY2))]
            lab = "≈ 2 SACKS OF UREA"
        else:
            g = [G("L", *[leaf_path(22) for _ in range(1)], fill(SAGE), tr={"position": [-30, 0]}), G("L2", leaf_path(22), fill(SAGE), tr={"position": [0, 0]}),
                 G("L3", leaf_path(22), fill(SAGE), tr={"position": [30, 0]})]
            lab = "GROUND COVER"
        L.append(shape(f"Item {nm}", g, A(K(t, list(src_p)), K(t + 0.9, list(dst))), t, z0, parent=beam))
        L.append(caps(f"Item {nm} Label", lab, [dst[0] - 90, dst[1] + 6], t + 0.9, z0, size=12, color=INK, just="right", parent=beam))
        t += 1.0
    L.append(shape("Item Gap", [G("G", rect([70, 70]), stroke(GREY, 3, dashes=(8, 6)))], A(K(t, [1300, 900]), K(t + 0.9, [bx + 200, by - 120])), t, z0, parent=beam))
    L.append(caps("Item Gap Label", "−18 % COFFEE", [bx + 200, by - 60], t + 0.9, z0, size=12, color=INK, parent=beam))
    L.append(shape(beam, [G("B", path([(bx - 300, by), (bx + 300, by)]), stroke(INK, 5))], [bx, by], a0, z0, anchorPoint=[bx, by], position=[bx, by], rotation=tilt))
    L.append(shape("Fulcrum", [G("F", path([(0, 0), (-30, 50), (30, 50)], True), fill(INK))], [bx, by + 4], a0, z0))
    L.append(tag("Lock", "ORGANIC: CAN'T BE BOUGHT", [bx - 180, by + 90], b0, z0, size=13))
    L.append(bag("Ledger Bag", [bx - 140, 860], b0 + 1.4, z0, scale=[30, 30]))
    L.append(tag("Buyer", "WHAT THE BUYER PAYS FOR", [bx - 90, 866], b0 + 1.6, z0, size=13, just="left"))
    for l in L:
        if l["out"] > z0 and l["type"] != "null":
            add_out(l, z0)
    L += farm("", 0, D, cam)
    s = 600 / 380
    Q = (CX - INGA[0] * s, CY - INGA[1] * s)
    P, sc = handoff(Q, s)
    L.append(rig(cam, D, [(0, V_FULL[0], V_FULL[1]), (z0, V_FULL[0], V_FULL[1]), (D - 0.3, P, sc)]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 11 - TREETOPS AGAIN (13 s)
# =====================================================================
def s11_close(D):
    L = []
    ar = "Aerial Rig"
    s = 600 / 150
    for k, (s_, dx, dy, t) in enumerate((("STEADIER HOURS", -300, -120, 3.4), ("NITROGEN", 260, -60, 4.0), ("GROUND COVER", -180, 140, 4.6), ("−18 %", 340, 150, 5.2))):
        L.append(disc(f"Pin {k + 1}", [CX + dx, CY + dy], 12, INK, t, D, sh=0, scale=grow(t)))
        L.append(tag(f"Label {k + 1}", s_, [CX + dx + 16, CY + dy + 6], t + 0.1, D, size=15, just="left"))
    L += wipe_text("End Title", "The Shade Forest in Your Cup", [CX, 960], 60, INK, 7.4, D)
    L.append(word_marker("End Swipe", "The Shade Forest in Your Cup", "Forest", CX, 960, 60, 8.2, D))
    L.append(tag("Place", "CHIAPAS, A COFFEE FARM", [CX, 860], 2.6, D))
    al, _ = aerial("", 0, D, ar, pop=False)
    L += al
    L.append(rig(ar, D, [(0, (CX - CX * s, CY - CY * s), s), (3.0, (0, 0), 1)]))
    L.append(bg(D))
    return L


SCENES = [("S1_Aerial", 16.0, s1_aerial), ("S2_Understory", 21.0, s2_understory), ("S3_Transect", 29.0, s3_transect), ("S4_HotHours", 32.0, s4_hot),
          ("S5_Nitrogen", 27.0, s5_nitrogen), ("S6_BirdCheck", 42.0, s6_birds), ("S7_Organic", 29.0, s7_organic), ("S8_Yield", 23.0, s8_yield),
          ("S9_Roya", 27.0, s9_roya), ("S10_Ledger", 22.0, s10_ledger), ("S11_Close", 13.0, s11_close)]

if __name__ == "__main__":
    write(SCENES, "Shade_Forest", "04_shade_forest")
