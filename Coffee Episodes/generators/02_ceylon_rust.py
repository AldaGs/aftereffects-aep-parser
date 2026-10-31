"""Generator for episode 2, "The Fungus That Turned Ceylon Into a Tea Country" (scripts/02_ceylon_rust_script.md).

    python "Coffee Episodes/generators/02_ceylon_rust.py"        # writes ../json/02_ceylon_rust.json
    go run ./cmd/json2jsx -i "Coffee Episodes/json/02_ceylon_rust.json" -o "Coffee Episodes/jsx/02_ceylon_rust.jsx" -aep "<abs>/Coffee Episodes/aep/02_ceylon_rust.aep"

Reuses episode 1's helpers, palette and maps by importing schema/examples/coffee_families.py.
White page, flat shapes, match cuts only. A handoff is a screen point/size H: the outgoing scene ends its shape
at inv(H) with size/HS (the master pushes every scene in by HS); the incoming scene starts it at H.
"""
import math, random

from coffee_common import *  # noqa: F401,F403


# =====================================================================
# SCENE 1 - THE TIN (20 s)  and the bookend layout reused by S11
# =====================================================================
TIN, SEAL, SEAL_D = (720, 580), (720, 640), 130
SPOT, SPOT_D = (1290, 736), 40
CLEAF, CLEAF_L, CLEAF_R = (1250, 744), 220, -8
TABLE_Y = 780


def tin_layers(D, t, lid_open_t=None, rig=None, prefix="", lid_open=False):
    """Tin, lid, table line, spilled tea. Returns layers top -> bottom."""
    L = []
    rnd = random.Random(3)
    lid_closed, lid_down = [TIN[0], 352], [440, TABLE_Y - 14]
    leaves = []
    for j in range(22):
        tx, ty = rnd.uniform(900, 1140), TABLE_Y - rnd.uniform(4, 10)
        g = G(f"Tea {j + 1}", ell([18, 7]), fill(TEALEAF), tr={"rotation": rnd.uniform(-60, 60)})
        if lid_open_t is not None:
            tt = lid_open_t + 1.6 + j * 0.05
            g["transform"]["position"] = A(K(tt, [TIN[0] + 60, 390]), K(tt + 0.6, [tx, ty]))
            g["transform"]["opacity"] = fade_in(tt, 0.1)
        else:
            g["transform"]["position"] = [tx, ty]
        leaves.append(g)
    L.append(shape(f"{prefix}Tea Leaves", leaves, [0, 0], t, D, parent=rig))
    if lid_open_t is not None:
        lp = A(K(lid_open_t, lid_closed), K(lid_open_t + 0.5, [TIN[0], 250]), K(lid_open_t + 1.2, lid_down))
    else:
        lp = lid_down if lid_open else lid_closed
    L.append(shape(f"{prefix}Lid", [G("Lid", rect([340, 56], None, 8), stroke(INK, 4), fill(WHITE))], lp, t, D, parent=rig))
    L.append(text(f"{prefix}Tin Name", "CEYLON", [TIN[0], 470], 50, INK, t, D, font=HEAD, parent=rig))
    L.append(caps(f"{prefix}Tin Sub", "PURE TEA", [TIN[0], 512], t, D, size=18, color=INK, parent=rig))
    L.append(shape(f"{prefix}Tin", [G("Body", rect([320, 400], None, 10), stroke(INK, 4), fill(WHITE))], list(TIN), t, D, parent=rig))
    L.append(shape(f"{prefix}Table", [G("Line", path([(300, TABLE_Y), (1700, TABLE_Y)]), stroke(LINE, 3))], [0, 0], t, D))
    return L


