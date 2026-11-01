"""Generator for episode 5, "Why Veracruz Lets Its Coffee Go Sour" (scripts/05_processing_script.md).

    python "Coffee Episodes/generators/05_processing.py"      # writes ../json/05_processing.json

Rigs are nulls with anchor [0, 0]: content point c lands on screen at P + c * s; handoff() writes the next scene's
start (P, s) as this scene's end, undoing the master push-in. No fades: cut_pass turns exits into cuts or pops.
"""
import math, random

from coffee_common import *  # noqa: F401,F403

MAG = "#B4457F"
COATEPEC = (-96.96, 19.45)


def handoff(P, s):
    return inv(P), s / HS


def rig(name, D, keys, t0=0):
    return null(name, [0, 0], t0, D, anchor=[0, 0], position=A(*[K(t, list(P)) for t, P, s in keys]),
                scale=A(*[K(t, [s * 100, s * 100]) for t, P, s in keys]))


def tag(name, s, pos, t, t1, size=16, color=INK, just="center", **tr):
    return appear(caps(name, s, pos, t, t1, size=size, color=color, just=just, **tr), t)


def arrow(name, a, b, t, t1, col=INK, w=4):
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    hd = [(b[0] - 16 * math.cos(ang - 0.5), b[1] - 16 * math.sin(ang - 0.5)), b, (b[0] - 16 * math.cos(ang + 0.5), b[1] - 16 * math.sin(ang + 0.5))]
    return shape(name, [G("A", path([a, b]), path(hd), trim(0, A(K(t, 0), K(t + 0.5, 100))), stroke(col, w))], [0, 0], t, t1)


# ---------------------------------------------------------------------
# the declaration (S1, S9)
# ---------------------------------------------------------------------
CL = ["…su acidez se atribuye a la altura", "y a la arraigada tradición de fermentar", "el café recién despulpado."]
CL_Y, CL_S = [520, 556, 592], 22
ZS = 2.4
ZP = (CX - CX * ZS, CY - CL_Y[1] * ZS)
L3W = tw(CL[2], CL_S, BODY)
CAP = (ZP[0] + (CX + L3W / 2 + 10) * ZS, ZP[1] + (CL_Y[2] - CL_S * 0.3) * ZS)
UNDER_Y = ZP[1] + (CL_Y[2] + 8) * ZS


def page(t0, t1, rg, type_t=None, swipes_t=None):
    op = (lambda k: fade_in(type_t + k * 0.25, 0.2)) if type_t is not None else (lambda k: 100)
    out = []
    head = [("DIARIO OFICIAL", 24, HEAD, 170), ("DECLARATORIA DE PROTECCIÓN DE LA", 15, LAB, 230), ("DENOMINACIÓN DE ORIGEN \"CAFÉ VERACRUZ\"", 15, LAB, 258)]
    for k, (s, sz, f, y) in enumerate(head):
        out.append(text(f"Head {k + 1}", s, [CX, y], sz, INK, t0, t1, font=f, tracking=60 if f == LAB else 0, parent=rg, opacity=op(k)))
    for k, s in enumerate(CL):
        out.append(text(f"Clause {k + 1}", s, [CX, CL_Y[k]], CL_S, INK, t0, t1, font=BODY, parent=rg, opacity=op(4 + k)))
    bars = [rect([w, 8], [CX - (620 - w) / 2, y]) for y, w in ((320, 620), (346, 600), (372, 620), (398, 520), (424, 610), (450, 380),
                                                                (650, 620), (676, 580), (702, 620), (728, 600), (754, 460), (820, 620), (846, 300))]
    out.append(shape("Filler", [G("F", *bars, fill(LINE))], [0, 0], t0, t1, parent=rg, opacity=op(3)))
    out.append(shape("Sheet", [G("S", rect([760, 1000], [CX, 540], 4), stroke("#D0D0D0", 2), fill(WHITE))], [0, 0], t0, t1, parent=rg))
    if swipes_t is not None:
        a, b = swipes_t
        out.insert(0, word_marker("Swipe Altura", CL[0], "altura", CX, CL_Y[0], CL_S, a, t1, font=BODY))
        out.insert(0, word_marker("Swipe Fermentar", CL[1], "fermentar", CX, CL_Y[1], CL_S, b, t1, font=BODY))
        out.insert(0, marker("Swipe Pulped", CX - L3W / 2 - 10, CL_Y[2], L3W + 20, b + 0.35, t1, size=CL_S))
        for l in out[:3]:
            l["parent"] = rg
        # markers sit under the text: move them below the clause layers
        sw, rest = out[:3], out[3:]
        out = rest[:-2] + sw + rest[-2:]
    return out


# =====================================================================
# SCENE 1 - THE LAW (23 s)
# =====================================================================
def s1_law(D):
    L = []
    rg = "Page Rig"
    z0, z1, sa, sb, c0 = 6.0, 8.4, 9.6, 12.0, 18.0
    L.append(tag("Meaning", "= FERMENTING FRESHLY PULPED COFFEE", [CX, UNDER_Y + 90], sb + 1.0, c0, size=20))
    L.append(src("Src DOF", "DIARIO OFICIAL DE LA FEDERACIÓN, 15 NOV 2000", 1.0, c0))
    pg = page(0, D, rg, type_t=0.4, swipes_t=(sa, sb))
    for l in pg:
        if not l["name"].startswith("Swipe Pulped"):
            add_out(l, c0)
    L += pg
    L.insert(0, disc("Cap Dot", A(K(c0, list(CAP)), K(c0 + 0.6, list(CAP)), K(D - 0.4, inv((CX, CY)))), 24, ARA, c0, D, sh=0,
                     scale=A(K(c0 + 0.6, [100, 100]), K(D - 0.4, [300 / 24 / HS * 100] * 2))))
    sp = [l for l in L if l["name"] == "Swipe Pulped"][0]
    sp["transform"]["scale"]["keyframes"] += [K(c0, [100, 100]), K(c0 + 0.6, [0, 100])]
    sp["out"] = c0 + 0.6
    L.append(rig(rg, D, [(0, (0, 0), 1), (z0, (0, 0), 1), (z1, ZP, ZS)]))
    L.append(bg(D))
    return L


