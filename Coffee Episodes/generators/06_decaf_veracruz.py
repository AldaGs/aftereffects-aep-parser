"""Generator for episode 6, "How Decaf Is Made, in Veracruz" (scripts/06_decaf_veracruz_script.md).

    python "Coffee Episodes/generators/06_decaf_veracruz.py"      # writes ../json/06_decaf_veracruz.json

A handoff is a screen point/size: the outgoing scene ends its shape at inv(p) with size/HS, the next starts at p.

Follows episode 1's rules: 24 fps, every in/out animation a whole number of 12-frame beats (write(..., beats=True)),
and drawn vectors: beans and seeds are bean outlines with their S-shaped cut, not ellipses; rounded cups.
"""
import math, random

from coffee_common import *  # noqa: F401,F403

BAG_C, BAG_SIZE, WIN, WIN_D = (CX, 560), (420, 580), (CX, 600), 180
SEED_W, SEED_H = 520, 380
BAR_Y, BAR_X0, BAR_X1 = 860, 260, 1660
BEAN = "#6B4226"


def bean_shape(w, h):
    """Coffee bean lying on its side (w wide, h tall): episode 1's egg outline, broad end to the left."""
    return egg(h, w, e=0.1, rot=-90)


def bean_cut(w, h):
    """The S-shaped centre cut along the bean's long axis."""
    return smooth([(-w * 0.38, 0), (-w * 0.12, -h * 0.07), (w * 0.12, h * 0.07), (w * 0.38, 0)], False)


def molecule(name, atoms, bonds, pos, t, t1, **tr):
    """Ink ball-and-stick: atoms [(x, y, r, label)], bonds [(i, j, double)]."""
    gs = []
    for j, (x, y, r, lab) in enumerate(atoms):
        gs.append(G(f"Atom {j + 1}", ell([r * 2, r * 2], [x, y]), stroke(INK, 3), fill(WHITE)))
    for j, (a, b, dbl) in enumerate(bonds):
        (x1, y1), (x2, y2) = atoms[a][:2], atoms[b][:2]
        if dbl:
            nx, ny = -(y2 - y1), x2 - x1
            n = math.hypot(nx, ny) or 1
            nx, ny = nx / n * 5, ny / n * 5
            gs.append(G(f"Bond {j + 1}", path([(x1 + nx, y1 + ny), (x2 + nx, y2 + ny)]), path([(x1 - nx, y1 - ny), (x2 - nx, y2 - ny)]), stroke(INK, 3)))
        else:
            gs.append(G(f"Bond {j + 1}", path([(x1, y1), (x2, y2)]), stroke(INK, 3)))
    out = [shape(name, gs, pos, t, t1, scale=grow(t, 100, 0.4), **tr)]
    for j, (x, y, r, lab) in enumerate(atoms):
        if lab:
            out.append(text(f"{name} A{j + 1}", lab, [pos[0] + x, pos[1] + y + r * 0.35], r * 0.95, INK, t + 0.2, t1, font=LAB,
                            opacity=tr.get("opacity", fade_in(t + 0.2))))
    return out


def dots_in(rnd, n, rx, ry, cx=0, cy=0):
    pts = []
    while len(pts) < n:
        x, y = rnd.uniform(-rx, rx), rnd.uniform(-ry, ry)
        if (x / rx) ** 2 + (y / ry) ** 2 < 0.8:
            pts.append((cx + x, cy + y))
    return pts


def bag_layers(D, t, rig, prefix="", beans=True):
    out = []
    if beans:
        bs = [G(f"B{j + 1}", bean_cut(46, 32), bean_shape(46, 32), stroke("#3E2A1E", 2), fill(BEAN),
                tr={"position": p, "rotation": r}) for j, (p, r) in enumerate([((-40, -36), 20), ((30, -44), -30), ((-50, 18), -10),
                                                                              ((10, 6), 40), ((50, 30), 10), ((-10, 50), -40)])]
        out.append(shape(f"{prefix}Window Beans", bs, list(WIN), t, D, parent=rig))
    out.append(shape(f"{prefix}Window", [G("Ring", ell([WIN_D, WIN_D]), stroke(INK, 4), fill(WHITE))], list(WIN), t, D, parent=rig))
    out.append(text(f"{prefix}Bag Name", "COLOMBIA", [BAG_C[0], 420], 52, INK, t, D, font=HEAD, parent=rig))
    out.append(caps(f"{prefix}Bag Sub", "DECAF", [BAG_C[0], 462], t, D, size=20, color=INK, parent=rig))
    out.append(text(f"{prefix}Print 1", "Decaffeinated by the Mountain Water Process,", [BAG_C[0], 744], 15, INK, t, D, parent=rig))
    out.append(text(f"{prefix}Print 2", "Córdoba, Veracruz, Mexico", [BAG_C[0], 766], 15, INK, t, D, parent=rig))
    out.append(shape(f"{prefix}Bag", [G("Crimp", rect([BAG_SIZE[0], 34], [0, -BAG_SIZE[1] / 2 + 17]), stroke(INK, 4)),
                                      G("Body", rect(list(BAG_SIZE), None, 8), stroke(INK, 4), fill(KRAFT))], list(BAG_C), t, D, parent=rig))
    return out


# =====================================================================
# SCENE 1 - THE BAG (20 s)
# =====================================================================
KM, MCEN, MO = 7, (-86, 10), (1350, 520)
COL, COR, MEX_CITY, NYC = (-75.6, 5.0), (-96.93, 18.88), (-99.13, 19.43), (-74.0, 40.7)