def s1_tin(D):
    L = []
    rig = "Tin Rig"
    push = (15.4, 19.0)
    # Mexico: second half of the question
    k = 3.2
    mx_items = [path([[(p[0] + 102) * k, -(p[1] - 23.5) * k] for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    mex = [shape("Mexico", [G("Mexico", *mx_items, fill(MX))], [1500, 340], 9.6, 15.2, opacity=fade_io(9.6, 15.2, 0.4)),
           shape("Mexico Leaf", icon_leaf(MX, 90), [1700, 400], 10.0, 15.2, rotation=-30, opacity=fade_io(10.0, 15.2, 0.4)),
           caps("Mexico Label", "MEXICO · STILL GROWS COFFEE", [1560, 470], 10.2, 15.2, size=18, color=MX, opacity=fade_io(10.2, 15.2, 0.4))]
    L += mex
    # the coffee leaf with its rust spot (last thing out of the tin)
    spot = disc("Rust Spot", list(SPOT), SPOT_D, RUST, 8.3, 15.2, sh=0, scale=grow(8.3, 100, 0.5), opacity=A(K(14.6, 100), K(15.2, 0)))
    leaf = grey_leaf("Coffee Leaf", CLEAF_L, A(K(7.3, [TIN[0] + 60, 400]), K(8.1, list(CLEAF))), 7.3, 15.2, rotation=CLEAF_R,
                     opacity=A(K(7.3, 0), K(7.5, 100), K(14.6, 100), K(15.2, 0)))
    L += [spot, leaf]
    L.append(caps("Label Ceylon", "CEYLON = SRI LANKA", [TIN[0], 300], 1.8, 6.2, size=18, color=INK, opacity=fade_io(1.8, 6.2)))
    # the seal survives the push-in; everything else on the tin fades
    seal = disc("Seal", list(SEAL), SEAL_D, TEA, 0.6, D, sh=0, parent=rig, scale=grow(0.6, 100, 0.5))
    tin = tin_layers(D, 0, lid_open_t=3.4, rig=rig)
    for l in tin:
        add_out(l, push[0] - 0.2, 0.8)
    tin[-2]["transform"]["scale"] = A(K(0, [0, 100]), K(0.9, [100, 100]))  # tin body draws open
    L += [seal] + tin
    s_end = 220 / SEAL_D / HS * 100
    L.append(null(rig, list(SEAL), 0, D, scale=A(K(push[0], [100, 100]), K(push[1], [s_end, s_end])),
                  position=A(K(push[0], list(SEAL)), K(push[1], [CX, CY]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 2 - THE COFFEE ISLAND (23 s)
# =====================================================================
KB, CEY = 90, (80.7, 7.8)
FR1 = 14 / KB
DOT_MAP = 24 / FR1
S2_P2 = (640, 560)
LEAF2, LEAF2_L = (650, 628), 40


def s2_island(D):
    L = []
    rig = "Map Rig"
    t_end = 21.4
    m = lambda ll: map_pt(ll, KB)
    scr = lambda ll: [S2_P2[0] + (ll[0] - CEY[0]) * KB, S2_P2[1] - (ll[1] - CEY[1]) * KB]
    # year and island label
    L.append(appear(text("Year", "1870", [120, 220], 96, INK, 2.6, D, font=HEAD, just="left"), 2.6))
    L.append(appear(caps("Island Label", "CEYLON", [S2_P2[0], 350], 5.6, D, size=22, color=INK), 5.6))
    # B: sacks, Ceylon 1870 against Mexico today (a little under a quarter)
    b0, b1 = 6.0, 11.2
    L += [sacks("Sacks Ceylon", 4, ARA, 1150, 820, b0, b1 + 0.4, ), sacks("Sacks Mexico", 18, MX, 1400, 820, b0 + 0.8, b1 + 0.4)]
    L.append(appear(caps("Sacks Ceylon Label", "CEYLON 1870", [1150, 860], b0, b1 + 0.4, size=16, color=ARA), b0))
    L.append(appear(text("Sacks Ceylon Value", "≈ 118 M lb", [1150, 900], 26, INK, b0 + 0.2, b1 + 0.4, font=HEAD), b0 + 0.2))
    L.append(appear(caps("Sacks Mexico Label", "MEXICO 2025/26", [1400, 860], b0 + 0.8, b1 + 0.4, size=16, color=MX), b0 + 0.8))
    L.append(appear(text("Sacks Mexico Value", "≈ 4.1 M bags", [1400, 900], 26, INK, b0 + 1.0, b1 + 0.4, font=HEAD), b0 + 1.0))
    L.append(src("Src Sacks", "SOURCE: KOEHLER (2017); USDA FAS MX2026-0026", b0, b1 + 0.4))
    for l in L[-7:]:
        add_out(l, b1)
    # C: Chiapas over the island, same scale
    c0, c1 = 11.6, 15.0
    rings = GEO["mexico"]["Chiapas"]
    cc = state_centroid("Chiapas")
    sl_c = (80.7, 7.65)
    chi = [path([m((p[0] - cc[0] + sl_c[0], p[1] - cc[1] + sl_c[1])) for p in r], True) for r in rings]
    L.append(shape("Chiapas Outline", [G("Chiapas", *chi, trim(0, A(K(c0, 0), K(c0 + 1.0, 100))), stroke(MX, 4))], [0, 0], c0, c1 + 0.4,
                   parent=rig, opacity=A(K(c1, 100), K(c1 + 0.4, 0))))
    L.append(appear(text("Area SL", "Sri Lanka  65,600 km²", [1000, 500], 34, INK, c0 + 0.4, c1, font=HEAD, just="left"), c0 + 0.4))
    L.append(appear(text("Area Chiapas", "Chiapas  73,300 km²", [1000, 560], 34, MX, c0 + 1.0, c1, font=HEAD, just="left"), c0 + 1.0))
    L.append(src("Src Area", "SOURCE: INEGI; DEPT. OF CENSUS AND STATISTICS, SRI LANKA", c0 + 0.4, c1))
    for l in L[-3:]:
        add_out(l, c1 - 0.3)
    # D: cinnamon, before coffee
    d0, d1 = 15.3, 18.2
    st = (79.95, 6.9)
    L.append(shape("Cinnamon", [G("Stick", rect([64, 12], None, 6), fill(CIN))], m(st), d0, d1 + 0.4, parent=rig, rotation=58,
                   scale=grow(d0, 100, 0.4), opacity=A(K(d1, 100), K(d1 + 0.4, 0))))
    sp = scr(st)
    L.append(leader("Cinnamon Leader", (sp[0] - 8, sp[1] + 14), (520, 744), d0 + 0.3, d1))
    L.append(appear(caps("Cinnamon Label", "CINNAMON, BEFORE COFFEE", [500, 770], d0 + 0.5, d1, size=18, color=TEA, just="right"), d0 + 0.5))
    L.append(src("Src Cinnamon", "SOURCE: DE SILVA, A HISTORY OF SRI LANKA", d0 + 0.5, d1))
    for l in L[-3:]:
        add_out(l, d1 - 0.3)
    # E: the highlands fill with estate blocks
    gs = []
    rnd = random.Random(5)
    lon = 80.45
    while lon < 81.12:
        lat = 6.62
        while lat < 7.52:
            tt = 18.4 + (lat - 6.62) / 0.9 * 1.4 + rnd.uniform(0, 0.4)
            gs.append(G(f"E{len(gs) + 1}", ell([5, 5]), fill(ARA), tr={"position": m((lon, lat)), "scale": grow(tt, 100, 0.2)}))
            lat += 0.07
        lon += 0.07
    L.append(shape("Estates", gs, [0, 0], 18.4, D, parent=rig))
    L.append(grey_leaf("Leaf Icon", LEAF2_L, list(inv(LEAF2)), 20.0, D, rotation=-25,
                       scale=A(K(20.0, [0, 0]), K(20.4, [100 / HS, 100 / HS]))))
    # the dot that came out of the seal; tea green turns red as the coffee years begin
    L.append(disc("Ceylon Dot", m(CEY), DOT_MAP, A(K(2.4, TEA), K(3.0, ARA)), 0, D, sh=0, parent=rig,
                  scale=A(K(3.6, [100, 100]), K(5.5, [24 / DOT_MAP * 100] * 2)), opacity=A(K(18.0, 100), K(18.5, 0))))
    L.append(land_layer("Land", KB, 0, D, bbox=(40, -10, 110, 35), parent=rig, opacity=fade_in(0.4, 1.4)))
    L.append(null(rig, [CX, CY], 0, D, anchor=m(CEY), scale=zmulti(220 / DOT_MAP, [(0.3, 2.6, FR1), (3.6, 5.6, 1.0)]),
                  position=pmulti((CX, CY), [(3.6, 5.6, S2_P2)])))
    fade_all(L, t_end, 0.6, keep={"Leaf Icon"})
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 3 - HOW ONE SPORE KILLS A LEAF (44 s)
# =====================================================================
BAND_C, BAND_W, BAND_H = (CX, 480), 1200, 320
BOT = BAND_C[1] + BAND_H / 2
STOMA1, STOMA2 = 820, 1240
SPORE3 = (1500, 540)


def s3_spore(D):
    L = []
    steps = [("LAND IN WATER", 4.0), ("ENTER", 14.5), ("FEED", 19.5), ("BREAK OUT", 28.5)]
    t_off = 37.0
    sec = []
    # rail
    xs = [520, 820, 1120, 1420]
    for j, ((lab, t), x) in enumerate(zip(steps, xs)):
        sec.append(caps(f"Step {j + 1} Label", f"{j + 1}  {lab}", [x, 930], 1.0, D, size=17, color=INK,
                        opacity=A(K(1.0, 0), K(1.4, 35), K(t, 35), K(t + 0.3, 100))))
        sec.append(disc(f"Step {j + 1} Dot", [x, 890], 16, A(K(t, GREY2), K(t + 0.3, RUST)), 1.0, D, sh=0, opacity=fade_in(1.0)))
    sec.append(shape("Rail", [G("Rail", path([(xs[0], 890), (xs[-1], 890)]), trim(0, A(K(1.0, 0), K(1.8, 100))), stroke(LINE, 3))], [0, 0], 1.0, D))
    sec += wipe_text("Sci", "Hemileia vastatrix", [BAND_C[0] - BAND_W / 2, 240], 44, INK, 1.4, D, font=SCI, just="left")
    sec.append(appear(caps("Sci Tag", "COFFEE LEAF RUST · LEAF CROSS-SECTION", [BAND_C[0] - BAND_W / 2, 284], 1.8, D, size=16, just="left"), 1.8))
    # step 1: spore lands under the leaf, in a film of water
    sx, sy = STOMA1 - 46, BOT + 12
    sec.append(shape("Spore", [G("Spore", ell([18, 12]), fill(RUST))], A(K(4.2, [sx, 860]), K(5.0, [sx, sy])), 4.2, D, rotation=-20))
    sec.append(shape("Water", [G("Film", ell([84, 34]), fill(WATER, 45))], [sx, sy + 2], 6.4, D, scale=grow(6.4, 100, 0.6),
                     opacity=A(K(6.4, 100), K(19.0, 100), K(19.6, 0))))
    sec.append(shape("Hair", [G("Hair", ell([54, 54]), stroke(GREY, 2))], [sx - 150, sy + 60], 5.4, 13.8, scale=grow(5.4), opacity=fade_io(5.4, 13.8)))
    sec.append(caps("Hair Label", "A HAIR, END ON", [sx - 150, sy + 120], 5.6, 13.8, size=14, opacity=fade_io(5.6, 13.8)))
    sec.append(caps("Wet Label", "24–48 H WET", [sx + 110, sy + 70], 7.4, 13.8, size=16, color=WATER, opacity=fade_io(7.4, 13.8)))
    # step 2: a thread into the stoma
    sec.append(shape("Thread", [G("Thread", path([(sx + 6, sy - 4), (STOMA1, BOT + 2), (STOMA1, BOT - 60)], False),
                                  trim(0, A(K(14.8, 0), K(16.4, 100))), stroke(RUST, 4))], [0, 0], 14.8, D))
    # step 3: hyphae between the cells
    rnd = random.Random(9)
    hy = []
    for j in range(9):
        a = (STOMA1, BOT - 60)
        b = (STOMA1 + rnd.uniform(-260, 380), rnd.uniform(BAND_C[1] - 40, BOT - 30))
        t = 19.8 + j * 0.5
        hy.append(G(f"H{j + 1}", arc(a, b, rnd.uniform(-0.25, 0.25)), trim(0, A(K(t, 0), K(t + 1.6, 100))), stroke(RUST, 3)))
    hy.append(G("To Pustule", arc((STOMA1, BOT - 60), (STOMA2, BOT - 20), 0.12), trim(0, A(K(28.6, 0), K(29.6, 100))), stroke(RUST, 3)))
    sec.append(shape("Hyphae", hy, [0, 0], 19.8, D))
    sec.append(caps("Days", "≈ 14 DAYS INSIDE", [STOMA1 + 60, BAND_C[1] - 200 + 20], 21.0, 28.2, size=18, color=RUST, just="left",
                    opacity=fade_io(21.0, 28.2)))
    sec.append(caps("Top Clean", "TOP OF THE LEAF: NO SIGN YET", [BAND_C[0] + BAND_W / 2, 284], 23.0, 28.2, size=16, color=INK, just="right",
                    opacity=fade_io(23.0, 28.2)))
    # step 4: pustule and a puff of spores
    sec.append(shape("Pustule", [G("P", ell([70, 34]), fill(RUST))], [STOMA2, BOT + 10], 29.4, D, scale=grow(29.4, 100, 0.7)))
    puff = []
    for j in range(30):
        ang = rnd.uniform(0.2, 1.4)
        r = rnd.uniform(40, 170)
        t = 30.6 + rnd.uniform(0, 1.2)
        tgt = [STOMA2 + math.cos(ang) * r, BOT + 30 + math.sin(ang) * r * 0.7]
        puff.append(G(f"S{j + 1}", ell([9, 6]), fill(RUST), tr={"position": A(K(t, [STOMA2, BOT + 20]), K(t + 1.0, tgt)), "opacity": fade_in(t, 0.1)}))
    sec.append(shape("Puff", puff, [0, 0], 30.6, D))
    sec.append(appear(text("Puff Count", "≈ 300,000", [STOMA2 + 230, BOT + 120], 44, INK, 32.0, D, font=HEAD, just="left"), 32.0))
    sec.append(appear(caps("Puff Label", "SPORES PER SPOT", [STOMA2 + 232, BOT + 156], 32.2, D, size=16, just="left"), 32.2))
    sec.append(src("Src Spore", "SOURCE: APS PLANT DISEASE LESSON, COFFEE RUST", 32.0, D))
    # the cross-section: outline band, palisade and spongy cells as grey outlines, two stomata
    cells = [rect([30, 86], [x - BAND_C[0], -BAND_H / 2 + 68], 12) for x in range(int(BAND_C[0] - BAND_W / 2 + 40), int(BAND_C[0] + BAND_W / 2 - 20), 42)]
    rnd2 = random.Random(4)
    spong = [ell([rnd2.uniform(40, 60), rnd2.uniform(28, 40)], [x - BAND_C[0] + rnd2.uniform(-8, 8), rnd2.uniform(30, 110)])
             for x in range(int(BAND_C[0] - BAND_W / 2 + 50), int(BAND_C[0] + BAND_W / 2 - 30), 58)]
    lips = []
    for s in (STOMA1, STOMA2):
        lips += [ell([22, 12], [s - BAND_C[0] - 14, BAND_H / 2]), ell([22, 12], [s - BAND_C[0] + 14, BAND_H / 2])]
    sec.append(shape("Section", [G("Stomata", *lips, stroke(INK, 3), fill(WHITE)), G("Cells", *cells, *spong, stroke(LINE, 2)),
                                 G("Band", rect([BAND_W, BAND_H], None, 36), trim(0, A(K(0.5, 0), K(1.6, 100))), stroke(INK, 3))],
                     list(BAND_C), 0.5, D))
    fade_all(sec, t_off, 0.6)
    L += sec
    # the grown leaf icon from scene 2 opens into the section
    L.append(grey_leaf("Leaf In", LEAF2_L, A(K(0, list(LEAF2)), K(1.0, list(BAND_C))), 0, 1.4, rotation=A(K(0, -25), K(1.0, 0)),
                       scale=A(K(0, [100, 100]), K(1.0, [900, 900])), opacity=A(K(0.7, 100), K(1.3, 0))))
    # F: the whole leaf, spotted, falls; one spore drifts off to the right
    LF = 420
    spots = [G(f"Spot {j + 1}", ell([d, d]), fill(RUST), tr={"position": p, "scale": grow(37.6 + j * 0.12, 100, 0.4)})
             for j, (p, d) in enumerate([((-120, -10), 34), ((-40, 30), 22), ((40, -30), 30), ((110, 10), 26), ((-160, 30), 18), ((70, 40), 16), ((150, -18), 14)])]
    leaf = shape("Falling Leaf", spots + [G("Vein", path([(-LF * 0.4, 0), (LF * 0.38, 0)]), stroke(INK, 2)),
                                         G("Leaf", leaf_path(LF), stroke(INK, 3), fill(LAND))],
                 A(K(37.4, [CX, 500]), K(41.0, [CX, 500]), K(43.0, [CX - 120, 1400], {"inInfluence": 10, "outInfluence": 70, "inSpeed": 0, "outSpeed": 0})),
                 37.4, 43.0, rotation=A(K(41.0, -12), K(43.0, 30)), scale=grow(37.4, 100, 0.6))
    L.append(leaf)
    L.append(shape("Drift Spore", [G("Spore", ell([18, 12]), fill(RUST))], A(K(41.0, [CX + 150, 490]), K(43.2, list(inv(SPORE3)))), 41.0, D,
                   scale=A(K(41.0, [100, 100]), K(43.2, [100 / HS, 100 / HS]))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 4 - A FIELD OF COPIES (22 s)
# =====================================================================
GRID_C, NX, NY, GS, GD = (CX, 540), 20, 10, 50, 34
AXIS_X0, AXIS_X1, AXIS_Y = 260, 1660, 820


def s4_grid(D):
    L = []
    land = (GRID_C[0] + (NX - 1) * GS / 2, GRID_C[1])
    comp = (19.2, 21.0)
    gs = []
    for i in range(NX):
        for j in range(NY):
            p = [(i - (NX - 1) / 2) * GS, (j - (NY - 1) / 2) * GS]
            dist = math.hypot(p[0] + GRID_C[0] - land[0], (p[1]) * 1.6)
            if i == NX - 1 and j in (4, 5):
                to = 1.0
            else:
                to = 9.4 + dist / 1000 * 7.0
            col = A(K(to, ARA), K(to + 0.25, RUST), K(to + 1.2, RUST), K(to + 1.6, GREY2))
            gs.append(G(f"T{i}_{j}", ell([GD, GD]), fill(col), tr={"position": p, "scale": grow(0.1 + i * 0.03, 100, 0.25)}))
    L.append(shape("Grid", gs, list(GRID_C), 0.1, D,
                   scale=A(K(comp[0], [100, 100]), K(comp[1], [1400 / (NX * GS - GS + GD) * 100, 1.3])),
                   position=A(K(comp[0], list(GRID_C)), K(comp[1], [CX, AXIS_Y]))))
    L.append(shape("Spore", [G("Spore", ell([18, 12]), fill(RUST))], A(K(0, list(SPORE3)), K(0.9, list(land))), 0, 1.3, opacity=A(K(1.0, 100), K(1.3, 0))))
    # B: one narrow family (inset) and every tree the same
    b0, b1 = 2.2, 8.6
    L.append(shape("Family Line", [G("Line", arc((150, 210), (GRID_C[0] - 490, GRID_C[1] - 240), -0.25), trim(0, A(K(b0, 0), K(b0 + 1.0, 100))), stroke(ARA, 3)),
                                   G("Yemen", ell([14, 14], [150, 210]), fill(ARA))], [0, 0], b0, b1, opacity=fade_io(b0, b1)))
    L.append(caps("Family Label", "TYPICA, FROM YEMEN · ONE NARROW FAMILY", [150, 170], b0 + 0.3, b1, size=16, color=ARA, just="left", opacity=fade_io(b0 + 0.3, b1)))
    tp = (GRID_C[0] - 4.5 * GS, GRID_C[1] + 4.5 * GS)
    L.append(leader("Same Leader", (tp[0], tp[1] + 22), (tp[0], 880), b0 + 1.6, b1, opacity=fade_io(b0 + 1.6, b1)))
    L.append(caps("Same Label", "EVERY TREE THE SAME", [tp[0], 910], b0 + 1.8, b1, size=18, color=INK, opacity=fade_io(b0 + 1.8, b1)))
    # C: the monsoon and the wave
    c0 = 9.0
    L.append(shape("Wind", [G("Arrow", path([(0, 0), (-260, 0)]), path([(-240, -14), (-262, 0), (-240, 14)]), trim(0, A(K(c0, 0), K(c0 + 0.8, 100))), stroke(INK, 4))],
                   [1660, 230], c0, comp[0], opacity=fade_io(c0, comp[0])))
    L.append(caps("Wind Label", "MONSOON", [1530, 200], c0 + 0.3, comp[0], size=18, color=INK, opacity=fade_io(c0 + 0.3, comp[0])))
    L.append(text("Year 1", "1869", [150, 240], 80, INK, c0, 16.6, font=HEAD, just="left", opacity=fade_io(c0, 16.6)))
    L.append(text("Year 2", "≈ 1874", [150, 240], 80, INK, 16.6, comp[0], font=HEAD, just="left", opacity=fade_io(16.6, comp[0])))
    L.append(caps("Year Label", "RUST IN EVERY COFFEE DISTRICT", [154, 290], 16.8, comp[0], size=16, color=RUST, just="left", opacity=fade_io(16.8, comp[0])))
    L.append(src("Src Grid", "SOURCE: MCCOOK, COFFEE IS NOT FOREVER (2019)", c0, comp[0]))
    add_out(L[-1], comp[0] - 0.4)
    # D: the grey field becomes the chart's baseline
    L.append(shape("Baseline", [G("Bar", rect([1400 / HS, 6 / HS]), fill(GREY2))], list(inv((CX, AXIS_Y))), comp[1] - 0.3, D, opacity=fade_in(comp[1] - 0.3, 0.3)))
    L[0]["transform"]["opacity"] = A(K(comp[1] - 0.2, 100), K(comp[1] + 0.1, 0))
    L[0]["out"] = comp[1] + 0.1
    L.append(bg(D))
    return L


# =====================================================================
# SCENES 5-6 - THE COLLAPSE AND TEA (one chart, 1870-1900 across the 1,400 px baseline)
# =====================================================================
def yx(year):
    return AXIS_X0 + (year - 1870) / 30 * (AXIS_X1 - AXIS_X0)


def vy(v):
    return AXIS_Y - v * 4


COFFEE = [(1870, 100), (1874, 104), (1878, 100), (1881, 72), (1884, 44), (1886, 20), (1888, 14), (1890, 10)]
TEA_L = [(1875, 1), (1880, 4), (1885, 22), (1890, 58), (1895, 84), (1900, 100)]


def poly_path(pts, f):
    return path([f(p) for p in pts])


def chart_base(D, t, years, rig=None, prefix=""):
    L = [shape(f"{prefix}Axis", [G("Axis", rect([AXIS_X1 - AXIS_X0, 6]), fill(GREY2))], [CX, AXIS_Y], t, D, parent=rig)]
    for y in years:
        L.append(caps(f"{prefix}Tick {y}", str(y), [yx(y), AXIS_Y + 40], t, D, size=16, parent=rig))
    return L


def s5_collapse(D):
    L = []
    t_keep = 16.4
    L += chart_base(D, 0, [])
    for j, y in enumerate([1870, 1875, 1880, 1885, 1890]):
        L.append(appear(caps(f"Tick {y}", str(y), [yx(y), AXIS_Y + 40], 0.4 + j * 0.1, D, size=16), 0.4 + j * 0.1))
    L += wipe_text("Title", "Ceylon's coffee exports", [AXIS_X0, 180], 44, INK, 0.8, D, just="left")
    # red line: flat, then falling, timed to the VO
    seg = [K(1.2, 0), K(4.0, 30), K(7.0, 30), K(11.0, 76), K(14.0, 100)]
    L.append(shape("Coffee Line", [G("Line", poly_path(COFFEE, lambda p: (yx(p[0]), vy(p[1]))), trim(0, {"keyframes": seg}), stroke(ARA, 5))], [0, 0], 1.2, D))
    L.append(shape("Ghost 1870", [G("Ghost", path([(yx(1870), vy(100)), (yx(1886), vy(100))]), stroke(GREY2, 2))], [0, 0], 10.4, t_keep, opacity=fade_io(10.4, t_keep)))
    L.append(leader("Drop Leader", (yx(1886), vy(20) - 14), (yx(1886), vy(100) + 30), 11.0, t_keep, col=ARA, opacity=fade_io(11.0, t_keep)))
    L.append(appear(text("Drop", "−80 %", [yx(1886) + 24, vy(60)], 56, ARA, 11.2, t_keep, font=HEAD, just="left"), 11.2))
    L.append(appear(caps("Drop Year", "BY 1886", [yx(1886) + 28, vy(60) + 36], 11.4, t_keep, size=16, just="left"), 11.4))
    # ten land squares, nine abandoned
    sq = [G(f"Q{j + 1}", rect([26, 26], [j * 34, 0], 4), fill(A(K(13.2 + j * 0.08, ARA), K(13.5 + j * 0.08, GREY2)) if j < 9 else ARA)) for j in range(10)]
    L.append(shape("Land Squares", sq, [AXIS_X0, 940], 12.6, t_keep, opacity=fade_io(12.6, t_keep)))
    L.append(caps("Land Label", "≈ 90 % OF COFFEE LAND ABANDONED BY 1890", [AXIS_X0 + 360, 948], 13.6, t_keep, size=16, color=INK, just="left",
                  opacity=fade_io(13.6, t_keep)))
    L.append(src("Src Collapse", "SOURCE: KOEHLER (2017)", 11.0, t_keep))
    # Ward and his report
    L.append(caps("Ward Chip", "HARRY MARSHALL WARD · KEW · 1880", [1450, 120], 3.4, 10.6, size=16, color=INK, opacity=fade_io(3.4, 10.6)))
    L += doc("Ward Report", [("REPORT ON", 22, LAB), ("COFFEE LEAF", 30, HEAD), ("DISEASE", 30, HEAD), ("Colombo, 1881", 20, SCI)],
             (1450, 330), (280, 300), 4.2, 10.6, hl_line=1)
    for l in L[-6:]:
        add_out(l, 10.4)
    L.append(caps("Ward Credit", "WARD, REPORT ON COFFEE LEAF DISEASE (1881), RECREATED", [90, 1040], 4.6, 10.6, size=14, just="left", opacity=fade_io(4.6, 10.6)))
    L.append(bg(D))
    return L


# Ceylon inset (scene 6, top right)
INS_K, INS_C, INS_O = 60, (80.75, 7.9), (1640, 260)
LOOL, DAMB = (80.73, 7.26), (80.98, 6.80)
DAMB_S = [INS_O[0] + (DAMB[0] - INS_C[0]) * INS_K, INS_O[1] - (DAMB[1] - INS_C[1]) * INS_K]


def s6_tea(D):
    L = []
    rig = "Chart Rig"
    ch = chart_base(D, 0, [1870, 1875, 1880, 1885, 1890], rig=rig)
    for j, y in enumerate([1895, 1900]):
        ch.append(caps(f"Tick {y}", str(y), [yx(y), AXIS_Y + 40], 0.6 + j * 0.15, D, size=16, parent=rig, opacity=fade_in(0.6 + j * 0.15)))
    ch.append(text("Title", "Ceylon's coffee exports", [AXIS_X0, 180], 44, INK, 0, D, font=HEAD, just="left", parent=rig,
                   opacity=A(K(5.0, 100), K(5.4, 0))))
    ch += wipe_text("Title Tea", "…and the land under tea", [AXIS_X0, 180], 44, TEA, 5.6, D, just="left", parent=rig)
    ch.append(shape("Coffee Line", [G("Line", poly_path(COFFEE, lambda p: (yx(p[0]), vy(p[1]))), stroke(ARA, 5))], [0, 0], 0, D, parent=rig))
    ch.append(shape("Tea Line", [G("Line", poly_path(TEA_L, lambda p: (yx(p[0]), vy(p[1] * 0.9))), trim(0, A(K(6.0, 0), K(12.4, 100))), stroke(TEA, 5))],
                    [0, 0], 6.0, D, parent=rig))
    ch.append(appear(text("Tea Value", "≈ 400,000 acres", [yx(1900) - 10, vy(90) - 60], 40, INK, 12.2, D, font=HEAD, just="right", parent=rig), 12.2))
    ch.append(appear(caps("Tea Value Label", "OF TEA BY 1900", [yx(1900) - 10, vy(90) - 26], 12.4, D, size=16, color=TEA, just="right", parent=rig), 12.4))
    ch.append(src("Src Tea", "SOURCE: WENZLHUEMER, FROM COFFEE TO TEA CULTIVATION IN CEYLON (2008)", 12.0, 14.0))
    add_out(ch[-1], 13.8)
    # the advert: chart dims while the page is up
    a0, a1 = 14.2, 21.0
    for l in ch:
        if l["type"] != "null" and l["name"] not in ("Src Tea", "Title"):
            op = l["transform"].get("opacity")
            base = [] if not isinstance(op, dict) else [k for k in op["keyframes"] if k["time"] < a0]
            last = base[-1]["value"] if base else 100
            l["transform"]["opacity"] = A(*base, K(a0, last), K(a0 + 0.4, 25), K(a1, 25), K(a1 + 0.4, 100)) if l["in"] < a0 else l["transform"].get("opacity", 100)
    L += ch
    L += doc("Advert", [("PURE CEYLON TEA", 34, HEAD), ("direct from", 22, SCI), ("THE GARDEN TO THE TEAPOT", 22, LAB), ("Sold in Britain", 20, SCI)],
             (CX, 470), (560, 340), a0 + 0.2, a1)
    for l in L[-5:]:
        add_out(l, a1 - 0.3)
    L.append(caps("Advert Credit", "1890s PRESS ADVERTISEMENT, RECREATED", [90, 1040], a0 + 0.6, a1, size=14, just="left", opacity=fade_io(a0 + 0.6, a1)))
    L.append(null(rig, [CX, CY], 0, D, scale=[HS * 100, HS * 100]))
    # inset: Ceylon with Loolecondera, then Dambatenne
    ip = lambda ll: [INS_O[0] + (ll[0] - INS_C[0]) * INS_K, INS_O[1] - (ll[1] - INS_C[1]) * INS_K]
    sl = next(r for r in GEO["land"] if 79 < min(p[0] for p in r) < 82 and 5 < min(p[1] for p in r) < 10)
    L.append(disc("Damb Dot", list(inv(DAMB_S)), 24, TEA, 21.6, D, sh=0, scale=A(K(21.6, [0, 0]), K(22.0, [100 / HS, 100 / HS]))))
    L.append(appear(caps("Damb Label", "LIPTON · DAMBATENNE · 1890", [inv(DAMB_S)[0] - 30, inv(DAMB_S)[1] + 6], 22.0, D, size=16, color=INK, just="right"), 22.0))
    L.append(disc("Lool Dot", ip(LOOL), 18, TEA, 1.6, D, sh=0, scale=grow(1.6)))
    L.append(appear(caps("Lool Label", "JAMES TAYLOR · 1867 · 19 ACRES", [ip(LOOL)[0] - 30, ip(LOOL)[1] + 6], 2.0, 13.8, size=16, color=INK, just="right"), 2.0))
    add_out(L[-1], 13.6)
    L.append(shape("Inset", [G("SL", path([ip(p) for p in sl], True), fill(LAND))], [0, 0], 1.0, D, opacity=fade_in(1.0)))
    fade_all(L, 25.6, 0.8, keep={"Damb Dot"})  # leave only the dot for the cut into the rail
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 7 - WHO COULD AFFORD TO SWITCH (31 s)
# =====================================================================
RAIL_Y, R0, RPY = 620, 360, 300
K8, C8, O8 = 8.5, (-10, 15), (CX, 540)
CEY8 = screen(CEY, K8, C8, O8)


def s7_switch(D):
    L = []
    shr = "Shrink"
    out0 = 27.2
    c = []
    c.append(disc("Year0 Dot", A(K(0, list(fwd(DAMB_S))), K(0.9, [R0, RAIL_Y])), 24, TEA, 0, D, sh=0))
    for y in range(5):
        c.append(appear(caps(f"Year {y}", f"YEAR {y}", [R0 + y * RPY, RAIL_Y + 50], 0.8 + y * 0.1, D, size=16), 0.8 + y * 0.1))
    c.append(shape("Rail", [G("Rail", path([(R0, RAIL_Y), (R0 + 4 * RPY, RAIL_Y)]), trim(0, A(K(0.6, 0), K(1.6, 100))), stroke(INK, 3))], [0, 0], 0.6, D))
    # clear the coffee
    tree = icon_plant(GREY, True) + [G("Roots", path([(0, 26), (-12, 40)]), path([(0, 26), (12, 40)]), path([(0, 26), (0, 44)]), stroke(GREY, 4))]
    c.append(shape("Uprooted", tree, [R0, RAIL_Y - 90], 1.8, D, rotation=-80, scale=grow(1.8, 130)))
    c.append(appear(caps("Clear Label", "CLEAR THE COFFEE", [R0, RAIL_Y - 150], 2.1, D, size=16, color=INK), 2.1))
    # no income until the first tea harvest
    c.append(shape("No Income", [G("Band", path([(R0, RAIL_Y), (R0 + 3 * RPY, RAIL_Y)]), trim(0, A(K(5.2, 0), K(8.6, 100))), stroke(GREY2, 16, cap="butt"))],
                   [0, 0], 5.2, D))
    c.append(appear(caps("No Income Label", "NO INCOME", [R0 + 1.5 * RPY, RAIL_Y - 30], 6.0, D, size=20, color=INK), 6.0))
    c.append(shape("Tea Bush", icon_plant(TEA, False), [R0 + 3 * RPY, RAIL_Y - 50], 8.6, D, scale=grow(8.6, 160)))
    c.append(appear(caps("Harvest Label", "FIRST HARVEST ≈ YEAR 3", [R0 + 3 * RPY, RAIL_Y - 110], 8.9, D, size=16, color=TEA), 8.9))
    c.append(src("Src Switch", "SOURCE: WENZLHUEMER (2008)", 8.9, 12.0))
    add_out(c[-1], 11.8)
    # the factory, as a flow the leaf moves through
    FY, fx = 300, [560, 820, 1080, 1340]
    stages = ["WITHER", "ROLL", "OXIDISE", "DRY"]
    f0 = 12.4
    fac = [shape("Flow", [G("Flow", path([(fx[0] - 60, FY), (fx[-1] + 60, FY)]), trim(0, A(K(f0, 0), K(f0 + 1.0, 100))), stroke(INK, 3))], [0, 0], f0, D)]
    for j, (s, x) in enumerate(zip(stages, fx)):
        t = f0 + 1.2 + j * 1.6
        fac.append(appear(caps(f"Stage {s}", s, [x, FY + 44], t, D, size=16, color=INK), t))
        fac.append(disc(f"Stage {s} Dot", [x, FY], 14, INK, t, D, sh=0, scale=grow(t)))
    heat = [G(f"Heat {k}", path([(k * 14 - 14, 0), (k * 14 - 10, -14), (k * 14 - 18, -28), (k * 14 - 14, -42)]), stroke(INK, 3)) for k in range(3)]
    fac.append(shape("Heat", heat, [fx[3], FY - 30], f0 + 6.0, D, opacity=fade_in(f0 + 6.0)))
    lt = [K(f0 + 1.2 + j * 1.6, [x, FY - 40]) for j, x in enumerate(fx)]
    fac.append(shape("Tea Leaf", [G("Leaf", leaf_path(46), fill(A(K(f0 + 4.4, TEA), K(f0 + 5.2, OXID))))], A(*lt), f0 + 1.0, D, rotation=-20,
                     opacity=fade_in(f0 + 1.0)))
    fac.append(appear(caps("Factory Label", "EVERY ESTATE NEEDED A FACTORY", [CX, 180], f0 + 0.4, D, size=18, color=INK), f0 + 0.4))
    # money and demand
    d0 = 21.0
    for l in fac:
        l["transform"]["opacity"] = A(K(d0, 100), K(d0 + 0.5, 30)) if l["in"] < d0 else l["transform"]["opacity"]
    c += fac
    c.append(shape("London Line", [G("L", path([(fx[-1] + 60, FY), (1580, FY)]), trim(0, A(K(d0 + 0.4, 0), K(d0 + 1.0, 100))), stroke(INK, 3))], [0, 0], d0 + 0.4, D))
    c.append(appear(text("London", "London £", [1600, FY + 12], 34, INK, d0 + 1.0, D, font=HEAD, just="left"), d0 + 1.0))
    cup = [G("Handle", ell([22, 22], [34, -4]), stroke(INK, 3)), G("Cup", path([(-30, -18), (30, -18), (22, 18), (-22, 18)], True), stroke(INK, 3), fill(WHITE)),
           G("Saucer", path([(-44, 24), (44, 24)]), stroke(INK, 3))]
    c.append(shape("Teacup", cup, [1660, 460], d0 + 2.0, D, scale=grow(d0 + 2.0)))
    c.append(appear(caps("Demand Label", "DEMAND ALREADY THERE", [1660, 530], d0 + 2.3, D, size=16, color=INK), d0 + 2.3))
    c.append(marker("No Income Swipe", R0 + 1.5 * RPY - 80, RAIL_Y - 30, 160, d0 + 3.4, D, size=20))
    parent_all(c, shr)
    L += c
    end = inv(CEY8)
    L.append(null(shr, end, 0, D, anchor=end, scale=A(K(out0, [100, 100]), K(out0 + 2.0, [0, 0]))))
    L.append(disc("Ceylon Dot", end, 24 / HS, TEA, out0 + 1.2, D, sh=0, opacity=fade_in(out0 + 1.2, 0.5)))
    # the world map of scene 8 fades in underneath at its scene-8 screen size
    L.append(land_layer("Land", K8, out0, D, parent="Map Match", position=[O8[0] - C8[0] * K8, O8[1] + C8[1] * K8], opacity=fade_in(out0, 1.4)))
    L.append(null("Map Match", [CX, CY], 0, D, anchor=[CX, CY], scale=[100 / HS, 100 / HS]))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 8 - THE RUST CROSSES THE ATLANTIC (29 s)
# =====================================================================
FOC = (-88.0, 15.0)
ZK = 40 / K8
CHI = (-92.6, 16.4)


def s8_atlantic(D):
    L = []
    rig = "Map Rig"
    m = lambda ll: [(ll[0] - C8[0]) * K8, -(ll[1] - C8[1]) * K8]  # map space relative to the frame centre
    p_world = screen(FOC, K8, C8, O8)
    p_zoom = (820, 520)
    p_chi = [CX - (CHI[0] - FOC[0]) * K8 * ZK, CY + (CHI[1] - FOC[1]) * K8 * ZK]
    z0, z1, c0, c1 = 12.0, 14.6, 25.0, 27.6
    # route
    stops = [("CEYLON 1869", (80.7, 7.8), 0.6), ("INDIA", (77.5, 12.5), 1.6), ("EAST AFRICA", (37.0, -1.0), 3.4),
             ("WEST AFRICA, 1950s", (-5.0, 7.5), 5.2), ("BRAZIL 1970", (-45.0, -15.0), 7.2), ("CHIAPAS 1981", CHI, 9.4)]
    dots, labs = [], []
    for j in range(1, len(stops)):
        (_, a, ta), (_, b, tb) = stops[j - 1], stops[j]
        pa, pb = m(a), m(b)
        mx_, my_ = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        cpt = (mx_ - dy * 0.2, my_ + dx * 0.2)
        n = max(3, int(math.hypot(dx, dy) / 16))
        for k in range(1, n + 1):
            u = k / n
            x = (1 - u) ** 2 * pa[0] + 2 * (1 - u) * u * cpt[0] + u * u * pb[0]
            y = (1 - u) ** 2 * pa[1] + 2 * (1 - u) * u * cpt[1] + u * u * pb[1]
            t = ta + 0.2 + (tb - ta - 0.2) * u
            dots.append(G(f"R{len(dots) + 1}", ell([7, 7]), fill(RUST), tr={"position": [x, y], "scale": grow(t, 100, 0.15)}))
    L.append(shape("Route", dots, [0, 0], 0.8, D, parent=rig, opacity=A(K(11.2, 100), K(11.6, 0))))
    for j, (lab, ll, t) in enumerate(stops):
        sp = screen(ll, K8, C8, O8)
        labs.append(caps(f"Stop {j + 1}", lab, [sp[0], sp[1] - 18], t + 0.1, 11.6, size=15, color=INK, opacity=fade_io(t + 0.1, 11.6)))
    L += labs
    L.append(src("Src Route", "SOURCE: MCCOOK (2019); APS; INIFAP", 1.0, 11.6))
    add_out(L[-1], 11.2)
    L.append(disc("Ceylon Dot", CEY8, 24, A(K(0.2, TEA), K(0.7, RUST)), 0, 11.6, sh=0, opacity=A(K(11.2, 100), K(11.6, 0))))
    # B: 2012, half of Central America's coffee land
    b0, b1 = 15.0, 19.6
    L.append(appear(text("Year 2012", "2012", [1440, 250], 96, INK, b0 - 0.6, 24.6, font=HEAD, just="left"), b0 - 0.6))
    add_out(L[-1], 24.6)
    rnd = random.Random(21)
    hits = []
    while len(hits) < 46:
        lo, la = rnd.uniform(-92, -83), rnd.uniform(9, 16)
        if in_land(lo, la):
            col = RUST if len(hits) % 2 == 0 or rnd.random() < 0.06 else GREY2
            hits.append(G(f"A{len(hits) + 1}", ell([2.6, 2.6]), fill(col), tr={"position": m((lo, la)), "scale": grow(b0 + rnd.uniform(0, 1.6), 100, 0.3)}))
    L.append(shape("Area Hit", hits, [0, 0], b0, b1 + 0.4, parent=rig, opacity=A(K(b1, 100), K(b1 + 0.4, 0))))
    L.append(shape("Area Bar", [G("Fill", rect([0.53 * 420, 34], [0.53 * 210, 0]), fill(RUST)), G("Box", rect([420, 34], [210, 0]), stroke(INK, 2))],
                   [1440, 420], b0 + 0.6, b1, opacity=fade_io(b0 + 0.6, b1)))
    L.append(appear(text("Area Value", "≈ 53 %", [1440, 510], 52, INK, b0 + 1.0, b1, font=HEAD, just="left"), b0 + 1.0))
    L.append(appear(caps("Area Label", "OF CENTRAL AMERICA'S COFFEE AREA HIT, 2012/13", [1440, 546], b0 + 1.2, b1, size=14, just="left"), b0 + 1.2))
    L.append(src("Src Area", "SOURCE: ICO COFFEE MARKET REPORT, MARCH 2013", b0 + 1.0, b1))
    for l in L[-4:]:
        add_out(l, b1 - 0.3)
    # C: Mexico's harvest bars (episode 1's rig, corrected low)
    h0, h1 = 19.8, 24.8
    for j, (lab, v, t) in enumerate([("2012/13", 4.3, h0), ("2015/16", 2.2, h0 + 1.6)]):
        x, h = 1500 + j * 200, v * 80
        L.append(shape(f"Bar {lab}", [G("Bar", rect([120, h], [0, -h / 2], 4), fill(MX if j == 0 else GREY2))], [x, 860], t, h1,
                       scale=A(K(t, [100, 0]), K(t + 0.6, [100, 100]))))
        L.append(appear(text(f"Bar {lab} Value", f"{v} M", [x, 860 - h - 20], 38, INK, t + 0.4, h1, font=HEAD), t + 0.4))
        L.append(appear(caps(f"Bar {lab} Label", lab, [x, 900], t, h1, size=16, color=INK), t))
    L.append(appear(caps("Bars Title", "MEXICO'S HARVEST, BAGS", [1600, 420], h0, h1, size=16, color=INK), h0))
    L.append(src("Src Bars", "SOURCE: USDA FAS PSD; USDA FAS MEXICO COFFEE ANNUAL 2016", h0, h1))
    for l in L[-8:]:
        add_out(l, h1 - 0.3)
    # D: Chiapas
    st_items = [path([m(p) for p in r], True) for rings in GEO["mexico"].values() for r in rings]
    chi = [path([m(p) for p in r], True) for r in GEO["mexico"]["Chiapas"]]
    L.append(shape("Chiapas", [G("Chiapas", *chi, fill(MX, 35))], [0, 0], c0, D, parent=rig, opacity=fade_in(c0, 0.6)))
    L.append(disc("Chiapas Dot", list(inv((CX, CY))), 24 / HS, MX, c1 - 0.2, D, sh=0, scale=grow(c1 - 0.2, 100, 0.3)))
    L.append(shape("States", [G("Borders", *st_items, stroke(WHITE, 2 / ZK)), G("Fill", *st_items, fill(LAND))], [0, 0], z0, D, parent=rig, opacity=fade_in(z0 + 1.0, 1.0)))
    L.append(shape("Land", [G("Land", *[path([m(p) for p in r], True) for r in GEO["land"]], fill(LAND))], [0, 0], 0, D, parent=rig))
    L.append(null(rig, list(p_world), 0, D, anchor=m(FOC), scale=zmulti(1.0, [(z0, z1, ZK)]),
                  position=pmulti(p_world, [(z0, z1, p_zoom), (c0, c1, p_chi)])))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 9 - MEXICO CHANGES THE TREE (26 s)
# =====================================================================
TREE = {"ar": (230, 300), "rb": (230, 680), "tm": (560, 490), "Catimor": (930, 300), "Sarchimor": (930, 680),
        "Costa Rica 95": (1330, 220), "Oro Azteca": (1330, 480), "Marsellesa": (1330, 760)}
NODE_H = 120


def half_disc(name, pos, d, t0, t1, **tr):
    r = d / 2
    k = 0.5523 * r
    left = path([(0, -r), (-r, 0), (0, r)], True, i=[(0, 0), (0, -k), (-k, 0)], o=[(-k, 0), (0, k), (0, 0)])
    right = path([(0, -r), (r, 0), (0, r)], True, i=[(0, 0), (0, -k), (k, 0)], o=[(k, 0), (0, k), (0, 0)])
    return shape(name, [G("Ara Half", left, fill(ARA)), G("Rob Half", right, fill(ROB))], pos, t0, t1, **tr)


def rescue_tree(t, D, prefix, cam, glow_t=None, keep=None):
    """Episode 1's rescue tree, shown whole (callback). Returns layers; all parented to cam."""
    T = TREE
    out = []
    op = fade_in(t, 0.6)
    w = A(K(glow_t, 4), K(glow_t + 0.8, 8)) if glow_t else 4

    def ln(name, pts, col, width=4):
        return shape(f"{prefix}{name}", [G("L", path(pts), stroke(col, width))], [0, 0], t, D, opacity=op)
    ar, rb, tm = T["ar"], T["rb"], T["tm"]
    out.append(ln("Link Ara", [(ar[0] + 46, ar[1]), (400, ar[1]), (400, tm[1] - 20), (tm[0] - 62, tm[1] - 20)], ARA))
    out.append(ln("Link Rob", [(rb[0] + 46, rb[1]), (400, rb[1]), (400, tm[1] + 20), (tm[0] - 62, tm[1] + 20)], ROB, w))
    for nm in ("Catimor", "Sarchimor"):
        p = T[nm]
        out.append(ln(f"Link {nm} A", [(tm[0] + 62, tm[1] - 3), (717, tm[1] - 3), (717, p[1] - 3), (p[0] - 52, p[1] - 3)], ARA))
        out.append(ln(f"Link {nm} R", [(tm[0] + 62, tm[1] + 3), (723, tm[1] + 3), (723, p[1] + 3), (p[0] - 52, p[1] + 3)], ROB, w))
    for nm, srcn in (("Costa Rica 95", "Catimor"), ("Oro Azteca", "Catimor"), ("Marsellesa", "Sarchimor")):
        p, s = T[nm], T[srcn]
        out.append(ln(f"Link {nm} A", [(s[0] + 50, s[1] - 3), (1147, s[1] - 3), (1147, p[1] - 3), (p[0] - 50, p[1] - 3)], ARA))
        out.append(ln(f"Link {nm} R", [(s[0] + 50, s[1] + 3), (1153, s[1] + 3), (1153, p[1] + 3), (p[0] - 50, p[1] + 3)], ROB, w))
    out.append(disc(f"{prefix}Arabica", list(ar), 80, ARA, t, D, sh=0, opacity=op))
    out.append(disc(f"{prefix}Robusta", list(rb), 80, ROB, t, D, sh=0, opacity=op))
    out.append(half_disc(f"{prefix}Timor", list(tm), 110, t, D, opacity=op))
    out.append(text(f"{prefix}Timor Name", "Timor Hybrid", [tm[0], tm[1] + 98], 30, INK, t, D, font=HEAD, opacity=op))
    for nm in ("Catimor", "Sarchimor"):
        out.append(half_disc(f"{prefix}{nm}", list(T[nm]), 90, t, D, opacity=op))
        out.append(text(f"{prefix}{nm} Name", nm, [T[nm][0], T[nm][1] - 66], 30, INK, t, D, font=HEAD, opacity=op))
    for nm in ("Costa Rica 95", "Oro Azteca", "Marsellesa"):
        p = T[nm]
        out.append(disc(f"{prefix}Var {nm}", list(p), 90, ARA, t, D, sh=0, opacity=op))
        out.append(text(f"{prefix}{nm} Name", nm, [p[0] + 72, p[1] + 12], 32, INK, t, D, font=HEAD, just="left", opacity=op))
    out.append(caps(f"{prefix}Ep1 Tag", "FROM EPISODE 1", [CX, 100], t, D, size=16, opacity=op))
    for l in out:
        l["parent"] = cam
    return out


def s9_tree(D):
    L = []
    g0, p0, f0, t0 = 0.0, 7.4, 12.2, 15.6
    # A: half a million families, most on two hectares or less
    CELL, GAP = 34, 6
    gx0, gy0 = CX - (10 * CELL + 9 * GAP) / 2 + CELL / 2, 340
    cells = []
    for k in range(100):
        r, c = divmod(k, 10)
        p = [gx0 + c * (CELL + GAP), gy0 + r * (CELL + GAP)]
        t = 0.9 + k * 0.025
        it = [G(f"C{k + 1}", rect([CELL, CELL], p, 3), fill(MX) if k < 84 else stroke(GREY2, 2), tr={"opacity": fade_in(t, 0.15)})]
        cells += it
    L.append(shape("Cells", cells, [0, 0], 0.9, p0 + 0.6, opacity=A(K(p0, 100), K(p0 + 0.5, 0))))
    L.append(disc("Dot In", A(K(0, [CX, CY]), K(0.8, [gx0, gy0])), 24, MX, 0, 1.1, sh=0))
    L.append(appear(text("Families", "≈ 500,000 families", [CX, 260], 46, INK, 1.2, p0, font=HEAD), 1.2))
    L.append(appear(text("Small", "84 % farm 2 ha or less", [CX, 800], 40, MX, 3.6, p0, font=HEAD), 3.6))
    L.append(src("Src Families", "SOURCE: INEGI CENSUS VIA LA JORNADA (2018); USDA FAS MX2026-0026", 1.2, p0))
    for l in L[-3:]:
        add_out(l, p0 - 0.3)
    # B: one plot against three football pitches
    PL = 300
    pc = (700, 520)
    rows = [G(f"Row {j + 1}", *[ell([12, 12], [x, -PL / 2 + 30 + j * 34]) for x in range(-PL // 2 + 24, PL // 2 - 10, 22)], fill(MX)) for j in range(8)]
    L.append(shape("Plot Rows", rows, list(pc), p0 + 0.6, f0 + 2.6, opacity=fade_io(p0 + 0.6, f0 + 2.6)))
    L.append(shape("Plot", [G("Plot", rect([PL, PL]), trim(0, A(K(p0, 0), K(p0 + 0.8, 100))), stroke(MX, 4))], list(pc), p0, f0 + 2.6,
                   opacity=A(K(f0 + 2.2, 100), K(f0 + 2.6, 0))))
    L.append(appear(text("Plot Label", "2 ha", [pc[0], pc[1] + PL / 2 + 60], 40, INK, p0 + 0.6, f0 - 0.2, font=HEAD), p0 + 0.6))
    for j in range(3):
        L.append(shape(f"Pitch {j + 1}", [G("P", rect([223, 145]), stroke(GREY, 2)), G("Half", path([(0, -72), (0, 72)]), ell([40, 40]), stroke(GREY2, 2))],
                       [1180, 360 + j * 160], p0 + 1.4 + j * 0.3, f0 - 0.2, scale=grow(p0 + 1.4 + j * 0.3), opacity=A(K(f0 - 0.6, 100), K(f0 - 0.2, 0))))
    L.append(appear(caps("Pitch Label", "≈ 3 FOOTBALL PITCHES", [1180, 880], p0 + 2.4, f0 - 0.2, size=18, color=INK), p0 + 2.4))
    add_out(L[-1], f0 - 0.6)
    # the tea factory of scene 7 drops over the plot and covers it
    fac = [G("Chimney", rect([40, 120], [130, -200]), stroke(INK, 4), fill(WHITE)),
           G("Roof", path([(-220, -100), (-150, -170), (-80, -100), (-10, -170), (60, -100), (130, -170), (220, -100)]), stroke(INK, 4)),
           G("Body", rect([440, 300], [0, 50]), stroke(INK, 4), fill(WHITE))]
    L.append(shape("Factory", fac, A(K(f0, [pc[0], -300]), K(f0 + 0.7, list(pc))), f0, t0, opacity=A(K(t0 - 0.6, 100), K(t0 - 0.2, 0))))
    # C: episode 1's rescue tree, whole; the robusta line thickens; settle on Catimor
    cam = "Cam"
    z0, z1 = 23.2, 25.6
    tree = rescue_tree(t0, D, "", cam, glow_t=18.5)
    for l in tree:
        if l["name"] != "Catimor":
            add_out(l, z0, 0.5)
    L += tree
    cat = TREE["Catimor"]
    zoom = NODE_H / 90 / HS
    L.append(null(cam, list(cat), 0, D, scale=zoom_scale(z0, z1, 1.0, zoom), position=zoom_pos(z0, z1, cat, (CX, CY))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 10 - WHAT THE BORROWED GENES COST (28 s)
# =====================================================================
SX0, SY = 360, 640


def sx(score):
    return SX0 + (score - 75) * 80


def s10_cost(D):
    L = []
    a1 = 16.6
    head_y = SY - 120
    # Catimor node drops onto the axis and becomes its tick
    L.append(half_disc("Catimor Head", A(K(0.2, [CX, CY]), K(1.4, [sx(80), head_y])), NODE_H, 0, a1,
                       scale=A(K(0.2, [100, 100]), K(1.4, [24 / NODE_H * 100] * 2)), opacity=A(K(a1 - 0.4, 100), K(a1, 0))))
    L.append(shape("Catimor Stem", [G("S", path([(sx(80), SY), (sx(80), head_y + 12)]), trim(0, A(K(1.4, 0), K(1.8, 100))), stroke(INK, 3))], [0, 0], 1.4, a1))
    L.append(appear(caps("Catimor Label", "CATIMOR ≈ 80", [sx(80) - 20, head_y - 30], 1.8, a1, size=18, color=INK, just="right"), 1.8))
    L.append(shape("Axis", [G("Axis", path([(sx(75), SY), (sx(90), SY)]), trim(0, A(K(0.6, 0), K(1.6, 100))), stroke(INK, 3))], [0, 0], 0.6, a1))
    for s in (75, 80, 85, 90):
        L.append(appear(caps(f"Score {s}", str(s), [sx(s), SY + 40], 1.0, a1, size=16), 1.0))
    L.append(appear(caps("Axis Label", "CUP SCORE", [sx(90), SY + 76], 1.2, a1, size=16, color=INK, just="right"), 1.2))
    # the specialty line
    L.append(shape("Specialty", [G("S", path([(sx(80), SY), (sx(80), 300)]), trim(0, A(K(3.0, 0), K(3.6, 100))), stroke(GREY2, 2))], [0, 0], 3.0, a1))
    L += wipe_text("Specialty Label", "80 = specialty", [sx(80) + 20, 300], 34, INK, 3.4, a1, just="left", hl=True)
    # INIFAP review, lower left
    L += doc("INIFAP", [("Rev. Mex. Cienc. Agríc.", 16, SCI), ("RUST-RESISTANT", 18, LAB), ("HYBRIDS: LOW", 18, LAB), ("CUP QUALITY", 18, LAB)],
             (1500, 340), (300, 250), 5.6, 10.6, hl_line=2)
    L.append(caps("INIFAP Credit", "INIFAP, REV. MEX. CIENC. AGRÍC. (2024), RECREATED", [90, 1040], 6.0, 10.6, size=14, just="left", opacity=fade_io(6.0, 10.6)))
    for l in L[-7:]:
        add_out(l, 10.4)
    # Caturra beside it
    L.append(disc("Caturra Head", A(K(10.8, [sx(82), 200]), K(11.6, [sx(82), head_y])), 24, ARA, 10.8, a1, sh=0))
    L.append(shape("Caturra Stem", [G("S", path([(sx(82), SY), (sx(82), head_y + 12)]), trim(0, A(K(11.6, 0), K(12.0, 100))), stroke(INK, 3))], [0, 0], 11.6, a1))
    L.append(appear(caps("Caturra Label", "CATURRA ≈ 82", [sx(82) + 20, head_y - 30], 12.0, a1, size=18, color=INK, just="left"), 12.0))
    L.append(src("Src Cup", "SOURCE: REVISTA AGROTECNOLÓGICA AMAZÓNICA (2021), PERU, ONE TRIAL", 12.0, a1))
    for l in L:
        if l["out"] > a1:
            add_out(l, a1 - 0.4)
    # the tree returns; Costa Rica 95 catches rust
    cam = "Cam"
    t0, r0, z0, z1 = 17.2, 19.8, 24.6, 27.4
    tree = rescue_tree(t0, D, "", cam)
    cr = TREE["Costa Rica 95"]
    tree.append(disc("CR95 Rust", list(cr), 90, RUST, r0, D, sh=0, parent=cam, scale=grow(r0, 100, 1.4)))
    tree.append(caps("CR95 Chip", "NOW CATCHES RUST IN COSTA RICA", [cr[0] + 72, cr[1] + 52], r0 + 1.2, D, size=16, color=RUST, just="left",
                     parent=cam, opacity=fade_in(r0 + 1.2)))
    tree.append(caps("Src CR95", "SOURCE: WORLD COFFEE RESEARCH", [90, 1040], r0 + 1.2, D, size=14, just="left", opacity=fade_in(r0 + 1.2)))
    for l in tree:
        if l["name"] != "CR95 Rust":
            add_out(l, z0, 0.5)
    L += tree
    zoom = SPOT_D / 90 / HS
    L.append(null(cam, list(cr), 0, D, scale=zoom_scale(z0, z1, 1.0, zoom), position=zoom_pos(z0, z1, cr, inv(SPOT))))
    L.append(bg(D))
    return L


# =====================================================================
# SCENE 11 - CLOSE (21 s)
# =====================================================================
def s11_close(D):
    L = []
    rig = "Tin Rig"
    sw, lid_t, up = 5.4, 9.6, (11.0, 12.0)
    L += wipe_text("End 1", "The Fungus That Turned", [CX, 860], 64, INK, 12.4, D)
    L += wipe_text("End 2", "Ceylon Into a Tea Country", [CX, 950], 64, INK, 12.9, D)
    fw = tw("Fungus", 64, HEAD)
    x0 = CX - tw("The Fungus That Turned", 64, HEAD) / 2 + tw("The ", 64, HEAD)
    L.append(marker("End Swipe", x0 - 10, 860, fw + 20, 13.6, D, size=64))
    L.append(disc("Spot", list(SPOT), SPOT_D, RUST, 0, D, sh=0, parent=rig, opacity=A(K(sw, 100), K(sw + 0.6, 0))))
    L.append(shape("Mexico Leaf", [G("Vein", path([(-CLEAF_L * 0.4, 0), (CLEAF_L * 0.38, 0)]), stroke(ROB, 4)), G("Leaf", leaf_path(CLEAF_L), fill(MX))],
                   list(CLEAF), sw, D, parent=rig, rotation=CLEAF_R, opacity=fade_in(sw, 0.6)))
    L.append(grey_leaf("Coffee Leaf", CLEAF_L, list(CLEAF), 0, sw + 0.8, parent=rig, rotation=CLEAF_R, opacity=A(K(0, 0), K(0.8, 100), K(sw, 100), K(sw + 0.6, 0))))
    L.append(caps("Label Oro", "ORO AZTECA · A LITTLE ROBUSTA", [CLEAF[0], CLEAF[1] - 110], sw + 0.6, up[0], size=16, color=MX, parent=rig,
                  opacity=fade_io(sw + 0.6, up[0])))
    tin = tin_layers(D, 0, rig=rig, lid_open=True)
    tin[1]["transform"]["position"] = A(K(lid_t, [440, TABLE_Y - 14]), K(lid_t + 0.6, [TIN[0], 250]), K(lid_t + 1.1, [TIN[0], 352]))
    L.append(disc("Seal", list(SEAL), SEAL_D, TEA, 0, D, sh=0, parent=rig, opacity=fade_in(0.2, 0.8)))
    for l in tin:
        l["transform"]["opacity"] = fade_in(0.2, 0.8)
    tin[-1]["parent"] = rig
    L += tin
    L.append(null(rig, [CX, CY], 0, D, anchor=[CX, CY], position=A(K(up[0], [CX, CY]), K(up[1], [CX, 420])),
                  scale=A(K(up[0], [100, 100]), K(up[1], [78, 78]))))
    L.append(bg(D))
    return L


# =====================================================================
# MAIN
# =====================================================================
SCENES = [("S1_Tin", 20.0, s1_tin), ("S2_Island", 23.0, s2_island), ("S3_Spore", 44.0, s3_spore), ("S4_Grid", 22.0, s4_grid),
          ("S5_Collapse", 18.0, s5_collapse), ("S6_Tea", 28.0, s6_tea), ("S7_Switch", 31.0, s7_switch), ("S8_Atlantic", 29.0, s8_atlantic),
          ("S9_Tree", 26.0, s9_tree), ("S10_Cost", 28.0, s10_cost), ("S11_Close", 21.0, s11_close)]


if __name__ == "__main__":
    write(SCENES, "Ceylon_Rust", "02_ceylon_rust")
