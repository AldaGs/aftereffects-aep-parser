# Visual direction notes: episodes 2–10 (draft v1 storyboards)

Reviewer: visual direction. Scope: storyboards, match cuts, colour, reuse and buildability. Facts and prose are out of scope here. Scene names are the precomp names from each script.

## 1. Season colour table

As drafted, the nine scripts add **12 colours** to the 6 channel colours. Five of them clash.

| Colour | Hex | Idea | Used in (drafts) | Problem | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Arabica red | `#D9432F` | arabica (cherry, dots, nodes) | all | olla clay (10) sits next to it; ep. 5 "red honey" chip could be drawn in it | **Keep.** Honey grades get dried-mucilage tones, never `ARA` |
| Robusta brown | `#7A5440` | robusta | 1, 2, 7, 10 | ep. 8 roast-ramp brown and melanoidins; ep. 10 olla clay and "ink-brown" cups | **Keep.** Nothing else in the season is brown except the roast ramp, which only appears in eps. 8 and 10 S5 |
| Slate | `#6F8796` | smaller species | 1 | none | **Keep** |
| Mexico green | `#2F7D5A` | Mexico | all | ep. 1 already draws the **leaf** in `MX`, so green foliage reads as "Mexico". Ep. 4 adds unlisted "dark-green shrubs". Ep. 9 puts the *global* Fairtrade floor in it | **Keep.** Foliage rule below |
| Roya orange | `#E8892B` | leaf rust | 1, 2, 4 | ep. 2 7→8 turns the tea route orange; olla clay is close | **Keep** |
| Highlighter | `#FFD84D` | marker swipe only | all | none | **Keep** |
| Tea green | `#8DB33A` | Sri Lanka / tea | 2, 10 | never shares an episode with sage | **Keep** |
| Ice blue | `#A7CFEA` | temperature | 3 | ep. 8 gives temperature a second colour (heat purple); thermometers in eps. 6 S4 and 10 S5 have no colour assigned | **Keep** for climate temperature. Process heat (roasters, extraction columns) is drawn in ink |
| Canopy sage | `#8FA88A` | shade trees, litter | 4 | none | **Keep** |
| Ferment magenta | `#B4457F` | microbes and their acid | 5 | aroma pink `#D65D8F` (ep. 8) is the same hue family; ep. 7 draws its gut bacteria in ink | **Keep.** Ep. 7 bacteria become magenta |
| Water cyan (drafted as "extract cyan") | `#4FB3C8` | water, incl. green-coffee extract | 5, 6 | water also appears uncoloured in 2 S3, 3 S4, 4 S5 and 10 S5 | **Keep**, renamed `WATER`, and used wherever water is drawn |
| Caffeine blue | `#3B73B9` | caffeine | 6, 7, 8 | instant blue `#3F6FB5` is indistinguishable from it | **Keep** |
| Pest violet | `#6C4F9E` | insect pests | 7 | heat purple `#7A4FA0` and C-price violet `#6A4FB3` are a near-match: three violets for three ideas | **Keep.** This is the season's only violet |
| Heat purple | `#7A4FA0` | roast temperature | 8 | the violet clash, and a second colour for temperature | **Drop.** Draw the roast curve in ink. The dot riding it is the bean itself, in its roast-ramp colour |
| Aroma pink | `#D65D8F` | aroma molecules | 8 | magenta clash | **Drop.** Aroma molecules are ink outlines. In S8 the cloud is guide grey, the 30 survivors are ink, and 2-furfurylthiol gets a highlighter swipe |
| C-price violet | `#6A4FB3` | futures price | 9 | violet clash | **Drop.** The C price is an ink line and an ink sliver. It still reads against the green floor and the grey ICA corridor |
| Instant blue | `#3F6FB5` | soluble coffee | 10 | the same colour as caffeine blue | **Drop.** Instant is mid grey `#8C8C8C` with an ink outline. This ties it to the grey heap of export rejects in S3, which is the episode's argument |
| Olla clay | `#B8613A` | café de olla | 10 | lands between arabica red, robusta brown and roya orange, and S6 (brown) and S7 (clay) are back-to-back | **Drop.** The pot is an ink outline with an object fill of `SEED_LINE #C9A56E` |

