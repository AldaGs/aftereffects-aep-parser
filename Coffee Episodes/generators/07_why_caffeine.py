"""Generator for episode 7, "Why Does a Plant Make Caffeine?" (scripts/07_why_caffeine_script.md).

    python "Coffee Episodes/generators/07_why_caffeine.py"      # writes ../json/07_why_caffeine.json

A handoff is a screen point/size: the outgoing scene ends its shape at inv(p) with size/HS, the next starts at p.
No fades: cut_pass (coffee_common) turns every appear/exit into a cut plus a scale pop.
"""
import math, random

from coffee_common import *  # noqa: F401,F403

PEST, MAG = "#6C4F9E", "#B4457F"
FLOWER_D = 300           # 6->7 handoff, flower at centre
MOL_R = 110              # caffeine ring radius; the molecule is ~360 px wide (2->3 handoff)
LEAF_L = 600             # 3->4 handoff, leaf at centre
SOIL_Y = 880             # 4->5->6 handoff, a full-width ink line
FALLEN = (CX, 850)       # 4->5 leaf on the soil line
FALLEN_L = 420
CHAPAS = (-92.17, 14.99)  # Cacahoatán
CHAPAS_DOT = 16          # 7->8 pest-violet dot


# ---------------------------------------------------------------------
# art
# ---------------------------------------------------------------------
def flower(name, d, pos, t0, t1, **tr):
    petals = [G(f"Petal {k + 1}", ell([d * 0.36, d * 0.5], [0, -d * 0.25]), stroke(INK, max(2, d * 0.012)), fill(WHITE), tr={"rotation": k * 72})
              for k in range(5)]
    return shape(name, [G("Centre", ell([d * 0.16, d * 0.16]), fill(SEED_LINE))] + petals, pos, t0, t1, **tr)


def bee(name, pos, t0, t1, s=100, **tr):
    wing = X("var f = 100 + 25 * Math.sin(time * 60); [100, f]")
    items = [G("Wing L", ell([34, 48], [-12, -30]), stroke(INK, 3), fill(WHITE, 80), tr={"scale": wing, "rotation": -20}),
             G("Wing R", ell([34, 48], [14, -30]), stroke(INK, 3), fill(WHITE, 80), tr={"scale": wing, "rotation": 20}),
             G("Stripes", path([(-6, -20), (-6, 20)]), path([(10, -20), (10, 20)]), stroke(INK, 6)),
             G("Head", ell([26, 26], [-40, 0]), stroke(INK, 3), fill(INK)),
             G("Body", ell([70, 44]), stroke(INK, 3), fill(HL))]
    return shape(name, items, pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)


def hornworm(name, pos, t0, t1, s=100, **tr):
    segs = [G(f"Seg {k + 1}", ell([34, 34], [k * 26 - 78, 0]), stroke(INK, 2), fill(PEST)) for k in range(7)]
    items = [G("Horn", path([(80, -10), (94, -30)]), stroke(INK, 3))] + segs
    return shape(name, items, pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)


def borer(name, pos, t0, t1, s=100, **tr):
    return shape(name, [G("Borer", ell([36, 22]), stroke(INK, 2), fill(PEST))], pos, t0, t1, scale=tr.pop("scale", [s, s]), **tr)


def wasp(name, pos, t0, t1, **tr):
    wing = X("var f = 100 + 25 * Math.sin(time * 70); [100, f]")
    items = [G("Wings", ell([20, 30], [-4, -18]), ell([20, 30], [8, -18]), stroke(INK, 2), fill(WHITE, 80), tr={"scale": wing}),
             G("Body", ell([22, 12], [-14, 0]), ell([30, 14], [10, 0]), stroke(INK, 2), fill(WHITE))]
    return shape(name, items, pos, t0, t1, **tr)


def caffeine(name, pos, t0, t1, r=MOL_R, tabs=None, rings=None, col=INK, **tr):
    """Purine double ring (hexagon + pentagon) with three methyl tabs. tabs: keyframed scale for the tab groups."""
    hx = [(r * math.cos(math.radians(a)), -r * math.sin(math.radians(a))) for a in (90, 150, 210, 270, 330, 30)]
    pa, pb = hx[5], hx[4]
    pc, pd, pe = (1.62 * r, -0.78 * r), (2.1 * r, 0), (1.62 * r, 0.78 * r)
    off = -0.6 * r
    sh = lambda p: (p[0] + off, p[1])
    hx = [sh(p) for p in hx]
    pa, pb, pc, pd, pe = map(sh, (pa, pb, pc, pd, pe))
    w = max(3, r * 0.04)
    ns = {"N1": hx[0], "N3": hx[2], "N7": pc, "N9": pe}
    items = []
    if rings is not None:
        items.append(G("N Rings", *[ell([r * 0.42, r * 0.42], list(p)) for p in ns.values()], stroke(INK, w), tr={"opacity": rings}))
    items.append(G("Atoms", *[ell([r * 0.22, r * 0.22], list(p)) for p in ns.values()], stroke(col, w), fill(WHITE)))
    for k, n in enumerate(("N1", "N3", "N7")):
        p = ns[n]
        c = hx[3] if False else None
        v = (p[0] - off - (0.75 * r if n == "N7" else 0), p[1])
        m = math.hypot(*v) or 1
        tip = (p[0] + v[0] / m * r * 0.55, p[1] + v[1] / m * r * 0.55)
        items.append(G(f"Methyl {k + 1}", ell([r * 0.26, r * 0.26], list(tip)), path([p, tip]), stroke(col, w), fill(CAF),
                       tr={"anchorPoint": list(p), "position": list(p), **({"scale": tabs[k]} if tabs else {})}))
    for k, a in enumerate((hx[1], hx[3])):
        v = (a[0] - off, a[1])
        m = math.hypot(*v)
        tip = (a[0] + v[0] / m * r * 0.45, a[1] + v[1] / m * r * 0.45)
        items.append(G(f"Oxygen {k + 1}", path([a, tip]), stroke(col, w)))
    items.append(G("Rings", path(hx, True), path([pa, pc, pd, pe, pb]), stroke(col, w), fill(WHITE)))
    return shape(name, items, pos, t0, t1, **tr)


def branch_layers(t0, t1, rig, flower_t=None, prefix=""):
    """The Chiapas branch of S9 D and S10: green leaves, an opening flower; the cherry is added by the caller."""
    out = [flower(f"{prefix}Open Flower", 170, [760, 400], t0, t1, parent=rig,
                  scale=A(K(flower_t, [35, 35]), K(flower_t + 1.2, [100, 100])) if flower_t is not None else [100, 100])]
    for k, (p, rot, L) in enumerate((((560, 520), 30, 220), ((980, 560), -20, 200), ((1500, 300), -40, 230), ((1320, 560), 25, 180))):
        out.append(shape(f"{prefix}Branch Leaf {k + 1}", [G("Vein", path([(-L * 0.4, 0), (L * 0.38, 0)]), stroke(WHITE, 3, 70)),
                                                           G("Leaf", leaf_path(L), stroke(INK, 2), fill(MX))], list(p), t0, t1, parent=rig, rotation=rot))
    out.append(shape(f"{prefix}Branch", [G("Stem", path([(200, 640), (760, 470), (1250, 430), (1760, 220)], False,
                                                          i=[(0, 0), (-200, 60), (-200, 20), (-200, 60)], o=[(200, -60), (200, -20), (200, -60), (0, 0)]),
                                           stroke(STEM, 10))], [0, 0], t0, t1, parent=rig))
    return out


