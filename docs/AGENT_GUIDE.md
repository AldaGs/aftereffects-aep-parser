# AI Agent Guide: Authoring After Effects Projects via Motion JSON

This guide explains how an AI agent (or automated pipeline) can author motion graphics in declarative JSON and compile them into native Adobe After Effects (`.aep`) projects and ExtendScript (`.jsx`) files.

---

## 1. Pipeline Overview

```
                                      ┌────────────────────────┐
                                      │   AI Agent / LLM       │
                                      └───────────┬────────────┘
                                                  │ emits
                                                  ▼
                                      ┌────────────────────────┐
                                      │ Authoring Motion JSON  │
                                      │ (schema/motion.schema) │
                                      └───────────┬────────────┘
                                                  │
                                                  ▼
               ┌──────────────────────────────────────────────────────────────────┐
               │                        json2jsx CLI                              │
               │                                                                  │
               │  json2jsx -i design.json -o build.jsx -aep project.aep -run      │
               └──────────────────┬─────────────────────────────┬─────────────────┘
                                  │                             │
                     emits ES3    │                             │ invokes headless CLI
                                  ▼                             ▼
                    ┌───────────────────────────┐ ┌───────────────────────────┐
                    │ ExtendScript (.jsx)       │ │ Adobe After Effects       │
                    │ Works in AE UI / Scripts  │ │ Native Project (.aep)     │
                    └───────────────────────────┘ └─────────────┬─────────────┘
                                                                │
                                                                ▼
                                                  ┌───────────────────────────┐
                                                  │ aep-parser CLI            │
                                                  │ Reads .aep directly into  │
                                                  │ JSON for verification     │
                                                  └───────────────────────────┘
```

### Why Motion JSON instead of raw JSX?
1. **Determinism & Schema Validation**: JSON can be validated against [`schema/motion.schema.json`](../schema/motion.schema.json) before touching After Effects.
2. **Layer Stacking Consistency**: In After Effects, `layers.add()` puts layers on *top*. `json2jsx` handles reverse layer instantiation so the order in your JSON matches the visual stacking order (index 0 on top).
3. **Escapes & ES3 Quirks Handled**: ExtendScript uses an old ES3 JavaScript engine (no `let`/`const`, no arrow functions, no native `JSON`). The compiler abstracts away all ExtendScript boilerplate.

---

## 2. Quick Start: The 3-Step Workflow

### Step 1: Write Motion JSON
Create a file `my_motion.json` conforming to `schema/motion.schema.json`.

```json
{
  "$schema": "../schema/motion.schema.json",
  "compositions": [
    {
      "name": "MainComp",
      "width": 1920,
      "height": 1080,
      "fps": 30,
      "duration": 5.0,
      "backgroundColor": "#0F172A",
      "layers": [
        {
          "name": "Headline",
          "type": "text",
          "text": {
            "string": "HELLO WORLD",
            "fontSize": 96,
            "fillColor": "#F8FAFC",
            "justification": "center"
          },
          "transform": {
            "position": [960, 540],
            "opacity": {
              "keyframes": [
                { "time": 0.0, "value": 0, "ease": "easeOut" },
                { "time": 0.5, "value": 100 }
              ]
            }
          }
        }
      ]
    }
  ]
}
```

### Step 2: Compile to JSX & AEP
Run the CLI tool:

```powershell
# Compile to ExtendScript (.jsx) only:
.\json2jsx.exe -i my_motion.json -o my_motion.jsx

# Compile AND execute After Effects headless to save native .aep:
.\json2jsx.exe -i my_motion.json -o my_motion.jsx -aep my_motion.aep -run
```

### Step 3: Verify with AEP Parser
Verify your `.aep` was created correctly without opening the AE GUI:

```powershell
.\aep-parser.exe -i my_motion.aep -o my_motion_parsed.json
```