# =====================================================================
# the cherry layers
# =====================================================================
LAYERS = {"muc": [130, 150], "parch": [104, 124], "silver": [96, 116], "seed": [88, 108]}


def seed_unit(name, pos, t0, t1, muc=1.0, muc_col=WHITE, parch=True, **tr):
    """Seed, silverskin, parchment and mucilage ring as one layer around pos (base size: CHERRY_D cross-section)."""
    items = [G("Crease", path([(0, -36), (0, 36)], False, i=[(0, 0), (-12, -14)], o=[(12, 14), (0, 0)]), stroke(SEED_LINE, 3)),
             G("Seed", ell(LAYERS["seed"]), fill(SEED)),
             G("Silverskin", ell(LAYERS["silver"]), stroke(GREY2, 2))]
    if parch:
        items.append(G("Parchment", ell(LAYERS["parch"]), stroke(SEED_LINE, 4), fill("#FBF6EA")))
    if muc is not None:
        mt = {"scale": muc} if isinstance(muc, dict) else {"scale": [muc * 100, muc * 100]}
        items.append(G("Mucilage", ell(LAYERS["muc"]), stroke(INK, 3), fill(muc_col), tr=mt))
    return shape(name, items, pos, t0, t1, **tr)


# =====================================================================
# SCENE 2 - INSIDE THE CHERRY (29 s)
# =====================================================================
S2 = 300 / CHERRY_D