### Proposed final palette

- **Channel (6, unchanged):** arabica red `#D9432F`, robusta brown `#7A5440`, slate `#6F8796`, Mexico green `#2F7D5A`, roya orange `#E8892B`, highlighter `#FFD84D`.
- **Season additions (7, one idea each, fixed from first use):** tea green `#8DB33A` (Sri Lanka/tea), ice blue `#A7CFEA` (climate temperature), canopy sage `#8FA88A` (shade trees), ferment magenta `#B4457F` (microbes and their acid), water cyan `#4FB3C8` (water), caffeine blue `#3B73B9` (caffeine), pest violet `#6C4F9E` (insect pests).
- **Neutrals and object colours (not ideas, take them from `coffee_families.py`):** ink `#161616`, line `#E2E2E2`, land `#ECECEC`, label grey `#8C8C8C`, seed `#F1E1BE` / `#C9A56E`, pulp `#F7CDBE`, stem `#5B4A2E`, mucilage white with an ink outline, sugar as a white hexagon with an ink outline. The ep. 8 roast ramp gets five fixed stops, for example `#F1E1BE → #E3C77A → #B9814A → #6B4226 → #2B1D16`. Keep robusta out of any frame that shows the ramp.
- **New colours per episode after this change:** ep2 1, ep3 1, ep4 1, ep5 1–2 (magenta, plus cyan if it airs before ep. 6), ep6 1–2, ep7 1, ep8 0, ep9 0, ep10 0.

### Season-wide rules that come out of this

- **Foliage.** The ep. 1 leaf is `MX` green. Keep it green only on Mexican plants. Non-Mexican leaves get an ink outline and a `#ECECEC` fill: the Ceylon leaf in ep. 2 S1/S3/S4, the Ethiopian understorey in ep. 4 S2 and the generic branch in ep. 7 S1/S5. Rust spots read better on grey anyway.
- **The green seed is ep. 1's cream `SEED`.** Eps. 6 and 8 call it "pale green". Use the ep. 1 asset as it is.
- **Colour changes at a cut** happen only after the cut frame, and only when the idea really changes. Ep. 2 1→2 (tea green → red as the year rolls back) is a good one. Ep. 7 8→9 (robusta → pest) is a bad one.
- **"Everything greys except X"** beats appear in 2 S9, 3 S7, 6 S8, 8 S8, 9 S8 and others. Opacity isn't inherited through parenting, so build these as one white rectangle at 75 % opacity, placed above the group and below the kept element. Don't fade every layer.

## 2. Shared module (`schema/examples/coffee_common.py`)

Pull these out of `coffee_families.py` before ep. 2 is built. Each one is used by three or more episodes.

| Asset | Source | Used by |
| :--- | :--- | :--- |
| Palette, `K`/`SNAP` easing, `paper()`, `leader()`, `marker()`, `wipe_text()`, `caps()` | ep. 1 | all |
| Map rig: world map, Mexico with states, `screen()`, push/pull null. New polygons go in the geo JSON: Sri Lanka, Réunion, the Mexico City outline, and Brazil and Indonesia insets | ep. 1 + new | 2, 3, 4, 5, 6, 7, 8, 9, 10 |
| Chart rig: axes, ticks, a line with trim driven by year, a ghost line, the lower-left `SOURCE:` line | new | 2, 3, 4, 5, 6, 7, 8, 9, 10 |
| Numbered step rail (1–N, fills on cue) | new | 2, 6, 8, 9, 10 |
| Composition bar and 100-cell unit strip | new | 2, 6, 8, 9, 10 |
| Cherry and cross-section, with ep. 5's inner layers added once (mucilage, parchment, silverskin) | ep. 1 + ep. 5 | 3, 5, 6, 7, 8, 9, 10 |
| Seed **cell honeycomb** (dense vs sparse) | new | 3 S4, 8 S2–S5 |
| Leaf with a rust-spot matte | ep. 1 | 2, 4, 7 |
| Molecule kit: ink ball-and-stick, ring, methyl tab, sugar hexagon and pentagon | new | 6, 7, 8 |
| Document recreation: page, typed lines, one highlighter swipe, credit lower-left | new | 2, 4, 5, 6, 7, 8, 9, 10 |
| Sack (60 kg unit), sack stack, generic bag outline | new | 2, 3, 4, 6, 8, 9, 10 |
| Gauge or thermometer: vertical bar plus needle dial (pH, pressure) | new | 3, 5, 6, 8, 10 |
| Family-tree nodes and connectors | ep. 1 | 2, 7 |
| Farm plot with football pitches, coyote truck, factory outline | ep. 2 / 9 | 2, 9, 10 |
| Altitude scale and mountain profile | ep. 1 contour icon | 3, 7 |

