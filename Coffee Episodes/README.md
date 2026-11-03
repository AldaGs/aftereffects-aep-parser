# Coffee Episodes

Scripts for Season 1. Rules: [STYLE_GUIDE.md](STYLE_GUIDE.md). Channel plan: [coffee_series_plan.md](../schema/examples/coffee_series_plan.md). Episode 1 script: [coffee_families_script.md](../schema/examples/coffee_families_script.md).

Main episodes run 3–5 minutes. Episode 1 (3:00) doubles as the pilot or channel trailer. All scripts 2–10 are **draft v2**: written, reviewed by a fact-checker, a visual director and a story editor (`notes/`), and revised. None is approved yet.

| # | Release | Script | Question | VO length |
|:-:|:-:| :--- | :--- | :-: |
| 1 | 1 | *built* (`schema/examples/coffee_families_*`) | Where does arabica come from? | 3:00 |
| 2 | 2 | [02_ceylon_rust_script.md](scripts/02_ceylon_rust_script.md) | Why did Ceylon give up coffee when Mexico didn't? | 4:50 |
| 6 | 3 | [06_decaf_veracruz_script.md](scripts/06_decaf_veracruz_script.md) | Why does Colombian decaf go to Veracruz? | 3:32 |
| 7 | 4 | [07_why_caffeine_script.md](scripts/07_why_caffeine_script.md) | What is caffeine for? | 4:07 |
| 3 | 5 | [03_mountain_coffee_script.md](scripts/03_mountain_coffee_script.md) | Why is coffee graded in metres? | 3:58 |
| 4 | 6 | [04_shade_forest_script.md](scripts/04_shade_forest_script.md) | Why do some coffee farms look like jungle? | 4:41 |
| 5 | 7 | [05_processing_script.md](scripts/05_processing_script.md) | Why Veracruz lets its coffee go sour | 4:09 |
| 8 | 8 | [08_roasting_script.md](scripts/08_roasting_script.md) | Where does the caramel in coffee come from? | 4:06 |
| 9 | 9 | [09_who_gets_paid_script.md](scripts/09_who_gets_paid_script.md) | Of a $5 latte, how much is coffee, and who sets the farmer's price? | 4:42 |
| 10 | 10 | [10_cafe_de_olla_script.md](scripts/10_cafe_de_olla_script.md) | Why does a coffee country drink instant? | 4:17 |

Episode 1 is built at **24 fps** with every in/out animation a multiple of 12 frames; `generators/01_coffee_families_vo.py` re-times it to the recorded VO (no time-stretch). Episodes 2 and 3 follow the same rules (`write(..., beats=True)` in `coffee_common`) and use episode 1's drawn vectors: ep. 2 its leaves and shrub icons plus a tea leaf, tea bush and teacup; ep. 3 its cherry and cross-section, the section's seed shape for the big seeds, shrub icons, hillside bushes, egg-shaped calendar cherries and an umbrella-crowned shade tree. Episodes 4–10 stay at 30 fps (`coffee_common.FPS`) until they are moved over. Preview: `previews/01_coffee_families_sheet.jpg`, cherry close-up `previews/01_coffee_families_cherry.jpg`.

Release order after episode 6 follows the story editor's recommendation; episode 10 goes last because it calls back episodes 2 and 8.

Each script lists its unconfirmed facts (†) at the end.

## Folder layout (one folder per file type)

| Folder | Holds |
| :--- | :--- |
| `scripts/` | `<NN>_<name>_script.md`: script and storyboard |
| `notes/` | Review notes |
| `generators/` | `<NN>_<name>.py`: Python generator, plus shared `coffee_common.py` |
| `json/` | `<NN>_<name>.json`: authoring JSON written by the generator (never hand-edit) |
| `jsx/` | `<NN>_<name>.jsx`: ExtendScript from `json2jsx` |
| `aep/` | `<NN>_<name>.aep`: After Effects projects built on your machine |
| `previews/` | Preview frames and contact sheets |

Build an episode from the repo root:

```bash
python "Coffee Episodes/generators/02_ceylon_rust.py"
go run ./cmd/json2jsx -i "Coffee Episodes/json/02_ceylon_rust.json" -o "Coffee Episodes/jsx/02_ceylon_rust.jsx" -aep "<abs path>/Coffee Episodes/aep/02_ceylon_rust.aep"
```
