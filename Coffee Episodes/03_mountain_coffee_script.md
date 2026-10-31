# Why Mountain Coffee Tastes Different: Script and Storyboard

**Status:** draft v2 (revised against `notes/fact_check.md`, `notes/visual_direction.md` and `notes/story_edit.md`).
**Format:** 3:58 (586 words of VO ≈ 3:47 at 155 wpm, plus about 11 s of holds on the charts and end card), 1920×1080, 30 fps, AE 26.5.
**The question:** Why is a coffee graded by the height of its farm?
**The answer:** Height is a stand-in for cold. Cooler air makes the cherry ripen more slowly, so the seed has longer to fill. It comes out denser, and the coffee tastes more acidic. A grade line in metres marks how long the seed had to fill, and height is only the usual way to find that out.
**The surprise:** The bean never reads an altimeter. Two Mexican farms on the same rung, at the same 1,200 m, sit about a degree apart, and a shade tree can delay ripening by up to a month without the farm moving at all. The grade can't see either. Lands in scene 8 (2:48).
**Mexico's part:** Mexico's grade ladder is the episode's document, and two Mexican farms on its top line (Coatepec in Veracruz, and the Soconusco in Chiapas) are the case that breaks the metres-only reading. The answer changes from "higher is better" to "colder is better, and metres are a rough proxy for it".
**Reused from earlier episodes:** the red cherry and its cross-section (ep. 1, S1), the Mexico map with state outlines (ep. 1, S7), the ep. 1 contour-mountain icon as the base of the altitude scale, the shared seed cell honeycomb and gauge/thermometer from `coffee_common.py`.
**New colours:** ice blue `#A7CFEA` (climate temperature: thermometers, isotherms, the cold end of every scale), from the locked season palette. Heat is drawn as the absence of blue, in ink. Water in S4 is water cyan `#4FB3C8` (season palette). Coatepec and Soconusco coffee leaves are Mexico green; the Colombian research farm's shrubs are grey.

## Logline

A dashed line runs across a hillside above Coatepec. Coffee picked above it can carry Mexico's top grade. The episode asks why a height should set a bean's grade. It climbs the slope with a thermometer to show the cherry ripening on a heat budget, then shows what the extra months do inside the seed and what the cold changes in the cup. The trade's grade lines, Mexico's among them, go on one altitude scale. Past the middle, two Mexican farms on the same rung turn out to be a degree apart, and a shade tree slows a cherry as a mountain does. The close goes back to the hillside, where the line in metres stays put and the cold it stood for climbs.

## Match-cut chain

| Cut | Out of | Into | Shared element |
| :--- | :--- | :--- | :--- |
| 1→2 | The dashed 1,200 m contour across the Coatepec hillside, ink, 3 px dash | The 1,200 m tick line on the altitude scale beside the full mountain profile | The same dashed line at the same screen height. The camera pulls back and the hillside becomes the upper slope of the mountain, so the profile and line are continuous |
| 2→3 | The thermometer bulb at the Coatepec pin, ice-blue circle, 60 px | The bulb of the heat-jar thermometer at frame centre | An ice-blue circle that slides to centre and grows to 90 px |
| 3→4 | The cherry icon at the end of the slow (upper) calendar bar, 90 px | The red cherry in cross-section at frame centre | A red circle that scales to 420 px as the camera pushes in |
| 4→5 | The slow seed's elliptical outline | The outline of Réunion on a small map | An ellipse that flattens into the island's outline |
| 5→6 | The coldest plot's dot on Réunion, ice blue, 18 px | A neutral "cold" marker at the foot of the shared altitude scale, which then climbs it and stops at the first grade band (Costa Rica, ≈ 1,200 m) | An ice-blue dot at the same screen position |
| 6→7 | The Mexico rail on the altitude scale | The Mexican grade ladder on the same scale | The rail itself. The other countries slide off and Mexico's rail widens into rungs |
| 7→8 | The Coatepec dot on the Mexico map, Mexico green, 22 px | The same dot on the same map, at the start of a pull-out | The dot and map are unchanged at the cut; S8 opens by pulling out to bring the Soconusco into frame |
| 8→9 | The Coatepec hillside profile with the ice-blue 19 °C isotherm sitting on the 1,200 m line | The S1 hillside with its dashed grade line | The same hillside drawing and a horizontal line at the same height |