**Repeater limit (affects four scripts).** A repeater can't vary fill colour, randomise position or change style per copy. Generate per-copy shapes in Python as groups inside one or a few shape layers. Use a track matte when only one region has to change.

## 3. Episodes

### Ep. 2: The Fungus That Turned Ceylon Into a Tea Country

**Must fix**
1. **Cut 4→5 (`S4_Grid` → `S5_Collapse`).** The dead grey grid becomes the healthy 1870 export bar, which gets the meaning backwards. A 600 × 120 bar also doesn't fit a line chart's first slot. Instead, compress the grey block into the chart's grey x-axis baseline, and draw the red line from 1870 on it.
2. **Cut 7→8 (`S7_Switch` → `S8_Atlantic`).** The tea route (Ceylon→London) turns orange and becomes an Africa→Brazil arc, so both the endpoints and the idea jump. End S7 on the Ceylon dot. In S8, draw the rust's own dotted route out of that dot, with a slow pull-out: Ceylon 1869 → India → East Africa → West Africa → Brazil 1970 → Chiapas 1981. It's a genuine cut and a real map move.
3. **`S8_Atlantic` B carries three data graphics in one beat** (area bar, 37 worker icons, harvest bars), plus a push-in. Keep the ep. 1 harvest bars and the area bar, cut the worker icons (say the jobs figure in VO only), and give each its own beat.
4. **`S4_Grid` C:** the orange wave can't be built as "a repeater with an expression on fill colour". Use the grid as generated groups in one layer, an orange copy matted by a growing blob driven from the wind origin, and a grey copy with a lagged matte. That's three layers.

**Could improve**
- `S1_Tin` has four changes in 21 s. Drop the 1870→2026 year roll; the VO carries it.
- `S2_Island`: the sack stacks and the Chiapas overlay are two comparisons in 18 s. The overlay is the stronger picture. Consider moving the stacks to a beat of their own or cutting them.
- `S10_Cost`: drop the balance scale. Drop the Catimor and Caturra nodes straight onto the 75–90 cup-score axis, so the shared axis carries the comparison. Cut 9→10 then becomes node → its tick.
- Cut 6→7: state the dot's screen position at the cut (it's in a corner inset, and the rail is centred).
- `S1_Tin`/`S3_Spore`: the Ceylon leaf follows the foliage rule (grey, not Mexico green).

### Ep. 3: Why Mountain Coffee Tastes Different

**Must fix**
1. **`S4_Seed`: seeds don't have growth rings.** The rings invent anatomy. Use the shared cell honeycomb instead: cells pack tight in the slow seed and loose in the fast one, and the walls thicken. Cut 4→5 becomes the seed's elliptical outline flattening into Réunion, which already works.
2. **`S9_Thermometer`: one sideways thermometer with "1,200 m above 19 °C and 1,650 m above the same 19 °C" can't be read.** One axis can't map metres to degrees for two mountains. Draw three stacked rails instead: °C on top, then VERACRUZ m and COLOMBIA m, offset so that 19 °C lines up over 1,200 and 1,650. The Mexican 1,200 m grade tick sits on the Veracruz rail. Either cut the Guatemala tick or give it its own rail. If that doesn't fit in 17 s, fold the beat into the end of S8.