Or run the automated round-trip verification suite:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\roundtrip.ps1 -AuthoringJson my_motion.json
```

---

## 3. Schema Reference & Properties

### 3.1 Project Root

| Field | Type | Description |
| :--- | :--- | :--- |
| `$schema` | `string` | Relative path to `motion.schema.json` |
| `expressionEngine` | `string` | `"javascript-1.0"` (recommended) or `"extendscript"` |
| `bitDepth` | `string` | `"8 bpc"`, `"16 bpc"`, or `"32 bpc"` |
| `assets` | `array` | Footages, solids, or audio imported into the project |
| `compositions` | `array` | One or more composition definitions |

### 3.2 Composition Object

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `name` | `string` | **Required** | Composition name |
| `width` | `integer` | `1920` | Width in pixels |
| `height` | `integer` | `1080` | Height in pixels |
| `fps` | `number` | `24` | Frames per second |
| `duration` | `number` | **Required** | Duration in seconds |
| `backgroundColor` | `string` | `"#000000"` | Hex color code (e.g. `"#0A0F1D"`) |
| `layers` | `array` | `[]` | Array of layers (first item is top-most) |

### 3.3 Layer Types & Options

- `"text"`: Text layer. Specify `text` object (`string`, `font`, `fontSize`, `fillColor`, `tracking`, `justification`).
- `"shape"`: Vector shape layer. Specify `shapes` array with items like `rect`, `ellipse`, `fill`, `stroke`, `trim`, `path`.
- `"solid"`: Color solid. Specify `solidColor` (hex or RGB array) and optional `width`/`height`.
- `"null"`: Invisible controller layer for parenting and rig hierarchies.
- `"adjustment"`: Adjustment layer with effects affecting all layers beneath it.
- `"precomp"`: Nested composition reference (`source: "CompName"`).
- `"footage"`: Imported image, video, or audio (`source: "asset_id"`).
- `"camera"`: 3D Camera layer.
- `"light"`: 3D Light layer.

### 3.4 Transform Properties

All transform properties can be specified as either:
1. **Static Value**: A number or array (e.g. `"opacity": 80`, `"position": [960, 540]`, `"scale": [100, 100]`).
2. **Animated Property Object**:
   ```json
   "scale": {
     "keyframes": [
       { "time": 0.0, "value": [0, 0], "ease": "easeOut" },
       { "time": 0.8, "value": [100, 100] }
     ],
     "expression": "loopOut('pingpong');"
   }
   ```

Supported transform property keys:
- `position` (`[x, y]` or `[x, y, z]`)
- `xPosition`, `yPosition`, `zPosition` (for separated dimensions)
- `scale` (`[sx, sy]` or `[sx, sy, sz]`, 100% = default)
- `rotation` (2D rotation in degrees)
- `xRotation`, `yRotation`, `orientation` (for 3D layers)
- `opacity` (0 to 100)
- `anchorPoint` (`[x, y]` or `[x, y, z]`)

### 3.5 Keyframe Easing Presets
- `"easeOut"`: Starts fast, slows down smoothly to a stop (speed: 0, influence: 75%).
- `"easeIn"`: Starts slow, accelerates into the keyframe.
- `"easeInOut"`: Smooth acceleration and deceleration.
- `"linear"`: Constant speed.
- `"hold"`: Holds previous value until next keyframe.

---

## 4. Motion Design Recipes (Copy & Paste)

### Recipe 1: Smooth Fade-In and Fade-Out
Fades a layer in over the first 0.5s, holds, and fades out over the last 0.5s:

```json
{
  "name": "Badge",
  "type": "shape",
  "transform": {
    "opacity": {
      "keyframes": [
        { "time": 0.0, "value": 0, "ease": "easeOut" },
        { "time": 0.5, "value": 100 },
        { "time": 4.5, "value": 100, "ease": "easeIn" },
        { "time": 5.0, "value": 0 }
      ]
    }
  }
}
```

### Recipe 2: Slide-Up Text Reveal with Track Matte
A title text layer sliding up from behind an invisible rectangular mask:

```json
[
  {
    "name": "Title Mask",
    "type": "shape",
    "shapes": [
      { "type": "rect", "size": [1000, 140] },
      { "type": "fill", "color": "#FFFFFF" }
    ],
    "transform": {
      "position": [960, 520]
    }
  },
  {
    "name": "Title Text",
    "type": "text",
    "text": {
      "string": "ELEVATE YOUR VISION",
      "font": "Helvetica-Bold",
      "fontSize": 72,
      "fillColor": "#FFFFFF",
      "justification": "center"
    },
    "trackMatte": {
      "target": "Title Mask",
      "type": "Alpha"
    },
    "transform": {
      "position": {
        "keyframes": [
          { "time": 0.2, "value": [960, 640], "ease": "easeOut" },
          { "time": 0.9, "value": [960, 545] }
        ]
      },
      "opacity": {
        "keyframes": [
          { "time": 0.2, "value": 0, "ease": "easeOut" },
          { "time": 0.6, "value": 100 }
        ]
      }
    }
  }
]
```

### Recipe 3: Organic Elastic Bounce (Inertial Decay Expression)
Add physics-driven spring oscillation without manual keyframes:

```json
{
  "name": "Hero Card",
  "type": "shape",
  "transform": {
    "scale": {
      "keyframes": [
        { "time": 0.0, "value": [0, 0], "ease": "easeOut" },
        { "time": 0.6, "value": [100, 100] }
      ],
      "expression": "n = 0;\nif (numKeys > 0) {\n  n = nearestKey(time).index;\n  if (key(n).time > time) n--;\n}\nif (n == 0) {\n  t = 0;\n} else {\n  t = time - key(n).time;\n}\nif (n > 0 && t < 1) {\n  v = velocityAtTime(key(n).time - 0.001);\n  amp = 0.05; freq = 4.0; decay = 5.0;\n  value + v*amp*Math.sin(freq*t*2*Math.PI)/Math.exp(decay*t);\n} else {\n  value;\n}"
    }
  }
}
```

### Recipe 4: Animated Lower Third with Animated Stroke Trim
A professional broadcast lower third with expanding accent line:

```json
[
  {
    "name": "Lower Third Text",
    "type": "text",
    "text": {
      "string": "SARAH CONNOR\nLead Systems Architect",
      "font": "Arial-BoldMT",
      "fontSize": 42,
      "fillColor": "#F1F5F9",
      "justification": "left"
    },
    "transform": {
      "position": [240, 890],
      "opacity": {
        "keyframes": [
          { "time": 0.4, "value": 0, "ease": "easeOut" },
          { "time": 0.9, "value": 100 }
        ]
      }
    }
  },
  {
    "name": "Accent Line",
    "type": "shape",
    "shapes": [
      { "type": "rect", "size": [6, 80], "roundness": 3 },
      { "type": "fill", "color": "#38BDF8" }
    ],
    "transform": {
      "position": [210, 895],
      "scale": {
        "keyframes": [
          { "time": 0.1, "value": [100, 0], "ease": "easeOut" },
          { "time": 0.6, "value": [100, 100] }
        ]
      }
    }
  },
  {
    "name": "Background Glass Plate",
    "type": "shape",
    "shapes": [
      { "type": "rect", "size": [620, 110], "roundness": 12 },
      { "type": "fill", "color": "#0F172A", "opacity": 85 }
    ],
    "transform": {
      "position": [510, 895],
      "scale": {
        "keyframes": [
          { "time": 0.0, "value": [0, 100], "ease": "easeOut" },
          { "time": 0.5, "value": [100, 100] }
        ]
      }
    }
  }
]
```

### Recipe 5: Staggered Multi-Item Intro via Parent Null
Parent all graphics to a central controller null, animate the controller, and let individual children follow automatically:

```json
[
  {
    "name": "Rig Controller",
    "type": "null",
    "transform": {
      "position": {
        "keyframes": [
          { "time": 0.0, "value": [960, 600], "ease": "easeOut" },
          { "time": 1.0, "value": [960, 540] }
        ]
      }
    }
  },
  {
    "name": "Graphic Item 1",
    "type": "shape",
    "parent": "Rig Controller",
    "transform": { "position": [-200, 0] }
  },
  {
    "name": "Graphic Item 2",
    "type": "shape",
    "parent": "Rig Controller",
    "transform": { "position": [200, 0] }
  }
]
```

---

## 5. Reverse Parsing: Inspecting Existing `.aep` Projects

When an agent needs to study how an existing motion project was constructed, use `aep-parser.exe`:

```powershell
.\aep-parser.exe -i "aep\TOP5.aep" -o "temp\top5.json"
```

The output JSON contains full RIFX tree extraction:
- Compositions (`width`, `height`, `framerate`, `seconds`, `backgroundColor`)
- Layers (`index`, `name`, `kind`, `parentIndex`, `flags`, `compInPoint`, `compOutPoint`)
- Keyframes & Transforms (`cdat` static values, `ldat` timeline keyframe values, `tdbs` blocks, expressions)
- Effects and Parameters (`parT`, `pard`, effect match names)
- Text Documents & Styles (Fonts, sizes, fill colors, tracking, alignment)

To convert this raw export directly into authoring format:

```powershell
.\export2author.exe -i "temp\top5.json" -o "temp\top5_authoring.json"
```

---

## 6. Rules for Agent Prompters

1. **Position Shape Layers via `transform.position` (Crucial!)**: In After Effects, a Shape Layer's `transform.position` defaults to the center of the composition (`[width/2, height/2]`), while a vector shape item's internal `position` (`rect.position` / `ellipse.position`) is a **relative offset** from the layer's anchor point (`[0, 0]`). **Always** leave the vector shape's internal `position` omitted (so it stays centered at `[0, 0]` on the layer's anchor point) and place the shape at composition coordinates `[X, Y]` using the layer's `"transform": { "position": [X, Y] }`. This avoids double-offsetting and ensures `transform.scale` and `transform.rotation` pivot around the shape's own center.
2. **Text Baseline Alignment**: A Text Layer's `transform.position` specifies its **baseline** (bottom of capital letters), whereas a Shape Layer's `transform.position` specifies its geometric center. To vertically center text of `fontSize: S` inside a badge centered at `Y`, place the text at `[X, Y + 0.35 * S]`.
3. **Keep layer names unique** within each composition to ensure clean parenting and track matte resolution.
4. **Order layers top-to-bottom**: The first element in the `"layers"` array is the top-most visual layer.
5. **Use percentage for scale and opacity**: Opacity ranges from `0` to `100`. Scale default is `[100, 100]`.
6. **Colors**: Hex strings (e.g. `"#FF3366"`) or normalized RGB arrays `[1.0, 0.2, 0.4]`.
7. **Expressions**: Use standard JavaScript expressions. Set `"expressionEngine": "javascript-1.0"` in project root.