def s1_bag(D):
    L = []
    rig = "Bag Rig"
    m0, m1 = 9.4, 14.6
    ms = lambda ll: screen(ll, KM, MCEN, MO)
    # C: map at right, bag slides left
    c, k = ms(COL), ms(COR)
    L.append(disc("Col Dot", c, 16, ARA, m0 + 0.6, m1, sh=0, scale=grow(m0 + 0.6), opacity=A(K(m1 - 0.4, 100), K(m1, 0))))
    L.append(disc("Cor Dot", k, 16, WATER, m0 + 0.8, m1, sh=0, scale=grow(m0 + 0.8), opacity=A(K(m1 - 0.4, 100), K(m1, 0))))
    L.append(shape("Route", [G("Arc", arc(c, k, -0.3), trim(0, A(K(m0 + 1.0, 0), K(m0 + 2.0, 100))), stroke(INK, 3))], [0, 0], m0 + 1.0, m1,
                   opacity=A(K(m1 - 0.4, 100), K(m1, 0))))
    L.append(appear(text("Route Km", "≈ 3,000 km", [k[0] + 40, k[1] - 70], 34, INK, m0 + 2.0, m1, font=HEAD, just="left"), m0 + 2.0))
    chord = math.dist(c, k)
    L.append(shape("Ruler", [G("R", rect([chord * 3400 / 3000, 8], [chord * 3400 / 3000 / 2, 0]), fill(GREY2))], [1120, 930], m0 + 2.6, m1,
                   scale=A(K(m0 + 2.6, [0, 100]), K(m0 + 3.2, [100, 100]))))
    L.append(appear(caps("Ruler Label", "MEXICO CITY → NEW YORK ≈ 3,400 KM", [1120, 970], m0 + 2.8, m1, size=16, color=INK, just="left"), m0 + 2.8))
    L.append(src("Src Dist", "SOURCE: GREAT-CIRCLE DISTANCE", m0 + 2.0, m1))
    for l in L[-4:]:
        add_out(l, m1 - 0.4)
    L.append(land_layer("Land", KM, m0, m1, bbox=(-170, -60, -30, 75), position=[MO[0] - MCEN[0] * KM, MO[1] + MCEN[1] * KM],
                        opacity=fade_io(m0, m1, 0.5)))
    # D: one bean slides out, scales up and fades back to a green seed
    d0 = 15.4
    seed_col = A(K(d0 + 1.0, BEAN), K(d0 + 3.4, SEED))
    L.append(shape("Seed", [G("Crease", bean_cut(SEED_W, SEED_H), stroke(SEED_LINE, 6)),
                            G("Seed", bean_shape(SEED_W, SEED_H), stroke(INK, 4), fill(seed_col))],
                   A(K(d0, [WIN[0] + 10, WIN[1]]), K(d0 + 1.6, list(inv((CX, CY))))), d0, D,
                   scale=A(K(d0, [46 / SEED_W * 100] * 2), K(d0 + 1.6, [100 / HS, 100 / HS]))))
    # B: small print with a swipe under "Veracruz"
    L.append(word_marker("Print Swipe", "Córdoba, Veracruz, Mexico", "Veracruz", BAG_C[0], 766, 15, 6.2, 9.0, font=BODY))
    L[-1]["parent"] = rig
    bag = bag_layers(D, 0, rig)
    for l in bag:
        l["transform"]["opacity"] = fade_in(0.2, 0.8)
    L += bag
    for l in L:
        if l.get("parent") == rig and l["name"] != "Print Swipe":
            add_out(l, d0 + 1.2, 0.6)
    zoom = (4.0, 6.0, 8.8, 9.4)
    L.append(null(rig, list(BAG_C), 0, D, anchor=[CX, 755],
                  position=A(K(zoom[0], [CX, 755]), K(zoom[1], [CX, 540]), K(zoom[2], [CX, 540]), K(zoom[3], [CX, 755]), K(m0, [CX, 755]), K(m0 + 0.6, [560, 755]),
                             K(m1, [560, 755]), K(m1 + 0.6, [CX, 755])),
                  scale=A(K(zoom[0], [100, 100]), K(zoom[1], [260, 260]), K(zoom[2], [260, 260]), K(zoom[3], [100, 100]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 2 - ONE PERCENT (21 s)
# =====================================================================
def s2_percent(D):
    L = []
    rnd = random.Random(2)
    b0, c0, d0 = 4.0, 11.0, 17.0
    pts = dots_in(rnd, 100, SEED_W / 2, SEED_H / 2, CX, CY)
    gs = []
    for j, p in enumerate(pts):
        tgt = [BAR_X0 + 14 + (j / 99) * (BAR_X1 - BAR_X0 - 20), BAR_Y]
        col = CAF if j == 0 else INK
        tt = b0 + j * 0.008
        tr = {"position": A(K(tt, list(p)), K(tt + 1.2, tgt)), "opacity": A(K(0.4, 0), K(0.8, 100), K(b0 + 1.4, 100), K(b0 + 1.8, 0))}
        if j == 0:
            tr["position"] = A(K(tt, list(p)), K(tt + 1.2, [BAR_X0 + 7, BAR_Y]))
            tr["scale"] = X("var p = 100 + 30 * Math.max(0, Math.sin((time - 1.5) * 5)) * (time < 4 ? 1 : 0); [p, p]")
        gs.append(G(f"D{j + 1}", ell([12, 12]), fill(col), tr=tr))
    L.append(shape("Dots", gs, [0, 0], 0.4, b0 + 1.8))
    L.append(shape("Seed", [G("Crease", bean_cut(SEED_W, SEED_H), stroke(SEED_LINE, 6), tr={"opacity": A(K(0.2, 100), K(0.5, 0))}),
                            G("Seed", bean_shape(SEED_W, SEED_H), stroke(INK, 4), fill(A(K(0.2, SEED), K(0.6, WHITE))))], [CX, CY], 0, b0 + 0.6,
                   opacity=A(K(b0, 100), K(b0 + 0.6, 0))))
    L.append(appear(caps("Seed Label", "GREEN ARABICA SEED, CUT OPEN", [CX, CY + SEED_H / 2 + 50], 0.8, b0, size=16), 0.8))
    add_out(L[-1], b0 - 0.3)
    # the composition bar
    bw = BAR_X1 - BAR_X0
    grey = shape("Bar Rest", [G("R", rect([bw - 14, 24], [(bw - 14) / 2, 0]), fill(GREY2))], [BAR_X0 + 14, BAR_Y], b0 + 1.4, D,
                 opacity=fade_in(b0 + 1.4), scale=A(K(d0 + 0.6, [100, 100]), K(d0 + 2.4, [0, 100])))
    L.append(shape("Bar Caffeine", [G("C", rect([14, 24], [7, 0]), fill(CAF))], [BAR_X0, BAR_Y], b0 + 1.4, D, opacity=fade_in(b0 + 1.4)))
    L.append(grey)
    L.append(leader("Caf Leader", (BAR_X0 + 7, BAR_Y - 20), (BAR_X0 + 7, BAR_Y - 90), b0 + 1.8, d0 + 0.4, col=CAF))
    L.append(appear(text("Caf Value", "≈ 1 %", [BAR_X0 + 24, BAR_Y - 100], 44, CAF, b0 + 2.0, d0 + 0.4, font=HEAD, just="left"), b0 + 2.0))
    L.append(appear(caps("Caf Label", "CAFFEINE", [BAR_X0 + 26, BAR_Y - 64], b0 + 2.1, d0 + 0.4, size=16, color=CAF, just="left"), b0 + 2.1))
    L.append(appear(caps("Rest Label", "EVERYTHING YOU TASTE AFTER ROASTING", [CX + 100, BAR_Y - 40], b0 + 2.6, d0 + 0.4, size=16), b0 + 2.6))
    L.append(src("Src Comp", "SOURCE: CEJA-NAVARRO ET AL. (2015); FARAH (2012)", b0 + 2.0, c0))
    for l in L[-5:]:
        add_out(l, d0)
    add_out(L[-1], c0 - 0.4)
    # C: two cups and their caffeine gauges
    cups = []
    for j, (nm, frac, lab, x) in enumerate([("Regular", 0.95, "≈ 95 mg", 700), ("Decaf", 0.08, "≈ 2–15 mg", 1220)]):
        t = c0 + j * 0.8
        cup = [G("Handle", ell([46, 46], [96, -10]), stroke(INK, 4)),
               G("Cup", smooth([(-82, -70), (82, -70), (74, 10), (50, 58), (22, 72), (-22, 72), (-50, 58), (-74, 10)], True, corners=(0, 1)),
                 stroke(INK, 4), fill(WHITE)),
               G("Saucer", smooth([(-112, 80), (0, 92), (112, 80)], False), stroke(INK, 4))]
        cups.append(shape(f"Cup {nm}", cup, [x, 420], t, D, scale=grow(t)))
        cups.append(shape(f"Gauge {nm}", [G("Fill", rect([26, 200 * frac], [0, 100 - 200 * frac / 2]), fill(CAF),
                                            tr={"scale": A(K(t + 0.4, [100, 0]), K(t + 1.2, [100, 100])), "anchorPoint": [0, 100], "position": [0, 100]}),
                                          G("Box", rect([26, 200]), stroke(INK, 2))], [x + 170, 420], t + 0.2, D, opacity=fade_in(t + 0.2)))
        cups.append(appear(caps(f"Cup {nm} Name", nm.upper(), [x, 560], t + 0.3, D, size=18, color=INK), t + 0.3))
        cups.append(appear(text(f"Cup {nm} Value", lab, [x, 610], 40, CAF, t + 0.5, D, font=HEAD), t + 0.5))
    cups.append(appear(caps("Standard", "US STANDARD: ≥ 97 % REMOVED", [CX + 10, 300], c0 + 2.0, D, size=18, color=INK), c0 + 2.0))
    cups.append(src("Src Cups", "SOURCE: USDA FOODDATA; McCUSKER ET AL. (2006)", c0 + 0.6, D))
    for l in cups:
        p = l["transform"]["position"]
        if not isinstance(p, dict):
            l["transform"]["position"] = A(K(d0, p), K(d0 + 0.8, [p[0], p[1] - 900]))
        else:
            ks = p["keyframes"]
            ks += [K(d0, ks[-1]["value"]), K(d0 + 0.8, [ks[-1]["value"][0], ks[-1]["value"][1] - 900])]
        l["out"] = min(l["out"], d0 + 0.8)
    L += cups
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 3 - BEFORE WATER (31 s)
# =====================================================================
RAIL_Y = fwd((0, BAR_Y))[1]
R_X0 = fwd((BAR_X0, 0))[0]


def yx(year):
    return 300 + (year - 1900) * 12


def s3_solvents(D):
    L = []
    a0, b0, c0, d0, e0 = 1.2, 9.6, 17.2, 25.0, 28.0
    L.append(shape("Rail", [G("R", rect(A(K(0, [14 * HS, 24 * HS]), K(0.8, [14, 6]), K(1.6, [1640 - R_X0, 6])), None), fill(A(K(0, CAF), K(0.8, GREY2))))],
                   A(K(0, [R_X0 + 7 * HS, RAIL_Y]), K(0.8, [R_X0 + 7, RAIL_Y]), K(1.6, [(R_X0 + 1640) / 2, RAIL_Y])), 0, D))
    for y in (1900, 1950, 2000):
        L.append(appear(caps(f"Year {y}", str(y), [yx(y), RAIL_Y + 40], 1.4, D, size=16), 1.4))
    L.append(appear(caps("Year Today", "TODAY", [1640, RAIL_Y + 40], 1.6, D, size=16, color=INK), 1.6))
    # A: Roselius and benzene
    ga = [disc("Dot 1905", [yx(1905), RAIL_Y], 18, INK, a0, D, sh=0, scale=grow(a0)),
          appear(caps("Lab 1905", "1905 · LUDWIG ROSELIUS, BREMEN", [yx(1905) - 10, RAIL_Y - 30], a0 + 0.2, D, size=16, color=INK, just="left"), a0 + 0.2)]
    r = 34
    hexa = [(r * math.cos(math.radians(30 + 60 * k)), r * math.sin(math.radians(30 + 60 * k)), 9, "") for k in range(6)]
    ga += molecule("Benzene", hexa, [(k, (k + 1) % 6, k % 2 == 0) for k in range(6)], [yx(1905) + 60, RAIL_Y - 140], a0 + 1.2, D)
    ga.append(appear(caps("Benzene Label", "BENZENE · NOW KNOWN TO CAUSE CANCER", [yx(1905) + 20, RAIL_Y - 210], a0 + 2.6, D, size=14, color=INK, just="left"), a0 + 2.6))
    pat = doc("Patent", [("KAISERLICHES", 18, LAB), ("PATENTAMT", 18, LAB), ("Verfahren zur", 20, SCI), ("Entcoffeinierung", 20, SCI), ("mittels Benzol", 22, HEAD)],
              (700, 400), (300, 380), a0 + 1.6, b0, hl_line=4)
    pat.append(caps("Patent Credit", "KAISERLICHES PATENTAMT, 1905, RECREATED", [90, 1040], a0 + 2.0, b0, size=14, just="left", opacity=fade_io(a0 + 2.0, b0)))
    for l in pat:
        add_out(l, b0 - 0.4)
    L += pat + ga
    dim(ga, b0)
    # B: safer solvents; methylene chloride boils long before the roaster is hot
    gb = [disc("Dot 1970", [yx(1970), RAIL_Y], 18, INK, b0, D, sh=0, scale=grow(b0)),
          appear(caps("Lab 1970", "BY 1970 · SAFER SOLVENTS", [yx(1970) - 10, RAIL_Y - 30], b0 + 0.2, D, size=16, color=INK, just="right"), b0 + 0.2)]
    gb += molecule("DCM", [(0, 0, 18, "C"), (-44, -30, 16, "Cl"), (44, -30, 16, "Cl"), (-34, 36, 10, "H"), (34, 36, 10, "H")],
                   [(0, 1, False), (0, 2, False), (0, 3, False), (0, 4, False)], [yx(1970) - 120, RAIL_Y - 150], b0 + 0.8, D)
    gb.append(appear(caps("DCM Label", "METHYLENE CHLORIDE", [yx(1970) - 120, RAIL_Y - 220], b0 + 1.0, D, size=14, color=INK), b0 + 1.0))
    th = [shape("Thermo", [G("Bulb", ell([40, 40], [0, 200]), stroke(INK, 3), fill(WHITE)), G("Tube", rect([20, 400], [0, 0], 10), stroke(INK, 3), fill(WHITE)),
                           G("M40", path([(10, 140), (40, 140)]), stroke(INK, 3)), G("M200", path([(10, -150), (40, -150)]), stroke(INK, 3))],
                  [1500, 380], b0 + 2.0, c0, opacity=fade_io(b0 + 2.0, c0))]
    th.append(appear(caps("Thermo 40", "BOILS AT 40 °C", [1550, 526], b0 + 2.6, c0, size=16, color=INK, just="left"), b0 + 2.6))
    th.append(appear(caps("Thermo 200", "ROASTER ≈ 200 °C", [1550, 236], b0 + 3.4, c0, size=16, color=INK, just="left"), b0 + 3.4))
    th.append(src("Src DCM", "SOURCE: MAX PLANCK SOCIETY; PUBCHEM", b0 + 2.0, c0))
    for l in th[1:]:
        add_out(l, c0 - 0.4)
    L += gb + th
    dim(gb, c0)
    # C: Zosel and supercritical CO2
    gc = [appear(caps("Lab Zosel", "1970 · KURT ZOSEL, PATENT", [yx(1970) + 10, RAIL_Y - 30], c0 + 0.2, D, size=16, color=INK, just="left"), c0 + 0.2)]
    gc += molecule("CO2", [(-48, 0, 14, "O"), (0, 0, 16, "C"), (48, 0, 14, "O")], [(0, 1, True), (1, 2, True)], [yx(1970) + 110, RAIL_Y - 140], c0 + 0.6, D)
    gauge = [G("Needle", path([(0, 0), (0, -80)]), stroke(INK, 4), tr={"rotation": A(K(c0 + 1.2, -110), K(c0 + 2.6, 50))}),
             G("Hub", ell([16, 16]), fill(INK)), G("Dial", ell([200, 200]), stroke(INK, 3), fill(WHITE))]
    gc.append(shape("Gauge", gauge, [1460, 420], c0 + 1.0, d0, scale=grow(c0 + 1.0)))
    gc.append(appear(text("Gauge Value", "≈ 160 atm", [1460, 580], 40, INK, c0 + 2.6, d0, font=HEAD), c0 + 2.6))
    gc.append(appear(caps("Gauge Label", "≈ THE PRESSURE 1.6 KM UNDER THE SEA", [1460, 616], c0 + 2.8, d0, size=14, color=INK), c0 + 2.8))
    gc.append(shape("Depth", [G("Tick", path([(-26, -200 + 400 * 1.6 / 4), (26, -200 + 400 * 1.6 / 4)]), stroke(INK, 3)), G("Col", rect([40, 400]), stroke(INK, 2))],
                    [1700, 400], c0 + 3.2, d0, opacity=fade_in(c0 + 3.2)))
    gc.append(appear(caps("Depth Label", "1.6 KM", [1740, 366], c0 + 3.4, d0, size=14, color=INK, just="left"), c0 + 3.4))
    gc.append(src("Src CO2", "SOURCE: MAX PLANCK SOCIETY; 10 M OF SEAWATER ≈ 1 ATM", c0 + 2.6, d0))
    for l in gc[-6:]:
        add_out(l, d0 - 0.4)
    L += gc
    dim(gc, d0)
    # D: the water drop, still waiting
    drop = path([(0, -30), (0, 26)], True, i=[(0, 0), (-22, 0)], o=[(22, 0), (0, 0)])
    drop = path([(0, -34), (20, 6), (0, 26), (-20, 6)], True, i=[(0, 0), (0, -14), (11, 0), (0, 11)], o=[(0, 0), (0, 11), (-11, 0), (0, -14)])
    L.append(shape("Drop", [G("Drop", drop, fill(WATER))], [1640, RAIL_Y - 50], d0 + 0.6, e0 + 0.6, scale=grow(d0 + 0.6),
                   opacity=A(K(e0 + 0.2, 100), K(e0 + 0.6, 0))))
    L.append(appear(caps("Drop Label", "WATER · THE OBVIOUS ONE", [1640, RAIL_Y - 104], d0 + 1.0, e0, size=16, color=WATER), d0 + 1.0))
    fade_all(L, e0, 0.6, keep={"Drop"})
    L.append(disc("Water Circle", A(K(e0 + 0.2, [1640, RAIL_Y - 46]), K(e0 + 1.8, list(inv((CX, CY))))), 420 / HS, WATER, e0 + 0.2, D, sh=0,
                  scale=A(K(e0 + 0.2, [40 / 420 * HS * 100] * 2), K(e0 + 1.8, [100, 100]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 4 - THE TROUBLE WITH WATER (14 s)
# =====================================================================
BEAK = 420


def beaker(name, pos, t0, t1, d=BEAK, **tr):
    return shape(name, [G("Rim", ell([d, d]), stroke(INK, 4)), G("Water", ell([d, d]), fill(WATER, 30))], pos, t0, t1, **tr)


def s4_water(D):
    L = []
    rnd = random.Random(4)
    L.append(disc("Circle In", [CX, CY], BEAK, WATER, 0, 0.9, sh=0, opacity=A(K(0.2, 100), K(0.8, 0))))
    pts = dots_in(rnd, 46, BEAK / 2 - 20, BEAK / 2 - 20, CX, CY)
    gs = [G(f"D{j + 1}", ell([11, 11]), fill(CAF if j % 4 == 0 else INK),
            tr={"position": A(K(2.4 + j * 0.08, [CX, CY]), K(3.6 + j * 0.08, list(p))), "opacity": fade_in(2.4 + j * 0.08, 0.1)})
          for j, p in enumerate(pts)]
    L.append(shape("Out Dots", gs, [0, 0], 2.4, D))
    L.append(shape("Seed", [G("Seed", bean_shape(130, 92), stroke(INK, 3), fill(A(K(2.6, SEED), K(7.0, WHITE))))],
                   A(K(0.8, [CX, -100]), K(1.8, [CX, CY]), K(9.6, [CX, CY]), K(10.6, [CX, -160])), 0.8, D))
    L.append(beaker("Beaker", [CX, CY], 0, D))
    L += wipe_text("Takes All", "Plain water takes almost everything", [CX, 880], 40, INK, 5.0, D)
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 5 - THE BATH THAT'S ALREADY FULL (53 s)
# =====================================================================
TANK = (480, 600)
BEAN_C, BEAN_W, BEAN_H = (1430, 580), 440, 320
FILT = (860, 600)


def s5_extract(D):
    L = []
    rnd = random.Random(5)
    a0, b0, c0, d0, e0 = 0.0, 8.0, 20.0, 36.0, 45.0
    stops = [("STEAM", 400, a0 + 1.4), ("MAKE THE EXTRACT", 760, b0), ("SOAK", 1160, c0), ("DRY", 1520, e0)]
    for nm, x, t in stops:
        L.append(caps(f"Stop {nm}", nm, [x, 140], 1.0, D, size=16, color=INK, opacity=A(K(1.0, 0), K(1.4, 35), K(t, 35), K(t + 0.3, 100))))
        L.append(disc(f"Stop {nm} Dot", [x, 100], 16, A(K(t, GREY2), K(t + 0.3, INK)), 1.0, D, sh=0, opacity=fade_in(1.0)))
    L.append(shape("Rail", [G("R", path([(400, 100), (1520, 100)]), trim(0, A(K(0.6, 0), K(1.4, 100))), stroke(LINE, 3))], [0, 0], 0.6, D))
    tankL = []
    # A: steam a batch of seeds
    seeds = [G(f"S{j + 1}", bean_shape(60, 42), stroke(INK, 2), fill(SEED), tr={"position": p, "scale": A(K(a0 + 2.6, [100, 100]), K(a0 + 4.6, [110, 110]))})
             for j, p in enumerate([(-60, -40), (30, -60), (60, 20), (-30, 40), (-90, 30)])]
    tankL.append(shape("Batch", seeds, list(TANK), a0 + 1.2, b0 + 6.0, opacity=A(K(a0 + 1.2, 0), K(a0 + 1.6, 100), K(b0 + 5.4, 100), K(b0 + 6.0, 0))))
    steam = [G(f"Steam {k}", path([(0, 0), (8, -20), (-8, -40), (0, -60)], False, i=[(0, 0), (6, 8), (6, 8), (6, 8)], o=[(6, -8), (-6, -8), (-6, -8), (0, 0)]),
               trim(0, X("100 * ((time * 0.8 + " + str(k * 0.3) + ") % 1)")), stroke(INK, 3), tr={"position": [-80 + k * 50, -130]}) for k in range(4)]
    tankL.append(shape("Steam", steam, list(TANK), a0 + 2.0, b0, opacity=fade_io(a0 + 2.0, b0)))
    # B: make the extract; the filter keeps the caffeine
    pts = dots_in(rnd, 40, 170, 170, *TANK)
    ink = [G(f"I{j + 1}", ell([11, 11]), fill(INK), tr={"position": list(p), "opacity": fade_in(b0 + 1.0 + j * 0.05, 0.1)}) for j, p in enumerate(pts[:28])]
    caf = []
    for j, p in enumerate(pts[28:]):
        tt = b0 + 5.6 + j * 0.15
        fpos = [FILT[0] + rnd.uniform(-22, 22), FILT[1] + rnd.uniform(-120, 120)]
        caf.append(G(f"C{j + 1}", ell([11, 11]), fill(CAF), tr={"position": A(K(tt, list(p)), K(tt + 1.0, fpos)), "opacity": fade_in(b0 + 1.4 + j * 0.05, 0.1)}))
    tankL.append(shape("Extract Ink", ink, [0, 0], b0 + 1.0, D))
    tankL.append(shape("Extract Caf", caf, [0, 0], b0 + 1.4, D))
    tankL.append(shape("Filter", [G("F", rect([80, 300], None, 30), stroke(INK, 4), fill(WHITE))], list(FILT), b0 + 3.0, D, scale=grow(b0 + 3.0)))
    tankL.append(appear(caps("Filter Label", "FILTER", [FILT[0], FILT[1] + 190], b0 + 3.2, D, size=16, color=INK), b0 + 3.2))
    tankL.append(shape("Pipe", [G("P", path([(TANK[0] + 210, TANK[1] - 120), (FILT[0], TANK[1] - 220), (FILT[0], FILT[1] - 150)]), path([(FILT[0], FILT[1] + 150), (FILT[0], TANK[1] + 230), (TANK[0] + 200, TANK[1] + 120)]),
                                    trim(0, A(K(b0 + 4.0, 0), K(b0 + 5.0, 100))), stroke(INK, 3))], [0, 0], b0 + 4.0, D))
    L.append(appear(text("Extract Label", "Green coffee extract", [TANK[0], 880], 38, INK, b0 + 8.0, c0 + 0.4, font=HEAD), b0 + 8.0))
    L.append(appear(caps("Extract Sub", "= EVERYTHING EXCEPT CAFFEINE", [TANK[0], 920], b0 + 8.4, c0 + 0.4, size=16, color=INK), b0 + 8.4))
    for l in L[-2:]:
        add_out(l, c0)
    tankL.append(beaker("Tank", A(K(0, [CX, CY]), K(1.0, list(TANK))), 0, D, scale=A(K(0, [100, 100]), K(1.0, [90, 90]))))
    L += tankL
    dim(tankL, c0 + 0.4, 25)
    # C: soak, the two gauges
    bean_rnd = random.Random(8)
    bpts = dots_in(bean_rnd, 34, BEAN_W / 2 - 10, BEAN_H / 2 - 10, 0, 0)
    bd = []
    for j, p in enumerate(bpts):
        if j % 3 == 0:
            tt = c0 + 9.0 + j * 0.12
            tr = {"position": A(K(tt, list(p)), K(tt + 1.4, [p[0] - 420, p[1] * 0.6])), "opacity": A(K(c0, 0), K(c0 + 0.4, 100), K(tt + 1.0, 100), K(tt + 1.4, 0))}
            bd.append(G(f"BC{j + 1}", ell([12, 12]), fill(CAF), tr=tr))
        else:
            bd.append(G(f"BI{j + 1}", ell([12, 12]), fill(INK), tr={"position": list(p), "opacity": fade_in(c0)}))
    L.append(shape("Bean Dots", bd, list(BEAN_C), c0, D))
    L.append(shape("Bean", [G("Bean", bean_shape(BEAN_W, BEAN_H), stroke(INK, 4), fill(SEED, 55))], list(BEAN_C), c0, D, scale=grow(c0, 100, 0.6)))
    L.append(appear(caps("Bean Label", "A FRESH BEAN, CUT OPEN", [BEAN_C[0], BEAN_C[1] + BEAN_H / 2 + 44], c0 + 0.4, D, size=16), c0 + 0.4))

    def gauge(name, y, inside, outside, col, t):
        out = []
        for k, (lab, v) in enumerate((("INSIDE", inside), ("OUTSIDE", outside))):
            yy = y + k * 34
            out.append(shape(f"{name} {lab}", [G("Fill", rect([200 * v, 20], [-100 + 100 * v, 0]), fill(col)), G("Box", rect([200, 20]), stroke(INK, 2))],
                             [1080, yy], t + k * 0.2, D, opacity=fade_in(t + k * 0.2)))
            out.append(caps(f"{name} {lab} Label", lab, [966, yy + 6], t + k * 0.2, D, size=13, color=INK, just="right", opacity=fade_in(t + k * 0.2)))
        return out
    gs1 = gauge("Sugar", 330, 0.7, 0.7, INK, c0 + 1.6)
    gs1.append(appear(caps("Sugar Name", "SUGARS AND ACIDS", [1080, 296], c0 + 1.6, D, size=15, color=INK), c0 + 1.6))
    gs1.append(shape("Sugar Arrow", [G("A", path([(0, 0), (-70, 0)]), path([(-56, -10), (-72, 0), (-56, 10)]), stroke(INK, 3))], [1240, 348], c0 + 3.0, c0 + 5.4,
                     opacity=A(K(c0 + 3.0, 0), K(c0 + 3.3, 100), K(c0 + 3.6, 20), K(c0 + 3.9, 100), K(c0 + 4.6, 100), K(c0 + 5.4, 0))))
    gs1.append(appear(caps("Sugar Verdict", "NOTHING TO GAIN", [1080, 420], c0 + 4.4, D, size=16, color=INK), c0 + 4.4))
    gs2 = gauge("Caffeine", 760, 0.95, 0.0, CAF, c0 + 6.0)
    gs2.append(appear(caps("Caffeine Name", "CAFFEINE", [1080, 726], c0 + 6.0, D, size=15, color=CAF), c0 + 6.0))
    gs2.append(shape("Caffeine Arrow", [G("A", path([(0, 0), (-150, 0)]), path([(-126, -20), (-154, 0), (-126, 20)]), trim(0, A(K(c0 + 8.0, 0), K(c0 + 8.8, 100))), stroke(CAF, 10))],
                     [1230, 680], c0 + 8.0, D))
    L += gs1 + gs2
    L += wipe_text("Rule", "Molecules move from more to less", [CX, 980], 36, INK, c0 + 10.0, D)
    # D: round again until 99.9 %
    loop = [G("Arrow", path([(-10, -8), (0, 4), (10, -8)]), stroke(INK, 4), tr={"position": [0, -60]}), G("Loop", ell([120, 120]), trim(0, 85), stroke(INK, 4))]
    L.append(shape("Loop", loop, [FILT[0], 200], d0, e0, rotation=X(f"(time - {d0}) * 160"), opacity=fade_io(d0, e0)))
    L.append(appear(text("Free", "99.9 %", [BEAN_C[0], 230], 72, INK, d0 + 3.0, e0, font=HEAD), d0 + 3.0))
    L.append(appear(caps("Free Label", "CAFFEINE-FREE", [BEAN_C[0], 270], d0 + 3.2, e0, size=18, color=INK), d0 + 3.2))
    L.append(src("Src Free", "SOURCE: SWISS WATER; ROYAL COFFEE NY", d0 + 3.0, e0))
    for l in L[-3:]:
        add_out(l, e0 - 0.4)
    # E: dry back to where it started
    L.append(appear(text("Moisture", "≈ 10–12 %", [BEAN_C[0], 230], 64, INK, e0 + 0.6, D, font=HEAD), e0 + 0.6))
    L.append(appear(caps("Moisture Label", "MOISTURE, AS THE GREEN BEAN STARTED", [BEAN_C[0], 270], e0 + 0.8, D, size=16, color=INK), e0 + 0.8))
    z0 = 50.4
    keep = {"Tank End"}
    fade_all(L, z0 - 1.2, 0.6, keep=keep)
    L.append(disc("Tank End", A(K(z0, list(TANK)), K(z0 + 1.8, list(inv((CX, CY))))), BEAK * 0.9, WATER, z0 - 1.4, D, sh=0,
                  scale=A(K(z0, [100, 100]), K(z0 + 1.8, [14 / (BEAK * 0.9) / HS * 100] * 2)), opacity=fade_in(z0 - 1.4, 0.6)))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 6 - CORDOBA (44 s)
# =====================================================================
K6 = 40
VER, BUR, MAN, PICO = (-96.13, 19.2), (-122.97, 49.25), (-75.5, 5.07), (-97.27, 19.03)


def s6_cordoba(D):
    L = []
    rig = "Map Rig"
    s_out, s_in = 0.15, 6.0
    z1, z2 = (1.4, 4.2), (19.0, 22.0)
    sp = lambda ll, s: [CX + (ll[0] - COR[0]) * K6 * s, CY - (ll[1] - COR[1]) * K6 * s]
    m = lambda ll: map_pt(ll, K6)
    t_map_out = 29.6
    # Mexico states (ep. 1) and the Veracruz dot where Typica landed
    st = [path([m(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    L.append(disc("Veracruz Dot", sp(VER, 1), 16, ARA, 0, z1[0] + 0.4, sh=0, opacity=A(K(z1[0], 100), K(z1[0] + 0.4, 0))))
    L.append(appear(caps("Cordoba Label", "CÓRDOBA, VERACRUZ", [CX - 20, CY + 40], 0.2, z1[0], size=16, color=INK, just="right"), 0.2))
    add_out(L[-1], z1[0] - 0.3)
    # A: Burnaby
    a0 = 4.4
    L.append(disc("Burnaby Dot", sp(BUR, s_out), 14, WATER, a0, z2[0], sh=0, scale=grow(a0)))
    L.append(appear(caps("Burnaby Chip", "SWISS WATER · BURNABY · SINCE 1988", [sp(BUR, s_out)[0] + 20, sp(BUR, s_out)[1] + 6], a0 + 0.3, 10.0, size=16, color=INK, just="left"), a0 + 0.3))
    L.append(src("Src Burnaby", "SOURCE: SWISS WATER DECAFFEINATED COFFEE CO.", a0 + 0.3, 10.0))
    for l in L[-2:]:
        add_out(l, 9.6)
    # B: one of very few; Colombia's own plant uses a solvent; the arc
    b0 = 10.2
    L.append(appear(text("Few", "One of very few water-only plants", [120, 220], 40, INK, b0, z2[0], font=HEAD, just="left"), b0))
    man = sp(MAN, s_out)
    L.append(disc("Manizales Dot", man, 16, ARA, b0 + 1.4, z2[0], sh=0, scale=grow(b0 + 1.4)))
    L += molecule("EtOAc", [(-30, 0, 11, "C"), (0, -14, 11, "C"), (30, 0, 12, "O"), (0, -48, 12, "O")], [(0, 1, False), (1, 2, False), (1, 3, True)],
                  [man[0] + 110, man[1] + 30], b0 + 2.0, z2[0])
    L.append(appear(caps("Manizales Label", "COLOMBIA'S OWN PLANT: ETHYL ACETATE FROM SUGARCANE", [man[0] + 20, man[1] + 120], b0 + 2.2, z2[0], size=15, color=INK), b0 + 2.2))
    L.append(shape("Arc Col", [G("Arc", arc(man, [CX, CY], 0.3), trim(0, A(K(b0 + 4.0, 0), K(b0 + 5.4, 100))), stroke(INK, 3))], [0, 0], b0 + 4.0, z2[0]))
    for l in L:
        if l["in"] >= a0 and l["name"] != "Few" and l["out"] >= z2[0]:
            add_out(l, z2[0] - 0.6)
    add_out(L[[l["name"] for l in L].index("Few")], z2[0] - 0.6)
    # C: below Pico de Orizaba; the mountain water matters less
    c0 = z2[1] + 0.2
    pk = sp(PICO, s_in)
    pk = [pk[0] - 140, pk[1] - 120]  # ponytail: drawn up-left of true scale so the contours clear the dot
    cont = [G(f"C{k}", path([(math.cos(a) * r * (1 + 0.12 * math.sin(3 * a + k)), math.sin(a) * r * 0.7 * (1 + 0.1 * math.cos(2 * a + k)))
                             for a in [i * math.pi / 12 for i in range(24)]], True), trim(0, A(K(c0 + k * 0.2, 0), K(c0 + 1.0 + k * 0.2, 100))), stroke(INK, 2))
            for k, r in enumerate((26, 62, 100, 140))]
    L.append(shape("Pico", cont, pk, c0, t_map_out))
    L.append(appear(text("Pico Name", "Pico de Orizaba", [pk[0], pk[1] - 140], 36, INK, c0 + 0.6, t_map_out, font=HEAD), c0 + 0.6))
    L.append(appear(caps("Pico Height", "5,636 M · ≈ 6.5 × CÓRDOBA'S ALTITUDE", [pk[0], pk[1] - 106], c0 + 0.8, t_map_out, size=15, color=INK), c0 + 0.8))
    drop = path([(0, -24), (14, 4), (0, 18), (-14, 4)], True, i=[(0, 0), (0, -10), (8, 0), (0, 8)], o=[(0, 0), (0, 8), (-8, 0), (0, -10)])
    L.append(shape("Mountain Drop", [G("D", drop, fill(A(K(c0 + 4.0, WATER), K(c0 + 4.6, GREY2))))], A(K(c0 + 1.6, pk), K(c0 + 3.0, [CX - 30, CY - 30])), c0 + 1.6, t_map_out))
    L.append(appear(caps("Mountain Quote", "\"MOUNTAIN WATER\"", [CX + 40, CY - 60], c0 + 2.6, t_map_out, size=18, color=WATER, just="left"), c0 + 2.6))
    L.append(appear(caps("Matters Less", "MATTERS LESS", [CX + 40, CY - 30], c0 + 4.6, t_map_out, size=16, color=GREY, just="left"), c0 + 4.6))
    L.append(disc("Cordoba Dot", [CX, CY], 14, WATER, 0, t_map_out + 0.6, sh=0, opacity=A(K(t_map_out, 100), K(t_map_out + 0.6, 0))))
    L.append(shape("States", [G("Borders", *st, stroke(WHITE, 2)), G("Fill", *st, fill(LAND))], [0, 0], 0, t_map_out, parent=rig,
                   opacity=A(K(z1[0], 100), K(z1[1], 0), K(z2[0], 0), K(z2[1], 100))))
    L.append(land_layer("Land", K6, 0, t_map_out, bbox=(-170, -60, -30, 75), parent=rig))
    add_out(L[-1], t_map_out - 0.6)
    add_out(L[-2], t_map_out - 0.6)
    L.append(null(rig, [CX, CY], 0, D, anchor=m(COR), scale=zmulti(1.0, [(z1[0], z1[1], s_out), (z2[0], z2[1], s_in)])))
    for l in L:
        if c0 <= l["in"] and l["name"] not in ("Cordoba Dot",):
            add_out(l, t_map_out - 0.6)
    # D: one extract per origin
    d0 = t_map_out + 0.4
    cam = "Cam"
    TC, TM = (700, 600), (1220, 600)
    dl = []
    for nm, tpos, srcp, lab in (("Col", TC, (260, 860), "COLOMBIAN EXTRACT"), ("Mex", TM, (1660, 340), "MEXICAN EXTRACT")):
        dl.append(beaker(f"Tank {nm}", A(K(d0, [CX, CY]), K(d0 + 1.0, list(tpos))), d0, D, d=160, scale=grow(d0, 100, 1.0)))
        dl.append(appear(caps(f"Tank {nm} Label", lab, [tpos[0], tpos[1] + 120], d0 + 1.2, D, size=16, color=INK), d0 + 1.2))
        dl.append(shape(f"Feed {nm}", [G("Arc", arc(srcp, (tpos[0], tpos[1] + (90 if nm == "Col" else -90)), 0.25 if nm == "Col" else -0.25),
                                         trim(0, A(K(d0 + 1.4, 0), K(d0 + 2.4, 100))), stroke(INK, 3))], [0, 0], d0 + 1.4, D))
    dl.append(appear(caps("Feed Col Label", "COLOMBIA", [260, 900], d0 + 1.4, D, size=16, color=ARA), d0 + 1.4))
    dl.append(appear(caps("Feed Mex Label", "VERACRUZ HIGHLANDS", [1660, 300], d0 + 1.4, D, size=16, color=MX), d0 + 1.4))
    dl += wipe_text("Per Origin", "One extract per origin", [CX, 200], 52, INK, d0 + 2.4, D, hl=True)
    dl.append(src("Src Origin", "SOURCE: ROYAL COFFEE NY, VISIT TO DESCAMEX", d0 + 2.4, D))
    # E: the Colombian bean drops in; push in on one caffeine dot leaving it
    e0 = 37.4
    bean_end = [TC[0] - 20, TC[1] + 10]
    dl.append(shape("Col Bean", [G("Bean", bean_shape(70, 50), stroke(INK, 2), fill(SEED))], A(K(e0, [260, 860]), K(e0 + 1.6, bean_end)), e0, D))
    caf_end = [bean_end[0] + 44, bean_end[1] - 20]
    dl.append(disc("Caf Dot", A(K(e0 + 2.0, bean_end), K(e0 + 3.0, caf_end)), 10, CAF, e0 + 2.0, D, sh=0))
    for l in dl:
        if l["name"] not in ("Caf Dot",):
            add_out(l, e0 + 3.4, 0.8)
    parent_all(dl, cam)
    L += dl
    zf = 60 / 10 / HS
    L.append(null(cam, list(caf_end), 0, D, scale=zoom_scale(e0 + 3.2, D - 0.4, 1.0, zf), position=zoom_pos(e0 + 3.2, D - 0.4, caf_end, inv((CX, CY)))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 7 - WHERE THE CAFFEINE GOES (10 s)
# =====================================================================
def hexagon(r):
    return path([(r * math.cos(math.radians(60 * k + 30)), r * math.sin(math.radians(60 * k + 30))) for k in range(6)], True)


def s7_crystal(D):
    L = []
    rnd = random.Random(7)
    can_top = (820, 420)
    L.append(disc("Dot In", [CX, CY], 60, CAF, 0, 0.8, sh=0, opacity=A(K(0.3, 100), K(0.8, 0))))
    heap = [G("Main", hexagon(40), stroke(CAF, 4), fill(WHITE), tr={"position": [0, 0], "scale": A(K(0.2, [75, 75]), K(0.8, [100, 100]))})]
    for j in range(12):
        p = [rnd.uniform(-140, 140), rnd.uniform(10, 90) - abs(j - 6) * 4]
        t = 1.0 + j * 0.15
        heap.append(G(f"X{j + 1}", hexagon(rnd.uniform(18, 30)), stroke(CAF, 3), fill(WHITE), tr={"position": A(K(t, [p[0], -400]), K(t + 0.5, p))}))
    L.append(shape("Heap", heap[::-1], [CX, CY], 0.2, D, position=A(K(3.4, [CX, CY]), K(4.4, [can_top[0], can_top[1] + 40])),
                   scale=A(K(3.4, [100, 100]), K(4.4, [30, 30])), opacity=A(K(4.2, 100), K(4.6, 0))))
    for nm, x, h, t in (("Can 1", can_top[0], 300, 3.6), ("Can 2", 1100, 380, 4.0)):
        L.append(shape(nm, [G("Top", ell([180, 46], [0, -h / 2]), stroke(INK, 4), fill(WHITE)), G("Body", rect([180, h], None, 12), stroke(INK, 4), fill(WHITE))],
                       [x, can_top[1] + h / 2], t, D, scale=grow(t, 100, 0.5)))
    L.append(appear(caps("Drinks", "SOLD ON TO DRINKS MAKERS", [960, 860], 4.8, D, size=18, color=INK), 4.8))
    L.append(src("Src Drinks", "SOURCE: ROYAL COFFEE NY", 4.8, D))
    z0 = 7.4
    fade_all(L, z0, 0.5)
    L.append(shape("Ring", [G("R", ell([180, 46]), stroke(INK, 4))], A(K(z0, list(can_top)), K(D - 0.2, list(inv((CX, CY))))), z0, D,
                   scale=A(K(z0, [100, 100]), K(D - 0.2, [100 / HS, 100 / HS]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 8 - CLOSE (19 s)
# =====================================================================
def s8_close(D):
    L = []
    rig = "Bag Rig"
    rnd = random.Random(2)
    up = (11.0, 12.0)
    L += wipe_text("End Title", "How Decaf Is Made, in Veracruz", [CX, 930], 64, INK, 12.4, D)
    L.append(word_marker("End Swipe", "How Decaf Is Made, in Veracruz", "Veracruz", CX, 930, 64, 13.2, D))
    L.append(shape("Ring In", [G("R", ell(A(K(0, [180, 46]), K(0.8, [180, 180]))), stroke(INK, 4))], A(K(0, [CX, CY]), K(1.4, list(WIN))), 0, 1.6,
                   opacity=A(K(1.2, 100), K(1.6, 0))))
    # the opened seed: every ink dot still there, the blue one gone
    s0 = 3.0
    pts = dots_in(rnd, 99, 160, 110, 0, 0)
    gs = [G(f"D{j + 1}", ell([8, 8]), fill(INK), tr={"position": list(p), "opacity": fade_in(s0 + 1.4 + j * 0.01, 0.1)}) for j, p in enumerate(pts)]
    seed = [shape("Seed Dots", gs, [1450, 560], s0 + 1.4, 9.6, opacity=A(K(8.6, 100), K(9.0, 0))),
            shape("Seed", [G("Seed", bean_shape(360, 260), stroke(INK, 4), fill(A(K(s0 + 0.4, BEAN), K(s0 + 1.4, SEED))))],
                  A(K(s0, [WIN[0], WIN[1]]), K(s0 + 1.0, [1450, 560]), K(8.8, [1450, 560]), K(9.6, list(WIN))), s0, 9.8,
                  scale=A(K(s0, [13, 13]), K(s0 + 1.0, [100, 100]), K(8.8, [100, 100]), K(9.6, [13, 13])), opacity=A(K(9.4, 100), K(9.8, 0)))]
    seed.append(appear(caps("Seed Note", "NO CAFFEINE · EVERYTHING ELSE STILL THERE", [1450, 740], s0 + 2.4, 8.6, size=15, color=INK), s0 + 2.4))
    add_out(seed[-1], 8.4)
    L += seed
    bag = bag_layers(D, 0.4, rig)
    for l in bag:
        l["transform"]["opacity"] = fade_in(0.6, 0.8)
    L += bag
    L.append(null(rig, [CX, CY], 0, D, anchor=[CX, CY], position=A(K(up[0], [CX, CY]), K(up[1], [CX, 420])),
                  scale=A(K(up[0], [100, 100]), K(up[1], [80, 80]))))
    L.append(bg(D))
    return L


SCENES = [("S1_Bag", 20.0, s1_bag), ("S2_OnePercent", 21.0, s2_percent), ("S3_Solvents", 31.0, s3_solvents), ("S4_Water", 14.0, s4_water),
          ("S5_Extract", 53.0, s5_extract), ("S6_Cordoba", 44.0, s6_cordoba), ("S7_Crystal", 10.0, s7_crystal), ("S8_Close", 19.0, s8_close)]

if __name__ == "__main__":
    write(SCENES, "Decaf_Veracruz", "06_decaf_veracruz", beats=True)