**Could improve**
- Cut 5→6: a cold plot on Réunion becomes Guatemala's 1,350 m line, which is arbitrary. Let the dot become a neutral "cold" marker that travels up the scale and stops at the first band.
- Cut 7→8: don't morph a plan-view map into a side profile. Keep the Coatepec dot fixed, wipe the map off and draw the profile, as ep. 1 swaps the world map for Mexico.
- There's no real map camera move in the episode. Add a 2 s locator pull-out in S8 (Coatepec 19° N, Colombia 5° N) on the world map, which the script lists as reused but never uses.
- `S7_Ladder` cites NMX-F-551 but shows no document. A recreated table row with a highlighter on "Estrictamente Altura" would be the episode's document on screen.
- `S4_Seed` D: the water glass uses water cyan.

### Ep. 4: The Shade Forest in Your Cup

**Must fix**
1. **`S3_Spectrum`: five equal 300 px panels in a row with labels is the card layout**, even on an axis. Make it one long transect cross-section that thins from forest to sun, left to right. The camera trucks along it and the labels drop at the five points, so each change happens on one drawing.
2. **Cuts 4→5 and 5→6 don't work geometrically.** The S4 chart sits *below* the cross-section, so its trace can't "become a root" in the soil. The litter band "slides to the top" while the camera "tilts up", but a tilt up moves the band down. Treat S4–S6 as one cross-section precomp with one camera. Each cut is a camera handoff (the same transform at the end of N and the start of N+1). The chart sits in an overlay that clears before the tilt.
3. **Cut 6→7 runs backwards.** The migrant flies off towards North America and then "lands" on Mexico. Turn it into the map move: pull out from the Chiapas farm, draw the route north to the Great Lakes, then draw it back south and land on the same farm dot ("it comes back every winter"). S7 opens on that dot.
4. **`S2_Understory`/`S4_Canopy`: the "dark-green coffee shrubs" are an unlisted colour.** Ethiopian shrubs are grey per the foliage rule. Chiapas shrubs are `MX` green.

