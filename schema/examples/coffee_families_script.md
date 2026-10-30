# The Coffee Family Tree: Script and Storyboard

**Status:** draft, waiting for approval. No JSON is generated yet.

**Format:** about 3:05, 1920×1080, 30 fps, English VO (to be recorded; timings assume about 150 words per minute)
**Audience:** curious general viewers who drink coffee but have never thought about where the plant comes from
**Build (after approval):** `coffee_families.py` generates `coffee_families.json` and then `json2jsx`. There is one precomp per scene inside `Coffee_Families`.

## Logline

Every cup comes from a seed, but not always the same plant. We zoom out to the whole *Coffea* genus, compare the two species that matter (arabica and robusta), meet the smaller ones, then follow arabica from Ethiopia to Yemen, around the world, and into the mountains of Mexico. There its family tree grows a branch with a twist: to survive leaf rust, Mexican arabica borrowed genes from robusta.

## Look and feel (Vox-style minimal documentary)

| | |
| :--- | :--- |
| Background | Pure white `#FFFFFF` in every scene. No colour fills behind scenes and no gradients |
| Ink | Near-black `#161616` for type and 3 px outlines. Light grey `#E6E6E6` for guide lines, grids and the "inactive" state |
| Colour coding | One colour per family, and it never changes: **Arabica** red `#D9432F` (the ripe cherry), **Robusta** brown `#7A5440`, **smaller species** slate `#6F8796`, **Mexico** green `#2F7D5A`, **roya (leaf rust)** orange `#E8892B`. Highlighter yellow `#FFD84D` is used only for the marker swipe behind key words |
| Type | Georgia Bold for headlines and numbers, *Georgia Italic* for scientific names (*Coffea arabica*), and Arial Bold in small tracked caps for labels and leader-line callouts |
| Graphic language | Flat cut-paper shapes with one soft drop shadow (8 % black, 6 px blur, offset downward), thin leader lines ending in dots, family-tree connectors with rounded elbows, and simplified maps drawn as flat light-grey landmasses with no borders, except Mexico, which gets state outlines in scene 7 |
| Motion | Snappy "leave fast, land soft" easing (out 85 / in 10), lines that draw on with trim paths, labels that type on or wipe in under a highlighter swipe, and a slow 3 % push-in on every scene through a camera null. Nothing bounces. It should feel calm and editorial |
| Texture | A 2 % grain adjustment layer over the master comp, so the white still reads as paper |
| Transitions | **Match cuts only.** Each scene ends on a shape whose position, size and colour are exactly where the next scene's first shape begins, so the cut is invisible. There are no wipes, fades or whip pans. See the match-cut chain below |

## Match-cut chain

| Cut | Out of | Into | Shared element |
| :--- | :--- | :--- | :--- |
| 1→2 | The red cherry, centred, 220 px | The arabica dot on the map of Africa | A red circle, which shrinks into place as the camera pulls out |
| 2→3 | The two highlighted dots (red and brown) | The two column headers, a red circle on the left and a brown one on the right | Two circles that slide apart and grow |
| 3→4 | The world-production bar's last grey sliver (<2 %) | The bar that becomes the timeline of the four smaller species | A thin grey bar at the same height |
| 4→5 | The *eugenioides* card's slate circle | The left parent node of arabica's family tree | A slate circle in the same place |
| 5→6 | Arabica's node splitting into two branch lines | The two migration routes on the world map | The same red line, which keeps drawing |
| 6→7 | The Typica route's arrowhead landing on Veracruz | The Veracruz dot on the map of Mexico | A red dot. The world map is swapped for the Mexico map at the same scale, then the camera pushes in |
| 7→8 | The four state dots | The root nodes of the Mexican variety tree | The dots lift off the map into tree positions |
| 8→9 | Garnica's leaf icon | A large leaf that roya spots spread across | A leaf shape that scales up to fill the frame |
| 9→10 | The Oro Azteca node, a red circle | A red cherry, the same as in scene 1 | A red circle, which closes the loop with the opening shot |

## Script and storyboard

Timecodes are for the master comp.

