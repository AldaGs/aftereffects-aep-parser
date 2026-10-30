# How Does an Espresso Machine Work? — Animation Pitch

**Format:** 2:22 animated explainer, 1920×1080, 30 fps
**Audience:** curious general viewers; no coffee knowledge assumed
**Build:** `espresso_explainer.json` → `json2jsx` → After Effects (one precomp per scene inside `Espresso_Explainer`)

## Logline

Every espresso is a 25-second feat of engineering: water near boiling, pushed at nine times the pressure of the air around us through a puck of coffee. We follow that water through the machine, meet the inventors who chased the pressure, and compare the five ways modern machines produce it.

## Look and feel

| | |
| :--- | :--- |
| Illustration | Flat shapes, dark ink outlines with round joins, one-tone shading, highlights and shadows under objects |
| Palette | Roast browns for the "coffee" acts, deep teal for the science, sepia paper for history and the map, one saturated background per machine type. Mustard `#E3A72F` is the accent throughout |
| Type | Georgia Bold for titles and numbers (editorial), Arial for labels and small tracked caps. Both ship with Windows and macOS |
| Motion | Fast-out, slow-in easing ("snap") for entrances, overshoot pops for objects, slow push-in camera on every scene, a camera that follows the water through the machine, and two-colour band wipes between acts |
| Texture | Drifting dust particles in every scene and a 3.5 % noise adjustment layer over the master comp |

## Script

Timecodes are for the master comp. VO is written at about 150 words per minute.

### 1. Hook — 0:00–0:12 (`S1_Hook`)
**Visual:** A group head drops in and a portafilter slides under it. A cup rises into frame. Two tiger-striped streams pour while callouts draw on: *9 bar*, *93 °C*, *25 s*. The machine lifts away, the cup steams and the title lands.

**VO:** "Nine times the pressure of the air around you. Water just shy of boiling. About twenty-five seconds. That's what it takes to pull a single shot of espresso. So how does a machine pull it off?"

### 2. Why pressure? — 0:12–0:25 (`S2_WhyPressure`)
**Visual:** A cross-section of the basket. Grounds pop in row by row and a tamper compresses them. Water pools on top while one sad drop falls. Then a piston slams down (with camera shake), channels of water snake through the puck and turn caramel as they go, and an espresso stream carries crema bubbles out.

**VO:** "Espresso coffee is ground very fine and packed tight. Gravity alone can barely push water through it. But press at nine bar, and water races through in seconds, dragging out oils, dissolved gases and fine solids. Together they form crema, the golden foam on top."

### 3. A short history of pressure — 0:25–0:43 (`S3_History`)
**Visual:** On sepia paper, the camera pans along a timeline. At each stop a drawing rises from the line: a steam brewer, the tall "Ideale" with its eagle, a spring lever pulling down, and a red E61 with a lightning bolt.

**VO:** "In 1884, Angelo Moriondo patented a steam machine that brewed coffee in bulk. By 1905, Bezzera and Pavoni were selling single cups, but steam only managed about one and a half bar, and the coffee tasted burnt. In 1948, Achille Gaggia's spring lever reached nine bar, and crema was born. And in 1961, the Faema E61 replaced muscle with an electric pump, setting the template for machines today."

### 4. Inside the machine — 0:43–1:08 (`S4_Inside`)
**Visual:** A blueprint-grid cutaway. The camera flies from component to component as water fills the pipes: tank, pump (rotor spins, gauge to 9 bar), boiler (coil glows, water turns red, bubbles, *93 °C*), group head (shower drops, puck darkens), cup (tiger streams, crema rises). It finishes on a wide shot: "About 25 seconds, start to finish."

**VO:** "Here's the journey. Water leaves the tank, and a pump squeezes it to about nine bar. A boiler heats it to around ninety-three degrees. At the group head it floods the coffee puck through a shower screen… and seconds later, espresso pours out, crowned with crema."

### 5. Five ways to make pressure — 1:08–2:02 (`S5_TypesIntro`, `S5a`–`S5e`)
**Visual:** Five icons pop up in a row. Each machine then gets its own coloured scene: an animated cutaway on a circular stage, its name and power source, a two-line description, a pressure-over-time chart drawn in sync with the animation, and pros and cons with check and cross badges.

**VO (intro):** "Every machine chases the same goal. They just build the pressure differently."

- **Lever (1:12):** "Pull the lever and you load a spring. Let go, and the spring presses the shot, starting near nine bar and gently falling off. Silent, beautiful, and it takes practice."
- **Vibratory pump (1:22):** "Most home machines use a vibratory pump: an electromagnet snaps a tiny piston back and forth fifty or sixty times a second. Compact and cheap, but buzzy, and the pressure wobbles."
- **Rotary pump (1:32):** "Café machines often use a rotary pump. A motor spins a vaned disc inside an off-centre chamber, sweeping water through for a smooth, steady nine bar. It's quiet, and it can be plumbed straight into the mains."
- **Super-automatic (1:42):** "Super-automatics do everything at the touch of a button: grind, dose, tamp, brew and dump the puck. Convenient and consistent, but you give up control."
- **Capsule (1:52):** "And capsule machines pierce a sealed pod of pre-ground coffee and pump hot water straight through. Fast and clean, but each cup costs more, and leaves a capsule behind."

### 6. Convenience vs. control — 2:02–2:13 (`S6_Map`)
**Visual:** Axes draw on, and a mustard trade-off band sweeps diagonally. Icons pop onto it from capsule (top left) to lever (bottom right).

**VO:** "Line them up and a pattern appears: the more a machine does for you, the less you steer the shot."

### 7. Outro — 2:13–2:22 (`S7_Outro`)
**Visual:** The cup returns with steam. Three mustard badges (9 bar, 93 °C, 25 s) bob gently below it as the closing line fades up. Fade to black.

**VO:** "Different machines, the same tiny miracle: nine bar, ninety-three degrees, twenty-five seconds. Enjoy your next espresso."

## Sound design notes

- A soft low hum under the inside-the-machine act. The pump click and buzz should sync with the vibratory scene's flickering "BZZZ".
- A metallic *thunk* on the piston slam (0:20) and on each band wipe.
- A gentle pour sound under every tiger-stream shot; a ceramic *clink* when the hero cup lands (0:01.5).
- Paper rustle and a light marimba under the history act.

## Production notes

- **Retiming:** every scene is a precomp. Drag scene layers in `Espresso_Explainer` to retime to the final VO; transitions are the `Wipe N A/B` layers at each cut.
- **Fonts:** Georgia and Arial; swap them in the JSON (`"font"`) for a house typeface.
- **Expressions:** loops (steam, rotors, the vibrating piston, pipe pulses, particles) use the JavaScript expression engine, which the project sets.
- **Grain:** the `Film Grain` adjustment layer at the top of the master comp. Turn it off for faster previews.