CH_END = (1250, 470)     # cherry on the branch, end of S9 / start of S10
CH_END_S = 60


def dose_scale(D, t, t1, prefix="", y=900):
    """S7's key image: a log dose axis with the bee at the low end and the hornworm at the high end."""
    out = [shape(f"{prefix}Dose Axis", [G("Axis", path([(300, y), (1620, y)]), path([(1596, y - 12), (1620, y), (1596, y + 12)]),
                                         trim(0, A(K(t, 0), K(t + 0.8, 100))), stroke(INK, 4))], [0, 0], t, t1)]
    for k, x in enumerate((420, 640, 860, 1080, 1300, 1520)):
        out.append(shape(f"{prefix}Dose Tick {k + 1}", [G("T", path([(0, -10), (0, 10)]), stroke(INK, 3))], [x, y], t + 0.3 + k * 0.05, t1))
    out.append(caps(f"{prefix}Dose Label", "CAFFEINE DOSE, LOW → HIGH", [CX, y + 50], t + 0.4, t1, size=16, color=INK))
    return out


# =====================================================================
# SCENE 1 - CAFFEINATED NECTAR (15 s)
# =====================================================================
def s1_flower(D):
    L = []
    cam = "Cam"
    z = (4.0, 6.0)
    zs = 2.2
    br = []
    br.append(bee("Bee", A(K(1.4, [1500, 120]), K(2.8, [CX + 40, CY - 30])), 1.4, D, s=110, rotation=A(K(1.4, -30), K(2.8, 0))))
    br.append(flower("Flower Centre", 180, [CX, CY], 0.8, D, scale=grow(0.8)))
    for k, (p, d) in enumerate((((760, 420), 120), ((1170, 650), 130), ((820, 700), 100), ((1120, 380), 110))):
        br.append(flower(f"Flower {k + 1}", d, list(p), 1.0 + k * 0.1, D, scale=grow(1.0 + k * 0.1)))
    for k, (p, rot, l) in enumerate((((480, 330), -30, 300), ((560, 800), 25, 280), ((1480, 760), -20, 320), ((1450, 300), 30, 260))):
        br.append(grey_leaf(f"Leaf {k + 1}", l, list(p), 0.4 + k * 0.12, D, rotation=rot, scale=grow(0.4 + k * 0.12)))
    br.append(shape("Stem", [G("S", path([(-60, 600), (500, 560), (CX, CY), (1500, 520), (2000, 480)], False), trim(0, A(K(0, 0), K(1.2, 100))), stroke(STEM, 10))],
                    [0, 0], 0, D))
    parent_all(br, cam)
    # B: nectar, molecule, nitrogen rings (screen space, after the push-in)
    b0 = 6.0
    L.append(caffeine("Mol", [1420, 330], b0 + 0.6, 12.0, r=46, scale=grow(b0 + 0.6),
                      rings=A(K(b0 + 2.2, 0), K(b0 + 2.3, 100))))
    L.append(leader("Mol Leader", (CX + 30, CY - 20), (1300, 360), b0 + 0.4, 12.0, col=CAF))
    L.append(appear(caps("Mol Label", "CAFFEINE", [1440, 230], b0 + 0.8, 12.0, size=18, color=CAF), b0 + 0.8))
    L.append(appear(caps("N Label", "4 NITROGEN ATOMS PER MOLECULE", [1440, 440], b0 + 2.3, 12.0, size=15, color=INK), b0 + 2.3))
    L += wipe_text("Title", "Coffea arabica", [CX, 150], 64, INK, 8.4, 12.0, font=SCI)
    # D: everything else cuts; the drop becomes a 40 px dot at centre
    fade_all(br, 12.0)
    L += br
    L.append(disc("Nectar", [CX, CY], 30 * zs, CAF, b0 - 0.2, D, sh=0,
                  scale=A(K(b0 - 0.2, [0, 0]), K(b0 + 0.3, [100, 100]), K(12.2, [100, 100]), K(14.4, [40 / (30 * zs) / HS * 100] * 2))))
    L.append(null(cam, [CX, CY], 0, D, scale=A(K(z[0], [100, 100]), K(z[1], [zs * 100, zs * 100]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 2 - WHERE THE CAFFEINE IS (17 s)
# =====================================================================
NECTAR2 = (1240, 300)
SC_Y, SC_X0, SC_X1 = 900, 360, 1560


def pct_x(p):
    return SC_X0 + (SC_X1 - SC_X0) * p / 3


def s2_plant(D):
    L = []
    rig = "Plant Rig"
    po = (0.0, 1.8)
    pl = []
    pl.append(flower("Plant Flower", 90, list(NECTAR2), 0, D))
    for k, (p, rot, l) in enumerate((((820, 300), -30, 170), ((1060, 470), 25, 190), ((780, 560), -15, 160), ((1300, 560), 30, 150))):
        pl.append(grey_leaf(f"Plant Leaf {k + 1}", l, list(p), 0, D, rotation=rot))
    pl.append(grey_leaf("Young Leaf", 90, [960, 200], 0, D, rotation=-60))
    pl.append(shape("Plant Cherries", [G("C", ell([44, 44], [880, 420]), ell([44, 44], [930, 440]), ell([40, 40], [1180, 420]), stroke(ARA_DARK, 2), fill(ARA))], [0, 0], 0, 10.4))
    pl.append(shape("Plant Stem", [G("S", path([(960, 760), (960, 180)]), path([(960, 420), (1240, 320)]), path([(960, 500), (760, 420)]), stroke(STEM, 8))], [0, 0], 0, D))
    pl.append(shape("Ground", [G("G", path([(700, 760), (1220, 760)]), stroke(INK, 3))], [0, 0], 0, D))
    parent_all(pl, rig)
    L.append(disc("Nectar Dot", A(K(po[0], [CX, CY]), K(po[1], list(NECTAR2))), 40, CAF, 0, 10.0, sh=0, scale=A(K(po[0], [100, 100]), K(po[1], [40, 40]))))
    # A: the shared scale and three leaders
    a0 = 2.2
    sc = [shape("Scale", [G("Axis", path([(SC_X0, SC_Y), (SC_X1, SC_Y)]), trim(0, A(K(a0, 0), K(a0 + 0.8, 100))), stroke(INK, 3))], [0, 0], a0, D)]
    for v in range(4):
        sc.append(caps(f"Scale {v}", f"{v} %", [pct_x(v), SC_Y + 40], a0 + 0.4, D, size=15, color=INK))
    sc.append(caps("Scale Title", "CAFFEINE BY DRY WEIGHT", [SC_X0, SC_Y + 80], a0 + 0.4, D, size=15, just="left"))
    sc.append(shape("Leaf Band", [G("B", rect([pct_x(3) - pct_x(1), 14], [(pct_x(1) + pct_x(3)) / 2, SC_Y]), fill(TEA))], [0, 0], a0 + 2.4, D))
    marks = [("Seed", (905, 430), pct_x(1), "SEED (ARABICA) ≈ 1 %", ARA, a0 + 1.2), ("Leaf", (960, 210), pct_x(2.2), "YOUNG LEAF ≈ 1–3 %", TEA, a0 + 2.4),
             ("Nectar", NECTAR2, pct_x(0.05), "NECTAR: A TRACE, BELOW A BEE'S TASTE", CAF, a0 + 3.6)]
    for nm, a, x, lab, col, t in marks:
        sc.append(leader(f"{nm} Leader", a, (x, SC_Y - 12), t, D, col=col))
        sc.append(disc(f"{nm} Tick", [x, SC_Y], 22, col, t + 0.4, D, sh=0, scale=grow(t + 0.4)))
    sc.append(caps("Seed Tick Label", "SEED (ARABICA) ≈ 1 %", [pct_x(1), SC_Y - 70], a0 + 1.6, D, size=14, color=ARA))
    sc.append(caps("Leaf Tick Label", "YOUNG LEAF ≈ 1–3 %", [pct_x(2.6), SC_Y - 40], a0 + 2.8, D, size=14, color=INK))
    sc.append(caps("Nectar Tick Label", "NECTAR: A TRACE", [pct_x(0.05) - 20, SC_Y - 40], a0 + 4.0, D, size=14, color=CAF, just="right"))
    b0 = 7.6
    sc.append(disc("Robusta Tick", [pct_x(2), SC_Y], 30, ROB, b0, D, sh=0, scale=grow(b0)))
    sc.append(caps("Robusta Label", "SEED (ROBUSTA) ≈ 2 %", [pct_x(2), SC_Y - 100], b0 + 0.2, D, size=14, color=ROB))
    sc.append(src("Src Plant", "SOURCE: CEJA-NAVARRO ET AL. (2015); ASHIHARA & CROZIER (2001); WRIGHT ET AL. (2013)", a0 + 1.2, D))
    c0 = 10.4
    fade_all(sc + pl, c0)
    L += sc + pl
    # C: a cherry slides out to centre and opens; D: one molecule grows to 360 px
    crig = "Cherry Rig"
    L.append(cherry_section("Cherry", c0 + 1.4, None, 13.4, crig))
    L += cherry("Cherry", c0, 13.4, crig)
    L.append(null(crig, A(K(c0, [880, 420]), K(c0 + 1.2, [CX, CY])), c0, D, anchor=[CX, CY],
                  scale=A(K(c0, [20, 20]), K(c0 + 1.2, [100, 100]), K(c0 + 2.4, [100, 100]), K(13.4, [260, 260]))))
    L.append(caffeine("Seed Mol", inv((CX, CY)), 13.0, D, scale=A(K(13.0, [8, 8]), K(15.6, [100 / HS, 100 / HS]))))
    L.append(null(rig, list(NECTAR2), 0, D, anchor=list(NECTAR2), position=A(K(po[0], [CX, CY]), K(po[1], list(NECTAR2))),
                  scale=A(K(po[0], [250, 250]), K(po[1], [100, 100]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 3 - BUILT ONCE, INVENTED FIVE TIMES (36 s)
# =====================================================================
ROOT = (960, 960)
TIPS = [("TEA", 330, TEA), ("CACAO", 700, CIN), ("GUARANA", 1000, ARA), ("CITRUS", 1290, RUST), ("COFFEE", 1600, CAF)]
TIP_Y = 260


def s3_origins(D):
    L = []
    # A: the tabs retract and snap back on in sequence (4 s)
    tabs = [A(K(0.6, [100, 100]), K(0.9, [0, 0]), K(1.6 + k * 0.7, [0, 0]), K(1.9 + k * 0.7, [100, 100])) for k in range(3)]
    mol = caffeine("Mol", [CX, CY], 0, 5.6, tabs=tabs,
                   position=A(K(4.6, [CX, CY]), K(5.6, [TIPS[4][1], TIP_Y])), scale=A(K(4.6, [100, 100]), K(5.6, [7, 7])))
    L.append(appear(caps("Theo", "THEOBROMINE · THE STIMULANT IN CHOCOLATE", [CX, 790], 2.2, 3.4, size=18, color=INK), 2.2))
    L.append(src("Src Path", "SOURCE: ASHIHARA, SANO & CROZIER, PHYTOCHEMISTRY (2008)", 0.6, 4.4))
    # B: the tree, five tips far apart
    b0 = 5.6
    tree = [disc("Coffee Tip", [TIPS[4][1], TIP_Y], 24, CAF, b0, D, sh=0)]
    branch = []
    for k, (nm, x, col, ) in enumerate(TIPS):
        mid = (ROOT[0] + (x - ROOT[0]) * 0.45, 640 - abs(x - ROOT[0]) * 0.1)
        branch.append(path([ROOT, mid, (x, TIP_Y)], False, i=[(0, 0), (-(mid[0] - ROOT[0]) * 0.4, 60), (0, 120)], o=[((mid[0] - ROOT[0]) * 0.4, -60), (0, -120), (0, 0)]))
        t = b0 + 1.0 + k * 0.3
        if nm != "COFFEE":
            tree.append(disc(f"Tip {nm}", [x, TIP_Y], 24, GREY2, t, D, sh=0, scale=grow(t)))
        tree.append(caps(f"Tip {nm} Label", nm, [x, TIP_Y - 40], t, D, size=18, color=INK))
    tree.append(shape("Tree", [G("Branches", *branch, trim(0, A(K(b0, 0), K(b0 + 1.4, 100))), stroke(GREY2, 6))], [0, 0], b0, D))
    # C: a single ancestor? the genome page says no
    c0 = 10.6
    L.append(disc("Ancestor", list(ROOT), 60, A(K(c0, CAF), K(c0 + 6.4, GREY2)), c0, 19.6, sh=0, line=INK, scale=grow(c0)))
    L.append(appear(text("Ancestor Q", "?", [ROOT[0], ROOT[1] + 14], 40, INK, c0 + 0.2, 19.6, font=HEAD), c0 + 0.2))
    pg = doc("Genome", [("The coffee genome", 22, HEAD), ("provides insight into", 18, BODY), ("the convergent evolution", 20, BODY), ("of caffeine biosynthesis", 18, BODY)],
             (CX, 520), (420, 320), c0 + 1.2, 18.8, hl_line=2, credit="DENOEUD ET AL., SCIENCE, 2014")
    for l in pg:
        if l["name"] != "Genome Credit":
            l["transform"]["position"] = slide(c0 + 1.2, l["transform"]["position"], dx=0, dy=700, d=0.7) if not isinstance(l["transform"]["position"], dict) else l["transform"]["position"]
            pos = l["transform"]["position"]["keyframes"][-1]["value"]
            l["transform"]["position"]["keyframes"] += [K(18.0, pos), K(18.8, [pos[0], pos[1] + 900])]
    L += pg
    dim(tree, c0 + 1.0, 30)
    for l in tree:
        op = l["transform"]["opacity"]
        last = op["keyframes"][-1]["value"]
        op["keyframes"] += [K(18.8, last), K(19.4, 100)]
    # D: a short blue segment under each tip, the counter
    d0 = 20.0
    for k, (nm, x, col) in enumerate(TIPS):
        t = d0 + 0.6 + k * 0.6
        L.append(shape(f"Seg {nm}", [G("S", path([(x, TIP_Y + 20), (x, TIP_Y + 110)]), trim(0, A(K(t, 0), K(t + 0.4, 100))), stroke(CAF, 10))], [0, 0], t, D))
    L += wipe_text("Count", "At least 5", [CX, 120], 64, INK, d0 + 3.6, D, hl=True)
    L.append(src("Src Count", "SOURCE: HUANG ET AL., PNAS (2016)", d0 + 3.6, D))
    L += tree
    # E: push into the coffee tip, which unfolds into the leaf
    e0 = 31.0
    fade_all(L, e0, keep={"Coffee Tip"})
    add_out(tree[0], e0 + 0.6)
    L.append(grey_leaf("Leaf Out", LEAF_L / HS, A(K(e0 + 0.4, [TIPS[4][1], TIP_Y]), K(e0 + 2.6, inv((CX, CY)))), e0 + 0.4, D,
                       scale=A(K(e0 + 0.4, [5, 5]), K(e0 + 2.6, [100, 100])), rotation=A(K(e0 + 0.4, -60), K(e0 + 2.6, 0))))
    L.insert(0, mol)
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 4 - A POISON FOR INSECTS (27 s)
# =====================================================================
LEAF4 = (520, 520)
CELL = (1380, 500)
ENZ = (1380, 640)


def s4_nerve(D):
    L = []
    s4 = 0.75
    e0 = 23.6
    leaf_pos = A(K(0.4, [CX, CY]), K(1.6, list(LEAF4)), K(e0, list(LEAF4)), K(e0 + 0.8, [LEAF4[0] + 120, 420]), K(e0 + 2.2, inv(FALLEN)))
    leaf_sc = A(K(0.4, [100, 100]), K(1.6, [s4 * 100] * 2), K(e0, [s4 * 100] * 2), K(e0 + 2.2, [FALLEN_L / LEAF_L / HS * 100] * 2))
    leaf_rot = A(K(e0, 0), K(e0 + 1.0, 25), K(e0 + 2.2, 0))
    rig = "Leaf Rig"
    lf = [shape("Notch", [G("N", ell(A(K(3.0, [0, 0]), K(20.0, [150, 110]))), fill(WHITE))], [LEAF_L * 0.3, -LEAF_L * 0.17], 3.0, D, parent=rig),
          grey_leaf("Leaf", LEAF_L, [0, 0], 0, D, parent=rig)]
    L.append(hornworm("Worm", A(K(1.8, [-200, 760]), K(3.0, [LEAF4[0] + 150, LEAF4[1] - 130]), K(21.4, [LEAF4[0] + 150, LEAF4[1] - 130]), K(22.6, [LEAF4[0] + 260, 1300])),
                      1.8, 22.6, s=90, rotation=A(K(1.8, -20), K(3.0, -20), K(21.4, -20), K(22.6, 160))))
    L += lf
    # A: Nathanson's page
    pg = doc("Nathanson", [("Caffeine and related", 20, HEAD), ("methylxanthines:", 18, BODY), ("possible naturally", 18, BODY), ("occurring pesticides", 20, BODY)],
             (1380, 500), (420, 320), 4.0, 9.0, hl_line=3, credit="NATHANSON, SCIENCE, 1984")
    for l in pg:
        if l["name"] != "Nathanson Credit":
            add_out(l, 8.6)
    L += pg
    # B: the nerve cell; signal, messenger, the enzyme clears it
    b0 = 9.4
    flash = X("var f = (time > 18.2 && time < 23.4) ? 100 + 6 * Math.abs(Math.sin((time - 18.2) * 9)) : 100; [f, f]")
    L.append(shape("Cell", [G("Cell", ell([560, 380]), stroke(INK, 5))], list(CELL), b0, e0, scale=flash))
    L.append(shape("Axon", [G("A", path([(CELL[0] - 600, CELL[1] - 300), (CELL[0] - 220, CELL[1] - 120)]), stroke(INK, 5))], [0, 0], b0, e0))
    for k, t in enumerate((b0 + 0.6, 17.0)):
        L.append(disc(f"Pulse {k + 1}", A(K(t, [CELL[0] - 600, CELL[1] - 300]), K(t + 0.6, [CELL[0] - 220, CELL[1] - 120])), 26, INK, t, t + 0.7, sh=0))
    rnd = random.Random(4)
    pts1 = [(rnd.uniform(-160, 160), rnd.uniform(-110, 40)) for _ in range(10)]
    gs = [G(f"M{j + 1}", ell([14, 14], list(p)), fill(INK), tr={"opacity": A(K(b0 + 1.2 + j * 0.04, 100), K(b0 + 2.4 + j * 0.3, 0))}) for j, p in enumerate(pts1)]
    L.append(shape("Messenger 1", gs, list(CELL), b0 + 1.2, b0 + 5.6))
    L.append(shape("Enzyme", [G("Pac", path([(0, 0), (34, -20), (0, -40), (-40, 0), (0, 40), (34, 20)], True,
                                            i=[(0, 0), (0, 0), (22, 0), (0, -22), (-22, 0), (0, 0)], o=[(0, 0), (0, 0), (-22, 0), (0, 22), (22, 0), (0, 0)]),
                                stroke(INK, 4), fill(WHITE))], list(ENZ), b0 + 1.0, e0, scale=[160, 160]))
    L.append(appear(caps("Quiet", "THE CELL GOES QUIET", [CELL[0], CELL[1] + 260], b0 + 4.4, 14.6, size=18, color=INK), b0 + 4.4))
    # C: caffeine wedges into the mouth; the next signal piles up
    c0 = 15.0
    L.append(caffeine("Jam", A(K(c0, [1800, 260]), K(c0 + 1.4, [ENZ[0] + 46, ENZ[1]])), c0, e0, r=16, col=CAF))
    pts2 = [(rnd.uniform(-200, 200), rnd.uniform(-130, 40)) for _ in range(28)]
    gs = [G(f"M{j + 1}", ell([14, 14], list(p)), fill(INK), tr={"opacity": A(K(17.6 + j * 0.06, 0), K(17.7 + j * 0.06, 100))}) for j, p in enumerate(pts2)]
    L.append(shape("Messenger 2", gs, list(CELL), 17.6, e0))
    L.append(appear(caps("Jams", "CAFFEINE JAMS THE OFF SWITCH", [CELL[0], CELL[1] + 260], 18.4, e0, size=18, color=CAF), 18.4))
    for l in L:
        if l["in"] >= b0 and l["out"] >= e0 - 0.01:
            add_out(l, e0)
    # E: the leaf falls onto the soil line
    sy = inv((0, SOIL_Y))[1]
    L.append(shape("Soil", [G("S", path([(-200, sy), (W + 200, sy)]), trim(A(K(e0 + 1.2, 50), K(e0 + 2.0, 0)), A(K(e0 + 1.2, 50), K(e0 + 2.0, 100))),
                              stroke(INK, 4 / HS))], [0, 0], e0 + 1.2, D))
    L.append(null(rig, list(LEAF4), 0, D, anchor=[0, 0], position=leaf_pos, scale=leaf_sc, rotation=leaf_rot))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 5 - A POISON IN THE SOIL (11 s)
# =====================================================================
def s5_soil(D):
    L = []
    rnd = random.Random(5)
    c0 = 8.6
    rain = [G(f"R{k}", path([(0, 0), (0, 22)]), stroke(WATER, 4),
              tr={"position": X(f"[{rnd.uniform(200, 1720):.0f}, (time * 700 + {rnd.uniform(0, 800):.0f}) % 800 - 60]")}) for k in range(26)]
    L.append(shape("Rain", rain, [0, 0], 0.4, c0))
    seep = [G(f"C{k}", ell([12, 12]), fill(CAF), tr={"position": A(K(1.4 + k * 0.12, [FALLEN[0] + rnd.uniform(-150, 150), SOIL_Y + 6]),
                                                                    K(2.6 + k * 0.12, [FALLEN[0] + rnd.uniform(-260, 260), SOIL_Y + rnd.uniform(40, 170)]))})
            for k in range(22)]
    L.append(shape("Seep", seep, [0, 0], 1.4, c0))
    for nm, x, depth, t in (("Near", FALLEN[0] + 300, 60, 3.4), ("Far", 1680, 160, 3.8)):
        L.append(shape(f"Root {nm}", [G("R", path([(x, SOIL_Y), (x - 6, SOIL_Y + depth * 0.5), (x + 4, SOIL_Y + depth)]),
                                         trim(0, A(K(t, 0), K(t + 1.6, 100))), stroke(STEM, 4))], [0, 0], t, c0))
        L.append(shape(f"Sprout {nm}", [G("L", leaf_path(40), fill(MX), tr={"position": [-16, -30], "rotation": 30}),
                                         G("R", leaf_path(40), fill(MX), tr={"position": [16, -30], "rotation": -30}),
                                         G("S", path([(0, 0), (0, -30)]), stroke(STEM, 4))], [x, SOIL_Y], t, c0, scale=grow(t)))
    L.append(appear(caps("Slows", "CAFFEINE IN LEAF LITTER SLOWS ROOTS", [CX, 200], 5.0, c0, size=20, color=INK), 5.0))
    L.append(src("Src Soil", "SOURCE: FRIEDMAN & WALLER, J. CHEM. ECOL. (1983)", 5.0, c0))
    peb = [G(f"P{k}", ell([rnd.uniform(20, 40), rnd.uniform(12, 24)], [rnd.uniform(200, 1700), rnd.uniform(SOIL_Y + 60, 1050)]), stroke(GREY2, 3)) for k in range(9)]
    L.append(shape("Pebbles", peb, [0, 0], 0.8, c0))
    L.append(grey_leaf("Fallen Leaf", FALLEN_L, [FALLEN[0], FALLEN[1]], 0, c0,
                       position=A(K(c0 - 0.6, list(FALLEN)), K(c0 + 0.0, [FALLEN[0], FALLEN[1] + 10]))))
    # held on screen through the push-in so it lands exactly on S6's x-axis
    L.append(shape("Soil", [G("S", path([(-200, SOIL_Y), (W + 200, SOIL_Y)]), stroke(INK, 4))], [0, 0], 0, D,
                   position=A(KL(0, [0, 0]), KL(D, [0, inv((0, SOIL_Y))[1] - SOIL_Y]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 6 - ROBUSTA CARRIES THE MOST (22 s)
# =====================================================================
CH_X0, CH_X1 = 360, 1560


def cx6(p):
    return CH_X0 + (CH_X1 - CH_X0) * p / 3


def cy6(m):
    return SOIL_Y - m * 0.3


K8M, C8M, O8M = 95, (-95.0, 17.6), (CX, 560)


def s6_robusta(D):
    L = []
    crig = "Chart Rig"
    c0 = 11.0
    span = W + 400
    ch = [shape("X Axis", [G("A", path([(-200, SOIL_Y), (W + 200, SOIL_Y)]),
                             trim(A(K(0, 0), K(0.8, (CH_X0 + 200) / span * 100)), A(K(0, 100), K(0.8, (CH_X1 + 260) / span * 100))), stroke(INK, 4))],
                [0, 0], 0, D)]
    ch.append(shape("Y Axis", [G("A", path([(CH_X0, SOIL_Y), (CH_X0, 240)]), trim(0, A(K(0.8, 0), K(1.4, 100))), stroke(INK, 4))], [0, 0], 0.8, D))
    ch.append(shape("Mountain", [G("M", path([(CH_X0 + 40, SOIL_Y), (760, 300), (1000, 520), (1200, 380), (1540, SOIL_Y)]), stroke(LINE, 4))], [0, 0], 1.0, D))
    for v in range(4):
        ch.append(caps(f"X {v}", f"{v} %", [cx6(v), SOIL_Y + 40], 1.0, D, size=15, color=INK))
    ch.append(caps("X Title", "CAFFEINE IN THE SEED", [CH_X1, SOIL_Y + 80], 1.0, D, size=15, just="right"))
    for m in (0, 1000, 2000):
        ch.append(caps(f"Y {m}", f"{m:,}", [CH_X0 - 20, cy6(m) + 6], 1.2, D, size=15, color=INK, just="right"))
    ch.append(caps("Y Title", "ALTITUDE, M", [CH_X0 - 20, 210], 1.2, D, size=15, just="right"))
    ch.append(disc("Arabica", [cx6(1), cy6(1450)], 130, ARA, 2.0, D, sh=0, scale=grow(2.0)))
    ch.append(caps("Arabica Label", "ARABICA · 900–2,000 M", [cx6(1) + 90, cy6(1450) + 6], 2.2, D, size=15, color=ARA, just="left"))
    ch.append(disc("Robusta", [cx6(2), cy6(400)], 130, ROB, 3.0, D, sh=0, scale=grow(3.0)))
    ch.append(caps("Robusta Label", "ROBUSTA · 0–800 M", [cx6(2) + 90, cy6(400) + 6], 3.2, D, size=15, color=ROB, just="left"))
    rnd = random.Random(6)
    pests = []
    for k in range(40):
        y = SOIL_Y - 20 - (rnd.random() ** 2.2) * 600
        pests.append(G(f"P{k}", ell([12, 8], [rnd.uniform(CH_X0 + 30, CH_X1), y]), fill(PEST), tr={"opacity": A(K(5.0 + k * 0.05, 0), K(5.1 + k * 0.05, 100))}))
    ch.append(shape("Pests", pests, [0, 0], 5.0, D))
    ch.append(shape("Hedge Box", [G("B", rect([620, 70], None, 8), stroke(INK, 2))], [1240, 170], 6.6, D))
    ch.append(caps("Hedge", "MORE PESTS IN THE HOT LOWLANDS:", [1240, 164], 6.6, D, size=14, color=INK))
    ch.append(caps("Hedge 2", "A LEADING EXPLANATION, NOT A PROOF", [1240, 188], 6.6, D, size=14, color=INK))
    ch.append(src("Src Chart", "SOURCE: ICO; CEJA-NAVARRO ET AL. (2015)", 1.4, c0))
    parent_all(ch, crig)
    for l in ch:
        l["out"] = min(l["out"], c0 + 0.8)
    L += ch
    L.append(null(crig, [CX, CY], 0, D, position=A(K(c0, [CX, CY]), K(c0 + 0.8, [CX - 2100, CY]))))
    # C: the Mexico map slides in; robusta states fill brown
    mrig = "Map Rig"
    m = lambda ll: map_pt(ll, K8M)
    st_all = [path([m(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    mp = []
    for k, (st, op) in enumerate((("Chiapas", 100), ("Veracruz", 70), ("Puebla", 55), ("Oaxaca", 55))):
        t = c0 + 1.4 + k * 0.4
        mp.append(shape(f"Rob {st}", [G(st, *[path([m(p) for p in r], True) for r in GEO["mexico"][st]], fill(ROB))], [0, 0], t, D, opacity=op))
    mp.append(shape("States", [G("Borders", *st_all, stroke(WHITE, 2)), G("Fill", *st_all, fill(LAND))], [0, 0], c0, D))
    mp.append(land_layer("Land", K8M, c0, D, bbox=(-110, 5, -80, 30)))
    parent_all(mp, mrig)
    chi = state_centroid("Chiapas")
    sacks_g = [G(f"Sack {j + 1}", rect([52, 30], [j * 64, 0], 9), fill(ROB if j == 9 else ARA)) for j in range(10)]
    strip = [shape("Sacks", sacks_g, [1100, 960], c0 + 2.6, 17.4),
             caps("Sacks Label", "MEXICO'S HARVEST, 2025/26", [1100, 920], c0 + 2.6, 17.4, size=15, color=INK, just="left"),
             caps("Growing", "↑ GROWING", [1676, 1016], c0 + 3.4, 17.4, size=14, color=ROB),
             src("Src Mex", "SOURCE: USDA FAS, MEXICO COFFEE ANNUAL, MX2026-0026 (MAY 2026)", c0 + 2.6, 17.4)]
    L += strip + mp
    z0 = 17.6
    o = screen(C8M, K8M, C8M, O8M)
    tgt = map_pt(chi, K8M)
    L.append(null(mrig, [o[0] + 2100, o[1]], c0, D, anchor=m(C8M),
                  position=A(K(c0, [o[0] + 2100, o[1]]), K(c0 + 0.9, list(o)), K(z0, list(o)), K(z0 + 2.4, [CX, CY])),
                  scale=A(K(z0, [100, 100]), K(z0 + 2.4, [600, 600]))))
    L[-1]["transform"]["anchorPoint"] = A(K(z0, m(C8M)), K(z0 + 2.4, tgt))
    # D: a robusta plant in the Chiapas lowlands; push on to one flower, 300 px at centre
    f0 = z0 + 1.6
    for l in L:
        if l["name"] not in (mrig,) and l["out"] > f0:
            add_out(l, f0 + 0.6)
    L.append(flower("Flower Out", FLOWER_D / HS, inv((CX, CY)), f0, D, scale=A(K(f0, [10, 10]), K(D - 0.4, [100, 100]))))
    for k, (p, rot) in enumerate((((-260, -180), -30), ((280, 160), 30))):
        L.append(shape(f"Rob Leaf {k + 1}", [G("L", leaf_path(260), stroke(INK, 2), fill(MX))], [CX + p[0], CY + p[1]], f0, f0 + 1.6, rotation=rot,
                       scale=A(K(f0, [10, 10]), K(f0 + 1.6, [200, 200]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 7 - THE DOSE (38 s, the turn)
# =====================================================================
def s7_dose(D):
    L = []
    frig = "Flower Rig"
    fl = [bee("Bee", A(K(0.6, [1500, 100]), K(2.0, [CX + 30, CY - 40])), 0.6, D, s=150, rotation=A(K(0.6, -30), K(2.0, 0))),
          flower("Flower", FLOWER_D, [CX, CY], 0, D)]
    parent_all(fl, frig)
    L += fl
    # B: the lab, two harnessed bees
    b0 = 3.6
    lab = []
    for k, (x, nm, col) in enumerate(((1100, "SUGAR", GREY2), (1560, "SUGAR + NECTAR-LEVEL CAFFEINE", CAF))):
        t = b0 + 0.6 + k * 0.5
        lab.append(bee(f"Lab Bee {k + 1}", [x, 380], t, 10.0, s=120))
        lab.append(shape(f"Harness {k + 1}", [G("H", rect([90, 40], [0, 30], 6), stroke(INK, 3))], [x, 380], t, 10.0))
        lab.append(disc(f"Drop {k + 1}", [x - 60, 470], 34, col, t + 0.3, 10.0, sh=0, scale=grow(t + 0.3)))
        lab.append(caps(f"Lab Label {k + 1}", nm, [x, 560], t + 0.3, 10.0, size=15, color=INK if k == 0 else CAF))
    lab.append(src("Src Lab", "WRIGHT ET AL., SCIENCE, 2013", b0 + 0.6, 10.0))
    L += lab
    # C: paired bars on one axis
    c0 = 10.0
    BX = [(1080, 60, 180, "24 H"), (1500, 60, 120, "72 H")]
    bars = [shape("Bar Axis", [G("A", path([(900, 820), (1740, 820)]), stroke(INK, 3))], [0, 0], c0, 20.0)]
    for k, (x, g, b, lb) in enumerate(BX):
        t = c0 + 0.6 + k * 1.2
        for nm, dx, h, col in (("Grey", -50, g * 2, GREY2), ("Blue", 50, b * 2, CAF)):
            bars.append(shape(f"Bar {lb} {nm}", [G("B", rect([80, h], [0, -h / 2]), fill(col))], [x + dx, 820], t, 20.0, scale=A(K(t, [100, 0]), K(t + 0.6, [100, 100]))))
        bars.append(caps(f"Bar {lb} Label", lb, [x, 860], t, 20.0, size=16, color=INK))
    bars.append(caps("Bar Title", "BEES THAT REMEMBERED THE SCENT", [1320, 300], c0 + 0.4, 20.0, size=16, color=INK))
    bars.append(appear(text("Three", "3×", [BX[0][0] + 50, 820 - 360 - 30], 44, CAF, c0 + 1.4, 20.0, font=HEAD), c0 + 1.4))
    bars.append(appear(text("Two", "2×", [BX[1][0] + 50, 820 - 240 - 30], 44, CAF, c0 + 2.6, 20.0, font=HEAD), c0 + 2.6))
    bars.append(src("Src Bars", "SOURCE: WRIGHT ET AL., SCIENCE 339:1202 (2013)", c0 + 0.6, 20.0))
    for l in bars:
        p = l["transform"]["position"]
        if not isinstance(p, dict):
            l["transform"]["position"] = A(K(19.4, p), K(20.0, [p[0], p[1] - 1100]))
        else:
            v = p["keyframes"][-1]["value"]
            p["keyframes"] += [K(19.4, v), K(20.0, [v[0], v[1] - 1100])]
    L += bars
    L.append(null(frig, [CX, CY], 0, D, position=A(K(b0, [CX, CY]), K(b0 + 0.8, [480, 480]), K(19.4, [480, 480]), K(20.0, [480, -620])),
                  scale=A(K(b0, [100, 100]), K(b0 + 0.8, [70, 70]))))
    # D: the dose scale; the bee at the low end, the hornworm at the high end
    d0 = 20.4
    L += dose_scale(D, d0, 33.0)
    L.append(bee("Low Bee", A(K(d0 + 1.0, [420, -100]), K(d0 + 1.8, [420, 840])), d0 + 1.0, 33.0, s=90))
    L.append(appear(caps("Memory", "MEMORY AID", [420, 760], d0 + 2.0, 33.0, size=18, color=INK), d0 + 2.0))
    hw_end = [1500, 850]
    L.append(appear(caps("Poison", "POISON", [1500, 760], d0 + 3.2, 33.0, size=18, color=PEST), d0 + 3.2))
    L += wipe_text("Decides", "The dose decides", [CX, 480], 72, INK, d0 + 4.6, 33.0, hl=True)
    # E: push on the hornworm; it curls into a 16 px dot
    e0 = 33.0
    L.append(hornworm("Worm", A(K(d0 + 2.4, [1500, -100]), K(d0 + 3.2, hw_end), K(e0, hw_end), K(e0 + 2.0, inv((CX, CY)))), d0 + 2.4, e0 + 2.4,
                      scale=A(K(e0, [70, 70]), K(e0 + 2.4, [12, 12])), rotation=A(K(e0, 0), K(e0 + 2.4, 540))))
    L.append(disc("Pest Dot", inv((CX, CY)), CHAPAS_DOT / HS, PEST, e0 + 2.4, D, sh=0))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 8 - LA BROCA (34 s)
# =====================================================================
K8, O8 = 70, (CX, CY)
GUAT = (-90.5, 14.6)
SAMPLES = [(37.9, -0.5), (110.4, -7.4), (76.0, 12.0), (-66.5, 18.2), (-155.5, 19.6), (-90.5, 14.6), (-92.6, 16.4)]


def s8_broca(D):
    L = []
    s8 = lambda ll: screen(ll, K8, CHAPAS, O8)
    rig = "Map Rig"
    m0, m1 = 0, 8.6
    L.append(disc("Arrival", [CX, CY], CHAPAS_DOT, PEST, 0, m1, sh=0))
    g = s8(GUAT)
    L.append(shape("Arrow", [G("A", arc(g, (CX + 10, CY + 8), -0.35), trim(0, A(K(0.4, 0), K(1.6, 100))), stroke(PEST, 4))], [0, 0], 0.4, m1))
    L.append(appear(caps("Arrival Label", "CACAHOATÁN, CHIAPAS, 1978", [CX - 30, CY - 40], 1.4, m1, size=18, color=INK, just="right"), 1.4))
    L.append(src("Src Arrival", "SOURCE: SENASICA; DOF QUARANTINE DECREE, 1978", 1.4, m1))
    rnd = random.Random(8)
    stain = []
    for k in range(18):
        ll = (rnd.uniform(-97.5, -91.5), rnd.uniform(15.0, 20.0))
        t = 2.6 + k * 0.25
        stain.append(G(f"E{k}", ell([rnd.uniform(60, 140), rnd.uniform(40, 90)], s8(ll)), fill(PEST, 40),
                       tr={"anchorPoint": s8(ll), "position": s8(ll), "scale": A(K(t, [0, 0]), K(t + 1.4, [100, 100]))}))
    L.append(shape("Stain", stain, [0, 0], 2.6, m1))
    st_all = [path([s8(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    L.append(shape("States", [G("Borders", *st_all, stroke(WHITE, 2)), G("Fill", *st_all, fill(LAND))], [0, 0], 0, m1))
    land = land_layer("Land", K8, 0, m1, bbox=(-110, 5, -80, 30))
    land["transform"]["position"] = [O8[0] - CHAPAS[0] * K8, O8[1] + CHAPAS[1] * K8]
    L.append(land)
    for l in L:
        add_out(l, m1 - 0.3)
    # B: the cherry, a sesame seed, the borer; it bores in
    b0 = 9.0
    crig = "Cherry Rig"
    L.append(shape("Sesame", [G("S", path([(0, -34), (16, 10), (0, 30), (-16, 10)], True, i=[(0, 0), (0, -16), (9, 0), (0, 9)], o=[(0, 0), (0, 9), (-9, 0), (0, -16)]),
                                stroke(INK, 2), fill(SEED))], [1460, 560], b0 + 0.6, 12.4, scale=grow(b0 + 0.6)))
    L.append(caps("Sesame Label", "SESAME ≈ 3 MM", [1460, 640], b0 + 0.8, 12.4, size=15, color=INK))
    L.append(caps("Borer Label", "BORER ≈ 2 MM", [1260, 640], b0 + 0.8, 12.4, size=15, color=PEST))
    L.append(borer("Borer", A(K(b0 + 0.6, [1260, 570]), K(12.6, [1260, 570]), K(13.6, [CX, CY - 104])), b0 + 0.6, 14.2))
    L.append(disc("Hole", [CX, CY - 100], 16, ARA_DARK, 14.0, 17.0, sh=0, parent=crig))
    L.append(cherry_section("Cherry", 14.4, None, 17.0, crig))
    L.append(shape("Tunnel", [G("T", path([(CX + 30, CY - 70), (CX + 40, CY - 20), (CX + 32, CY + 30)]), trim(0, A(K(15.0, 0), K(15.8, 100))), stroke(PEST, 6)),
                              G("Seed Blue", path([(CX + 6, CY - 72), (CX + 6, CY + 72)], True, i=[(0, 0), (70, 0)], o=[(70, 0), (0, 0)]), stroke(CAF, 5))],
                   [0, 0], 14.8, 17.0, parent=crig))
    L += cherry("Cherry", b0, 17.0, crig)
    L.append(null(crig, [CX, CY], b0, D, scale=A(K(16.2, [100, 100]), K(17.0, [400, 400])), anchor=[CX + 36, CY]))
    # C: the gut, bacteria eating the caffeine stream
    c0 = 17.0
    gut_op = A(K(21.0, 100), K(21.4, 30), K(25.0, 30), K(25.4, 100))
    bact = [G(f"B{k}", rect([60, 22], [rnd.uniform(60, 360), rnd.uniform(-70, 70)], 11), fill(A(K(26.6, MAG), K(27.2, GREY2))), tr={"rotation": rnd.uniform(-40, 40)})
            for k in range(12)]
    L.append(shape("Bacteria", bact, [CX, CY], c0 + 0.6, 30.4, opacity=gut_op))
    flow = []
    for k in range(18):
        y = rnd.uniform(-80, 80)
        off = rnd.uniform(0, 640)
        flow.append(G(f"F{k}", ell([16, 16]), fill(CAF),
                      tr={"position": X(f"var x = -560 + ((time * 220 + {off:.0f}) % 640); [x, {y:.0f}]"),
                          "opacity": X(f"var x = -560 + ((time * 220 + {off:.0f}) % 640); x > 40 ? 0 : 100")}))
    L.append(shape("Flow", flow, [CX, CY], c0 + 0.8, 26.6, opacity=gut_op))
    pile = [G(f"P{k}", ell([16, 16], [rnd.uniform(-100, 380), rnd.uniform(-90, 90)]), fill(CAF), tr={"opacity": A(K(26.6 + k * 0.05, 0), K(26.65 + k * 0.05, 100))})
            for k in range(40)]
    L.append(shape("Pile", pile, [CX, CY], 26.6, 30.4))
    L.append(shape("Gut", [G("G", rect([1300, 280], None, 140), stroke(INK, 5), fill(WHITE))], [CX, CY], c0, 30.4, opacity=gut_op))
    L.append(text("Bact Label", "Pseudomonas fulva and others live on caffeine", [CX, 280], 34, INK, c0 + 1.4, 21.0, font=SCI))
    L.append(caps("Bact Label 2", "IN THE BEETLE'S GUT", [CX, 320], c0 + 1.4, 21.0, size=15))
    # the sampling strip
    W8 = 4.6
    ws = lambda ll: screen(ll, W8, (0, 10), (CX, 860))
    strip = [land_layer("World", W8, 21.2, 25.0, bbox=(-180, -45, 180, 60))]
    strip[0]["transform"]["position"] = [CX, 860 + 10 * W8]
    for k, ll in enumerate(SAMPLES):
        strip.append(disc(f"Sample {k + 1}", ws(ll), 16, MX if k == 6 else PEST, 21.6 + k * 0.15, 25.0, sh=0, scale=grow(21.6 + k * 0.15)))
    cp = ws(SAMPLES[6])
    strip.append(marker("Chiapas Swipe", cp[0] - 10, cp[1] + 44, 120, 22.8, 25.0, size=20))
    strip.append(caps("Chiapas Name", "CHIAPAS", [cp[0] + 50, cp[1] + 44], 22.8, 25.0, size=16, color=INK))
    strip.append(caps("Samples", "7 COFFEE REGIONS SAMPLED", [CX, 660], 21.4, 25.0, size=16, color=INK))
    strip.append(src("Src Gut", "SOURCE: CEJA-NAVARRO ET AL., NAT. COMMUN. (2015)", 18.4, 30.4))
    for l in strip[:-1]:
        p = l["transform"]["position"]
        l["transform"]["position"] = A(K(21.2, [p[0], p[1] + 400]), K(21.8, p), K(24.4, p), K(25.0, [p[0], p[1] + 400]))
    L += strip
    # D: the antibiotic
    L.append(shape("Pill", [G("Half", rect([40, 50], [0, 25], 0), fill(WHITE)), G("Pill", rect([50, 100], None, 25), stroke(INK, 4), fill("#E6E6E6"))],
                   A(K(25.6, [CX + 200, -100]), K(26.4, [CX + 200, CY])), 25.6, 30.4, rotation=A(K(25.6, -30), K(26.4, 60))))
    L.append(appear(caps("No Bacteria", "NO BACTERIA, NO DIGESTION", [CX, 820], 27.2, 30.4, size=20, color=INK), 27.2))
    # E: pull back to the closed cherry, its hole at the tip
    e0 = 30.4
    erig = "End Rig"
    L += cherry("End Cherry", e0, D, erig)
    L.append(disc("End Hole", [CX, CY - 100], 16, ARA_DARK, e0, D, sh=0, parent=erig))
    L.append(null(erig, [CX, CY], e0, D, scale=A(K(e0, [300, 300]), K(D - 0.4, [100 / HS, 100 / HS]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 9 - MEXICO'S ANSWER (27 s)
# =====================================================================
def s9_wasps(D):
    L = []
    crig = "Cherry Rig"
    d0 = 21.4
    L.append(wasp("Wasp", A(K(1.0, [1600, 120]), K(2.2, [CX + 40, CY - 128]), K(10.6, [CX + 40, CY - 128]), K(12.0, [CX + 30, CY - 20])), 1.0, 15.6,
                  scale=[130, 130]))
    sec = cherry_section("Cherry", 10.0, 20.4, D, crig)
    L.append(shape("Young", [G("Y", ell([22, 14], [CX + 36, CY]), ell([22, 14], [CX + 46, CY + 30]), fill(A(K(15.0, PEST), K(15.6, GREY2))))], [0, 0], 10.6, 20.4, parent=crig))
    L.append(shape("Eggs", [G("E", ell([8, 8], [CX + 30, CY - 6]), ell([8, 8], [CX + 52, CY + 24]), fill(INK))], [0, 0], 13.2, 20.4, parent=crig))
    L.append(sec)
    L.append(disc("Hole", [CX, CY - 100], 16, ARA_DARK, 0, D, sh=0, parent=crig))
    L += cherry("Cherry", 0, D, crig)
    # A: the dashed arc from Africa
    W9 = 5.0
    ws = lambda ll: screen(ll, W9, (-30, 10), (CX, 880))
    strip = [land_layer("World", W9, 2.4, 9.6, bbox=(-120, -40, 60, 45))]
    strip[0]["transform"]["position"] = [CX + 30 * W9, 880 + 10 * W9]
    a, b = ws((20, 2)), ws((-92.6, 16.4))
    strip.append(shape("Wasp Arc", [G("A", arc(a, b, -0.3), trim(0, A(K(3.0, 0), K(4.4, 100))), stroke(INK, 3))], [0, 0], 3.0, 9.6))
    strip.append(disc("Chiapas Dot", b, 14, MX, 4.4, 9.6, sh=0, scale=grow(4.4)))
    for l in strip:
        p = l["transform"]["position"]
        l["transform"]["position"] = A(K(2.4, [p[0], p[1] + 400]), K(3.0, p), K(9.0, p), K(9.6, [p[0], p[1] + 400]))
    L += strip
    L += wipe_text("Year", "1988 · 2 species of African wasp", [CX, 140], 44, INK, 4.6, 21.0)
    nm = [text("Name Ceph", "Cephalonomia stephanoderis", [CX - 380, 210], 30, INK, 5.4, 21.0, font=SCI),
          text("Name Prorops", "Prorops nasuta", [CX + 340, 210], 30, INK, 5.6, 21.0, font=SCI)]
    L += nm
    L.append(shape("Prorops Grey", [G("R", rect([300, 44], [0, -10]), fill(WHITE, 60))], [CX + 340, 210], 16.0, 21.0))
    L.append(marker("Ceph Swipe", CX - 380 - 200, 210, 400, 16.6, 21.0, size=30))
    L.append(caps("Established", "ESTABLISHED", [CX - 380, 250], 17.0, 21.0, size=16, color=INK))
    L.append(src("Src Wasps", "SOURCE: BARRERA ET AL. (1991); LÓPEZ-RODRÍGUEZ ET AL., ACTA ZOOL. MEX. (2009)", 3.0, 21.0))
    # D: the cherry slides up onto a Chiapas branch beside an opening flower
    brig = "Branch Rig"
    L += branch_layers(d0, D, brig, flower_t=d0 + 1.6)
    L.append(null(brig, [CX, CY], d0, D, scale=A(K(d0, [100 / HS, 100 / HS]))))
    L[-1]["transform"]["scale"] = [100 / HS, 100 / HS]
    end = inv(CH_END)
    L.append(null(crig, [CX, CY], 0, D, position=A(K(d0, [CX, CY]), K(d0 + 1.6, end)), scale=A(K(d0, [100, 100]), K(d0 + 1.6, [CH_END_S / HS] * 2))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 10 - CLOSE (20 s)
# =====================================================================
def s10_close(D):
    L = []
    brig, crig = "Branch Rig", "Cherry Rig"
    L.append(bee("Bee", A(K(1.2, [1700, 80]), K(2.6, [790, 370])), 1.2, D, s=60))
    # B: one blue dot, two leaders
    b0 = 5.0
    dot = (1010, 620)
    L.append(disc("Caf Dot", list(dot), 30, CAF, b0, 12.6, sh=0, scale=grow(b0)))
    L.append(leader("To Seed", dot, (CH_END[0] - 20, CH_END[1] + 50), b0 + 0.4, 12.6, col=CAF))
    L.append(leader("To Nectar", dot, (770, 450), b0 + 0.4, 12.6, col=CAF))
    L.append(caps("Defence", "DEFENCE", [CH_END[0] + 20, CH_END[1] + 120], b0 + 0.8, 12.6, size=20, color=INK, just="left"))
    L.append(caps("Reward", "REWARD", [700, 500], b0 + 0.8, 12.6, size=20, color=INK, just="right"))
    # the dose scale returns once
    f0 = 8.6
    L += dose_scale(D, f0, 12.6, prefix="End ")
    L.append(bee("Dose Bee", [420, 850], f0 + 0.6, 12.6, s=70))
    L.append(hornworm("Dose Worm", [1460, 850], f0 + 0.8, 12.6, s=55))
    L.append(borer("Dose Borer", [1580, 850], f0 + 1.0, 12.6, s=120))
    # C: end card
    L += wipe_text("End Title", "Why Does a Plant Make Caffeine?", [CX, 930], 64, INK, 13.2, D)
    L.append(word_marker("End Swipe", "Why Does a Plant Make Caffeine?", "Caffeine?", CX, 930, 64, 14.0, D))
    L += cherry("Cherry", 0, D, crig)
    L.append(disc("Hole", [CX, CY - 100], 16, ARA_DARK, 0, D, sh=0, parent=crig))
    L.append(null(crig, list(CH_END), 0, D, anchor=[CX, CY], scale=[CH_END_S, CH_END_S]))
    L += branch_layers(0, D, brig)
    L.append(null(brig, [CX, CY], 0, D))
    L.append(bg(D))
    return L


SCENES = [("S1_Flower", 15.0, s1_flower), ("S2_Plant", 17.0, s2_plant), ("S3_Origins", 36.0, s3_origins), ("S4_Nerve", 27.0, s4_nerve),
          ("S5_Soil", 11.0, s5_soil), ("S6_Robusta", 22.0, s6_robusta), ("S7_Dose", 38.0, s7_dose), ("S8_Broca", 34.0, s8_broca),
          ("S9_Wasps", 27.0, s9_wasps), ("S10_Close", 20.0, s10_close)]

if __name__ == "__main__":
    write(SCENES, "Why_Caffeine", "07_why_caffeine")