## Script and storyboard

Timecodes are for the master comp.

### 1. The line on the hillside (0:00–0:21, `S1_Line`)
**Storyboard**
- **A:** White frame. A hillside draws on as a single ink slope line on white, rising left to right (no filled ground), planted with rows of small coffee shrubs (Mexico-green leaves). A small label top-left: ABOVE COATEPEC, VERACRUZ. A dashed ink contour draws across the slope with a tag at its end: ≈ 1,200 m.
- **B:** Above the line, the shrubs' row-end tags read ESTRICTAMENTE ALTURA. Below it they read ALTURA. A highlighter swipe runs along the dashed line. Then the grade tags fade and only the line and hillside are left. *(Match cut out.)*

**VO:** "On a hillside above Coatepec, in Veracruz, there's a line nobody can see. Coffee picked above it, about twelve hundred metres up, can carry Mexico's top grade. Coffee a few rows below it can't, and buyers pay less for it.† Why would the height of a farm set the grade of a bean?"

### 2. Up the slope (0:21–0:42, `S2_Slope`)
**Storyboard**
- **A:** *(Match cut in.)* The camera pulls back. The hillside becomes the upper flank of a mountain drawn as one grey outline rising from sea level (white inside, no fill), with a vertical altitude scale on the left (0–2,000 m, ticks every 200 m). The dashed line becomes the 1,200 m tick line.
- **B:** A small thermometer walks up the slope. At each 200 m tick its column drops a notch and the ice blue in it deepens. A label wipes in: ≈ 0.65 °C COOLER PER 100 m.
- **C:** Two pins: the port of Veracruz at sea level (≈ 25.5 °C†) and Coatepec at 1,200 m (≈ 19 °C†). A bracket between them reads ≈ 6 °C, with a small icon pair: a sun hat at the bottom, a light jacket at the top. Source line: `SOURCE: ICAO STANDARD ATMOSPHERE; ERA5 VIA OPEN-METEO, 2015–2024`.
- **D:** The thermometer settles at the Coatepec pin, its bulb glowing. *(Match cut out.)*

**VO:** "The first thing height does is chill the air. Every hundred metres up, it cools by a little more than half a degree. Drive from the port of Veracruz up to Coatepec and the average day is about six degrees cooler: the difference between a sun hat and a jacket."

### 3. The heat budget (0:42–1:08, `S3_HeatBudget`)
**Storyboard**
- **A:** *(Match cut in.)* The bulb grows at centre into a tall glass jar marked in degree-days, empty. A label: FLOWER → RIPE CHERRY ≈ 2,500 DEGREE-DAYS†.
- **B:** The jar splits into two jars on a shared horizontal calendar axis (months 0–12), both tagged A COLOMBIAN RESEARCH FARM, with grey-leaved shrub icons. The lower one (1,100 m, 23 °C) fills in thick pours, the upper one (1,900 m, 17 °C) in thin ones. A day counter runs.
- **C:** The lower jar fills and becomes a red cherry at about month 6. The upper jar is still half full. It fills and becomes a cherry at about month 11. A bracket between the cherries: ≈ 5 MONTHS. Source line: `SOURCE: CENICAFÉ`.
- **D:** The camera follows the upper cherry. *(Match cut out.)*

**VO:** "A coffee cherry ripens on a heat budget. From flower to harvest it needs a fixed amount of warmth, which agronomists count in degree-days. On a Colombian research farm at eleven hundred metres, averaging twenty-three degrees, the budget fills in about six months. At nineteen hundred metres and seventeen degrees, it takes closer to a year. Same plant. It just waits longer."