### 1. Hook (0:00–0:10, `S1_Seed`)
**Storyboard**
- **A:** White frame. A single red cherry draws on as an outline, then fills. Its stem and leaf pop in on the right.
- **B:** The cherry splits down the middle like a cross-section and reveals two pale seeds, flat sides facing each other. A label wipes in: COFFEE SEED.
- **C:** The seeds slide back together, the cherry closes, and the leaf falls away. Only the red circle is left, centred. *(Match cut out.)*

**VO:** "This is a coffee cherry. Inside are two seeds, and every cup you've ever had started as one of them. But not every cup comes from the same plant."

### 2. The genus (0:10–0:24, `S2_Genus`)
**Storyboard**
- **A:** *(Match cut in.)* The red circle shrinks to a 14 px dot as the camera pulls out, revealing a light-grey map of Africa, Madagascar, India and Southeast Asia.
- **B:** About 120 grey dots pop on in quick clusters across the tropics. A counter in Georgia Bold ticks up to **120+**. The headline *Coffea* types on in italics, with a highlighter swipe.
- **C:** Every dot fades to light grey except two: the red one in the Ethiopian highlands and a brown one in Central and West Africa. *(Match cut out.)*

**VO:** "Coffee is a genus, *Coffea*, with more than a hundred and twenty wild species scattered across Africa, Madagascar and Asia. But almost all the coffee we drink comes from just two of them."

### 3. Arabica vs. robusta (0:24–0:50, `S3_TwoSpecies`)
**Storyboard**
- **A:** *(Match cut in.)* The two dots slide apart and grow into 160 px circles at the top of two columns: *Coffea canephora* ("robusta") in brown on the left and *Coffea arabica* in red on the right. A thin grey divider draws down the middle.
- **B:** Comparison rows build one at a time, mirrored across the divider, each with a small icon:
  - **Altitude:** a mountain silhouette with a marker. Robusta sits low (0–800 m) and arabica high (about 900–2,000 m).
  - **Caffeine:** two vertical bars. Robusta is about 2.2–2.7 % and arabica about 1.2–1.5 %, so the brown bar is roughly double the red one.
  - **Chromosomes:** small ticks in rows, 22 against 44.
  - **Flavour:** two word chips each. Robusta is *bitter, earthy* and arabica is *sweet, acidic*.
  - **Bean shape:** a round robusta bean with a straight crease next to an oval arabica bean with an S-curve crease.
- **C:** The columns collapse into one horizontal **world production** bar across the bottom third: red about 60 %, brown about 38 %, and a thin grey sliver at the end. A label with a leader line points to the sliver: <2 %. *(Match cut out on the sliver.)*

**VO:** "*Coffea canephora*, better known as robusta, lives up to its name. It grows low and hot, shrugs off pests, and carries about twice the caffeine, which makes it bitter. *Coffea arabica* is fussier. It wants altitude, cool nights and shade, and in return it's sweeter, brighter and more aromatic. Arabica is about sixty percent of the world's coffee. Robusta is almost all the rest."

### 4. The smaller families (0:50–1:10, `S4_Others`)
**Storyboard**
- **A:** *(Match cut in.)* The grey sliver stretches across the frame into a horizontal rail. Four slate circles drop onto it at even spacing.
- **B:** Each circle expands into a minimal card in turn. On the card is an icon of the plant or bean, the scientific name in italics, the origin, and one trait:
  - *C. liberica*, from Liberia. A tree up to 17 m tall with big, asymmetric beans that taste smoky and fruity, like jackfruit. The bean draws at twice the size of an arabica bean beside it.
  - *C. liberica* var. *dewevrei* ("excelsa"), grown in Southeast Asia. Tart and fruity. A small note reads: *reclassified as liberica in 2006*.
  - *C. stenophylla*, from Sierra Leone. Rediscovered in 2018 after decades of being lost. Tastes like arabica and grows in heat about 6 °C warmer. A thermometer icon rises.
  - *C. eugenioides*, from the East African highlands. Low in caffeine and mild. The last card gets a highlighter swipe on "arabica's mother".
- **C:** The first three cards slide off to the left. The *eugenioides* card shrinks back to its slate circle, which moves to the left third of the frame. *(Match cut out.)*