**Could improve**
- Cut 7→8: an organic-area bar (hectares) becomes a yield bar (%), so the idea changes inside the shape. End S7 on a stack of sacks for Mexico's organic coffee, and open S8 with that stack as the FULL SUN bar.
- Cut 1→2: the bag "dissolves" into the forest. Clear the bag inside S1 so the cut frame is only the bird.
- `S10_Answer` is a recap with brackets, close to text on white. Make the brackets do something: each layer's work (temperature, nitrogen, litter, birds) slides out as a small priced item, so the bracket totals "work the trees do" against the 18 % kilo cost from S8.
- `S3_Spectrum` A shows Moguel & Toledo only as a citation chip. Recreate their figure (the five-system diagram) as the document on screen.
- `S6_Birds`: the 46 migrant outlines need a second repeater layer (per-copy style isn't possible). The Mexico City outline (S7) is shared with ep. 10 S2.

### Ep. 5: Washed, Natural, Honey

**Must fix**
1. **`S4_Oxygen` is a slideshow of labels**: an anaerobic tank, a carbonic tank, a trophy chip, an Indonesia inset with a stopwatch, then a caption. It runs 35 s and doesn't move toward the question. Cut the trophy and the wet-hulled inset. Keep anaerobic and carbonic as two seeds sliding down the oxygen axis (about 12 s), and say "wet-hulled" in one VO clause or not at all.
2. **Cut 3→4 contradicts itself.** The fruit axis "tilts 90°" to become the oxygen axis, yet washed, honey and natural are still on the fruit axis at OPEN. The build note's "rotate one precomp" would rotate the dots too. Keep the fruit axis horizontal as the top edge (OPEN) and grow the oxygen axis down from its middle. That's a continuation inside one precomp, not a tilt.
3. **Cut 6→7 is fake.** The pH needle becomes "a pointer on the hand-test inset", which means nothing. Merge `S7_HandTest` into the end of `S6_Tank`: the needle lands at the tomato mark, then the camera pushes into a fistful of seeds from the tank. Cut 7→8 starts from the magenta dot on one of those seeds, as drafted.

**Could improve**
- `S3_FruitAxis`: place the four honey grades *along* the axis at their mucilage amount, not in a separate row. Give the "red" and "black" chips dried-mucilage tones, not arabica red.
- `S6_Tank`: microbes from a count-driven repeater line up in rows, not on seeds. Use pre-placed dot groups on the seeds with staggered opacity.
- `S10_Water` has five beats in 34 s. The litre-bottle rows and the river are the two pictures, so make the "no tank" tag and its dashed line back to the clause one beat.
- Cut 1→2: the red dot appears from a yellow highlighter swipe. Let the swipe's end cap shrink into the dot as it turns red, or open S1 on a small cherry printed in the declaration's margin.
- The hand (S7) should be two static silhouettes (open, closed) swapped on a cut, not an articulated hand.

### Ep. 6: How Decaf Is Made, in Veracruz

The cleanest chain in the set: every cut shares a real shape at a stated position and size.

**Must fix**
1. **`S4_Solvents` B:** the "heat-coloured column" to 200 °C has no colour assigned. Draw it in ink (process heat is ink; ice blue is climate temperature).

**Could improve**
- `S1_Bag`: a retail decaf bag's window would show roasted beans, not green ones. Show roasted beans, and let the one that slides out fade back to the seed colour (the same device as ep. 8 S1).
- `S8_Cordoba` has three camera moves, a timeline strip, a mountain, a water drop, two arcs and split tanks in 40 s. Drop the Switzerland/Canada timeline strip and give the Burnaby dot a date chip.
- Cuts 2→3 here and in ep. 8 use the same device (composition bar thins into an axis). Keep it here and vary it in ep. 8.
- `S10_Close` ends on the red cherry, as eps. 1 and 9 also do. That's fine as a series signature, but don't let every episode end on it.

### Ep. 7: Why Does a Plant Make Caffeine?

**Must fix**
1. **Cut 8→9 (`S8_Robusta` → `S9_Broca`):** the robusta-brown dot turns pest violet at Cacahoatán, which says robusta brought the borer. End S8 on the Mexico map with the robusta bands. Open S9 on the same map (a genuine continuation) and draw the violet arrow in fresh from Guatemala.

**Could improve**
- `S5_Hornworm` has five beats in 30 s (two experiments, a nerve inset and a journal page). Cut the slug and keep the spray-vs-robusta-seed gauge as one beat, or drop it.
- `S9_Broca`: draw the gut bacteria in ferment magenta (microbes, as in ep. 5), not ink. Draw the violet stain as overlapping ellipses scaling under a coffee-belt track matte. That's cheap and irregular.
- `S1_Flower`/`S5_Hornworm`: the leaves follow the foliage rule (grey). Violet and caffeine blue then read cleanly against them.
- `S3_Pathway`'s sugar is a pentagon (ribose) and ep. 8's is a hexagon. That's correct, but take both from the shared molecule kit so the stroke and fill match.

### Ep. 8: What Roasting Really Does

**Must fix**
1. **Colours:** drop heat purple and aroma pink (see the palette). The roast curve is ink, and its dot is the bean in its ramp colour, which also ties the curve to the ramp. Aroma molecules are ink outlines, and in `S8_Sugar` C the cloud is grey with the survivors in ink.
2. **`S8_Sugar` C:** the 1,000-dot cloud "with a repeater, randomised by expression" can't be built. Generate the dots in Python as groups: one layer for the 970 that fade and one layer for the 30 that stay.
3. **`S7_SecondCrack` C trims the weight loss off the right end of the dry-matter bar**, which is OTHER. The loss is mostly water and gas. Empty S2's separate water bar first, then take a thin slice of the dry bar for CO₂ and volatiles. The ghost outline stays.

**Could improve**
- `S3_Curve` B: cut the heart-monitor flicker. It's a gimmick on top of a curve that already reads.
- Cut 2→3 repeats ep. 6's bar-into-axis device. An alternative: the yellow-to-be seed sits on the left of the frame, and the curve's start point is the seed itself.
- `S9_Mexico` has five beats in 36 s. The faint map with leader lines (SAME MOUNTAINS) can be a single chip. Spend the time on the drum cut-away and the share bar.
- `S4_Maillard`: the Strecker step (C) needs the longest hold, and the brown in D must use the ramp's roast brown, not robusta brown.
- The seed is ep. 1's cream `SEED`, not "pale green" (S1, S2).

### Ep. 9: Who Gets Paid for Your Coffee

**Must fix**
1. **`S4_Chain`: slices cut from a price bar "without sizes, only as order" still look like sizes.** A slice on a bar is a magnitude. Either find a sourced breakdown for Mexico, or draw each deduction as an equal-width hatched segment marked "?" and keep the green remainder unhatched, so the chart says out loud that the sizes are unknown.
2. **Cut 9→10 puts the green floor band *under* the 15¢ sliver**, as if the farmer's money were added to the coffee's. The farmer's share is *inside* the 15¢. Turn the floor line into the lower part of the sliver itself (green within ink), matching S4, where the remainder turned green.
3. **Colour:** the C price is ink, not violet (palette).

**Could improve**
- `S2_Grams` has three pictures for one number (the pans, the pound bag, the 100-square strip). Keep the pans and the strip.
- `S3_Exchange` B: contract size against a shipping container is trivia that doesn't move the answer. Cut it and give the time to the frost/harvest beat (C), which is the mechanism.
- `S6_Treaty` D: the Cold War inset is a corner card. Say it in VO over the quota bar instead.
- `S9_Floor` C: the Fairtrade minimum is global, so draw the line ink-dashed and let it grow out of the green UCIRI dot. Mexico green stays on UCIRI and the farmer's share.
- The coyote truck (S4) and the 2 ha plot (S5) are shared assets for ep. 10. Build them in the common module.

### Ep. 10: Café de Olla and the Instant Nation

**Must fix**
1. **Instant blue is caffeine blue.** Draw instant in mid grey `#8C8C8C` with an ink outline (jar lid, cups, factories). The grey heap in S3 then becomes the grey jar: the argument, in one colour.
2. **Drop olla clay.** The pot is an ink outline with a sand object fill, and piloncillo and canela take object tones.
3. **`S2_Cups` "ink-brown" cups** are an unassigned colour next to robusta brown. Draw them as empty ink outlines in S2 and fill them Mexico green in S9. That's the change S9 needs.
4. **Cut 5→6 lands the instant-coffee sack on the EXPORTS pan**, the opposite of the idea. Build IMPORTS first: the sack lands on the import pan, then the export side stacks up.
5. **`S6_Imports` has seven elements in 29 s** (the balance, the brown turn, a Brazil inset, price tags, a second factory, a crop stack, a protest sign). Keep the balance and the Brazil route. Move the Veracruz plant, the crop stack and the protest into a beat of their own, or cut the protest sign.

**Could improve**
- Cut 3→4: the heap is pushed to the frame centre, but the timeline dot sits at (360, 540). End the push with the dot at (360, 540).
- `S7_Olla` C: a figurative woman at a camp is the most expensive drawing in the season for a line the VO calls a legend. Use a recreated document (a period illustration caption or a corrido sheet) with the highlighter on "legend".
- `S7_Olla` D: the coffee-vs-rest flavour split has no data. Show it as the pot's ingredients by weight on one bar (coffee, piloncillo, canela), which is a real number.
- `S1_Jar`/`S10_Close`: keep the kitchen to a table line, a window frame and ep. 1 tree icons. `S9_Specialty`'s street map is a grid plus a ring road, not a real map.
- `S5_Soluble` roasts beans brown just before S6 turns the import sacks robusta brown. Keep the S5 beans on the roast ramp's darkest stop so the two browns don't meet.

## 4. Summary

| Ep. | Must fix | Notes |
| :-: | :-: | :--- |
| 2 | 4 | Strong mechanism and turn. Two cuts break meaning (4→5, 7→8) |
| 3 | 2 | Strong. S9 needs a readable dual scale |
| 4 | 4 | **Weakest storyboard.** A card-like spectrum, and three broken cuts in the core (4→5, 5→6, 6→7) |
| 5 | 3 | S4 is a detour, and the axis geometry and the hand-test cut need rework |
| 6 | 1 | The best chain in the set |
| 7 | 1 | One misleading colour flip at 8→9 |
| 8 | 3 | Colours, the dot cloud, and the weight-loss bar |
| 9 | 3 | Chart honesty in S4 and the closing bar |
| 10 | 5 | Mostly colour; S6 is overloaded |