### 4. Inside the slow cherry (1:08–1:34, `S4_Seed`, the mechanism)
**Storyboard**
- **A:** *(Match cut in.)* The cherry scales up and splits into the ep. 1 cross-section, with the two cream seeds.
- **B:** The camera pushes into one seed until it is about 500 px tall, centred on white. Its inside is the shared cell honeycomb, in grey outlines. A small clock runs, and the cells fill one by one with small pale dots. Leader line: FOOD FOR A SEEDLING. The cell walls thicken as the clock runs. Second leader line: CELL WALLS.
- **C:** A seed from the fast cherry appears beside it at the same scale. Its honeycomb has fewer filled cells and thinner walls.
- **D:** Both seeds drop into a glass of water-cyan water. The slow seed sinks faster and the fast seed drifts. Label: DENSER. The slow seed then rotates to show its centre cut, which draws closed in a zigzag. Label: GRADERS' SIGN OF A HIGH-GROWN BEAN: A CLOSED, ZIGZAG CUT†. Source line: `SOURCE: CASSAMO ET AL. 2022; AGUILAR RUIZ 1999`.
- **E:** The camera pulls back onto the slow seed's outline. *(Match cut out.)*

**VO:** "Those extra months go into the seed. As it fills, it packs its cells with oil and sugar for a seedling it will never grow, and thickens the walls between them. Fill slowly and the cells pack tighter. The seed comes out denser, and Mexican graders say they can spot one by eye: the cut down its middle closes into a zigzag."

### 5. What the cold changes in the cup (1:34–1:58, `S5_Reunion`)
**Storyboard**
- **A:** *(Match cut in.)* The seed's outline flattens into Réunion. Sixteen dots pop onto it, shaded from ice blue (cold plots) to ink (warm plots).
- **B:** A chart builds to the right. Its x-axis is MEAN TEMPERATURE WHILE THE SEED FILLS. Two lines draw: ACIDITY falls as temperature rises, and EARTHY DEFECTS rises. The y-axis has no values, only the direction. Source line: `SOURCE: BERTRAND ET AL. 2012, FOOD CHEMISTRY`.
- **C:** A small bar pair below it: TOTAL SUGAR, cold plots against warm plots, at the same height. A highlighter swipe on "SAME". Source line: `SOURCE: JOËT ET AL. 2010`.
- **D:** Everything greys except the coldest dot. *(Match cut out.)*

**VO:** "On the island of Réunion, researchers grew arabica on sixteen plots and tasted the results. The weather that mattered most was the temperature while the seed was filling. Cooler plots tasted more acidic and more like fruit. Warmer plots built up compounds that taste of soil. The total sugar barely moved. The cold changes the mix, not the amount."

### 6. Density becomes a grade (1:58–2:22, `S6_Grades`)
**Storyboard**
- **A:** *(Match cut in.)* The cold dot becomes a neutral marker at the foot of a shared vertical altitude scale (0–2,000 m) that now spans the frame. Four country rails stand on it: Costa Rica, Guatemala, Colombia and Mexico. The marker climbs and stops at the first grade band, Costa Rica's SHB from ≈ 1,200 m†.
- **B:** Guatemala's SHB band lights from ≈ 1,350 m†. The labels STRICTLY HARD BEAN and STRICTLY HIGH GROWN type on beside the scale, with one leader line to the same band: TWO NAMES, ONE CLAIM. Colombia's rail stays empty, with a small sieve icon: GRADED BY BEAN SIZE†. Mexico's rail lights last. Source line: `SOURCE: ANACAFÉ; ICAFE; FNC`.
- **C:** The other rails slide off left. *(Match cut out on the Mexico rail.)*

**VO:** "The trade turned that density into a grade. Guatemala calls its top coffee Strictly Hard Bean, from about thirteen hundred and fifty metres. Costa Rica uses the same name from about twelve hundred. Other countries say Strictly High Grown. Either way the claim is the same: this seed grew slowly. Colombia skips the altimeter and sorts its beans through sieves."

### 7. Mexico's ladder (2:22–2:48, `S7_Ladder`)
**Storyboard**
- **A:** *(Match cut in.)* Mexico's rail widens into a ladder of four rungs on the same scale, named bottom to top: BUEN LAVADO, PRIMA LAVADO, ALTURA, ESTRICTAMENTE ALTURA. Only one boundary is labelled: the top line, ≈ 1,200 m. The other boundaries are drawn as plain guide-grey lines with no numbers.
- **B:** The document on screen slides in lower-left: a recreated table row from the cupping manual, typed flat, with a highlighter swipe on "Estrictamente Altura". Credit: `AGUILAR RUIZ, TOMANDO CAFÉ (1999), ONE COMMON SCALE`. A small tag under the word LAVADO: = WASHED.
- **C:** The ladder slides left. The ep. 1 Mexico map wipes in on the right with a Mexico-green dot on Coatepec and a dashed leader line from the dot to the top line of the ladder. *(Match cut out on the Coatepec dot.)*