**VO:** "That last sliver belongs to the smaller species. Liberica, a towering tree with big, smoky beans. Excelsa, tart and fruity, grown across Southeast Asia. Stenophylla, a species from Sierra Leone that was lost for decades, tastes like arabica, and handles the heat. And eugenioides, a mild highland plant that turns out to be arabica's mother."

### 5. Where arabica comes from (1:10–1:24, `S5_Origin`)
**Storyboard**
- **A:** *(Match cut in.)* The slate circle (eugenioides) sits on the left. The brown circle (canephora) slides in from the right. Tree connectors draw down from both and meet below.
- **B:** A red circle (arabica) pops at the meeting point. Small chromosome ticks above each parent (11 pairs + 11 pairs) slide down and stack into 22 pairs inside arabica. A label reads: 2 GENOMES → 1 SPECIES.
- **C:** A tiny map inset of Ethiopia and Yemen wipes in. A dashed line crosses the Red Sea and the port of Mocha is labelled. Then the red node pulses and **two lines branch downward** from it. *(Match cut out.)*

**VO:** "Arabica is a natural hybrid of eugenioides and canephora, robusta itself, formed long before anyone drank coffee. It kept both sets of chromosomes, learned to pollinate itself, and grew wild in the forests of Ethiopia until people carried it across the Red Sea to Yemen."

### 6. Two lines: Typica and Bourbon (1:24–1:44, `S6_Routes`)
**Storyboard**
- **A:** *(Match cut in.)* The two branch lines keep drawing as the camera pulls out to a grey world map, centred on Yemen. They are labelled TYPICA and BOURBON in small caps.
- **B:** The **Typica** route draws east and then west, with a dot and a year at each stop: India (1670), Java (1696), Amsterdam (1706), Paris (1714), Martinique (around 1720), and then fanning out across the Caribbean.
- **C:** The **Bourbon** route draws south to Bourbon Island, now Réunion (1715), then on to Brazil and East Africa. A side note: *nearly all arabica descends from these two lines, so it has very little genetic diversity* (a highlighter swipe on "very little").
- **D:** One Typica branch arcs from the Caribbean towards the Gulf of Mexico, and its arrowhead lands on Veracruz. *(Match cut out on the dot.)*

**VO:** "From Yemen, almost every arabica on Earth descends from two lines. Typica travelled east to India and Java, then to Amsterdam, Paris and the Caribbean. Bourbon went south to the island of Bourbon, today Réunion, and on to Brazil and East Africa. Such a narrow family would matter later."

### 7. Arrival in Mexico (1:44–1:58, `S7_Mexico`)
**Storyboard**
- **A:** *(Match cut in.)* The Veracruz dot stays fixed while the world map is replaced, at the same scale, by a detailed silhouette of Mexico. The camera pushes in. A label reads VERACRUZ, LATE 1700s.
- **B:** The coffee states fill in green, each with a dot and a label: Chiapas, Veracruz, Puebla and Oaxaca (with Guerrero, Hidalgo and San Luis Potosí lighter). A contour-line icon of a mountain rises next to Chiapas with a label: 900–1,700 m.
- **C:** A small stat chip shows MOSTLY ARABICA. Then the four main state dots lift off the map and rise into a row. *(Match cut out.)*

**VO:** "In the late seventeen hundreds, Typica reached Veracruz from the Caribbean. Today Mexico grows coffee in the mountains of Chiapas, Veracruz, Puebla and Oaxaca, and most of it is arabica."

### 8. Mexico's arabica family tree (1:58–2:30, `S8_Varieties`, the centrepiece)
**Storyboard.** A full-frame family tree builds from the top down. The camera tilts down it as it grows. Each variety is a node made of a circle, a name in Georgia Bold, a one-line trait in Arial, and a small icon such as plant height, bean size or a leaf.
- **A:** *(Match cut in.)* The dots settle into two root nodes, **Typica** and **Bourbon** (the other dots merge in).
- **B:** Under Typica: **Typica / Criollo** (old farms, tall and elegant, low yield), **Pluma Hidalgo** (a selection from Oaxaca), and **Maragogype** (a mutation with giant "elephant" beans; the bean icon scales up to twice the size).
- **C:** Under Bourbon: **Caturra** (a dwarf mutation, so it can be planted densely). A small plant-height icon shrinks.
- **D:** A cross connector between Typica and Bourbon gives **Mundo Novo** (tall and productive). Then a cross between Mundo Novo and Caturra gives **Catuaí** and **Garnica**, which gets a green MADE IN MEXICO tag and a highlighter swipe.
- **E:** The camera settles on Garnica. Its leaf icon is centred. *(Match cut out.)*

