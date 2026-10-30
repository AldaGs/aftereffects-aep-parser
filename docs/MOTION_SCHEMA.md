# Motion Design Authoring Schema (`motion.schema.json`)

The Motion Design Authoring Schema is a high-level, human- and LLM-friendly JSON specification for authoring After Effects projects, compositions, layers, keyframe animations, shape vectors, text styling, and expressions.

Instead of writing verbose ExtendScript (`.jsx`) or reverse-engineering proprietary binary `.aep` chunks, an agent authors a concise JSON file. The `json2jsx` tool then compiles this schema into valid After Effects ExtendScript and builds a native `.aep`.

Schema Definition: [`schema/motion.schema.json`](../schema/motion.schema.json)

---

## 1. Top-Level Structure

```json
{
  "$schema": "../schema/motion.schema.json",
  "file": "my_animation.aep",
  "expressionEngine": "javascript-1.0",
  "bitDepth": "8 bpc",
  "assets": [ ... ],
  "compositions": [ ... ]
}
```

- `file`: Optional filename for saving the generated project.
- `expressionEngine`: `"javascript-1.0"` (default, modern AE engine) or `"extendscript"`.
- `bitDepth`: `"8 bpc"`, `"16 bpc"`, or `"32 bpc"`.
- `assets`: Footages, external images/videos/audio, or solid definitions.
- `compositions`: Array of compositions.

---

## 2. Compositions

```json
{
  "name": "MainComp",
  "width": 1920,
  "height": 1080,
  "fps": 24,
  "duration": 10.0,
  "backgroundColor": "#000000",
  "layers": [ ... ]
}
```

- `duration`: In composition seconds.
- `layers`: Array of layer definitions ordered top-to-bottom (stack order matching After Effects timeline).

---

## 3. Layers

### Supported Layer Types:
- `"solid"`
- `"text"`
- `"shape"`
- `"null"`
- `"precomp"`
- `"footage"`
- `"audio"`
- `"camera"`
- `"light"`
- `"adjustment"`

### Layer Properties:
```json
{
  "name": "Heading Text",
  "type": "text",
  "parent": "Background Card",
  "in": 0.5,
  "out": 8.0,
  "threeD": false,
  "motionBlur": true,
  "blendMode": "Normal",
  "transform": { ... },
  "text": { ... },
  "shapes": [ ... ],
  "effects": [ ... ]
}
```

- `parent`: The `name` of the parent layer in the same composition (much more intuitive for agents than index numbers).
- `in` / `out`: Active visibility duration on the timeline in composition seconds.
- `blendMode`: Standard AE blend mode string (e.g. `"Normal"`, `"Screen"`, `"Multiply"`, `"Overlay"`, `"Add"`).
- `trackMatte`: Object with `target` (layer name) and `type` (`"Alpha"`, `"Alpha Inverted"`, `"Luma"`, `"Luma Inverted"`).

---

## 4. Animatable Properties & Keyframes

Properties in `transform`, `effects`, or `shapes` can be defined either as a static constant or as an object with keyframes/expressions.

### Constant Values:
```json
"position": [960, 540, 0]
"opacity": 100
"rotation": 45
```

### Animated Keyframes:
```json
"opacity": {
  "keyframes": [
    { "time": 0.0, "value": 0, "ease": "easeOut" },
    { "time": 0.8, "value": 100, "ease": "easeOut" }
  ]
}
```

- `time`: Composition timeline time in seconds.
- `ease`: Shorthand preset (`"linear"`, `"easeIn"`, `"easeOut"`, `"easeInOut"`) OR custom `{ "inSpeed": 0, "inInfluence": 70, "outSpeed": 0, "outInfluence": 70 }`.
- `interp`: Optional interpolation type: `"bezier"` (default), `"linear"`, or `"hold"`.
- `inTangent` / `outTangent`: Optional spatial tangents for 2D/3D bezier motion paths.

### Expressions:
```json
"rotation": {
  "expression": "time * 180"
}
```

---

## 5. Text Styling

For `"type": "text"` layers:
```json
"text": {
  "string": "HELLO WORLD",
  "font": "HelveticaNeue-Bold",
  "fontSize": 72,
  "fillColor": "#ffffff",
  "strokeColor": "#388bfd",
  "strokeWidth": 2,
  "applyFill": true,
  "applyStroke": false,
  "tracking": 50,
  "justification": "center"
}
```

---

## 6. Shapes

For `"type": "shape"` layers, add elements in the `shapes` array:
- `rect`: `size` `[width, height]`, `position`, `roundness`
- `ellipse`: `size` `[width, height]`, `position`
- `fill`: `color` (hex or RGB), `opacity`
- `stroke`: `color`, `strokeWidth`, `opacity`, `lineCap` (`"butt"`, `"round"`, `"projecting"`), `lineJoin` (`"miter"`, `"round"`, `"bevel"`)
- `trim`: `start`, `end`, `offset` (supports keyframing)
- `path`: Custom bezier vector path with `vertices`, `inTangents`, `outTangents`, `closed`
- `group`: `items` plus an optional `transform` (`anchorPoint`, `position`, `scale`, `rotation`, `opacity`) to animate parts inside one layer

Items listed first draw on top, and a `fill`/`stroke` applies to the paths above it in the same group.

Layers also accept `"enabled": false` to hide guide layers and track matte sources.

---

## 7. Escape Hatch (`jsx`)

If an agent needs an advanced or niche After Effects capability not directly modeled in the schema:
```json
{
  "name": "Complex Layer",
  "type": "null",
  "jsx": "layer.blendingMode = BlendingMode.OVERLAY;"
}
```
The generator runs this snippet with the layer or composition context bound during generation.