**VO:** "Mexico's grades come from the same idea. On one common scale, written down in a cuppers' manual in 1999, the ladder has four rungs, from Buen Lavado on the low farms to Estrictamente Altura, from about twelve hundred metres. Lavado means washed, which is a story of its own. Coatepec sits right on the top line, and that's where the metres start to mislead."

### 8. Same rung, different cold (2:48–3:30, `S8_SameRung`, the turn)
**Storyboard**
- **A:** *(Match cut in.)* The camera pulls out from the Coatepec dot until a second dot enters frame: the SOCONUSCO, CHIAPAS. Both dots carry a tag: 1,200 m, ESTRICTAMENTE ALTURA.
- **B:** The map wipes off. Both dots stay fixed while two mountain profiles draw under them as grey outline lines on one shared altitude scale, VERACRUZ on the left and CHIAPAS on the right, each with a thermometer pinned at 1,200 m: COATEPEC ≈ 19 °C and SOCONUSCO ≈ 20 °C†. An ice-blue 19 °C isotherm draws from the Coatepec pin. On the Chiapas profile it meets the slope higher, at ≈ 1,400 m†. Bracket: ≈ 200 m. Source line: `SOURCE: ERA5 VIA OPEN-METEO, 2015–2024`.
- **C:** Two small heat jars from scene 3 pop under the pins and fill side by side. The Chiapas jar reaches 2,500 first. Bracket on the calendar: ≈ 2 WEEKS SOONER†.
- **D:** The Chiapas profile slides off. On the Coatepec profile, a sage shade-tree crown draws over the shrubs at 1,200 m. The jar under it fills more slowly and its cherry arrives later on the calendar. Bracket: UP TO ≈ 1 MONTH LATER, SAME SPOT†. Source line: `SOURCE: VAAST ET AL. 2006 (COSTA RICA)`.
- **E:** The tree and jar clear, leaving the Coatepec profile with the 19 °C isotherm resting on the 1,200 m line. *(Match cut out.)*

**VO:** "The bean never reads an altimeter. It only feels the temperature. Take two farms on that top line, both at twelve hundred metres: one above Coatepec, one in the Soconusco, in Chiapas. In one weather record, the Chiapas farm runs about a degree warmer, and its cherries fill their budget a couple of weeks sooner. To feel Coatepec's cold, it would have to sit about two hundred metres higher. And a tree can do a mountain's job. In a Costa Rican trial, shade delayed ripening by up to a month, without the farm moving at all. The grade counts metres. It can't see either of those."

### 9. The line stays, the cold moves (3:30–3:58, `S9_Close`)
**Storyboard**
- **A:** *(Match cut in.)* The profile is the S1 hillside again, at the same size and position, with the dashed grade line and the shrubs' grade tags back on: ESTRICTAMENTE ALTURA above, ALTURA below. The ice-blue 19 °C isotherm lies on top of the dashed line.
- **B:** A label: + 1 °C. The isotherm lifts about 150 m up the hillside, past several rows of shrubs. A bracket shows the climb, with a comparison: ≈ THE HEIGHT OF A 45-STOREY TOWER†. The dashed grade line and its tags stay where they were. Source line: `SOURCE: ICAO STANDARD ATMOSPHERE (0.65 °C / 100 m)`. Then the end card types on, **Why Mountain Coffee Tastes Different**, with a highlighter swipe, and holds for 2 s.

**VO:** "Metres don't travel well. What a grade line really marks is how long the seed had to fill, and that's set by cold. Height is only the usual way to find it. And the cold is moving. Warm the air by one degree, and nineteen degrees climbs about a hundred and fifty metres up this hillside. The line stays where it is, and so does the name on the sacks."

## Notes for the build