**VO:** "Mexico's farms are a living family tree. Typica, known here as *criollo*, still grows on old farms. From it came Pluma Hidalgo, selected in Oaxaca, and Maragogype, a mutation with giant beans. Bourbon gave Caturra, a compact dwarf you can plant densely. Cross Typica with Bourbon and you get Mundo Novo, tall and productive. Cross Mundo Novo with Caturra and you get Catuaí, and, bred right here in Mexico, Garnica."

### 9. La roya and the rescue (2:30–2:54, `S9_Roya`)
**Storyboard**
- **A:** *(Match cut in.)* The leaf scales up to fill most of the frame. A label reads 2012. Orange rust spots grow and spread across it (circles that scale up with a slight offset). The leaf greys out.
- **B:** A small line chart draws in the corner, showing Mexico's harvest falling by about half over a few seasons. A label reads *Hemileia vastatrix*, "la roya". The leaf shrinks back into a node.
- **C:** The rescue builds as a new family tree. On the left is the island of **Timor**, a tiny map, where a red (arabica) circle and a brown (robusta) circle meet to make the **Timor Hybrid**. Lines run from it to the **Catimor** and **Sarchimor** groups, and then to the varieties grown in Mexico: **Costa Rica 95**, **Oro Azteca** (bred in Mexico) and **Marsellesa**. The brown line is kept visible all the way down, so robusta's genes can be seen reaching the bottom of the tree.
- **D:** The camera pushes into the Oro Azteca node, a red circle. The rest of the tree fades to light grey and the node centres. *(Match cut out.)*

**VO:** "But a narrow family has a weak spot. In 2012, coffee leaf rust, *la roya*, swept through Central America and into Mexico, and harvests fell by around half. The rescue came from an old relative. On the island of Timor, arabica had crossed with robusta. Its rust-resistant descendants, Catimors and Sarchimors like Costa Rica 95, Oro Azteca and Marsellesa, now cover much of Mexico's hillsides."

### 10. Close (2:54–3:05, `S10_Close`)
**Storyboard**
- **A:** *(Match cut in.)* The red circle becomes the cherry from scene 1: the stem and leaf return, in the same position and at the same size, as a bookend.
- **B:** The cherry opens again to show the two seeds. This time a tiny brown thread runs through one of them, a visual hint of the robusta in its ancestry.
- **C:** The end card types on: **The Coffee Family Tree**, with a small *Coffea* subtitle and a highlighter swipe. It holds for 2 s.

**VO:** "So your next cup of Mexican coffee is almost certainly arabica, with a little robusta hiding in its family tree."

## Notes for the build

- **Scene precomps** go on the master comp in order and butt-cut. There are no overlaps, because every transition is a cut. To retime to the recorded VO, drag the precomp layers.
- **Match-cut discipline:** each scene's last frame and the next scene's first frame share the matched element's exact position, size and colour. The generator defines these "handoff" values once as constants and both scenes read them, so retiming a scene can never break a match.
- **Maps:** simplified hand-drawn polygons (a low-detail world map and a Mexico outline with state shapes for the states named), kept in the generator as point lists. They are deliberately stylised, not cartographic.
- **Loops** (the drifting cherry, the pulsing nodes) are expressions, not keyframes.
- **Fonts:** Georgia, Georgia-Bold, Georgia-Italic, ArialMT and Arial-BoldMT.

## Facts to double-check before final

- The species count (about 130 described *Coffea* species. Using "more than 120" is the safe wording).
- The production split (arabica about 56–60 %, robusta about 40 %, others under 2 %). This varies by year.
- The roya impact on Mexico (USDA figures show a drop from about 4.3 M to about 2.3 M bags between 2012/13 and 2016/17).
- The Typica route dates, which are traditional and approximate.