def s2_layers(D):
    L = []
    rg, sr = "Cherry Rig", "Seed Rig"
    o0, b0, c0 = 1.2, 13.0, 22.0
    names = [("SKIN", CHERRY_D, -40), ("PULP", 196, -20), ("MUCILAGE", LAYERS["muc"][1], 0), ("PARCHMENT", LAYERS["parch"][1], 18),
             ("SILVERSKIN", LAYERS["silver"][1], 34), ("SEED", 60, 50)]
    for k, (nm, d, a) in enumerate(names):
        t = o0 + 1.2 + k * 1.3
        r = d / 2 * S2 * 0.92
        p = (CX + r * math.cos(math.radians(a)), CY + r * math.sin(math.radians(a)))
        lp = (1300, 300 + k * 90)
        L.append(leader(f"{nm} Leader", p, (lp[0] - 16, lp[1] - 6), t, c0))
        L.append(caps(f"{nm} Label", nm, list(lp), t + 0.3, c0, size=18, color=INK, just="left"))
    L.append(marker("Muc Swipe", 1290, 480, tw("MUCILAGE", 18, LAB) + 50, b0, c0, size=18))
    bx, by, bh = 330, 800, 460
    comp = [("WATER ≈ 85–91 %", 0.88, WATER), ("SUGARS ≈ 6–7 %", 0.07, SEED_LINE), ("PECTIN AND OTHER", 0.05, GREY)]
    y = by
    for k, (s, f, col) in enumerate(comp):
        h = bh * f
        t = b0 + 0.6 + k * 0.5
        L.append(shape(f"Comp {k + 1}", [G("B", rect([70, h], [0, -h / 2]), fill(col))], [bx, y], t, c0, scale=A(K(t, [100, 0]), K(t + 0.4, [100, 100]))))
        L.append(caps(f"Comp Label {k + 1}", s, [bx + 60, y - h / 2 + 6 - k * 16], t, c0, size=14, color=INK, just="left"))
        y -= h
    L.append(caps("Comp Title", "INSIDE THE MUCILAGE", [bx - 35, by - bh - 30], b0 + 0.6, c0, size=14, color=INK, just="left"))
    L.append(src("Src Cenicafe", "SOURCE: CENICAFÉ", b0, c0))
    for l in L:
        add_out(l, c0)
    L.append(seed_unit("Seed Unit", [CX, CY], o0, D, parent=sr, scale=grow(o0, 100, 0.5)))
    L.append(shape("Pulp", [G("P", ell([196, 196]), fill(PULP))], [CX, CY], o0, c0 + 0.8, parent=rg,
                   scale=A(K(o0, [0, 0]), K(o0 + 0.5, [100, 100]), K(c0, [100, 100]), K(c0 + 0.8, [0, 0]))))
    ch = cherry("Cherry", 0, c0 + 0.8, rg)
    for l in ch:
        l["transform"]["position"] = A(K(c0, l["transform"]["position"]), K(c0 + 0.8, [l["transform"]["position"][0] + 1400, l["transform"]["position"][1]]))
    L += ch
    L.append(null(rg, [CX, CY], 0, D, scale=[S2 * 100] * 2))
    L.append(null(sr, [CX, CY], 0, D, scale=A(K(c0 + 0.8, [S2 * 100] * 2), K(D - 0.4, [S2 * 100 / HS] * 2))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 3 - HOW MUCH FRUIT STAYS ON (34 s)
# =====================================================================
AX_Y, AX0, AX1 = 360, 260, 1660
S3 = 0.6
SEED4, S4 = (CX, 640), 1.0


def s3_axis(D):
    L = []
    rg = "Axis Rig"
    a1, b0, c0, d0 = 1.2, 4.0, 19.0, 28.0
    L.append(shape("Fruit Axis", [G("A", path([(AX0, AX_Y), (AX1, AX_Y)]), trim(A(K(a1, 50), K(a1 + 1.0, 0)), A(K(a1, 50), K(a1 + 1.0, 100))), stroke(INK, 4))],
                   [0, 0], a1, D, parent=rg))
    L.append(caps("Axis Title", "FRUIT LEFT ON THE SEED WHILE IT DRIES", [CX, AX_Y - 150], a1 + 0.6, D, size=16, color=INK, parent=rg))
    L.append(caps("None", "NONE", [AX0, AX_Y + 50], a1 + 0.8, D, size=14, color=INK, parent=rg))
    L.append(caps("All", "ALL", [AX1, AX_Y + 50], a1 + 0.8, D, size=14, color=INK, parent=rg))
    # natural: a cherry at ALL dries to a husk
    L.append(disc("Natural", [AX1, AX_Y - 70], 90, A(K(b0 + 1.0, ARA), K(b0 + 3.0, OXID)), b0, D, sh=0, parent=rg, scale=grow(b0)))
    L.append(caps("Natural Label", "NATURAL, THE OLDEST METHOD", [AX1, AX_Y + 80], b0 + 0.4, D, size=13, color=INK, parent=rg))
    L.append(caps("Natural Days", "≈ 3–4 WEEKS", [AX1, AX_Y - 140], b0 + 1.0, D, size=13, color=INK, parent=rg))
    honey = [("WHITE", 560, 0.4, ROAST[0]), ("YELLOW", 860, 0.6, ROAST[1]), ("RED", 1160, 0.8, ROAST[2]), ("BLACK", 1400, 1.0, ROAST[3])]
    for k, (nm, x, m, col) in enumerate(honey):
        t = b0 + 4.0 + k * 0.7
        L.append(seed_unit(f"Honey {nm}", [x, AX_Y - 70], t, D, muc=m * 1.25, muc_col=col, parent=rg,
                           position=A(K(t, [x, AX_Y - 400]), K(t + 0.5, [x, AX_Y - 70])), scale=[S3 * 100] * 2))
        L.append(caps(f"Honey {nm} Label", f"{nm} HONEY", [x, AX_Y + 50], t + 0.4, D, size=13, color=INK, parent=rg))
    L.append(caps("Washed Label", "WASHED", [AX0, AX_Y + 80], 12.0, D, size=13, color=INK, parent=rg))
    L.append(src("Src Methods", "SOURCE: SCA; ICAFE", b0, d0))
    # C: the oxygen branch
    L.append(shape("Oxygen Axis", [G("A", path([(CX, AX_Y), (CX, 980)]), trim(0, A(K(c0, 0), K(c0 + 0.8, 100))), stroke(INK, 4))], [0, 0], c0, D, parent=rg))
    L.append(caps("Open", "OXYGEN: OPEN", [CX + 20, AX_Y + 110], c0 + 0.4, D, size=13, color=INK, just="left", parent=rg))
    L.append(caps("Sealed", "SEALED", [CX + 20, 960], c0 + 0.4, D, size=13, color=INK, just="left", parent=rg))
    L.append(shape("Sealed Tank", [G("T", rect([200, 150], None, 10), path([(-110, -75), (110, -75)]), stroke(INK, 4))], [CX, 820], c0 + 0.8, D, parent=rg,
                   scale=grow(c0 + 0.8)))
    L.append(seed_unit("Anaerobic Seed", [CX, AX_Y + 90], c0 + 1.0, D, parent=rg, scale=[S3 * 100 * 0.8] * 2,
                       position=A(K(c0 + 1.2, [CX, AX_Y + 90]), K(c0 + 2.6, [CX, 830]))))
    L.append(caps("Anaerobic", "ANAEROBIC", [CX - 130, 830], c0 + 2.6, D, size=13, color=INK, just="right", parent=rg))
    for l in L:
        if l["out"] > d0 and l["name"] != "Src Methods":
            add_out(l, d0)
    # the S2 seed slides to NONE and loses its mucilage: WASHED
    wpos = (AX0, AX_Y - 70)
    L.insert(0, seed_unit("Washed", [CX, CY], 0, D, muc=A(K(10.4, [100, 100]), K(11.2, [0, 0])), parent=rg,
                          position=A(K(0, [CX, CY]), K(a1, [CX, AX_Y - 70]), K(9.6, [CX, AX_Y - 70]), K(10.4, list(wpos))),
                          scale=A(K(0, [S2 * 100] * 2), K(a1, [S3 * 100] * 2))))
    s = S4 / S3
    Q = (SEED4[0] - wpos[0] * s, SEED4[1] - wpos[1] * s)
    P, sc = handoff(Q, s)
    L.append(rig(rg, D, [(0, (0, 0), 1), (d0, (0, 0), 1), (D - 0.4, P, sc)]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 4 - THE PULPER (16 s)
# =====================================================================
WL = 380


def s4_pulper(D):
    L = []
    b0, f0 = 6.0, 11.0
    seed_s = S4 * S3 * 100
    L.append(seed_unit("Seed", list(SEED4), 0, D, muc=A(K(0.2, [0, 0]), K(0.9, [100, 100])), scale=[seed_s, seed_s],
                       position=A(K(0, list(SEED4)), K(b0, list(SEED4)), K(f0, list(SEED4)), K(f0 + 1.2, inv((CX, WL))), K(D, inv((CX, WL + 30))))))
    L.append(shape("Stream", [G("S", *[path([(x, -300), (x + 10, 0)]) for x in (-30, 0, 30)], trim(0, A(K(b0, 0), K(b0 + 0.6, 100))), stroke(WATER, 6))],
                   [SEED4[0], SEED4[1] - 50], b0, f0))
    L.append(tag("Alone", "WATER ALONE WON'T SHIFT IT", [CX + 280, SEED4[1]], b0 + 1.2, f0, just="left"))
    L.append(shape("Water Line", [G("W", path([(CX - 400, 0), (CX + 400, 0)]), trim(A(K(f0, 50), K(f0 + 0.6, 0)), A(K(f0, 50), K(f0 + 0.6, 100))), stroke(WATER, 5 / HS))],
                   [0, inv((0, WL))[1]], f0, D, scale=[100 / HS, 100], anchorPoint=[CX, 0], position=[CX, inv((0, WL))[1]]))
    # the pulper, side view
    drum = (CX, 330)
    pul = [shape("Drum", [G("Spokes", path([(-60, 0), (60, 0)]), path([(0, -60), (0, 60)]), stroke(INK, 3), tr={"rotation": X("time * 120")}),
                          G("D", ell([200, 200]), stroke(INK, 5), fill(WHITE))], list(drum), 0.2, f0, scale=grow(0.2)),
           shape("Hopper", [G("H", path([(-160, -220), (-50, -100), (50, -100), (160, -220)]), stroke(INK, 5))], list(drum), 0.4, f0),
           shape("Chute", [G("C", path([(-40, 100), (-40, 240)]), path([(40, 100), (40, 240)]), stroke(INK, 5))], list(drum), 0.5, f0),
           shape("Spout", [G("S", path([(100, 20), (300, 120)]), stroke(INK, 5))], list(drum), 0.6, f0)]
    for k in range(4):
        t = 1.0 + k * 1.1
        L.append(disc(f"Cherry In {k + 1}", A(K(t, [drum[0] - 150 + k * 20, -40]), K(t + 0.8, [drum[0], drum[1] - 120])), 50, ARA, t, t + 0.8, sh=0))
        L.append(shape(f"Skin Out {k + 1}", [G("S", path([(-20, 0), (0, -14), (20, 0)], False, i=[(0, 0), (-10, 0), (0, 0)], o=[(0, 0), (10, 0), (0, 0)]), stroke(ARA, 8))],
                       A(K(t + 0.9, [drum[0] + 300, drum[1] + 120]), K(t + 2.0, [drum[0] + 420, 1150])), t + 0.9, t + 2.0))
        if k < 3:
            L.append(seed_unit(f"Seed Out {k + 1}", [drum[0], drum[1] + 240], t + 0.9, t + 1.8, scale=[seed_s * 0.7] * 2,
                               position=A(K(t + 0.9, [drum[0] + 10, drum[1] + 240]), K(t + 1.8, [drum[0] - 260 - k * 70, 1150]))))
    L.append(tag("Pulper", "PULPER", [drum[0] - 180, drum[1] + 10], 0.8, f0, just="right"))
    L += pul
    for l in L:
        if l["out"] > f0 and l["name"] not in ("Seed", "Water Line"):
            add_out(l, f0)
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 5 - THE TANK (31 s)
# =====================================================================
TANK = (CX, 560, 800, 420)
BACT = (520, 500)
PH = (1560, 560)


def ph_angle(ph):
    return -90 + (7 - ph) / 4 * 180


def gauge(prefix, pos, t0, t1, needle, marks=True, **tr):
    ticks = []
    for ph in range(3, 8):
        a = math.radians(ph_angle(ph) - 90)
        ticks.append(path([(100 * math.cos(a), 100 * math.sin(a)), (120 * math.cos(a), 120 * math.sin(a))]))
    out = [shape(f"{prefix}Needle", [G("N", path([(0, 0), (0, -110)]), stroke(MAG, 6), tr={"rotation": needle}), G("Hub", ell([18, 18]), fill(INK))], pos, t0, t1, **tr),
           shape(f"{prefix}Dial", [G("T", *ticks, stroke(INK, 3)),
                                   G("Arc", path([(-130, 0), (130, 0)], False, i=[(0, 0), (0, -180)], o=[(0, -180), (0, 0)]), stroke(INK, 4))], pos, t0, t1, **tr),
           caps(f"{prefix}pH Label", "pH", [pos[0], pos[1] + 40], t0, t1, size=16, color=INK)]
    for ph in (7, 5, 3):
        a = math.radians(ph_angle(ph) - 90)
        out.append(caps(f"{prefix}pH {ph}", str(ph), [pos[0] + 150 * math.cos(a), pos[1] + 150 * math.sin(a) + 6], t0, t1, size=13, color=INK))
    if marks:
        for nm, ph in (("MILK 6.7", 6.7), ("TOMATO JUICE 4.2", 4.2)):
            a = math.radians(ph_angle(ph) - 90)
            out.append(caps(f"{prefix}{nm}", nm, [pos[0] + 190 * math.cos(a), pos[1] + 190 * math.sin(a)], t0 + 0.6, t1, size=12, color=INK))
    return out


def hand(name, pos, t0, t1, closed=False):
    if closed:
        items = [G("Knuckles", *[path([(-60 + k * 40, -40), (-60 + k * 40, 0)]) for k in range(4)], stroke(INK, 3)),
                 G("Fist", rect([200, 150], None, 50), stroke(INK, 4), fill(LAND))]
    else:
        fingers = [rect([36, 130], [-66 + k * 44, -120], 18) for k in range(4)]
        items = [G("Hand", rect([200, 170], [0, 0], 40), *fingers, rect([110, 36], [-140, 10], 18), stroke(INK, 4), fill(LAND))]
    return shape(name, items, pos, t0, t1)


def s5_tank(D):
    L = []
    x, y, w, h = TANK
    b0, c0, d0, d1 = 3.0, 14.0, 23.0, 26.5
    rnd = random.Random(5)
    seeds = [(rnd.uniform(x - w / 2 + 50, x + w / 2 - 50), rnd.uniform(y + 20, y + h / 2 - 30)) for _ in range(46)]
    L.append(shape("Water Line", [G("W", path([(x - w / 2, WL), (x + w / 2, WL)]), stroke(WATER, 5))], [0, 0], 0, d0))
    groups = [("Other", 26, lambda p: [ell([10, 10], p)], [stroke(INK, 2), fill(WHITE)], b0, "OTHER BACTERIA (FIRST, MOST NUMEROUS)"),
              ("Yeasts", 14, lambda p: [ell([16, 16], p)], [fill(MAG)], b0 + 3.0, "YEASTS"),
              ("Lactic", 14, lambda p: [rect([24, 9], p, 4)], [fill(MAG)], b0 + 5.6, "LACTIC ACID BACTERIA")]
    for k, (nm, n, fn, st, t, lab) in enumerate(groups):
        gs = []
        for j in range(n):
            sx, sy = rnd.choice(seeds)
            p = [sx + rnd.uniform(-20, 20), sy + rnd.uniform(-14, 14)]
            gs.append(G(f"{nm}{j}", *fn(p), *st, tr={"opacity": A(K(t + j * 0.08, 0), K(t + j * 0.08 + 0.1, 100))}))
        L.append(shape(f"Microbes {nm}", gs, [0, 0], t, d0))
        L.append(caps(f"{nm} Label", lab, [x - w / 2 + 20, y + h / 2 + 40 + k * 28], t, d0, size=13, color=MAG if k else INK, just="left"))
    L.append(shape("Yoghurt", [G("Y", path([(-16, -20), (16, -20), (12, 18), (-12, 18)], True), stroke(INK, 3), fill(WHITE))],
                   [x - w / 2 + 380, y + h / 2 + 90], b0 + 6.0, d0, scale=grow(b0 + 6.0)))
    pile = [G(f"S{j}", ell([40, 28], list(p)), stroke(SEED_LINE, 2), fill(SEED), tr={"rotation": rnd.uniform(-40, 40)}) for j, p in enumerate(seeds)]
    for g, p in zip(pile, seeds):
        g["transform"].update({"anchorPoint": list(p), "position": list(p)})
    L.append(shape("Pile", pile, [0, 0], 0, d0))
    L.append(shape("Tank", [G("T", path([(x - w / 2, y - h / 2), (x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w / 2, y - h / 2)]), stroke(INK, 5))], [0, 0], 0, d0))
    L.append(shape("Clock", [G("Hand", path([(0, 0), (0, -26)]), stroke(INK, 4), tr={"rotation": X(f"Math.min(time, {d0}) / {d0} * 600")}),
                             G("Face", ell([70, 70]), stroke(INK, 4), fill(WHITE))], [x + w / 2 - 40, 240], 0.4, d0))
    L.append(caps("Clock Label", "0 → 20 HOURS", [x + w / 2 + 10, 250], 0.6, d0, size=13, color=INK, just="left"))
    meter = [shape("Meter", [G("M", rect([30, 300], [0, -150]), fill(SEED_LINE), tr={"anchorPoint": [0, 0], "position": [0, 0],
                                                                                     "scale": A(K(b0 + 6.0, [100, 100]), K(b0 + 10.0, [100, 40]))}),
                             G("O", rect([30, 300], [0, -150]), stroke(INK, 3))], [x - w / 2 - 70, y + h / 2], 1.0, d0),
             caps("Meter Label", "SUGAR", [x - w / 2 - 70, y + h / 2 + 34], 1.0, d0, size=13, color=INK),
             tag("Eaten", "≈ 60 % OF THE SIMPLE SUGARS EATEN, ALL MICROBES TOGETHER", [CX, 150], b0 + 9.0, c0)]
    L += meter
    dim(meter[:2], c0, 28)
    L.append(src("Src Microbes", "SOURCE: AVALLONE ET AL. 2001", b0, c0))
    ndl = A(K(c0 + 0.4, ph_angle(5)), K(c0 + 4.0, ph_angle(4.05)))
    L += gauge("", list(PH), c0, d0, ndl, scale=grow(c0))
    L.append(src("Src pH", "SOURCE: AVALLONE ET AL. 2002; FDA pH TABLE", c0, d0))
    for l in L:
        if l["out"] > d0:
            add_out(l, d0)
    # D: the hand test, two silhouettes on a cut
    L.append(hand("Open Hand", [CX, 620], d0, d1))
    L.append(shape("Slide", [G(f"S{j}", ell([40, 28], [-60 + j * 40, 0]), stroke(SEED_LINE, 2), fill(SEED)) for j in range(4)],
                   A(K(d0 + 0.2, [CX, 520]), K(d1, [CX, 1200])), d0, d1))
    L.append(tag("Slick", "SLICK · 6 HOURS", [CX, 880], d0 + 0.3, d1, size=18))
    L.append(hand("Closed Hand", [CX, 620], d1, D))
    L.append(shape("Held", [G(f"S{j}", ell([40, 28], [-60 + j * 40, -90]), stroke(SEED_LINE, 2), fill(SEED)) for j in range(4)], [CX, 620], d1, D))
    L.append(tag("Gritty", "GRITTY · 20 HOURS", [CX, 880], d1 + 0.3, D - 1.6, size=18))
    L.insert(0, disc("Bacterium", A(K(d1, [CX - 20, 530]), K(D - 1.6, [CX - 20, 530]), K(D - 0.3, inv(BACT))), 12, MAG, d1 + 0.2, D, sh=0,
                     scale=A(K(D - 1.6, [100, 100]), K(D - 0.3, [160 / 12 / HS * 100] * 2))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 6 - WHAT THE TANK REALLY DOES (41 s, the turn)
# =====================================================================
CH_Y = 620


def s6_acid(D):
    L = []
    b0, c0, d0 = 9.0, 20.0, 36.0
    pg = doc("Paper", [("Avallone, Guiraud, Guyot,", 20, BODY), ("Olguín & Brillouet", 20, BODY), ("J. Agric. Food Chem., 2001", 18, SCI)],
             (1250, 420), (620, 280), 0.6, b0, hl_line=None, credit=None)
    L += pg
    L.append(disc("Coatepec Dot", [1000, 700], 22, MX, 1.4, b0, sh=0, scale=grow(1.4)))
    L.append(tag("Coatepec Tag", "COATEPEC, VERACRUZ · 1998 HARVEST", [1030, 706], 1.6, b0, just="left"))
    L.append(text("Bact Name", "Leuconostoc mesenteroides", [BACT[0], BACT[1] + 140], 32, INK, 0.4, c0, font=SCI))
    # B: pectin before / after
    x0 = 1100
    for k, (nm, hgt) in enumerate((("BEFORE", 320), ("AFTER 20 H", 300))):
        t = b0 + 0.6 + k * 0.8
        L.append(shape(f"Pectin {nm}", [G("B", rect([140, hgt], [0, -hgt / 2]), fill(SEED_LINE))], [x0 + k * 260, 760], t, c0,
                       scale=A(K(t, [100, 0]), K(t + 0.5, [100, 100]))))
        L.append(caps(f"Pectin {nm} Label", nm, [x0 + k * 260, 800], t, c0, size=14, color=INK))
    L.append(caps("Pectin Title", "PECTIN IN THE MUCILAGE", [x0 + 130, 380], b0 + 0.4, c0, size=16, color=INK))
    L.append(tag("Barely", "BARELY TOUCHED", [x0 + 130, 860], b0 + 2.4, c0, size=20))
    sc = [G("X", path([(-50, -50), (50, 50)]), path([(50, -50), (-50, 50)]), stroke(MAG, 6), tr={"opacity": A(K(b0 + 4.6, 0), K(b0 + 4.7, 100))}),
          G("Blades", path([(-30, 30), (30, -40)]), path([(30, 30), (-30, -40)]), ell([24, 24], [-34, 38]), ell([24, 24], [34, 38]), stroke(INK, 4))]
    L.append(shape("Scissors", sc, [BACT[0] + 170, BACT[1] - 120], b0 + 3.8, c0, scale=grow(b0 + 3.8)))
    L.append(tag("No Enzyme", "MADE NO PECTIN-CUTTING ENZYME", [BACT[0], BACT[1] + 190], b0 + 4.8, c0, size=15))
    L.append(src("Src Pectin", "SOURCE: AVALLONE ET AL. 2001", b0, c0))
    for l in L:
        add_out(l, min(l["out"], c0))
    # C: needle and ring on one clock
    gp, sp = (760, 560), (1300, 540)
    ndl = A(K(c0 + 1.0, ph_angle(5)), K(c0 + 8.0, ph_angle(4.05)))
    L += gauge("Tank ", list(gp), c0, d0, ndl, marks=False, scale=grow(c0))
    L.append(seed_unit("Loose Seed", list(sp), c0, d0, muc=A(K(c0 + 1.0, [100, 100]), K(c0 + 8.0, [128, 128])), scale=[220, 220]))
    L.append(leader("Acid", (sp[0] + 150, sp[1] - 120), (1640, 300), c0 + 5.0, d0, col=MAG))
    L.append(caps("Acid Label", "ACID?", [1650, 290], c0 + 5.2, d0, size=16, color=MAG, just="left"))
    L.append(leader("Osmosis", (sp[0] + 150, sp[1] + 120), (1640, 760), c0 + 6.0, d0))
    L.append(caps("Osmosis Label", "WATER DRAWN OUT AS", [1650, 760], c0 + 6.2, d0, size=14, color=INK, just="left"))
    L.append(caps("Osmosis Label 2", "SUGAR IS EATEN?", [1650, 784], c0 + 6.2, d0, size=14, color=INK, just="left"))
    L.append(tag("Unknown", "EXACT MECHANISM: UNKNOWN", [sp[0], 900], c0 + 8.6, d0, size=14))
    L.append(src("Src Mech", "SOURCE: AVALLONE ET AL. 2002", c0, d0))
    for l in L:
        if l["out"] > d0:
            add_out(l, d0)
    # the bacterium: grows from the S5 dot, then drops into the washing channel (6->7 handoff)
    L.insert(0, disc("Bacterium", A(K(c0 - 0.8, list(BACT)), K(c0, [240, 200]), K(d0, [240, 200]), K(D - 0.3, inv((300, CH_Y)))), 160, MAG, 0, D, sh=0,
                     scale=A(K(c0 - 0.8, [100, 100]), K(c0, [40, 40]), K(d0, [40, 40]), K(D - 0.3, [20 / 160 / HS * 100] * 2))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 7 - WASHING AND DRYING (22 s)
# =====================================================================
COA8 = (720, 400)


def s7_dry(D):
    L = []
    b0, c0, d0 = 6.0, 12.0, 19.6
    L.append(disc("Drop", A(K(0, [300, CH_Y]), K(0.6, [300, CH_Y]), K(1.4, [900, CH_Y])), 20, A(K(0.1, MAG), K(0.2, WATER)), 0, 1.6, sh=0))
    L.append(shape("Channel", [G("C", path([(-100, CH_Y - 60), (2020, CH_Y - 60)]), path([(-100, CH_Y + 60), (2020, CH_Y + 60)]), stroke(INK, 4)),
                               G("W", path([(-100, CH_Y), (2020, CH_Y)]), stroke(WATER, 5))], [0, 0], 0, b0))
    for k in range(6):
        t = 0.4 + k * 0.6
        L.append(seed_unit(f"Tumble {k + 1}", [0, CH_Y], t, t + 3.0, muc=None, scale=[50, 50],
                           position=A(KL(t, [-80, CH_Y + 20]), KL(t + 3.0, [2000, CH_Y + 20])), rotation=A(KL(t, 0), KL(t + 3.0, 720))))
    # B: patio and bed
    L.append(shape("Patio", [G("P", path([(120, 820), (900, 820)]), stroke(GREY2, 5))], [0, 0], b0, c0))
    L.append(shape("Patio Seeds", [G(f"S{j}", ell([24, 16], [160 + j * 36, 808]), fill(SEED)) for j in range(20)], [0, 0], b0 + 0.2, c0))
    L.append(shape("Rake", [G("R", path([(0, 0), (0, -260)]), path([(-60, 0), (60, 0)]), *[path([(x, 0), (x, 16)]) for x in (-60, -30, 0, 30, 60)], stroke(INK, 4))],
                   A(K(b0 + 0.6, [200, 790]), K(c0 - 0.6, [820, 790])), b0 + 0.4, c0))
    L.append(caps("Patio Label", "PATIO", [510, 880], b0 + 0.2, c0, size=15, color=INK))
    L.append(shape("Split", [G("S", path([(CX, 300), (CX, 900)]), stroke(INK, 3))], [0, 0], b0, c0))
    L.append(shape("Bed", [G("Mesh", *[path([(1080 + j * 40, 700), (1080 + j * 40, 720)]) for j in range(18)], stroke(GREY, 2)),
                           G("B", rect([720, 20], [1440, 710]), path([(1100, 720), (1100, 840)]), path([(1780, 720), (1780, 840)]), stroke(INK, 4))], [0, 0], b0, c0))
    L.append(shape("Bed Seeds", [G(f"S{j}", ell([24, 16], [1110 + j * 36, 690]), fill(SEED)) for j in range(19)], [0, 0], b0 + 0.2, c0))
    for k in range(4):
        L.append(arrow(f"Air {k + 1}", (1200 + k * 160, 830), (1200 + k * 160, 740), b0 + 0.8 + k * 0.2, c0, col=GREY))
    L.append(caps("Bed Label", "RAISED BED", [1440, 880], b0 + 0.2, c0, size=15, color=INK))
    for l in L:
        add_out(l, min(l["out"], c0))
    # C: the scale
    pan = (CX, 560)
    L.append(shape("Scale", [G("Pan", path([(-180, 0), (180, 0)]), stroke(INK, 6)), G("Body", rect([300, 160], [0, 110], 14), stroke(INK, 4), fill(WHITE)),
                             G("Display", rect([180, 60], [0, 110], 6), stroke(INK, 3))], list(pan), c0, d0))
    vals = [100, 90, 80, 70, 62, 56]
    for k, v in enumerate(vals):
        t = c0 + 0.6 + k * 0.9
        L.append(text(f"Grams {v}", f"{v} g", [pan[0], pan[1] + 124], 34, INK, t, t + 0.9 if k < len(vals) - 1 else d0, font=HEAD))
        L.append(caps(f"Day {k + 1}", f"DAY {1 + k * 2}", [pan[0] + 300, pan[1] + 120], t, t + 0.9 if k < len(vals) - 1 else d0, size=15, color=INK, just="left"))
    L.append(L.pop(len(L) - 2 * len(vals) - 1))
    L.append(tag("Water Pct", "≈ 50 % WATER → 10–12 %", [CX, 260], c0 + 1.0, d0, size=20))
    L.append(src("Src SCA", "SOURCE: SCA GREEN COFFEE STANDARD", c0, d0))
    L.append(shape("Pan Pile", [G(f"S{j}", ell([30, 20], [-60 + j * 30, -12]), stroke(SEED_LINE, 2), fill(SEED)) for j in range(5)], list(pan), c0 + 0.4, d0))
    for l in L:
        if l["out"] > d0:
            add_out(l, d0)
    L.insert(0, seed_unit("Last Seed", [pan[0], pan[1] - 40], c0 + 0.4, D, muc=None, scale=[40, 40],
                          position=A(K(d0, [pan[0], pan[1] - 40]), K(D - 0.3, inv(COA8))), ))
    L[0]["transform"]["scale"] = A(K(d0, [40, 40]), K(D - 0.3, [22 / LAYERS["parch"][0] / HS * 100] * 2))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 8 - THE PRICE IN WATER (35 s)
# =====================================================================
K8 = 70


def bottle(k, x, y, part=1.0):
    p = path([(-8, -26), (-8, -20), (-14, -12), (-14, 24), (14, 24), (14, -12), (8, -20), (8, -26)], True)
    items = [p, stroke(INK, 2)]
    if part < 1:
        return G(f"Bottle {k}", p, stroke(INK, 2), tr={"position": [x, y], "scale": [part * 100, 100]})
    return G(f"Bottle {k}", *items, tr={"position": [x, y]})


def s8_water(D):
    L = []
    a1, b0, c0 = 3.0, 17.0, 26.0
    s8 = lambda ll: screen(ll, K8, COATEPEC, COA8)
    st = [path([s8(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    mp = shape("Map", [G("Borders", *st, stroke(WHITE, 3)), G("States", *st, fill(LAND))], [0, 0], 0.2, c0 + 4.0, scale=grow(0.2, 100, 0.8),
               anchorPoint=list(COA8), position=list(COA8))
    dim([mp], 7.0, 28)
    L.append(disc("Coatepec", list(COA8), 22, MX, 0, D - 4.0, sh=0))
    L.append(shape("Mill", [G("M", rect([40, 30], [0, -30]), path([(-26, -45), (0, -64), (26, -45)], True), stroke(INK, 3), fill(WHITE))],
                   [COA8[0] + 40, COA8[1]], 1.0, c0 + 4.0, scale=grow(1.0)))
    L.append(tag("Lavado", "MOST MEXICAN EXPORT GRADES ARE WASHED (LAVADO)", [COA8[0] - 30, COA8[1] + 60], 2.0, b0, size=15, color=MX, just="left"))
    # bottles
    r1 = [bottle(j, 300 + j * 52, 180) for j in range(20)]
    L.append(shape("Bottles Trad", r1, [0, 0], a1 + 4.0, b0, scale=A(K(a1 + 4.0, [0, 100]), K(a1 + 5.0, [100, 100]))))
    L.append(caps("Trad Label", "TRADITIONAL WASHED MILL: UP TO ≈ 20 L PER KG OF CHERRY", [300, 240], a1 + 4.4, b0, size=13, color=INK, just="left"))
    r2 = [bottle(j, 300 + j * 52, 300) for j in range(3)] + [bottle(3, 300 + 3 * 52 - 8, 300, 0.4)]
    L.append(shape("Bottles Machine", r2, [0, 0], a1 + 6.0, b0, scale=A(K(a1 + 6.0, [0, 100]), K(a1 + 6.6, [100, 100]))))
    L.append(caps("Machine Label", "MEXICO, MACHINE DEMUCILAGING: ≈ 3.4 L", [520, 306], a1 + 6.4, b0, size=13, color=INK, just="left"))
    L.append(src("Src Litres", "SOURCE: VON ENDEN & CALVERT 2002; BELLO-MENDOZA & CASTILLO-RIVERA 1998", a1 + 4.0, b0))
    # B: the river and the aguas mieles
    river = path([(COA8[0] + 40, COA8[1]), (1000, 520), (1180, 560), (1400, 700)], False, i=[(0, 0), (-80, -40), (-60, -10), (-60, -60)], o=[(80, 40), (60, 10), (60, 60), (0, 0)])
    L.append(shape("River", [G("R", river, trim(0, A(K(b0, 0), K(b0 + 1.2, 100))), stroke(WATER, 8))], [0, 0], b0, c0 + 4.0))
    L.append(shape("Runoff", [G("R", path([(COA8[0] + 50, COA8[1] - 10), (900, 470)], False, i=[(0, 0), (-60, -20)], o=[(60, 0), (0, 0)]),
                                trim(0, A(K(b0 + 1.4, 0), K(b0 + 2.4, 100))), stroke(MAG, 8))], [0, 0], b0 + 1.4, c0 + 4.0))
    L.append(text("Aguas", "aguas mieles", [1040, 440], 34, MAG, b0 + 2.4, c0, font=SCI))
    L.append(tag("Aguas pH", "pH ≈ 4 · TOMATO JUICE 4.2", [1040, 476], b0 + 2.8, c0, size=14, color=INK))
    L.append(src("Src Runoff", "SOURCE: BELLO-MENDOZA ET AL. 1995 (SOCONUSCO MILLS)", b0, c0))
    # C: the machine skips the tank
    L.append(tag("No Tank", "NO TANK, NO FERMENTATION", [COA8[0] + 40, COA8[1] - 100], c0, c0 + 4.0, size=15))
    thumb = (1500, 260)
    L.append(shape("Thumb Line", [G("D", path([(COA8[0] + 220, COA8[1] - 110), (thumb[0] - 180, thumb[1])]), trim(0, A(K(c0 + 0.4, 0), K(c0 + 1.2, 100))),
                                    stroke(INK, 3, dashes=(12, 9)))], [0, 0], c0 + 0.4, c0 + 4.0))
    L.append(shape("Thumb", [G("T", rect([340, 90], None, 4), stroke("#D0D0D0", 2), fill(WHITE))], list(thumb), c0 + 1.0, c0 + 4.0, scale=grow(c0 + 1.0)))
    L.append(text("Thumb Text", "fermentar el café recién despulpado", [thumb[0], thumb[1] + 6], 15, INK, c0 + 1.2, c0 + 4.0, font=BODY))
    L.append(text("Thumb Q", "?", [thumb[0] + 200, thumb[1] + 14], 44, INK, c0 + 1.8, c0 + 4.0, font=HEAD))
    for l in L:
        if l["out"] > c0 + 4.0:
            add_out(l, c0 + 4.0)
    L.append(mp)
    # the river straightens into the clause underline (8->9 handoff)
    ln = shape("Underline", [G("U", path([(-L3W / 2 * ZS, 0), (L3W / 2 * ZS, 0)]), stroke(WATER, 6))], A(K(c0 + 4.0, [1100, 600]), K(D - 0.3, inv((CX, UNDER_Y)))),
               c0 + 4.0, D, scale=A(K(c0 + 4.0, [40, 100]), K(D - 0.3, [100 / HS, 100 / HS])))
    L.insert(0, ln)
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 9 - CLOSE (18 s)
# =====================================================================
def s9_close(D):
    L = []
    rg = "Page Rig"
    L.append(shape("Underline", [G("U", path([(-L3W / 2 * ZS, 0), (L3W / 2 * ZS, 0)]), stroke(WATER, 6))], [CX, UNDER_Y], 0, D))
    L.append(text("Note", "= the water sours and the slime lets go", [CX, ZP[1] + (CL_Y[0] - 40) * ZS], 40, MAG, 2.0, D, font=SCI))
    L[-1]["transform"]["opacity"] = fade_in(2.0)
    L += wipe_text("End Title", "Why Veracruz Lets Its Coffee Go Sour", [CX, 1000], 56, INK, 9.0, D)
    L.append(word_marker("End Swipe", "Why Veracruz Lets Its Coffee Go Sour", "Sour", CX, 1000, 56, 9.8, D))
    L += page(0, D, rg, swipes_t=(0, 0))
    L.append(rig(rg, D, [(0, ZP, ZS)]))
    L.append(bg(D))
    return L


SCENES = [("S1_Declaration", 23.0, s1_law), ("S2_Layers", 29.0, s2_layers), ("S3_FruitAxis", 34.0, s3_axis), ("S4_Pulper", 16.0, s4_pulper),
          ("S5_Tank", 31.0, s5_tank), ("S6_Acid", 41.0, s6_acid), ("S7_Dry", 22.0, s7_dry), ("S8_Water", 35.0, s8_water), ("S9_Close", 18.0, s9_close)]

if __name__ == "__main__":
    write(SCENES, "Go_Sour", "05_processing")