- **One shared altitude scale.** Scenes 2, 6, 7 and 8 use the same vertical scale (0–2,000 m, same pixels per metre, same screen x), defined once in the generator so ticks match across cuts. The S1/S9 hillside is the 1,000–1,500 m section of the S2 mountain at a larger scale. Build it once and scale it, so the 1→2 pull-back and the 8→9 return land on the same geometry.
- **Heat jars (S3, S8)** are rectangles whose fill height is a slider expression (`degree_days / 2500`). The calendar axis is shared. Cherries pop on the frames for the computed months.
- **Seed (S4)** uses the shared cell honeycomb (`coffee_common.py`). Filled-cell count and wall stroke width are driven by one slider, so slow and fast seeds are the same asset at two slider values. The v1 growth rings are gone: seeds don't have them.
- **The zigzag cut (S4)** is a trim-path draw on one shape path in the seed. The fast seed's cut stays straight and open.
- **The S8 isotherm** bends up between the two profiles so the eye reads "same temperature, different height". Use one path with two vertices per profile. The v1 sideways thermometer (old S9) is cut, so the dual-scale problem in the visual notes no longer arises.
- **"Everything greys except X" (S5)** is one white rectangle at 75 % opacity above the dots and below the kept dot, per the season rule.
- **Colours:** ice blue only for temperature. Water cyan only for the S4 water. Mexico green on Mexican dots and Mexican leaves. Grey leaves on the Colombian research farm. Arabica red only on cherries. Canopy sage on the one S8 shade tree, which is the same idea as ep. 4.
- **White-frame pass:** the S1/S9 hillside and the S2 and S8 mountains are single outline lines on white instead of filled ground; the S4 seed stops at about 500 px instead of filling the frame.
- **Fonts:** Chonburi-Regular, Georgia-Italic, ArialMT and Arial-BoldMT.

**Review decisions (v2):**
- **Turn rebuilt on comparable data.** Both reviewers flagged the v1 Coatepec-vs-Colombia gap (≈ 450 m), which mixed town-station normals with Cenicafé farm plots. I re-derived the temperatures from one dataset: ERA5 reanalysis through Open-Meteo, 2015–2024, elevation-corrected. On that basis the Colombian gap shrinks to ≈ 180 m (Naranjal, Caldas: 19 °C at ≈ 1,380 m), below the story editor's 200 m threshold. So the Colombia comparison is dropped as the turn. The same dataset puts the Soconusco at 1,200 m ≈ 1.2 °C warmer than Coatepec, reaching Coatepec's 19 °C at ≈ 1,375 m. Its degree-day budget (from 1 April, base 10 °C) fills ≈ 15–24 days sooner. That's a smaller gap, but it's measured the same way at both ends, and both farms are Mexican and on the same rung. The shade result (Vaast 2006) carries the rest of the turn. Reanalysis is coarse in mountains, so confirm with WorldClim (see facts).
- **Grade bands.** The story editor wanted no rung boundaries on screen. The fact checker accepted "on one common scale" with an Aguilar Ruiz credit. I followed both: only the ≈ 1,200 m top line is labelled, and the other boundaries are unnumbered lines. The VO speaks only the top line.
- **The sack is gone from the cold open.** The fact checker noted that Mexican sacks carry the grade name, not metres, and rule 10 asks for cold opens that aren't a product on a table. The open is now the grade line on the hillside, and the close returns to it. The S9 last line keeps "the name on the sacks" as the only sack reference.
- **Old S9 (sideways thermometer) is cut** and its point folded into S8/S9. **Old S10 (warming) is merged into the close** and tied to the grade line, as the story editor proposed. The visual director's alternative (a readable three-rail dual scale for old S9) wasn't needed once the scene was cut.
- **"Not X but Y":** the only one is S5's "The cold changes the mix, not the amount."
- **Rejected:** the story editor's suggestion to swap Cenicafé for INIFAP or Veracruz phenology data in S3. I couldn't find altitude-resolved Mexican phenology, so S3 says "a Colombian research farm" once, as the note's fallback allows.

## Facts to check (†)

- **"Buyers pay less" for the grade below the line.** Grade premiums for Estrictamente Altura/SHG over Altura are standard in importer price lists but vary by year. Confirm with a dated Mexican offer sheet (e.g. an importer's Mexico Altura vs SHG listing) or AMECAFÉ. If no clear premium can be shown, change the line to "and it's sold under a lower grade."
- **Lapse rate ≈ 0.65 °C per 100 m.** ICAO standard atmosphere, 6.5 °C/km. Real slopes vary, so the VO says "a little more than half a degree."
- **Port of Veracruz ≈ 25.5 °C; Coatepec ≈ 19 °C mean annual.** ERA5 via Open-Meteo, 2015–2024, elevation-corrected (port 25.6 °C at 10 m; Coatepec 18.9–19.0 °C at 1,200 m). This agrees with published Coatepec normals (19–19.2 °C, INEGI/EcuRed). Confirm with SMN (CONAGUA) station normals.
- **≈ 2,500 degree-days (base 10 °C) from first flowering to harvest.** Cenicafé bulletin. The six-month and near-a-year figures are my arithmetic (≈ 190 and ≈ 350 days). Confirm with Cenicafé phenology for the 1,100 m and 1,900 m stations.
- **1,100 m = 23.2 °C; 1,900 m = 17.1 °C.** Cenicafé three-altitude flowering study. Confirm station names and that it is the same study.
- **Density rises with altitude.** Cassamo et al. 2022, *Agronomy* 12: 2540 (Mozambique, 650–935 m). No g/mL is shown.
- **Closed, zigzag centre cut on high-grown beans.** A grader's description (Aguilar Ruiz 1999, via UV-IIESCA 2004: "hendidura … cerrada y torcida en forma de zigzag", for 1,200–1,400 m). It is attributed to graders on screen.
- **Réunion: 16 plots, temperature during seed fill mattered most.** Bertrand et al. 2012, *Food Chemistry* 135: 2575–2583.
- **Total sugars not affected by climate.** Joët et al. 2010, *Food Chemistry* 118: 693–701 (abstract).
- **Guatemala SHB ≈ 1,350 m (Anacafé: 4,500 ft ≈ 1,370 m); Costa Rica SHB ≈ 1,200 m.** Confirmed in substance (fact check). Keep "about".
- **Colombia grades by screen size, not altitude** (Supremo, Excelso). Confirm with the FNC export standard.
- **Mexican ladder: four washed-arabica rungs, top line ≈ 1,200 m.** Aguilar Ruiz, *Tomando Café, Manual del Catador* (1999), pp. 42–43, via UV-IIESCA 2004. It is credited as "one common scale". NMX-F-551 has been cancelled and replaced by NMX-F-597-SCFI-2016, whose altitude clauses (if any) weren't read. Importers give other cutoffs (SHG > 1,200 m, > 1,350 m, ≈ 1,700 m). Read NMX-F-597 before lock. The v1 inference "Chiapas grows most of its coffee in the top two bands" is cut.
- **Coatepec ≈ 1,200 m.** INEGI (1,190–1,250 m).
- **Soconusco at 1,200 m ≈ 20 °C, ≈ 1 °C warmer than Coatepec; 19 °C at ≈ 1,400 m; budget fills ≈ 2 weeks sooner.** My computation from ERA5 via Open-Meteo, 2015–2024. Points used: Coatepec 19.45° N 96.96° W, Soconusco 15.15° N 92.20° W, both at elevation 1,200 m. The Soconusco reaches 19 °C at ≈ 1,375 m. Days to 2,500 DD from 1 April average 255–258 at Coatepec and 234–243 at the Soconusco across two nearby points each. Reanalysis at 0.25° resolution in mountains is approximate. Confirm with WorldClim 2.1 (1 km) at named farms, and with a farm station if one is available (e.g. Finca Irlanda or Finca Hamburgo, both Soconusco). This is the fact the turn now rests on.
- **Shade delayed ripening by up to ≈ 1 month and gave bigger beans.** Vaast et al. 2006, *J. Sci. Food Agric.* 86: 197–204 (45 % shade, Costa Rica central valley, Costa Rica 95). "Up to a month" comes from a summary of the abstract; confirm in the paper.
- **+1 °C ≈ 150 m up the slope; ≈ a 45-storey tower.** Arithmetic from the lapse rate (1 ÷ 0.65 × 100 ≈ 154 m) and ≈ 3.3 m per storey.
